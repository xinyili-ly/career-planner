# -*- coding: utf-8 -*-
"""
模块三：学习与实践行动计划

重构后的版本：
1. 使用 skill_path_generator 生成技能学习路径库
2. 使用 gap_analyzer 分析差距
3. 使用 action_plan_generator 生成行动计划
4. 保留原有的 plan_mode 和人机协同功能
"""
import logging
from typing import Any, Dict, List, Optional

from app.models.student_profile import StudentProfile
from app.utils.llm_client import generate_study_plan_for_gap
from app.utils.action_plan_generator import generate_action_plan


_GAP_DIM_LABELS = {
    "base": "基础要求",
    "skill": "职业技能",
    "soft": "职业素养",
    "potential": "发展潜力",
}

_TIER_LABELS = {
    "simple": "简单",
    "standard": "标准",
    "advanced": "进阶",
}


def _safe_list(v: Any) -> List[Any]:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def _tier_or_default(v: Optional[str]) -> str:
    t = str(v or "").strip()
    return t if t in {"simple", "standard", "advanced"} else "standard"


def _adjustment_rules() -> List[Dict[str, Any]]:
    return [
        {
            "if": "同一主题连续两次评估未达标",
            "then": "拆小任务、减少并行主题、替换学习资源，并用实践驱动学习（先做后补）。",
            "owner": "系统/用户",
        },
        {
            "if": "核心项目里程碑提前完成",
            "then": "提前进入下一主题，同时增加一次模拟面试或提高投递频率。",
            "owner": "系统",
        },
        {
            "if": "匹配分连续两次无提升且差距集中在同一维度",
            "then": "下周期 60% 时间投入该维度对应的学习主题与实践任务。",
            "owner": "系统",
        },
    ]


def _selected_path_type(module_2: Optional[Dict[str, Any]]) -> str:
    if not module_2:
        return "mixed"
    cp = module_2.get("career_paths") or {}
    sel = cp.get("selected_path") or cp.get("recommended_path") or {}
    t = str(sel.get("type", "")).strip()
    return t if t in {"vertical", "lateral"} else "mixed"


def _metrics(target_job: Dict[str, Any], tier: str, path_type: str) -> List[Dict[str, Any]]:
    title = str(target_job.get("title", "")).strip()
    base_targets = {
        "simple": {"resume_submits_per_week": 5, "deliverables_per_month": 2},
        "standard": {"resume_submits_per_week": 10, "deliverables_per_month": 3},
        "advanced": {"resume_submits_per_week": 15, "deliverables_per_month": 4},
    }
    t = base_targets.get(tier, base_targets["standard"])
    metrics = [
        {
            "name": "作品集产出",
            "definition": "本周期可展示的项目/文档/报告数量",
            "target": f">= {t['deliverables_per_month']} / 月",
            "data_source": "项目仓库/文档记录",
        },
        {
            "name": "岗位投递节奏",
            "definition": "每周有效投递数量（含岗位匹配与简历定制）",
            "target": f">= {t['resume_submits_per_week']} / 周",
            "data_source": "投递台账",
        },
        {
            "name": "目标岗位匹配维度改进",
            "definition": "match_detail 里的四维得分（base/skill/soft/potential）变化",
            "target": "至少提升 1 个关键维度或保持高位稳定",
            "data_source": "系统重新计算的匹配结果",
        },
    ]
    if path_type == "lateral":
        metrics.append(
            {
                "name": "换岗补位完成度",
                "definition": "selected_path.required_skills 对应学习与实践完成比例",
                "target": ">= 70%",
                "data_source": "学习清单与实践验收",
            }
        )
    if "运维" in title or "SRE" in title:
        metrics.append(
            {
                "name": "稳定性与故障演练",
                "definition": "至少完成一次故障演练/复盘或监控告警配置",
                "target": ">= 1 次 / 月",
                "data_source": "演练记录/配置",
            }
        )
    return metrics


def _content_settings(tier: str) -> Dict[str, Any]:
    if tier == "simple":
        return {
            "topics_short": 3,
            "topics_mid": 3,
            "practice_short": 2,
            "practice_mid": 2,
            "effort_short": "6-8 小时/周",
            "effort_mid": "6-8 小时/周",
        }
    if tier == "advanced":
        return {
            "topics_short": 6,
            "topics_mid": 6,
            "practice_short": 4,
            "practice_mid": 4,
            "effort_short": "15-18 小时/周",
            "effort_mid": "15-18 小时/周",
        }
    return {
        "topics_short": 4,
        "topics_mid": 4,
        "practice_short": 3,
        "practice_mid": 3,
        "effort_short": "10-12 小时/周",
        "effort_mid": "10-12 小时/周",
    }


async def generate_module_3(
    student: StudentProfile,
    target_job: Dict[str, Any],
    match_detail: Dict[str, Any],
    module_1: Optional[Dict[str, Any]] = None,
    module_2: Optional[Dict[str, Any]] = None,
    plan_preferences: Optional[Dict[str, str]] = None,
) -> Dict[str, Any]:
    """
    生成模块三：学习与实践行动计划

    重构后的流程：
    1. 使用 action_plan_generator 生成基础行动计划
    2. 整合原有的人机协同功能
    3. 生成 plan_mode 和 task_adjustments
    """
    logger = logging.getLogger("CareerAgent")
    prefs = plan_preferences or {}

    # 1. 生成基础行动计划
    action_plan = generate_action_plan(student, target_job, match_detail)

    # 2. 获取配置
    content_tier = _tier_or_default(prefs.get("content_tier"))
    content = _content_settings(content_tier)
    path_type = _selected_path_type(module_2)

    # 3. 生成评估指标
    metrics_items = _metrics(target_job, content_tier, path_type)

    # 4. 生成 task_adjustments（可调整的任务参数）
    timeline = action_plan.get("timeline", {})
    gap_analysis = action_plan.get("gap_analysis", {})

    task_adjustments = {
        "label": "任务量微调",
        "groups": [
            {
                "group_label": "学习内容",
                "items": [
                    {
                        "key": "topics_short",
                        "label": "短期学习主题数",
                        "default": int(content["topics_short"]),
                        "min": 2,
                        "max": 8,
                        "step": 1,
                        "unit": "个",
                        "current": int(content["topics_short"]),
                    },
                    {
                        "key": "topics_mid",
                        "label": "中期学习主题数",
                        "default": int(content["topics_mid"]),
                        "min": 2,
                        "max": 8,
                        "step": 1,
                        "unit": "个",
                        "current": int(content["topics_mid"]),
                    },
                    {
                        "key": "effort_short",
                        "label": "每周投入时间（短期）",
                        "default": str(content["effort_short"]),
                        "options": ["6-8 小时", "10-12 小时", "15-18 小时"],
                        "type": "select",
                        "current": str(content["effort_short"]),
                    },
                    {
                        "key": "effort_mid",
                        "label": "每周投入时间（中期）",
                        "default": str(content["effort_mid"]),
                        "options": ["6-8 小时", "10-12 小时", "15-18 小时"],
                        "type": "select",
                        "current": str(content["effort_mid"]),
                    },
                ]
            },
            {
                "group_label": "求职节奏",
                "items": [
                    {
                        "key": "resume_submits_per_week",
                        "label": "每周投递简历",
                        "default": 10,
                        "min": 3,
                        "max": 20,
                        "step": 1,
                        "unit": "份",
                        "current": 10,
                    },
                    {
                        "key": "deliverables_per_month",
                        "label": "每月产出数量",
                        "default": 3,
                        "min": 1,
                        "max": 8,
                        "step": 1,
                        "unit": "个",
                        "current": 3,
                    }
                ]
            },
        ]
    }

    # 5. 整合 selected_plan
    # skills_plan 去掉 learning_path 嵌套，只保留技能关键信息
    def _flatten_skill(item: Dict[str, Any]) -> Dict[str, Any]:
        lp = item.get("learning_path") or {}
        acceptance = lp.get("acceptance") or {}
        project = acceptance.get("project") or {}
        return {
            "skill": item.get("skill", ""),
            "tier": item.get("tier", ""),
            "tier_label": item.get("tier_label", ""),
            "duration_weeks": item.get("duration_weeks", 4),
            "goal": lp.get("goal", ""),
            "project": {
                "name": project.get("name", ""),
                "description": project.get("description", ""),
                "features": project.get("features", []),
            },
            "resume": acceptance.get("resume", ""),
        }

    skills_plan = action_plan.get("skills_plan", {}) or {}
    plan_table = action_plan.get("plan_table") or {}
    # plan_table.rows 里已有 skills_detail，与 skills_plan 是同一份数据，不再重复
    # 只在 plan_table 里保留（展示用），selected_plan.skills 里不再存重复内容

    short_plan = [_flatten_skill(item) for item in skills_plan.get("short_term_plan") or []]
    mid_plan = [_flatten_skill(item) for item in skills_plan.get("mid_term_plan") or []]

    # 处理维度标签（可能是列表或字符串）
    short_term_info = gap_analysis.get("short_term") or {}
    mid_term_info = gap_analysis.get("mid_term") or {}
    short_dim_labels = short_term_info.get("dimension_labels", [])
    mid_dim_labels = mid_term_info.get("dimension_labels", [])
    short_dim_str = "、".join(short_dim_labels) if isinstance(short_dim_labels, list) else str(short_dim_labels)
    mid_dim_str = "、".join(mid_dim_labels) if isinstance(mid_dim_labels, list) else str(mid_dim_labels)

    selected_plan = {
        "gap_analysis": gap_analysis or {},
        "timeline": timeline or {},
        "short_term": {
            "duration_months": timeline.get("short_term_months", 0) if timeline else 0,
            "dimension": short_dim_str,
            "gap": short_term_info.get("total_gap", 0) or 0,
            "goals": [
                f"攻克「{short_dim_str}」维度" if short_dim_str else "形成至少一个可展示的项目/成果",
                "形成至少一个可展示的项目/成果",
            ],
            "skills": short_plan,
        },
        "mid_term": {
            "duration_months": timeline.get("mid_term_months", 0) if timeline else 0,
            "dimension": mid_dim_str,
            "gap": mid_term_info.get("total_gap", 0) or 0,
            "goals": [
                f"深化「{mid_dim_str}」维度" if mid_dim_str else "形成稳定的投递-面试-复盘闭环",
                "形成稳定的投递-面试-复盘闭环",
            ],
            "skills": mid_plan,
        },
        "evaluation": {
            "metrics": metrics_items,
            "review_questions": [
                "本周期最大的阻碍是什么？",
                "哪些任务完成后显著提升了匹配度或面试表现？",
                "下周期要减少什么、强化什么？",
            ],
        },
        "adjustment_rules": _adjustment_rules(),
        "plan_table": plan_table,
    }

    # plan_config 单独打包：UI 可调参数，不属于报告内容本身
    plan_config = {
        "selected_tier": content_tier,
        "labels": _TIER_LABELS,
        "task_adjustments": task_adjustments,
        "time_context": {
            "graduation_year": timeline.get("graduation_year"),
            "remaining_months": timeline.get("remaining_months", 0),
            "assumptions": "假设毕业时间为毕业年份的7月，保留1个月作为缓冲期",
        },
    }

    return {
        "plan_config": plan_config,
        "selected_plan": selected_plan,
    }
