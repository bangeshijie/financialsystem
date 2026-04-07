from datetime import datetime
from typing import Optional

from sqlalchemy import Index, BigInteger, String, Enum, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from config.base import Base


class City(Base):
    """
    城市信息表 ORM 模型
    """
    __tablename__ = 'city'

    # 索引定义
    __table_args__ = (
        Index('idx_city_name', 'name'),
        Index('idx_city_province', 'province'),
        Index('idx_city_id', 'id', unique=True),
    )

    # --- 字段定义 ---

    # 城市ID：主键，自增
    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="城市ID"
    )

    # 城市名称
    name: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="城市名称"
    )

    # 省
    province: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="省份"
    )

    # 区域
    area: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="区域"
    )

    # 城市分类
    category: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        comment="城市分类"
    )








    def __repr__(self):
        return f"<City(id={self.id}, name='{self.name}')>"