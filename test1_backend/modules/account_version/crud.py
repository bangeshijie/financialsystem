# crud.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_, select,func
from typing import Optional, List
from fastapi import HTTPException, status

from modules.account.models import Account
from modules.account_version.models import AccountVersion
from modules.account_version import schemas


# ============ AccountVersion CRUD ============
class AccountVersionCRUD:
    """科目版本CRUD操作"""

    @staticmethod
    async def get(db: AsyncSession, account_version_id: int) -> Optional[AccountVersion]:
        """根据ID获取单个版本"""
        return await db.get(AccountVersion, account_version_id)

    @staticmethod
    async def get_by_code(db: AsyncSession, version_code: str) -> Optional[AccountVersion]:
        """根据编码获取版本"""
        result = await db.execute(
            select(AccountVersion).where(AccountVersion.version_code == version_code)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_default_version(db: AsyncSession) -> Optional[AccountVersion]:
        """获取默认版本"""
        result = await db.execute(
            select(AccountVersion).where(AccountVersion.is_default == True)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def get_multi(
            db: AsyncSession,
            skip: int = 0,
            limit: int = 100,
            is_active: Optional[bool] = None,
            search: Optional[str] = None
    ) -> tuple[List[AccountVersion], int]:
        """获取多个版本（分页）"""
        query = select(AccountVersion)

        if is_active is not None:
            query = query.where(AccountVersion.is_active == is_active)

        if search:
            query = query.where(
                or_(
                    AccountVersion.version_code.contains(search),
                    AccountVersion.version_name.contains(search),
                    AccountVersion.description.contains(search)
                )
            )


        # 获取总数
        count_query = select(func.count()).select_from(query.subquery())
        result = await db.execute(count_query)
        total = result.scalar()

        # 分页查询
        query = query.order_by(AccountVersion.id.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()

        return items, total

    @staticmethod
    async def create(db: AsyncSession, obj_in: schemas.AccountVersionCreate) -> AccountVersion:
        """创建新版本"""
        existing = await AccountVersionCRUD.get_by_code(db, obj_in.version_code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"版本编码 {obj_in.version_code} 已存在"
            )

        if obj_in.is_default:
            await db.execute(
                select(AccountVersion).where(AccountVersion.is_default == True)
            )
            await db.execute(
                AccountVersion.__table__.update().where(AccountVersion.is_default == True).values(is_default=False)
            )

        db_obj = AccountVersion(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    @staticmethod
    async def update(
            db: AsyncSession,
            db_obj: AccountVersion,
            obj_in: schemas.AccountVersionUpdate
    ) -> AccountVersion:
        """更新版本"""
        update_data = obj_in.model_dump(exclude_unset=True)

        if 'version_code' in update_data:
            existing = await AccountVersionCRUD.get_by_code(db, update_data['version_code'])
            if existing and existing.id != db_obj.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"版本编码 {update_data['version_code']} 已存在"
                )

        if update_data.get('is_default', False):
            await db.execute(
                select(AccountVersion).where(
                    AccountVersion.is_default == True,
                    AccountVersion.id != db_obj.id
                )
            )
            await db.execute(
                AccountVersion.__table__.update()
                .where(AccountVersion.is_default == True, AccountVersion.id != db_obj.id)
                .values(is_default=False)
            )

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

    @staticmethod
    async def delete(db: AsyncSession, account_version_id: int) -> bool:
        """删除版本"""
        db_obj = await AccountVersionCRUD.get(db, account_version_id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="版本不存在"
            )

        result = await db.execute(
            select(Account).where(Account.account_version_id == account_version_id)
        )
        subject_count = len(result.scalars().all())

        if subject_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"该版本下有 {subject_count} 个科目在使用，无法删除。请先删除或迁移相关科目"
            )

        if db_obj.is_default:
            result = await db.execute(select(AccountVersion).where(AccountVersion.id != account_version_id))
            other_versions = result.scalars().all()
            if len(other_versions) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="不能删除唯一的默认版本，请先创建其他版本"
                )

        await db.delete(db_obj)
        await db.commit()

        return True

    @staticmethod
    async def set_default(db: AsyncSession, account_version_id: int) -> AccountVersion:
        """设置默认版本"""
        await db.execute(
            AccountVersion.__table__.update().where(AccountVersion.is_default == True).values(is_default=False)
        )

        db_obj = await AccountVersionCRUD.get(db, account_version_id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="版本不存在"
            )

        db_obj.is_default = True
        await db.commit()
        await db.refresh(db_obj)

        return db_obj

