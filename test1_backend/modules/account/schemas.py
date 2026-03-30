from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from modules.account.models import BalanceDirection

# 配置 Pydantic v2 以支持 ORM 模式
model_config = ConfigDict(
    populate_by_name=True,  # alias / 字段名兼容
    from_attributes=True)


# --- 创建/更新模型 ---
class SubjectCreate(BaseModel):
    model_config = model_config
    code: str = Field(..., min_length=4, max_length=20, description="科目编码")
    name: str = Field(..., max_length=100, description="科目名称")
    parent_id: Optional[int] = Field(None, description="父科目ID，留空则为一级科目")
    balance_direction: BalanceDirection = Field(default=BalanceDirection.DEBIT, description="余额方向")
    is_active: bool = True


class SubjectUpdate(BaseModel):
    model_config = model_config
    name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None
    # 注意：实际生产中修改 code 或 parent_id 需要非常谨慎，可能涉及历史数据一致性


# --- 响应模型 ---
class SubjectResponse(BaseModel):
    model_config = model_config

    id: int
    code: str
    name: str
    parent_id: Optional[int] = None
    level: int
    balance_direction: BalanceDirection
    is_active: bool
    full_name: Optional[str]
    created_at: Optional[datetime] = None  # 如果模型中有时间字段需加上

    # 嵌套显示子科目 (可选，防止循环引用需小心处理)
    children: List['SubjectResponse'] = []


# 解决递归引用问题 (Pydantic V2 写法)
SubjectResponse.model_rebuild()