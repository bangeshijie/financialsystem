from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, Body, UploadFile, File, logger

from starlette import status

from config import User
from modules.users import crud
from modules.users.schemas import UserRequest, UserAuthResponse, UserInfoResponse, UserUpdateRequest, \
    UserChangePasswordRequest, UserListResponse, RoleAssignSchema, UserDeleteRequest, PageResponse, RoleListApiResponse, \
    RoleCreate, RoleListItem, RoleUpdate, RoleItem, MenuInfo, MenuUpdate, MenuCreate, UserInfoWithRolesResponse, \
    UserInfoDetail

from modules.users.crud import get_user_by_username, create_user, create_token, authenticate_user, update_user, \
    change_password, \
    revoke_token, get_all_users_with_roles, admin_reset_password, delete_user, get_user_rolelist, set_user_roles, \
    delete_target_users, get_rolelist, get_menu_tree, get_role_menu_tree, get_menu_by_id, update_menu, delete_menu, \
    create_menu, get_user_by_user_id, clear_user_avatar_by_user_id, update_user_avatar_by_user_id

from utils.auth import get_current_user
from utils.response import success_response, error_response
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from utils.upload_image import AvatarUpload

router = APIRouter(prefix="/user", tags=["users"])
import logging

logger = logging.getLogger(__name__)


@router.post("/register")
async def register(user_data:UserRequest, db: AsyncSession = Depends(get_db)):
    """
    暂时不用,内部管理系统由管理员添加,暂不在前端放注册入口!
    """
    # 用户信息 和 db
    # 注册逻辑：验证用户是否存在 -> 创建用户 → 生成 Token  → 响应结果
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await create_user(db, user_data)
    token=await create_token(db, user.user_id)

    # return {
    #   "code": 200,
    #   "message": "注册成功",
    #   "data": {
    #     "token": token,
    #     "userInfo": {
    #       "id": user.id,
    #       "username": user.username,
    #       "bio": user.bio,
    #       "avatar": user.avatar
    #     }
    #   }
    # }
    response_data= UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功",data=response_data,status_code=status.HTTP_201_CREATED)


@router.post("/login")
async def login(user_data:UserRequest, db: AsyncSession = Depends(get_db)):
    # 登录逻辑：验证用户是否存在 -> 验证密码 -> 生成 Token  → 响应结果
    user=await authenticate_user(db, user_data.username, user_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
    token=await create_token(db, user.user_id)
    response_data= UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response(message="登录成功",data=response_data)





@router.get("/info")
async def get_user_info(
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    获取当前用户的详细信息，包括：
    - 基本信息（昵称、头像等）
    - 角色列表 (roles)
    - 路由权限列表 (routes)
    - 按钮权限列表 (buttons)
    """
    try:
        # 获取用户的完整权限信息
        user_with_permissions = await crud.get_user_with_permissions(db, user.user_id)

        if not user_with_permissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        # 使用 UserInfoDetail 模型验证并返回数据
        response_data = UserInfoDetail.model_validate(user_with_permissions)

        return success_response(
            message="获取用户详细信息成功",
            data=response_data
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )






@router.put("/update")
async def update_user_info(user_data: UserUpdateRequest, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):

    user= await update_user(db, user.username, user_data)
    return success_response(message="更新用户信息成功",data=UserInfoResponse.model_validate(user))
# 修改密码:验证Token->验证旧密码->新密码加密->修改密码->响应结果
@router.put("/password")
async def update_password(
        password_data :UserChangePasswordRequest,
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)):
    # 验证旧密码
    res_change_pwd= await change_password(db, user, password_data.old_password, password_data.new_password)
    if not res_change_pwd:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="修改密码失败,请稍后再试")

    return success_response(message="修改密码成功")




@router.post("/logout")
async def logout(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """
    用户登出：
    1. 依赖 get_current_user 确保用户已登录且 Token 有效
    2. 从数据库中删除该用户的 Token
    3. 返回成功响应
    """
    # 执行删除操作
    rows_deleted = await revoke_token(db, user.user_id)

    # 可选：如果没有删除任何记录，可以记录日志或视为成功（因为目标就是让 token 无效）
    if rows_deleted > 0:
        print(f"用户 {user.username} 已登出，Token 已销毁。")
    else:
        print(f"用户 {user.username} 尝试登出，但未找到有效的 Token 记录。")

    return success_response(message="登出成功")


@router.get("/acl/userlist", response_model=UserListResponse)
async def get_user_list(
        page: int = Query(1, ge=1, description="当前页码，从1开始"),
        limit: int = Query(100, ge=1, le=500, description="返回记录数上限"),
        username: Optional[str] = Query(None, description="用户名（支持模糊搜索）"),
        user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    获取用户列表，角色名称以列表格式返回
    """
    skip = (page - 1) * limit
    users, total = await get_all_users_with_roles(
        db, skip=skip, limit=limit, username=username
    )

    items = []
    for user_obj in users:
        # 1. 从 ORM 对象创建基础响应（排除 roles 字段）
        user_dict = {
            "id": user_obj.id,
            "user_id": user_obj.user_id,
            "username": user_obj.username,
            "nickname": user_obj.nickname,
            "avatar": user_obj.avatar,
            "gender": user_obj.gender,
            "bio": user_obj.bio,
            "email": user_obj.email,
            "created_time": user_obj.created_time,
            "updated_time": user_obj.updated_time,
        }

        # 2. 提取角色名称列表
        roles = [ur.role.role_name for ur in user_obj.roles if ur.role]

        # 3. 添加 roles 到字典
        user_dict["roles"] = roles

        # 4. 验证并创建响应对象
        item_schema = UserInfoWithRolesResponse.model_validate(user_dict)
        items.append(item_schema)

    data= UserListResponse(total=total, items=items)
    return success_response(data=data, message="列表获取成功")
@router.post("/acl/adduser")
async def register(user_data:UserRequest,
                   user: User = Depends(get_current_user),
                   db: AsyncSession = Depends(get_db)):
    # 请注意!!!!!!!这里是管理员添加用户!!!!!需要带上认证token!!!!!!!用户信息 和 db
    # 注册逻辑：验证用户是否存在 -> 创建用户 → 生成 Token  → 响应结果
    existing_user = await get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户已存在")
    user = await create_user(db, user_data)
    token=await create_token(db, user.user_id)

    # return {
    #   "code": 200,
    #   "message": "注册成功",
    #   "data": {
    #     "token": token,
    #     "userInfo": {
    #       "id": user.id,
    #       "username": user.username,
    #       "bio": user.bio,
    #       "avatar": user.avatar
    #     }
    #   }
    # }
    response_data= UserAuthResponse(token=token, userInfo=UserInfoResponse.model_validate(user))
    return success_response(message="注册成功",data=response_data,status_code=status.HTTP_201_CREATED)


@router.post("/acl/resetpwd/{username}")
async def reset_user_password(
        username: str,
        current_user: User = Depends(get_current_user),  # 确保操作者是已登录的管理员
        db: AsyncSession = Depends(get_db)
):
    """
    管理员重置指定用户的密码为默认值 (123456)
    前端点击按钮时调用此接口
    """
    DEFAULT_RESET_PWD = "123456"

    # 可选：防止管理员重置自己的密码导致逻辑冲突（视业务需求而定，此处仅做提示）
    if current_user.username == username:
        # 如果允许重置自己，可注释掉下面这行；通常建议走普通修改密码流程
        pass

    try:
        updated_user = await admin_reset_password(db, username, DEFAULT_RESET_PWD)
        return success_response(
            message=f"用户 {username} 密码已成功重置为 {DEFAULT_RESET_PWD}",
            data={
                "username": updated_user.username,
                "reset_success": True
            }
        )
    except HTTPException as e:
        # 透抛 CRUD 层产生的异常（如用户不存在）
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置密码失败: {str(e)}")


@router.delete("/acl/deleteuser/{username}")
async def remove_user(
        username: str,
        current_user: User = Depends(get_current_user),  # 确保操作者是已登录的管理员
        db: AsyncSession = Depends(get_db)
):
    """
    管理员删除指定用户
    前端点击删除按钮时调用此接口
    """

    # 可选：防止管理员删除自己（视业务需求而定）
    if current_user.username == username :
        raise HTTPException(status_code=400, detail="不能删除当前登录的管理员账号")
    # 定义受保护的账户列表
    PROTECTED_ACCOUNTS = ["admin", "root", "system"]
    # 防止删除受保护的账户
    if username in PROTECTED_ACCOUNTS:
        raise HTTPException(status_code=403, detail=f"不能删除系统保护账户: {username}")


    try:
        deleted_user = await delete_user(db, username)
        return success_response(
            message=f"用户 {username} 已成功删除",
            data={
                "deleted_username": deleted_user.username,
                "success": True
            }
        )
    except HTTPException as e:
        # 透抛 CRUD 层产生的异常（如用户不存在）
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除用户失败: {str(e)}")


@router.post("/deleteusers")
# 注意：这里改为了 POST 方法，因为 DELETE 方法通常不建议带 Body (虽然 technically 可以，但很多网关/代理会拦截)
# 如果必须用 DELETE 方法，可以将参数放在 query string: ?usernames=a&usernames=b
async def remove_users(
        payload: UserDeleteRequest,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    管理员删除指定用户（支持单个或批量）
    请求体示例:
    { "usernames": "zhangsan" }  (兼容单个字符串)
    { "usernames": ["zhangsan", "lisi"] } (批量)
    """

    # 1. 解析输入，统一转换为列表
    raw_input = payload.username

    if isinstance(raw_input, str):
        target_usernames = [raw_input]
    else:
        target_usernames = raw_input

    # 2. 安全检查：防止删除当前登录的管理员自己
    # 即使是批量删除，只要列表里包含自己，就拒绝整个操作
    if current_user.username in target_usernames:
        return error_response(
            status_code=400,
            message=f"不能删除当前登录的管理员账号 ({current_user.username})"
        )

    # 3. 安全检查：防止删除 admin 账户
    # 定义受保护的账户列表
    PROTECTED_ACCOUNTS = ["admin", "root", "system"]  # 可根据需要调整

    # 检查是否有受保护的账户在删除列表中
    protected_in_list = [username for username in target_usernames if username in PROTECTED_ACCOUNTS]

    if protected_in_list:
        return error_response(
            status_code=403,
            message=f"不能删除系统保护账户: {', '.join(protected_in_list)}"
        )

    try:
        # 4. 调用批量删除逻辑
        # 注意：delete_users 内部如果有异常（如404），会自动抛出，FastAPI 会捕获并返回
        deleted_list = await delete_target_users(db, target_usernames)

        return success_response(
            message=f"成功删除 {len(deleted_list)} 个用户",
            data={
                "deleted_count": len(deleted_list),
                "deleted_users": deleted_list,
                "success": True
            }
        )
    except HTTPException as e:
        # 透抛业务异常（如用户不存在、禁止删除自己）
        # 由于使用了 async session，如果没有显式 rollback，FastAPI 依赖注入通常在异常时会自动回滚
        # 但为了保险起见，可以在 catch 块中显式回滚（取决于你的 Depends(get_db) 实现）
        return error_response(
            message=e.detail,
            status_code=e.status_code
        )
    except Exception as e:
        # 捕获未知数据库错误
        await db.rollback()  # 显式回滚
        return error_response(
            message=f"批量删除用户失败: {str(e)}",
            status_code=500
        )
@router.get("/acl/role/{username}")
async def get_user_roles(
        username: str,
        current_user: User = Depends(get_current_user),  # 需要登录权限，建议后端校验是否为管理员
        db: AsyncSession = Depends(get_db)
):
    """
    获取指定用户ID的角色列表
    前端用于展示该用户拥有哪些角色
    """
    try:
        user_roles_data = await get_user_rolelist(db, username)

        return success_response(
            message="获取用户角色成功",
            data=user_roles_data
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取角色失败: {str(e)}")


@router.put("/acl/assignRole/{username}")
async def set_user_rolelist(
    username: str,
    payload:RoleAssignSchema,
    current_user: User = Depends(get_current_user),  # 需要登录权限
    db: AsyncSession = Depends(get_db)
):
    """
    设置用户的角色（覆盖式更新）
    - 请求体直接传递角色ID数组: [1, 2, 3]
    - 会先删除用户所有现有角色，再添加新角色
    - 如果传递空数组 []，将清空用户的所有角色
    """
    try:
        result = await set_user_roles(db, username, payload.role_ids)
        return success_response(
            message=result["message"],
            data={
                "username": result["username"],
                "set_roles": result["set_roles"],
                "current_roles": result["current_roles"]
            }
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置角色失败: {str(e)}")


@router.get("/rolelist", response_model=RoleListApiResponse, summary="获取角色列表")
async def list_roles(
        page: int = Query(1, ge=1, description="当前页码，从1开始"),
        limit: int = Query(100, ge=1, le=500, description="每页数量"),
        role_name: Optional[str] = Query(None, description="角色名称模糊搜索"),
        current_user: User = Depends(get_current_user),  # 需要登录权限
        db: AsyncSession = Depends(get_db)
):
    """
    获取角色分页列表，返回 menus 对象列表。
    """
    skip = (page - 1) * limit

    # 1. 调用服务层
    # 确保 get_rolelist 内部使用了:
    # select(Role).options(selectinload(Role.role_menus).joinedload(RoleMenu.menu))
    roles, total = await get_rolelist(
        db=db,
        skip=skip,
        limit=limit,
        role_name=role_name
    )

    # 2. 直接返回数据
    # FastAPI 的 response_model 会自动处理 ORM 对象到 Pydantic 模型的转换
    # 包括嵌套的 role_menus -> menu 结构
    return success_response(
        message="获取角色列表成功",
        data={
            "items": roles,  # 直接传入 ORM 对象列表
            "total": total,
            "page": page,
            "limit": limit
        }
    )


# --- 1. 新增角色 ---
@router.post("/role/addrole", summary="新增角色", response_model=dict)
async def create_role(
        role_in: RoleCreate,
        current_user: User = Depends(get_current_user),  # 需要登录权限
        db: AsyncSession = Depends(get_db)
):
    """
    创建一个新的角色。
    """
    try:
        new_role = await crud.create_role(db, role_in)
        # 转换为 Pydantic 模型返回
        role_data = RoleItem(
            role_id=new_role.role_id,
            role_name=new_role.role_name,
            remark=new_role.remark,


        )
        return success_response(data=role_data, message="角色创建成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


# --- 2. 修改角色 ---
@router.put("/role/{role_id}", summary="修改角色", response_model=dict)
async def update_role(
        role_id: int,
        role_in: RoleUpdate,
        current_user: User = Depends(get_current_user),  # 需要登录权限
        db: AsyncSession = Depends(get_db)
):
    """
    根据 ID 修改角色信息。
    """
    # 检查是否提供了至少一个更新字段
    if not role_in.model_dump(exclude_unset=True):
        raise HTTPException(status_code=400, detail="未提供有效的更新字段")

    try:
        updated_role = await crud.update_role(db, role_id, role_in)
        if not updated_role:
            raise HTTPException(status_code=404, detail="角色不存在")

        role_data = RoleItem(
            role_id=updated_role.role_id,
            role_name=updated_role.role_name,
            remark=updated_role.remark,

        )
        return success_response(data=role_data, message="角色更新成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")


# --- 3. 删除角色 (单个) ---
@router.delete("/deleterole/{role_id}", summary="删除角色", response_model=dict)
async def delete_role(
        role_id: int,
        current_user: User = Depends(get_current_user),  # 需要登录权限
        db: AsyncSession = Depends(get_db)
):
    """
    根据 ID 删除角色。
    """
    try:
        # 可以在这里先检查权限或特殊规则 (如超级管理员不可删)
        # CRUD 中已经做了简单检查，这里主要处理返回值
        success = await crud.delete_role(db, role_id)

        if not success:
            raise HTTPException(status_code=404, detail="角色不存在或不可删除")

        return success_response(message="角色删除成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器内部错误: {str(e)}")



# --- -----------------------------------菜单按钮 -------------------------------------

# 1. 增加 Menu
@router.post("/addmenu", response_model=MenuInfo, status_code=status.HTTP_201_CREATED)
async def create_menu_route(
        menu_in: MenuCreate,
        db: AsyncSession = Depends(get_db)
):
    """
    创建新菜单
    """
    # 可选：检查 code 是否已存在
    # 这里简单演示直接创建，实际生产中建议增加唯一性校验

    # 将 Pydantic 模型转换为字典
    menu_data = menu_in.model_dump()

    try:
        new_menu = await create_menu(db=db, menu_data=menu_data)
        return new_menu
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"创建失败: {str(e)}")


# 2. 修改 Menu
@router.put("/updatemenu/{menu_id}", response_model=MenuInfo)
async def update_menu_route(
        menu_id: int,
        menu_in: MenuUpdate,
        db: AsyncSession = Depends(get_db)
):
    """
    更新指定 ID 的菜单信息
    """
    # 先检查菜单是否存在
    existing_menu = await get_menu_by_id(db, menu_id)
    if not existing_menu:
        raise HTTPException(status_code=404, detail="菜单不存在")

    # 提取需要更新的字段 (排除 None 值)
    update_data = menu_in.model_dump(exclude_unset=True, exclude_none=True)

    if not update_data:
        # 如果没有提供任何字段，直接返回原数据
        return existing_menu

    try:
        updated_menu = await update_menu(db=db, menu_id=menu_id, update_data=update_data)
        if not updated_menu:
            raise HTTPException(status_code=404, detail="更新失败，菜单未找到")
        return updated_menu
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"更新失败: {str(e)}")


# 3. 删除 Menu (逻辑删除)
@router.delete("/inactivemenu/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_route(
        menu_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    删除指定 ID 的菜单 (逻辑删除：将状态设为 inactive)
    """
    success = await delete_menu(db=db, menu_id=menu_id)

    if not success:
        raise HTTPException(status_code=404, detail="菜单不存在或删除失败")

    return None


# 4. 物理删除 Menu - 如果需要彻底删除数据           前端暂时不用!!!!!!!!!!!!!!!!!!!!!!
@router.delete("/deletemenu/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def hard_delete_menu_route(
        menu_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    物理删除指定 ID 的菜单 (慎用)
    """
    from modules.users.crud import hard_delete_menu
    success = await hard_delete_menu(db=db, menu_id=menu_id)

    if not success:
        raise HTTPException(status_code=404, detail="菜单不存在")

    return None


@router.get("/menus/tree")
async def get_all_menu_tree(db: AsyncSession = Depends(get_db)):
    """获取所有菜单树"""
    tree_data = await get_menu_tree(db)  #
    return success_response(data=tree_data, message="查询成功")






@router.get("/menus/role/{role_id}")
async def get_role_menu_tree_with_selected(
        role_id: int,
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    获取指定角色的菜单权限树（包含选中状态）
    """
    try:
        tree_data = await crud.get_role_menus_with_selected(db, role_id)
        return success_response(
            message="获取角色菜单权限成功",
            data=tree_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取菜单权限失败: {str(e)}")


@router.post("/menus/assign_menu/{role_id}")
async def assign_menu_permissions(
        role_id: int,
        menu_ids: List[int] = Body(..., description="菜单ID列表"),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    为角色分配菜单权限（先删除所有原有权限，再添加新权限）
    请求体格式: [1, 2, 3, 4]
    """
    try:
        success = await crud.assign_menus_to_role(db, role_id, menu_ids)

        if not success:
            raise HTTPException(status_code=500, detail="分配菜单权限失败")

        return success_response(
            message="分配菜单权限成功",
            data={
                "role_id": role_id,
                "assigned_menu_count": len(menu_ids)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分配菜单权限失败: {str(e)}")


@router.post("/avatar/upload")
async def upload_avatar(
        file: UploadFile = File(..., description="头像文件"),
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user),  # 放在最后
):
    """
    上传当前用户的头像
    """
    try:
        # 1. 保存头像文件
        filename = await AvatarUpload.save_avatar(file)

        # 2. 更新数据库中的头像字段
        updated_user, old_avatar = await crud.update_user_avatar_by_user_id(
            db,
            current_user.user_id,
            filename
        )

        if not updated_user:
            # 如果更新失败，删除刚上传的文件
            await AvatarUpload.delete_old_avatar(filename)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户头像失败"
            )

        # 3. 删除旧头像文件
        if old_avatar:
            await AvatarUpload.delete_old_avatar(old_avatar)

        # 4. 获取头像完整URL
        avatar_url = AvatarUpload.get_avatar_url(filename)

        return success_response(
            message="头像上传成功",
            data={
                "avatar": avatar_url,
                "filename": filename
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传头像失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传头像失败: {str(e)}"
        )
@router.delete("/avatar/delete")
async def delete_avatar(
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    删除当前用户的头像
    """
    try:
        # 1. 获取用户当前头像（调用 crud 层）
        user = await get_user_by_user_id(db, current_user.user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        if not user.avatar:
            return success_response(
                message="用户没有头像",
                data={"avatar": ""}
            )

        # 2. 保存旧头像文件名
        old_avatar = user.avatar

        # 3. 清空数据库中的头像字段（调用 crud 层）
        updated_user, _ = await clear_user_avatar_by_user_id(db, current_user.user_id)

        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="清空头像失败"
            )

        # 4. 删除头像文件（文件操作，不涉及数据库）
        await AvatarUpload.delete_old_avatar(old_avatar)

        return success_response(
            message="头像删除成功",
            data={"avatar": ""}
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除头像失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除头像失败: {str(e)}"
        )


@router.get("/avatar/{user_id}")
async def get_user_avatar(
        user_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
    获取指定用户的头像URL（公开接口）
    """
    try:
        # 调用 crud 层获取用户信息
        user = await get_user_by_user_id(db, user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )

        avatar_url = ""
        if user.avatar:
            avatar_url = AvatarUpload.get_avatar_url(user.avatar)

        return success_response(
            message="获取头像成功",
            data={
                "user_id": user.user_id,
                "username": user.username,
                "avatar": avatar_url
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取头像失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取头像失败: {str(e)}"
        )