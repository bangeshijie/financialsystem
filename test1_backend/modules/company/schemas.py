from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator

# 配置 Pydantic v2 以支持 ORM 模式
model_config = ConfigDict(
    populate_by_name=True,  # alias / 字段名兼容
    from_attributes=True)
# --- 请求模型 ---
class CompanyCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=128, description="公司名称")
    company_code: str = Field(..., min_length=4, max_length=8, description="公司编码")
    address: Optional[str] = Field(None, max_length=255, description="公司地址")
    contact_person: Optional[str] = Field(None, max_length=64, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    contact_email: Optional[str] = Field(None, max_length=128, description="联系邮箱")
    industry: Optional[str] = Field(None, max_length=64, description="行业")
    scale: Optional[str] = Field('small', description="规模")
    description: Optional[str] = Field('', max_length=1000, description="简介")


class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=128, description="公司名称")
    address: Optional[str] = Field(None, max_length=255, description="公司地址")
    contact_person: Optional[str] = Field(None, max_length=64, description="联系人")
    contact_phone: Optional[str] = Field(None, max_length=20, description="联系电话")
    contact_email: Optional[str] = Field(None, max_length=128, description="联系邮箱")
    industry: Optional[str] = Field(None, max_length=64, description="行业")
    scale: Optional[str] = Field(None, description="规模")
    description: Optional[str] = Field(None, max_length=1000, description="简介")
    status: Optional[int] = Field(None, ge=0, le=1, description="状态")


# --- 响应模型：简化版 (用于创建/更新) ---
class CompanyBaseResponse(BaseModel):
    """
    仅包含公司基础信息。
    不包含 created_by/updater_by ID，更不包含任何用户对象或名字。
    """
    id: int
    company_id: int
    name: str
    company_code: str
    address: Optional[str]
    contact_person: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    industry: Optional[str]
    scale: Optional[str]
    description: Optional[str]
    status: int
    created_time: datetime
    updated_time: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'  # 忽略任何未定义的字段（如意外挂载的属性）
    )



# --- 响应模型：详细版 (用于详情/列表) ---
class CompanyDetailResponse(BaseModel):
    """
    包含公司详细信息 + 创建人/更新人的 username。
    【安全承诺】：绝不返回 password, email, avatar 等任何其它用户字段。
    """
    id: int
    company_id: int
    name: str
    company_code: str
    address: Optional[str]
    contact_person: Optional[str]
    contact_phone: Optional[str]
    contact_email: Optional[str]
    industry: Optional[str]
    scale: str
    description: Optional[str]
    status: int

    # 只返回用户名字符串
    creator_name: Optional[str] = None
    updater_name: Optional[str] = None

    created_time: datetime
    updated_time: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore'
    )

    @model_validator(mode='before')
    @classmethod
    def ensure_strings_only(cls, values):
        if isinstance(values, dict):
            # 如果 CRUD 层失误传入了对象，这里强制转为字符串并清除对象
            for key in ['creator', 'updater']:
                obj = values.get(key)
                if obj:
                    username = getattr(obj, 'username', None) or obj.get('username', '未知')
                    values[f'{key}_name'] = username
                    values.pop(key, None)  # 彻底移除对象
        return values


class CompanyListResponse(BaseModel):
    total: int
    items: List[CompanyDetailResponse]




# ✅ 轻量级模型：只包含下拉框需要的字段
class CompanyOption(BaseModel):
    company_code: str
    name: str
    model_config =model_config


# 列表响应包装（可选，看你是否需要统一包裹 data/items）
class CompanyOptionsResponse(BaseModel):
    items: List[CompanyOption]