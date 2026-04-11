from typing import List, Optional, Dict
from pydantic import BaseModel, Field

# --- 1. 基础信息 ---
class BasicInfo(BaseModel):
    name: str = Field(..., description="姓名")
    gender: Optional[str] = Field(None, description="性别：男/女/其他/不便透露")
    university: Optional[str] = Field(None, description="毕业院校")
    major: str = Field(..., description="专业")
    education_level: str = Field(..., description="学历层次：本科/硕士/博士")
    graduation_year: Optional[int] = Field(
        None, description="毕业年份，如 2025；与 LLM 输出保持一致"
    )

# --- 2. 职业意愿 ---
class CareerIntent(BaseModel):
    expected_salary: Optional[str] = Field(default=None, description="期望薪资范围")
    job_preferences: List[str] = Field(default_factory=list, description="偏好岗位")
    target_cities: List[str] = Field(default_factory=list, description="意向城市（可多选）")

# --- 3. 核心能力 (7维度) ---
class CompetencyItem(BaseModel):
    score: int = Field(default=0, ge=0, le=10, description="能力评分(0-10)")
    evidence: str = Field(default="信息不足，无法评估", description="评分依据/证据链")
    gap_analysis: Optional[str] = Field(default=None, description="能力差距分析")

class SkillCompetency(BaseModel):
    score: int = Field(default=0, ge=0, le=10, description="技能评分(0-10)")
    evidence: str = Field(default="信息不足，无法评估", description="评分依据/证据链")
    keywords: List[str] = Field(default_factory=list, description="技能关键词")
    gap_analysis: Optional[str] = Field(default=None, description="能力差距分析")

class CertificateCompetency(BaseModel):
    score: int = Field(default=0, ge=0, le=10)
    items: List[str] = Field(default_factory=list, description="已获证书")
    missing: List[str] = Field(default_factory=list, description="缺失的关键证书")

class InternshipCompetency(BaseModel):
    score: int = Field(default=0, ge=0, le=10)
    history: List[Dict[str, str]] = Field(default_factory=list, description="实习经历列表")
    evaluation: Optional[str] = Field(default=None, description="实习质量综合评价")

class CoreCompetencies(BaseModel):
    professional_skills: SkillCompetency
    certificate_requirements: CertificateCompetency
    innovation_capability: CompetencyItem
    learning_capability: CompetencyItem
    stress_resistance: CompetencyItem
    communication_skills: CompetencyItem
    internship_experience: InternshipCompetency

# --- 4. 经历详情 ---
class ProjectExperience(BaseModel):
    name: str
    role: str
    tech_stack: List[str]
    achievement: str

class Experiences(BaseModel):
    projects: List[ProjectExperience] = Field(default_factory=list)
    awards: List[str] = Field(default_factory=list)
    main_courses: List[str] = Field(default_factory=list, description="主修课程/核心课程")
    campus_experience: Optional[str] = Field(None, description="校园经历（社团/学生工作等）")
    social_practice: Optional[str] = Field(None)

# --- 5. 职业性格 (可选) ---
class Personality(BaseModel):
    mbti: Optional[str] = Field(None)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)

# --- 总模型 ---
class StudentProfile(BaseModel):
    basic_info: BasicInfo
    career_intent: CareerIntent
    competencies: CoreCompetencies
    experiences: Experiences
    personality: Optional[Personality] = None
