# 使用官方 Python 运行时作为父镜像
FROM python:3.14-slim

# 设置工作目录
WORKDIR /code

# 设置环境变量，防止 Python 生成 .pyc 文件，并关闭缓冲以便实时日志
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 安装系统依赖 (如果需要编译某些包，如 psycopg2 等，需在此处安装 build-essential)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt

# 复制项目源代码
COPY . .
# 暴露端口 (FastAPI 默认运行在 8000)
EXPOSE 8000

# 启动命令
# 注意：host=0.0.0.0 是为了让容器外部可以访问
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]