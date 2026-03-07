from pydantic import BaseModel, Field
from typing import List, Optional

# 定义赛题要求的核心能力维度 
class CompetencyMetrics(BaseModel):
    innovation: int = Field(5, ge=1, le=10, description="创新能力")
    learning: int = Field(5, ge=1, le=10, description="学习能力")
    stress: int = Field(5, ge=1, le=10, description="抗压能力")
    communication: int = Field(5, ge=1, le=10, description="沟通能力")
    internship: int = Field(5, ge=1, le=10, description="实习能力")

class StudentProfile(BaseModel):
    name: str = "待提取"
    major: str = "未知专业"
    skills: List[str] = []
    certificates: List[str] = []
    abilities: CompetencyMetrics # 嵌套上面定义的五个维度
    # 赛题要求的量化评分 [cite: 102]
    completeness_score: float = 0.0 # 完整度
    competitiveness_score: float = 0.0 # 竞争力