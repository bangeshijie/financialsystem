from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, select, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship
import enum

from config.base import Base
from modules.account_version.models import AccountVersion


class BalanceDirection(str, enum.Enum):
    """余额方向枚举"""
    DEBIT = "debit"  # 借方
    CREDIT = "credit"  # 贷方




class Account(Base):
    """会计科目表"""
    __tablename__ = "account"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 核心字段 - code 不再唯一，由 (code, account_version_id) 联合唯一
    code = Column(String(20), nullable=False, comment="科目编码")
    name = Column(String(100), nullable=False, comment="科目名称")
    display_name = Column(String(100), nullable=True, comment="显示名称")

    # 层级与结构 - 使用 parent_id 引用主键 id
    parent_id = Column(Integer, ForeignKey("account.id"), nullable=True, index=True, comment="父科目ID")
    level = Column(Integer, default=1, comment="科目级次 (1=一级, 2=二级...)")
    is_leaf = Column(Boolean, default=False, comment="是否叶子节点(末级科目)")

    # 属性
    balance_direction = Column(Enum(BalanceDirection), default=BalanceDirection.DEBIT, comment="余额方向")
    is_active = Column(Boolean, default=True, comment="是否启用")
    full_name = Column(String(255), nullable=True, comment="全称路径")

    # 版本外键
    account_version_id = Column(Integer, ForeignKey("account_version.id"), nullable=False, default=1,
                                comment="科目版本ID")

    # 联合唯一约束：同一版本内科目编码唯一
    __table_args__ = (
        UniqueConstraint('code', 'account_version_id', name='uq_account_code_version'),
    )

    # --- 关系定义 ---

    # 版本关系
    account_version = relationship("AccountVersion", back_populates="accounts")

    # 自关联：子节点 (One-to-Many)
    children = relationship(
        "Account",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    # 自关联：父节点 (Many-to-One)
    parent = relationship(
        "Account",
        back_populates="children",
        remote_side="Account.id",
        lazy="joined"
    )

    def __repr__(self):
        return f"<Account(code={self.code}, name={self.name}, account_version_id={self.account_version_id})>"

    # --- 业务逻辑方法（异步版本）---

    @staticmethod
    async def update_leaf_status(db: AsyncSession, subject_id: int):
        """
        递归更新指定科目及其祖先节点的 is_leaf 状态
        """
        # 检查是否有子节点
        result = await db.execute(
            select(Account).where(Account.parent_id == subject_id).limit(1)
        )
        has_children = result.scalar_one_or_none() is not None

        # 获取当前节点
        result = await db.execute(
            select(Account).where(Account.id == subject_id)
        )
        subject = result.scalar_one_or_none()

        if subject:
            new_leaf_status = not has_children
            if subject.is_leaf != new_leaf_status:
                subject.is_leaf = new_leaf_status
                await db.flush()
                # 自下而上迭代
                if subject.parent_id:
                    await Account.update_leaf_status(db, subject.parent_id)

    async def update_full_name(self, db: AsyncSession):
        """更新科目的完整路径名称"""
        if self.parent_id:
            result = await db.execute(
                select(Account).where(Account.id == self.parent_id)
            )
            parent = result.scalar_one_or_none()

            if parent:
                if not parent.full_name:
                    await parent.update_full_name(db)

                self.full_name = f"{parent.full_name}/{self.name}"
            else:
                self.full_name = self.name
        else:
            self.full_name = self.name

    @classmethod
    async def create_in_db(cls, db: AsyncSession,
                           code: str, name: str,
                           account_version_id: int,
                           parent_id: int = None,
                           **kwargs):
        """
        在数据库中创建科目，自动处理层级、全名、叶子节点状态
        """
        # 1. 检查版本
        version = await db.get(AccountVersion, account_version_id)
        if not version:
            raise ValueError("版本不存在")

        # 2. 处理父节点逻辑
        parent = None
        level = 1
        full_name = name

        if parent_id:
            parent = await db.get(Account, parent_id)
            if not parent:
                raise ValueError(f"父科目 ID {parent_id} 不存在")

            if parent.account_version_id != account_version_id:
                raise ValueError(f"父科目 ID {parent_id} 不属于指定版本")

            level = parent.level + 1
            parent_full = parent.full_name or parent.name
            full_name = f"{parent_full}/{name}"

        # 3. 检查编码冲突（同一版本内编码唯一）
        result = await db.execute(
            select(Account).where(
                Account.code == code,
                Account.account_version_id == account_version_id
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError(f"编码 {code} 在版本 {account_version_id} 中已存在")

        # 4. 创建新科目
        subject = cls(
            code=code,
            name=name,
            display_name=kwargs.get('display_name', name),
            parent_id=parent_id,
            level=level,
            full_name=full_name,
            balance_direction=kwargs.get('balance_direction', BalanceDirection.DEBIT),
            is_active=kwargs.get('is_active', True),
            account_version_id=account_version_id,
            is_leaf=True
        )

        db.add(subject)
        await db.flush()

        # 5. 更新父节点状态
        if parent:
            parent.is_leaf = False
            db.add(parent)

        return subject

    async def delete_with_children(self, db: AsyncSession):
        """
        安全删除科目及其子树
        """
        # 检查是否有子节点
        result = await db.execute(
            select(Account).where(
                Account.parent_id == self.id,
                Account.account_version_id == self.account_version_id
            ).limit(1)
        )
        has_children = result.scalar_one_or_none() is not None

        if has_children:
            raise ValueError("请先删除所有子科目")

        parent_id = self.parent_id
        account_version_id = self.account_version_id

        await db.delete(self)
        await db.flush()

        # 更新父节点的 is_leaf 状态
        if parent_id:
            result = await db.execute(
                select(Account).where(
                    Account.parent_id == parent_id,
                    Account.account_version_id == account_version_id
                ).limit(1)
            )
            remaining_children = result.scalar_one_or_none() is not None

            parent = await db.get(Account, parent_id)
            if parent:
                parent.is_leaf = not remaining_children
                db.add(parent)

        return True

    @staticmethod
    async def get_full_tree(db: AsyncSession, account_version_id: int):
        """
        一次性查询所有节点，在内存中构建树
        """
        result = await db.execute(
            select(Account)
            .where(Account.account_version_id == account_version_id)
            .order_by(Account.code)
        )
        nodes = result.scalars().all()

        # 将 SQLAlchemy 对象转换为普通字典，避免懒加载问题
        node_list = []
        node_map = {}

        for node in nodes:
            # 创建普通字典而不是 ORM 对象
            node_dict = {
                'id': node.id,
                'code': node.code,
                'name': node.name,
                'display_name': node.display_name,
                'parent_id': node.parent_id,
                'level': node.level,
                'is_leaf': node.is_leaf,
                'balance_direction': node.balance_direction,
                'is_active': node.is_active,
                'full_name': node.full_name,
                'account_version_id': node.account_version_id,
                'children': []
            }
            node_map[node.id] = node_dict
            node_list.append(node_dict)





        # 构建树结构
        root_nodes = []
        for node in node_list:
            if node['parent_id'] is None:
                root_nodes.append(node)
            else:
                parent = node_map.get(node['parent_id'])
                if parent:
                    parent['children'].append(node)
                else:
                    root_nodes.append(node)

        return root_nodes
    @classmethod
    async def find_by_code(cls, db: AsyncSession, code: str, account_version_id: int):
        """根据科目编码和版本查找科目"""
        result = await db.execute(
            select(cls).where(
                cls.code == code,
                cls.account_version_id == account_version_id
            )
        )
        return result.scalar_one_or_none()