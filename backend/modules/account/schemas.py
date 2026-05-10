# schemas.py
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List

import enum

from modules.account_version.schemas import AccountVersionResponse

# 配置 Pydantic v2 以支持 ORM 模式
model_config = ConfigDict(
    populate_by_name=True,
    from_attributes=True
)


class BalanceDirection(str, enum.Enum):
    DEBIT = "debit"  # 借方
    CREDIT = "credit"  # 贷方




# ============ Account Schemas ============
class AccountBase(BaseModel):
    """会计科目基础模型"""
    code: str = Field(..., max_length=20, description="科目编码")
    name: str = Field(..., max_length=100, description="科目名称")
    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    parent_id: Optional[int] = Field(None, description="父科目ID")  # 改为 parent_id
    level: int = Field(1, ge=1, description="科目级次")
    is_leaf: bool = Field(False, description="是否叶子节点")
    balance_direction: BalanceDirection = Field(BalanceDirection.DEBIT, description="余额方向")
    is_active: bool = Field(True, description="是否启用")
    full_name: Optional[str] = Field(None, max_length=255, description="全称路径")
    account_version_id: int = Field(..., description="科目版本ID")

    model_config = model_config


class AccountCreate(AccountBase):
    """创建会计科目"""
    pass


class AccountUpdate(BaseModel):
    """更新会计科目（所有字段可选）"""
    code: Optional[str] = Field(None, max_length=20, description="科目编码")
    name: Optional[str] = Field(None, max_length=100, description="科目名称")
    display_name: Optional[str] = Field(None, max_length=100, description="显示名称")
    parent_id: Optional[int] = Field(None, description="父科目ID")  # 改为 parent_id
    level: Optional[int] = Field(None, ge=1, description="科目级次")
    is_leaf: Optional[bool] = Field(None, description="是否叶子节点")
    balance_direction: Optional[BalanceDirection] = Field(None, description="余额方向")
    is_active: Optional[bool] = Field(None, description="是否启用")
    full_name: Optional[str] = Field(None, max_length=255, description="全称路径")
    account_version_id: Optional[int] = Field(None, description="科目版本ID")

    model_config = model_config


class AccountInDB(AccountBase):
    """数据库中的会计科目"""
    id: int

    model_config = ConfigDict(from_attributes=True)


class AccountResponse(AccountInDB):
    """会计科目响应"""
    children: Optional[List['AccountResponse']] = None
    version: Optional[AccountVersionResponse] = None


class AccountListResponse(BaseModel):
    """会计科目列表响应"""
    total: int
    items: List[AccountResponse]
    skip: int = Field(0, description="跳过的记录数")
    limit: int = Field(100, description="每页记录数")

    model_config = model_config


# 更新前向引用
AccountResponse.model_rebuild()
