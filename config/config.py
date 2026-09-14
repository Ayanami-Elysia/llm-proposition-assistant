import os
import pymysql

# 应用配置
DEBUG = True
SECRET_KEY = 'your-secret-key-here'

# 数据库配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'database': '0_80205mingtifuzhu',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 上传文件配置
UPLOAD_FOLDER = 'upload'
# 允许的文件扩展名：图片格式
ALLOWED_EXTENSIONS_IMAGE = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp'}
# 允许的文件扩展名：文档格式
ALLOWED_EXTENSIONS_DOCUMENT = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt'}
# 所有允许的文件扩展名
ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS_IMAGE | ALLOWED_EXTENSIONS_DOCUMENT
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

# 会话配置
PERMANENT_SESSION_LIFETIME = 86400  # 24小时

# 文心一言静态配置
# 真实密钥不入库：优先读环境变量，其次读本地 config/config_local.py（已 gitignore）
WENXIN_API_KEY = os.environ.get('WENXIN_API_KEY', '')
WENXIN_SECRET_KEY = os.environ.get('WENXIN_SECRET_KEY', '')
WENXIN_BEARER_TOKEN = os.environ.get('WENXIN_BEARER_TOKEN', '')
WENXIN_OAUTH_URL = 'https://aip.baidubce.com/oauth/2.0/token'
# 千帆 v2 Bearer 直连地址
WENXIN_API_URL = 'https://qianfan.baidubce.com/v2/chat/completions'
# 默认模型（千帆 v2）
WENXIN_MODEL = os.environ.get('WENXIN_MODEL', 'ernie-3.5-8k')

try:
    from config.config_local import (  # noqa: F401
        WENXIN_API_KEY,
        WENXIN_SECRET_KEY,
        WENXIN_BEARER_TOKEN,
    )
except ImportError:
    pass
