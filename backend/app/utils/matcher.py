import json
import os
from typing import Dict
from app.utils.vector_utils import get_embedding, calculate_similarity
from app.models.student_profile import StudentProfile

# 全局缓存
_JOB_PROFILES = []
_JOB_EMBEDDINGS = {}  # {job_id: np.array}

def load_jobs():
    """
    加载岗位数据并预计算向量
    """
    global _JOB_PROFILES, _JOB_EMBEDDINGS
    
    # 避免重复加载
    if _JOB_PROFILES:
        return _JOB_PROFILES

    file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "job_profiles.json")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            _JOB_PROFILES = json.load(f)
            
        print(f"Loaded {len(_JOB_PROFILES)} job profiles. Generating vectors...")
        
        for job in _JOB_PROFILES:
            # 提取所有维度的关键词拼接成文本
            keywords = []
            # 遍历 7 大维度，提取 keywords
            for key in ["professional_skills", "certificate_requirements", "innovation_capability", 
                       "learning_capability", "stress_resistance", "communication_skills", "internship_experience"]:
                if key in job and "keywords" in job[key]:
                    keywords.extend(job[key]["keywords"])
            
            # 加上标题，权重最高
            text = f"{job['title']} " + " ".join(keywords)
            
            # 生成向量并缓存
            _JOB_EMBEDDINGS[job["job_id"]] = get_embedding(text)
            
        print("Job vectors generated successfully.")
        return _JOB_PROFILES
        
    except Exception as e:
        print(f"Error loading job profiles: {e}")
        return []

def calculate_match(student: StudentProfile, job: Dict) -> Dict:
    """
    计算人岗匹配度 (混合评分逻辑)
    """
    # --- 1. 硬性门槛过滤 ---
    # 学历映射表
    edu_level_map = {"大专": 1, "本科": 2, "硕士": 3, "博士": 4}
    student_edu_val = edu_level_map.get(student.basic_info.education_level, 0)
    job_min_edu_val = edu_level_map.get(job.get("min_education", "本科"), 2)
    
    if student_edu_val < job_min_edu_val:
        return _build_fail_result(job, f"学历不达标 (需{job.get('min_education')})")
        
    # 专业匹配 (宽松匹配：只要包含关键词即可)
    matched_major = False
    for target in job.get("target_majors", []):
        if target in student.basic_info.major or student.basic_info.major in target:
            matched_major = True
            break
    if not matched_major:
        # 这里可以做个妥协，如果专业不匹配但技能分极高也可以放行，暂时先严格过滤
        # return _build_fail_result(job, f"专业不匹配 (需{'/'.join(job.get('target_majors', []))})")
        # 降级处理：扣分但不完全过滤
        pass
    
    # 额外处理：如果专业不匹配，规则分上限打折
    major_penalty_factor = 1.0 if matched_major else 0.8

    # --- 2. 语义相似度计算 (60% 权重) ---
    # 构建学生向量文本
    student_keywords = []
    # 提取学生技能关键词
    student_keywords.extend(student.competencies.professional_skills.keywords)
    # 提取证书
    student_keywords.extend(student.competencies.certificate_requirements.items)
    # 提取意向岗位
    student_keywords.extend(student.career_intent.job_preferences)
    
    student_text = " ".join(student_keywords)
    student_vec = get_embedding(student_text)
    
    # 获取岗位向量
    job_vec = _JOB_EMBEDDINGS.get(job["job_id"])
    if job_vec is None:
        # 兜底：如果缓存里没有，实时生成
        job_vec = get_embedding(job["title"]) 
        
    sim_score = calculate_similarity(student_vec, job_vec) * 100  # 归一化到 0-100

    # --- 3. 规则评分 (40% 权重) ---
    # 获取学生各项能力分 (0-10)
    comp = student.competencies
    
    # 3.1 基础要求 (学历已过门槛，主要看证书+实习)
    score_base = (comp.certificate_requirements.score + comp.internship_experience.score) / 2
    
    # 3.2 职业技能
    score_skill = comp.professional_skills.score
    
    # 3.3 职业素养 (抗压+沟通)
    score_soft = (comp.stress_resistance.score + comp.communication_skills.score) / 2
    
    # 3.4 发展潜力 (创新+学习)
    score_potential = (comp.innovation_capability.score + comp.learning_capability.score) / 2
    
    # 加权计算规则分 (权重来自岗位画像)
    weights = job.get("weights", {"base": 0.25, "skill": 0.25, "soft": 0.25, "potential": 0.25})
    rule_score = (
        score_base * weights.get("base", 0.25) +
        score_skill * weights.get("skill", 0.25) +
        score_soft * weights.get("soft", 0.25) +
        score_potential * weights.get("potential", 0.25)
    ) * 10 * major_penalty_factor # 换算成 100 分制，并应用专业惩罚
    
    # --- 4. 最终混合得分 ---
    final_score = sim_score * 0.6 + rule_score * 0.4
    
    return {
        "job_id": job["job_id"],
        "title": job["title"],
        "match_score": round(final_score, 1),
        "is_qualified": True,
        "details": {
            "semantic_score": round(sim_score, 1),
            "rule_score": round(rule_score, 1),
            "dimensions": {
                "base": round(score_base * 10, 1),
                "skill": round(score_skill * 10, 1),
                "soft": round(score_soft * 10, 1),
                "potential": round(score_potential * 10, 1)
            }
        }
    }

def _build_fail_result(job, reason):
    return {
        "job_id": job["job_id"],
        "title": job["title"],
        "match_score": 0,
        "is_qualified": False,
        "fail_reason": reason
    }
