# crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select
from typing import Optional, List
from fastapi import HTTPException, status

from modules.account.models import  Account
from modules.account import schemas
from modules.account_version.crud import AccountVersionCRUD


# ============ Account CRUD ============
class AccountCRUD:
    """会计科目CRUD操作"""

    @staticmethod
    async def get(db: AsyncSession, subject_id: int) -> Optional[Account]:
        """根据ID获取科目"""
        return await db.get(Account, subject_id)

    @staticmethod
    async def get_by_code(db: AsyncSession, code: str, account_version_id: Optional[int] = None) -> Optional[Account]:
        """根据编码和版本获取科目"""
        query = select(Account).where(Account.code == code)
        if account_version_id:
            query = query.where(Account.account_version_id == account_version_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_multi(
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            account_version_id: Optional[int] = None,
            parent_id: Optional[int] = None,  # 改为 parent_id
            level: Optional[int] = None,
            is_active: Optional[bool] = None,
            is_leaf: Optional[bool] = None,
            search: Optional[str] = None
    ) -> tuple[List[Account], int]:
        """获取多个科目（分页）"""
        query = select(Account)

        if account_version_id:
            query = query.where(Account.account_version_id == account_version_id)

        if parent_id is not None:
            if parent_id == 0:  # 0 表示根节点
                query = query.where(Account.parent_id.is_(None))
            else:
                query = query.where(Account.parent_id == parent_id)

        if level:
            query = query.where(Account.level == level)

        if is_active is not None:
            query = query.where(Account.is_active == is_active)

        if is_leaf is not None:
            query = query.where(Account.is_leaf == is_leaf)

        if search:
            query = query.where(
                or_(
                    Account.code.contains(search),
                    Account.name.contains(search),
                    Account.display_name.contains(search),
                    Account.full_name.contains(search)
                )
            )

        # 获取总数
        count_query = select(Account).select_from(Account)
        if account_version_id:
            count_query = count_query.where(Account.account_version_id == account_version_id)
        if parent_id is not None:
            if parent_id == 0:
                count_query = count_query.where(Account.parent_id.is_(None))
            else:
                count_query = count_query.where(Account.parent_id == parent_id)
        if level:
            count_query = count_query.where(Account.level == level)
        if is_active is not None:
            count_query = count_query.where(Account.is_active == is_active)
        if is_leaf is not None:
            count_query = count_query.where(Account.is_leaf == is_leaf)
        if search:
            count_query = count_query.where(
                or_(
                    Account.code.contains(search),
                    Account.name.contains(search),
                    Account.display_name.contains(search),
                    Account.full_name.contains(search)
                )
            )
        result = await db.execute(count_query)
        total = len(result.scalars().all())

        # 分页查询
        query = query.order_by(Account.code).offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()

        return items, total

    @staticmethod
    async def get_tree(db: AsyncSession, account_version_id: int):
        """获取科目树形结构"""
        return await Account.get_full_tree(db, account_version_id)

    @staticmethod
    async def create(db: AsyncSession, obj_in: schemas.AccountCreate) -> Account:
        """创建科目"""
        try:
            subject = await Account.create_in_db(
                db=db,
                code=obj_in.code,
                name=obj_in.name,
                account_version_id=obj_in.account_version_id,
                parent_id=obj_in.parent_id,
                display_name=obj_in.display_name,
                balance_direction=obj_in.balance_direction,
                is_active=obj_in.is_active
            )
            await db.commit()
            await db.refresh(subject)
            return subject
        except ValueError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    async def update(
            db: AsyncSession,
            db_obj: Account,
            obj_in: schemas.AccountUpdate
    ) -> Account:
        """更新科目"""
        update_data = obj_in.model_dump(exclude_unset=True)

        if 'account_version_id' in update_data:
            version = await AccountVersionCRUD.get(db, update_data['account_version_id'])
            if not version:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="指定的科目版本不存在"
                )

        if 'code' in update_data:
            existing = await AccountCRUD.get_by_code(
                db, update_data['code'],
                update_data.get('account_version_id', db_obj.account_version_id)
            )
            if existing and existing.id != db_obj.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"科目编码 {update_data['code']} 在指定版本中已存在"
                )

        if 'parent_id' in update_data:
            if update_data['parent_id']:
                parent = await db.get(Account, update_data['parent_id'])
                if not parent:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"父科目ID {update_data['parent_id']} 不存在"
                    )
                update_data['level'] = parent.level + 1
                new_name = update_data.get('name', db_obj.name)
                update_data['full_name'] = f"{parent.full_name}/{new_name}"
            else:
                update_data['level'] = 1
                update_data['full_name'] = update_data.get('name', db_obj.name)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    @staticmethod
    async def delete(db: AsyncSession, subject_id: int) -> bool:
        """删除科目"""
        subject = await db.get(Account, subject_id)
        if not subject:
            raise HTTPException(status_code=404, detail="科目不存在")

        try:
            await subject.delete_with_children(db)
            await db.commit()
            return True
        except ValueError as e:
            await db.rollback()
            raise HTTPException(status_code=400, detail=str(e))