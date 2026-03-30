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
