from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException

from config import AccountingSubject
from modules.account.schemas import SubjectCreate, SubjectUpdate


# --- Helper ---.
async def get_subject_by_id(db: AsyncSession, account_id: int) -> Optional[AccountingSubject]:
    stmt = select(AccountingSubject).where(AccountingSubject.id == account_id)
    result = await db.execute(stmt)
    return result.scalars().first()


# --- Create ---
async def create_accounting_subject(db: AsyncSession, subject_in: SubjectCreate) -> AccountingSubject:
    # 检查编码
    existing_stmt = select(AccountingSubject).where(AccountingSubject.code == subject_in.code)
    result = await db.execute(existing_stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="科目编码已存在")

    level = 1
    full_name = subject_in.name


    if subject_in.parent_id:
        parent_obj = await get_subject_by_id(db, subject_in.parent_id)
        if not parent_obj:
            raise HTTPException(status_code=404, detail="父科目不存在")
        if not parent_obj.is_active:
            raise HTTPException(status_code=400, detail="不能在未启用的父科目下创建子科目")

        level = parent_obj.level + 1
        parent_prefix = parent_obj.full_name or parent_obj.name
        full_name = f"{parent_prefix} / {subject_in.name}"

    db_subject = AccountingSubject(
        code=subject_in.code,
        name=subject_in.name,
        parent_id=subject_in.parent_id,
        level=level,
        balance_direction=subject_in.balance_direction,
        is_active=subject_in.is_active,
        full_name=full_name
    )

    db.add(db_subject)
    await db.commit()
    await db.refresh(db_subject)
    return db_subject


# --- Read ---
async def get_account(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        parent_id: Optional[int] = None
) -> List[AccountingSubject]:
    stmt = select(AccountingSubject)

    # 【关键优化】预加载 children 关系，防止序列化时触发 N+1 查询
    stmt = stmt.options(selectinload(AccountingSubject.children))

    if parent_id is not None:
        stmt = stmt.where(AccountingSubject.parent_id == parent_id)
    else:
        # 默认只查一级科目
        stmt = stmt.where(AccountingSubject.parent_id == None)

    stmt = stmt.offset(skip).limit(limit)
    # 按 code 排序以保证顺序稳定
    stmt = stmt.order_by(AccountingSubject.code)

    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_accounting_subject(db: AsyncSession, account_id: int) -> AccountingSubject:
    # 【关键修改】链式加载：主节点 -> children -> children (孙子) -> children (曾孙)
    # 根据你的业务需求，加载足够的层级。通常 3 层足够覆盖绝大多数会计科目结构。
    stmt = select(AccountingSubject).options(
        selectinload(AccountingSubject.children)
        .selectinload(AccountingSubject.children)
        .selectinload(AccountingSubject.children)
    ).where(AccountingSubject.id == account_id)

    result = await db.execute(stmt)
    db_subject = result.scalars().first()

    if not db_subject:
        raise HTTPException(status_code=404, detail="科目未找到")

    # 不需要再手动 _ = child.children 了，selectinload 链式调用已经把它们都捞出来了
    return db_subject


# --- Update ---
async def update_accounting_subject(
        db: AsyncSession,
        account_id: int,
        subject_in: SubjectUpdate
) -> AccountingSubject:
    # 1. 获取当前科目
    db_subject = await get_subject_by_id(db, account_id)
    if not db_subject:
        raise HTTPException(status_code=404, detail="科目未找到")

    update_data = subject_in.model_dump(exclude_unset=True)

    # 如果没有需要更新的字段，直接返回
    if not update_data:
        return db_subject

    # 2. 处理 parent_id 变更逻辑
    new_parent_id = update_data.get('parent_id', db_subject.parent_id)

    # 检查是否试图将自己设为父节点 (防止循环引用)
    if new_parent_id == account_id:
        raise HTTPException(status_code=400, detail="不能将科目设置为自身的子科目")

    parent_obj = None
    needs_recalculate_full_name = False

    # 情况 A: parent_id 发生了改变
    if 'parent_id' in update_data and new_parent_id != db_subject.parent_id:
        if new_parent_id is not None:
            parent_obj = await get_subject_by_id(db, new_parent_id)
            if not parent_obj:
                raise HTTPException(status_code=404, detail="新的父科目不存在")
            if not parent_obj.is_active:
                raise HTTPException(status_code=400, detail="不能移动到未启用的父科目下")

            # 更新层级
            db_subject.level = parent_obj.level + 1
            needs_recalculate_full_name = True
        else:
            # 变为一级科目
            db_subject.level = 1
            needs_recalculate_full_name = True

    # 情况 B: parent_id 没变，但 name 变了，或者 parent_id 变了需要拼接新名字
    # 只要 name 变了，或者 parent 变了，都需要重新计算 full_name
    if 'name' in update_data or needs_recalculate_full_name:
        current_name = update_data.get('name', db_subject.name)

        if needs_recalculate_full_name:
            # 如果 parent_obj 已经在上面获取过 (情况 A)，直接使用
            # 如果只是 name 变了但 parent 没变 (情况 B 的子集)，且是子科目，需要重新获取父节点来拼接
            if not needs_recalculate_full_name and db_subject.parent_id:
                # 这里逻辑有点绕，简化一下：
                # 如果进入了这个 if 块，说明要么 parent 变了 (parent_obj 已有)，要么 name 变了。
                pass

            # 重新梳理逻辑：
            # 1. 如果 parent 变了，parent_obj 已经在上面查好了。
            # 2. 如果 parent 没变，但 name 变了，且它是子科目，我们需要查父节点来获取父级的 full_name。
            if db_subject.parent_id and not parent_obj:
                parent_obj = await get_subject_by_id(db, db_subject.parent_id)
                if not parent_obj:
                    # 理论上外键约束不会让这种情况发生，除非数据脏了
                    raise HTTPException(status_code=500, detail="数据不一致：父科目丢失")

            # 计算新的 full_name
            if parent_obj:
                parent_prefix = parent_obj.full_name or parent_obj.name
                db_subject.full_name = f"{parent_prefix} / {current_name}"
            else:
                # 一级科目
                db_subject.full_name = current_name
        else:
            # 仅 name 变化且是一级科目的情况 (parent_id is None)
            if db_subject.parent_id is None:
                db_subject.full_name = update_data['name']

    # 3. 应用其他字段的更新
    for field, value in update_data.items():
        # parent_id 和 name 的特殊逻辑已处理，这里跳过或覆盖均可
        # 如果 name 在 update_data 中，上面已经用了它计算 full_name，这里 setattr 更新 name 字段本身
        setattr(db_subject, field, value)

    # 4. 提交事务
    await db.commit()
    await db.refresh(db_subject)

    # 可选：刷新后重新加载 children，确保返回对象包含最新子节点状态（如果需要）
    # await db.refresh(db_subject, attribute_names=['children'])

    return db_subject


# --- Delete ---
async def delete_accounting_subject(db: AsyncSession, account_id: int):
    db_subject = await get_subject_by_id(db, account_id)
    if not db_subject:
        raise HTTPException(status_code=404, detail="科目未找到")

    # 检查是否有子科目 (利用关系或查询)
    # 由于定义了 cascade="delete-orphan"，直接删除父节点可能会级联删除子节点。
    # 如果你的业务要求“有子节点禁止删除”，则必须先检查。
    count_stmt = select(AccountingSubject.id).where(AccountingSubject.parent_id == account_id)
    result = await db.execute(count_stmt)
    if result.scalars().first():
        raise HTTPException(status_code=400, detail="该科目下存在子科目，无法删除")

    await db.delete(db_subject)
    await db.commit()
    return True