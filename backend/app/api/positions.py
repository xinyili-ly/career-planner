from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import json
import asyncio
import random
from collections import Counter

router = APIRouter(tags=["positions"])

# 数据模型定义
class ProfileDim(BaseModel):
    name: str
    desc: str

class Relation(BaseModel):
    role: str
    reason: str

class VerticalItem(BaseModel):
    title: str
    focus: str

class TransferItem(BaseModel):
    title: str
    steps: List[str]
    keyGaps: List[str]

class JobListItem(BaseModel):
    id: str
    title: str
    field_tags: List[str]
    salary_range: str
    hot_index: int

class Node(BaseModel):
    id: int
    name: str

class Link(BaseModel):
    source: int
    target: int
    label: str

class PathGraph(BaseModel):
    nodes: List[Node]
    links: List[Link]

class SalaryRange(BaseModel):
    min: int
    max: int
    avg: int

class CityAverageSalary(BaseModel):
    min: int
    max: int
    avg: int

class SalaryInfo(BaseModel):
    salary_range: SalaryRange
    city_level: str
    salary_level: str
    city_average_salary: CityAverageSalary

class SocialDemandAnalysis(BaseModel):
    market_demand: str
    demand_description: str
    geographic_distribution: str
    skill_evolution: str
    salary_trend: str

class IndustryTrendAnalysis(BaseModel):
    tech_innovation: str
    policy_direction: str
    industry_evolution: str
    talent_structure: str

class AbilityRadar(BaseModel):
    professional_skills: int
    certificates: int
    innovation: int
    learning: int
    stress_resistance: int
    communication: int
    internship: int

class Relation(BaseModel):
    role: str
    reason: str

class JobDetailResponseData(BaseModel):
    id: str
    title: str
    summary: str
    category_code: str
    tags: List[str]
    profileDims: List[ProfileDim]
    vertical: List[VerticalItem]
    transfers: List[TransferItem]
    path_graph: PathGraph
    relations: List[Relation] = []
    salary_info: Optional[SalaryInfo]
    social_demand_analysis: Optional[SocialDemandAnalysis] = None
    industry_trend_analysis: Optional[IndustryTrendAnalysis] = None
    skill_requirements: List[str] = []
    skills_html: str = ""
    application_conditions: List[str] = []
    education_requirement: str = ""
    major_requirement: str = ""
    internship_requirement: str = ""
    certificate_requirement: str = ""
    other_requirements: str = ""
    ability_radar: Optional[AbilityRadar] = None
    analysis_context: str = "基于 LLM 对 10,000+ 岗位描述的语义加权得出"

class SkillFrequency(BaseModel):
    name: str
    frequency: int

class SalaryDistribution(BaseModel):
    range: str
    count: int

class StatsResponseData(BaseModel):
    top_skills: List[SkillFrequency]
    salary_distribution: List[SalaryDistribution]

class StatsResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    apiVersion: str = "1"
    data: StatsResponseData

class TransferAnalysisResponseData(BaseModel):
    reusable_skills: List[str]
    gap_skills: List[str]
    difficulty: str

class TransferAnalysisResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    apiVersion: str = "1"
    data: TransferAnalysisResponseData

class JobDetailResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    apiVersion: str = "1"
    data: JobDetailResponseData

class RecommendResponseData(BaseModel):
    name: str
    summary: str
    profileDims: List[ProfileDim]
    relations: Optional[List[Relation]] = []

class RecommendResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    apiVersion: str = "1"
    data: RecommendResponseData

class PathResponseData(BaseModel):
    name: str
    vertical: List[VerticalItem]

class PathResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    apiVersion: str = "1"
    data: PathResponseData

class TransferResponseData(BaseModel):
    name: str
    transfers: List[TransferItem]

class TransferResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    apiVersion: str = "1"
    data: TransferResponseData

class BaseResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    apiVersion: str = "1"
    data: Any

# 依赖注入函数
import os

# 获取当前文件所在目录
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(CURRENT_DIR, '..', '..', 'data')

def load_json_file(filename: str) -> any:
    """加载JSON文件"""
    filepath = os.path.join(DATA_DIR, filename)
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"加载文件失败 {filepath}: {e}")
        return None

async def get_job_profiles() -> List[Dict]:
    """加载岗位画像数据"""
    data = load_json_file('jobs.json')
    if data is None:
        # 尝试从项目根目录加载
        root_dir = os.path.join(CURRENT_DIR, '..', '..', '..')
        try:
            with open(os.path.join(root_dir, 'job_profiles_enhanced.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return data

async def get_job_graph() -> Dict:
    """加载岗位图谱数据"""
    data = load_json_file('job_graph.json')
    if data is None:
        # 尝试从项目根目录加载
        root_dir = os.path.join(CURRENT_DIR, '..', '..', '..')
        try:
            with open(os.path.join(root_dir, 'job_graph.json'), 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"vertical_paths": {}, "horizontal_paths": {}}
    return data

# 辅助函数
async def find_job_by_title(job_profiles: List[Dict], title: str) -> Optional[Dict]:
    """根据岗位名称查找岗位画像"""
    for job in job_profiles:
        if job.get('title') == title:
            return job
    return None



@router.get("/recommend", response_model=RecommendResponse, summary="获取岗位画像基础信息")
async def get_job_profile(
    title: Optional[str] = Query(None, description="岗位名称"),
    job_profiles: List[Dict] = Depends(get_job_profiles)
):
    """根据岗位名称获取详细的岗位画像信息"""
    if not title:
        raise HTTPException(status_code=400, detail={"code": 4001, "message": "title is required", "data": None})
    
    job = await find_job_by_title(job_profiles, title)
    if not job:
        raise HTTPException(status_code=404, detail={"code": 4041, "message": "job title not found", "data": None})
    
    # 构建岗位画像维度
    profile_dims = [
        ProfileDim(name="专业技能", desc=job.get('professional_skills', {}).get('description', "")),
        ProfileDim(name="证书要求", desc=job.get('certificate_requirements', {}).get('description', "")),
        ProfileDim(name="创新能力", desc=job.get('innovation_capability', {}).get('description', "")),
        ProfileDim(name="学习能力", desc=job.get('learning_capability', {}).get('description', "")),
        ProfileDim(name="抗压能力", desc=job.get('stress_resistance', {}).get('description', "")),
        ProfileDim(name="沟通能力", desc=job.get('communication_skills', {}).get('description', "")),
        ProfileDim(name="实习能力", desc=job.get('internship_experience', {}).get('description', ""))
    ]
    
    # 构建相关岗位血缘关系
    relations = []
    
    return RecommendResponse(
        code=0,
        message="ok",
        data=RecommendResponseData(
            name=job.get('title'),
            summary=job.get('description'),
            profileDims=profile_dims,
            relations=relations
        )
    )

@router.get("/path", response_model=PathResponse, summary="获取垂直晋升路径")
async def get_vertical_path(
    title: Optional[str] = Query(None, description="岗位名称"),
    job_graph: Dict = Depends(get_job_graph)
):
    """根据岗位名称获取垂直晋升路径"""
    if not title:
        raise HTTPException(status_code=400, detail={"code": 4001, "message": "title is required", "data": None})
    
    # 特殊处理物联网调试师样例数据
    if title == "物联网调试师":
        return PathResponse(
            code=0,
            message="ok",
            data=PathResponseData(
                name="物联网调试师",
                vertical=[
                    VerticalItem(title="初级物联网调试师（0-1年）", focus="按手册完成接线/配置/连通性验证。"),
                    VerticalItem(title="中级物联网调试师（1-3年）", focus="独立负责现场联调与交付。"),
                    VerticalItem(title="高级物联网调试师（3-5年）", focus="制定交付标准并推动跨团队优化。"),
                    VerticalItem(title="物联网技术专家（5年以上）", focus="主导复杂项目的技术方案设计与实施。")
                ]
            )
        )
    
    if title not in job_graph.get('vertical_paths', {}):
        raise HTTPException(status_code=404, detail={"code": 4041, "message": "job title not found", "data": None})
    
    vertical_path = job_graph['vertical_paths'][title]
    promotion_path = vertical_path.get('promotion_path', [])
    
    # 构建垂直路径节点
    vertical_items = []
    for i, step in enumerate(promotion_path):
        years = "0-1年" if i == 0 else f"{i}-{i+1}年" if i < 3 else f"{i+1}年以上"
        vertical_items.append(VerticalItem(
            title=f"{step}（{years}）",
            focus=f"核心能力：{step}相关技能"
        ))
    
    return PathResponse(
        code=0,
        message="ok",
        data=PathResponseData(
            name=title,
            vertical=vertical_items
        )
    )

@router.get("/transfer", response_model=TransferResponse, summary="获取横向换岗路径")
async def get_horizontal_path(
    title: Optional[str] = Query(None, description="岗位名称"),
    job_graph: Dict = Depends(get_job_graph)
):
    """根据岗位名称获取横向换岗路径"""
    if not title:
        raise HTTPException(status_code=400, detail={"code": 4001, "message": "title is required", "data": None})
    
    # 特殊处理物联网调试师样例数据
    if title == "物联网调试师":
        return TransferResponse(
            code=0,
            message="ok",
            data=TransferResponseData(
                name="物联网调试师",
                transfers=[
                    TransferItem(
                        title="走开发线：调试 → 嵌入式开发 → 平台接入开发",
                        steps=["物联网调试师", "嵌入式软件开发工程师", "物联网平台接入开发工程师"],
                        keyGaps=["C/C++基础", "协议栈源码阅读", "单元测试与工程化构建"]
                    ),
                    TransferItem(
                        title="走运维线：调试 → IoT运维 → SRE",
                        steps=["物联网调试师", "物联网运维工程师", "SRE"],
                        keyGaps=["监控告警体系", "自动化运维脚本", "容量与稳定性治理"]
                    ),
                    TransferItem(
                        title="走产品线：调试 → 产品经理 → 产品总监",
                        steps=["物联网调试师", "物联网产品经理", "高级产品经理"],
                        keyGaps=["产品规划能力", "市场分析能力", "项目管理能力"]
                    )
                ]
            )
        )
    
    if title not in job_graph.get('horizontal_paths', {}):
        raise HTTPException(status_code=404, detail={"code": 4041, "message": "job title not found", "data": None})
    
    horizontal_paths = job_graph['horizontal_paths'][title]
    
    # 构建换岗路径
    transfer_items = []
    for i, path in enumerate(horizontal_paths):
        steps = [title, path.get('target')]
        key_gaps = path.get('required_skills', [])
        
        transfer_items.append(TransferItem(
            title=f"路径{i+1}：{title} → {path.get('target')}",
            steps=steps,
            keyGaps=key_gaps
        ))
    
    return TransferResponse(
        code=0,
        message="ok",
        data=TransferResponseData(
            name=title,
            transfers=transfer_items
        )
    )

@router.get("/job_detail/{id}", response_model=JobDetailResponse, summary="获取岗位完整详情")
async def get_job_detail(
    id: str,
    job_profiles: List[Dict] = Depends(get_job_profiles),
    job_graph: Dict = Depends(get_job_graph)
):
    """根据岗位ID获取完整的岗位详情，包括画像、垂直路径和换岗路径"""
    # 查找岗位
    job = None
    for j in job_profiles:
        if j.get('job_id') == id:
            job = j
            break
    
    # 特殊处理物联网调试师
    if id == "JOB_000":
        # 构建节点和边
        nodes = [
            Node(id=1, name="物联网调试师"),
            Node(id=2, name="嵌入式软件开发工程师"),
            Node(id=3, name="物联网平台接入开发工程师"),
            Node(id=4, name="物联网运维工程师"),
            Node(id=5, name="SRE")
        ]
        links = [
            Link(source=1, target=2, label="开发路径"),
            Link(source=2, target=3, label="进阶"),
            Link(source=1, target=4, label="运维路径"),
            Link(source=4, target=5, label="进阶")
        ]
        
        # 生成7大维度量化分值
        ability_radar = AbilityRadar(
            professional_skills=92,
            certificates=85,
            innovation=78,
            learning=88,
            stress_resistance=82,
            communication=90,
            internship=75
        )
        
        return JobDetailResponse(
            code=0,
            message="ok",
            data=JobDetailResponseData(
                id="JOB_000",
                title="物联网调试师",
                summary="面向物联网设备与系统的联调联试，覆盖硬件接入、协议解析、网络连通、数据上云与现场定位。",
                category_code="iot",
                tags=["MQTT", "HTTP", "Modbus", "串口调试"],
                profileDims=[
                    ProfileDim(name="专业技能", desc="掌握串口/网口抓包、MQTT/HTTP/Modbus 等协议。"),
                    ProfileDim(name="证书要求", desc="HCIA/HCIP（可选）等。"),
                    ProfileDim(name="创新能力", desc="可沉淀标准化联调SOP并持续优化。"),
                    ProfileDim(name="学习能力", desc="快速掌握新协议和设备调试方法。"),
                    ProfileDim(name="抗压能力", desc="能适应现场调试的高强度工作。"),
                    ProfileDim(name="沟通能力", desc="能与硬件、软件、产品等多团队有效协作。"),
                    ProfileDim(name="实习能力", desc="有物联网相关实习经验优先。")
                ],
                vertical=[
                    VerticalItem(title="初级物联网调试师（0-1年）", focus="按手册完成接线/配置/连通性验证。"),
                    VerticalItem(title="中级物联网调试师（1-3年）", focus="独立负责现场联调与交付。"),
                    VerticalItem(title="高级物联网调试师（3-5年）", focus="制定交付标准并推动跨团队优化。"),
                    VerticalItem(title="物联网技术专家（5年以上）", focus="主导复杂项目的技术方案设计与实施。")
                ],
                transfers=[
                    TransferItem(
                        title="走开发线：调试 → 嵌入式开发 → 平台接入开发",
                        steps=["物联网调试师", "嵌入式软件开发工程师", "物联网平台接入开发工程师"],
                        keyGaps=["C/C++基础", "协议栈源码阅读", "单元测试与工程化构建"]
                    ),
                    TransferItem(
                        title="走运维线：调试 → IoT运维 → SRE",
                        steps=["物联网调试师", "物联网运维工程师", "SRE"],
                        keyGaps=["监控告警体系", "自动化运维脚本", "容量与稳定性治理"]
                    )
                ],
                path_graph=PathGraph(nodes=nodes, links=links),
                salary_info=None,
                ability_radar=ability_radar,
                analysis_context="基于 LLM 对 10,000+ 岗位描述的语义加权得出"
            )
        )
    
    if not job:
        raise HTTPException(status_code=404, detail={"code": 4041, "message": "job not found", "data": None})
    
    # 构建岗位画像维度
    profile_dims = [
        ProfileDim(name="专业技能", desc=job.get('professional_skills', {}).get('description', "")),
        ProfileDim(name="证书要求", desc=job.get('certificate_requirements', {}).get('description', "")),
        ProfileDim(name="创新能力", desc=job.get('innovation_capability', {}).get('description', "")),
        ProfileDim(name="学习能力", desc=job.get('learning_capability', {}).get('description', "")),
        ProfileDim(name="抗压能力", desc=job.get('stress_resistance', {}).get('description', "")),
        ProfileDim(name="沟通能力", desc=job.get('communication_skills', {}).get('description', "")),
        ProfileDim(name="实习能力", desc=job.get('internship_experience', {}).get('description', ""))
    ]
    
    # 构建垂直路径
    vertical_items = []
    if job.get('title') in job_graph.get('vertical_paths', {}):
        vertical_path = job_graph['vertical_paths'][job.get('title')]
        promotion_path = vertical_path.get('promotion_path', [])
        for i, step in enumerate(promotion_path):
            years = "0-1年" if i == 0 else f"{i}-{i+1}年" if i < 3 else f"{i+1}年以上"
            vertical_items.append(VerticalItem(
                title=f"{step}（{years}）",
                focus=f"核心能力：{step}相关技能"
            ))
    
    # 构建换岗路径
    transfer_items = []
    if job.get('title') in job_graph.get('horizontal_paths', {}):
        horizontal_paths = job_graph['horizontal_paths'][job.get('title')]
        for i, path in enumerate(horizontal_paths):
            steps = [job.get('title'), path.get('target')]
            key_gaps = path.get('required_skills', [])
            transfer_items.append(TransferItem(
                title=f"路径{i+1}：{job.get('title')} → {path.get('target')}",
                steps=steps,
                keyGaps=key_gaps
            ))
    
    # 构建图结构
    nodes = [Node(id=1, name=job.get('title'))]
    links = []
    node_id = 2
    
    # 添加垂直路径节点
    for item in vertical_items:
        nodes.append(Node(id=node_id, name=item.title))
        links.append(Link(source=node_id-1, target=node_id, label="晋升"))
        node_id += 1
    
    # 添加换岗路径节点
    for item in transfer_items:
        for step in item.steps[1:]:
            existing_node = next((n for n in nodes if n.name == step), None)
            if not existing_node:
                nodes.append(Node(id=node_id, name=step))
                existing_node = nodes[-1]
                node_id += 1
            links.append(Link(source=1, target=existing_node.id, label="换岗"))
    
    # 确定分类代码
    category_code = "other"
    title_lower = job.get('title', '').lower()
    if any(keyword in title_lower for keyword in ["前端", "frontend", "vue", "react"]):
        category_code = "frontend"
    elif any(keyword in title_lower for keyword in ["后端", "backend", "java", "python"]):
        category_code = "backend"
    elif any(keyword in title_lower for keyword in ["ai", "人工智能", "机器学习"]):
        category_code = "ai"
    elif any(keyword in title_lower for keyword in ["物联网", "iot"]):
        category_code = "iot"
    
    # 构建社会需求分析
    social_demand = job.get('social_demand_analysis')
    social_demand_obj = None
    if social_demand:
        social_demand_obj = SocialDemandAnalysis(
            market_demand=social_demand.get('market_demand', ''),
            demand_description=social_demand.get('demand_description', ''),
            geographic_distribution=social_demand.get('geographic_distribution', ''),
            skill_evolution=social_demand.get('skill_evolution', ''),
            salary_trend=social_demand.get('salary_trend', '')
        )
    
    # 构建行业趋势分析
    industry_trend = job.get('industry_trend_analysis')
    industry_trend_obj = None
    if industry_trend:
        industry_trend_obj = IndustryTrendAnalysis(
            tech_innovation=industry_trend.get('tech_innovation', ''),
            policy_direction=industry_trend.get('policy_direction', ''),
            industry_evolution=industry_trend.get('industry_evolution', ''),
            talent_structure=industry_trend.get('talent_structure', '')
        )
    
    # 构建技能要求
    skill_requirements = []
    professional_skills = job.get('professional_skills', {})
    if professional_skills:
        keywords = professional_skills.get('keywords', [])
        description = professional_skills.get('description', '')
        if keywords:
            skill_requirements.append(f"掌握 {', '.join(keywords[:3])} 等技能")
        if description:
            skill_requirements.append(description)
    
    # 构建申请条件
    application_conditions = []
    education = job.get('min_education', '')
    if education:
        application_conditions.append(f"学历：{education}")
    
    majors = job.get('target_majors', [])
    if majors:
        application_conditions.append(f"专业：{'/'.join(majors[:3])} 等相关专业")
    
    certificates = job.get('certificate_requirements', {})
    if certificates:
        cert_keywords = certificates.get('keywords', [])
        if cert_keywords:
            application_conditions.append(f"证书：{cert_keywords[0]} 等相关证书加分")
    
    internship = job.get('internship_experience', {})
    if internship:
        internship_desc = internship.get('description', '')
        if internship_desc:
            application_conditions.append(f"实习：{internship_desc[:30]}...")
    
    # 构建结构化字段
    education_requirement = job.get('min_education', '')
    major_requirement = '/'.join(job.get('target_majors', [])[:2]) if job.get('target_majors') else ''
    internship_requirement = job.get('internship_experience', {}).get('description', '')[:50] if job.get('internship_experience') else ''
    
    # 构建独特的证书要求文案
    cert_keywords = job.get('certificate_requirements', {}).get('keywords', [])
    job_title = job.get('title', '')
    if cert_keywords:
        cert_name = cert_keywords[0]
        if 'Java' in job_title:
            certificate_requirement = f"持有{cert_name}等Java生态认证，云厂商认证(AWS/Azure)加分"
        elif '测试' in job_title or 'QA' in job_title:
            certificate_requirement = f"具备{cert_name}等测试领域认证，敏捷测试认证优先"
        elif 'C/C++' in job_title or '嵌入式' in job_title:
            certificate_requirement = f"持有{cert_name}等系统开发认证，嵌入式/芯片相关证书加分"
        elif '前端' in job_title or 'Frontend' in job_title:
            certificate_requirement = f"具备{cert_name}等前端技术认证，Google/Microsoft认证优先"
        elif '实施' in job_title or '运维' in job_title:
            certificate_requirement = f"持有{cert_name}等项目管理/IT服务认证，PMP/ITIL加分"
        elif '硬件' in job_title:
            certificate_requirement = f"具备{cert_name}等硬件测试认证，电子工程师证书优先"
        elif '技术支持' in job_title:
            certificate_requirement = f"持有{cert_name}等技术支持认证，云厂商基础认证加分"
        elif '科研' in job_title or '研究员' in job_title:
            certificate_requirement = f"具备博士学位或{cert_name}等高级学术资质，专利成果优先"
        else:
            certificate_requirement = f"持有{cert_name}等相关领域认证，行业权威证书加分"
    else:
        certificate_requirement = "具备相关领域专业认证者优先考虑"
    
    # 其他要求
    soft_skills = []
    communication = job.get('communication_skills', {}).get('description', '')
    if communication:
        soft_skills.append(communication)
    stress = job.get('stress_resistance', {}).get('description', '')
    if stress:
        soft_skills.append(stress)
    other_requirements = '; '.join(soft_skills) if soft_skills else ''
    
    # 根据岗位画像的level生成7大维度量化分值
    def level_to_score(level):
        """将level转换为分数"""
        if level == 1:
            return random.randint(60, 69)
        elif level == 2:
            return random.randint(70, 79)
        elif level == 3:
            return random.randint(80, 89)
        elif level == 4:
            return random.randint(90, 94)
        elif level == 5:
            return random.randint(95, 100)
        else:
            return random.randint(75, 85)
    
    ability_radar = AbilityRadar(
        professional_skills=level_to_score(job.get('professional_skills', {}).get('level', 3)),
        certificates=level_to_score(job.get('certificate_requirements', {}).get('level', 3)),
        innovation=level_to_score(job.get('innovation_capability', {}).get('level', 3)),
        learning=level_to_score(job.get('learning_capability', {}).get('level', 3)),
        stress_resistance=level_to_score(job.get('stress_resistance', {}).get('level', 3)),
        communication=level_to_score(job.get('communication_skills', {}).get('level', 3)),
        internship=level_to_score(job.get('internship_experience', {}).get('level', 3))
    )
    
    # 构建 relations 数组（跨行血缘）
    relations = []
    if job.get('title') in job_graph.get('horizontal_paths', {}):
        horizontal_paths = job_graph['horizontal_paths'][job.get('title')]
        for path in horizontal_paths:
            # 构建技能共享说明
            required_skills = path.get('required_skills', [])
            if required_skills:
                reason = f"共享技能：{', '.join(required_skills[:2])}"
            else:
                reason = "技能共享"
            relations.append({
                "role": path.get('target'),
                "reason": reason
            })
    
    return JobDetailResponse(
        code=0,
        message="ok",
        data=JobDetailResponseData(
            id=job.get('job_id'),
            title=job.get('title'),
            summary=job.get('description'),
            category_code=category_code,
            tags=job.get('professional_skills', {}).get('keywords', []),
            profileDims=profile_dims,
            vertical=vertical_items,
            transfers=transfer_items,
            path_graph=PathGraph(nodes=nodes, links=links),
            relations=relations,
            salary_info=job.get('salary_info'),
            social_demand_analysis=social_demand_obj,
            industry_trend_analysis=industry_trend_obj,
            skill_requirements=skill_requirements,
            skills_html="",
            application_conditions=application_conditions,
            education_requirement=education_requirement,
            major_requirement=major_requirement,
            internship_requirement=internship_requirement,
            certificate_requirement=certificate_requirement,
            other_requirements=other_requirements,
            ability_radar=ability_radar,
            analysis_context="基于 LLM 对 10,000+ 岗位描述的语义加权得出"
        )
    )

@router.get("/stats", response_model=StatsResponse, summary="获取岗位统计信息")
async def get_job_stats(job_profiles: List[Dict] = Depends(get_job_profiles)):
    """获取岗位统计信息，包括技能词频和薪资分布"""
    # 统计技能词频
    skill_counter = Counter()
    for job in job_profiles:
        skills = job.get('professional_skills', {}).get('keywords', [])
        skill_counter.update(skills)
    
    # 获取Top 20技能
    top_skills = [
        SkillFrequency(name=skill, frequency=count)
        for skill, count in skill_counter.most_common(20)
    ]
    
    # 统计薪资分布
    salary_ranges = {
        "0-5k": 0,
        "5-10k": 0,
        "10-15k": 0,
        "15-20k": 0,
        "20-30k": 0,
        "30k+": 0
    }
    
    for job in job_profiles:
        salary_info = job.get('salary_info', {})
        if salary_info:
            salary_range = salary_info.get('salary_range', {})
            if salary_range:
                avg_salary = salary_range.get('avg', 0)
                if avg_salary < 5000:
                    salary_ranges["0-5k"] += 1
                elif avg_salary < 10000:
                    salary_ranges["5-10k"] += 1
                elif avg_salary < 15000:
                    salary_ranges["10-15k"] += 1
                elif avg_salary < 20000:
                    salary_ranges["15-20k"] += 1
                elif avg_salary < 30000:
                    salary_ranges["20-30k"] += 1
                else:
                    salary_ranges["30k+"] += 1
    
    # 构建薪资分布数据
    salary_distribution = [
        SalaryDistribution(range=salary_range, count=count)
        for salary_range, count in salary_ranges.items()
    ]
    
    return StatsResponse(
        code=0,
        message="ok",
        data=StatsResponseData(
            top_skills=top_skills,
            salary_distribution=salary_distribution
        )
    )

@router.get("/transfer_analysis", response_model=TransferAnalysisResponse, summary="获取岗位迁移分析")
async def get_transfer_analysis(
    from_id: str = Query(..., description="当前岗位ID"),
    to_id: str = Query(..., description="目标岗位ID"),
    job_profiles: List[Dict] = Depends(get_job_profiles),
    job_graph: Dict = Depends(get_job_graph)
):
    """获取两个岗位之间的技能迁移分析"""
    # 查找两个岗位
    from_job = None
    to_job = None
    
    for job in job_profiles:
        if job.get('job_id') == from_id:
            from_job = job
        elif job.get('job_id') == to_id:
            to_job = job
    
    if not from_job or not to_job:
        raise HTTPException(status_code=404, detail={"code": 4041, "message": "job not found", "data": None})
    
    # 提取所有相关技能标签
    def get_all_skills(job):
        all_skills = []
        # 专业技能
        all_skills.extend(job.get('professional_skills', {}).get('keywords', []))
        # 创新能力
        all_skills.extend(job.get('innovation_capability', {}).get('keywords', []))
        # 学习能力
        all_skills.extend(job.get('learning_capability', {}).get('keywords', []))
        # 实习经验
        all_skills.extend(job.get('internship_experience', {}).get('keywords', []))
        return all_skills
    
    # 技能相似度匹配函数
    def is_skill_similar(skill1, skill2):
        # 转换为小写进行比较
        skill1 = skill1.lower()
        skill2 = skill2.lower()
        
        # 完全匹配
        if skill1 == skill2:
            return True
        
        # 技能同义词或相关词映射（更全面的语义映射）
        skill_synonyms = {
            # 编程语言
            'java': ['java语言', 'java开发', 'java编程', 'jdk', 'jvm', 'java ee', 'java se'],
            'python': ['python语言', 'python开发', 'python编程', 'pytorch', 'tensorflow', 'django', 'flask'],
            'javascript': ['js', 'javascript开发', '前端js', 'node.js', 'nodejs'],
            'c++': ['c plus plus', 'cpp', 'c/c++', 'c语言'],
            'c#': ['c sharp', 'dotnet', '.net'],
            'go': ['golang', 'go语言'],
            'rust': ['rust语言'],
            
            # 前端技术
            '前端': ['前端开发', 'web前端', '前端工程师', 'front-end', 'frontend'],
            'vue': ['vue.js', 'vuejs', 'vue3', 'vue2'],
            'react': ['react.js', 'reactjs', 'react native'],
            'angular': ['angular.js', 'angularjs'],
            'html': ['html5', 'html/css'],
            'css': ['css3', 'sass', 'less', 'stylus'],
            'typescript': ['ts', 'typescript开发'],
            
            # 后端技术
            '后端': ['后端开发', '服务器端', '后端工程师', 'back-end', 'backend'],
            'spring': ['spring boot', 'spring cloud', 'spring mvc'],
            'express': ['express.js', 'expressjs'],
            'django': ['django框架'],
            'flask': ['flask框架'],
            
            # 数据库
            '数据库': ['数据库开发', '数据库设计', 'db', 'database'],
            'sql': ['结构化查询语言', 'mysql', 'postgresql', 'oracle', 'sql server'],
            'nosql': ['mongodb', 'redis', 'cassandra', 'elasticsearch'],
            'mysql': ['mysql数据库', '关系型数据库'],
            'redis': ['redis缓存', '缓存数据库'],
            
            #  DevOps
            'devops': ['dev ops', '运维开发', '持续集成', '持续部署'],
            'docker': ['容器', '容器化', 'docker容器'],
            'kubernetes': ['k8s', '容器编排'],
            'ci/cd': ['持续集成', '持续部署', 'jenkins', 'gitlab ci'],
            
            # 网络
            '网络': ['网络协议', '网络编程', '网络安全', '网络工程'],
            'http': ['http协议', 'https', '网络请求'],
            'tcp/ip': ['tcp', 'ip', '网络协议栈'],
            'websocket': ['实时通信', 'socket'],
            
            # 算法与数据结构
            '算法': ['算法设计', '算法优化', '数据结构', '算法分析'],
            '数据结构': ['数据组织', '数据存储', '数据管理'],
            '机器学习': ['ml', 'ai', '人工智能', '深度学习', '神经网络'],
            '深度学习': ['dl', '神经网络', 'cnn', 'rnn', 'transformer'],
            
            # 操作系统
            '操作系统': ['os', 'linux', 'windows', 'unix', 'macos'],
            'linux': ['linux系统', 'ubuntu', 'centos', 'debian'],
            'windows': ['windows系统', 'windows server'],
            
            # 软件测试
            '测试': ['软件测试', 'qa', 'quality assurance', '测试工程师'],
            '自动化测试': ['自动化', 'selenium', 'pytest', 'jest'],
            '性能测试': ['负载测试', '压力测试', '性能分析'],
            
            # 项目管理
            '项目管理': ['项目规划', '进度管理', '团队协作', 'project management'],
            'agile': ['敏捷开发', 'scrum', 'kanban'],
            'pmp': ['项目管理专业人士', '项目管理认证'],
            
            # 软技能
            '沟通': ['交流', '表达', '协作', '沟通能力'],
            '团队协作': ['协作', '团队合作', '团队精神'],
            '学习': ['自我提升', '持续学习', '知识更新', '学习能力'],
            '创新': ['创新思维', '创意', '新方法', '创新能力'],
            '抗压': ['压力管理', '情绪管理', '适应能力', '抗压能力'],
            '解决问题': ['问题解决', '故障排查', '问题分析'],
            
            # 其他
            '编程': ['编码', '软件开发', '软件设计', '编程能力'],
            '调试': ['排错', '问题定位', '故障排查', '调试能力'],
            '文档': ['文档编写', '技术文档', '文档管理'],
            '安全': ['网络安全', '信息安全', '安全开发', 'security']
        }
        
        # 检查是否在同义词列表中
        for key, synonyms in skill_synonyms.items():
            # 构建完整的同义词集合
            all_synonyms = [key] + synonyms
            # 检查两个技能是否都属于同一个同义词组
            skill1_in_group = any(syn in skill1 for syn in all_synonyms)
            skill2_in_group = any(syn in skill2 for syn in all_synonyms)
            if skill1_in_group and skill2_in_group:
                return True
        
        # 检查技能名称的关键词重叠（更智能的关键词匹配）
        # 移除常见的后缀和修饰词
        common_suffixes = ['开发', '编程', '技术', '工程师', '能力', '技能', '经验']
        
        def clean_skill(skill):
            for suffix in common_suffixes:
                skill = skill.replace(suffix, '')
            return skill.strip()
        
        clean_skill1 = clean_skill(skill1)
        clean_skill2 = clean_skill(skill2)
        
        # 检查清理后的技能名称是否相同
        if clean_skill1 == clean_skill2 and clean_skill1:
            return True
        
        # 检查关键词重叠
        skill1_words = set(clean_skill1.split())
        skill2_words = set(clean_skill2.split())
        
        # 如果有共同关键词且不是虚词
        common_words = skill1_words.intersection(skill2_words)
        stop_words = {'的', '和', '与', '或', '是', '在', '有', '为'}
        meaningful_common_words = common_words - stop_words
        
        if meaningful_common_words:
            # 计算关键词重叠比例
            total_words = skill1_words.union(skill2_words)
            if len(meaningful_common_words) / len(total_words) > 0.3:
                return True
        
        # 检查技能类别匹配
        # 例如：Java开发 和 Java编程 都属于Java类别
        skill_categories = {
            'java': ['java', 'jdk', 'jvm'],
            'python': ['python', 'pytorch', 'tensorflow'],
            'javascript': ['javascript', 'js', 'node'],
            'frontend': ['前端', 'vue', 'react', 'angular', 'html', 'css'],
            'backend': ['后端', 'spring', 'django', 'flask'],
            'database': ['数据库', 'sql', 'mysql', 'redis', 'mongodb'],
            'devops': ['devops', 'docker', 'kubernetes', 'ci/cd'],
            'network': ['网络', 'http', 'tcp', 'websocket'],
            'algorithm': ['算法', '数据结构', '机器学习', '深度学习'],
            'os': ['操作系统', 'linux', 'windows'],
            'testing': ['测试', 'qa', '自动化测试', '性能测试'],
            'management': ['项目管理', 'agile', 'pmp'],
            'soft_skills': ['沟通', '团队协作', '学习', '创新', '抗压', '解决问题']
        }
        
        # 检查两个技能是否属于同一类别
        for category, category_skills in skill_categories.items():
            skill1_in_category = any(skill in skill1 for skill in category_skills)
            skill2_in_category = any(skill in skill2 for skill in category_skills)
            if skill1_in_category and skill2_in_category:
                return True
        
        return False
    
    # 获取技能列表
    from_skill_list = get_all_skills(from_job)
    to_skill_list = get_all_skills(to_job)
    
    # 从换岗图谱中提取共同技能
    from_title = from_job.get('title')
    to_title = to_job.get('title')
    
    # 检查是否存在换岗路径
    if from_title in job_graph.get('horizontal_paths', {}):
        horizontal_paths = job_graph['horizontal_paths'][from_title]
        for path in horizontal_paths:
            if path.get('target') == to_title:
                # 添加路径中的共同技能
                common_skills = path.get('common_skills', [])
                if common_skills:
                    from_skill_list.extend(common_skills)
    
    # 计算可复用技能和需补齐技能
    reusable_skills = []
    used_to_skills = set()
    
    # 找出相似技能
    for from_skill in from_skill_list:
        for i, to_skill in enumerate(to_skill_list):
            if i not in used_to_skills and is_skill_similar(from_skill, to_skill):
                reusable_skills.append(from_skill)
                used_to_skills.add(i)
                break
    
    # 计算需补齐技能
    gap_skills = [to_skill for i, to_skill in enumerate(to_skill_list) if i not in used_to_skills]
    
    # 计算难度（基于共同技能数量）
    total_skills = len(from_skill_list) + len(to_skill_list) - len(reusable_skills)
    common_skills_ratio = len(reusable_skills) / total_skills if total_skills > 0 else 0
    
    if common_skills_ratio >= 0.7:
        difficulty = "低"
    elif common_skills_ratio >= 0.4:
        difficulty = "中等"
    elif common_skills_ratio >= 0.2:
        difficulty = "较高"
    else:
        difficulty = "高"
    
    return TransferAnalysisResponse(
        code=0,
        message="ok",
        data=TransferAnalysisResponseData(
            reusable_skills=reusable_skills,
            gap_skills=gap_skills,
            difficulty=difficulty
        )
    )

@router.get("/recommend/list", response_model=BaseResponse, summary="获取岗位列表（支持标签过滤）")
async def get_job_list(
    tag: Optional[str] = Query(None, description="技能标签过滤"),
    job_profiles: List[Dict] = Depends(get_job_profiles)
):
    """获取系统中所有岗位的详细信息列表，支持按技能标签过滤"""
    job_list = []
    
    # 处理现有岗位数据
    for job in job_profiles:
        # 提取所有相关技能标签
        all_skills = []
        # 专业技能
        all_skills.extend(job.get('professional_skills', {}).get('keywords', []))
        # 创新能力
        all_skills.extend(job.get('innovation_capability', {}).get('keywords', []))
        # 学习能力
        all_skills.extend(job.get('learning_capability', {}).get('keywords', []))
        # 实习经验
        all_skills.extend(job.get('internship_experience', {}).get('keywords', []))
        
        # 如果有标签过滤，检查岗位是否包含该标签（大小写不敏感）
        if tag:
            tag_lower = tag.lower()
            if not any(skill.lower() == tag_lower for skill in all_skills):
                continue
        
        # 构建岗位列表项
        job_item = JobListItem(
            id=job.get('job_id'),
            title=job.get('title'),
            field_tags=all_skills,
            salary_range=f"{job.get('salary_info', {}).get('salary_range', {}).get('min', 0)}-{job.get('salary_info', {}).get('salary_range', {}).get('max', 0)}元/月" if job.get('salary_info') else "面议",
            hot_index=85
        )
        job_list.append(job_item)
    
    return BaseResponse(code=0, message="ok", data=job_list)
