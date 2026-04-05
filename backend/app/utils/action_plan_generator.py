# -*- coding: utf-8 -*-
"""
行动计划生成器

整合差距分析、技能匹配、表格生成
"""
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.models.student_profile import StudentProfile
from app.utils.skill_path_generator import (
    get_skill_learning_path_with_fallback,
    get_skill_learning_path,
)
from app.utils.gap_analyzer import (
    GAP_DIM_LABELS,
    QUADRANT_INFO,
    _calculate_remaining_months,
    _calculate_timeline,
    _match_dims,
    _extract_gap_skills,
    _select_tier_by_gap,
    calculate_quadrant_priorities,
    group_by_quadrant,
)


def _format_learning_content(skill_plan: List[Dict[str, Any]]) -> str:
    """格式化学习内容"""
    if not skill_plan:
        return ""
    content_parts = []
    for item in skill_plan:
        skill = item.get("skill", "")
        tier = item.get("tier", "")
        tier_label = {"entry": "入门", "intermediate": "进阶", "advanced": "精进"}.get(tier, tier)
        content_parts.append(f"{skill}（{tier_label}）")
    return "、".join(content_parts)


def _format_acceptance(item: Dict[str, Any]) -> str:
    """格式化验收指标"""
    learning_path = item.get("learning_path", {})
    if not learning_path:
        return ""
    acceptance = learning_path.get("acceptance", {})
    if not acceptance:
        return ""
    project = acceptance.get("project", {})
    if project:
        name = project.get("name", "")
        desc = project.get("description", "")
        return f"{name}：{desc}" if name else desc
    skill = acceptance.get("skill", {})
    if skill:
        return skill.get("criteria", "")
    return ""


def _get_skill_category(skill_name: str) -> str:
    """获取技能类别"""
    from app.utils.skill_path_generator import _get_skill_category as _get_cat
    return _get_cat(skill_name)


def _build_skill_plan(
    skills: List[str],
    gap_score: float,
    dimension_key: str,
) -> List[Dict[str, Any]]:
    """构建技能学习计划"""
    plan = []
    tier = _select_tier_by_gap(gap_score)

    for skill in skills:
        # 使用带降级逻辑的路径获取
        learning_path = get_skill_learning_path_with_fallback(
            skill_name=skill,
            tier=tier,
            category=_get_skill_category(skill),
            dimension=dimension_key,
        )

        # 如果 learning_path 是完整结构，取对应 tier
        if learning_path and isinstance(learning_path, dict) and "tiers" not in learning_path:
            pass  # 已经是单 tier 结构
        elif learning_path and isinstance(learning_path, dict) and "tiers" in learning_path:
            tier_data = learning_path.get("tiers", {}).get(tier, {})
            if tier_data:
                learning_path = tier_data

        plan.append({
            "skill": skill,
            "tier": tier,
            "tier_label": {"entry": "入门", "intermediate": "进阶", "advanced": "精进"}.get(tier, tier),
            "learning_path": learning_path,
            "gap_dimension": dimension_key,
            "duration_weeks": learning_path.get("duration_weeks", 4) if isinstance(learning_path, dict) else 4,
        })

    return plan


def _select_stage_dims_by_quadrant(
    quadrant_priorities: List[Dict[str, Any]],
    timeline: Dict[str, Any]
) -> tuple:
    """
    根据四象限优先级分配短期/中期维度

    分配逻辑：
        短期阶段：优先处理「必须达标」和「优先攻克」的象限
                这些维度决定了学生能否通过岗位门槛
                如果没有 gap > 0 的维度，则从「重点提升」中选择
        中期阶段：处理「重点提升」和「顺带解决」的象限
                这些维度提升简历竞争力

    Args:
        quadrant_priorities: 四象限排序后的维度列表
        timeline: 时间线信息

    Returns:
        tuple: (short_term_dims, mid_term_dims)，每个都是维度key列表
    """
    short_months = timeline.get("short_term_months", 0)
    mid_months = timeline.get("mid_term_months", 0)

    # 决定每个阶段处理多少个维度
    # 原则：短期专注1-2个维度，避免精力分散；中期可以处理更多
    short_count = min(2, short_months) if short_months > 0 else 0
    mid_count = min(4, mid_months * 2) if mid_months > 0 else 0

    short_dims = []
    mid_dims = []
    used_keys = set()

    # 象限优先级顺序（来自 quadrant_priorities 的自然排序）
    for item in quadrant_priorities:
        dim_key = item["dimension_key"]
        quadrant_key = item["quadrant_key"]
        gap = float(item.get("gap", 0))

        # 短期：从必须达标和优先攻克中选
        # 如果没有高优先级维度有 gap，则从「重点提升」中选择
        if len(short_dims) < short_count and quadrant_key in ("must_pass", "high_req_high_val"):
            short_dims.append(dim_key)
            used_keys.add(dim_key)

        # 如果短期还有空位且「重点提升」象限有 gap > 0 的维度，优先填充
        elif len(short_dims) < short_count and quadrant_key == "low_req_high_val" and gap > 0:
            if dim_key not in used_keys:
                short_dims.append(dim_key)
                used_keys.add(dim_key)

        # 如果短期还有空位且「顺带解决」象限有 gap > 0 的维度，填充
        elif len(short_dims) < short_count and quadrant_key == "low_req_low_val" and gap > 0:
            if dim_key not in used_keys:
                short_dims.append(dim_key)
                used_keys.add(dim_key)

        # 中期：从剩余象限中选
        elif dim_key not in used_keys and len(mid_dims) < mid_count:
            mid_dims.append(dim_key)
            used_keys.add(dim_key)

    # 如果所有维度 gap = 0，则平均分配到短期和中期（用于巩固和保持）
    if not short_dims and not mid_dims:
        for i, item in enumerate(quadrant_priorities):
            dim_key = item["dimension_key"]
            if i < short_count:
                short_dims.append(dim_key)
            else:
                mid_dims.append(dim_key)

    return short_dims, mid_dims


def _format_quadrant_summary(
    quadrant_groups: Dict[str, List[Dict[str, Any]]]
) -> List[Dict[str, Any]]:
    """格式化四象限摘要"""
    summary = []

    # 按象限顺序遍历
    for quadrant_key in ["must_pass", "high_req_high_val", "low_req_high_val", "low_req_low_val"]:
        dims = quadrant_groups.get(quadrant_key, [])
        if not dims:
            continue

        info = QUADRANT_INFO[quadrant_key]
        dim_labels = [d["dimension_label"] for d in dims]

        summary.append({
            "quadrant_key": quadrant_key,
            "quadrant_label": info["label"],
            "description": info["description"],
            "strategy": info["strategy"],
            "dimensions": dim_labels,
            "dimension_count": len(dims),
        })

    return summary


def generate_action_plan(
    student: StudentProfile,
    target_job: Dict[str, Any],
    match_detail: Dict[str, Any],
) -> Dict[str, Any]:
    """
    生成行动计划

    流程：
    1. 使用四象限法则分析四维差距并排序
    2. 根据四象限优先级分配短期/中期维度
    3. 匹配技能学习路径（优先预定义，降级生成）
    4. 生成计划表格
    """
    # 1. 提取四维分数
    dims = _match_dims(match_detail)

    # 2. 从岗位画像读取四维目标分和权重
    job_required = target_job.get("required_dimensions") or {}
    job_weights = target_job.get("weights") or {}

    # 3. 计算剩余时间
    graduation_year = student.basic_info.graduation_year
    remaining_months = _calculate_remaining_months(graduation_year)
    timeline = _calculate_timeline(remaining_months)

    # 4. 使用四象限法则计算优先级
    quadrant_priorities = calculate_quadrant_priorities(dims, job_required, job_weights)

    # 5. 按纯 gap 降序生成 gap_list（保留原有结构，用于兼容展示）
    gap_list = []
    for item in quadrant_priorities:
        fit_percent = min(100.0, round(item["student_score"] / item["target_score"] * 100, 1)) \
            if item["target_score"] > 0 else 100.0
        gap_list.append({
            "dimension_key": item["dimension_key"],
            "dimension_label": item["dimension_label"],
            "student_score": item["student_score"],
            "target_score": item["target_score"],
            "gap": item["gap"],
            "fit_percent": fit_percent,
            "urgency": item["urgency"],
            "weight": item["weight"],
            "importance": item["importance"],
            "quadrant_key": item["quadrant_key"],
            "quadrant_label": item["quadrant_label"],
            "priority_score": item["priority_score"],
            "strategy": item["strategy"],
        })

    # 6. 按四象限分组
    quadrant_groups = group_by_quadrant(gap_list)

    # 7. 根据四象限分配短期/中期维度
    short_dim_keys, mid_dim_keys = _select_stage_dims_by_quadrant(quadrant_priorities, timeline)

    # 8. 提取对应维度的技能
    short_term_skills = []
    mid_term_skills = []

    for dim_key in short_dim_keys:
        short_term_skills.extend(_extract_gap_skills(student, target_job, dim_key))

    for dim_key in mid_dim_keys:
        mid_term_skills.extend(_extract_gap_skills(student, target_job, dim_key))

    # 去重
    short_term_skills = list(dict.fromkeys(short_term_skills))[:12]
    mid_term_skills = list(dict.fromkeys(mid_term_skills))[:12]

    # 9. 构建技能学习计划
    short_gap_score = sum(item["gap"] for item in quadrant_priorities if item["dimension_key"] in short_dim_keys)
    mid_gap_score = sum(item["gap"] for item in quadrant_priorities if item["dimension_key"] in mid_dim_keys)

    short_term_plan = _build_skill_plan(
        short_term_skills,
        short_gap_score / len(short_dim_keys) if short_dim_keys else 50,
        short_dim_keys[0] if short_dim_keys else ""
    )

    mid_term_plan = _build_skill_plan(
        mid_term_skills,
        mid_gap_score / len(mid_dim_keys) if mid_dim_keys else 50,
        mid_dim_keys[0] if mid_dim_keys else ""
    )

    # 10. 生成计划表格
    short_months = timeline.get("short_term_months", 0)
    mid_months = timeline.get("mid_term_months", 0)

    rows = []

    # 短期行
    if short_months > 0 and short_dim_keys:
        acceptance_parts = [_format_acceptance(item) for item in short_term_plan]
        dim_labels = [GAP_DIM_LABELS[k] for k in short_dim_keys]
        primary_dim = quadrant_priorities[0] if quadrant_priorities else {}

        rows.append({
            "stage": "短期",
            "time_range": f"第1-{short_months}个月" if short_months > 1 else "第1个月",
            "dimension": "、".join(dim_labels),
            "gap_score": short_gap_score,
            "reasoning": f"【{primary_dim.get('quadrant_label', '')}象限】{primary_dim.get('strategy', '')}",
            "learning_content": _format_learning_content(short_term_plan),
            "acceptance": "；".join([p for p in acceptance_parts if p]),
            "skills_detail": [
                {
                    "skill": item.get("skill", ""),
                    "tier": item.get("tier", ""),
                    "tier_label": item.get("tier_label", ""),
                    "duration_weeks": item.get("duration_weeks", 4),
                    "goal": item.get("learning_path", {}).get("goal", "") if isinstance(item.get("learning_path"), dict) else "",
                    "project": item.get("learning_path", {}).get("acceptance", {}).get("project", {}) if isinstance(item.get("learning_path"), dict) else {},
                    "resume": item.get("learning_path", {}).get("acceptance", {}).get("resume", "") if isinstance(item.get("learning_path"), dict) else "",
                }
                for item in short_term_plan
            ]
        })

    # 中期行
    if mid_months > 0 and mid_dim_keys:
        acceptance_parts = [_format_acceptance(item) for item in mid_term_plan]
        dim_labels = [GAP_DIM_LABELS[k] for k in mid_dim_keys]
        primary_dim = next((p for p in quadrant_priorities if p["dimension_key"] in mid_dim_keys), {})

        start_month = short_months + 1
        rows.append({
            "stage": "中期",
            "time_range": f"第{start_month}-{start_month + mid_months - 1}个月",
            "dimension": "、".join(dim_labels),
            "gap_score": mid_gap_score,
            "reasoning": f"【{primary_dim.get('quadrant_label', '')}象限】{primary_dim.get('strategy', '')}",
            "learning_content": _format_learning_content(mid_term_plan),
            "acceptance": "；".join([p for p in acceptance_parts if p]),
            "skills_detail": [
                {
                    "skill": item.get("skill", ""),
                    "tier": item.get("tier", ""),
                    "tier_label": item.get("tier_label", ""),
                    "duration_weeks": item.get("duration_weeks", 4),
                    "goal": item.get("learning_path", {}).get("goal", "") if isinstance(item.get("learning_path"), dict) else "",
                    "project": item.get("learning_path", {}).get("acceptance", {}).get("project", {}) if isinstance(item.get("learning_path"), dict) else {},
                    "resume": item.get("learning_path", {}).get("acceptance", {}).get("resume", "") if isinstance(item.get("learning_path"), dict) else "",
                }
                for item in mid_term_plan
            ]
        })

    plan_table = {
        "headers": ["阶段", "学习时间", "核心维度", "差距分数", "行动策略", "学习内容", "成果验收指标"],
        "rows": rows
    }

    # 11. 生成四象限摘要
    quadrant_summary = _format_quadrant_summary(quadrant_groups)

    # 12. 生成行动序列（用于展示）
    action_sequence = []
    for i, item in enumerate(gap_list, 1):
        action_sequence.append({
            "step": i,
            "dimension_label": item["dimension_label"],
            "quadrant_label": item["quadrant_label"],
            "gap": item["gap"],
            "priority_score": item["priority_score"],
            "strategy": item["strategy"],
        })

    # 13. 返回完整结果
    return {
        "gap_analysis": {
            "dimensions": gap_list,
            "quadrants": quadrant_summary,
            "action_sequence": action_sequence,
            "short_term": {
                "dimension_keys": short_dim_keys or [],
                "dimension_labels": [GAP_DIM_LABELS[k] for k in short_dim_keys] if short_dim_keys else [],
                "total_gap": round(short_gap_score, 1),
            } if short_dim_keys is not None and len(short_dim_keys) > 0 else {
                "dimension_keys": [],
                "dimension_labels": [],
                "total_gap": 0,
            },
            "mid_term": {
                "dimension_keys": mid_dim_keys or [],
                "dimension_labels": [GAP_DIM_LABELS[k] for k in mid_dim_keys] if mid_dim_keys else [],
                "total_gap": round(mid_gap_score, 1),
            } if mid_dim_keys is not None and len(mid_dim_keys) > 0 else {
                "dimension_keys": [],
                "dimension_labels": [],
                "total_gap": 0,
            },
        },
        "timeline": {
            "graduation_year": graduation_year,
            "remaining_months": remaining_months,
            "short_term_months": short_months,
            "mid_term_months": mid_months,
        },
        "skills_plan": {
            "short_term_skills": short_term_skills,
            "mid_term_skills": mid_term_skills,
            "short_term_plan": short_term_plan,
            "mid_term_plan": mid_term_plan,
        },
        "plan_table": plan_table,
    }
