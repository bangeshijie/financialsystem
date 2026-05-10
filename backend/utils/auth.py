
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from modules.users.crud import get_user_by_token

# ==========================================
# 1. 定义全局安全方案 (关键！)
# ==========================================
# 这个对象将在 main.py 和 这里 被共同引用
security_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="请输入您的访问 Token",
    auto_error=False  # 设为 False，允许我们在函数内部自定义错误提示（如中文提示）
)


# ==========================================
# 2. 修改 get_current_user 依赖函数
# ==========================================
async def get_current_user(
        db: AsyncSession = Depends(get_db),
        # 【核心修改】使用 Security 替代 Header
        # FastAPI 会自动解析 "Authorization: Bearer <token>"
        # 并将 token 部分填入 credentials.credentials
        credentials: HTTPAuthorizationCredentials = Security(security_scheme)
):
    token = credentials.credentials

    # 调用 CRUD 查询用户
    user = await get_user_by_token(db, token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌或已经过期的令牌",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user



















