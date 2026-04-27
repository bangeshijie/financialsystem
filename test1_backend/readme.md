uvicorn app.main:app --reload

#### 命名规范

###### 1. 蛇形命名法 (snake_case) —— Python 首选

适用场景：
变量名 (Variables)
函数名 (Functions)
模块名 (Modules / 文件名
包名 (Packages)
方法名 (Methods)

###### 2. 大驼峰命名法 (PascalCase / UpperCamelCase)

首字母大写，后续每个单词首字母也大写，中间无分隔符。
适用场景：
类名 (Classes)
异常类名 (Exceptions)
(注：在 Python 中几乎只用于这两处)

######  3. 小驼峰命名法 (camelCase)

首字母小写，后续每个单词首字母大写。
适用场景：
Python 中通常不推荐使用。
仅在为了兼容某些外部库（如 JavaScript 生成的 JSON 字段映射）或特定框架强制要求时才使用。
如果你看到 Python 代码里满篇的 getUserInfo，那通常被认为是不符合 Pythonic 风格的。

######  4. 全大写下划线命名法 (UPPER_CASE)

所有字母大写，单词间用下划线连接。
适用场景：
常量 (Constants)：指那些在程序运行期间不应该被修改的值。

###### 5. 特殊命名规范 (双下划线)

除了上述常规命名，Python 还有一些带有特殊含义的下划线用法：
命名形式	含义与用途	示例
_variable	内部使用 (Protected)：暗示该变量是“受保护的”，仅供类内部或子类使用，不应从外部直接访问（但这只是约定，Python 不强制）。	_internal_cache
__variable	名称修饰 (Private)：用于类中，Python 会对其进行名称改写（Name Mangling），使其难以从类外部直接访问，模拟“私有”属性。	__password
__method__	魔术方法 (Dunder methods)：Python 内置的特殊方法，由解释器调用。	__init__, __str__, __len__
_	临时变量：表示一个你不在乎的变量，或者在交互式解释器中保存上一次结果。	for _ in range(10): pass


#### alembic 的使用 
日常开发标准流程（三步走）
假设你现在的需求是：给 User 表增加一个 age 字段。
###### 第一步：修改代码（模型层）
在你的 modules/users/models.py (或类似文件) 中修改代码：



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    # ... 其他字段 ...
    
    # 1. 在这里添加新字段
    age = Column(Integer, nullable=True) 
###### 第二步：生成迁移脚本
在终端执行命令，让 Alembic 自动检测变化：



`alembic revision --autogenerate -m "add age column to user"`
结果：你会看到 Generating ...，说明脚本生成成功。
检查：Alembic 会尝试自动分析差异。虽然它很智能，但偶尔也会漏掉一些东西（比如外键约束或复杂的默认值），所以生成的脚本最好看一眼。
###### 第三步：执行迁移（同步到数据库）
将变更真正应用到 MySQL 数据库：


`alembic upgrade head`
结果：数据库里的 users 表现在多了一个 age 列。
###### 🛠️ 常用命令速查表
除了上面的流程，这几个命令是你以后最常用的：

| 命令	                                     | 作用	| 场景                        |
|-----------------------------------------|---|---------------------------|
| alembic revision --autogenerate -m "描述" |  自动生成迁移脚本|修改了 models.py 后使用 |
| alembic downgrade -1	                   |回滚上一个版本	| 发现刚才的修改有问题，想撤销时使用         |
| alembic current	                        |查看当前数据库版本	| 确认数据库现在是哪个版本              |
| alembic history	                        |查看迁移历史| 	查看所有修改记录                 |

表格

###### 💡 两个重要提示
1. 关于 --autogenerate 的局限性
Alembic 的自动检测功能很强，但不是万能的。
能检测到：新增表、新增列、修改列类型、删除列。
检测不到：
表名或列名的重命名（它会认为是删除旧列+新增新列，导致数据丢失）。
复杂的约束变更。
建议：生成脚本后，打开 alembic/versions/xxx_xxx.py 扫一眼，确保 upgrade() 和 downgrade() 逻辑是对的。
2. 多人协作场景
如果你和队友一起开发：
队友修改了模型并提交了代码（包含 alembic/versions/ 下的新脚本）。
你拉取代码后，只需要在本地执行：




`alembic upgrade head`

Alembic 会自动检测到你本地数据库缺哪些版本，并依次执行，把数据库结构同步到最新。

### sqlalchemy
SQLAlchemy 是一个 Python 数据库工具，用于数据库操作。
#### 1安装
#### 2用法
##### 联合唯一约束
联合唯一约束，即多个字段的组合必须唯一。
  举例:同一版本下会计科目代码必须唯一
`    __table_args__ = (
        UniqueConstraint('code', 'account_version_id', name='uq_account_code_version'),
    )`

