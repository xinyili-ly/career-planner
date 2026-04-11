# -*- coding: utf-8 -*-
"""
技能学习路径生成器

核心逻辑：
1. 命中预设库：差距技能在 Top 50 中，直接使用预定义的学习路径
2. 未命中预设库：触发 LLM 实时生成（降级方案）
"""
import json
import os
import logging
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("SkillPathGenerator")

client = AsyncOpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url=os.getenv("LLM_BASE_URL")
)

# 预定义的 Top 50 技能路径文件
LEARNING_PATHS_FILE = os.path.join(
    os.path.dirname(__file__), "..", "data", "skill_learning_paths.json"
)

# 维度标签映射
DIM_LABELS = {
    "base": "基础要求",
    "skill": "专业技能",
    "soft": "职业素养",
    "potential": "发展潜力",
    "experience": "实习经历",
    "project": "项目经验",
}

# 技能类别判断关键词
SOFT_SKILL_KEYWORDS = {"沟通", "协作", "表达", "领导", "团队", "管理", "时间管理", "学习方法", "文档", "简历", "面试"}
CERTIFICATE_KEYWORDS = {"证书", "认证", "资格", "考试"}
EXPERIENCE_KEYWORDS = {"实习", "工作", "兼职", "项目经历"}
PROJECT_KEYWORDS = {"项目", "demo", "作品"}


def _get_skill_category(skill_name: str, tags: str = "") -> str:
    """根据技能名称和标签判断类别"""
    combined = skill_name + tags
    if any(kw in combined for kw in CERTIFICATE_KEYWORDS):
        return "certificate"
    if any(kw in combined for kw in SOFT_SKILL_KEYWORDS):
        return "soft"
    if any(kw in combined for kw in EXPERIENCE_KEYWORDS):
        return "experience"
    if any(kw in combined for kw in PROJECT_KEYWORDS):
        return "project"
    return "skill"


def _load_learning_paths() -> Dict[str, Any]:
    """加载预定义的学习路径库"""
    if not os.path.exists(LEARNING_PATHS_FILE):
        return {"learning_paths": {}}

    try:
        with open(LEARNING_PATHS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"加载学习路径库失败: {e}")
        return {"learning_paths": {}}


def is_skill_in_top50(skill_name: str) -> bool:
    """检查技能是否在 Top 50 预设库中"""
    paths = _load_learning_paths()
    learning_paths = paths.get("learning_paths", {})
    return skill_name in learning_paths


def get_skill_learning_path(
    skill_name: str,
    tier: str = "entry",
    default: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """
    获取指定技能的学习路径

    优先级：
    1. 从预定义的 Top 50 技能路径中查找
    2. 如果未找到，返回 default
    """
    paths = _load_learning_paths()
    learning_paths = paths.get("learning_paths", {})

    if skill_name not in learning_paths:
        logger.debug(f"技能 '{skill_name}' 不在预定义库中，使用默认路径")
        return default

    skill_path = learning_paths[skill_name]
    tiers = skill_path.get("tiers", {})

    return tiers.get(tier, default)


def load_learning_paths() -> Dict[str, Any]:
    """加载已生成的学习路径库（兼容旧接口）"""
    return _load_learning_paths()


async def _generate_learning_path_for_skill_llm(
    skill_name: str,
    category: str,
    dimension: str = "",
) -> Dict[str, Any]:
    """
    调用 LLM 生成单个技能的学习路径（降级方案）
    """
    prompt = f"""
你是学习路径规划专家。请为以下技能生成标准化的三档学习路径。

【技能词】：{skill_name}
【技能类别】：{category}
【所属维度】：{dimension}

【输出要求】
针对 entry（入门）、intermediate（进阶）、advanced（精进）三档，每档输出：

1. duration_weeks: 学习时长（周数，每档不超过4周）
2. goal: 学习目标描述
3. weekly_plan: 每周学习内容列表
4. resources: 学习资源字典
   - official: 官方文档/教材
   - courses: 在线课程推荐
   - practice: 实战练习资源
5. acceptance: 三类验收指标

【技能类别对应的验收指标要求】

如果是 skill（技术技能）：
- skill: 能独立完成XX操作/代码编写/配置部署
- project: 可交付的 Demo 名称 + 简介 + 核心功能列表
- resume: 可写进简历的简短描述

如果是 soft（职业素养）：
- skill: 能在XX场景中稳定体现该能力
- project: 场景化练习/案例分析
- resume: 能说出一个具体体现该能力的事件

【输出格式】
严格 JSON，不要 Markdown 代码块：
{{
  "skill_name": "{skill_name}",
  "category": "{category}",
  "tiers": {{
    "entry": {{
      "duration_weeks": 4,
      "goal": "...",
      "weekly_plan": ["...", "...", "...", "..."],
      "resources": {{"official": "...", "courses": ["..."], "practice": "..."}},
      "acceptance": {{"skill": {{"criteria": "..."}}, "project": {{"name": "...", "description": "...", "features": ["..."]}}, "resume": "..."}}
    }},
    "intermediate": {{...}},
    "advanced": {{...}}
  }}
}}
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3",
            messages=[
                {"role": "system", "content": "你是一个严格输出 JSON 的学习路径规划专家。"},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
        )

        raw = response.choices[0].message.content or ""
        raw = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(raw)

        if "tiers" not in data:
            data["tiers"] = {}

        return data

    except Exception as e:
        logger.error(f"LLM 生成学习路径失败: {skill_name}, error: {e}")
        return {
            "skill_name": skill_name,
            "category": category,
            "tiers": {},
            "error": str(e)
        }


def get_skill_learning_path_with_fallback(
    skill_name: str,
    tier: str = "entry",
    category: str = "skill",
    dimension: str = "",
) -> Dict[str, Any]:
    """
    获取技能学习路径（含降级逻辑）

    参数：
    - skill_name: 技能名称
    - tier: 学习档位（entry/intermediate/advanced）
    - category: 技能类别
    - dimension: 所属维度

    逻辑：
    1. 先从预定义库查找
    2. 如果未找到，生成一个通用模板路径
    """
    # 1. 尝试从预定义库获取
    predefined = get_skill_learning_path(skill_name, tier)
    if predefined:
        return predefined

    # 2. 生成通用模板（未命中预设库的降级方案）
    logger.info(f"技能 '{skill_name}' 未在预定义库中，生成通用模板")

    return _generate_generic_template(skill_name, tier, category)


def _generate_generic_template(
    skill_name: str,
    tier: str,
    category: str,
) -> Dict[str, Any]:
    """
    为未在预设库中的技能生成通用模板
    """
    tier_labels = {"entry": "入门", "intermediate": "进阶", "advanced": "精进"}
    tier_label = tier_labels.get(tier, "入门")

    # 根据类别生成不同的模板
    if category == "soft":
        return {
            "duration_weeks": 4,
            "goal": f"掌握{skill_name}基础",
            "weekly_plan": [
                f"第1周：{skill_name}概念与重要性",
                f"第2周：{skill_name}核心方法",
                f"第3周：{skill_name}实践练习",
                f"第4周：{skill_name}场景应用"
            ],
            "resources": {
                "official": "相关书籍/课程",
                "courses": ["在线课程"],
                "practice": "实际场景练习"
            },
            "acceptance": {
                "skill": {"criteria": f"能稳定体现{skill_name}能力"},
                "project": {"name": f"{skill_name}练习", "description": f"{skill_name}实践案例", "features": ["案例分析"]},
                "resume": f"具备{skill_name}能力"
            }
        }
    else:
        return {
            "duration_weeks": 4,
            "goal": f"掌握{skill_name}基础",
            "weekly_plan": [
                f"第1周：{skill_name}基础概念与环境搭建",
                f"第2周：{skill_name}核心语法/功能",
                f"第3周：{skill_name}进阶特性",
                f"第4周：{skill_name}项目实战"
            ],
            "resources": {
                "official": "官方文档",
                "courses": ["在线教程"],
                "practice": "项目实战"
            },
            "acceptance": {
                "skill": {"criteria": f"能独立完成{skill_name}相关任务"},
                "project": {"name": f"{skill_name}项目", "description": f"{skill_name}实战项目", "features": ["核心功能"]},
                "resume": f"掌握{skill_name}"
            }
        }


async def generate_skill_learning_paths(
    skills: Optional[List[str]] = None,
    max_skills: int = 50,
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """
    批量生成技能学习路径

    参数：
    - skills: 指定要生成的技能列表，None 表示从技能表读取所有
    - max_skills: 最大生成数量（防止 API 调用过多）
    - output_path: 输出文件路径

    注意：此方法主要用于补充预定义库之外的技能
    建议使用 get_skill_learning_path_with_fallback 进行单技能查询
    """
    pools = _load_skill_pools()

    items_to_process = []

    if skills:
        for skill in skills[:max_skills]:
            items_to_process.append({
                "name": skill,
                "category": _get_skill_category(skill),
                "dimension": "skill"
            })
    else:
        skill_lib = pools.get("skill_library", [])
        for item in skill_lib[:max_skills]:
            name = item.get("skill_name", "")
            dim = item.get("dimension", "")
            tags = item.get("skill_tags", "")

            if name and not is_skill_in_top50(name):
                items_to_process.append({
                    "name": name,
                    "category": _get_skill_category(name, tags),
                    "dimension": dim
                })

    logger.info(f"开始生成 {len(items_to_process)} 个技能的学习路径...")

    learning_paths = {}
    for i, item in enumerate(items_to_process):
        name = item["name"]
        logger.info(f"[{i+1}/{len(items_to_process)}] 生成: {name}")

        path = await _generate_learning_path_for_skill_llm(
            skill_name=name,
            category=item["category"],
            dimension=item["dimension"],
        )

        learning_paths[name] = path

    if output_path is None:
        output_path = LEARNING_PATHS_FILE

    result = {
        "generated_at": "",
        "total_skills": len(learning_paths),
        "learning_paths": learning_paths
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    logger.info(f"学习路径库已保存到: {output_path}")

    return result


def _load_skill_pools() -> Dict[str, Any]:
    """加载结构化技能表"""
    data_path = os.path.join(os.path.dirname(__file__), "..", "data", "skill_pools_structured.json")
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_top_50_skills() -> List[str]:
    """获取 Top 50 技能列表"""
    paths = _load_learning_paths()
    learning_paths = paths.get("learning_paths", {})
    return list(learning_paths.keys())


if __name__ == "__main__":
    # 测试
    print("=== Top 50 技能列表 ===")
    top_50 = get_top_50_skills()
    print(f"共 {len(top_50)} 个技能")
    for i, skill in enumerate(top_50[:10]):
        print(f"  {i+1}. {skill}")

    print("\n=== 测试获取学习路径 ===")
    path = get_skill_learning_path("Java", "intermediate")
    if path:
        print(f"Java (进阶): {path.get('goal', '')}")
    else:
        print("Java 未在预定义库中")
