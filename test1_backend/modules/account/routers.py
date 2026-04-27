# routers.py
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List

from db.session import get_db
from modules.account.crud import  AccountCRUD
from modules.account_version.crud import AccountVersionCRUD
from modules.account import schemas
from utils.auth import get_current_user
from utils.response import success_response, error_response

# 创建路由器
router = APIRouter(prefix="/account", tags=["会计科目管理"])



# ============ 会计科目管理接口 ============
@router.post("/add", response_model=schemas.AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
        subject_in: schemas.AccountCreate,
        db: AsyncSession = Depends(get_db)
):
    """创建会计科目"""
    data= await AccountCRUD.create(db, subject_in)
    return success_response(
                message="增加科目成功",
                data=data
            )



@router.get("/list", response_model=schemas.AccountListResponse)
async def get_subjects(
        skip: int = Query(0, ge=0, description="跳过的记录数"),
        limit: int = Query(100, ge=1, le=1000, description="返回的记录数"),
        account_version_id: Optional[int] = Query(None, description="科目版本ID"),
        parent_id: Optional[int] = Query(None, description="父科目ID"),  # 改为 parent_id
        level: Optional[int] = Query(None, ge=1, description="科目级次"),
        is_active: Optional[bool] = Query(None, description="是否启用"),
        is_leaf: Optional[bool] = Query(None, description="是否叶子节点"),
        search: Optional[str] = Query(None, description="搜索关键词"),
        db: AsyncSession = Depends(get_db)
):
    """获取会计科目列表（分页）"""


    items, total = await AccountCRUD.get_multi(
        db, skip, limit, account_version_id, parent_id, level, is_active, is_leaf, search
    )
    data= schemas.AccountListResponse(total=total, items=items)
    return success_response(
        message="获取会计科目列表成功",
        data=data
    )


@router.get("/tree", response_model=List[schemas.AccountResponse])
async def get_subject_tree(
        account_version_id: int = Query(..., description="科目版本ID"),
        db: AsyncSession = Depends(get_db)
):
    """获取会计科目树形结构"""
    data= await AccountCRUD.get_tree(db, account_version_id)

    return success_response(
                message="获取科目层级树成功",
                data=data
            )


@router.get("/info/{subject_id}", response_model=schemas.AccountResponse)
async def get_subject(
        subject_id: int,
        db: AsyncSession = Depends(get_db)
):
    """获取单个会计科目详情"""
    subject = await AccountCRUD.get(db, subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="科目不存在"
        )

    return success_response(
        message="增加科目成功",
        data=subject
    )


@router.put("/update/{subject_id}", response_model=schemas.AccountResponse)
async def update_subject(
        subject_id: int,
        subject_in: schemas.AccountUpdate,
        db: AsyncSession = Depends(get_db)
):
    """更新会计科目"""
    subject = await AccountCRUD.get(db, subject_id)
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="科目不存在"
        )
    data= await AccountCRUD.update(db, subject, subject_in)
    return success_response(
        message="修改科目成功",
        data=data
    )


@router.delete("/delete/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
        subject_id: int,
        db: AsyncSession = Depends(get_db)
):
    """删除会计科目"""
    await AccountCRUD.delete(db, subject_id)
    return  success_response(
        message = "删除科目成功"
    )


# ============ 批量操作接口 ============
@router.post("/add/batch", response_model=List[schemas.AccountResponse])
async def batch_create_subjects(
        subjects_in: List[schemas.AccountCreate],
        db: AsyncSession = Depends(get_db)
):
    """批量创建（优化版：单次事务）"""
    # ✅ 添加日志
    print(f"接收到 {len(subjects_in)} 条数据")
    for i, subject in enumerate(subjects_in):
        print(
            f"第 {i + 1} 条: code={subject.code}, name={subject.name}, account_version_id={subject.account_version_id}")

    created_subjects = []
    try:
        for subject_in in subjects_in:
            subject = await AccountCRUD.create(db, subject_in)
            created_subjects.append(subject)
        await db.commit()
        data = created_subjects
        return success_response(data=data, message=f"成功创建 {len(subjects_in)} 条数据")

    except Exception as e:
        await db.rollback()
        print(f"批量创建失败: {e}")  # ✅ 打印错误
        raise e


@router.get("/export/{account_version_id}")
async def export_subjects(
        account_version_id: int,
        db: AsyncSession = Depends(get_db)
):
    """导出指定版本的科目数据"""
    version = await AccountVersionCRUD.get(db, account_version_id)
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="版本不存在"
        )

    subjects, total = await AccountCRUD.get_multi(db, account_version_id=account_version_id, limit=10000)

    data= {
        "account_version": version,
        "total": total,
        "subjects": subjects
    }
    return success_response(
        message="获取科目数据成功",
        data=data
    )
