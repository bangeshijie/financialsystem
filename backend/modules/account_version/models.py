from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, select, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
import enum

from config.base import Base




class AccountVersion(Base):
    """科目版本管理表"""
    __tablename__ = "account_version"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    version_code = Column(String(20), unique=True, index=True, nullable=False, comment="版本编码")
    version_name = Column(String(100), nullable=False, comment="版本名称")
    description = Column(String(255), nullable=True, comment="版本描述")
    is_default = Column(Boolean, default=False, comment="是否默认版本")
    is_active = Column(Boolean, default=True, comment="是否启用")
    effective_date = Column(String(20), nullable=True, comment="生效日期")
    remark = Column(String(500), nullable=True, comment="版本备注")

    # 关系：一个版本包含多个科目
    accounts = relationship("Account", back_populates="account_version", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<AccountVersion(code={self.version_code}, name={self.version_name})>"

