from datetime import datetime
from typing import Optional, List, Union

from pydantic import BaseModel, Field, ConfigDict

# 配置 Pydantic v2 以支持 ORM 模式
model_config = ConfigDict(
    populate_by_name=True,  # alias / 字段名兼容
    from_attributes=True)


class UserRequest(BaseModel):
    username: str
    password: str


# user_info 对应的类：基础类 + Info 类（id、用户名）
class UserInfoBase(BaseModel):
    """
    用户信息基础数据模型
    """
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, max_length=255, description="头像URL")
    gender: Optional[str] = Field(None, max_length=10, description="性别")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    email: Optional[str] = Field(None, max_length=64, description="邮箱")

    model_config =model_config

class UserInfoResponse(UserInfoBase):
    id: int
    user_id: int
    username: str
    created_time: datetime
    updated_time: datetime



#
# data 数据类型
class UserAuthResponse(BaseModel):
    token: str
    user_info: UserInfoResponse = Field(..., alias="userInfo")


    # 模型类配置
    model_config = model_config

class UserInfoDetail(UserInfoResponse):
    """
    用户信息详情模型类
    """

    roles: List[str] = Field(default=[], description="用户角色名称列表，如：['管理员', '前端用户']")
    routes: List[str] = Field(default=[], description="用户路由名称列表，如：['Permission', 'User']")
    buttons: List[str] = Field(default=[], description="用户按钮名称列表，如：['btn.add', 'btn.update']")



#
# 更新用户信息的模型类
class UserUpdateRequest(BaseModel):
    nickname: str = None
    avatar: str = None
    gender: str = None
    bio: str = None
    phone: str = None
#
#

class UserChangePasswordRequest(BaseModel):
    old_password: str = Field(..., alias="oldPassword", description="旧密码")
    new_password: str = Field(..., min_length=6, alias="newPassword", description="新密码")


class UserDeleteRequest(BaseModel):
    username: Union[str, List[str]]  # 明确告诉系统：可以是字符串，也可以是列表
    # 模型类配置
    model_config = model_config




class UserRoleNameSchema(BaseModel):
    """仅包含角色名称的 Schema"""
    role_name: str = Field(..., description="角色名称")

    model_config = model_config


class UserInfoWithRolesResponse(UserInfoResponse):
    """扩展用户信息，包含角色列表"""
    # 继承原有的 id, user_id, username, nickname 等字段
    roles: List[str] = Field(default=[], description="用户角色名称列表，如：['管理员', '前端用户']")




class UserListResponse(BaseModel):
    """用户列表响应包装"""
    items: List[UserInfoWithRolesResponse]
    total: int = Field(..., description="用户总数")


    model_config = model_config


class RoleAssignSchema(BaseModel):
    role_ids: List[int] = Field(..., description="角色ID列表")
    model_config = model_config



class MenuInfo(BaseModel):
    menu_id: int
    pid: int
    name: str
    code: str
    to_code: str
    type: Optional[int] = None
    status: str
    level: int

    selected: bool

    model_config = model_config


# --- 2. 角色菜单关联 Schema (可选，如果只需要菜单信息可跳过，直接用 MenuInfo) ---
# 如果你的前端只需要菜单详情，可以直接在 Role 里放 List[MenuInfo]
# 如果需要关联表的 ID (user_role 表的 id)，则保留这个中间层
class RoleMenuDetail(BaseModel):
    id: int  # 关联表 user_role_menu 的 ID
    role_id: int
    menu_id: int
    menu: MenuInfo  # 嵌套菜单详情

    model_config = model_config


# --- 3. 角色列表项 Schema ---
class RoleItem(BaseModel):
    role_id: int
    role_name: str
    remark: Optional[str] = None

    model_config = model_config




class RoleListItem(RoleItem):

    created_time: datetime
    updated_time: datetime






# --- 4. 分页响应包装器 ---
class PageResponse(BaseModel):
    items: List[RoleListItem]
    total: int
    page: int
    limit: int

    model_config = model_config

class RoleListApiResponse(BaseModel):
    code: int
    message: str
    data: PageResponse  # 这里嵌套
    ok: bool

    model_config = model_config


class RoleCreate(BaseModel):
    """新增角色请求模型"""
    role_name: str = Field(..., min_length=2, max_length=50, description="角色名称")
    remark: Optional[str] = Field(None, max_length=255, description="备注")
    model_config = model_config


class RoleUpdate(BaseModel):
    """修改角色请求模型"""
    role_name: Optional[str] = Field(None, min_length=2, max_length=50, description="角色名称")
    remark: Optional[str] = Field(None, max_length=255, description="备注")
    model_config = model_config

class RoleDelete(BaseModel):
    """批量删除请求模型 (可选，支持单个或批量)"""
    ids: List[int] = Field(..., description="要删除的角色ID列表")


    # --------------菜单按钮类--------------------------------
class MenuCreate(BaseModel):
    """创建菜单请求模型"""
    pid: int = Field(0, description="父级菜单ID")
    name: str = Field(..., max_length=100, description="菜单名称")
    code: str = Field(..., max_length=100, description="菜单编码")
    to_code: str = Field(..., max_length=100, description="目标编码")
    type: Optional[int] = Field(1, description="类型: 1 菜单，2 按钮")
    status: str = Field('active', description="状态")
    level: int = Field(1, description="层级")
    selected: bool = Field(False, description="是否选中")

    model_config = model_config


class MenuUpdate(BaseModel):
    """更新菜单请求模型 (所有字段可选)"""
    pid: Optional[int] = Field(None, description="父级菜单ID")
    name: Optional[str] = Field(None, max_length=100, description="菜单名称")
    code: Optional[str] = Field(None, max_length=100, description="菜单编码")
    to_code: Optional[str] = Field(None, max_length=100, description="目标编码")
    type: Optional[int] = Field(None, description="类型: 1 菜单，2 按钮")
    status: Optional[str] = Field(None, description="状态")
    level: Optional[int] = Field(None, description="层级")
    selected: Optional[bool] = Field(None, description="是否选中")

    model_config = model_config