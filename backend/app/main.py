import shutil
import os
import copy
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from uuid import UUID, uuid4
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.utils.extractor import extract_text_from_pdf, extract_text_from_docx
from app.utils.llm_client import (
    get_structured_resume_data,
    extract_intake_patch_v2,
    generate_next_question,
    build_student_profile_from_intake,
)
from app.models.student_profile import StudentProfile

# 动态导入匹配逻辑
from app.utils.matcher import load_jobs, calculate_match
from app.utils.career_report_module1 import generate_module_1
from app.utils.career_report_module2 import generate_module_2
from app.utils.career_report_module3 import generate_module_3
from app.utils.career_report_module4 import generate_module_4
from app.api import positions

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CareerAgent")

app = FastAPI(title="职业规划智能体后端")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 请求/响应模型 ---

class MatchReportRequest(BaseModel):
    student_profile: Optional[StudentProfile] = None
    profile_cache_id: Optional[str] = None
    job_id: str
    plan_preferences: Optional[Dict[str, str]] = None


class MatchDetailRequest(BaseModel):
    """与 MatchReportRequest 相同画像解析方式，仅返回匹配详情（供雷达图等，不生成完整报告）。"""

    student_profile: Optional[StudentProfile] = None
    profile_cache_id: Optional[str] = None
    job_id: str


class ManualParseRequest(BaseModel):
    resume_text: str


class IntakeStartResponse(BaseModel):
    session_id: str
    question: Dict[str, Any]
    intake_data: Dict[str, Any]
    missing_fields: List[str]
    optional_missing_fields: List[str] = []
    warnings: List[str] = []


class IntakeAnswerRequest(BaseModel):
    session_id: str
    answer: str


class IntakeAnswerResponse(BaseModel):
    session_id: str
    question: Optional[Dict[str, Any]] = None
    is_complete: bool
    intake_data: Dict[str, Any]
    notes: Optional[str] = None
    missing_fields: List[str] = []
    optional_missing_fields: List[str] = []
    warnings: List[str] = []


class IntakeFinishRequest(BaseModel):
    session_id: str


class IntakeStartFromProfileRequest(BaseModel):
    student_profile: StudentProfile


class IntakeStartFromProfileCacheRequest(BaseModel):
    """用解析接口返回的 profile_cache_id 开 intake；画像缓存在 data/.profile_cache 下，多进程可共读。"""

    profile_cache_id: str


# 解析简历后暂存画像：落盘 + 本进程内存，便于多 worker / reload 子进程间共享
_PROFILE_CACHE_MAX = 128
_PROFILE_CACHE: Dict[str, Dict[str, Any]] = {}
_PROFILE_CACHE_DIR = Path(__file__).resolve().parent / "data" / ".profile_cache"


def _canonical_profile_cache_token(raw: Optional[str]) -> Optional[str]:
    if not raw or not str(raw).strip():
        return None
    try:
        return str(UUID(str(raw).strip()))
    except ValueError:
        return None


def _evict_profile_cache_files() -> None:
    _PROFILE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(_PROFILE_CACHE_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime)
    while len(files) >= _PROFILE_CACHE_MAX:
        oldest = files.pop(0)
        try:
            oldest.unlink(missing_ok=True)
        except OSError:
            pass
        _PROFILE_CACHE.pop(oldest.stem, None)


def _store_profile_cache(profile_dict: Dict[str, Any]) -> str:
    _evict_profile_cache_files()
    token = str(uuid4())
    _PROFILE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = _PROFILE_CACHE_DIR / f"{token}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(profile_dict, f, ensure_ascii=False)
    _PROFILE_CACHE[token] = profile_dict
    return token


def _load_profile_cache(raw_token: str) -> Optional[Dict[str, Any]]:
    token = _canonical_profile_cache_token(raw_token)
    if not token:
        return None
    if token in _PROFILE_CACHE:
        return _PROFILE_CACHE[token]
    path = _PROFILE_CACHE_DIR / f"{token}.json"
    if not path.is_file():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        _PROFILE_CACHE[token] = data
        return data
    except Exception as e:
        logger.warning("读取 profile 缓存文件失败: %s", e)
        return None



def _match_level_label(score: float) -> str:
    if score >= 80:
        return "高度匹配"
    if score >= 60:
        return "中度匹配"
    return "低度匹配"


# --- 核心业务逻辑 ---
async def _process_resume_to_leaderboard(text: str):
    """
    阶段一：简历解析 -> 生成岗位适配度榜单
    """
    # 1. 文本校验
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="简历内容为空，请检查文件")
    
    logger.info(f"解析简历文本长度: {len(text)}")

    # 2. AI 解析 (全维画像)
    try:
        student_profile = await get_structured_resume_data(text)
    except Exception as e:
        logger.error(f"AI解析失败: {e}", exc_info=True)
        # 这里可以构建一个空的兜底 Profile，但为了演示效果，直接抛出更直观
        raise HTTPException(status_code=500, detail=f"简历解析失败: {str(e)}")

    # 3. 计算完整度 (根据 7 大维度是否有分)
    # 逻辑：只要有分数 > 0 就算有效
    comp = student_profile.competencies
    valid_scores = [
        comp.professional_skills.score,
        comp.certificate_requirements.score,
        comp.innovation_capability.score,
        comp.learning_capability.score,
        comp.stress_resistance.score,
        comp.communication_skills.score,
        comp.internship_experience.score
    ]
    completeness_score = round((len([s for s in valid_scores if s > 0]) / 7) * 100, 1)
    
    # 竞争力评分 (7维度的平均分 * 10) -> 0-100
    competitiveness_score = round((sum(valid_scores) / 7) * 10, 1)

    # 4. 生成岗位榜单 (Leaderboard)
    all_jobs = load_jobs()
    leaderboard = []
    
    for job in all_jobs:
        match_result = calculate_match(student_profile, job)
        # 只保留关键信息，减少传输量
        if match_result["match_score"] > 0: # 过滤掉完全不匹配的
            leaderboard.append({
                "job_id": match_result["job_id"],
                "title": match_result["title"],
                "match_score": match_result["match_score"],
                "tags": list(job.get("weights", {}).keys()) # 转换为列表以支持 JSON 序列化
            })
            
    # 按分数降序
    leaderboard.sort(key=lambda x: x["match_score"], reverse=True)

    profile_dump = student_profile.model_dump(mode="json")
    profile_cache_id = _store_profile_cache(profile_dump)

    return {
        "student_profile": profile_dump,  # 返回给前端缓存，用于第二阶段
        "profile_cache_id": profile_cache_id,  # 推荐：intake/start_from_profile_cache（与同机磁盘缓存对应）
        "analysis_summary": {
            "completeness": completeness_score,
            "competitiveness": competitiveness_score,
            "overall_comment": "简历解析完成。建议针对目标岗位补充具体项目经历。" 
        },
        "recommended_jobs": leaderboard[:3], # AI 强推 Top 3
        "other_jobs": leaderboard[3:],       # 其余岗位，供用户在“其他”中选择
        "leaderboard": leaderboard[:10]      # (保留旧字段兼容性，可选)
    }


async def _process_student_profile_to_leaderboard(student_profile: StudentProfile):
    """
    阶段一（问答版）：已拿到 StudentProfile -> 生成岗位适配度榜单
    """
    comp = student_profile.competencies
    valid_scores = [
        comp.professional_skills.score,
        comp.certificate_requirements.score,
        comp.innovation_capability.score,
        comp.learning_capability.score,
        comp.stress_resistance.score,
        comp.communication_skills.score,
        comp.internship_experience.score,
    ]
    completeness_score = round((len([s for s in valid_scores if s > 0]) / 7) * 100, 1)
    competitiveness_score = round((sum(valid_scores) / 7) * 10, 1)

    all_jobs = load_jobs()
    leaderboard = []
    for job in all_jobs:
        match_result = calculate_match(student_profile, job)
        if match_result["match_score"] > 0:
            leaderboard.append(
                {
                    "job_id": match_result["job_id"],
                    "title": match_result["title"],
                    "match_score": match_result["match_score"],
                    "tags": list(job.get("weights", {}).keys()),
                }
            )
    leaderboard.sort(key=lambda x: x["match_score"], reverse=True)

    return {
        "student_profile": student_profile.model_dump(mode="json"),
        "analysis_summary": {
            "completeness": completeness_score,
            "competitiveness": competitiveness_score,
            "overall_comment": "信息采集完成，已生成岗位适配度榜单。",
        },
        "recommended_jobs": leaderboard[:3],
        "other_jobs": leaderboard[3:],
        "leaderboard": leaderboard[:10],
    }


def _build_question_fallback(templates: List[Dict[str, Any]]) -> Dict[str, Any]:
    t = templates[0] if templates else _QUESTION_TEMPLATES[0]
    return {
        "question_id": t.get("template_id", "fallback"),
        "target_fields": t.get("target_fields", []),
        "assistant_message": t.get("base_question", ""),
        "examples": t.get("examples", []),
        "quick_options": t.get("quick_options", []),
        "actions": t.get("actions", []),
    }


async def _start_intake_session(intake_data: Dict[str, Any]) -> Dict[str, Any]:
    session_id = str(uuid4())
    if isinstance(intake_data, dict):
        _normalize_intake_nested_keys(intake_data)
    core_missing, optional_missing, warnings = _compute_missing_fields(intake_data)
    missing_fields = core_missing if core_missing else optional_missing
    templates = _pick_templates_for_missing(missing_fields, asked_fields=[])
    q = await generate_next_question(
        missing_fields=missing_fields,
        asked_fields=[],
        intake_data=intake_data,
        question_templates=templates,
    )
    if not isinstance(q, dict) or not q.get("assistant_message") or not q.get("target_fields"):
        q = _build_question_fallback(templates)

    _INTAKE_SESSIONS[session_id] = {
        "intake_data": intake_data,
        "history": [{"role": "assistant", "question": q}],
        "missing_fields": missing_fields,
        "core_missing_fields": core_missing,
        "optional_missing_fields": optional_missing,
        "warnings": warnings,
        "asked_fields": [],
        "nudged_optional_fields": [],
        "current_question": q,
        "turn": 0,
        "status": "collecting",
        "review_status": "pending",       # pending → in_review → done（最终补全确认阶段）
        "review_fields_queue": [],        # 待补全字段队列
        "review_turn": 0,
    }
    return {
        "session_id": session_id,
        "question": q,
        "intake_data": intake_data,
        "missing_fields": missing_fields,
        "optional_missing_fields": optional_missing,
        "warnings": warnings,
    }


def _intake_data_from_student_profile(profile: StudentProfile) -> Dict[str, Any]:
    """
    将已解析出的 StudentProfile 转换为问答采集 intake_data 的“原材料格式”，用于继续补全。
    注意：这里不做评分/推断，只做字段映射。
    """
    p = profile
    data: Dict[str, Any] = {
        "basic_info": {
            "name": p.basic_info.name,
            "gender": p.basic_info.gender,
            "education_level": p.basic_info.education_level,
            "major": p.basic_info.major,
            "graduation_year": p.basic_info.graduation_year,
        },
        "career_intent": {
            "job_preferences": p.career_intent.job_preferences,
            "target_cities": p.career_intent.target_cities,
            "expected_salary": p.career_intent.expected_salary,
        },
        "competencies": {
            "professional_skills": {
                "keywords": p.competencies.professional_skills.keywords,
            },
            "certificate_requirements": {
                "items": p.competencies.certificate_requirements.items,
            },
            "internship_experience": {
                "history": p.competencies.internship_experience.history,
            },
            # 新增软技能维度：按 CompetencyItem 嵌套格式存储 evidence，
            # normalize 后会变成 competencies.innovation_capability.evidence 等正确路径
            "innovation_capability": {
                "evidence": p.competencies.innovation_capability.evidence,
            },
            "learning_capability": {
                "evidence": p.competencies.learning_capability.evidence,
            },
            "stress_resistance": {
                "evidence": p.competencies.stress_resistance.evidence,
            },
            "communication_skills": {
                "evidence": p.competencies.communication_skills.evidence,
            },
        },
        "experiences": {
            "main_courses": p.experiences.main_courses,
            "projects": [x.model_dump(mode="json") for x in p.experiences.projects],
            "awards": p.experiences.awards,
            "campus_experience": p.experiences.campus_experience,
            "social_practice": p.experiences.social_practice,
        },
        "personality": {
            "mbti": p.personality.mbti if p.personality else None,
            "strengths": p.personality.strengths if p.personality else [],
            "weaknesses": p.personality.weaknesses if p.personality else [],
        },
    }
    _normalize_intake_nested_keys(data)
    return data


def _profile_missing_hint(profile: StudentProfile) -> Dict[str, Any]:
    """
    针对“文件解析得到的 StudentProfile”，给出缺失项提示（供前端提示用户补充）。
    这里的缺失项只用于提示，不影响后续流程。
    """
    missing_sections: List[Dict[str, Any]] = []
    warnings: List[str] = []

    # 项目
    if not profile.experiences.projects:
        missing_sections.append(
            {
                "key": "projects",
                "label": "项目经历",
                "why_it_matters": "项目经历是专业技能与工程化能力的重要证据，会影响匹配解释与行动计划的具体性。",
                "suggested_action": "可补充 1-2 个代表性项目：你负责什么、用了哪些技术、结果是什么。",
            }
        )
    # 实习/实践
    if not (profile.competencies.internship_experience.history or []):
        missing_sections.append(
            {
                "key": "internship_practice",
                "label": "实习/实践经历",
                "why_it_matters": "实习/实践是岗位落地能力的重要证据，会影响“实习经历”维度评分与路径建议。",
                "suggested_action": "可补充实习/实践：公司/岗位/周期/做了什么/产出（没有也可填“无”）。",
            }
        )
    # 证书
    if not (profile.competencies.certificate_requirements.items or []):
        missing_sections.append(
            {
                "key": "certificates",
                "label": "证书/认证",
                "why_it_matters": "证书是基础门槛与学习投入的辅助证据，会影响“基础要求”维度的解释。",
                "suggested_action": "可补充英语/软考/厂商认证等（没有也可填“无”）。",
            }
        )
    # 主修课程
    if not (profile.experiences.main_courses or []):
        missing_sections.append(
            {
                "key": "main_courses",
                "label": "主修课程",
                "why_it_matters": "课程信息可作为学习能力与基础知识的证据补充，帮助解释优势与差距。",
                "suggested_action": "可补充 3-8 门核心课程（不记得也可填“无”）。",
            }
        )
    # 校园经历
    if not (profile.experiences.campus_experience or "").strip():
        missing_sections.append(
            {
                "key": "campus_experience",
                "label": "校园经历",
                "why_it_matters": "校园经历可以补充沟通协作、组织能力等证据。",
                "suggested_action": "可补充 1-3 条社团/学生工作/志愿活动（没有也可填“无”）。",
            }
        )

    # 期望薪资若为占位值，给 warning
    if not str(profile.career_intent.expected_salary or "").strip():
        warnings.append("期望薪资未填写：会影响报告中“目标设定/计划强度”的个性化程度。")

    return {
        "missing_sections": missing_sections,
        "warnings": warnings,
        "suggested_next_step": "continue_intake" if missing_sections else "proceed",
    }

# --- 接口定义 ---

@app.get("/")
def read_root():
    return {"status": "running", "version": "v2.0-semantic"}

@app.post("/api/v1/student/parse")
async def parse_resume_file(file: UploadFile = File(...)):
    """
    阶段一接口：上传文件 -> 解析 -> 返回榜单
    """
    filename = file.filename.lower()
    if not (filename.endswith('.pdf') or filename.endswith('.docx')):
        raise HTTPException(status_code=400, detail="仅支持 PDF/DOCX 文件")

    temp_path = f"temp_{uuid4().hex}_{os.path.basename(file.filename)}"
    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        text = extract_text_from_pdf(temp_path) if filename.endswith('.pdf') else extract_text_from_docx(temp_path)
        result = await _process_resume_to_leaderboard(text)

        # 额外返回缺失项提示（不改变原有 student_profile/榜单结构）
        try:
            sp = StudentProfile(**(result.get("student_profile") or {}))
            result["missing_hint"] = _profile_missing_hint(sp)
        except Exception:
            result["missing_hint"] = {"missing_sections": [], "warnings": [], "suggested_next_step": "proceed"}

        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"处理异常: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


@app.post("/api/v1/student/parse/manual")
async def parse_resume_text(request: ManualParseRequest):
    """
    阶段一接口（兼容旧流程）：直接提交简历文本 -> 解析 -> 返回榜单
    """
    return await _process_resume_to_leaderboard(request.resume_text)


# --- 问答式信息采集（替代手动简历文字输入） ---
_INTAKE_SESSIONS: Dict[str, Dict[str, Any]] = {}

# 必收字段（以 intake_data 的路径表达）
_CORE_FIELDS: List[str] = [
    "basic_info.name",
    "basic_info.gender",
    "basic_info.education_level",
    "basic_info.major",
    "basic_info.graduation_year",
    "competencies.professional_skills.keywords",
    "career_intent.job_preferences",
    "career_intent.expected_salary",
    "career_intent.target_cities",
]

# 真实场景中允许缺省/可跳过，但会提示用户补充的字段
_OPTIONAL_FIELDS: List[str] = [
    "experiences.main_courses",
    "experiences.projects",
    "competencies.internship_experience.history",
    "experiences.awards",
    "competencies.certificate_requirements.items",
    "experiences.campus_experience",
    "experiences.social_practice",
    "personality.mbti",
    "personality.strengths",
    "personality.weaknesses",
]

# 可选项中的「列表型」字段：空列表 [] 表示用户已答「无」，不得继续当作缺失
_OPTIONAL_LIST_FIELDS: frozenset[str] = frozenset(
    {
        "experiences.main_courses",
        "experiences.projects",
        "competencies.internship_experience.history",
        "experiences.awards",
        "competencies.certificate_requirements.items",
        "personality.strengths",
        "personality.weaknesses",
    }
)

# 最终补全确认时，每类字段的用户友好中文名称
_FIELD_DISPLAY_NAMES: Dict[str, str] = {
    "experiences.main_courses": "主修课程",
    "experiences.projects": "项目经历",
    "competencies.internship_experience.history": "实习/实践经历",
    "experiences.awards": "获奖/竞赛",
    "competencies.certificate_requirements.items": "证书",
    "experiences.campus_experience": "校园经历",
    "experiences.social_practice": "社会实践",
    "personality.mbti": "MBTI 性格",
    "personality.strengths": "个人优势",
    "personality.weaknesses": "个人短板",
}

# 最终补全确认阶段询问的「综合信息」类字段
_REVIEW_ASK_FIELDS: List[str] = [
    "personality.strengths",
    "personality.weaknesses",
]

# 问题模板库（程序护栏 + LLM 自然改写）
_QUESTION_TEMPLATES: List[Dict[str, Any]] = [
    {
        "template_id": "t_basic_name",
        "target_fields": ["basic_info.name"],
        "base_question": "先从简单的开始：我该怎么称呼你？（不方便也可以写“匿名”）",
        "examples": ["张三", "匿名"],
        "quick_options": ["匿名"],
    },
    {
        "template_id": "t_basic_gender",
        "target_fields": ["basic_info.gender"],
        "base_question": "你愿意告诉我你的性别吗？（不便透露也没关系）",
        "examples": ["男", "女", "不便透露"],
        "quick_options": ["不便透露"],
    },
    {
        "template_id": "t_edu_major_year",
        "target_fields": ["basic_info.education_level", "basic_info.major", "basic_info.graduation_year"],
        "base_question": "你现在的学历、专业，以及预计毕业年份分别是什么？你可以像聊天一样说。",
        "examples": ["本科 软件工程 2026", "硕士 计算机科学与技术 2025"],
        "quick_options": ["不清楚"],
    },
    {
        "template_id": "t_skills_keywords",
        "target_fields": ["competencies.professional_skills.keywords"],
        "base_question": "你最常用/最熟的技能关键词有哪些？比如语言、框架、数据库、工具都可以。",
        "examples": ["Python、FastAPI、MySQL、Redis、Docker", "Java SpringBoot MySQL"],
        "quick_options": ["不清楚"],
    },
    {
        "template_id": "t_courses",
        "target_fields": ["experiences.main_courses"],
        "base_question": "你大学/研究生阶段主修或学得最扎实的课程有哪些？列 3–8 门就行。",
        "examples": ["数据结构、操作系统、计算机网络、数据库系统"],
        "quick_options": ["不记得了"],
    },
    {
        "template_id": "t_projects",
        "target_fields": ["experiences.projects"],
        "base_question": "挑 1–2 个你最能代表能力的项目讲讲：你负责什么、用了哪些技术、结果是什么？",
        "examples": ["做了简历解析系统（后端），用 FastAPI+MySQL，实现…，最终…"],
        "quick_options": ["暂无项目"],
    },
    {
        "template_id": "t_internship",
        "target_fields": ["competencies.internship_experience.history"],
        "base_question": "你有没有实习/实践经历？有的话讲讲：在哪、做什么、周期多长、产出是什么；没有也直接说“无”。",
        "examples": ["XX公司 后端实习 3个月，负责…，产出…"],
        "quick_options": ["无"],
    },
    {
        "template_id": "t_intent",
        "target_fields": ["career_intent.job_preferences", "career_intent.target_cities", "career_intent.expected_salary"],
        "base_question": "你现在更想找什么方向的工作？请一次性说明：意向岗位、意向城市、期望薪资（均为必填；薪资可用「面议」「10k左右」等概括，城市可多选）。如果暂时没思路，可以先点下面按钮查看岗位画像，再回来回答。",
        "examples": ["后端开发，北京/深圳，15k-20k", "数据分析，成都，面议"],
        "quick_options": [],
        "actions": [
            {
                "type": "open_job_profile_detail",
                "label": "查看岗位画像详情",
                "payload": {"source": "job_profiles"},
            }
        ],
    },
    {
        "template_id": "t_awards",
        "target_fields": ["experiences.awards"],
        "base_question": "你有比较想展示的获奖/竞赛经历吗？没有也没关系。",
        "examples": ["挑战杯省一等奖", "ACM校赛二等奖"],
        "quick_options": ["无"],
    },
    {
        "template_id": "t_certs",
        "target_fields": ["competencies.certificate_requirements.items"],
        "base_question": "你目前有哪些证书或技能认证？比如英语、软考、厂商认证等。",
        "examples": ["CET-4", "软考中级"],
        "quick_options": ["无"],
    },
    {
        "template_id": "t_campus",
        "target_fields": ["experiences.campus_experience"],
        "base_question": "你在校园里做过哪些事情？比如社团、学生工作、志愿活动等，挑 1–3 条说说。",
        "examples": ["学生会技术部干事，负责…", "社团负责人，组织…"],
        "quick_options": ["无"],
    },
    {
        "template_id": "t_social_practice",
        "target_fields": ["experiences.social_practice"],
        "base_question": "你有没有参加过社会实践、兼职、志愿服务或培训营等经历？说说大概内容就行。",
        "examples": ["暑期支教一个月", "外卖骑手兼职", "线上产品经理训练营"],
        "quick_options": ["无"],
    },
    {
        "template_id": "t_innovation",
        "target_fields": ["competencies.innovation_capability.evidence"],
        "base_question": "你有没有什么创新经历可以分享？比如独立做过的工具、比赛中的新方案、获奖项目、专利等，不需要很正式，聊聊就行。",
        "examples": ["做了一个自动化脚本获奖", "课程设计中提出新方案被老师采纳"],
        "quick_options": ["没有明显创新", "不记得了"],
    },
    {
        "template_id": "t_learning",
        "target_fields": ["competencies.learning_capability.evidence"],
        "base_question": "你是怎么学习新技能/新知识的？有没有自学过什么课程、刷过哪些技术博客或专栏、转专业/跨领域学习的经历？",
        "examples": ["自学了机器学习并在比赛中应用", "通过开源社区学到了 Docker"],
        "quick_options": ["没有特别的自学经历", "不记得了"],
    },
    {
        "template_id": "t_stress",
        "target_fields": ["competencies.stress_resistance.evidence"],
        "base_question": "你遇到压力比较大的情况是怎么扛过来的？比如赶 deadline、期末考试、项目上线前的加班调试等，举个例子说说。",
        "examples": ["期末周同时备考和做项目，最后都完成了", "线上项目 bug 紧急修复，最后按时交付"],
        "quick_options": ["没有特别扛压经历", "不记得了"],
    },
    {
        "template_id": "t_communication",
        "target_fields": ["competencies.communication_skills.evidence"],
        "base_question": "你平时跟人沟通协作多吗？有没有做过小组负责人、答辩汇报、对外协调等工作？举一两个例子。",
        "examples": ["担任课设组长，协调 4 人分工", "多次课堂答辩汇报"],
        "quick_options": ["沟通协作经验不多", "不记得了"],
    },
    {
        "template_id": "t_mbti",
        "target_fields": ["personality.mbti"],
        "base_question": "你了解自己的性格类型吗（MBTI）？知道的话可以写，不知道也可以跳过。",
        "examples": ["INTJ", "ENFP", "不清楚"],
        "quick_options": ["不清楚"],
    },
    {
        "template_id": "t_strengths",
        "target_fields": ["personality.strengths"],
        "base_question": "你觉得自己的核心优势是什么？比如学习速度快、逻辑清晰、有审美感、执行力强、善于沟通等，挑 2–3 条说说。",
        "examples": ["逻辑思维强", "自学能力强", "沟通表达好"],
        "quick_options": ["不太清楚"],
    },
    {
        "template_id": "t_weaknesses",
        "target_fields": ["personality.weaknesses"],
        "base_question": "你觉得自己哪些方面还有提升空间？比如经验不足、英语一般、不太会包装自己、不太敢表达等。",
        "examples": ["项目经验少", "英语口语需提升", "简历包装能力弱"],
        "quick_options": ["暂时想不出来"],
    },
]

# 抽取时给 LLM 的结构提示（只提示本轮 target_fields 涉及到的结构）
_FIELD_SCHEMA_HINTS: Dict[str, Any] = {
    "basic_info.name": "string",
    "basic_info.gender": "string",
    "basic_info.education_level": "string（如：本科/硕士/博士）",
    "basic_info.major": "string（专业全称）",
    "basic_info.graduation_year": "int（年份，如 2026）",
    "competencies.professional_skills.keywords": "string[]（技能关键词数组）",
    "experiences.main_courses": "string[]（课程名数组）",
    "experiences.projects": [
        {"name": "string", "role": "string", "tech_stack": ["string"], "achievement": "string"}
    ],
    "competencies.internship_experience.history": [
        {"company": "string", "position": "string", "duration": "string", "description": "string"}
    ],
    "career_intent.job_preferences": "string[]（意向岗位，至少一项）",
    "career_intent.target_cities": "string[]（意向城市，至少一项；可写「全国」「一线」等概括）",
    "career_intent.expected_salary": "string（必填；如 15k-20k、面议、10k左右）",
    "experiences.awards": "string[]（获奖/竞赛）",
    "competencies.certificate_requirements.items": "string[]（证书列表）",
    "experiences.campus_experience": "string（校园经历文本）",
    "experiences.social_practice": "string（社会实践/兼职/志愿/培训经历文本）",
    "competencies.innovation_capability.evidence": "string（创新能力证据描述）",
    "competencies.learning_capability.evidence": "string（学习能力证据描述）",
    "competencies.stress_resistance.evidence": "string（抗压能力证据描述）",
    "competencies.communication_skills.evidence": "string（沟通能力证据描述）",
    "personality.mbti": "string（如 INTJ、ENFP，不清楚可写「不清楚」）",
    "personality.strengths": "string[]（个人优势关键词列表）",
    "personality.weaknesses": "string[]（个人短板关键词列表）",
}


def _deep_merge(a: Any, b: Any) -> Any:
    if isinstance(a, dict) and isinstance(b, dict):
        out = dict(a)
        for k, v in b.items():
            if k in out:
                out[k] = _deep_merge(out[k], v)
            else:
                out[k] = v
        return out
    # list 默认覆盖（由 LLM 输出整段）
    return b


def _deep_copy_dict(d: Dict[str, Any]) -> Dict[str, Any]:
    """深拷贝嵌套字典"""
    return copy.deepcopy(d)


def _normalize_intake_nested_keys(d: Dict[str, Any]) -> None:
    """
    将 LLM 或历史数据里错误的「扁平带点号键」展开为嵌套结构。
    例如 {"basic_info.name": "张三"} -> {"basic_info": {"name": "张三"}}，
    否则 _get_path(data, "basic_info.name") 永远读不到，会误判整表缺失、重复追问。
    """
    if not isinstance(d, dict):
        return
    for k in list(d.keys()):
        v = d[k]
        if isinstance(k, str) and "." not in k and isinstance(v, dict):
            _normalize_intake_nested_keys(v)
    dot_moves: List[Tuple[str, Any]] = []
    for k in list(d.keys()):
        if isinstance(k, str) and "." in k:
            dot_moves.append((k, d.pop(k)))
    for path, v in dot_moves:
        if isinstance(v, dict):
            _normalize_intake_nested_keys(v)
        _set_path(d, path, v)


def _get_path(d: Dict[str, Any], path: str) -> Any:
    cur: Any = d
    for p in path.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(p)
    return cur


def _is_valid_field_value(v: Any) -> bool:
    """检查字段值是否有效（非空且非'无'类占位值）"""
    explicit_none_values = {"无", "暂无", "没有", "无相关经历", "不清楚", "不记得了", "不便透露", "暂无项目", "暂不填写"}
    
    if v is None:
        return False
    if isinstance(v, str):
        stripped = v.strip()
        if not stripped:
            return False
        if stripped in explicit_none_values:
            return False
        return True
    if isinstance(v, list):
        if len(v) == 0:
            return False
        for item in v:
            if _is_valid_field_value(item):
                return True
        return False
    if isinstance(v, dict):
        return len(v) > 0
    return True


def _set_path(d: Dict[str, Any], path: str, value: Any) -> None:
    """在嵌套字典 d 中按 path（如 a.b.c）写入 value，自动创建中间 dict。"""
    parts = path.split(".")
    cur = d
    for p in parts[:-1]:
        if p not in cur:
            cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value


_EXPLICIT_NONE = {
    "无",
    "暂无",
    "没有",
    "无相关经历",
    "不清楚",
    "不记得了",
    "不便透露",
}


def _is_explicit_none(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return False
        if s in _EXPLICIT_NONE:
            return True
        # 常见口语
        if s.startswith("无") and len(s) <= 6:
            return True
        if "不方便" in s or "不便" in s:
            return True
        return False
    if isinstance(v, list):
        # 若列表里只有“无/暂无”等，也视为明确缺省
        items = [str(x).strip() for x in v if str(x).strip()]
        if not items:
            return False
        return all(x in _EXPLICIT_NONE or (x.startswith("无") and len(x) <= 6) for x in items)
    return False


def _field_missing(intake_data: Dict[str, Any], field: str) -> bool:
    data = intake_data or {}
    v = _get_path(data, field)
    if v is None:
        return True
    if isinstance(v, str):
        return not v.strip()
    if isinstance(v, list):
        return len(v) == 0
    return False


def _core_placeholder_invalid(v: Any) -> bool:
    """必填核心字段：不接受「暂不填写」或仅含该词的列表。"""
    if isinstance(v, str):
        return v.strip() == "暂不填写"
    if isinstance(v, list):
        items = [str(x).strip() for x in v if str(x).strip()]
        if not items:
            return False
        return all(x == "暂不填写" for x in items)
    return False


def _compute_missing_fields(intake_data: Dict[str, Any]) -> Tuple[List[str], List[str], List[str]]:
    """
    更贴近真实场景的缺失判定：
    - core：必须收集到有效内容（不接受「暂不填写」占位）
    - optional：可选项，若用户明确“无/暂无/不便透露”等则不再追问
    - warnings：对明确缺省的可选项给提醒，便于最终报告完整性提示
    """
    data = intake_data or {}
    if isinstance(data, dict):
        _normalize_intake_nested_keys(data)
    core_missing: List[str] = []
    optional_missing: List[str] = []
    warnings: List[str] = []

    for f in _CORE_FIELDS:
        v = _get_path(data, f)
        # 优先级：字段本身为空 → placeholder → 显式缺省
        if _field_missing(data, f):
            core_missing.append(f)
            continue
        if _core_placeholder_invalid(v):
            core_missing.append(f)
            continue
        # 姓名/性别允许「不便透露」算已答；其他核心字段若显式缺省，只记录 warning 不阻止流程
        if _is_explicit_none(v):
            if f not in {"basic_info.name", "basic_info.gender"}:
                warnings.append(f"{f} 为缺省/占位值，建议后续补充以提升画像准确性")

    for f in _OPTIONAL_FIELDS:
        v = _get_path(data, f)
        if f in _OPTIONAL_LIST_FIELDS and isinstance(v, list) and len(v) == 0:
            continue
        if _field_missing(data, f):
            optional_missing.append(f)
            continue
        if _is_explicit_none(v):
            # 用户明确“无/暂无/不便透露”等，不再追问，但给轻提示
            warnings.append(f"{f} 已明确缺省（用户回答为“无/暂无/不便透露”等），将按缺失信息进行保守评估")

    # 替代满足逻辑：项目 / 实习 / 校园经历至少其一「有内容」或「列表已明确答空 []」
    def _exp_lane_ok(field: str) -> bool:
        v = _get_path(data, field)
        if field in _OPTIONAL_LIST_FIELDS and isinstance(v, list) and len(v) == 0:
            return True
        return not _field_missing(data, field)

    exp_ok = (
        _exp_lane_ok("experiences.projects")
        or _exp_lane_ok("competencies.internship_experience.history")
        or _exp_lane_ok("experiences.campus_experience")
    )
    if not exp_ok:
        if "experiences.projects" not in optional_missing:
            optional_missing.insert(0, "experiences.projects")

    return core_missing, optional_missing, warnings


def _pick_templates_for_missing(missing_fields: List[str], asked_fields: List[str] = None) -> List[Dict[str, Any]]:
    asked = set(asked_fields or [])
    mf = set(missing_fields or [])
    # 只考虑还未被问过的字段
    mf = mf - asked
    out = []
    for t in _QUESTION_TEMPLATES:
        tfs = set(t.get("target_fields") or [])
        if tfs.intersection(mf):
            out.append(t)
    # 模板越能覆盖缺失字段越靠前
    out.sort(key=lambda x: len(set(x.get("target_fields") or []).intersection(mf)), reverse=True)
    return out[:8]


@app.post("/api/v1/student/intake/start", response_model=IntakeStartResponse)
async def intake_start():
    return await _start_intake_session({})


@app.post("/api/v1/student/intake/start_from_profile", response_model=IntakeStartResponse)
async def intake_start_from_profile(request: IntakeStartFromProfileRequest):
    """
    从“文件解析得到的 student_profile”继续进入问答补全流程。
    前端可在展示 missing_hint 后让用户选择“继续填写”，然后调用此接口开始补全。

    注意：请求体必须是合法 JSON。若在 Swagger 中整段粘贴 student_profile，易截断或漏逗号导致 422（json_invalid）。
    更稳妥：先调解析接口拿到 profile_cache_id，再调 /intake/start_from_profile_cache。
    """
    intake_data = _intake_data_from_student_profile(request.student_profile)
    return await _start_intake_session(intake_data)


@app.post("/api/v1/student/intake/start_from_profile_cache", response_model=IntakeStartResponse)
async def intake_start_from_profile_cache(request: IntakeStartFromProfileCacheRequest):
    """
    使用 POST /parse 或 /parse/manual 返回的 profile_cache_id 开启 intake，无需在请求里携带完整 student_profile。
    缓存写入本机目录 app/data/.profile_cache/，多 worker 可共享；超过 128 条会按最旧文件淘汰。
    """
    if not _canonical_profile_cache_token(request.profile_cache_id):
        raise HTTPException(status_code=400, detail="profile_cache_id 格式无效，应为标准 UUID（与解析接口返回一致）。")
    raw = _load_profile_cache(request.profile_cache_id)
    if not raw:
        raise HTTPException(
            status_code=404,
            detail="画像缓存不存在或已过期。请确认未换机器/未清空缓存目录，并重新调用简历解析接口获取新的 profile_cache_id。",
        )
    try:
        sp = StudentProfile(**raw)
    except Exception as e:
        logger.warning("profile_cache 反序列化失败: %s", e)
        raise HTTPException(status_code=400, detail=f"缓存中的画像结构无效: {e}")
    intake_data = _intake_data_from_student_profile(sp)
    return await _start_intake_session(intake_data)


@app.post("/api/v1/student/intake/answer", response_model=IntakeAnswerResponse)
async def intake_answer(request: IntakeAnswerRequest):
    session = _INTAKE_SESSIONS.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期，请重新开始")

    intake_data = session.get("intake_data", {}) or {}
    if isinstance(intake_data, dict):
        _normalize_intake_nested_keys(intake_data)
    current_q = session.get("current_question", {}) or {}
    target_fields = current_q.get("target_fields") or []
    asked_fields = session.get("asked_fields", []) or []
    nudged_optional_fields = session.get("nudged_optional_fields", []) or []

    logger.info(f"[Intake Answer] START - session_id={request.session_id[:8]}..., target_fields={target_fields}")
    logger.info(f"[Intake Answer] BEFORE merge - intake_data={intake_data}")

    # 生成本轮 schema hints（只包含 target_fields）
    hints = {k: _FIELD_SCHEMA_HINTS.get(k) for k in target_fields if k in _FIELD_SCHEMA_HINTS}

    llm: Dict[str, Any] = {}
    patch: Dict[str, Any] = {}
    # 快捷选项兜底：如果用户选的就是当前问题的 quick_options，直接写标准值（不走 LLM）
    raw_answer = str(request.answer).strip()
    quick_options = current_q.get("quick_options") or []

    # =========================================================
    # 早期拦截：「最终补全确认」阶段的 review_single 快速回复
    # 必须放在任何条件分支之前，确保无论 is_complete 是否为 True 都能拦截
    # =========================================================
    if session.get("review_status") == "in_review":
        qid = str(current_q.get("question_id") or "")
        if qid.startswith("review_") and raw_answer in {
            "继续", "不需要补充", "不需要", "跳过", "跳过本项", "无", "暂无", "没有",
        }:
            queue: List[str] = session.get("review_fields_queue", [])
            if queue:
                remaining = queue[1:]
                session["review_fields_queue"] = remaining
                session["review_turn"] = int(session.get("review_turn", 0)) + 1
                if remaining:
                    next_f = remaining[0]
                    disp_name = _FIELD_DISPLAY_NAMES.get(next_f, next_f.split('.')[-1])
                    review_t = next(
                        (t for t in _QUESTION_TEMPLATES if next_f in (t.get("target_fields") or [])),
                        None,
                    )
                    if review_t:
                        next_q = {
                            "question_id": "review_single",
                            "target_fields": [next_f],
                            "assistant_message": f"「{disp_name}」这部分需要补充吗？",
                            "examples": review_t.get("examples", []),
                            "quick_options": review_t.get("quick_options", []) + ["继续", "不需要补充"],
                            "actions": review_t.get("actions", []),
                        }
                    else:
                        next_q = {
                            "question_id": "review_single",
                            "target_fields": [next_f],
                            "assistant_message": f"「{disp_name}」可以补充一下吗？（没有也可以直接说“继续”）",
                            "examples": [],
                            "quick_options": ["继续", "不需要补充"],
                            "actions": [],
                        }
                    session["current_question"] = next_q
                    return {
                        "session_id": request.session_id,
                        "question": next_q,
                        "is_complete": False,
                        "intake_data": intake_data,
                        "notes": "",
                        "missing_fields": [],
                        "optional_missing_fields": [],
                        "warnings": [],
                    }
                else:
                    session["review_status"] = "done"
                    session["current_question"] = None
                    return {
                        "session_id": request.session_id,
                        "question": None,
                        "is_complete": True,
                        "intake_data": intake_data,
                        "notes": "",
                        "missing_fields": [],
                        "optional_missing_fields": [],
                        "warnings": [],
                    }
            else:
                session["review_status"] = "done"
                session["current_question"] = None
                return {
                    "session_id": request.session_id,
                    "question": None,
                    "is_complete": True,
                    "intake_data": intake_data,
                    "notes": "",
                    "missing_fields": [],
                    "optional_missing_fields": [],
                    "warnings": [],
                }
    if raw_answer in quick_options:
        if "basic_info.name" in target_fields and raw_answer in {"匿名"}:
            patch = {"basic_info": {"name": "匿名"}}
        elif "basic_info.gender" in target_fields and raw_answer in {"不便透露"}:
            patch = {"basic_info": {"gender": "不便透露"}}
        elif raw_answer == "继续":
            # nudge 追问的「继续」：明确本次放弃该字段，继续下一题
            for f in target_fields:
                if "skills" in f or "projects" in f or "history" in f or "awards" in f or "courses" in f or "items" in f:
                    _set_path(patch, f, [])
                else:
                    _set_path(patch, f, "无")
        elif raw_answer in {"无", "暂无", "没有", "无相关经历", "不清楚", "不记得了", "不便透露", "暂无项目"}:
            # 通用兜底：对可选字段写入明确空值（列表或原文）
            for f in target_fields:
                if f in _CORE_FIELDS:
                    # 核心题点「不清楚/不记得」时也必须写入，否则既不合并也无法标记已问，会死循环重复同一问
                    if raw_answer in {"不清楚", "不记得了"}:
                        if "keywords" in f or "job_preferences" in f or "target_cities" in f:
                            _set_path(patch, f, [raw_answer])
                        else:
                            _set_path(patch, f, raw_answer)
                    continue
                if "skills" in f or "projects" in f or "history" in f or "awards" in f or "courses" in f or "items" in f:
                    _set_path(patch, f, [])
                else:
                    _set_path(patch, f, raw_answer)
    else:
        llm = await extract_intake_patch_v2(
            target_fields=target_fields,
            user_answer=request.answer,
            intake_data=intake_data,
            field_schema_hints=hints,
            question_text=str(current_q.get("assistant_message", "")),
        )
        patch = llm.get("patch") if isinstance(llm, dict) else {}

    patch_norm: Dict[str, Any] = {}
    if isinstance(patch, dict) and patch:
        # LLM 常把路径打成扁平键 basic_info.name，先规范为嵌套再合并/校验
        patch_norm = _deep_copy_dict(patch)
        _normalize_intake_nested_keys(patch_norm)
        # 在合并之前，先清理 patch 中的无效值，避免覆盖 intake_data 中已有的有效值
        cleaned_patch = _deep_copy_dict(patch_norm)
        for f in target_fields:
            parts = f.split(".")
            current = cleaned_patch
            for part in parts[:-1]:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    current = None
                    break
            if current is not None and isinstance(current, dict) and parts[-1] in current:
                if not _is_valid_field_value(current[parts[-1]]):
                    # 如果值无效，从 patch 中移除，避免覆盖有效值
                    del current[parts[-1]]
        intake_data = _deep_merge(intake_data, cleaned_patch)

    if isinstance(intake_data, dict):
        _normalize_intake_nested_keys(intake_data)

    logger.info(f"[Intake Answer] AFTER merge - intake_data={intake_data}")

    # 分析 patch 中每个字段的有效性（用规范嵌套后的结构）
    patch_fields = set()
    explicit_none_values = {"无", "暂无", "没有", "无相关经历", "不清楚", "不记得了", "不便透露", "暂无项目", "暂不填写"}
    
    patch_for_scan = patch_norm
    if isinstance(patch_for_scan, dict) and patch_for_scan:
        for f in target_fields:
            parts = f.split(".")
            current = patch_for_scan
            found = True
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    found = False
                    break
            if found:
                is_valid = False
                if isinstance(current, str):
                    stripped = current.strip()
                    if stripped and stripped not in explicit_none_values:
                        is_valid = True
                elif isinstance(current, list) and len(current) > 0:
                    has_valid = False
                    for item in current:
                        if isinstance(item, str):
                            stripped = str(item).strip()
                            if stripped and stripped not in explicit_none_values:
                                has_valid = True
                                break
                        elif isinstance(item, dict):
                            has_valid = True
                            break
                    if has_valid:
                        is_valid = True
                elif current is not None and not isinstance(current, (str, list)):
                    is_valid = True
                if is_valid:
                    patch_fields.add(f)
    
    logger.info(f"[Intake Answer] patch_fields={patch_fields}")
    
    # 更新 asked_fields
    # - patch_fields：本轮提取到「有效」非空占位的内容
    # - 合并后 intake 上该路径已有值（含「不清楚」等）：视为本题已覆盖，避免重复追问
    # - 可选字段：用户明确跳过（"无"等）也可以标记为已问过
    for f in target_fields:
        if f in asked_fields:
            continue
        if f in patch_fields:
            asked_fields.append(f)
        elif f in _OPTIONAL_FIELDS and raw_answer in {"无", "暂无", "没有", "无相关经历", "不清楚", "不记得了", "暂无项目", "继续"}:
            asked_fields.append(f)
        elif not _field_missing(intake_data, f):
            asked_fields.append(f)
        # review_single 阶段：即使 patch 为空，也要出队（避免死循环）
        elif session.get("review_status") == "in_review" and current_q.get("question_id") == "review_single":
            asked_fields.append(f)

    # 重新计算 missing_fields（程序权威）
    core_missing, optional_missing, warnings = _compute_missing_fields(intake_data)
    # 完成条件：核心字段补齐即可进入完成态；可选项不强制，但会继续“智能追问”
    is_core_complete = len(core_missing) == 0

    # 控制对话长度：核心已完成且可选字段全部处理完才停止
    # 只有当 optional_missing 为空时才停止追问可选字段，不再依赖轮次限制
    if not is_core_complete:
        missing_fields = core_missing
    else:
        missing_fields = optional_missing

    history = session.get("history", []) or []
    history.append({"role": "user", "text": request.answer})
    history.append({"role": "assistant_patch", "patch": patch, "llm_notes": llm.get("notes", "") if isinstance(llm, dict) else ""})

    # 如果 LLM 要求澄清且目标字段仍缺失，则优先追问
    need_clarify = bool(llm.get("need_clarification")) if isinstance(llm, dict) else False
    clarify_q = (llm.get("clarify_question") or "").strip() if isinstance(llm, dict) else ""
    still_missing = any(f in missing_fields for f in target_fields)

    def _optional_explicit_none_followup_fields(tfs: List[str]) -> List[str]:
        out: List[str] = []
        for f in tfs:
            if f not in _OPTIONAL_FIELDS:
                continue
            v = _get_path(intake_data, f)
            if _is_explicit_none(v):
                out.append(f)
        return out

    # 可选项：若用户明确“无/没有”等，追问一遍并说明影响，然后继续其他提问
    nudge_fields = _optional_explicit_none_followup_fields(target_fields)

    if nudge_fields:
        f = nudge_fields[0]
        nudged_optional_fields.append(f)
        impact_map = {
            "experiences.projects": "如果没有项目经历，我们会更保守地评估“专业技能/工程化能力”的证据，报告里的项目案例也会更少。",
            "competencies.internship_experience.history": "如果没有实习/实践经历，我们会更保守地评估“实习经历”维度，职业路径建议会更偏学习/作品集补强。",
            "experiences.awards": "如果没有获奖/竞赛经历，创新与学习能力的证据会更多依赖课程/项目描述。",
            "competencies.certificate_requirements.items": "如果没有证书，我们会把证书维度作为可提升项写入行动计划（不影响你现有技能匹配）。",
            "experiences.campus_experience": "如果没有校园经历，沟通协作的证据会更多依赖项目/实践描述。",
            "experiences.main_courses": "如果不提供课程信息，学习能力与基础知识证据会更多依赖项目/奖项等描述。",
        }
        impact = impact_map.get(f, "该项信息缺失会让系统在相关维度上更保守评估。")
        followup = (
            f"收到。你提到这部分暂时“无/没有”。{impact}\n\n"
            "如果你愿意，可以补充一个替代信息来帮助评估："
            "比如用“课程作业/实验/社团项目/个人作品/训练营/比赛参与过程”等作为证据。"
            "如果确实没有，也回复“继续”。"
        )
        next_q = {
            "question_id": "optional_nudge",
            "target_fields": [f],
            "assistant_message": followup,
            "examples": ["继续", "我做过数据库课程设计：…", "我在社团做过一个小工具：…"],
            "quick_options": ["继续"],
        }
        # nudging 后仍不标记完成，下一轮会继续处理其他可选字段
        is_complete = False
    elif need_clarify and clarify_q and still_missing:
        next_q = {
            "question_id": "clarify",
            "target_fields": target_fields,
            "assistant_message": clarify_q,
            "examples": current_q.get("examples", []),
            "quick_options": current_q.get("quick_options", []) or ["不清楚", "先跳过"],
            "actions": current_q.get("actions", []),
        }
        is_complete = False
    else:
        is_complete = False
        next_q = None
        if len(missing_fields) > 0:
            templates = _pick_templates_for_missing(missing_fields, asked_fields=asked_fields)
            q2 = await generate_next_question(
                missing_fields=missing_fields,
                asked_fields=asked_fields,
                intake_data=intake_data,
                question_templates=templates,
            )
            if not isinstance(q2, dict) or not q2.get("assistant_message") or not q2.get("target_fields"):
                t = templates[0] if templates else _QUESTION_TEMPLATES[0]
                q2 = {
                    "question_id": t.get("template_id", "fallback"),
                    "target_fields": t.get("target_fields", []),
                    "assistant_message": t.get("base_question", ""),
                    "examples": t.get("examples", []),
                    "quick_options": t.get("quick_options", []),
                    "actions": t.get("actions", []),
                }
            # 强制校验：过滤掉已问过的字段，防止 LLM 重复提问
            q2_target_fields = q2.get("target_fields") or []
            filtered_fields = [f for f in q2_target_fields if f not in asked_fields]
            if len(filtered_fields) < len(q2_target_fields):
                q2["target_fields"] = filtered_fields
            # 如果过滤后没有字段了，使用模板兜底（确保获取未问过的字段）
            if not q2.get("target_fields") and templates:
                for t in templates:
                    tfs = t.get("target_fields") or []
                    remaining = [f for f in tfs if f not in asked_fields]
                    if remaining:
                        q2["target_fields"] = remaining
                        break
            # 如果所有模板的字段都被问过了，但仍有 core 字段缺失，强制获取第一个缺失的 core 字段
            if not q2.get("target_fields") and core_missing:
                # 获取第一个未问过的 core 字段
                for f in core_missing:
                    if f not in asked_fields:
                        q2["target_fields"] = [f]
                        q2["assistant_message"] = f"请继续填写：{f.split('.')[-1]}"
                        break
            # 无下一题 target 时：仅当程序判定核心+可选均无缺失才可结束；否则强制单字段兜底追问
            if not q2.get("target_fields"):
                if len(core_missing) == 0 and len(optional_missing) == 0:
                    # =========================================================
                    # 阶段一：所有常规题都问完了，进入「最终补全确认」阶段
                    # =========================================================
                    review_status = session.get("review_status", "pending")
                    if review_status == "pending":
                        # 扫描所有可选字段：找出值为空/无/明确的缺失
                        def _review_needed(fld: str) -> bool:
                            v = _get_path(intake_data, fld)
                            if fld in _OPTIONAL_LIST_FIELDS:
                                return v is None or (isinstance(v, list) and len(v) == 0)
                            if isinstance(v, str):
                                stripped = v.strip()
                                return not stripped or _is_explicit_none(stripped)
                            return v is None

                        review_missing = [f for f in _OPTIONAL_FIELDS if _review_needed(f)]
                        if review_missing:
                            # 进入补全确认阶段
                            session["review_status"] = "in_review"
                            session["review_fields_queue"] = review_missing
                            session["review_turn"] = 0

                            review_labels = [
                                f"「{_FIELD_DISPLAY_NAMES.get(f, f.split('.')[-1])}」"
                                for f in review_missing
                            ]
                            if len(review_labels) == 1:
                                label_text = review_labels[0]
                            else:
                                label_text = "、".join(review_labels[:-1]) + "和" + review_labels[-1]
                            review_intro = (
                                f"好，基本信息已经收集得差不多了。\n\n"
                                f"我发现你的简历中还有 {label_text} 目前为空或填写了“无”。\n"
                                f"这些信息对生成更精准的职业报告非常有帮助。\n\n"
                                f"我们来逐项确认一下（如果确实没有，直接回复“继续”即可）："
                            )
                            next_q = {
                                "question_id": "review_intro",
                                "target_fields": [],
                                "assistant_message": review_intro,
                                "examples": ["好，开始确认", "继续"],
                                "quick_options": ["继续"],
                            }
                            is_complete = False
                            q2 = next_q
                        else:
                            is_complete = True
                            missing_fields = []
                    elif review_status == "in_review":
                        # 补全确认阶段：用户本轮正常回答了某字段 → 先出队再看下一题
                        # （跳过/不需要补充在函数开头已拦截，不会走到这里）
                        queue: List[str] = session.get("review_fields_queue", [])
                        if queue and target_fields:
                            answered_set = set(target_fields)
                            if queue[0] in answered_set:
                                queue = queue[1:]
                                session["review_fields_queue"] = queue
                                session["review_turn"] = int(session.get("review_turn", 0)) + 1
                        if queue:
                            f = queue[0]
                            # 构建单个字段的补全追问
                            disp_name = _FIELD_DISPLAY_NAMES.get(f, f.split('.')[-1])
                            review_t = next(
                                (t for t in _QUESTION_TEMPLATES if f in (t.get("target_fields") or [])),
                                None,
                            )
                            if review_t:
                                msg = f"最后确认一下：「{disp_name}」这部分你还有需要补充的吗？"
                                next_q = {
                                    "question_id": "review_single",
                                    "target_fields": [f],
                                    "assistant_message": msg,
                                    "examples": review_t.get("examples", []),
                                    "quick_options": review_t.get("quick_options", []) + ["继续", "不需要补充"],
                                    "actions": review_t.get("actions", []),
                                }
                            else:
                                next_q = {
                                    "question_id": "review_single",
                                    "target_fields": [f],
                                    "assistant_message": f"「{disp_name}」这部分可以补充一下吗？（没有也可以直接说“继续”）",
                                    "examples": [],
                                    "quick_options": ["继续", "不需要补充"],
                                    "actions": [],
                                }
                            is_complete = False
                            q2 = next_q
                        else:
                            # 补全确认全部完成，结束
                            session["review_status"] = "done"
                            is_complete = True
                            missing_fields = []
                    else:
                        is_complete = True
                        missing_fields = []
                else:
                    pool = list(core_missing) + list(optional_missing)
                    asked_set = set(asked_fields)
                    remaining = [x for x in pool if x not in asked_set]
                    if remaining:
                        f0 = remaining[0]
                        q2["target_fields"] = [f0]
                        q2["question_id"] = "force_single"
                        matched_t = next(
                            (t for t in _QUESTION_TEMPLATES if f0 in (t.get("target_fields") or [])),
                            None,
                        )
                        if matched_t:
                            q2["assistant_message"] = matched_t.get("base_question", "")
                            q2["examples"] = matched_t.get("examples", [])
                            q2["quick_options"] = matched_t.get("quick_options", [])
                            q2["actions"] = matched_t.get("actions", [])
                        else:
                            q2["assistant_message"] = f"请补充：{f0.split('.')[-1].replace('_', ' ')}"
                            q2["examples"] = []
                            q2["quick_options"] = []
                            q2["actions"] = []
                    else:
                        is_complete = True
                        missing_fields = []
            next_q = q2
        else:
            is_complete = True
            next_q = None

    # 写回 session
    session["intake_data"] = intake_data
    session["missing_fields"] = missing_fields
    session["core_missing_fields"] = core_missing
    session["optional_missing_fields"] = optional_missing
    session["warnings"] = warnings
    session["asked_fields"] = asked_fields
    session["nudged_optional_fields"] = nudged_optional_fields
    session["current_question"] = next_q
    session["history"] = history
    session["turn"] = int(session.get("turn", 0)) + 1
    session["status"] = "ready_to_finish" if is_complete else "collecting"

    return {
        "session_id": request.session_id,
        "question": next_q,
        "is_complete": is_complete,
        "intake_data": intake_data,
        "notes": llm.get("notes", "") if isinstance(llm, dict) else "",
        "missing_fields": missing_fields,
        "optional_missing_fields": optional_missing,
        "warnings": warnings,
    }


@app.post("/api/v1/student/intake/finish")
async def intake_finish(request: IntakeFinishRequest):
    session = _INTAKE_SESSIONS.get(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="会话不存在或已过期，请重新开始")

    intake_data = session.get("intake_data", {}) or {}
    if isinstance(intake_data, dict):
        _normalize_intake_nested_keys(intake_data)

    try:
        student_profile = await build_student_profile_from_intake(intake_data)
    except Exception as e:
        logger.error(f"构建 StudentProfile 失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"画像生成失败: {str(e)}")

    profile_cache_id = _store_profile_cache(student_profile.model_dump(mode="json"))

    result = await _process_student_profile_to_leaderboard(student_profile)
    result["profile_cache_id"] = profile_cache_id
    _INTAKE_SESSIONS.pop(request.session_id, None)
    return result


def _resolve_student_profile_for_match(
    student_profile: Optional[StudentProfile], profile_cache_id: Optional[str]
) -> StudentProfile:
    if student_profile is not None:
        return student_profile
    if profile_cache_id:
        raw = _load_profile_cache(profile_cache_id)
        if not raw:
            raise HTTPException(
                status_code=404,
                detail="画像缓存不存在或已过期。请确认未清空缓存目录，并重新调用简历解析接口获取新的 profile_cache_id。",
            )
        try:
            return StudentProfile(**raw)
        except Exception as e:
            logger.warning("profile_cache 反序列化失败: %s", e)
            raise HTTPException(status_code=400, detail=f"缓存中的画像结构无效: {e}")
    raise HTTPException(
        status_code=422,
        detail="请提供 student_profile 或 profile_cache_id 之一。",
    )


@app.post("/api/v1/match/detail")
async def get_match_detail(request: MatchDetailRequest):
    """
    阶段二：选中岗位后拉取匹配详情（四维学生分 vs 岗位要求分），与前端雷达图字段对齐。
    """
    student_profile = _resolve_student_profile_for_match(
        request.student_profile, request.profile_cache_id
    )
    all_jobs = load_jobs()
    target_job = next((job for job in all_jobs if str(job["job_id"]) == str(request.job_id)), None)
    if not target_job:
        raise HTTPException(status_code=404, detail="岗位不存在")

    match_detail = calculate_match(student_profile, target_job)
    module_1 = generate_module_1(student_profile, target_job, match_detail)
    raw_dims = (module_1.get("fit_analysis") or {}).get("four_dimensions") or []

    dimensions = []
    for row in raw_dims:
        if not isinstance(row, dict):
            continue
        dimensions.append(
            {
                "dimension_key": row.get("dimension_key"),
                "dimension_label": row.get("dimension_label"),
                "student_score": row.get("student_score_100"),
                "job_required_score": row.get("job_required_score_100"),
                "student_score_100": row.get("student_score_100"),
                "job_required_score_100": row.get("job_required_score_100"),
                "fit_percent": row.get("fit_percent"),
                "conclusion": row.get("conclusion"),
                "evidence": row.get("evidence") or [],
            }
        )

    details = match_detail.get("details") or {}
    student_name = getattr(student_profile.basic_info, "name", "") or ""

    return {
        "job_id": target_job.get("job_id"),
        "title": target_job.get("title"),
        "match_score": match_detail.get("match_score"),
        "match_level": _match_level_label(float(match_detail.get("match_score") or 0)),
        "is_qualified": match_detail.get("is_qualified", True),
        "dimensions": dimensions,
        "semantic_score": details.get("semantic_score"),
        "rule_score": details.get("rule_score"),
        "student_name": student_name,
        "details": details,
        "gap_analysis": "",
        "improvement_suggestions": "",
        "narrative": "",
    }


@app.post("/api/v1/match/report")
async def generate_match_report(request: MatchReportRequest):
    """
    阶段二接口：选择岗位 -> 生成深度报告

    支持两种调用方式（二选一）：
    1. 直接传 student_profile（保持向后兼容）
    2. 传 profile_cache_id（由 parse/parse_manual 返回，推荐）

    同时传了 student_profile 和 profile_cache_id 时，优先使用 student_profile。
    """
    student_profile = _resolve_student_profile_for_match(
        request.student_profile, request.profile_cache_id
    )

    # 2. 找到目标岗位数据
    all_jobs = load_jobs()
    target_job = next((job for job in all_jobs if str(job["job_id"]) == str(request.job_id)), None)
    if not target_job:
        raise HTTPException(status_code=404, detail="岗位不存在")
        
    # 3. 计算匹配 & 生成四个模块报告
    match_detail = calculate_match(student_profile, target_job)

    module_1 = generate_module_1(student_profile, target_job, match_detail)
    module_2 = await generate_module_2(student_profile, target_job, match_detail, all_jobs)
    module_3 = await generate_module_3(
        student_profile,
        target_job,
        match_detail,
        module_1,
        module_2,
        request.plan_preferences,
    )
    module_4 = await generate_module_4(
        student_profile,
        target_job,
        match_detail,
        module_1,
        module_2,
        module_3,
    )

    # 构建全局摘要（放在最外层，方便前端直接取用，不需要进 career_report）
    student_name = getattr(student_profile.basic_info, "name", "")
    top_strengths = [s["dimension_label"] for s in module_1.get("strengths", [])]
    key_gaps = [g["dimension_label"] for g in module_1.get("gaps", [])]

    # 精简 job_info：只保留前端展示必需字段，去掉冗长的 description 和 keywords
    job_info_slim = {
        "job_id": target_job.get("job_id"),
        "title": target_job.get("title"),
        "min_education": target_job.get("min_education"),
        "target_majors": target_job.get("target_majors", []),
        "weights": target_job.get("weights", {}),
        "salary_info": target_job.get("salary_info"),
    }

    # 精简 match_summary：把 match_detail 中最关键的维度分数提到外层
    match_dims = (match_detail.get("details", {}) or {}).get("dimensions", {})
    match_summary_slim = {
        "match_score": match_detail.get("match_score"),
        "match_level": _match_level_label(match_detail.get("match_score", 0)),
        "is_qualified": match_detail.get("is_qualified"),
        "dimensions": {
            "base": match_dims.get("base"),
            "skill": match_dims.get("skill"),
            "soft": match_dims.get("soft"),
            "potential": match_dims.get("potential"),
        },
    }
    
    return {
        "summary": {
            "student_name": student_name,
            "target_job": {"job_id": target_job.get("job_id"), "title": target_job.get("title")},
            "match_score": match_detail.get("match_score"),
            "match_level": _match_level_label(match_detail.get("match_score", 0)),
            "overall_fit_percent": module_1.get("overall_fit_percent"),
            "top_strengths": top_strengths,
            "key_gaps": key_gaps,
        },
        "job_info": job_info_slim,
        "match_summary": match_summary_slim,
        "career_report": {
            "module_1": module_1,
            "module_2": module_2,
            "module_3": module_3,
            "module_4": module_4,
        },
    }


# 合并远程：岗位画像路由 + 版本头 + 健康检查
@app.middleware("http")
async def add_version_header(request, call_next):
    response = await call_next(request)
    response.headers["X-API-Version"] = "1"
    return response


app.include_router(positions.router)


@app.get("/health", summary="健康检查")
async def health_check():
    return {"status": "healthy"}
