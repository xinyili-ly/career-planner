import os
import re
import json
import logging
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI
from dotenv import load_dotenv

from app.models.student_profile import StudentProfile

load_dotenv()

# 配置日志
logger = logging.getLogger("LLM_Client")

# 初始化客户端
client = AsyncOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)

# --- 定义全维画像提取 Prompt ---
STUDENT_PROFILE_PROMPT = """
你是一位资深职业规划专家。请分析用户的简历内容，提取并推断出结构化的【全维学生就业能力画像】。

### 核心任务
将简历内容转化为严格符合以下 JSON Schema 的数据。如果简历中缺少某些信息（如抗压能力、职业价值观），请根据用户的经历细节进行【合理推断】。

### 输出 JSON 结构要求
```json
{
  "basic_info": {
    "name": "姓名",
    "gender": "性别（男/女/其他/不便透露，无则填null）",
    "university": "学校（无则填null）",
    "major": "专业",
    "education_level": "学历(本科/硕士/博士)",
    "graduation_year": 2025
  },
  "career_intent": {
    "expected_salary": "期望薪资(如 15k-20k，无则null)",
    "job_preferences": ["意向岗位1", "意向岗位2"],
    "target_cities": ["意向城市1", "意向城市2"]
  },
  "competencies": {
    "professional_skills": {
      "score": 8, 
      "keywords": ["Python", "Java"], 
      "evidence": "项目经历或证书证明",
      "gap_analysis": "与大厂要求相比的不足之处"
    },
    "certificate_requirements": {
      "score": 7, 
      "items": ["CET-6", "PMP"],
      "missing": ["建议考取的证书"]
    },
    "innovation_capability": {
      "score": 8,
      "evidence": "评分依据",
      "gap_analysis": "差距分析（无则null）"
    },
    "learning_capability": {
      "score": 8,
      "evidence": "评分依据",
      "gap_analysis": "差距分析（无则null）"
    },
    "stress_resistance": {
      "score": 8,
      "evidence": "评分依据",
      "gap_analysis": "差距分析（无则null）"
    },
    "communication_skills": {
      "score": 8,
      "evidence": "评分依据",
      "gap_analysis": "差距分析（无则null）"
    },
    "internship_experience": {
      "score": 8,
      "history": [{"company": "A公司", "position": "岗位", "duration": "3个月"}],
      "evaluation": "实习含金量评价（无则null）"
    }
  },
  "experiences": {
    "projects": [{"name": "项目名", "role": "角色", "tech_stack": ["技术栈"], "achievement": "成果"}],
    "awards": ["奖项1", "奖项2"],
    "main_courses": ["核心课程列表"],
    "campus_experience": "校园经历（无则null）",
    "social_practice": "社会实践描述（无则null）"
  },
  "personality": {
    "mbti": "推断的MBTI(如INTJ，无则null)",
    "strengths": ["性格优势1"],
    "weaknesses": ["性格劣势1"]
  }
}
```

### 注意事项
1. **评分标准 (score)**：必须为 0-10 的整数。10分=行业顶尖，6分=合格，0分=完全缺失。
2. **推断能力**：例如，如果用户有“ACM金牌”经历，则“学习能力”和“创新能力”应给高分。
3. **严格JSON**：只输出 JSON 字符串，不要包含 Markdown 代码块标记。
4. **字符串与引号（极其重要）**：所有 JSON 字符串值内禁止使用英文双引号字符 "；如需引用内容请用中文引号「」或『』，或使用逗号改写，否则会导致解析失败。
"""

_JSON_REPAIR_SYSTEM = (
    "你是一个 JSON 修复器。用户会给你一段损坏的 JSON（常见错误：字符串里含有未转义的英文双引号、尾部截断、多余逗号）。"
    "请只输出一段可被标准 json.loads 解析的完整 JSON 对象，保留原意与字段结构，不要 Markdown，不要解释。"
)


def _extract_balanced_json_object(text: str) -> str | None:
    """从文本中提取第一个花括号配平的 JSON 对象子串（比贪婪正则更可靠）。"""
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start : i + 1]
    return None


def _parse_json_loose(raw: str) -> Dict[str, Any]:
    """清洗后依次尝试：整段解析、配平子串解析。"""
    s = (raw or "").replace("```json", "").replace("```", "").strip()
    if not s:
        raise json.JSONDecodeError("empty", s, 0)
    try:
        out = json.loads(s)
        if isinstance(out, dict):
            return out
    except json.JSONDecodeError:
        pass
    blob = _extract_balanced_json_object(s)
    if blob:
        out = json.loads(blob)
        if isinstance(out, dict):
            return out
    raise json.JSONDecodeError("no valid object", s, 0)


async def _repair_json_with_llm(broken_snippet: str) -> str:
    """调用 LLM 将损坏的 JSON 修成合法 JSON 文本（仅文本，无代码块）。"""
    snippet = (broken_snippet or "")[:14000]
    response = await client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[
            {"role": "system", "content": _JSON_REPAIR_SYSTEM},
            {
                "role": "user",
                "content": "请修复以下内容为合法 JSON 对象（StudentProfile 结构），字符串内的英文双引号必须写成 \"。\n\n"
                + snippet,
            },
        ],
        response_format={"type": "json_object"},
        temperature=0.0,
    )
    return (response.choices[0].message.content or "").strip()


async def get_structured_resume_data(resume_text: str) -> StudentProfile:
    """
    调用大模型解析简历，返回标准化的 StudentProfile 对象
    """
    try:
        logger.info("正在调用 LLM 进行简历深度解析...")
        
        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3", 
            messages=[
                {"role": "system", "content": "你是一个严格的 JSON 数据提取助手。"},
                {"role": "user", "content": f"{STUDENT_PROFILE_PROMPT}\n\n待解析简历原文：\n{resume_text}"}
            ],
            response_format={ 'type': 'json_object' },
            temperature=0.1  # 低温度以保证格式稳定
        )
        
        raw_content = (response.choices[0].message.content or "").strip()

        data_dict: Dict[str, Any] | None = None
        try:
            data_dict = _parse_json_loose(raw_content)
        except json.JSONDecodeError as e1:
            logger.warning("简历 JSON 首次解析失败，尝试 LLM 修复: %s", e1)
            try:
                fixed = await _repair_json_with_llm(raw_content)
                data_dict = _parse_json_loose(fixed)
            except Exception as e2:
                logger.error(
                    "Failed to parse JSON. Raw head: %s...",
                    raw_content[:800],
                )
                raise ValueError(f"LLM 返回了无效的 JSON 格式: {e1}") from e2

        if not isinstance(data_dict, dict):
            raise ValueError("LLM 返回的根节点不是 JSON 对象")

        # --- Pydantic 模型验证 ---
        # 这一步会自动进行类型检查和必要字段校验
        profile = StudentProfile(**data_dict)
        logger.info(f"简历解析成功: {profile.basic_info.name}")
        
        return profile

    except Exception as e:
        logger.error(f"简历解析服务异常: {str(e)}", exc_info=True)
        # 抛出异常由上层处理，不再静默返回 None
        raise e


async def generate_study_plan_for_gap(
    student: StudentProfile,
    target_job: Dict[str, Any],
    focus: Dict[str, Any],
    stage: str,
    duration_months: int,
    effort_label: str,
) -> Dict[str, Any]:
    """
    基于单个核心缺口，调用大模型生成结构化的学习与实践计划内容。
    仅负责“Content”，不做任何业务决策。
    """
    dimension_key = str(focus.get("dimension_key", "")).strip()
    dimension_label = str(focus.get("dimension_label", "")).strip()
    fit_percent = float(focus.get("fit_percent", 0.0) or 0.0)

    stage_label = "短期" if stage == "short_term" else "中期"
    student_name = student.basic_info.name
    major = student.basic_info.major
    edu = student.basic_info.education_level
    job_title = str(target_job.get("title", "")).strip()

    # 将 0-100 契合度近似映射为“学生得分”“岗位要求分”
    # 简化假设：岗位要求为 9/10，学生得分按契合度线性缩放
    job_score_10 = 9.0
    student_score_10 = round(job_score_10 * fit_percent / 100.0, 1)
    gap_10 = max(0.0, job_score_10 - student_score_10)

    user_prompt = f"""
你是一名资深职业规划教练，擅长为大学生制定可落地的学习与实践计划。

【学生与岗位背景】
- 学生姓名：{student_name}
- 专业：{major}，学历：{edu}
- 目标岗位：{job_title}
- 当前维度：[{dimension_label}] 学生估算得分约为 {student_score_10} / 10，目标岗位要求约为 {job_score_10} / 10，相差约 {gap_10} 分。
- 规划阶段：{stage_label}（持续 {duration_months} 个月）
- 每周可投入时间：约 {effort_label}

【你的任务】
围绕上述「{dimension_label}」这一维度，为学生制定一个为期 {duration_months} 个月的具体计划，重点填补这一差距。要求：
1. 计划必须可执行、具体，不要空洞口号。
2. 学习部分至少包含 2-4 个学习主题，每个主题要写清楚“学什么、用什么资源、预期能做到什么”。
3. 实践部分至少设计 1-3 个可以在简历上写出来的实践任务（项目 / 实习 / 模拟面试等），每个任务需要有明确的“可交付成果”。
4. 至少设计 1 个可交付的项目 Demo（给出简短名称），并说明该 Demo 与目标岗位的关联。

【输出格式（严格 JSON，禁止出现 Markdown 代码块标记）】
请严格按照下面的 JSON 结构返回内容：
{{
  "learning_items": [
    {{
      "topic": "学习主题，例如：FastAPI 入门与实战",
      "category": "skill | certificate | soft",
      "estimated_effort_per_week": "例如：{effort_label}",
      "resources": ["资源 1（如官方文档 / 课程）", "资源 2"],
      "outcome": "完成什么成果，例如：掌握基础增删改查接口并能部署到云端"
    }}
  ],
  "practice_items": [
    {{
      "type": "项目 | 实习 | 面试",
      "task": "具体任务，例如：实现一个 XX 管理系统的后端 API",
      "deliverable": "产出物，例如：GitHub 仓库 + README + 演示视频链接"
    }}
  ],
  "summary": "用一小段话总结该阶段的重点，例如：本阶段核心目标是补齐后端开发的实战经验……"
}}
"""

    try:
        logger.info(
            "正在调用 LLM 生成学习计划: student=%s, job=%s, dim=%s, stage=%s",
            student_name,
            job_title,
            dimension_key,
            stage,
        )

        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严格按照给定 JSON Schema 输出的职业规划助手。",
                },
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )

        raw_content = response.choices[0].message.content or ""
        raw_content = raw_content.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", raw_content, re.DOTALL)
            if not match:
                raise ValueError("LLM 返回格式无法解析为 JSON")
            data = json.loads(match.group(1))

        if not isinstance(data, dict):
            raise ValueError("LLM 返回的根节点不是对象")

        # 简单兜底，保证 key 存在
        if "learning_items" not in data or not isinstance(data.get("learning_items"), list):
            data["learning_items"] = []
        if "practice_items" not in data or not isinstance(data.get("practice_items"), list):
            data["practice_items"] = []
        if "summary" not in data or not isinstance(data.get("summary"), str):
            data["summary"] = ""

        return data
    except Exception as e:
        logger.error(f"生成学习计划 LLM 调用异常: {str(e)}", exc_info=True)
        # 失败时返回空结构，由上层回退到规则版计划
        return {
            "learning_items": [],
            "practice_items": [],
            "summary": "",
            "error": str(e),
        }


async def pick_and_explain_career_path(
    student: StudentProfile,
    target_job: Dict[str, Any],
    match_detail: Dict[str, Any],
    market_trend: Dict[str, Any],
    candidate_paths: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    在规则生成的候选路径集合中，调用大模型选择“最推荐路径 + 备选路径”，并给出解释。
    大模型只能在 candidate_paths 范围内选择，不允许发明新路径。
    """
    if not candidate_paths:
        return {}

    dims = (match_detail.get("details", {}) or {}).get("dimensions", {}) or {}
    base = float(dims.get("base", 0.0) or 0.0)
    skill = float(dims.get("skill", 0.0) or 0.0)
    soft = float(dims.get("soft", 0.0) or 0.0)
    potential = float(dims.get("potential", 0.0) or 0.0)

    student_name = student.basic_info.name
    major = student.basic_info.major
    edu = student.basic_info.education_level
    job_title = str(target_job.get("title", "")).strip()

    mt = market_trend or {}
    demand_level = mt.get("demand_level", "待补充")
    trend_direction = mt.get("trend_direction", "待补充")

    candidate_paths_json = json.dumps(candidate_paths, ensure_ascii=False, indent=2)
    market_trend_json = json.dumps(mt, ensure_ascii=False, indent=2)

    user_prompt = f"""
你是一名严谨的职业发展规划顾问。现在需要在给定的“候选职业路径集合”中，为这位学生选出最合适的路径，并解释原因。

【学生画像摘要】
- 姓名：{student_name}
- 专业/学历：{major} / {edu}
- 目标岗位：{job_title}
- 人岗匹配四维得分（0-100）：基础要求 {base}，职业技能 {skill}，职业素养 {soft}，发展潜力 {potential}

【市场信号】
{market_trend_json}

【候选路径集合】
下面是系统根据岗位图谱和规则筛选出的候选路径。注意：
- 你只能在这些路径中选择，禁止发明任何新的路径或岗位。
- 每条路径包含 id、type（vertical/lateral）、title、nodes（岗位名称序列）、required_skills（如有）、trade_off（利弊）。

{candidate_paths_json}

【你的任务】
1. 综合学生画像、人岗匹配维度和市场信号，从候选路径中选出 1 条“最推荐路径”（best_path），以及最多 2 条“可考虑的备选路径”（secondary_paths，可以为空数组）。
2. 对每条被提及的路径，解释“为什么适合 / 适合什么类型的学生”，请结合：
   - 路径类型（vertical 垂直晋升 / lateral 换岗）
   - 路径中涉及的岗位序列（nodes）
   - 对基础/技能/素养/潜力四个维度的要求
   - 市场需求和趋势（demand_level, trend_direction, trade_off）
3. 如果某些路径虽然存在，但不推荐当前学生优先选择，可以在解释中点出“风险或前置条件”。

【输出格式（严格 JSON，禁止出现 Markdown 代码块标记）】
请严格按照下面的 JSON 结构返回内容：
{{
  "best_path_id": "候选路径中的 id，例如 path_vertical_0",
  "secondary_path_ids": ["path_lateral_1"],
  "overall_summary": "用 2-4 句话总结整体判断，例如：基于你当前的职业技能和发展潜力，更建议你沿着 XXX 方向垂直发展……",
  "path_explanations": [
    {{
      "path_id": "path_vertical_0",
      "why": "为什么这条路径适合当前学生（结合优势、匹配维度、市场趋势等）",
      "fit_for": "适合什么类型的同学，例如：已经有一定后端基础、希望长期深耕技术方向的同学"
    }}
  ],
  "risk_and_opportunity": [
    "优势：例如该路径岗位需求稳定，对你目前的技能结构友好……",
    "风险：例如对某个维度要求较高（如沟通/项目管理），需要在中长期补齐……"
  ]
}}
"""

    try:
        logger.info(
            "正在调用 LLM 进行职业路径决策: student=%s, job=%s, candidates=%d",
            student_name,
            job_title,
            len(candidate_paths),
        )

        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个只在给定候选路径集合中做选择的职业规划顾问，必须严格按指定 JSON Schema 输出。",
                },
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        raw_content = response.choices[0].message.content or ""
        raw_content = raw_content.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(raw_content)
        except json.JSONDecodeError:
            match = re.search(r"(\{.*\})", raw_content, re.DOTALL)
            if not match:
                raise ValueError("LLM 返回格式无法解析为 JSON")
            data = json.loads(match.group(1))

        if not isinstance(data, dict):
            raise ValueError("LLM 返回的根节点不是对象")

        # 兜底字段
        if "best_path_id" not in data or not isinstance(data.get("best_path_id"), str):
            data["best_path_id"] = ""
        if "secondary_path_ids" not in data or not isinstance(data.get("secondary_path_ids"), list):
            data["secondary_path_ids"] = []
        if "overall_summary" not in data or not isinstance(data.get("overall_summary"), str):
            data["overall_summary"] = ""
        if "path_explanations" not in data or not isinstance(data.get("path_explanations"), list):
            data["path_explanations"] = []
        if "risk_and_opportunity" not in data or not isinstance(data.get("risk_and_opportunity"), list):
            data["risk_and_opportunity"] = []

        return data
    except Exception as e:
        logger.error(f"职业路径决策 LLM 调用异常: {str(e)}", exc_info=True)
        return {
            "best_path_id": "",
            "secondary_path_ids": [],
            "overall_summary": "",
            "path_explanations": [],
            "risk_and_opportunity": [],
            "error": str(e),
        }


async def polish_full_career_report(
    student: StudentProfile,
    target_job: Dict[str, Any],
    match_detail: Dict[str, Any],
    module_1: Dict[str, Any],
    module_2: Dict[str, Any],
    module_3: Dict[str, Any],
) -> Dict[str, Any]:
    """
    基于模块 1/2/3 的结构化结果，调用大模型生成一份自然语言版的完整职业规划报告。
    仅做“润色与组织”，不改变原有结论。
    """
    student_name = student.basic_info.name
    major = student.basic_info.major
    edu = student.basic_info.education_level
    job_title = str(target_job.get("title", "")).strip()

    dims = (match_detail.get("details", {}) or {}).get("dimensions", {}) or {}
    base = float(dims.get("base", 0.0) or 0.0)
    skill = float(dims.get("skill", 0.0) or 0.0)
    soft = float(dims.get("soft", 0.0) or 0.0)
    potential = float(dims.get("potential", 0.0) or 0.0)

    overall_m1 = (module_1 or {}).get("overall_conclusion", {}) if isinstance(module_1, dict) else {}
    judgement_text = str(overall_m1.get("judgement", "")).strip()

    # 为防止 prompt 过长，只传模块的关键部分
    safe_m1 = {
        "profile_overview": (module_1 or {}).get("profile_overview", {}),
        "target_job_overview": (module_1 or {}).get("target_job_overview", {}),
        "overall_conclusion": overall_m1,
    } if isinstance(module_1, dict) else {}
    safe_m2 = {
        "market_trend": (module_2 or {}).get("market_trend", {}),
        "career_paths": {
            "path_options": ((module_2 or {}).get("career_paths", {}) or {}).get("path_options", []),
            "recommended_path": ((module_2 or {}).get("career_paths", {}) or {}).get("recommended_path", {}),
            "llm_commentary": ((module_2 or {}).get("career_paths", {}) or {}).get("llm_commentary", {}),
        },
    } if isinstance(module_2, dict) else {}
    safe_m3 = {
        "selected_plan": (module_3 or {}).get("selected_plan", {}),
        "plan_mode": (module_3 or {}).get("plan_mode", {}),
    } if isinstance(module_3, dict) else {}

    m1_json = json.dumps(safe_m1, ensure_ascii=False, indent=2)
    m2_json = json.dumps(safe_m2, ensure_ascii=False, indent=2)
    m3_json = json.dumps(safe_m3, ensure_ascii=False, indent=2)

    user_prompt = f"""
你现在扮演一位资深职业发展顾问，请基于系统已经生成的结构化分析结果，为这位学生写一份完整的职业规划报告，面向学生本人阅读。

【学生与目标岗位基本信息】
- 姓名：{student_name}
- 专业/学历：{major} / {edu}
- 目标岗位：{job_title}
- 人岗匹配四维得分（0-100）：基础要求 {base}，职业技能 {skill}，职业素养 {soft}，发展潜力 {potential}

【模块一：人岗匹配分析摘要（结构化 JSON）】
{m1_json}

【模块二：职业路径与市场信号（结构化 JSON）】
{m2_json}

【模块三：学习与实践行动计划（结构化 JSON）】
{m3_json}

【写作要求】
1. 报告的读者是学生本人，语气专业但友好，避免官话空话。
2. 报告结构要相对完整和丰富，建议包含（可以适当合并）：
   - 开篇概览：用一小节概括当前整体匹配情况和报告会解决什么问题；
   - 当前画像与优势/短板：结合模块一的七维能力和总体结论，分点说明优势和需要关注的地方；
   - 人岗匹配解读：结合四维得分与模块一结论，解释“为什么是中度/高度匹配”“哪些地方拉高了分数，哪些地方是风险点”；
   - 推荐职业路径说明：基于模块二中推荐路径和 LLM 决策结果，从“这条路径是什么”“为什么适合你”“还有哪些备选方向”三个角度展开；
   - 短期行动计划（3–6 个月）：基于模块三短期计划，详细说明应该学哪些知识、做哪些实践项目、如何量化进展（不要发明新主题，只能使用 JSON 中已有的 learning_path / practice_plan 信息，允许对已有条目进行拆解和解释）；
   - 中期行动计划（6–12 个月）：基于模块三中期计划，说明如何在已有基础上「深化/升级」，同样只能引用已有 JSON 信息；
   - 复盘与迭代建议：根据模块三中的 evaluation 和 adjustment_rules，用自然语言解释如何定期复盘、如何根据评估结果调整。
3. 必须 **严格基于上述 JSON 里的结论和字段**，禁止主观“发明”任何新的经历、技能、证书、项目、路径或数值：
   - 可以对 JSON 里的内容进行重组、展开说明、举例说明（例如引用某个项目经历、某个技能关键词）；
   - 但不可以添加 JSON 里没有出现的新技能名称、新证书名称、新岗位名称、新路径或新时间长度；
   - 不可以改变匹配结论、推荐路径或学习计划的核心方向，只能用更丰富的语言来解释和串联。
4. 字数上允许相对详细（例如 1500–2500 字），但要保持条理清晰、段落分明，适合学生完整阅读和收藏使用。
5. 重点做到“可读、可理解、可执行”：用自然语言解释各模块的要点，并串联成一个整体故事，让学生看完之后“知道自己是谁”“适合去哪”“短期/中期具体该怎么做”。

【输出格式】
只输出一段 Markdown 文本，不要包含任何 JSON，也不要重复粘贴上面的结构化数据。
"""

    try:
        logger.info(
            "正在调用 LLM 进行整份报告润色: student=%s, job=%s",
            student_name,
            job_title,
        )

        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {
                    "role": "system",
                    "content": "你是一名善于写作的职业发展顾问，擅长将结构化分析结果整理成易读的规划报告。",
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.5,
        )

        content = response.choices[0].message.content or ""
        return {
            "polished_markdown": content.strip(),
        }
    except Exception as e:
        logger.error(f"整份报告润色 LLM 调用异常: {str(e)}", exc_info=True)
        return {
            "polished_markdown": "",
            "error": str(e),
        }

async def extract_intake_patch_v2(
    target_fields: List[str],
    user_answer: str,
    intake_data: Dict[str, Any],
    field_schema_hints: Dict[str, Any],
    question_text: str = "",
) -> Dict[str, Any]:
    """
    动态问答采集：在给定 target_fields 范围内抽取 patch。
    - 只允许抽取 target_fields 相关字段
    - 不允许编造
    - 输出包含 need_clarification/clarify_question 以支持追问
    """
    tf = [str(x).strip() for x in (target_fields or []) if str(x).strip()]
    ans = str(user_answer or "").strip()
    current_json = json.dumps(intake_data or {}, ensure_ascii=False, indent=2)
    schema_json = json.dumps(field_schema_hints or {}, ensure_ascii=False, indent=2)

    user_prompt = f"""
你是一个严格的结构化信息抽取助手，正在通过“问答”方式收集学生简历信息。

【本轮目标字段 target_fields】
{json.dumps(tf, ensure_ascii=False)}

【字段结构提示（JSON）】
{schema_json}

【当前问题（可选）】
{str(question_text or "").strip()}

【用户回答】
{ans}

【当前已收集的信息（JSON）】
{current_json}

【抽取规则（非常重要）】
1. 你只能从“用户回答”中抽取信息，禁止编造任何经历、项目、奖项、证书、课程、技能、公司名称等。
2. 只输出与 target_fields 相关的 patch；不要补全其他字段。
3. 如果信息不足或表达模糊，请把 need_clarification 设为 true，并给出 clarify_question（一句自然追问）；不要瞎猜。
4. 输出必须是严格 JSON（不要 Markdown 代码块）。
5. patch 必须是嵌套 JSON 对象：用 basic_info、career_intent、competencies、experiences 等层级组织字段。
   禁止在 patch 顶层使用带点号的扁平键名（错误：{{"basic_info.name":"张三"}}；正确：{{"basic_info":{{"name":"张三"}}}}）。

【输出格式（严格 JSON）】
{{
  "patch": {{}},
  "confidence": 0.0,
  "need_clarification": false,
  "clarify_question": "",
  "notes": ""
}}
"""

    try:
        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": "你是一个只做抽取、不做生成的 JSON 抽取器。"},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )

        raw = (response.choices[0].message.content or "").strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"(\{.*\})", raw, re.DOTALL)
            if not m:
                raise ValueError("LLM 返回格式无法解析为 JSON")
            data = json.loads(m.group(1))

        if not isinstance(data, dict):
            raise ValueError("LLM 返回根节点不是对象")

        patch = data.get("patch")
        if not isinstance(patch, dict):
            patch = {}
        notes = data.get("notes")
        if not isinstance(notes, str):
            notes = ""
        conf = data.get("confidence")
        try:
            confidence = float(conf)
        except Exception:
            confidence = 0.0
        need = data.get("need_clarification")
        need_clarification = bool(need) if isinstance(need, (bool, int)) else False
        cq = data.get("clarify_question")
        clarify_question = cq if isinstance(cq, str) else ""

        return {
            "patch": patch,
            "confidence": confidence,
            "need_clarification": need_clarification,
            "clarify_question": clarify_question,
            "notes": notes,
        }
    except Exception as e:
        logger.error(f"问答抽取(v2) LLM 调用异常: {str(e)}", exc_info=True)
        return {
            "patch": {},
            "confidence": 0.0,
            "need_clarification": False,
            "clarify_question": "",
            "notes": "",
            "error": str(e),
        }


async def generate_next_question(
    missing_fields: List[str],
    asked_fields: List[str],
    intake_data: Dict[str, Any],
    question_templates: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    动态生成下一问：
    - LLM 在程序给定的 question_templates（候选问法集合）中做选择并改写成更自然的问题
    - 输出必须包含 target_fields（missing_fields 的子集）
    """
    mf = [str(x).strip() for x in (missing_fields or []) if str(x).strip()]
    af = [str(x).strip() for x in (asked_fields or []) if str(x).strip()]
    current_json = json.dumps(intake_data or {}, ensure_ascii=False, indent=2)
    templates_json = json.dumps(question_templates or [], ensure_ascii=False, indent=2)

    user_prompt = f"""
你是一名对话式信息采集助手，需要通过自然对话收集学生简历关键信息。

【缺失字段 missing_fields（必须从这里选择要问的目标）】
{json.dumps(mf, ensure_ascii=False)}

【已问过/已覆盖字段 asked_fields（尽量避免重复问同一件事）】
{json.dumps(af, ensure_ascii=False)}

【当前已收集信息（JSON）】
{current_json}

【可用的“问题模板库”（JSON 数组）】
每个模板包含：
- template_id
- target_fields（该模板希望收集的字段集合）
- base_question（基础问法）
- examples（示例）
- quick_options（快捷选项）
- actions（可选：快捷操作，如跳转到岗位画像详情页）

请从模板库中选择最适合当前 missing_fields 的一个模板，并把它改写成更自然、更像聊天的提问。
要求：
1. target_fields 必须是 missing_fields 的子集，并尽量少而明确（1-3个字段）。
2. assistant_message 要自然、友好，不要像表单，不要强制格式。
3. 可以给 1-3 个 examples（可选），帮助用户理解怎么回答。
4. quick_options 给 0-4 个常见快捷选项（如：无/不清楚/先跳过）；求职意向类问题不要提供「暂不填写」。
5. 如模板提供 actions，可保留或做轻微改写；actions 用于前端渲染按钮/链接，不要发明不存在的 action 类型。
6. 输出必须严格 JSON（不要 Markdown）。

模板库如下：
{templates_json}

【输出格式（严格 JSON）】
{{
  "question_id": "auto_xxx",
  "target_fields": ["experiences.projects"],
  "assistant_message": "自然语言问题",
  "examples": ["示例1", "示例2"],
  "quick_options": ["无", "不清楚", "先跳过"],
  "actions": [
    {{"type": "open_job_profile_detail", "label": "查看岗位画像详情", "payload": {{}}}}
  ]
}}
"""

    try:
        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": "你是一个只负责生成下一问的对话助手，必须严格按 JSON 输出。"},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.6,
        )

        raw = (response.choices[0].message.content or "").strip()
        raw = raw.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"(\{.*\})", raw, re.DOTALL)
            if not m:
                raise ValueError("LLM 返回格式无法解析为 JSON")
            data = json.loads(m.group(1))

        if not isinstance(data, dict):
            raise ValueError("LLM 返回根节点不是对象")

        qid = data.get("question_id")
        if not isinstance(qid, str) or not qid.strip():
            qid = "auto_question"
        tfs = data.get("target_fields")
        if not isinstance(tfs, list):
            tfs = []
        tfs = [str(x).strip() for x in tfs if str(x).strip()]
        msg = data.get("assistant_message")
        if not isinstance(msg, str):
            msg = ""
        ex = data.get("examples")
        if not isinstance(ex, list):
            ex = []
        ex = [str(x).strip() for x in ex if str(x).strip()][:3]
        qo = data.get("quick_options")
        if not isinstance(qo, list):
            qo = []
        qo = [str(x).strip() for x in qo if str(x).strip()][:4]

        actions = data.get("actions")
        if not isinstance(actions, list):
            actions = []
        cleaned_actions = []
        for a in actions[:4]:
            if not isinstance(a, dict):
                continue
            at = a.get("type")
            lab = a.get("label")
            if not isinstance(at, str) or not at.strip():
                continue
            if not isinstance(lab, str) or not lab.strip():
                continue
            payload = a.get("payload")
            if not isinstance(payload, dict):
                payload = {}
            cleaned_actions.append({"type": at.strip(), "label": lab.strip(), "payload": payload})

        return {
            "question_id": qid,
            "target_fields": tfs,
            "assistant_message": msg.strip(),
            "examples": ex,
            "quick_options": qo,
            "actions": cleaned_actions,
        }
    except Exception as e:
        logger.error(f"下一问生成 LLM 调用异常: {str(e)}", exc_info=True)
        return {"error": str(e)}


async def build_student_profile_from_intake(intake_data: Dict[str, Any]) -> StudentProfile:
    """
    问答采集结束后：基于 intake_data（结构化原材料），调用大模型生成完整 StudentProfile。
    目标：
    - 输出严格符合 StudentProfile schema
    - competencies 的 7 维必须给出 0-10 score + evidence（基于 intake_data 的证据）
    - 不允许编造不存在的项目/经历/奖项/证书；若缺失则低分并说明缺失
    """
    src_json = json.dumps(intake_data or {}, ensure_ascii=False, indent=2)

    user_prompt = f"""
你是一名严谨的职业规划专家。下面给出的是通过问答采集到的学生信息（结构化 JSON）。
你的任务是：在不编造任何事实的前提下，将这些信息转化为严格符合 StudentProfile 的 JSON。

【输入：问答采集信息（JSON）】
{src_json}

【硬性要求（非常重要）】
1. 只能使用输入 JSON 中出现的信息，禁止编造任何新的项目/实习/奖项/证书/课程/技能/公司名称等。
2. 必须输出严格符合 StudentProfile 的 JSON（不要 Markdown 代码块）。
3. competencies 的 7 个维度必须输出 score（0-10整数）与 evidence（证据链）：
   - 如果输入里没有对应证据，score 必须给低分（0-3），并在 evidence 中说明“缺少客观证据/信息不足”。
   - professional_skills.keywords：从输入的技能关键词中提取；若缺失则空数组。
   - certificate_requirements.items：从输入证书中提取；missing 可给出“建议补充”的证书，但必须用“建议”表述，不要当成已获得。
   - internship_experience.history：从输入的实习/实践经历中结构化；evaluation 必须基于输入描述，不足则写“信息不足，建议补充实习细节”。
4. career_intent.expected_salary 必须来自用户明确回答（如具体范围、面议、10k左右等）；禁止输出「暂不填写」；若输入中确实无此信息则填「面议」并在 evidence 中说明信息不足。
4.1 career_intent.target_cities 必须来自用户明确回答（至少一个城市或如「全国」「一线」等概括）；禁止用「暂不填写」作为唯一元素。
5. experiences.main_courses / campus_experience：如输入有则填入，没有则留空/空数组。

【关于可选/缺失字段的明确规则】
以下字段在输入中可能不存在，这是正常的问答采集限制，你必须自行补全：
- basic_info.university：若输入无院校信息，写 null。
- competencies.innovation_capability / learning_capability / stress_resistance / communication_skills：
  - 如果输入 JSON 的 competencies 节点下存在 xxx.evidence（字符串）且非空，则据此推断 score（4-7）和 evidence；
  - 如果 xxx.evidence 为空或不存在，则 score 填 1，evidence 填「信息不足，无法评估」。
- competencies.internship_experience.evaluation：若输入无实习信息，写 null。
- personality：如果输入中有 mbti/strengths/weaknesses 则填入，否则设为 null / 空数组。
- experiences.social_practice：如果输入中有则填入，没有则写 null。

【输出格式】
只输出 JSON 对象。
"""

    response = await client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",
        messages=[
            {"role": "system", "content": "你是一个严格输出 StudentProfile JSON 的助手。"},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    raw = (response.choices[0].message.content or "").strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"(\{.*\})", raw, re.DOTALL)
        if not m:
            raise ValueError("LLM 返回格式无法解析为 JSON")
        data = json.loads(m.group(1))

    profile = StudentProfile(**data)
    return profile


# ===========================================================
# 行动计划生成（替代技能库查表，改为 LLM 规划）
# ===========================================================


async def generate_action_plan_for_gaps(
    student: StudentProfile,
    target_job: Dict[str, Any],
    match_detail: Dict[str, Any],
    module_1: Dict[str, Any],
    module_2: Optional[Dict[str, Any]],
    plan_preferences: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    基于阶段一（人岗匹配分析）、阶段二（职业路径）以及个人画像与岗位画像之间的差距，
    调用大模型生成完整的短期/中期行动计划。

    输入信息包括：
    - 学生画像（StudentProfile）
    - 目标岗位画像（target_job）
    - 四维匹配详情（match_detail）
    - 模块一：人岗匹配分析摘要（module_1）
    - 模块二：职业路径建议（module_2，可选）
    - 用户偏好 plan_preferences（如每周可投入时间）

    输出结构与原 action_plan_generator 保持一致，保证计划表格内容不变。
    """
    prefs = plan_preferences or {}

    # --- 拼装学生背景 ---
    student_name = student.basic_info.name or "学生"
    major = student.basic_info.major or ""
    edu = student.basic_info.education_level or ""
    grad_year = student.basic_info.graduation_year or 0
    job_title = str(target_job.get("title", "")).strip()

    # --- 提取四维分数 ---
    dims = (match_detail.get("details", {}) or {}).get("dimensions", {}) or {}

    def _f(k: str) -> float:
        try:
            return float(dims.get(k, 0.0) or 0.0)
        except Exception:
            return 0.0

    base_score = _f("base")
    skill_score = _f("skill")
    soft_score = _f("soft")
    potential_score = _f("potential")

    # --- 计算剩余时间 ---
    from datetime import datetime
    now = datetime.now()
    cur_yr = now.year
    cur_mo = now.month
    grad_month = 7
    remaining_months = (grad_year - cur_yr) * 12 + (grad_month - cur_mo)
    remaining_months = max(0, remaining_months - 1)  # 保留 1 个月缓冲

    short_months = max(3, remaining_months // 2) if remaining_months > 6 else remaining_months
    mid_months = max(0, remaining_months - short_months)

    effort_short = prefs.get("effort_short", "10-12 小时/周")
    effort_mid = prefs.get("effort_mid", "10-12 小时/周")

    # --- 提取模块一关键信息 ---
    m1 = module_1 or {}
    strengths = m1.get("strengths", [])
    gaps = m1.get("gaps", [])
    strengths_text = ", ".join([s.get("dimension_label", "") for s in strengths]) or "暂无"
    gaps_text = ", ".join([g.get("dimension_label", "") for g in gaps]) or "暂无"

    strengths_detail = []
    for s in strengths:
        dim = s.get("dimension_label", "")
        student_s = s.get("student_score", 0)
        target_s = s.get("target_score", 0)
        evidence = s.get("evidence", "暂无具体证据")
        strengths_detail.append(f"  - {dim}（学生 {student_s} / 目标 {target_s}）：{evidence}")

    gaps_detail = []
    for g in gaps:
        dim = g.get("dimension_label", "")
        student_s = g.get("student_score", 0)
        target_s = g.get("target_score", 0)
        evidence = g.get("evidence", "暂无具体证据")
        gaps_detail.append(f"  - {dim}（学生 {student_s} / 目标 {target_s}）：{evidence}")

    # --- 提取模块二职业路径 ---
    m2 = module_2 or {}
    career_paths = m2.get("career_paths") or {}
    recommended_path = career_paths.get("recommended_path") or {}
    path_type = recommended_path.get("type", "未明确")
    path_title = recommended_path.get("title", "未明确")

    # --- 学生技能关键词 ---
    student_skills = student.competencies.professional_skills.keywords or []
    skills_text = "、".join(student_skills) if student_skills else "暂无"

    # --- 岗位技能要求 ---
    job_prof = target_job.get("professional_skills") or {}
    job_skill_list = job_prof.get("keywords", []) if isinstance(job_prof, dict) else []
    if isinstance(job_skill_list, str):
        job_skill_list = [job_skill_list]
    job_skills_text = "、".join(job_skill_list) if job_skill_list else "暂无"

    user_prompt = f"""
你是资深职业规划教练，擅长基于人岗匹配分析（阶段一）和职业路径规划（阶段二），
为学生制定有针对性、可落地的短期/中期行动计划。

【学生基本信息】
- 姓名：{student_name}
- 专业/学历：{major} / {edu}
- 毕业年份：{grad_year} 年
- 目标岗位：{job_title}
- 当前掌握技能：{skills_text}

【目标岗位关键要求】
- 岗位名称：{job_title}
- 核心技能要求：{job_skills_text}
- 推荐职业路径：{path_title}（类型：{path_type}）

【人岗四维匹配得分】（0-100，100 为岗位要求满分）
- 基础要求：{base_score} 分
- 职业技能：{skill_score} 分
- 职业素养：{soft_score} 分
- 发展潜力：{potential_score} 分

【阶段一分析结果】
优势维度：
{chr(10).join(strengths_detail) if strengths_detail else "  暂无明显优势"}

差距维度：
{chr(10).join(gaps_detail) if gaps_detail else "  暂无明显差距"}

【阶段二职业路径】
- 推荐路径：{path_title}
- 路径类型：{path_type}

【时间规划】
- 距离毕业约 {remaining_months} 个月
- 短期计划：前 {short_months} 个月（每周投入 {effort_short}）
- 中期计划：后 {mid_months} 个月（每周投入 {effort_mid}）
  （若 mid_months = 0，则只规划短期）

【你的任务】
请基于以上信息，为学生制定：
1. **短期行动计划**（前 {short_months} 个月）：针对最紧急的 1-2 个差距维度，具体学什么、用什么资源、做什么项目
2. **中期行动计划**（{'后 ' + str(mid_months) + ' 个月' if mid_months > 0 else '无中期计划（剩余时间不足）'}）：在短期基础上深化或拓展

要求：
- 短期计划：专注 1-2 个高优先级差距维度（如"必须达标"或"优先攻克"象限），要具体到技能名称
- 中期计划：在已有基础上进一步提升，可涉及职业路径上的下一个节点能力
- 每个阶段必须包含：学习主题、对应维度、理由（为什么选这个维度）、学习内容（具体技能/知识点）、成果验收指标
- 学习内容必须紧密围绕学生已有技能和岗位要求的差距来设计，禁止引入岗位要求之外的全新技能方向
- 成果验收指标要可量化（如：能独立完成 XX 操作、在 GitHub 上线 XX 项目、通过 XX 认证）

【输出格式（严格 JSON，禁止 Markdown 代码块）】
请严格返回以下 JSON 结构：
{{
  "short_term": {{
    "dimension_keys": ["维度key"],
    "dimension_labels": ["维度中文名"],
    "total_gap": 数值,
    "goals": ["目标1", "目标2"],
    "skills": [
      {{
        "skill": "具体技能名",
        "tier": "entry | intermediate | advanced",
        "tier_label": "入门 | 进阶 | 精进",
        "duration_weeks": 数字,
        "goal": "学习目标描述",
        "project": {{"name": "项目名", "description": "项目简介", "features": ["功能1", "功能2"]}},
        "resume": "可写进简历的一句话"
      }}
    ]
  }},
  "mid_term": {{
    "dimension_keys": ["维度key"],
    "dimension_labels": ["维度中文名"],
    "total_gap": 数值,
    "goals": ["目标1", "目标2"],
    "skills": [
      {{
        "skill": "具体技能名",
        "tier": "entry | intermediate | advanced",
        "tier_label": "入门 | 进阶 | 精进",
        "duration_weeks": 数字,
        "goal": "学习目标描述",
        "project": {{"name": "项目名", "description": "项目简介", "features": ["功能1", "功能2"]}},
        "resume": "可写进简历的一句话"
      }}
    ]
  }}
}}
"""

    try:
        logger.info(
            "调用 LLM 生成行动计划: student=%s, job=%s, remaining=%d months",
            student_name,
            job_title,
            remaining_months,
        )

        response = await client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个严格按照 JSON Schema 输出行动计划的职业规划助手。输出必须是合法 JSON，不含 Markdown 代码块。",
                },
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.4,
        )

        raw = (response.choices[0].message.content or "").strip()
        raw = raw.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            m = re.search(r"(\{.*\})", raw, re.DOTALL)
            if not m:
                raise ValueError("LLM 返回格式无法解析为 JSON")
            data = json.loads(m.group(1))

        if not isinstance(data, dict):
            raise ValueError("LLM 返回根节点不是对象")

        # 兜底字段
        def _ensure_keys(obj, short_or_mid):
            if not isinstance(obj, dict):
                return {
                    "dimension_keys": [],
                    "dimension_labels": [],
                    "total_gap": 0,
                    "goals": [],
                    "skills": [],
                }
            skills = obj.get("skills") or []
            if not isinstance(skills, list):
                obj["skills"] = []
            for s in obj["skills"]:
                if not isinstance(s, dict):
                    continue
                s.setdefault("tier", "entry")
                s.setdefault("tier_label", "入门")
                s.setdefault("duration_weeks", 4)
                s.setdefault("goal", "")
                s.setdefault("resume", "")
                proj = s.get("project")
                if isinstance(proj, dict):
                    proj.setdefault("name", "")
                    proj.setdefault("description", "")
                    proj.setdefault("features", [])
                else:
                    s["project"] = {"name": "", "description": "", "features": []}
            obj.setdefault("dimension_keys", [])
            obj.setdefault("dimension_labels", [])
            obj.setdefault("total_gap", 0)
            obj.setdefault("goals", [])
            return obj

        short_data = _ensure_keys(data.get("short_term"), "short")
        mid_data = _ensure_keys(data.get("mid_term"), "mid")

        return {
            "short_term": short_data,
            "mid_term": mid_data,
            "remaining_months": remaining_months,
            "short_term_months": short_months,
            "mid_term_months": mid_months,
        }

    except Exception as e:
        logger.error("行动计划 LLM 生成异常: %s", str(e), exc_info=True)
        # 失败时返回空结构，上层可兜底
        return {
            "short_term": {
                "dimension_keys": [],
                "dimension_labels": [],
                "total_gap": 0,
                "goals": [],
                "skills": [],
            },
            "mid_term": {
                "dimension_keys": [],
                "dimension_labels": [],
                "total_gap": 0,
                "goals": [],
                "skills": [],
            },
            "remaining_months": remaining_months,
            "short_term_months": short_months,
            "mid_term_months": mid_months,
            "error": str(e),
        }
