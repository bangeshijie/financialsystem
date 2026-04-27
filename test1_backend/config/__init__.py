# 先导入 Base
from config.base import Base

# 导入所有模型，触发它们注册到 Base 的过程

from modules.users.models import User,UserToken,UserRole,Role,Menu,RoleMenu

from modules.account.models import  Account
from modules.account_version.models import   AccountVersion

from modules.company.models import  Company

from modules.sale.models import City



# 导出方便外部使用
__all__ = ["Base",
           "User", "UserToken","UserRole","Role","Menu","RoleMenu",
           "AccountVersion",
           "Account",
           "Company",
           "City"]