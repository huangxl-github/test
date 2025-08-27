# 许可证系统

一个功能完整的软件许可证管理系统，支持许可证的生成、验证和管理。

## 功能特性

### 许可证生成
- 支持多种许可证类型（试用版、正式版、专业版、企业版）
- 可自定义许可证有效期
- 生成唯一的许可证密钥，具备防伪造机制
- 支持批量生成许可证

### 许可证验证
- 支持在线验证和离线验证两种方式
- 验证许可证的有效性、格式、有效期等
- 提供明确的错误提示信息

### 许可证管理
- 管理员可创建、修改、吊销许可证
- 查看许可证的使用记录和状态
- 支持按产品ID、状态等条件查询许可证
- 具备审计功能，记录许可证的重要操作

### 安全特性
- 许可证密钥加密存储和传输
- 防止许可证被破解、篡改和复制
- 详细的操作日志记录

## 系统架构

- **数据模型层**：定义许可证相关的数据结构和枚举类型
- **生成器层**：负责创建和格式化许可证密钥
- **验证器层**：负责验证许可证的有效性
- **管理器层**：负责许可证的CRUD操作和持久化存储
- **存储层**：使用SQLite数据库存储许可证和审计日志

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用示例

```python
from datetime import datetime, timedelta
from src.models import LicenseType
from src.license_manager import LicenseManager

# 初始化许可证管理器
license_manager = LicenseManager(secret_key='your_secure_secret_key')

# 创建许可证
license = license_manager.create_license(
    license_type=LicenseType.PROFESSIONAL,
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=365),
    product_id="your_product_id",
    user_info={"company": "Your Company", "contact": "Your Contact"}
)

# 验证许可证
valid, message = license_manager.validator.validate_license_online(
    license_key=license.license_key,
    product_id="your_product_id",
    machine_info={"user_id": "user123", "machine_id": "machine456"}
)

# 批量创建许可证
batch_licenses = license_manager.batch_create_licenses(
    count=10,
    license_type=LicenseType.STANDARD,
    valid_years=1,
    product_id="your_product_id"
)

# 查询许可证
all_licenses = license_manager.get_all_licenses()
active_licenses = license_manager.get_all_licenses(status=LicenseStatus.ACTIVE)
```

### 运行示例

```bash
cd src
python -m main
```

### 运行测试

```bash
cd tests
python -m unittest discover
```

## 配置说明

系统配置文件位于 `config/settings.py`，可以根据需要修改以下配置：

- `SECRET_KEY`：用于加密许可证的密钥
- `DATABASE_PATH`：SQLite数据库文件路径
- `DEFAULT_TRIAL_DAYS`：默认试用期天数
- `DEFAULT_VALID_YEARS`：默认许可证有效期年数
- `ONLINE_VERIFICATION_ENABLED`：是否启用在线验证

## 安全建议

1. 生产环境中，请使用强密钥替换默认的 `SECRET_KEY`
2. 定期备份数据库文件
3. 考虑使用HTTPS协议进行在线验证通信
4. 根据实际需求调整 `MAX_ACTIVATION_COUNT` 和其他安全相关配置

## 开发说明

- 系统使用Python 3.7+开发
- 依赖库包括：cryptography, pycryptodome, python-dateutil, pysqlite3
- 遵循模块化设计原则，便于扩展和维护

## 项目结构

```
├── src/                # 源代码目录
│   ├── __init__.py     # 包初始化文件
│   ├── models.py       # 数据模型定义
│   ├── license_generator.py  # 许可证生成模块
│   ├── license_validator.py  # 许可证验证模块
│   ├── license_manager.py    # 许可证管理模块
│   └── main.py         # 主入口文件
├── tests/              # 测试目录
│   ├── test_license_generator.py  # 许可证生成器测试
│   ├── test_license_validator.py  # 许可证验证器测试
│   └── test_license_manager.py    # 许可证管理器测试
├── config/             # 配置目录
│   └── settings.py     # 系统配置文件
├── requirements.txt    # 项目依赖
└── README.md           # 项目说明文档
```