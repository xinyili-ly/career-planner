# -*- coding: utf-8 -*-
"""
差距分析器

功能：
1. 分析学生与目标岗位的四个维度差距
2. 确定短期/中期目标（Top 1 / Top 2 差距）
3. 计算时长
4. 匹配具体技能词
"""
import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime

from app.models.student_profile import StudentProfile


# 维度标签映射
GAP_DIM_LABELS = {
    "base": "基础要求",
    "skill": "职业技能",
    "soft": "职业素养",
    "potential": "发展潜力",
}

# 维度中文标签转 key
DIM_KEY_MAP = {
    "基础要求": "base",
    "基础": "base",
    "职业技能": "skill",
    "技能": "skill",
    "专业技能": "skill",
    "职业素养": "soft",
    "素养": "soft",
    "发展潜力": "potential",
    "潜力": "potential",
}


def _normalize_dimension_key(dim_label: str) -> str:
    """标准化维度标签为 key"""
    return DIM_KEY_MAP.get(dim_label, dim_label)


def _safe_list(v: Any) -> List[Any]:
    """安全的列表转换"""
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def _calculate_remaining_months(graduation_year: Optional[int]) -> int:
    """计算距离毕业剩余的月份数"""
    if not graduation_year or graduation_year <= 0:
        return 12  # 默认按 1 年规划

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    grad_month = 7  # 假设毕业时间为 7 月
    remaining_months = (graduation_year - current_year) * 12 + (grad_month - current_month)
    remaining_months = max(0, remaining_months - 1)  # 保留 1 个月缓冲

    return remaining_months


def _calculate_timeline(remaining_months: int) -> Dict[str, Any]:
    """根据剩余时间计算短期/中期时长"""
    if remaining_months <= 0:
        return {
            "short_term_months": 3,
            "mid_term_months": 0,
            "remaining_months": 0,
        }

    if remaining_months <= 6:
        return {
            "short_term_months": remaining_months,
            "mid_term_months": 0,
            "remaining_months": remaining_months,
        }

    # 均匀分配
    short = max(3, remaining_months // 2)
    return {
        "short_term_months": short,
        "mid_term_months": remaining_months - short,
        "remaining_months": remaining_months,
    }


def _match_dims(match_detail: Dict[str, Any]) -> Dict[str, float]:
    """提取四维分数"""
    dims = (match_detail.get("details", {}) or {}).get("dimensions", {}) or {}

    def _f(k: str) -> float:
        try:
            return float(dims.get(k, 0.0))
        except Exception:
            return 0.0

    return {"base": _f("base"), "skill": _f("skill"), "soft": _f("soft"), "potential": _f("potential")}


def _extract_gap_skills(
    student: StudentProfile,
    target_job: Dict[str, Any],
    dimension: str
) -> List[str]:
    """
    提取指定维度的差距技能

    根据 dimension 参数，从不同的数据源提取技能：
    - skill -> 专业技能
    - soft -> 职业素养（沟通、协作等）
    - potential -> 发展潜力（学习、创新等）
    - base -> 基础要求（证书、基础技能）
    """
    gaps = []
    student_skills = set()

    # 从学生画像提取技能
    if hasattr(student.competencies, 'professional_skills'):
        keywords = student.competencies.professional_skills.keywords or []
        student_skills = set([str(x).strip() for x in keywords if str(x).strip()])

    # 从岗位要求提取技能
    job_skills = []
    professional_skills = target_job.get("professional_skills", {}) or {}
    keywords = professional_skills.get("keywords", [])

    if isinstance(keywords, list):
        job_skills = [str(x).strip() for x in keywords if str(x).strip()]
    else:
        job_skills = [str(keywords).strip()]

    # 找出差距技能（岗位有但学生没有的）
    job_skills_set = set(job_skills)
    for skill in job_skills_set:
        if skill not in student_skills:
            gaps.append(skill)

    # 如果差距技能太少，从技能表补充
    if len(gaps) < 3:
        from app.utils.skill_path_generator import get_top_50_skills
        top_50 = get_top_50_skills()

        # 根据维度过滤相关技能
        dim_keywords = {
            "skill": ["Java", "Python", "Spring", "MySQL", "Redis", "Docker", "Linux", "微服务", "架构", "API"],
            "soft": ["沟通", "协作", "团队", "管理", "表达", "文档", "面试", "简历"],
            "potential": ["学习", "创新", "研究", "分析", "算法"],
            "base": ["证书", "考试", "认证", "基础"],
        }

        related = dim_keywords.get(dimension, [])
        for skill in top_50:
            if skill not in student_skills and skill not in gaps:
                # 检查是否包含维度相关关键词
                if any(kw in skill for kw in related):
                    gaps.append(skill)
                    if len(gaps) >= 12:
                        break

    return gaps[:12]  # 最多返回 12 个


def _select_tier_by_gap(gap_score: float) -> str:
    """根据差距分数选择学习档位"""
    if gap_score >= 60:
        return "entry"  # 差距大，从入门开始
    elif gap_score >= 30:
        return "intermediate"  # 差距中等，从进阶开始
    else:
        return "advanced"  # 差距较小，从精进开始


# 四象限常量
WEIGHT_THRESHOLD_HIGH = 0.25   # weight >= 0.25 为高权重
WEIGHT_THRESHOLD_MEDIUM = 0.22  # 0.22 <= weight < 0.25 为中等权重

GAP_THRESHOLD_HIGH = 15.0  # gap >= 15 为高要求
GAP_THRESHOLD_MEDIUM = 8.0  # 8 <= gap < 15 为中等要求

# 四象限定义：key -> (label, description, order)
QUADRANT_INFO = {
    "must_pass": {
        "label": "必须达标",
        "description": "岗位要求高，但市场价值相对较低。需要达到门槛，但不必投入过多精力。",
        "strategy": "确保达到岗位最低要求，不必过度投入",
        "order": 1,
    },
    "high_req_high_val": {
        "label": "优先攻克",
        "description": "既要求高，市场又看重。投入产出比最高，应该优先投入精力。",
        "strategy": "集中精力优先攻克，这是最有价值的学习投资",
        "order": 2,
    },
    "low_req_high_val": {
        "label": "重点提升",
        "description": "岗位要求不高，但市场看重。容易达标且收益大。",
        "strategy": "快速提升，这是提升简历竞争力的高效途径",
        "order": 3,
    },
    "low_req_low_val": {
        "label": "顺带解决",
        "description": "要求不高，市场也不太看重。可以最后处理。",
        "strategy": "在完成更高优先级任务后再处理",
        "order": 4,
    },
}


def _classify_quadrant(gap: float, weight: float) -> str:
    """根据差距和权重划分象限"""
    is_high_req = gap >= GAP_THRESHOLD_HIGH
    is_high_val = weight >= WEIGHT_THRESHOLD_HIGH

    if is_high_req and not is_high_val:
        return "must_pass"
    elif is_high_req and is_high_val:
        return "high_req_high_val"
    elif not is_high_req and is_high_val:
        return "low_req_high_val"
    else:
        return "low_req_low_val"


def _classify_weight_importance(weight: float) -> str:
    """根据权重分档"""
    if weight >= WEIGHT_THRESHOLD_HIGH:
        return "high"
    elif weight >= WEIGHT_THRESHOLD_MEDIUM:
        return "medium"
    else:
        return "low"


def calculate_quadrant_priorities(
    dims: Dict[str, float],
    job_required: Dict[str, float],
    job_weights: Dict[str, float],
) -> List[Dict[str, Any]]:
    """
    使用四象限法则计算各维度的优先级

    逻辑：
    1. 对每个维度计算必要度（urgency = gap / target）和价值度（weight）
    2. 根据 gap 和 weight 划分四象限
    3. 按象限顺序 + 象限内 priority_score 排序

    四象限顺序：
        1. 必须达标（高要求×低价值）  -> 先确保能过门槛
        2. 优先攻克（高要求×高价值）  -> 投入产出比最高
        3. 重点提升（低要求×高价值）  -> 快速提升匹配分
        4. 顺带解决（低要求×低价值）  -> 最后处理

    Returns:
        List[Dict], 按优先级排序的维度列表，每个元素包含：
            - dimension_key, dimension_label
            - target_score, student_score, gap
            - urgency (gap / target)
            - weight, importance (weight分档)
            - quadrant_key, quadrant_label, quadrant_description
            - priority_score (urgency × weight)
            - strategy
    """
    result = []

    for key, label in GAP_DIM_LABELS.items():
        student_score = dims.get(key, 0.0)
        target_score = job_required.get(key, 0.0)
        weight = job_weights.get(key, 0.0)
        gap = max(0.0, target_score - student_score)

        # 计算必要度：gap > 0 时正常计算，gap = 0 时给一个小的 base 值用于排序
        if gap > 0:
            urgency = round(gap / target_score, 4) if target_score > 0 else 1.0
        else:
            # gap = 0 表示已达标，但仍需"巩固"；给一个极小值用于排序（但不参与象限判定）
            urgency = 0.0

        # 划分象限：基于原始 gap 而非 urgency
        quadrant_key = _classify_quadrant(gap, weight)
        quadrant_info = QUADRANT_INFO[quadrant_key]

        # 如果 gap=0，给一个"巩固"策略而非"快速提升"
        if gap == 0:
            strategy = f"已达标（{label} {student_score:.0f} ≥ {target_score:.0f}），保持优势并持续巩固"
        else:
            strategy = quadrant_info["strategy"]

        importance = _classify_weight_importance(weight)

        # 计算优先级分数：gap > 0 时用 urgency * weight，gap = 0 时用 weight * 0.01（极小）
        if gap > 0:
            priority_score = round(urgency * weight, 6)
        else:
            # 已达标的维度按 weight 降序排列，但排在所有有 gap 的维度之后
            priority_score = round(weight * 0.001, 6)

        result.append({
            "dimension_key": key,
            "dimension_label": label,
            "target_score": round(target_score, 1),
            "student_score": round(student_score, 1),
            "gap": round(gap, 1),
            "urgency": urgency,
            "weight": weight,
            "importance": importance,
            "quadrant_key": quadrant_key,
            "quadrant_label": quadrant_info["label"],
            "quadrant_description": quadrant_info["description"],
            "priority_score": priority_score,
            "strategy": strategy,
            "quadrant_order": quadrant_info["order"],
        })

    # 按象限顺序 + priority_score 降序排序
    result.sort(key=lambda x: (x["quadrant_order"], -x["priority_score"]))

    return result


def group_by_quadrant(
    priorities: List[Dict[str, Any]]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    将优先级列表按四象限分组

    Returns:
        Dict[str, List[Dict]]，key为象限key，value为该象限的维度列表（已按priority_score降序）
    """
    groups = {
        "must_pass": [],
        "high_req_high_val": [],
        "low_req_high_val": [],
        "low_req_low_val": [],
    }

    for item in priorities:
        qk = item["quadrant_key"]
        if qk in groups:
            groups[qk].append(item)

    # 每个象限内按 priority_score 降序
    for qk in groups:
        groups[qk].sort(key=lambda x: -x["priority_score"])

    return groups
