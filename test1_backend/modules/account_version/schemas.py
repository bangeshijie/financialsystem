
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List




# 配置 Pydantic v2 以支持 ORM 模式
model_config = ConfigDict(
    populate_by_name=True,
    from_attributes=True
)



# ============ AccountVersion Schemas ============
class AccountVersionBase(BaseModel):
    """科目版本基础模型"""
    version_code: str = Field(..., max_length=20, description="版本编码")
    version_name: str = Field(..., max_length=100, description="版本名称")
    description: Optional[str] = Field(None, max_length=255, description="版本描述")
    is_default: bool = Field(False, description="是否默认版本")
    is_active: bool = Field(True, description="是否启用")
    effective_date: Optional[str] = Field(None, max_length=20, description="生效日期")
    remark: Optional[str] = Field(None, max_length=500, description="版本备注")

    model_config = model_config


class AccountVersionCreate(AccountVersionBase):
    """创建科目版本"""
    pass


class AccountVersionUpdate(BaseModel):
    """更新科目版本（所有字段可选）"""
    version_code: Optional[str] = Field(None, max_length=20, description="版本编码")
    version_name: Optional[str] = Field(None, max_length=100, description="版本名称")
    description: Optional[str] = Field(None, max_length=255, description="版本描述")
    is_default: Optional[bool] = Field(None, description="是否默认版本")
    is_active: Optional[bool] = Field(None, description="是否启用")
    effective_date: Optional[str] = Field(None, max_length=20, description="生效日期")
    remark: Optional[str] = Field(None, max_length=500, description="版本备注")

    model_config = model_config


class AccountVersionInDB(AccountVersionBase):
    """数据库中的科目版本"""
    id: int



class AccountVersionResponse(AccountVersionInDB):
    """科目版本响应"""
    pass


class AccountVersionListResponse(BaseModel):
    """科目版本列表响应"""
    total: int
    items: List[AccountVersionResponse]

    model_config = model_config

