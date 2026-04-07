
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession,async_sessionmaker


import os
from dotenv import load_dotenv

load_dotenv()

# 数据库配置
# ASYNC_DATABASE_URL = "mysql+aiomysql://root:123456@localhost:3306/news_app?charset=utf8mb4"
ASYNC_DATABASE_URL = f"mysql+aiomysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DB')}?charset=utf8mb4"

# 创建引擎
async_engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=True,             #正式环境 关闭 减少日志输出，提升性能
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
)

# 需求:查询功能的接口,依赖注入:创建数据库会话+Depends 注入路由处理函数
AsyncSessionLocal = async_sessionmaker(
   bind=async_engine,  #绑定数据引擎
    class_=AsyncSession,   #指定会话类
    expire_on_commit=False,   #提交后会话不过期,不会重新查询数据库
)
# 依赖项 用于获取数据库会话
async def get_db():
    async with  AsyncSessionLocal() as session:      #包括自动关闭会话
        try:
            yield session       #返回数据库会话给路由处理函数
            await session.commit()  #提交事务
        except Exception:
            await session.rollback()         #有异常,回滚
            raise