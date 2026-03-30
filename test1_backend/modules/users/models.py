
from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, String, DateTime, func, Index, ForeignKey, Enum, Integer, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from config.base import Base


class User(Base):
    """
    用户信息表ORM模型
    """
    __tablename__ = 'user'

    # 创建索引
    __table_args__ = (
        Index('username_UNIQUE', 'username'),

    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="自增ID")
    user_id: Mapped[int] = mapped_column(BigInteger,unique=True,nullable=False,comment="用户ID（雪花算法）")
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="用户名")
    password: Mapped[str] = mapped_column(String(64), nullable=False, comment="密码（加密存储）")
    nickname: Mapped[Optional[str]] = mapped_column(String(64), comment="昵称")
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, comment="手机号")
    avatar: Mapped[Optional[str]] = mapped_column(String(255), comment="头像URL",
                                                  default='totoro.png')

    bio: Mapped[Optional[str]] = mapped_column(String(500), comment="个人简介", default='这个人很懒，什么都没留下')
    email: Mapped[Optional[str]] = mapped_column(String(64), comment="邮箱", )

    gender: Mapped[Optional[str]] = mapped_column(Enum('male', 'female', 'unknown'), comment="性别", default='unknown')



    # 【关键】定义一对多关系：一个 User 对应多个 UserRole 记录
    # lazy="select" 是默认值，意味着当你访问 user.roles 时才会去数据库查
    # 如果想一次性查出，可以使用 lazy="joined" 或在查询时使用 options(joinedload(User.roles))
    roles: Mapped[list["UserRole"]] = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', nickname='{self.nickname}')>"


class UserToken(Base):
    """
    用户令牌表ORM模型
    """
    __tablename__ = 'user_token'

    # 创建索引
    __table_args__ = (
        Index('token_UNIQUE', 'token'),
        Index('fk_user_token_user_idx', 'user_id'),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True, comment="令牌ID")
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('user.user_id', onupdate="CASCADE", ondelete="CASCADE"), nullable=False, comment="用户ID（雪花算法）")
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, comment="令牌值")
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment="过期时间")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), comment="创建时间")


    def __repr__(self):
        return f"<UserToken(id={self.id}, user_id={self.user_id}, token='{self.token}')>"


class Role(Base):
    """
    角色信息表 ORM 模型 (role_id 改为数据库自增)
    """
    __tablename__ = 'role'

    # --- 修改开始 ---
    # 1. autoincrement=True (或者干脆不写这个参数，默认就是 True)
    # 2. 建议加上 default=None 或 nullable=True (仅在 Python 层面，DB 层依然是 NOT NULL)
    #    这样在创建对象 Role(role_name="...") 时不需要传 role_id
    role_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,  # 👈 关键：开启自增，让数据库生成 ID
        comment="角色业务ID (主键)"
    )
    # --- 修改结束 ---

    # 角色名称保持唯一
    role_name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        comment="角色名称"
    )

    remark: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        comment="备注"
    )

    # --- 关系映射 (保持不变) ---
    users: Mapped[List["UserRole"]] = relationship(
        "UserRole",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    role_menus: Mapped[List["RoleMenu"]] = relationship(
        "RoleMenu",
        back_populates="role",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    def __repr__(self):
        return f"<Role(role_id={self.role_id}, role_name='{self.role_name}')>"


class UserRole(Base):
    """
    用户角色关联表 ORM 模型
    对应 SQL: CREATE TABLE `user_role` ...
    """
    __tablename__ = 'user_role'

    # 可选：添加联合索引，加速查询特定用户或特定角色的记录
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_role_id', 'role_id'),
        # 如果需要确保一个用户不能有重复的同一个角色，可以添加唯一联合索引：
        Index('uq_user_role', 'user_id', 'role_id', unique=True),
    )

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,

        # 数据库层面有外键约束，并确认 User 表已定义
        ForeignKey('user.user_id', onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        comment="用户ID（雪花算法）"
    )

    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('role.role_id', onupdate="CASCADE", ondelete="CASCADE"),
        nullable=False,
        comment="角色ID"
    )



    # 定义多对一关系：多个UserRole记录对应一个User
    # back_populates 必须与 User 类中的字段名一致
    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")

    def __repr__(self):
        return f"<UserRole(id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"


class Menu(Base):
    """
    菜单信息表 ORM 模型
    """
    __tablename__ = 'menu'

    __table_args__ = (
        Index('idx_menu_pid', 'pid'),
        Index('idx_menu_code', 'code'),
        {'comment': '菜单信息表'}
    )

    menu_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
        comment="菜单业务ID (主键)"
    )

    pid: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="父级菜单ID"
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="菜单名称"
    )

    code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="菜单编码"
    )

    to_code: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="目标编码"
    )

    type: Mapped[Optional[int]] = mapped_column(
        Integer,
        default=1,
        comment="类型: 1 菜单，2 按钮"
    )

    status: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default='active',
        server_default=text("'active'"),  # 数据库级别的默认值（关键修复）
        comment="状态"
    )

    level: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        comment="层级"
    )

    # ✅ 修复：为 select 字段添加 server_default
    selected: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,              # Python 级别的默认值
        server_default=text('0'),   # 数据库级别的默认值（关键修复）
        comment="是否选中"
    )



    role_menus: Mapped[List["RoleMenu"]] = relationship(
        "RoleMenu",
        back_populates="menu",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Menu(menu_id={self.menu_id}, name='{self.name}', code='{self.code}')>"

class RoleMenu(Base):
    """
    角色菜单关联表 ORM 模型
    对应 SQL: CREATE TABLE `role_menu` ...
    """
    __tablename__ = 'role_menu'

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment="主键ID"
    )

    role_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('role.role_id'),
        nullable=False,
        comment="角色ID"
    )

    menu_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('menu.menu_id'),
        nullable=False,
        comment="菜单ID"
    )



    # 如果需要反向查询，可以在此处添加 relationship
    menu = relationship("Menu", back_populates="role_menus")
    role = relationship("Role", back_populates="role_menus")

    def __repr__(self):
        return f"<RoleMenu(id={self.id}, role_id={self.role_id}, menu_id={self.menu_id})>"