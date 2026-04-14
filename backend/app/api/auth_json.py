from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
import pymysql
import jwt
import datetime

# ===================== 配置 =====================
router = APIRouter(prefix="/auth", tags=["认证"])

# 数据库配置
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "hanyu7399",
    "db": "test_login",
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor
}

# JWT 配置
SECRET_KEY = "my-super-secure-key-123456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2

# ===================== 纯 Python 密码加密（不需要 bcrypt） =====================
import hashlib
def hash_password(password: str):
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str):
    return hash_password(plain_password) == hashed_password

# ===================== 数据库工具 =====================
def get_db():
    return pymysql.connect(**DB_CONFIG)

def get_user(username: str):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM user WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()
    return user

# ===================== 数据模型 =====================
class User(BaseModel):
    username: str
    disabled: bool = False

class UserCreate(BaseModel):
    username: str
    password: str

class LoginRequest(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# ===================== 1. 注册 =====================
@router.post("/register", response_model=User)
async def register(user: UserCreate):
    if get_user(user.username):
        raise HTTPException(status_code=400, detail="用户名已存在")

    hashed_password = hash_password(user.password)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO user (username, password) VALUES (%s, %s)",
        (user.username, hashed_password)
    )
    db.commit()
    cursor.close()
    db.close()

    return User(username=user.username, disabled=False)

# ===================== 2. 登录 =====================
@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    user = get_user(login_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")

    if not verify_password(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="密码错误")

    expire = datetime.datetime.utcnow() + datetime.timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    payload = {"sub": user["username"], "exp": expire}
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}

# ===================== 3. 获取用户信息 =====================
@router.get("/me", response_model=User)
async def read_users_me(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="无效凭证")
        
        user = get_user(username)
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")
        
        return User(username=user["username"], disabled=user["disabled"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="登录已过期")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效登录")