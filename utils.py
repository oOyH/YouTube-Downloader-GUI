"""
YouTube下载器工具函数
包含各种通用的工具函数和辅助方法
"""

import os
import re
import time
import subprocess
from datetime import datetime
from config import SUBPROCESS_FLAGS, QUALITY_CONFIG


def clean_filename(filename):
    """
    清理文件名中的非法字符
    
    Args:
        filename (str): 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)


def format_timestamp():
    """
    获取格式化的时间戳
    
    Returns:
        str: 格式化的时间戳字符串
    """
    return datetime.now().strftime('%Y%m%d_%H%M%S')


def build_format_spec(quality, format_type, audio_codec):
    """
    根据质量、格式类型和音频编码构建格式字符串
    
    Args:
        quality (str): 视频质量
        format_type (str): 格式类型
        audio_codec (str): 音频编码
        
    Returns:
        str: yt-dlp格式字符串
    """
    audio_formats = QUALITY_CONFIG['audio_formats']
    
    # 如果是仅音频
    if format_type == "仅音频":
        return audio_formats.get(audio_codec, "bestaudio")
    
    # 如果是自定义格式
    if quality == "自定义":
        return '248+251'  # 默认自定义格式
    
    # 如果是最佳质量
    if quality == "最佳质量":
        if format_type == "自动选择":
            return "bestvideo+bestaudio/best"
        elif format_type == "MP4 (H.264)":
            return f"bestvideo[ext=mp4]+{audio_formats.get(audio_codec, 'bestaudio')}/best[ext=mp4]"
        elif format_type == "WebM (VP9)":
            return f"bestvideo[ext=webm]+{audio_formats.get(audio_codec, 'bestaudio')}/best[ext=webm]"
        elif format_type == "MP4 (AV1)":
            return f"bestvideo[vcodec^=av01]+{audio_formats.get(audio_codec, 'bestaudio')}"
    
    # 质量到格式ID的映射
    quality_formats = QUALITY_CONFIG['quality_formats']
    
    if quality not in quality_formats:
        return "248+251"  # 默认1080p VP9
    
    video_formats = quality_formats[quality]
    audio_format = audio_formats.get(audio_codec, "251")
    
    # 根据格式类型选择视频格式
    if format_type == "自动选择":
        # 优先选择VP9，然后AV1，最后H.264
        for i, fmt in enumerate([1, 2, 0]):  # VP9, AV1, H.264
            if video_formats[fmt]:
                return f"{video_formats[fmt]}+{audio_format}"
        return f"{video_formats[1]}+{audio_format}"  # 默认VP9
    
    elif format_type == "MP4 (H.264)":
        video_fmt = video_formats[0]
        if not video_fmt:
            return f"bestvideo[ext=mp4]+{audio_format}/best[ext=mp4]"
        return f"{video_fmt}+{audio_format}"
    
    elif format_type == "WebM (VP9)":
        video_fmt = video_formats[1]
        if not video_fmt:
            return f"bestvideo[ext=webm]+{audio_format}/best[ext=webm]"
        return f"{video_fmt}+{audio_format}"
    
    elif format_type == "MP4 (AV1)":
        video_fmt = video_formats[2]
        if not video_fmt:
            return f"bestvideo[vcodec^=av01]+{audio_format}"
        return f"{video_fmt}+{audio_format}"
    
    # 默认返回
    return f"{video_formats[1]}+{audio_format}"


def build_yt_dlp_command(base_args, cookie_args=None, url=None, additional_args=None):
    """
    构建yt-dlp命令
    
    Args:
        base_args (list): 基础参数
        cookie_args (list, optional): Cookie相关参数
        url (str, optional): 视频URL
        additional_args (list, optional): 额外参数
        
    Returns:
        list: 完整的命令参数列表
    """
    command = ["yt-dlp"] + base_args
    
    if cookie_args:
        command.extend(cookie_args)
    
    if additional_args:
        command.extend(additional_args)
    
    if url:
        command.append(url)
    
    return command


def run_subprocess(command, capture_output=True, text=True, check=True):
    """
    运行子进程命令
    
    Args:
        command (list): 命令参数列表
        capture_output (bool): 是否捕获输出
        text (bool): 是否以文本模式处理
        check (bool): 是否检查返回码
        
    Returns:
        subprocess.CompletedProcess: 进程结果
    """
    return subprocess.run(
        command,
        capture_output=capture_output,
        text=text,
        check=check,
        creationflags=SUBPROCESS_FLAGS
    )


def normalize_url(url):
    """
    标准化YouTube URL
    
    Args:
        url (str): 原始URL或视频ID
        
    Returns:
        str: 标准化的YouTube URL
    """
    # 处理以'-'开头的视频ID
    if url.startswith('-'):
        return f"https://www.youtube.com/watch?v={url[1:]}"
    elif not url.startswith(('http://', 'https://')):
        return f"https://www.youtube.com/watch?v={url}"
    return url


def get_browser_profile_path(browser, appdata_local):
    """
    获取浏览器配置文件路径
    
    Args:
        browser (str): 浏览器名称
        appdata_local (str): 本地应用数据目录
        
    Returns:
        str: 浏览器配置文件路径
    """
    from config import BROWSER_CONFIG
    
    browser_profiles = BROWSER_CONFIG['browser_profiles']
    if browser in browser_profiles:
        return browser_profiles[browser](appdata_local)
    return None


def validate_file_exists(file_path, file_type="文件"):
    """
    验证文件是否存在
    
    Args:
        file_path (str): 文件路径
        file_type (str): 文件类型描述
        
    Returns:
        bool: 文件是否存在
        
    Raises:
        Exception: 文件不存在时抛出异常
    """
    if not file_path or not os.path.exists(file_path):
        raise Exception(f"{file_type}不存在: {file_path}")
    return True


def ensure_directory_exists(directory):
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory (str): 目录路径
        
    Returns:
        str: 目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return directory


def parse_video_id_from_url(url):
    """
    从YouTube URL中解析视频ID
    
    Args:
        url (str): YouTube URL
        
    Returns:
        str: 视频ID，如果解析失败返回None
    """
    patterns = [
        r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
        r'(?:embed\/)([0-9A-Za-z_-]{11})',
        r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None


def format_file_size(size_bytes):
    """
    格式化文件大小
    
    Args:
        size_bytes (int): 字节数
        
    Returns:
        str: 格式化的文件大小字符串
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def format_duration(seconds):
    """
    格式化时长
    
    Args:
        seconds (int): 秒数
        
    Returns:
        str: 格式化的时长字符串 (HH:MM:SS)
    """
    if not seconds:
        return "00:00"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    else:
        return f"{minutes:02d}:{seconds:02d}"
