# 使用 Node 24 Alpine 版本（体积小）
FROM node:24-alpine AS builder

# 启用 corepack 并使用 pnpm
RUN corepack enable && corepack prepare pnpm@latest --activate

# 设置工作目录
WORKDIR /app

# 复制 package.json 和 lock 文件
COPY package.json pnpm-lock.yaml ./

# 限制 pnpm 安装时的并发和内存!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# --no-optional 跳过可选依赖，减少内存占用
RUN pnpm install --frozen-lockfile --no-optional

# 复制源代码
COPY . .

# 关键：限制 Node.js 内存为 512MB
ENV NODE_OPTIONS="--max-old-space-size=512"

# 限制线程池大小，降低并发
ENV UV_THREADPOOL_SIZE=2

# 构建项目（限制并发）
RUN pnpm run build

# 生产阶段
FROM nginx:alpine 

# 拷贝 ssl 证书
COPY ssl /etc/nginx/ssl

# 复制构建产物到 nginx
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 nginx 配置（如果有）
COPY nginx.conf /etc/nginx/conf.d/default.conf

# 暴露端口
EXPOSE 80

# 启动 nginx
CMD ["nginx", "-g", "daemon off;"]