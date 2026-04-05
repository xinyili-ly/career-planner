import json
import os
from typing import Any, Dict, List, Optional, Tuple
import logging

from app.models.student_profile import StudentProfile
from app.utils.llm_client import pick_and_explain_career_path


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


def _read_json(path: str, default: Any) -> Any:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def _data_path(filename: str) -> str:
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", filename)


def _get_job_by_id(jobs: List[Dict[str, Any]], job_id: str) -> Optional[Dict[str, Any]]:
    for j in jobs:
        if str(j.get("job_id")) == str(job_id):
            return j
    return None


def _safe_list(v: Any) -> List[Any]:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def _job_keywords(job: Dict[str, Any]) -> Dict[str, List[str]]:
    res: Dict[str, List[str]] = {}
    for k in _COMP_KEYS:
        kws = _safe_list((job.get(k, {}) or {}).get("keywords"))
        res[k] = [str(x).strip() for x in kws if str(x).strip()]
    return res


def _job_text_for_track_match(job: Dict[str, Any]) -> str:
    parts = [str(job.get("title", "")), str(job.get("description", ""))]
    for k in _COMP_KEYS:
        v = job.get(k, {}) or {}
        parts.extend([str(x) for x in _safe_list(v.get("keywords"))])
        parts.append(str(v.get("description", "")))
    return " ".join([p for p in parts if p and str(p).strip()])


def _infer_track_for_job(job: Dict[str, Any], raw_graph: Dict[str, Any]) -> Dict[str, Any]:
    vertical_paths = raw_graph.get("vertical_paths") or {}
    horizontal_paths = raw_graph.get("horizontal_paths") or {}
    job_text = _job_text_for_track_match(job)

    candidates: List[Dict[str, Any]] = []
    for track, info in vertical_paths.items():
        if not isinstance(info, dict):
            continue
        desc = str(info.get("description", "")).strip()
        promotion = _safe_list(info.get("promotion_path"))
        required_skills: List[str] = []
        for edge in _safe_list(horizontal_paths.get(track)):
            if isinstance(edge, dict):
                required_skills.extend([str(x).strip() for x in _safe_list(edge.get("required_skills")) if str(x).strip()])

        score = 0
        if track and str(track).strip() and str(track).strip() in job_text:
            score += 5
        for role in promotion:
            r = str(role).strip()
            if r and r in job_text:
                score += 2
        for sk in required_skills:
            if sk and sk in job_text:
                score += 1

        candidates.append(
            {
                "track": track,
                "score": score,
                "description": desc,
                "promotion_path_len": len(promotion),
            }
        )

    candidates.sort(key=lambda x: (x["score"], x["promotion_path_len"]), reverse=True)
    chosen = candidates[0]["track"] if candidates else None
    confidence = "high" if candidates and candidates[0]["score"] >= 6 else "low"
    return {"track": chosen, "confidence": confidence, "candidates": candidates[:6]}


def _overlap_and_gap(from_job: Dict[str, Any], to_job: Dict[str, Any]) -> Dict[str, Any]:
    a = _job_keywords(from_job)
    b = _job_keywords(to_job)
    overlap: Dict[str, List[str]] = {}
    gap: Dict[str, List[str]] = {}
    for k in _COMP_KEYS:
        sa = set(a.get(k, []))
        sb = set(b.get(k, []))
        overlap[k] = sorted(list(sa.intersection(sb)))[:12]
        gap[k] = sorted(list(sb.difference(sa)))[:12]
    return {"overlap": overlap, "gap": gap}


def _pick_recommendation(student: StudentProfile, match_detail: Dict[str, Any]) -> Dict[str, Any]:
    dims = (match_detail.get("details", {}) or {}).get("dimensions", {}) or {}
    skill = float(dims.get("skill", 0.0))
    potential = float(dims.get("potential", 0.0))
    soft = float(dims.get("soft", 0.0))

    strength_flags = []
    if potential >= 80:
        strength_flags.append("发展潜力较强")
    if skill >= 80:
        strength_flags.append("职业技能较强")
    if soft >= 80:
        strength_flags.append("职业素养较强")

    if potential >= 80 and skill >= 70:
        return {
            "recommended_type": "vertical",
            "why": "基于匹配结果，发展潜力与职业技能得分较高，更适合沿垂直路径逐步深化。",
            "evidence": strength_flags or ["匹配维度得分（skill/potential/soft）"],
        }
    if soft >= 80 and skill < 70:
        return {
            "recommended_type": "lateral",
            "why": "基于匹配结果，职业素养维度更突出，建议考虑与沟通/协作强相关的换岗路径。",
            "evidence": strength_flags or ["匹配维度得分（skill/potential/soft）"],
        }
    return {
        "recommended_type": "mixed",
        "why": "当前各维度较均衡，建议同时参考垂直晋升与换岗路径，优先选择与个人优势一致的路线。",
        "evidence": strength_flags or ["匹配维度得分（skill/potential/soft）"],
    }


def _build_path_options(
    vertical_paths: List[Dict[str, Any]],
    lateral_paths: List[Dict[str, Any]],
    use_raw_graph: bool,
) -> List[Dict[str, Any]]:
    options: List[Dict[str, Any]] = []
    idx = 0

    for v in vertical_paths:
        option_id = f"path_vertical_{idx}"
        idx += 1
        if use_raw_graph:
            nodes = [str(x.get("title", "")).strip() for x in _safe_list(v.get("promotion_path")) if isinstance(x, dict)]
            options.append(
                {
                    "id": option_id,
                    "type": "vertical",
                    "title": f"垂直晋升路径（{str(v.get('track', '')).strip()}）",
                    "nodes": nodes,
                    "rationale": "基于岗位图谱的晋升序列展示。",
                    "required_skills": [],
                    "trade_off": "通常需要更深的专业积累与长期投入。",
                    "evidence": {"source": "career_graph_raw.json"},
                }
            )
        else:
            nodes = [str(x.get("title", "")).strip() for x in _safe_list(v.get("path")) if isinstance(x, dict)]
            options.append(
                {
                    "id": option_id,
                    "type": "vertical",
                    "title": "垂直晋升路径",
                    "nodes": nodes,
                    "rationale": "基于赛题图谱在岗位画像库内生成的垂直路径。",
                    "required_skills": [],
                    "trade_off": "路径更聚焦同一岗位族，要求持续深化核心能力。",
                    "evidence": {"source": "career_graph.json"},
                }
            )

    for l in lateral_paths:
        option_id = f"path_lateral_{idx}"
        idx += 1
        if use_raw_graph:
            from_track = str(l.get("from_track", "")).strip()
            target_track = str(l.get("target_track", "")).strip()
            req = [str(x).strip() for x in _safe_list(l.get("required_skills")) if str(x).strip()]
            options.append(
                {
                    "id": option_id,
                    "type": "lateral",
                    "title": f"换岗路径（{from_track} → {target_track}）",
                    "nodes": [from_track, target_track],
                    "rationale": str(l.get("reason", "")).strip(),
                    "required_skills": req,
                    "trade_off": "需要补位新领域技能，短期学习成本更高。",
                    "evidence": {"source": "career_graph_raw.json"},
                }
            )
        else:
            nodes = [str(x.get("title", "")).strip() for x in _safe_list(l.get("path")) if isinstance(x, dict)]
            options.append(
                {
                    "id": option_id,
                    "type": "lateral",
                    "title": "换岗路径",
                    "nodes": nodes,
                    "rationale": "基于赛题图谱在岗位画像库内生成的换岗路径。",
                    "required_skills": [],
                    "trade_off": "需要补位跨领域能力，可能带来阶段性不确定性。",
                    "evidence": {"source": "career_graph.json"},
                }
            )

    return options[:3]


def _select_default_path(options: List[Dict[str, Any]], recommended_type: str) -> Optional[Dict[str, Any]]:
    if not options:
        return None
    if recommended_type == "vertical":
        for o in options:
            if o.get("type") == "vertical":
                return {"id": o.get("id"), "type": o.get("type"), "title": o.get("title")}
    if recommended_type == "lateral":
        for o in options:
            if o.get("type") == "lateral":
                return {"id": o.get("id"), "type": o.get("type"), "title": o.get("title")}
    return {"id": options[0].get("id"), "type": options[0].get("type"), "title": options[0].get("title")}


def _build_path_steps(path: List[str], jobs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    steps: List[Dict[str, Any]] = []
    if len(path) < 2:
        return steps
    for i in range(len(path) - 1):
        a_id = path[i]
        b_id = path[i + 1]
        a = _get_job_by_id(jobs, a_id)
        b = _get_job_by_id(jobs, b_id)
        if not a or not b:
            continue
        diff = _overlap_and_gap(a, b)
        steps.append(
            {
                "from_job": {"job_id": a.get("job_id"), "title": a.get("title")},
                "to_job": {"job_id": b.get("job_id"), "title": b.get("title")},
                "overlap": diff["overlap"],
                "gap": diff["gap"],
                "evidence": {
                    "from_keywords": _job_keywords(a),
                    "to_keywords": _job_keywords(b),
                },
            }
        )
    return steps


async def generate_module_2(
    student: StudentProfile,
    target_job: Dict[str, Any],
    match_detail: Dict[str, Any],
    jobs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    signals = _read_json(_data_path("job_market_signals.json"), {})
    raw_graph = _read_json(_data_path("career_graph_raw.json"), {})
    graph = _read_json(_data_path("career_graph.json"), {"vertical_paths": {}, "lateral_paths": {}})

    target_id = str(target_job.get("job_id"))
    signal = signals.get(target_id) or {}

    demand = {
        "demand_level": signal.get("demand_level", "待补充"),
        "demand_evidence": signal.get("demand_evidence", "暂无证据，请补充岗位需求依据。"),
        "trend_direction": signal.get("trend_direction", "待补充"),
        "trend_evidence": signal.get("trend_evidence", "暂无证据，请补充趋势依据。"),
    }

    use_raw_graph = isinstance(raw_graph, dict) and "vertical_paths" in raw_graph and "horizontal_paths" in raw_graph
    vertical_paths = (graph.get("vertical_paths") or {}).get(target_id) or []
    lateral_paths = (graph.get("lateral_paths") or {}).get(target_id) or []

    vertical = []
    lateral = []

    track_match = None
    if use_raw_graph:
        track_match = _infer_track_for_job(target_job, raw_graph)
        track = track_match.get("track") if isinstance(track_match, dict) else None
        vinfo = (raw_graph.get("vertical_paths") or {}).get(track) if track else None
        if isinstance(vinfo, dict):
            promotion = [str(x).strip() for x in _safe_list(vinfo.get("promotion_path")) if str(x).strip()]
            vertical.append(
                {
                    "track": track,
                    "description": str(vinfo.get("description", "")).strip(),
                    "promotion_path": [{"title": x, "order": i + 1} for i, x in enumerate(promotion)],
                    "notes": [
                        "图谱节点包含扩展岗位（非岗位画像库内岗位），此处仅展示路径与图谱给定理由/补位技能，不做量化匹配评分。"
                    ],
                }
            )

        edges = (raw_graph.get("horizontal_paths") or {}).get(track) if track else None
        if isinstance(edges, list):
            target_skill_kws = set(_job_keywords(target_job).get("professional_skills", []))
            for e in edges[:4]:
                if not isinstance(e, dict):
                    continue
                req_skills = [str(x).strip() for x in _safe_list(e.get("required_skills")) if str(x).strip()]
                overlap = [x for x in req_skills if x in target_skill_kws]
                lateral.append(
                    {
                        "from_track": track,
                        "target_track": str(e.get("target", "")).strip(),
                        "reason": str(e.get("reason", "")).strip(),
                        "required_skills": req_skills,
                        "skill_overlap_with_target_job": overlap,
                    }
                )
    else:
        for p in vertical_paths[:2]:
            if not isinstance(p, list) or len(p) < 2:
                continue
            vertical.append(
                {
                    "path": [{"job_id": x, "title": (_get_job_by_id(jobs, x) or {}).get("title", "")} for x in p],
                    "steps": _build_path_steps([str(x) for x in p], jobs),
                }
            )

        for p in lateral_paths[:2]:
            if not isinstance(p, list) or len(p) < 2:
                continue
            lateral.append(
                {
                    "path": [{"job_id": x, "title": (_get_job_by_id(jobs, x) or {}).get("title", "")} for x in p],
                    "steps": _build_path_steps([str(x) for x in p], jobs),
                }
            )

    rec = _pick_recommendation(student, match_detail)

    focus = []
    weights = target_job.get("weights") or {}
    for k in ["base", "skill", "soft", "potential"]:
        v = weights.get(k)
        if isinstance(v, (int, float)):
            focus.append({"dimension_key": k, "dimension_label": _DIM_LABELS.get(k, k), "weight": round(float(v), 3)})
    focus.sort(key=lambda x: x["weight"], reverse=True)

    path_options = _build_path_options(vertical, lateral, use_raw_graph)
    recommended_path = _select_default_path(path_options, str(rec.get("recommended_type", "mixed")))
    selected_path = recommended_path

    result: Dict[str, Any] = {
        "goal": {
            "target_job_id": target_job.get("job_id"),
            "target_job_title": target_job.get("title"),
        },
        "market_trend": {
            "demand_level": demand["demand_level"],
            "demand_evidence": demand["demand_evidence"],
            "trend_direction": demand["trend_direction"],
            "trend_evidence": demand["trend_evidence"],
        },
        "career_paths": {
            "path_options": path_options,
            "recommended_path": recommended_path,
            "selected_path": selected_path,
        },
    }

    # --- LLM 参与路径决策：在候选 path_options 中选择 best_path 并给出解释 ---
    logger = logging.getLogger("CareerAgent")
    llm_status = "no_candidates"
    try:
        if path_options:
            llm_choice = await pick_and_explain_career_path(
                student=student,
                target_job=target_job,
                match_detail=match_detail,
                market_trend=result["market_trend"],
                candidate_paths=path_options,
            )

            best_id = str(llm_choice.get("best_path_id") or "").strip()
            if best_id:
                for o in path_options:
                    if str(o.get("id")) == best_id:
                        result["career_paths"]["recommended_path"] = {
                            "id": o.get("id"),
                            "type": o.get("type"),
                            "title": o.get("title"),
                        }
                        result["career_paths"]["selected_path"] = result["career_paths"]["recommended_path"]
                        break

            # llm_commentary 只保留 LLM 特有的推理内容，去掉对 path_options 的重复描述
            result["career_paths"]["llm_commentary"] = {
                "best_path_id": llm_choice.get("best_path_id"),
                "overall_summary": llm_choice.get("overall_summary"),
                "risk_and_opportunity": llm_choice.get("risk_and_opportunity", []),
            }
            llm_status = "ok" if best_id else "empty_or_invalid"
        else:
            llm_status = "no_candidates"
    except Exception as e:
        logger.error("职业路径决策 LLM 处理失败: %s", str(e), exc_info=True)
        llm_status = "error"

    result["llm_status"] = llm_status
    return result
