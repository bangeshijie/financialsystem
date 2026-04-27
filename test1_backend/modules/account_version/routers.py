# routers.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from db.session import get_db
from modules.account_version.crud import AccountVersionCRUD
from modules.account_version import schemas
from utils.auth import get_current_user
from utils.response import success_response, error_response

# 创建路由器
router = APIRouter(prefix="/account_version", tags=["版本管理"])


# ============ 科目版本管理接口 ============
@router.post("/add", response_model=schemas.AccountVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
        version_in: schemas.AccountVersionCreate,
        db: AsyncSession = Depends(get_db)
):
    """创建科目版本"""
    await AccountVersionCRUD.create(db, version_in)
    return success_response(  message="创建科目版本成功")


@router.get("/list", response_model=schemas.AccountVersionListResponse)
async def get_versions(
        skip: int = Query(0, ge=0, description="跳过的记录数"),
        limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
        is_active: Optional[bool] = Query(None, description="是否启用"),
        search: Optional[str] = Query(None, description="搜索关键词"),
        db: AsyncSession = Depends(get_db)
):
    """获取科目版本列表（分页）"""
    items, total = await AccountVersionCRUD.get_multi(db, skip, limit, is_active, search)
    data =  schemas.AccountVersionListResponse(total=total, items=items)
    return success_response(data = data, message="列表获取成功")





@router.get("/info/{account_version_id}", response_model=schemas.AccountVersionResponse)
async def get_version(
        account_version_id: int,
        db: AsyncSession = Depends(get_db)
):
    """获取单个科目版本详情"""
    version = await AccountVersionCRUD.get(db, account_version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    return version


@router.put("/update/{account_version_id}", response_model=schemas.AccountVersionResponse)
async def update_version(
        account_version_id: int,
        version_in: schemas.AccountVersionUpdate,
        db: AsyncSession = Depends(get_db)
):
    """更新科目版本"""
    version = await AccountVersionCRUD.get(db, account_version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )
    return await AccountVersionCRUD.update(db, version, version_in)


@router.delete("/delete/{account_version_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_version(
        account_version_id: int,
        db: AsyncSession = Depends(get_db)
):
    """删除科目版本"""
    await AccountVersionCRUD.delete(db, account_version_id)
    return None


@router.post("/set-default/{account_version_id}", response_model=schemas.AccountVersionResponse)
async def set_default_version(
        account_version_id: int,
        db: AsyncSession = Depends(get_db)
):
    """设置默认版本"""
    return await AccountVersionCRUD.set_default(db, account_version_id)




