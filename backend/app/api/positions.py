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
async def get_job_profiles() -> List[Dict]:
    """加载岗位画像数据"""
    try:
        with open('../data/jobs.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        # 如果找不到文件，返回空列表
        return []

async def get_job_graph() -> Dict:
    """加载岗位图谱数据"""
    try:
        with open('../../job_graph.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        # 如果找不到文件，返回空字典
        return {"vertical_paths": {}, "horizontal_paths": {}}

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
            salary_info=job.get('salary_info')
        )
    )
