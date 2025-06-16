"""
YouTube下载器配置文件
包含应用程序的常量、默认设置和配置项
"""

import os
import platform
import subprocess

# 系统相关配置
IS_WINDOWS = platform.system() == 'Windows'

# 为Windows系统添加subprocess标志，防止命令窗口弹出
SUBPROCESS_FLAGS = 0
if IS_WINDOWS:
    SUBPROCESS_FLAGS = subprocess.CREATE_NO_WINDOW

# 默认下载目录
def get_default_download_dir():
    """
    获取默认下载目录
    返回当前工作目录下的download文件夹
    """
    download_path = os.path.join(os.getcwd(), "download")
    return download_path

# 应用程序配置
APP_CONFIG = {
    'window_title': 'YouTube 下载器',
    'window_size': (950, 900),
    'window_position': (100, 100),
    'icon_file': 'icon.ico',
    'log_font': ('Consolas', 9),
    'button_font': ('Arial', 12),
}

# 下载配置
DOWNLOAD_CONFIG = {
    'default_quality': '1080p',
    'default_format': '自动选择',
    'default_audio_codec': '最佳',
    'retry_count': 3,
    'socket_timeout': 30,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'delay_between_downloads': 5,  # 秒
}

# 浏览器配置
BROWSER_CONFIG = {
    'supported_browsers': ['Firefox', 'Chrome', 'Microsoft Edge'],
    'browser_map': {
        "Firefox": "firefox",
        "Chrome": "chrome", 
        "Microsoft Edge": "edge"
    },
    'browser_profiles': {
        "edge": lambda appdata: os.path.join(appdata, "Microsoft", "Edge", "User Data"),
        "chrome": lambda appdata: os.path.join(appdata, "Google", "Chrome", "User Data"),
        "firefox": lambda appdata: os.path.join(appdata, "Mozilla", "Firefox", "Profiles")
    }
}

# 质量和格式配置
QUALITY_CONFIG = {
    'quality_options': ["最佳质量", "8K", "4K", "1440p", "1080p", "720p", "480p", "360p", "自定义"],
    'format_options': ["自动选择", "MP4 (H.264)", "WebM (VP9)", "MP4 (AV1)", "仅音频"],
    'audio_codec_options': ["最佳", "Opus", "AAC"],
    
    # 质量到格式ID的映射 [H.264_ID, VP9_ID, AV1_ID]
    'quality_formats': {
        "8K": ["", "313", "401"],      # 2160p
        "4K": ["", "313", "401"],      # 2160p
        "1440p": ["", "271", "400"],   # 1440p
        "1080p": ["137", "248", "399"], # 1080p
        "720p": ["136", "247", "398"],  # 720p
        "480p": ["135", "244", "397"],  # 480p
        "360p": ["134", "243", "396"],  # 360p
        "240p": ["133", "242", "395"],  # 240p
    },
    
    # 音频格式映射
    'audio_formats': {
        "最佳": "bestaudio",
        "Opus": "251/250/249",  # Opus格式，按质量排序
        "AAC": "140"  # AAC格式
    }
}

# Cookie相关配置
COOKIE_CONFIG = {
    'important_cookies': [
        '__Secure-3PSID', 'SAPISID', 'HSID', 'SSID', 'APISID',
        'LOGIN_INFO', 'SID', '__Secure-3PAPISID'
    ],
    'cookie_file_headers': [
        "# Netscape HTTP Cookie File",
        "# HTTP Cookie File"
    ]
}

# UI样式配置
UI_STYLES = {
    'download_button': """
        QPushButton {
            background-color: #28a745;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #218838;
        }
        QPushButton:pressed {
            background-color: #1e7e34;
        }
        QPushButton:disabled {
            background-color: #6c757d;
            color: #ffffff;
        }
    """,
    
    'stop_button': """
        QPushButton {
            background-color: #dc3545;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
        }
        QPushButton:hover {
            background-color: #c82333;
        }
        QPushButton:pressed {
            background-color: #bd2130;
        }
        QPushButton:disabled {
            background-color: #6c757d;
            color: #ffffff;
        }
    """,
    
    'help_text': "color: #666; font-size: 11px;"
}

# 输出模板帮助文本
TEMPLATE_HELP_TEXT = """
输出模板变量说明：

基本变量：
%(title)s - 视频标题
%(id)s - 视频ID
%(ext)s - 文件扩展名
%(uploader)s - 上传者
%(upload_date)s - 上传日期 (YYYYMMDD)
%(duration)s - 视频时长（秒）
%(view_count)s - 观看次数
%(like_count)s - 点赞数

质量相关：
%(height)s - 视频高度
%(width)s - 视频宽度
%(fps)s - 帧率
%(vcodec)s - 视频编码
%(acodec)s - 音频编码

常用模板示例：
%(title)s.%(ext)s
%(uploader)s - %(title)s.%(ext)s
%(upload_date)s - %(title)s.%(ext)s
[%(id)s] %(title)s.%(ext)s
%(title)s [%(height)sp].%(ext)s

注意：
- 文件名中的特殊字符会被自动替换
- 建议至少包含 %(title)s 或 %(id)s
- 必须包含 %(ext)s 以确保正确的文件扩展名
"""

# 确保下载目录存在
DEFAULT_DOWNLOAD_DIR = get_default_download_dir()
os.makedirs(DEFAULT_DOWNLOAD_DIR, exist_ok=True)
