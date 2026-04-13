# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from modules.users.routers import router  as users
from modules.company.routers import router  as company

from utils.exception_handlers import register_exception_handlers
from contextlib import asynccontextmanager
from db.session import AsyncSessionLocal, async_engine
from db.init_db import  seed_default_users, seed_default_roles
from fastapi.staticfiles import StaticFiles
import logging



logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("⏳ 应用正在启动...")
    async with AsyncSessionLocal() as session:
        try:
            await seed_default_roles()
            await seed_default_users()
            logger.info("✅ 数据库初始化完成！")
        except Exception as e:
            logger.error(f"🛑 数据库初始化失败: {e}")
            raise  # 添加这一行，让启动过程失败，避免运行一个不可用的服务
    yield
    await async_engine.dispose()

# 初始化 App

app = FastAPI(
    title="tests_App",
    lifespan=lifespan,
    description="XX后端 API 文档",
    version="1.0.0",
    # 【关键】显式注册安全方案，这样 Swagger 一定会显示 Authorize 按钮
    openapi_extra={
        "components": {
            "securitySchemes": {
                "BearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT"
                }
            }
        }
    }
)



# 注册异常处理器
register_exception_handlers(app)

# origins=[
#     "http://localhost",
#     "",
#     "",
# ]

#   测试环境 再开启
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],            # 允许的源 上线时需修改为实际线上地址
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )



# ✅ 生产环境指定具体域名
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://www.chyichyi.com",
        "https://chyichyi.com",
        "http://localhost:5173",  # 本地开发
        "http://localhost:80",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.mount("/static", StaticFiles(directory="static"), name="static")
@app.get("/")
async def read_root():
    return {"status": "running"}

app.include_router(users)
app.include_router(company)


