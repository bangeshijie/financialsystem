from datetime import datetime
from typing import Optional

from sqlalchemy import Index, BigInteger, String, Enum, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from config.base import Base


class Company(Base):
    """
    公司信息表 ORM 模型
    【安全重构版】：仅映射数据库列，无任何关联关系，杜绝自动加载用户数据。
    """
    __tablename__ = 'company'

    __table_args__ = (
        Index('idx_company_name', 'name'),
        Index('idx_company_code', 'company_code', unique=True),
        Index('idx_created_by', 'created_by'),
        Index('idx_updated_by', 'updated_by'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="主键ID")
    company_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, comment="公司唯一标识(ID)")

    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="公司名称")
    company_code: Mapped[str] = mapped_column(String(8), unique=True, nullable=False, comment="公司编码/简称")

    address: Mapped[Optional[str]] = mapped_column(String(255), comment="公司地址")
    contact_person: Mapped[Optional[str]] = mapped_column(String(64), comment="联系人姓名")
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20), comment="联系电话")
    contact_email: Mapped[Optional[str]] = mapped_column(String(128), comment="联系邮箱")

    industry: Mapped[Optional[str]] = mapped_column(String(64), comment="所属行业")
    scale: Mapped[Optional[str]] = mapped_column(Enum('small', 'medium', 'large', 'enterprise'),
                                                 comment="公司规模", default='small')
    description: Mapped[Optional[str]] = mapped_column(String(1000), comment="公司简介", default='')
    status: Mapped[int] = mapped_column(BigInteger, default=1, comment="状态: 1-正常, 0-停用")

    # --- 仅保留外键 ID ---
    created_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey('user.user_id'), comment="创建人ID")
    updated_by: Mapped[Optional[int]] = mapped_column(BigInteger, ForeignKey('user.user_id'), comment="更新人ID")



    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}')>"