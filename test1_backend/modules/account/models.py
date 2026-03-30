from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from config.base import Base


class BalanceDirection(str, enum.Enum):
    DEBIT = "debit"  # 借方
    CREDIT = "credit"  # 贷方


class AccountingSubject(Base):
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 科目编码：核心字段，通常唯一且有序 (如 1001, 100201)
    code = Column(String(20), unique=True, index=True, nullable=False, comment="科目编码")

    # 科目名称
    name = Column(String(100), nullable=False, comment="科目名称")

    # 层级结构
    parent_id = Column(Integer, ForeignKey("account.id"), nullable=True, index=True, comment="父科目ID")
    level = Column(Integer, default=1, comment="科目级次 (1=一级, 2=二级...)")

    # 属性
    balance_direction = Column(Enum(BalanceDirection), default=BalanceDirection.DEBIT, comment="余额方向")
    is_active = Column(Boolean, default=True, comment="是否启用")
    full_name = Column(String(255), nullable=True, comment="全称路径 (如: 资产/流动资产/货币资金)")

    # 关系：自关联 (一个父科目有多个子科目)
    # children: 一个父节点对应多个子节点 (One-to-Many)
    # cascade="all, delete-orphan" 确保删除父节点时处理子节点（根据你的业务需求决定是否开启）
    children = relationship(
        "AccountingSubject",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin"  # 优化查询，自动预加载子节点，避免 N+1 问题
    )

    # parent: 多个子节点对应一个父节点 (Many-to-One)
    # remote_side 指向父表的 ID 列
    parent = relationship(
        "AccountingSubject",
        back_populates="children",
        remote_side=[id],  # type: ignore[arg-type] # 这里的 id 指的是本类中的 id 列，表示这一侧是“多”的一方
        lazy="joined"  # 加载父节点时使用 join
    )


    def __repr__(self):
        return f"<AccountingSubject(code={self.code}, name={self.name})>"