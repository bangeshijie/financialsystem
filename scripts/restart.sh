#!/bin/bash
echo "🔄 重启服务..."
docker-compose restart
sleep 5
docker-compose ps
echo "✅ 服务已重启"
