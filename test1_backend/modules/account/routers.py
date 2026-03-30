from fastapi import APIRouter, Depends, status
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from modules.users.models import User
# 引入你的配置和 CRUD
from db.session import get_db  # 确保这里返回的是 AsyncSession
from modules.account.schemas import SubjectCreate, SubjectResponse, SubjectUpdate
from modules.account.crud import  create_accounting_subject,get_account,get_accounting_subject,update_accounting_subject,delete_accounting_subject
from utils.auth import get_current_user
from utils.response import success_response

# 定义 Router
router = APIRouter(prefix="/account", tags=["account"])

@router.post("/caccount/", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject: SubjectCreate,
user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建新的会计科目"""
    result= await create_accounting_subject(db=db, subject_in=subject)
    return success_response(message="添加科目成功", data=result)

@router.get("/raccounts/", response_model=List[SubjectResponse])
async def read_subjects(
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None,
user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取科目列表，默认只返回一级科目，可通过 parent_id 查询子科目"""
    result= await get_account(
        db=db,
        skip=skip,
        limit=limit,
        parent_id=parent_id
    )
    return success_response(message="查询科目列表成功", data=result)


@router.get("/raccount/{account_id}", response_model=SubjectResponse)
async def read_subject(
    account_id: int,
user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取单个科目详情"""
    return await get_accounting_subject(db=db, account_id=account_id)


@router.put("/uaccount/{account_id}", response_model=SubjectResponse)
async def update_subject(
    account_id: int,
    subject: SubjectUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新科目信息"""
    return await update_accounting_subject(
        db=db,
        account_id=account_id,
        subject_in=subject
    )

# 如果需要删除功能，可以取消注释
@router.delete("/daccount/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(account_id: int,
                         user: User = Depends(get_current_user),
                         db: AsyncSession = Depends(get_db)):
    """删除科目信息"""
    result= await delete_accounting_subject(db=db, account_id=account_id)
    return success_response(message="删除科目成功")