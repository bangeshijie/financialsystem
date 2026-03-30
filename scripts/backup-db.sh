#!/bin/bash
BACKUP_DIR="./backups"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

mkdir -p $BACKUP_DIR

echo "💾 备份数据库到: $BACKUP_FILE"

if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

docker exec myapp-mysql mysqldump \
    --single-transaction \
    -u root \
    -p${MYSQL_ROOT_PASSWORD} \
    --all-databases > $BACKUP_FILE 2>/dev/null

if [ $? -eq 0 ]; then
    gzip $BACKUP_FILE
    echo "✅ 备份完成: ${BACKUP_FILE}.gz"
    find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete
else
    echo "❌ 备份失败"
    exit 1
fi
