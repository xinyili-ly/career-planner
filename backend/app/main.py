from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import positions

# 创建FastAPI应用实例
app = FastAPI(
    title="岗位画像与图谱API",
    description="提供岗位画像查询、晋升路径和换岗路径等功能",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有域名访问，生产环境应设置为具体的前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 添加版本信息中间件
@app.middleware("http")
async def add_version_header(request, call_next):
    response = await call_next(request)
    response.headers["X-API-Version"] = "1"
    return response

# 注册路由
app.include_router(positions.router)

# 根路径
@app.get("/", summary="API信息")
async def root():
    """获取API服务信息"""
    return {
        "message": "岗位画像与图谱API服务",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

# 健康检查端点
@app.get("/health", summary="健康检查")
async def health_check():
    """检查API服务是否正常运行"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    print("FastAPI服务器启动中...")
    print("可用接口:")
    print("GET /api/positions/list - 获取岗位列表")
    print("GET /api/positions/recommend?title=岗位名称 - 获取岗位画像")
    print("GET /api/positions/path?title=岗位名称 - 获取垂直晋升路径")
    print("GET /api/positions/transfer?title=岗位名称 - 获取横向换岗路径")
    print("GET /api/positions/detail/{id} - 获取岗位完整详情")
    print("GET /docs - 交互式API文档")
    print("GET /redoc - 另一种API文档格式")
    print("服务器运行在 http://localhost:8000")
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
