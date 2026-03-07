from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models.student import StudentProfile

app = FastAPI(title="职业规划智能体后端")

# 必须配置 CORS，否则成员 C 的前端无法调用你的接口
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # 比赛期间可设为全匹配
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/student/parse", response_model=StudentProfile)
async def mock_parse_resume():
    """
    第一天任务：提供 Mock 数据接口，方便前端联调
    """
    return {
        "name": "张同学",
        "major": "计算机科学",
        "abilities": {"innovation": 8, "learning": 9, "stress": 7, "communication": 8, "internship": 6},
        "completeness_score": 0.85
    }