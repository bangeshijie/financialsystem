import os
import sys
from dotenv import load_dotenv
from logging.config import fileConfig

from sqlalchemy import engine_from_config,pool
from alembic import context
from config.base import Base


# 导入你的项目根目录

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
# --- 1. 加载 .env 文件 ---
# 这一步确保 os.getenv 能读取到你 .env 文件里的内容
load_dotenv()

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


# --- 2. 定义获取数据库连接 URL 的函数 ---
def get_database_url():
    # 读取 .env 中的变量，如果找不到变量则使用默认值（防止报错）
    host = os.getenv("MYSQL_HOST", "localhost")
    port = os.getenv("MYSQL_PORT", "3306")
    user = os.getenv("MYSQL_USER", "root")
    password = os.getenv("MYSQL_PASSWORD", "")
    db = os.getenv("MYSQL_DB", "")

    # 拼接成 SQLAlchemy 格式的连接字符串
    # 格式: mysql+pymysql://用户:密码@主机:端口/数据库名
    return f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}?charset=utf8mb4"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    # --- 3. 使用我们自定义的 URL ---
    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    # --- 3. 修改配置，注入自定义 URL ---
    # 获取配置字典
    configuration = config.get_section(config.config_ini_section, {})
    # 将 sqlalchemy.url 替换为从 .env 读取的值
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()