#!/bin/bash
# 生产环境部署脚本

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}🚀 开始部署 myapp...${NC}"

# 检查是否在项目目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ 请在项目根目录运行此脚本 (/opt/myapp)${NC}"
    exit 1
fi

# 检查环境变量文件
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 文件不存在，创建示例...${NC}"
    cp .env.example .env 2>/dev/null || echo "# 请创建 .env 文件" > .env
    echo -e "${RED}请编辑 .env 文件配置密码后再运行${NC}"
    exit 1
fi

# 加载环境变量
export $(cat .env | grep -v '^#' | xargs)

# 备份数据库
if [ -f "scripts/backup-db.sh" ]; then
    echo -e "${GREEN}💾 备份数据库...${NC}"
    ./scripts/backup-db.sh
fi

# 停止旧容器
echo -e "${GREEN}🛑 停止旧容器...${NC}"
docker-compose down

# 重新构建镜像
echo -e "${GREEN}🔨 重新构建镜像...${NC}"
docker-compose build --no-cache

# 启动新容器
echo -e "${GREEN}🚀 启动新容器...${NC}"
docker-compose up -d

# 等待服务启动
echo -e "${GREEN}⏳ 等待服务启动...${NC}"
sleep 10

# 检查服务状态
echo -e "${GREEN}🔍 检查服务状态...${NC}"
docker-compose ps

# 清理旧镜像
echo -e "${GREEN}🧹 清理旧镜像...${NC}"
docker image prune -f

echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "前端访问: http://chyichyi.com"
echo -e "API文档: http://chyichyi.com/docs"
