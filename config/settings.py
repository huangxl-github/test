# 许可证系统配置文件

# 加密配置
SECRET_KEY = "your_secure_secret_key_here"  # 实际应用中应使用安全的密钥
ENCRYPTION_ALGORITHM = "AES-256-CBC"

# 数据库配置
DATABASE_PATH = "licenses.db"  # SQLite数据库路径

# 许可证配置
DEFAULT_TRIAL_DAYS = 30  # 默认试用期天数
DEFAULT_VALID_YEARS = 1  # 默认许可证有效期年数
MAX_ACTIVATION_COUNT = 5  # 单个许可证最大激活次数

# 日志配置
LOG_LEVEL = "INFO"
LOG_FILE = "license_system.log"

# 在线验证配置
ONLINE_VERIFICATION_ENABLED = True
VERIFICATION_SERVER_URL = "https://license.yourcompany.com/verify"  # 在线验证服务器URL

# API配置
API_KEY = "your_api_key_here"  # 实际应用中应使用安全的API密钥
API_RATE_LIMIT = 100  # 每分钟最大API请求次数

# 安全配置
REQUIRE_ONLINE_VERIFICATION = False  # 是否强制要求在线验证
IP_BINDING_ENABLED = False  # 是否启用IP绑定
MACHINE_FINGERPRINT_ENABLED = True  # 是否启用机器指纹