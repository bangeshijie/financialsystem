from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime
from typing import Any, Dict

# 定义一个 Mixin 类，包含时间戳字段
class TimestampMixin:
    # 注意：在 Mixin 中，我们通常只声明类型，或者确保 mapped_column 被正确处理
    # 对于 DeclarativeBase，最安全的 Mixin 写法是直接定义属性，但去掉 Mapped 泛型提示可能会报错
    # 正确的 SQLAlchemy 2.0 Mixin 写法如下：

    created_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="创建时间"
    )
    updated_time: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间"
    )


class Base(DeclarativeBase, TimestampMixin):
    """
    所有数据库模型的基类。
    通过 Mixin 自动继承 created_time 和 updated_time 字段。
    """
    def to_dict(self) -> Dict[str, Any]:
        data = {}
        # 安全地获取列
        if hasattr(self, '__table__'):
            for column in self.__table__.columns:
                key = column.name
                value = getattr(self, key)
                if isinstance(value, datetime):
                    value = value.isoformat()
                data[key] = value
        return data