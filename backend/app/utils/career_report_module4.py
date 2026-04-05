from typing import Any, Dict, Optional, List

from app.models.student_profile import StudentProfile
from app.utils.llm_client import polish_full_career_report


def _safe_dict(v: Any) -> Dict[str, Any]:
    return v if isinstance(v, dict) else {}


def _safe_list(v: Any) -> List[Any]:
    if isinstance(v, list):
        return v
    if v is None:
        return []
    return [v]


def _validate_career_report_structure(
    module_1: Optional[Dict[str, Any]],
    module_2: Optional[Dict[str, Any]],
    module_3: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    规则版完整性检测：
    - 不依赖 LLM，只检查关键字段是否存在、是否有内容
    - 用于在前端提示“报告是否完整”“缺哪些块”
    """
    missing: List[str] = []
    warnings: List[str] = []

    m1 = _safe_dict(module_1)
    m2 = _safe_dict(module_2)
    m3 = _safe_dict(module_3)

    # 模块一：学生画像 & 匹配结论
    # 兼容 student_info（七维在这里）和 profile_overview（旧结构）
    student_info = m1.get("student_info") or m1.get("profile_overview") or {}
    seven = _safe_list(student_info.get("seven_dimensions"))
    summary = student_info.get("summary", "")

    # 检查七维是否有有效分数（score_100 > 0）
    valid_dims = [d for d in seven if float(d.get("score_100", 0)) > 0]
    if not valid_dims:
        missing.append("module_1.seven_dimensions（七维能力画像无有效分数）")
    if len(valid_dims) < 7:
        warnings.append(f"module_1.seven_dimensions（仅 {len(valid_dims)}/7 个维度有有效分数）")

    # 检查 summary 是否为空或仅包含占位符
    if not summary or summary in ["", "暂无数据"]:
        warnings.append("module_1.summary（学生画像摘要为空）")

    # 模块二：职业路径 & 市场趋势
    market = _safe_dict(m2.get("market_trend"))
    cp = _safe_dict(m2.get("career_paths"))
    path_options = _safe_list(cp.get("path_options"))
    recommended_path = _safe_dict(cp.get("recommended_path"))
    if not market.get("demand_level"):
        warnings.append("module_2.market_trend.demand_level（岗位需求强度为缺省值）")
    if not market.get("trend_direction"):
        warnings.append("module_2.market_trend.trend_direction（趋势方向为缺省值）")
    if not path_options:
        missing.append("module_2.career_paths.path_options（缺少职业路径候选集合）")
    if not recommended_path:
        missing.append("module_2.career_paths.recommended_path（未生成推荐路径）")

    # 模块三：行动计划
    sp = _safe_dict(m3.get("selected_plan"))
    short_term = _safe_dict(sp.get("short_term"))
    mid_term = _safe_dict(sp.get("mid_term"))
    eval_block = _safe_dict(sp.get("evaluation"))

    if not short_term:
        missing.append("module_3.selected_plan.short_term（缺少短期计划）")
    else:
        # 检查 skills 列表是否有内容（实际的字段是 skills）
        skills = _safe_list(short_term.get("skills", []))
        if not skills:
            warnings.append("module_3.selected_plan.short_term.skills（短期技能列表为空）")

    if not mid_term:
        # mid_term 可为空，表示时间不足
        warnings.append("module_3.selected_plan.mid_term（缺少中期计划，可为空表示时间不足）")
    else:
        skills = _safe_list(mid_term.get("skills", []))
        if not skills:
            warnings.append("module_3.selected_plan.mid_term.skills（中期技能列表为空）")

    metrics = _safe_list(eval_block.get("metrics"))
    if not metrics:
        missing.append("module_3.selected_plan.evaluation.metrics（缺少量化评估指标）")

    plan_table = _safe_dict(sp.get("plan_table"))
    rows = _safe_list(plan_table.get("rows"))
    if not rows:
        warnings.append("module_3.selected_plan.plan_table.rows（计划表为空，无法按时间维度展示）")

    is_complete = len(missing) == 0

    return {
        "is_complete": is_complete,
        "missing_fields": missing,
        "warnings": warnings,
    }


async def generate_module_4(
    student: StudentProfile,
    target_job: Dict[str, Any],
    match_detail: Dict[str, Any],
    module_1: Optional[Dict[str, Any]] = None,
    module_2: Optional[Dict[str, Any]] = None,
    module_3: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    模块四：报告润色 + 完整性检测

    - 基于模块 1/2/3 的结构化结果，调用大模型生成一份自然语言版的完整职业规划报告。
    - 同时做一轮规则版完整性检测，方便前端提示“缺哪些块/有哪些提醒”。
    """
    module_1 = module_1 or {}
    module_2 = module_2 or {}
    module_3 = module_3 or {}

    llm_result = await polish_full_career_report(
        student=student,
        target_job=target_job,
        match_detail=match_detail,
        module_1=module_1,
        module_2=module_2,
        module_3=module_3,
    )

    validation = _validate_career_report_structure(module_1, module_2, module_3)

    return {
        "polished_markdown": llm_result.get("polished_markdown", ""),
        "llm_status": "ok" if llm_result.get("polished_markdown") else "error",
        "validation": validation,
    }


