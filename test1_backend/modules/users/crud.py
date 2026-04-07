import uuid
import random
import time
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any

from fastapi import HTTPException


from utils import security
from utils.snowflake import SnowflakeIdGenerator

from sqlalchemy import select, func, update, delete
from sqlalchemy.orm import selectinload  # 关键：用于预加载关联数据
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from modules.users.models import User, UserToken, UserRole,Menu, RoleMenu, Role
from modules.users.schemas import UserRequest, UserUpdateRequest

from utils.upload_image import AvatarUpload, DEFAULT_AVATAR_FILENAME
#
#
# 根据用户名查询数据库
async def get_user_by_username(db: AsyncSession, username: str):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar_one_or_none()

# 创建用户
async def create_user(db: AsyncSession, user_data: UserRequest):
    # 先密码加密处理 → add
    hashed_password = security.get_hash_password(user_data.password)
    # 雪花算法生成 用户id
    snowflake_gen = SnowflakeIdGenerator(worker_id=1, datacenter_id=1)
    try:
        new_user_id = snowflake_gen.next_id()
    except Exception as e:
        # 如果发生时钟回拨等异常， fallback 到一个随机大整数或重试
        print(f"雪花算法生成失败: {e}, 尝试使用备用方案")

        new_user_id = int(time.time() * 1000) + random.randint(1000, 9999)

    user = User(username=user_data.username, password=hashed_password, user_id=new_user_id)




    db.add(user)
    await db.commit()
    await db.refresh(user)  # 从数据库读回最新的 user
    return user
#
#
# 生成 Token
async def create_token(db: AsyncSession, user_id: int):
    # 生成 Token + 设置过期时间 → 查询数据库当前用户是否有 Token → 有：更新；没有：添加
    token = str(uuid.uuid4())
    # timedelta(days=7, hours=2, minutes=30, seconds=10)
    expires_at = datetime.now() + timedelta(days=7)
    query = select(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    user_token = result.scalar_one_or_none()

    if user_token:
        user_token.token = token
        user_token.expires_at = expires_at
    else:
        user_token = UserToken(user_id=user_id, token=token, expires_at=expires_at)
        db.add(user_token)
        await db.commit()

    return token
#
#
async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not security.verify_password(password, user.password):
        return None

    return user
#
#
# 根据 Token 查询用户：验证 Token → 查询用户
async def get_user_by_token(db: AsyncSession, token: str):
    query = select(UserToken).where(UserToken.token == token)
    result = await db.execute(query)
    db_token = result.scalar_one_or_none()

    if not db_token or db_token.expires_at < datetime.now():
        return None

    query = select(User).where(User.user_id == db_token.user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()
#
#
# # 更新用户信息: update更新 → 检查是否命中 → 获取更新后的用户返回
async def update_user(db: AsyncSession, username: str, user_data: UserUpdateRequest):
    # update(User).where(User.username == username).values(字段=值, 字段=值)
    # user_data 是一个Pydantic类型，得到字典 → ** 解包
    # 没有设置值的不更新
    query = update(User).where(User.username == username).values(**user_data.model_dump(
        exclude_unset=True,
        exclude_none=True
    ))
    result = await db.execute(query)
    await db.commit()
#
    # 检查更新
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 获取一下更新后的用户
    updated_user = await get_user_by_username(db, username)
    return updated_user


# 修改密码: 验证旧密码 → 新密码加密 → 修改密码
async def change_password(db: AsyncSession, user: User, old_password: str, new_password: str):
    if not security.verify_password(old_password, user.password):
        return False

    hashed_new_pwd = security.get_hash_password(new_password)
    user.password = hashed_new_pwd
    # 更新: 由SQLAlchemy真正接管这个 User 对象，确保可以 commit
    # 规避 session 过期或关闭导致的不能提交的问题
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return True


# --- 新增：删除 Token (实现登出) ---
async def revoke_token(db: AsyncSession, user_id: int):
    """
    根据 user_id 删除对应的 Token 记录
    """
    query = delete(UserToken).where(UserToken.user_id == user_id)
    result = await db.execute(query)
    await db.commit()

    # 返回受影响的行数，如果为 0 说明本来就没有 Token
    return result.rowcount

# ---------------------用户详细信息含路由\按钮\角色列表的方法----------------------------
async def get_user_permissions(db: AsyncSession, user: User) -> Dict[str, Any]:
    """
    获取用户的完整权限信息（角色列表、路由列表、按钮列表）

    Args:
        db: 数据库会话
        user: 用户对象

    Returns:
        {
            "roles": ["角色名称1", "角色名称2"],
            "routes": ["路由code1", "路由code2"],
            "buttons": ["按钮code1", "按钮code2"]
        }
    """
    from sqlalchemy import distinct

    # 1. 获取用户的所有角色
    user_roles_query = (
        select(UserRole)
        .where(UserRole.user_id == user.user_id)
        .options(selectinload(UserRole.role))
    )
    user_roles_result = await db.execute(user_roles_query)
    user_roles = list(user_roles_result.scalars().all())

    # 提取角色名称列表
    roles = []
    role_ids = []
    for user_role in user_roles:
        if user_role.role:
            roles.append(user_role.role.role_name)
            role_ids.append(user_role.role.role_id)

    # 2. 如果没有角色，返回空权限
    if not role_ids:
        return {
            "roles": [],
            "routes": [],
            "buttons": []
        }

    # 3. 查询所有角色关联的菜单（去重）
    role_menus_query = (
        select(RoleMenu.menu_id)
        .where(RoleMenu.role_id.in_(role_ids))
        .distinct()
    )
    role_menus_result = await db.execute(role_menus_query)
    menu_ids = list(role_menus_result.scalars().all())

    # 4. 如果没有菜单，返回只有角色的权限
    if not menu_ids:
        return {
            "roles": roles,
            "routes": [],
            "buttons": []
        }

    # 5. 查询菜单详情
    menus_query = (
        select(Menu)
        .where(
            Menu.menu_id.in_(menu_ids),
            Menu.status == 'active'
        )
        .order_by(Menu.level, Menu.menu_id)
    )
    menus_result = await db.execute(menus_query)
    menus = list(menus_result.scalars().all())

    # 6. 分离路由和按钮
    routes = []
    buttons = []

    for menu in menus:
        if menu.type == 1:  # 菜单类型为路由
            routes.append(menu.code)
        elif menu.type == 2:  # 按钮类型
            buttons.append(menu.code)

    return {
        "roles": roles,
        "routes": routes,
        "buttons": buttons
    }


async def get_user_with_permissions(db: AsyncSession, user_id: int) -> Optional[Dict[str, Any]]:
    """
    获取用户及其完整权限信息

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        包含用户信息和权限的字典
    """
    from sqlalchemy.orm import selectinload, joinedload

    # 1. 先查询用户基本信息（不加载复杂关联，避免N+1查询）
    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None

    # 2. 单独查询用户的角色
    user_roles_query = (
        select(UserRole)
        .where(UserRole.user_id == user.user_id)
        .options(selectinload(UserRole.role))
    )
    user_roles_result = await db.execute(user_roles_query)
    user_roles = list(user_roles_result.scalars().all())

    # 3. 提取角色ID和角色名称
    roles = []
    role_ids = []
    for user_role in user_roles:
        if user_role.role:
            roles.append(user_role.role.role_name)
            role_ids.append(user_role.role.role_id)

    # 4. 如果没有角色，直接返回
    if not role_ids:
        user_info = {
            "id": user.id,
            "user_id": user.user_id,
            "username": user.username,
            "nickname": user.nickname,
            "avatar": f"/static/uploads/avatars/{user.avatar}",
            "gender": user.gender,
            "bio": user.bio,
            "email": user.email,
            "created_time": user.created_time,
            "updated_time": user.updated_time,
            "roles": [],
            "routes": [],
            "buttons": []
        }
        return user_info

    # 5. 查询角色关联的菜单
    from sqlalchemy import distinct

    # 先查询角色菜单关联表
    role_menus_query = (
        select(RoleMenu)
        .where(RoleMenu.role_id.in_(role_ids))
        .options(selectinload(RoleMenu.menu))
    )
    role_menus_result = await db.execute(role_menus_query)
    role_menus = list(role_menus_result.scalars().all())

    # 6. 收集菜单ID并去重
    menu_ids = set()
    for role_menu in role_menus:
        if role_menu.menu_id:
            menu_ids.add(role_menu.menu_id)

    # 7. 查询菜单详情
    routes = []
    buttons = []

    if menu_ids:
        menus_query = (
            select(Menu)
            .where(
                Menu.menu_id.in_(menu_ids),
                Menu.status == 'active'  # 只获取启用的菜单
            )
            .order_by(Menu.level, Menu.menu_id)
        )
        menus_result = await db.execute(menus_query)
        menus = list(menus_result.scalars().all())

        # 8. 分离路由和按钮
        for menu in menus:
            if menu.type == 1:  # 菜单类型为路由
                routes.append(menu.code)
            elif menu.type == 2:  # 按钮类型
                buttons.append(menu.code)

    # 9. 组装用户信息
    user_info = {
        "id": user.id,
        "user_id": user.user_id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": f"/static/uploads/avatars/{user.avatar}",
        "gender": user.gender,
        "bio": user.bio,
        "email": user.email,
        "created_time": user.created_time,
        "updated_time": user.updated_time,
        "roles": roles,
        "routes": routes,
        "buttons": buttons
    }

    return user_info





async def get_all_users_with_roles(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        username: Optional[str] = None  # 新增参数
):
    """
    获取所有用户及其角色信息
    支持按用户名搜索
    """
    # 构建基础查询
    query = select(User).options(
        selectinload(User.roles).joinedload(UserRole.role)
    )

    # 如果提供了用户名，添加搜索条件
    if username:
        # 使用 ilike 进行不区分大小写的模糊搜索
        # 如果需要精确搜索，可以使用 ==
        query = query.filter(User.username.ilike(f"%{username}%"))

    # 获取总数（带搜索条件）
    count_query = select(func.count()).select_from(User)
    if username:
        count_query = count_query.filter(User.username.ilike(f"%{username}%"))
    total = await db.scalar(count_query)

    # 执行分页查询
    result = await db.execute(
        query.offset(skip).limit(limit)
    )
    users = result.scalars().unique().all()

    return users, total


async def admin_reset_password(db: AsyncSession, target_username: str, new_password: str):
    """
    管理员强制重置用户密码
    :param db: 数据库会话
    :param target_username: 目标用户名
    :param new_password: 新密码（明文，将在函数内加密）
    :return: 更新后的用户对象
    """
    # 1. 检查用户是否存在
    user = await get_user_by_username(db, target_username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 2. 加密新密码
    hashed_password = security.get_hash_password(new_password)

    # 3. 执行更新操作
    query = update(User).where(User.username == target_username).values(password=hashed_password)
    result = await db.execute(query)

    if result.rowcount == 0:
        # 理论上不会发生，因为前面已经检查过用户存在
        raise HTTPException(status_code=500, detail="密码更新失败")

    await db.commit()
    await db.refresh(user)

    return user


async def cleanup_user_resources(user: User) -> None:
    """
    清理用户相关的静态资源文件
    包括：头像、上传的附件等
    """
    # 1. 清理用户头像
    if user.avatar and user.avatar != DEFAULT_AVATAR_FILENAME:
        await AvatarUpload.delete_old_avatar(user.avatar)

    # 2. 【扩展点】清理用户的其他资源
    # 例如：用户上传的认证图片、合同文件等
    # await cleanup_user_documents(user.user_id)
    # await cleanup_user_certificates(user.user_id)

    # 3. 【可选】清理用户专属目录（如果有）
    # user_folder = f"static/uploads/users/{user.user_id}"
    # if os.path.exists(user_folder):
    #     import shutil
    #     shutil.rmtree(user_folder)


async def delete_user(db: AsyncSession, target_username: str):
    """
    管理员删除指定用户
    :param db: 数据库会话
    :param target_username: 目标用户名
    :return: 被删除的用户对象（用于返回信息）
    """
    # 1. 检查用户是否存在
    user = await get_user_by_username(db, target_username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在，无法删除")

        # 2. 【新增】清理用户的静态资源文件
    await cleanup_user_resources(user)

    # 3. 执行删除操作（会级联删除 UserRole、UserToken 等关联数据）
    await db.delete(user)
    await db.commit()

    return user


async def delete_target_users(db: AsyncSession, target_usernames: List[str]) -> List[dict]:
    """
    管理员批量删除指定用户
    :param db: 数据库会话
    :param target_usernames: 目标用户名列表
    :return: 被删除的用户信息列表
    """
    if not target_usernames:
        return []

    deleted_users_info = []

    # 1. 预检查：确保所有用户都存在，避免删了一半发现后面有人不存在导致逻辑复杂化
    # 也可以选择在循环中逐个处理，但预检查能更快反馈错误
    users_to_delete = []
    for username in target_usernames:
        user = await get_user_by_username(db, username)
        if not user:
            # 发现任何一个用户不存在，抛出异常，触发事务回滚
            raise HTTPException(status_code=404, detail=f"用户 '{username}' 不存在，无法执行批量删除")
        users_to_delete.append(user)

        # 2. 【新增】批量清理用户的静态资源文件
    for user in users_to_delete:
        await cleanup_user_resources(user)


    # 3. 执行删除操作
    for user in users_to_delete:
        await db.delete(user)
        # 复制必要信息，因为 commit 后对象会变成 detached 状态，某些字段可能无法访问
        deleted_users_info.append({
            "username": user.username,
            "id": getattr(user, 'user_id', None),  # 根据实际模型调整
            # "email": user.email # 根据需要返回其他字段
        })

    # 3. 提交事务
    await db.commit()

    return deleted_users_info

async def get_user_rolelist(db: AsyncSession, username: str):
    """
    获取指定用户的已分配角色列表 以及 系统所有角色列表

    返回数据结构:
    {

        "username": ...,
        "assign_roles": [ ... ], # 用户当前拥有的角色
        "all_roles": [ ... ]     # 系统内所有可用的角色
    }
    """

    # --- 第一步：查询用户及其已分配的角色 (高性能预加载) ---
    query_user = (
        select(User)
        .where(User.username == username)
        .options(
            selectinload(User.roles).joinedload(UserRole.role)
        )
    )

    result_user = await db.execute(query_user)
    user = result_user.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 解析已分配角色
    assign_roles_list = []
    for user_role_rel in user.roles:
        role_obj = user_role_rel.role
        if role_obj:
            assign_roles_list.append({
                "role_id": role_obj.role_id,
                "role_name": role_obj.role_name,
                "remark": role_obj.remark
            })

    # --- 第二步：查询系统所有角色 ---
    # 只需要 role_id 和 role_name，按需索取
    query_all_roles = select(Role).order_by(Role.role_id)  # 可选：按ID排序
    result_all = await db.execute(query_all_roles)
    all_role_objects = result_all.scalars().all()

    # 解析所有角色
    all_roles_list = []
    for role_obj in all_role_objects:
        all_roles_list.append({
            "role_id": role_obj.role_id,
            "role_name": role_obj.role_name,
            "remark": role_obj.remark
        })

    # --- 第三步：组装返回结果 ---
    return {

        "username": user.username,
        "assign_roles": assign_roles_list,
        "all_roles": all_roles_list
    }






async def set_user_roles(
        db: AsyncSession,
        username: str,
        role_ids: List[int]
):
    """
    设置用户的角色（覆盖式更新：先删除所有现有角色，再添加新角色）   适合少量的数据!!!!
    :param db: 数据库会话
    :param username: 用户名
    :param role_ids: 要设置的角色ID列表
    :return: 更新后的用户角色信息
    """
    # 1. 检查用户是否存在
    user = await get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 2. 验证要设置的角色ID是否都存在
    if role_ids:
        role_check_query = select(Role.role_id).where(Role.role_id.in_(role_ids))
        role_check_result = await db.execute(role_check_query)
        valid_role_ids = set(role_check_result.scalars().all())

        invalid_role_ids = set(role_ids) - valid_role_ids
        if invalid_role_ids:
            raise HTTPException(
                status_code=400,
                detail=f"角色ID不存在: {sorted(invalid_role_ids)}"
            )
    else:
        valid_role_ids = set()

    # 3. 删除用户所有现有角色
    delete_query = delete(UserRole).where(UserRole.user_id == user.user_id)
    await db.execute(delete_query)

    # 4. 添加新角色
    for role_id in valid_role_ids:
        user_role = UserRole(
            user_id=user.user_id,
            role_id=role_id
        )
        db.add(user_role)

    await db.commit()

    # 5. 获取更新后的用户角色信息
    updated_user_data = await get_user_rolelist(db, username)

    return {
        "username": user.username,
        "set_roles": list(valid_role_ids),
        "current_roles": updated_user_data["assign_roles"],
        "message": f"成功设置 {len(valid_role_ids)} 个角色"
    }



# -------------------------------------角色模块部分操作---------------------------
async def get_rolelist(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        role_name: Optional[str] = None
) -> Tuple[List[Role], int]:
    """
    获取角色列表
    """
    stmt = select(Role)

    if role_name:
        stmt = stmt.filter(Role.role_name.ilike(f"%{role_name}%"))

    # 获取总数
    count_stmt = select(func.count(Role.role_id))
    if role_name:
        count_stmt = count_stmt.filter(Role.role_name.ilike(f"%{role_name}%"))

    total_result = await db.scalar(count_stmt)
    total = total_result if total_result is not None else 0

    # 执行查询
    stmt = stmt.offset(skip).limit(limit)
    result = await db.execute(stmt)

    # 【关键修改】显式转换为 list[Role]
    # result.scalars() 返回的是 ScalarResult[Role]
    # .all() 返回 Sequence[Role]，我们用 list() 包裹它变成 List[Role]
    roles: List[Role] = list(result.scalars().all())

    return roles, total


async def create_role(db: AsyncSession, role_in: "RoleCreate") -> Role:
    """
    新增角色
    """
    db_role = Role(
        role_name=role_in.role_name,
        remark=role_in.remark
    )
    db.add(db_role)
    try:
        await db.commit()
        # await db.refresh(db_role),    refresh 可能会触发关联表的懒加载，导致在 commit 后的会话中出现意外行为或额外查询。
    except IntegrityError:
        await db.rollback()
        # 这里可以抛出自定义异常，或者在 router 层处理
        raise ValueError("角色名称已存在")
    return db_role


async def update_role(db: AsyncSession, role_id: int, role_in: "RoleUpdate") -> Optional[Role]:
    """
    修改角色
    """
    # 先查询是否存在
    stmt = select(Role).where(Role.role_id == role_id)
    result = await db.execute(stmt)
    db_role = result.scalar_one_or_none()

    if not db_role:
        return None

    # 更新字段 (只更新传入的字段)
    update_data = role_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_role, field, value)

    try:
        await db.commit()
        await db.refresh(db_role)
    except IntegrityError:
        await db.rollback()
        raise ValueError("更新失败：角色名称可能已存在")

    return db_role


async def delete_role(db: AsyncSession, role_id: int) -> bool:
    """
    删除单个角色
    返回 True 表示删除成功，False 表示未找到
    """
    stmt = select(Role).where(Role.role_id == role_id)
    result = await db.execute(stmt)
    db_role = result.scalar_one_or_none()

    if not db_role:
        return False

    # 可选：增加保护逻辑，例如不允许删除超级管理员
    if db_role.role_id == 1:  # 假设 1 是超级管理员
        raise ValueError("超级管理员不可删除")

    await db.delete(db_role)
    await db.commit()
    return True


# ==================== 菜单部分基础 CRUD 操作 ====================

async def get_menu_by_id(db: AsyncSession, menu_id: int) -> Optional[Menu]:
    """根据 ID 获取菜单"""
    query = select(Menu).where(Menu.menu_id == menu_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_all_menus(db: AsyncSession, status: str = None) -> List[Menu]:
    """
    获取所有菜单
    """
    query = select(Menu)
    if status:
        query = query.where(Menu.status == status)
    query = query.order_by(Menu.level, Menu.menu_id)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_active_menus(db: AsyncSession) -> List[Menu]:
    """
    获取所有启用的菜单
    """

    query = select(Menu).where(
        Menu.status == 'active'
    ).order_by(Menu.level, Menu.menu_id)

    result = await db.execute(query)
    return list(result.scalars().all())


async def create_menu(db: AsyncSession, menu_data: Dict[str, Any]) -> Menu:
    """
    创建菜单
    """
    db_menu = Menu(**menu_data)
    db.add(db_menu)
    await db.commit()
    await db.refresh(db_menu)
    return db_menu


async def update_menu(db: AsyncSession, menu_id: int, update_data: Dict[str, Any]) -> Optional[Menu]:
    """
    更新菜单
    """
    db_menu = await get_menu_by_id(db, menu_id)
    if not db_menu:
        return None

    for key, value in update_data.items():
        if hasattr(db_menu, key):
            setattr(db_menu, key, value)

    await db.commit()
    await db.refresh(db_menu)
    return db_menu


async def delete_menu(db: AsyncSession, menu_id: int) -> bool:
    """
    删除菜单（逻辑删除，将状态设为 inactive）
    """
    db_menu = await get_menu_by_id(db, menu_id)
    if not db_menu:
        return False

    db_menu.status = 'inactive'
    await db.commit()
    return True


async def hard_delete_menu(db: AsyncSession, menu_id: int) -> bool:
    """
    物理删除菜单
    """
    db_menu = await get_menu_by_id(db, menu_id)
    if not db_menu:
        return False

    await db.delete(db_menu)
    await db.commit()
    return True


# ==================== 树形结构相关操作 ====================

def build_menu_tree(menus: List[Menu]) -> List[Dict[str, Any]]:
    """
    将平铺的菜单列表转换为树形结构
    （这个是纯函数，不需要 db，所以保持同步即可）
    """
    # 1. 将菜单列表转换为字典，key 为 menu_id
    menu_dict = {menu.menu_id: {
        'menu_id': menu.menu_id,  # 改为 menu_id 以保持一致性
        'name': menu.name,
        'label': menu.name,  # 同时保留 label 供前端使用
        'pid': menu.pid,
        'code': menu.code,
        'to_code': menu.to_code,
        'type': menu.type,
        'status': menu.status,
        'level': menu.level,
        'selected': menu.selected,
        'children': []
    } for menu in menus}

    # 2. 构建树形结构
    tree = []
    for menu_id, menu_item in menu_dict.items():
        if menu_item['pid'] == 0:  # 根节点
            tree.append(menu_item)
        else:
            # 找到父节点，将当前节点添加到父节点的 children 中
            parent = menu_dict.get(menu_item['pid'])
            if parent:
                parent['children'].append(menu_item)

    return tree


def build_menu_tree_recursive(menus: List[Menu], pid: int = 0) -> List[Dict[str, Any]]:
    """
    递归方式构建菜单树
    """
    tree = []
    for menu in menus:
        if menu.pid == pid:
            children = build_menu_tree_recursive(menus, pid=menu.menu_id)
            tree.append({
                'menu_id': menu.menu_id,
                'name': menu.name,
                'label': menu.name,
                'pid': menu.pid,
                'code': menu.code,
                'to_code': menu.to_code,
                'type': menu.type,
                'status': menu.status,
                'level': menu.level,
                'selected': menu.selected,
                'children': children
            })
    return tree


async def get_menu_tree(db: AsyncSession, status: str = 'active') -> List[Dict[str, Any]]:
    """
    获取菜单树形结构
    """
    if status == 'active':
        menus = await get_active_menus(db)
    else:
        menus = await get_all_menus(db, status)
    return build_menu_tree(menus)


# ==================== 角色菜单相关操作 ====================

async def get_role_menu_ids(db: AsyncSession, role_id: int) -> List[int]:
    """
    获取角色关联的菜单ID列表
    """
    query = select(RoleMenu.menu_id).where(RoleMenu.role_id == role_id)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_role_menus(db: AsyncSession, role_id: int) -> List[Menu]:
    """
    获取角色关联的所有菜单
    """
    menu_ids = await get_role_menu_ids(db, role_id)
    if not menu_ids:
        return []

    query = select(Menu).where(
        Menu.menu_id.in_(menu_ids),
        Menu.status == 'active'
    ).order_by(Menu.level, Menu.menu_id)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_role_menu_tree(db: AsyncSession, role_id: int) -> List[Dict[str, Any]]:
    """
    获取角色的菜单树形结构
    """
    menus = await get_role_menus(db, role_id)
    return build_menu_tree(menus)


async def get_role_menus_with_selected(
        db: AsyncSession,
        role_id: int
) -> List[Dict[str, Any]]:
    """
    获取所有菜单，并标记当前角色已选中的菜单
    注意：只有叶子节点（按钮或最底层菜单）才标记 selected=True
    父节点的选中状态由前端树形控件自动处理
    """
    # 1. 获取所有菜单
    all_menus_query = select(Menu).order_by(Menu.level, Menu.menu_id)
    all_menus_result = await db.execute(all_menus_query)
    all_menus = list(all_menus_result.scalars().all())

    # 2. 获取角色已分配的菜单ID（只有实际勾选的权限）
    assigned_menu_ids_query = select(RoleMenu.menu_id).where(RoleMenu.role_id == role_id)
    assigned_result = await db.execute(assigned_menu_ids_query)
    assigned_menu_ids = set(assigned_result.scalars().all())

    print(f"角色 {role_id} 实际拥有的菜单ID: {assigned_menu_ids}")

    # 3. 构建菜单字典
    menu_dict = {}
    for menu in all_menus:
        # 判断是否为叶子节点（没有子节点的节点）
        is_leaf = True  # 这里需要根据你的数据结构判断

        menu_dict[menu.menu_id] = {
            'menu_id': menu.menu_id,
            'pid': menu.pid,
            'name': menu.name,
            'label': menu.name,
            'code': menu.code,
            'to_code': menu.to_code,
            'type': menu.type,
            'status': menu.status,
            'level': menu.level,
            # 关键修改：只有叶子节点才标记 selected，父节点不标记
            'selected': is_leaf and menu.menu_id in assigned_menu_ids,
            'children': []
        }

    # 4. 先找出所有父子关系，完善 is_leaf 判断
    # 收集所有父节点ID
    parent_ids = set()
    for menu in all_menus:
        if menu.pid != 0:
            parent_ids.add(menu.pid)

    # 重新设置 selected，只有非父节点且被分配的才标记
    for menu_id, menu_item in menu_dict.items():
        if menu_id not in parent_ids:  # 如果不是任何节点的父节点（即是叶子节点）
            menu_item['selected'] = menu_id in assigned_menu_ids
        else:
            menu_item['selected'] = False  # 父节点不标记选中

    # 5. 构建树形结构
    tree = []
    for menu_id, menu_item in menu_dict.items():
        if menu_item['pid'] == 0:
            tree.append(menu_item)
        else:
            parent = menu_dict.get(menu_item['pid'])
            if parent:
                parent['children'].append(menu_item)

    # 6. 检查被标记为 selected 的节点
    selected_nodes = []

    def collect_selected(node_list):
        for node in node_list:
            if node['selected']:
                selected_nodes.append({
                    'menu_id': node['menu_id'],
                    'name': node['name'],
                    'level': node['level']
                })
            if node['children']:
                collect_selected(node['children'])

    collect_selected(tree)
    print(f"最终被标记为选中的节点: {selected_nodes}")

    return tree


async def assign_menus_to_role(
        db: AsyncSession,
        role_id: int,
        menu_ids: List[int]
) -> bool:
    """
    为角色分配菜单权限（先删除所有原有权限，再添加新权限）
    """
    try:
        # 1. 先删除该角色原有的所有菜单关联
        delete_query = delete(RoleMenu).where(RoleMenu.role_id == role_id)
        await db.execute(delete_query)

        # 2. 批量插入新的菜单关联
        if menu_ids:  # 只有当有菜单ID时才添加
            for menu_id in menu_ids:
                role_menu = RoleMenu(role_id=role_id, menu_id=menu_id)
                db.add(role_menu)

        await db.flush()
        return True
    except Exception as e:
        await db.rollback()
        print(f"分配菜单权限失败: {e}")
        return False


async def update_user_avatar_by_user_id(
        db: AsyncSession,
        user_id: int,
        avatar_filename: str
) -> tuple[Optional[User], Optional[str]]:
    """
    根据用户ID更新用户头像
    Returns:
        (更新后的用户对象, 旧头像文件名)
    """
    # 1. 获取用户和旧头像
    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None, None

    old_avatar = user.avatar

    # 2. 更新头像（不使用 RETURNING）
    stmt = (
        update(User)
        .where(User.user_id == user_id)
        .values(avatar=avatar_filename)
    )

    await db.execute(stmt)
    await db.commit()

    # 3. 重新查询获取更新后的用户
    updated_query = select(User).where(User.user_id == user_id)
    updated_result = await db.execute(updated_query)
    updated_user = updated_result.scalar_one_or_none()

    return updated_user, old_avatar


async def clear_user_avatar_by_user_id(
        db: AsyncSession,
        user_id: int
) -> tuple[Optional[User], Optional[str]]:
    """
    清空用户头像
    Returns:
        (更新后的用户对象, 旧头像文件名)
    """
    # 1. 获取用户和旧头像
    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        return None, None

    old_avatar = user.avatar

    # 2. 清空头像字段（不使用 RETURNING）
    stmt = (
        update(User)
        .where(User.user_id == user_id)
        .values(avatar="")
    )

    await db.execute(stmt)
    await db.commit()

    # 3. 重新查询获取更新后的用户
    updated_query = select(User).where(User.user_id == user_id)
    updated_result = await db.execute(updated_query)
    updated_user = updated_result.scalar_one_or_none()

    return updated_user, old_avatar

async def get_user_by_user_id(
        db: AsyncSession,
        user_id: int
) -> Optional[User]:
    """
    根据用户ID获取用户信息
    Args:
        db: 数据库会话
        user_id: 用户ID
    Returns:
        用户对象或None
    """
    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()
