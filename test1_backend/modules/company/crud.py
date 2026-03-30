import random
import time

import logging
from typing import Optional, List

from fastapi import HTTPException
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from config import Company
from modules.users.models import User # 仅在 CRUD 中引入，用于 Join
from modules.company.schemas import CompanyCreateRequest, CompanyUpdateRequest, CompanyOption
from utils.snowflake import SnowflakeIdGenerator


# 配置日志
logger = logging.getLogger(__name__)
snowflake_gen = SnowflakeIdGenerator(worker_id=1, datacenter_id=1)


def _get_detail_query_with_users():
    """
    构建带用户信息的查询语句。
    使用 left join 获取创建人和更新人的 User 对象。
    返回结构：(Company 实例, Creator User 实例, Updater User 实例)
    """
    creator_user = aliased(User, name='creator_user')    # type: ignore[assignment]
    updater_user = aliased(User, name='updater_user')    # type: ignore[assignment]

    stmt = (select(Company, creator_user, updater_user)
            .outerjoin(creator_user, Company.created_by == creator_user.user_id)   # type: ignore[arg-type]
            .outerjoin(updater_user, Company.updated_by == updater_user.user_id))   # type: ignore[arg-type]
    return stmt


async def get_company_by_id(db: AsyncSession, company_id: int):
    stmt = _get_detail_query_with_users().where(Company.id == company_id)
    result = await db.execute(stmt)
    row = result.first()

    if not row:
        return None

    company_obj, creator_obj, updater_obj = row

    # ✅【关键修改】：只挂载用户名字符串，属性名对应 Schema 中的 creator_name
    # 这样根本不会把 User 对象传给 Pydantic，彻底杜绝密码泄露
    company_obj.creator_name = creator_obj.username if creator_obj else None
    company_obj.updater_name = updater_obj.username if updater_obj else None

    # 可选：如果你担心旧代码依赖 creator 属性，也可以赋值，但赋值为 None 或简单字典
    # company_obj.creator = None
    # company_obj.updater = None

    return company_obj



async def get_company_by_code(db: AsyncSession, code: str):
    # 简单查询，不需要用户信息
    stmt = select(Company).where(Company.company_code == code)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def add_company(db: AsyncSession, company_data: CompanyCreateRequest, created_by: int):
    existing = await get_company_by_code(db, company_data.company_code)
    if existing:
        raise HTTPException(status_code=400, detail="公司编码已存在")



    try:
        # 尝试生成雪花 ID
        new_company_id = snowflake_gen.next_id()
    except (RuntimeError, ValueError, AttributeError) as e:
        # 捕获常见的运行时错误（如时钟回拨、未初始化等）
        logger.warning(f"雪花算法生成 ID 失败 ({type(e).__name__}): {e}. 正在启用降级策略...")
        # 降级策略：时间戳毫秒 + 随机数
        new_company_id = int(time.time() * 1000) + random.randint(1000, 9999)
        logger.info(f"已生成降级 ID: {new_company_id}")
    except Exception as e:
        # 捕获其他未知异常，防止程序崩溃，但必须记录堆栈
        logger.error(f"雪花算法发生未知错误: {e}", exc_info=True)
        new_company_id = int(time.time() * 1000) + random.randint(1000, 9999)



    company = Company(
        company_id=new_company_id,
        name=company_data.name,
        company_code=company_data.company_code,
        address=company_data.address,
        contact_person=company_data.contact_person,
        contact_phone=company_data.contact_phone,
        contact_email=company_data.contact_email,
        industry=company_data.industry,
        scale=company_data.scale,
        description=company_data.description,
        status=1,
        created_by=created_by,
        updated_by=created_by
    )

    db.add(company)
    await db.commit()
    await db.refresh(company)

    return company


async def change_company(db: AsyncSession, company_id: int, company_data: CompanyUpdateRequest, updated_by: int):
    # 1. 检查存在性 (简单查询)
    stmt = select(Company).where(Company.id == company_id)
    result = await db.execute(stmt)
    existing_company = result.scalar_one_or_none()

    if not existing_company:
        raise HTTPException(status_code=404, detail="公司不存在")

    # 2. 准备更新数据
    update_data = company_data.model_dump(exclude_unset=True, exclude_none=True)
    if not update_data:
        return existing_company

    update_data['updated_by'] = updated_by

    # 3. 执行更新
    stmt = update(Company).where(Company.id == company_id).values(**update_data)
    result = await db.execute(stmt)
    await db.commit()

    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="更新失败")

    # 4. 返回更新后的对象 (简单查询，不带用户信息)
    stmt = select(Company).where(Company.id == company_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def delete_company(db: AsyncSession, company_id: int):
    stmt = delete(Company).where(Company.id == company_id)
    result = await db.execute(stmt)
    await db.commit()
    return result.rowcount > 0


async def get_companies(db: AsyncSession, skip: int = 0, limit: int = 10, keyword: str = None):
    # 1. 计数
    count_stmt = select(func.count(Company.id))
    if keyword:
        count_stmt = count_stmt.where(Company.name.contains(keyword))
    total_result = await db.execute(count_stmt)
    total = total_result.scalar() or 0

    # 2. 查询数据
    stmt = _get_detail_query_with_users()
    if keyword:
        stmt = stmt.where(Company.name.contains(keyword))

    stmt = stmt.order_by(Company.created_time.desc()).offset(skip).limit(limit)

    result = await db.execute(stmt)
    rows = result.all()

    items = []
    for row in rows:
        company_obj, creator_obj, updater_obj = row

        # ✅【关键修改】：直接挂载字符串到 creator_name 和 updater_name
        company_obj.creator_name = creator_obj.username if creator_obj else None
        company_obj.updater_name = updater_obj.username if updater_obj else None

        # 确保没有残留整个对象（防御性编程）
        if hasattr(company_obj, 'creator'):
            delattr(company_obj, 'creator')
        if hasattr(company_obj, 'updater'):
            delattr(company_obj, 'updater')

        items.append(company_obj)

    return {"total": total, "items": items}


async def get_company_options(
        db: AsyncSession,
        keyword: Optional[str] = None,
        limit: int = 100
) -> List[CompanyOption]:
    """
    获取用于下拉框的公司列表。
    特点：
    1. 只查询 company_code 和 name，性能极高。
    2. 默认只查询启用状态 (is_active=True)，根据你实际模型调整。
    3. 支持关键字模糊搜索。
    4. 强制限制最大返回数量，防止前端卡顿。
    """

    # 1. 构建基础查询：只选需要的列
    stmt = select(Company.company_code, Company.name)

    # 2. 添加过滤条件 (例如：只显示启用的公司)
    # 假设你的模型有个 is_active 字段，如果没有可以去掉这行
    if hasattr(Company, 'is_active'):
        stmt = stmt.where(Company.is_active == True)

    # 3. 关键字搜索
    if keyword:
        stmt = stmt.where(Company.name.contains(keyword))

    # 4. 排序：通常按名称字母顺序或 ID 倒序
    stmt = stmt.order_by(Company.name.asc())

    # 5. 【关键】安全限流：即使没有分页，也要限制最大返回条数
    # 如果数据量极大，前端下拉框渲染超过 200 条就会卡顿
    stmt = stmt.limit(limit)

    result = await db.execute(stmt)
    rows = result.all()

    # 6. 转换为 Pydantic 模型列表
    # row 是元组 (company_code, name)，我们需要映射到 CompanyOption
    options = []
    for row in rows:
        options.append(CompanyOption(company_code=row.company_code, name=row.name))

    return options