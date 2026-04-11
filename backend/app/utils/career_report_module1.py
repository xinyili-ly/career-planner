from typing import Any, Dict, List, Tuple

from app.models.student_profile import StudentProfile


_DIM_LABELS = {
    "base": "基础要求",
    "skill": "职业技能",
    "soft": "职业素养",
    "potential": "发展潜力",
}

_COMP_KEYS = [
    "professional_skills",
    "certificate_requirements",
    "innovation_capability",
    "learning_capability",
    "stress_resistance",
    "communication_skills",
    "internship_experience",
]

_COMP_LABELS = {
    "professional_skills": "专业技能",
    "certificate_requirements": "证书要求",
    "innovation_capability": "创新能力",
    "learning_capability": "学习能力",
    "stress_resistance": "抗压能力",
    "communication_skills": "沟通能力",
    "internship_experience": "实习经历",
}


def _safe_list(v: Any) -> List[Any]:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def _job_level(job: Dict[str, Any], key: str) -> int:
    v = job.get(key, {})
    level = v.get("level")
    if isinstance(level, int) and 1 <= level <= 5:
        return level
    return 3


def _level_to_score_100(level: int) -> float:
    return round(max(1, min(5, level)) * 20.0, 1)


def _student_comp_scores_100(student: StudentProfile) -> Dict[str, float]:
    c = student.competencies
    return {
        "professional_skills": float(c.professional_skills.score) * 10.0,
        "certificate_requirements": float(c.certificate_requirements.score) * 10.0,
        "innovation_capability": float(c.innovation_capability.score) * 10.0,
        "learning_capability": float(c.learning_capability.score) * 10.0,
        "stress_resistance": float(c.stress_resistance.score) * 10.0,
        "communication_skills": float(c.communication_skills.score) * 10.0,
        "internship_experience": float(c.internship_experience.score) * 10.0,
    }


def _job_comp_scores_100(job: Dict[str, Any]) -> Dict[str, float]:
    return {k: _level_to_score_100(_job_level(job, k)) for k in _COMP_KEYS}


def _evidence_empty(student: StudentProfile, dim: str) -> bool:
    """
    检查某维度的 evidence 是否为空（无有效内容）。
    
    支持两种维度类型：
    - 四维：base, skill, soft, potential
    - 七维：professional_skills, certificate_requirements, innovation_capability, 
            learning_capability, stress_resistance, communication_skills, internship_experience
    """
    ev = _dim_evidence(student, dim)
    if not ev:
        return True
    # 检查是否有实质内容（排除纯占位符短语）
    placeholder_phrases = {
        "信息不足，无法评估",  # 默认值
        "缺少客观证据",         # 默认值
        "已获证书：无",         # 明确表示无证书
        "建议补充：无",         # 明确表示无建议
        "实习经历：无",         # 明确表示无实习
        "未收集到信息",         # 通用未收集
    }
    # 如果所有证据行都是占位符短语，则认为无证据
    non_placeholder_lines = [line for line in ev if str(line).strip() not in placeholder_phrases]
    return len(non_placeholder_lines) == 0


_DIM_COMP_FIELDS: Dict[str, List[str]] = {
    "base":      ["certificate_requirements", "internship_experience"],
    "skill":     ["professional_skills"],
    "soft":      ["stress_resistance", "communication_skills"],
    "potential": ["innovation_capability", "learning_capability"],
}


def _dim_scores_from_comp_scores(scores_100: Dict[str, float]) -> Dict[str, float]:
    base = (scores_100["certificate_requirements"] + scores_100["internship_experience"]) / 2.0
    skill = scores_100["professional_skills"]
    soft = (scores_100["stress_resistance"] + scores_100["communication_skills"]) / 2.0
    potential = (scores_100["innovation_capability"] + scores_100["learning_capability"]) / 2.0
    return {
        "base": round(base, 1),
        "skill": round(skill, 1),
        "soft": round(soft, 1),
        "potential": round(potential, 1),
    }


def _fit_percent(student_score: float, job_score: float, evidence_empty: bool = False) -> float:
    if job_score <= 0:
        return 100.0
    if evidence_empty and student_score <= 30:
        return 0.0
    return round(min(1.0, student_score / job_score) * 100.0, 1)


def _fit_grade(pct: float) -> str:
    if pct >= 80:
        return "高度契合"
    if pct >= 60:
        return "基本契合"
    return "待提升"


def _match_level_by_score(score: float) -> str:
    if score >= 80:
        return "高度匹配"
    if score >= 60:
        return "中度匹配"
    return "低度匹配"


def _top_weight_dims(job: Dict[str, Any], top_n: int = 2) -> List[Tuple[str, float]]:
    weights = job.get("weights") or {}
    items: List[Tuple[str, float]] = []
    for k in ["base", "skill", "soft", "potential"]:
        v = weights.get(k)
        if isinstance(v, (int, float)):
            items.append((k, float(v)))
    items.sort(key=lambda x: x[1], reverse=True)
    return items[:top_n]


def _student_evidence(student: StudentProfile, key: str) -> List[str]:
    c = student.competencies
    if key == "professional_skills":
        ev = c.professional_skills.evidence
        kws = _safe_list(c.professional_skills.keywords)
        parts = []
        if ev:
            parts.append(ev)
        if kws:
            parts.append("技能关键词：" + "、".join([str(x) for x in kws]))
        return parts
    if key == "certificate_requirements":
        items = _safe_list(c.certificate_requirements.items)
        missing = _safe_list(c.certificate_requirements.missing)
        parts = []
        if items:
            parts.append("已获证书：" + "、".join([str(x) for x in items]))
        if missing:
            parts.append("建议补充：" + "、".join([str(x) for x in missing]))
        return parts
    if key == "innovation_capability":
        return [c.innovation_capability.evidence] if c.innovation_capability.evidence else []
    if key == "learning_capability":
        return [c.learning_capability.evidence] if c.learning_capability.evidence else []
    if key == "stress_resistance":
        return [c.stress_resistance.evidence] if c.stress_resistance.evidence else []
    if key == "communication_skills":
        return [c.communication_skills.evidence] if c.communication_skills.evidence else []
    if key == "internship_experience":
        parts = []
        history = _safe_list(c.internship_experience.history)
        if history:
            parts.append("实习经历：" + "；".join([_format_internship(x) for x in history]))
        if c.internship_experience.evaluation:
            parts.append(c.internship_experience.evaluation)
        return parts
    return []


def _format_internship(item: Any) -> str:
    if not isinstance(item, dict):
        return str(item)
    company = str(item.get("company", "")).strip()
    position = str(item.get("position", "")).strip()
    duration = str(item.get("duration", "")).strip()
    pieces = [x for x in [company, position, duration] if x]
    return " / ".join(pieces) if pieces else str(item)


def _job_requirement(job: Dict[str, Any], key: str) -> Dict[str, Any]:
    v = job.get(key, {}) or {}
    return {
        "dimension_key": key,
        "dimension_label": _COMP_LABELS.get(key, key),
        "level": _job_level(job, key),
        "score_100": _level_to_score_100(_job_level(job, key)),
        "keywords": _safe_list(v.get("keywords")),
        "description": str(v.get("description", "")).strip(),
    }


def _dim_evidence(student: StudentProfile, dim: str) -> List[str]:
    """
    获取指定维度的证据。
    
    支持两种维度类型：
    - 四维：base, skill, soft, potential（返回组合后的证据）
    - 七维：professional_skills, certificate_requirements, innovation_capability,
            learning_capability, stress_resistance, communication_skills, internship_experience（直接返回）
    """
    keys = []
    # 四维维度映射
    if dim == "base":
        keys = ["certificate_requirements", "internship_experience"]
    elif dim == "skill":
        keys = ["professional_skills"]
    elif dim == "soft":
        keys = ["stress_resistance", "communication_skills"]
    elif dim == "potential":
        keys = ["innovation_capability", "learning_capability"]
    # 七维维度直接映射
    elif dim in ["professional_skills", "certificate_requirements", "innovation_capability",
                 "learning_capability", "stress_resistance", "communication_skills", "internship_experience"]:
        keys = [dim]
    else:
        return []
    
    parts: List[str] = []
    for k in keys:
        parts.extend(_student_evidence(student, k))
    return [x for x in parts if str(x).strip()]


def _missing_keywords(student: StudentProfile, job: Dict[str, Any]) -> Dict[str, List[str]]:
    c = student.competencies
    student_skill_kws = {str(x).strip() for x in _safe_list(c.professional_skills.keywords) if str(x).strip()}
    student_certs = {str(x).strip() for x in _safe_list(c.certificate_requirements.items) if str(x).strip()}
    student_intern_kws = set()
    for h in _safe_list(c.internship_experience.history):
        if isinstance(h, dict):
            for k in ["company", "position", "description"]:
                v = str(h.get(k, "")).strip()
                if v:
                    student_intern_kws.add(v)
        else:
            v = str(h).strip()
            if v:
                student_intern_kws.add(v)

    def _job_kws(key: str) -> List[str]:
        return [str(x).strip() for x in _safe_list((job.get(key, {}) or {}).get("keywords")) if str(x).strip()]

    job_skill_kws = _job_kws("professional_skills")
    job_cert_kws = _job_kws("certificate_requirements")
    job_intern_kws = _job_kws("internship_experience")

    return {
        "professional_skills": [x for x in job_skill_kws if x not in student_skill_kws],
        "certificate_requirements": [x for x in job_cert_kws if x not in student_certs],
        "internship_experience": [x for x in job_intern_kws if x not in student_intern_kws],
    }


def generate_module_1(student: StudentProfile, job: Dict[str, Any], match_detail: Dict[str, Any]) -> Dict[str, Any]:
    student_comp_scores = _student_comp_scores_100(student)
    job_comp_scores = _job_comp_scores_100(job)
    student_dim_scores = match_detail.get("details", {}).get("dimensions") or _dim_scores_from_comp_scores(student_comp_scores)
    job_dim_scores = _dim_scores_from_comp_scores(job_comp_scores)

    top_focus = _top_weight_dims(job, top_n=2)
    focus_labels = [{"dimension": k, "label": _DIM_LABELS.get(k, k), "weight": round(v, 3)} for k, v in top_focus]

    four_dimensions = []
    for dim in ["base", "skill", "soft", "potential"]:
        s_score = float(student_dim_scores.get(dim, 0.0))
        j_score = float(job_dim_scores.get(dim, 0.0))
        ev = _dim_evidence(student, dim)
        is_evidence_empty = _evidence_empty(student, dim)
        # 有证据时正常算 fit；无证据时强制 0%（不在 strengths 中出现）
        if is_evidence_empty:
            pct = 0.0
        else:
            pct = _fit_percent(s_score, j_score)
        four_dimensions.append(
            {
                "dimension_key": dim,
                "dimension_label": _DIM_LABELS.get(dim, dim),
                "student_score_100": round(s_score, 1),
                "job_required_score_100": round(j_score, 1),
                "fit_percent": pct,
                "conclusion": "未收集" if is_evidence_empty else _fit_grade(pct),
                "evidence": ev if ev else ["未收集到信息"],
            }
        )

    # strengths：排除无证据的维度（不能把「无数据」的维度算作优势）
    strengths = [x for x in four_dimensions if x.get("conclusion") != "未收集" and float(x["fit_percent"]) >= 80.0]
    gaps = [x for x in four_dimensions if float(x["fit_percent"]) < 60.0]

    missing = _missing_keywords(student, job)

    gaps_detail = []
    for g in gaps:
        dim = str(g["dimension_key"])
        gap_items: List[str] = []
        if g.get("conclusion") == "未收集":
            gap_labels = {
                "base":      "证书和实习",
                "skill":     "专业技能",
                "soft":      "沟通与抗压",
                "potential": "创新与学习",
            }
            gap_items.append(f"该维度信息未收集，建议通过问答补充 {gap_labels.get(dim, dim)} 相关经历描述")
        else:
            if dim == "skill" and missing["professional_skills"]:
                gap_items.append("待补充技能：" + "、".join(missing["professional_skills"][:10]))
            if dim == "base":
                if missing["certificate_requirements"]:
                    gap_items.append("待补充证书：" + "、".join(missing["certificate_requirements"][:10]))
                if missing["internship_experience"]:
                    gap_items.append("建议补充经历：" + "、".join(missing["internship_experience"][:10]))
        gaps_detail.append(
            {
                "dimension_key": dim,
                "dimension_label": g["dimension_label"],
                "fit_percent": g["fit_percent"],
                "gap_items": gap_items,
                "evidence": g.get("evidence", []),
            }
        )

    overall_fit_percent = round(sum([float(x["fit_percent"]) for x in four_dimensions]) / 4.0, 1)
    match_score = float(match_detail.get("match_score", 0.0))
    match_level = _match_level_by_score(match_score)

    student_7d = []
    for k in _COMP_KEYS:
        raw_score = student_comp_scores.get(k, 0.0)
        ev = _student_evidence(student, k)
        is_empty = _evidence_empty(student, k)
        display_score = 0.0 if is_empty else raw_score
        student_7d.append(
            {
                "dimension_key": k,
                "dimension_label": _COMP_LABELS.get(k, k),
                "score_100": round(display_score, 1),
                "evidence": ev if ev else ["未收集到信息"],
            }
        )

    # job_7d 去掉 description（太长），keywords 仅在需要时单独查
    job_7d = [_job_requirement(job, k) for k in _COMP_KEYS]
    for item in job_7d:
        item.pop("description", None)

    # strengths/low 只看有证据的维度（score > 0 即有证据，score=0 的未收集维度不参与排序）
    valid_7d = [x for x in student_7d if float(x.get("score_100", 0.0)) > 0]
    top_student = sorted(valid_7d, key=lambda x: float(x.get("score_100", 0.0)), reverse=True)[:2]
    low_student = sorted(valid_7d, key=lambda x: float(x.get("score_100", 0.0)))[:2]
    empty_labels = [x["dimension_label"] for x in student_7d if float(x.get("score_100", 0.0)) == 0]
    strengths_text = "、".join([x["dimension_label"] for x in top_student if x.get("dimension_label")])
    gaps_text = "、".join([x["dimension_label"] for x in low_student if x.get("dimension_label")])
    empty_note = f"（另有 {', '.join(empty_labels)} 未收集）" if empty_labels else ""
    profile_summary = f"七维平均分 {round(sum([float(x['score_100']) for x in student_7d]) / 7.0, 1)} 分；优势维度：{strengths_text}；待提升：{gaps_text}。{empty_note}"

    key_gap_dims = "、".join([x["dimension_label"] for x in gaps_detail]) if gaps_detail else "暂无明显短板维度"

    return {
        # --- 学生画像 ---
        "student_info": {
            "student_name": student.basic_info.name,
            "seven_dimensions": student_7d,
            "summary": profile_summary,
        },
        # --- 目标岗位 ---
        "target_job": {
            "job_id": job.get("job_id"),
            "title": job.get("title"),
            "focus": focus_labels,
            "seven_dimensions": job_7d,
        },
        # --- 四维匹配分析 ---
        "fit_analysis": {
            "four_dimensions": four_dimensions,
            "overall_fit_percent": overall_fit_percent,
        },
        # --- 短板维度（strengths 可由前端从 fit_analysis 推导，此处只保留 gaps）---
        "gaps": gaps_detail,
        # --- 总体结论 ---
        "conclusion": {
            "match_score": round(match_score, 1),
            "match_level": match_level,
            "overall_fit_percent": overall_fit_percent,
            "key_gap_dims": key_gap_dims,
        },
    }
