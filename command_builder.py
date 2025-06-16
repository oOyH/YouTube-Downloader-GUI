"""
命令构建器
统一yt-dlp命令构建逻辑，减少重复代码
"""

import os
from config import DOWNLOAD_CONFIG
from utils import build_format_spec, ensure_directory_exists


class YtDlpCommandBuilder:
    """yt-dlp命令构建器"""
    
    def __init__(self):
        self.reset()
        
    def reset(self):
        """重置构建器"""
        self.base_args = ["yt-dlp"]
        self.cookie_args = []
        self.format_args = []
        self.output_args = []
        self.misc_args = []
        self.url = None
        
    def with_cookies(self, cookie_manager):
        """添加Cookie参数"""
        try:
            self.cookie_args = cookie_manager.get_cookie_args()
        except Exception as e:
            raise Exception(f"Cookie配置错误: {str(e)}")
        return self
        
    def with_format(self, quality, format_type, audio_codec, custom_format=None):
        """添加格式参数"""
        if quality == "自定义" and custom_format:
            format_spec = custom_format
        else:
            format_spec = build_format_spec(quality, format_type, audio_codec)
            
        self.format_args = ["-f", format_spec]
        return self
        
    def with_output(self, download_dir, output_template=None, download_archive=None):
        """添加输出参数"""
        # 确保下载目录存在
        ensure_directory_exists(download_dir)
        
        # 设置输出模板
        if output_template:
            template = os.path.join(download_dir, output_template)
        else:
            template = os.path.join(download_dir, "%(title)s.%(ext)s")
            
        self.output_args = ['-o', template]
        
        # 添加下载归档
        if download_archive:
            self.output_args.extend(['--download-archive', download_archive])
            
        return self
        
    def with_basic_options(self):
        """添加基础选项"""
        self.misc_args.extend([
            "--no-check-certificates",
            "--no-playlist",
            "--extractor-retries", str(DOWNLOAD_CONFIG['retry_count']),
            "--socket-timeout", str(DOWNLOAD_CONFIG['socket_timeout']),
            "--user-agent", DOWNLOAD_CONFIG['user_agent']
        ])
        return self
        
    def with_info_only(self):
        """仅获取信息模式"""
        self.misc_args.extend(["-J", "--flat-playlist"])
        return self
        
    def with_format_list(self):
        """获取格式列表模式"""
        self.misc_args.extend([
            "-F", "--verbose", "--no-warnings", "--no-playlist"
        ])
        return self
        
    def with_playlist_options(self, start_index=None, end_index=None, date_after=None):
        """添加播放列表选项"""
        if start_index is not None:
            self.misc_args.extend(["--playlist-start", str(start_index + 1)])
            
        if end_index is not None:
            self.misc_args.extend(["--playlist-end", str(end_index)])
            
        if date_after:
            self.misc_args.extend(["--dateafter", date_after])
            
        return self
        
    def with_url(self, url):
        """设置URL"""
        self.url = url
        return self
        
    def build(self):
        """构建最终命令"""
        if not self.url:
            raise ValueError("URL不能为空")
            
        command = self.base_args.copy()
        command.extend(self.format_args)
        command.extend(self.misc_args)
        command.extend(self.cookie_args)
        command.extend(self.output_args)
        command.append(self.url)
        
        return command
        
    def build_info_command(self, url, cookie_manager):
        """构建信息获取命令"""
        return (self.reset()
                .with_cookies(cookie_manager)
                .with_info_only()
                .with_url(url)
                .build())
                
    def build_format_command(self, url, cookie_manager):
        """构建格式列表命令"""
        return (self.reset()
                .with_cookies(cookie_manager)
                .with_format_list()
                .with_url(url)
                .build())
                
    def build_download_command(self, url, options, cookie_manager):
        """构建下载命令"""
        builder = (self.reset()
                  .with_cookies(cookie_manager)
                  .with_basic_options())
                  
        # 添加格式选项
        quality = options.get('format_choice', '1080p')
        format_type = options.get('format_type', '自动选择')
        audio_codec = options.get('audio_codec', '最佳')
        custom_format = options.get('custom_format')
        
        builder.with_format(quality, format_type, audio_codec, custom_format)
        
        # 添加输出选项
        download_dir = options.get('download_dir', os.path.join(os.getcwd(), "download"))
        output_template = options.get('output_template')
        download_archive = options.get('download_archive')
        
        builder.with_output(download_dir, output_template, download_archive)
        
        # 添加播放列表选项
        if 'start_index' in options or 'date_after' in options:
            start_index = options.get('start_index')
            count = options.get('count')
            end_index = start_index + count if start_index is not None and count else None
            date_after = options.get('date_after')
            
            builder.with_playlist_options(start_index, end_index, date_after)
            
        return builder.with_url(url).build()


class CommandPresets:
    """命令预设"""
    
    @staticmethod
    def get_video_info(url, cookie_manager):
        """获取视频信息的预设命令"""
        builder = YtDlpCommandBuilder()
        return builder.build_info_command(url, cookie_manager)
        
    @staticmethod
    def get_format_list(url, cookie_manager):
        """获取格式列表的预设命令"""
        builder = YtDlpCommandBuilder()
        return builder.build_format_command(url, cookie_manager)
        
    @staticmethod
    def download_single_video(url, options, cookie_manager):
        """下载单个视频的预设命令"""
        builder = YtDlpCommandBuilder()
        return builder.build_download_command(url, options, cookie_manager)
        
    @staticmethod
    def download_playlist_by_range(url, start_index, count, options, cookie_manager):
        """按范围下载播放列表的预设命令"""
        range_options = options.copy()
        range_options.update({
            'start_index': start_index,
            'count': count
        })
        
        builder = YtDlpCommandBuilder()
        return builder.build_download_command(url, range_options, cookie_manager)
        
    @staticmethod
    def download_playlist_by_date(url, date_after, options, cookie_manager):
        """按日期下载播放列表的预设命令"""
        date_options = options.copy()
        date_options.update({
            'date_after': date_after
        })
        
        builder = YtDlpCommandBuilder()
        return builder.build_download_command(url, date_options, cookie_manager)
        
    @staticmethod
    def test_cookie_access(cookie_manager):
        """测试Cookie访问的预设命令"""
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        builder = YtDlpCommandBuilder()
        command = builder.reset()
        command.with_cookies(cookie_manager)
        command.misc_args.extend(["-J", "--no-warnings", "--no-playlist"])
        command.url = test_url
        return command.build()


class OptionsValidator:
    """选项验证器"""
    
    @staticmethod
    def validate_download_options(options):
        """验证下载选项"""
        errors = []
        
        # 验证下载目录
        download_dir = options.get('download_dir')
        if not download_dir:
            errors.append("下载目录不能为空")
        elif not os.path.exists(os.path.dirname(download_dir)):
            errors.append(f"下载目录的父目录不存在: {os.path.dirname(download_dir)}")
            
        # 验证自定义格式
        if options.get('format_choice') == '自定义':
            custom_format = options.get('custom_format', '').strip()
            if not custom_format:
                errors.append("自定义格式不能为空")
            elif not OptionsValidator._is_valid_format_spec(custom_format):
                errors.append("自定义格式格式不正确")
                
        # 验证下载归档文件
        archive_file = options.get('download_archive')
        if archive_file:
            archive_dir = os.path.dirname(archive_file)
            if archive_dir and not os.path.exists(archive_dir):
                errors.append(f"下载归档文件目录不存在: {archive_dir}")
                
        return errors
        
    @staticmethod
    def validate_cookie_options(options):
        """验证Cookie选项"""
        errors = []
        
        use_browser = options.get('use_browser', True)
        if not use_browser:
            cookie_file = options.get('cookie_file')
            if not cookie_file:
                errors.append("请选择Cookie文件")
            elif not os.path.exists(cookie_file):
                errors.append(f"Cookie文件不存在: {cookie_file}")
                
        return errors
        
    @staticmethod
    def _is_valid_format_spec(format_spec):
        """验证格式规格是否有效"""
        # 简单的格式验证
        if not format_spec:
            return False
            
        # 检查是否包含有效的格式ID或格式表达式
        valid_patterns = [
            r'^\d+$',  # 纯数字ID
            r'^\d+\+\d+$',  # 视频+音频格式
            r'^best',  # best开头的表达式
            r'^worst',  # worst开头的表达式
            r'^\w+\[',  # 带条件的表达式
        ]
        
        import re
        for pattern in valid_patterns:
            if re.match(pattern, format_spec):
                return True
                
        return False
        
    @staticmethod
    def validate_all_options(options):
        """验证所有选项"""
        errors = []
        errors.extend(OptionsValidator.validate_download_options(options))
        errors.extend(OptionsValidator.validate_cookie_options(options))
        return errors
