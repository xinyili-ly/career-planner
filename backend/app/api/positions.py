from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
import json
import asyncio

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
    company: str
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

# API端点
@router.get("/recommend/list", response_model=BaseResponse, summary="获取岗位列表")
async def get_job_list(job_profiles: List[Dict] = Depends(get_job_profiles)):
    """获取系统中所有岗位的详细信息列表"""
    job_list = []
    
    # 处理现有岗位数据
    for job in job_profiles:
        # 提取技能标签
        skills = job.get('professional_skills', {}).get('keywords', [])
        # 构建岗位列表项
        job_item = JobListItem(
            id=job.get('job_id'),
            title=job.get('title'),
            field_tags=skills,
            company="示例公司",
            salary_range=f"{job.get('salary_info', {}).get('salary_range', {}).get('min', 0)}-{job.get('salary_info', {}).get('salary_range', {}).get('max', 0)}元/月" if job.get('salary_info') else "面议",
            hot_index=85
        )
        job_list.append(job_item)
    
    # 添加物联网调试师作为样例数据
    if not any(item.title == "物联网调试师" for item in job_list):
        job_item = JobListItem(
            id="JOB_000",
            title="物联网调试师",
            field_tags=["MQTT", "HTTP", "Modbus", "串口调试"],
            company="示例科技公司",
            salary_range="8000-15000元/月",
            hot_index=90
        )
        job_list.append(job_item)
    
    return BaseResponse(code=0, message="ok", data=job_list)

@router.get("/recommend", response_model=RecommendResponse, summary="获取岗位画像基础信息")
async def get_job_profile(
    title: Optional[str] = Query(None, description="岗位名称"),
    job_profiles: List[Dict] = Depends(get_job_profiles)
):
    """根据岗位名称获取详细的岗位画像信息"""
    if not title:
        raise HTTPException(status_code=400, detail={"code": 4001, "message": "title is required", "data": None})
    
    # 特殊处理物联网调试师样例数据
    if title == "物联网调试师":
        return RecommendResponse(
            code=0,
            message="ok",
            data=RecommendResponseData(
                name="物联网调试师",
                summary="面向物联网设备与系统的联调联试，覆盖硬件接入、协议解析、网络连通、数据上云与现场定位。",
                profileDims=[
                    ProfileDim(name="专业技能", desc="掌握串口/网口抓包、MQTT/HTTP/Modbus 等协议。"),
                    ProfileDim(name="证书要求", desc="HCIA/HCIP（可选）等。"),
                    ProfileDim(name="创新能力", desc="可沉淀标准化联调SOP并持续优化。"),
                    ProfileDim(name="学习能力", desc="快速掌握新协议和设备调试方法。"),
                    ProfileDim(name="抗压能力", desc="能适应现场调试的高强度工作。"),
                    ProfileDim(name="沟通能力", desc="能与硬件、软件、产品等多团队有效协作。"),
                    ProfileDim(name="实习能力", desc="有物联网相关实习经验优先。")
                ],
                relations=[
                    Relation(role="嵌入式软件开发工程师", reason="共享设备驱动/协议栈能力。"),
                    Relation(role="物联网平台开发工程师", reason="共享平台接入和数据处理能力。")
                ]
            )
        )
    
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
                salary_info=None
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
            other_requirements=other_requirements
        )
    )
