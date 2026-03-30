import asyncio
from typing import List

# 引入你的配置和模型
from db.session import async_engine, AsyncSessionLocal
from config.base import Base
from modules.users.models import User, Role, UserRole
from utils.security import get_hash_password
from sqlalchemy import select


async def init_db_tables():
    """创建所有表结构"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表结构初始化完成")


async def seed_default_roles():
    """
    初始化固定角色数据
    【修改策略】：不再指定 role_id，让数据库自增。
    通过 role_name 唯一性来确保不重复插入。
    """
    # 定义固定角色清单 (移除了 role_id)
    roles_config: List[dict] = [
        {"role_name": "超级管理员", "remark": "系统最高权限，不可删除"},
        {"role_name": "普通管理员", "remark": "负责日常内容管理和用户审核"},
        {"role_name": "编辑", "remark": "可以发布、编辑和下架文章"},
        {"role_name": "普通用户", "remark": "系统默认注册用户角色"},
        {"role_name": "访客", "remark": "未登录或仅浏览权限"},
        {"role_name": "测试用户", "remark": "用于测试权限功能"},
        {"role_name": "财务", "remark": "财务部门的用户"}
    ]

    async with AsyncSessionLocal() as session:
        try:
            for r_config in roles_config:
                r_name = r_config["role_name"]

                # 1. 通过 role_name 查询是否已存在 (因为 role_name 有唯一索引)
                stmt = select(Role).where(Role.role_name == r_name)
                result = await session.execute(stmt)
                role = result.scalar_one_or_none()

                if not role:
                    # 不存在 -> 插入 (不传 role_id，数据库自动生成)
                    new_role = Role(
                        role_name=r_name,
                        remark=r_config["remark"]
                    )
                    session.add(new_role)
                    # flush 一下以便立即获取生成的 ID (可选，为了打印日志)
                    await session.flush()
                    print(f"✅ [新增] 角色: {r_name} (自动生成 ID: {new_role.role_id})")
                else:
                    # 存在 -> 检查是否需要更新备注
                    is_updated = False
                    if role.remark != r_config["remark"]:
                        role.remark = r_config["remark"]
                        is_updated = True

                    if is_updated:
                        print(f"🔄 [更新] 角色: {r_name} 的备注信息")
                    # else: 静默跳过

            await session.commit()
            print("🎉 角色数据同步完成！")

        except Exception as e:
            await session.rollback()
            print(f"❌ 角色初始化失败: {e}")
            raise


async def seed_default_users():
    """插入默认数据 - 包含创建 Admin 并绑定超级管理员角色"""
    async with AsyncSessionLocal() as session:
        try:
            # 1. 检查是否已存在 admin 用户
            stmt = select(User).where(User.username == 'admin')
            result = await session.execute(stmt)
            admin_user = result.scalar_one_or_none()

            if not admin_user:
                # 2. 创建默认管理员 (user_id 也可以改为自增，这里暂时保留你原有的逻辑或改为自增)

                raw_password = "qiqi19900901"
                hashed_password = get_hash_password(raw_password)

                default_user = User(
                    user_id=1001,
                    username='admin',
                    password=hashed_password,
                    nickname='超级管理员',
                    gender='unknown',
                    bio='系统初始化的超级管理员账号',
                    avatar='https://fastly.jsdelivr.net/npm/@vant/assets/cat.jpeg',
                )

                session.add(default_user)
                await session.flush()  # 获取生成的 user_id

                actual_user_id = default_user.user_id  # 获取实际生成的 ID
                print(f"✅ 默认管理员用户已创建: username=admin, ID={actual_user_id}")

                # 👇 3. 【关键步骤】动态查找“超级管理员”角色并绑定
                # 不再硬编码 role_id=1，而是查名字
                role_stmt = select(Role).where(Role.role_name == "超级管理员")
                role_result = await session.execute(role_stmt)
                super_admin_role = role_result.scalar_one_or_none()

                if super_admin_role:
                    # 创建关联记录
                    user_role_link = UserRole(
                        user_id=actual_user_id,
                        role_id=super_admin_role.role_id  # 使用查到的真实 ID
                    )
                    session.add(user_role_link)
                    print(f"🔗 已将 admin 绑定到角色: {super_admin_role.role_name} (ID: {super_admin_role.role_id})")
                else:
                    print("⚠️ 警告: 未找到'超级管理员'角色，跳过绑定。")

                await session.commit()
                print(f"✅ 默认管理员初始化完毕 (密码: {raw_password})")

            else:
                print("ℹ️  默认管理员账号已存在，跳过创建。")

        except Exception as e:
            await session.rollback()
            print(f"❌ 用户种子数据插入失败: {e}")
            raise


async def main():
    print("🚀 开始初始化数据库...")
    await init_db_tables()
    await seed_default_roles()
    await seed_default_users()
    print("🎉 数据库初始化全部完成！")
    await async_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
