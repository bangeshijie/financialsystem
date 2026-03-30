from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from modules.company.crud import get_company_by_id, get_company_options, get_companies, add_company, change_company, \
    delete_company
from modules.users.models import User
from modules.company.schemas import (
    CompanyCreateRequest,
    CompanyUpdateRequest,
    CompanyBaseResponse,
    CompanyDetailResponse,
    CompanyListResponse, CompanyOption
)
from db.session import get_db
from utils.response import success_response
from utils.auth import get_current_user

router = APIRouter(prefix="/company", tags=["company"])

@router.post("/add", response_model=CompanyBaseResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建公司。
    返回：仅公司基础信息 (无创建人名字，无用户对象)。
    """
    new_company = await add_company(db, company_data, created_by=current_user.user_id)
    return success_response(message="公司创建成功", data=new_company)

@router.get("/info/{company_id}", response_model=CompanyDetailResponse)
async def get_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取公司详情。
    返回：公司详细信息 + creator_name (username) + updater_name (username)。
    """
    company = await get_company_by_id(db, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="公司不存在")
    return success_response(message="获取成功", data=company)

@router.get("/list", response_model=CompanyListResponse)
async def list_companies(
    page: int = Query(1, ge=1, description="当前页码，从1开始"),
    limit: int = Query(10, ge=1, le=100),
    keyword: str = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    获取公司列表。
    返回：列表项包含 creator_name 和 updater_name。
    """
    skip = (page - 1) * limit


    result = await get_companies(db, skip=skip, limit=limit, keyword=keyword)
    return success_response(message="获取列表成功", data=result)

@router.put("/update/{company_id}", response_model=CompanyBaseResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    更新公司。
    返回：仅公司基础信息 (无更新人名字，无用户对象)。
    """
    updated_company = await change_company(db, company_id, company_data, updated_by=current_user.user_id)
    return success_response(message="更新成功", data=updated_company)

@router.delete("/delete/{company_id}")
async def remove_company(
    company_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    success = await delete_company( db,company_id)
    if not success:
        raise HTTPException(status_code=404, detail="删除失败")
    return success_response(message="删除成功")


@router.get("/options", response_model=List[CompanyOption], summary="获取公司下拉选项")
async def list_company_options(

    keyword: str = Query(None, description="搜索关键字，用于模糊匹配公司名"),
    limit: int = Query(100, ge=1, le=500, description="最大返回数量，默认100，最大500"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    专门用于前端下拉选择框的接口。
    返回精简数据 (id, name)，不包含创建人、更新时间等冗余信息。
    支持模糊搜索，适合数据量大的场景配合前端远程搜索使用。
    """
    options = await get_company_options(

        keyword=keyword if keyword else None,
        limit=limit,
        db=db


    )

    return success_response(message="获取成功", data=options)