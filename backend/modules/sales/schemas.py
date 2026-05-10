from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, model_validator

# 配置 Pydantic v2 以支持 ORM 模式
model_config = ConfigDict(
    populate_by_name=True,  # alias / 字段名兼容
    from_attributes=True)
# --- 请求模型 ---





