"""
下载线程模块
处理YouTube视频下载的后台线程逻辑
"""

import os
import json
import subprocess
import time
import re
import threading
from PyQt5.QtCore import QThread, pyqtSignal as Signal, QMutex

from config import SUBPROCESS_FLAGS, DOWNLOAD_CONFIG
from utils import run_subprocess, normalize_url, clean_filename
from cookie_manager import CookieManager
from command_builder import CommandPresets, OptionsValidator


class DownloadThread(QThread):
    """优化的下载工作线程"""

    progress_update = Signal(str)
    download_complete = Signal()
    download_error = Signal(str)
    download_progress = Signal(int)  # 新增：下载进度百分比
    download_speed = Signal(str)     # 新增：下载速度
    eta_update = Signal(str)         # 新增：预计剩余时间
    
    def __init__(self, url, mode, options):
        super().__init__()
        self.url = url
        self.mode = mode  # 'single', 'date', 'range'
        self.options = options

        # 线程控制
        self._stop_requested = False
        self._mutex = QMutex()
        self._current_process = None

        # 初始化Cookie管理器
        self.cookie_manager = CookieManager()
        self._setup_cookie_manager()
        
    def _setup_cookie_manager(self):
        """设置Cookie管理器"""
        try:
            use_browser = self.options.get('use_browser', True)

            if use_browser:
                browser = self.options.get('browser', 'Firefox')
                self.cookie_manager.set_browser_mode(browser)
            else:
                cookie_file = self.options.get('cookie_file')
                if cookie_file:
                    self.cookie_manager.set_file_mode(cookie_file)
        except Exception as e:
            self.progress_update.emit(f"⚠️ Cookie设置警告: {str(e)}")
            # 使用默认浏览器模式
            self.cookie_manager.set_browser_mode('Firefox')
                
    def get_cookie_args(self):
        """获取Cookie参数"""
        try:
            if self.cookie_manager is None:
                self.progress_update.emit("⚠️ Cookie管理器未初始化，使用默认设置")
                return ["--cookies-from-browser", "firefox"]
            return self.cookie_manager.get_cookie_args()
        except Exception as e:
            self.progress_update.emit(f"⚠️ Cookie配置警告: {str(e)}，使用默认设置")
            return ["--cookies-from-browser", "firefox"]

    def request_stop(self):
        """请求停止下载"""
        self._mutex.lock()
        self._stop_requested = True
        if self._current_process:
            try:
                self._current_process.terminate()
            except:
                pass
        self._mutex.unlock()

    def is_stop_requested(self):
        """检查是否请求停止"""
        self._mutex.lock()
        result = self._stop_requested
        self._mutex.unlock()
        return result
            
    def get_playlist_info(self, url):
        """获取播放列表信息"""
        try:
            # 构建简单的命令
            from utils import build_yt_dlp_command
            command = build_yt_dlp_command(
                base_args=["-J", "--flat-playlist"],
                cookie_args=self.get_cookie_args(),
                url=url
            )
            self.progress_update.emit(f"执行命令: {' '.join(command)}")
            result = run_subprocess(command)
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            error_msg = f"命令执行失败: {e}\n"
            if e.stderr:
                error_msg += f"错误输出: {e.stderr}\n"
            if e.stdout:
                error_msg += f"标准输出: {e.stdout}"
            self.progress_update.emit(error_msg)
            return None
        except json.JSONDecodeError:
            self.progress_update.emit("无法解析 JSON 输出")
            return None
        except Exception as e:
            self.progress_update.emit(f"获取播放列表信息时出错: {str(e)}")
            return None
            
    def get_video_info(self, url):
        """获取视频信息"""
        try:
            # 构建简单的命令
            from utils import build_yt_dlp_command
            command = build_yt_dlp_command(
                base_args=[
                    "-F", "--verbose", "--no-check-certificates", "--no-playlist",
                    "--extractor-retries", str(DOWNLOAD_CONFIG['retry_count']),
                    "--socket-timeout", str(DOWNLOAD_CONFIG['socket_timeout'])
                ],
                cookie_args=self.get_cookie_args(),
                url=url
            )
            self.progress_update.emit(f"执行命令: {' '.join(command)}")
            result = run_subprocess(command)
            
            # 从格式列表输出中解析视频信息
            video_info = {'formats': []}
            title = None
            
            for line in result.stdout.split('\n'):
                # 尝试从输出中提取标题
                if '[info] ' in line and ': ' in line:
                    info_parts = line.split(': ', 1)
                    if len(info_parts) == 2:
                        title = info_parts[1].strip()
                        video_info['title'] = title
                        continue
                        
                # 解析格式信息
                if line.strip() and not line.startswith('[') and 'ID' not in line and '---' not in line:
                    parts = line.split()
                    if len(parts) >= 3:
                        format_id = parts[0]
                        format_info = {
                            'format_id': format_id,
                            'ext': 'mp4',  # 默认扩展名
                        }
                        video_info['formats'].append(format_info)
                        
            if not title:
                # 如果无法从输出中获取标题，使用视频ID
                from utils import parse_video_id_from_url
                video_id = parse_video_id_from_url(url)
                video_info['title'] = f'video_{video_id}' if video_id else 'unknown_video'
                
            return video_info
            
        except subprocess.CalledProcessError as e:
            error_msg = f"命令执行失败: {e}\n"
            if e.stderr:
                error_msg += f"错误输出: {e.stderr}\n"
            if e.stdout:
                error_msg += f"标准输出: {e.stdout}"
            self.progress_update.emit(error_msg)
            return None
        except Exception as e:
            self.progress_update.emit(f"发生未知错误: {str(e)}")
            return None
            
    def download_video(self, url, title, format_choice="1080p"):
        """下载视频"""
        # 标准化URL
        url = normalize_url(url)

        try:
            # 更新格式选择
            options = self.options.copy()
            options['format_choice'] = format_choice

            # 构建下载命令 - 使用简化的方式
            from utils import build_format_spec, build_yt_dlp_command
            import os

            # 获取格式类型和音频编码偏好
            format_type = options.get('format_type', '自动选择')
            audio_codec = options.get('audio_codec', '最佳')

            # 根据格式类型构建格式字符串
            if format_choice == '自定义':
                format_spec = options.get('custom_format', '248+251')
            else:
                format_spec = build_format_spec(format_choice, format_type, audio_codec)

            # 构建下载命令基础参数
            base_args = [
                "-f", format_spec,
                "--no-check-certificates",
                "--no-playlist",
                "--extractor-retries", str(DOWNLOAD_CONFIG['retry_count']),
                "--socket-timeout", str(DOWNLOAD_CONFIG['socket_timeout']),
                "--user-agent", DOWNLOAD_CONFIG['user_agent']
            ]

            # 添加下载目录
            download_dir = options.get('download_dir', os.path.join(os.getcwd(), "download"))
            if not os.path.exists(download_dir):
                os.makedirs(download_dir, exist_ok=True)

            # 添加输出模板
            if options.get('output_template'):
                output_template = os.path.join(download_dir, options['output_template'])
            else:
                output_template = os.path.join(download_dir, "%(title)s.%(ext)s")
            base_args.extend(['-o', output_template])

            # 添加下载归档
            if options.get('download_archive'):
                base_args.extend(['--download-archive', options['download_archive']])

            # 构建完整命令
            command = build_yt_dlp_command(
                base_args=base_args,
                cookie_args=self.get_cookie_args(),
                url=url
            )
            
            # 执行下载
            self.progress_update.emit(f"开始下载: {title}")
            self.progress_update.emit(f"执行命令: {' '.join(command)}")

            self._mutex.lock()
            self._current_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=SUBPROCESS_FLAGS
            )
            process = self._current_process
            self._mutex.unlock()

            # 实时输出下载进度
            while True:
                if self.is_stop_requested():
                    process.terminate()
                    self.progress_update.emit("⏹️ 下载已取消")
                    return

                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    line = line.strip()
                    self._parse_progress_line(line)
                    self.progress_update.emit(line)

            if process.returncode == 0:
                self.progress_update.emit("✅ 视频下载完成")
            else:
                if not self.is_stop_requested():
                    self.download_error.emit("下载失败")
                
        except Exception as e:
            self.download_error.emit(f"下载出错: {str(e)}")
            if hasattr(e, 'stderr') and e.stderr:
                self.progress_update.emit(f"错误输出: {e.stderr}")

    def _parse_progress_line(self, line):
        """解析下载进度行"""
        try:
            # 解析下载进度百分比
            if '[download]' in line and '%' in line:
                # 匹配进度百分比
                progress_match = re.search(r'(\d+(?:\.\d+)?)%', line)
                if progress_match:
                    progress = float(progress_match.group(1))
                    self.download_progress.emit(int(progress))

                # 匹配下载速度
                speed_match = re.search(r'at\s+([0-9.]+[KMG]?iB/s)', line)
                if speed_match:
                    speed = speed_match.group(1)
                    self.download_speed.emit(speed)

                # 匹配预计剩余时间
                eta_match = re.search(r'ETA\s+([0-9:]+)', line)
                if eta_match:
                    eta = eta_match.group(1)
                    self.eta_update.emit(eta)

        except Exception:
            # 忽略解析错误，不影响主要功能
            pass
                
    def run(self):
        """线程主运行方法"""
        try:
            if self.mode == 'single':
                self._download_single_video()
            elif self.mode == 'date':
                self._download_by_date()
            elif self.mode == 'range':
                self._download_by_range()
                
            self.download_complete.emit()
            
        except Exception as e:
            self.download_error.emit(str(e))
            
    def _download_single_video(self):
        """下载单个视频"""
        try:
            # 获取视频信息
            video_info = self.get_video_info(self.url)
            if not video_info:
                self.download_error.emit("无法获取视频信息")
                return

            # 获取视频标题
            title = video_info.get('title', 'video')
            title = clean_filename(title)

            # 获取格式选择
            format_choice = self.options.get('format_choice', '1080p')
            if format_choice == '自定义':
                format_choice = self.options.get('custom_format', '1080p')

            # 下载视频
            self.download_video(self.url, title, format_choice)
        except Exception as e:
            self.download_error.emit(f"下载过程中出错: {str(e)}")
        
    def _download_by_date(self):
        """按日期下载播放列表视频"""
        # 获取播放列表信息
        self.progress_update.emit("正在获取播放列表信息...")
        playlist_info = self.get_playlist_info(self.url)
        if not playlist_info or not playlist_info.get('entries'):
            self.download_error.emit("无法获取播放列表信息")
            return
            
        self.progress_update.emit(f"播放列表信息已获取，共包含 {len(playlist_info.get('entries', []))} 个视频")
        
        # 根据日期过滤视频
        date_after = self.options.get('date_after')
        format_choice = self.options.get('format_choice', '1080p')
        if format_choice == '自定义':
            format_choice = self.options.get('custom_format', '1080p')
            
        downloaded_count = 0
        for i, entry in enumerate(playlist_info['entries']):
            try:
                video_id = entry.get('id')
                if not video_id:
                    continue
                    
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                
                # 获取视频详细信息
                video_info = self.get_video_info(video_url)
                if not video_info:
                    self.progress_update.emit(f"跳过视频 {video_url}：无法获取视频信息")
                    continue
                    
                # 获取标题
                title = video_info.get('title', f'video_{video_id}')
                title = clean_filename(title)
                
                # 检查上传日期
                upload_date = video_info.get('upload_date', '')
                if upload_date and upload_date >= date_after:
                    self.progress_update.emit(f"正在下载第 {downloaded_count + 1} 个视频: {title}")
                    self.download_video(video_url, title, format_choice)
                    downloaded_count += 1
                    
                    # 添加延迟避免被限制
                    if downloaded_count < len(playlist_info['entries']):
                        self.progress_update.emit(f"等待{DOWNLOAD_CONFIG['delay_between_downloads']}秒后继续下载下一个视频...")
                        time.sleep(DOWNLOAD_CONFIG['delay_between_downloads'])
                else:
                    self.progress_update.emit(f"跳过视频 {title}：不在指定日期范围内")
                    
            except Exception as e:
                self.progress_update.emit(f"下载视频时出错: {str(e)}")
                continue
                
        self.progress_update.emit(f"按日期下载完成，共下载了 {downloaded_count} 个视频")
        
    def _download_by_range(self):
        """按范围下载播放列表视频"""
        # 获取播放列表信息
        self.progress_update.emit("正在获取播放列表信息...")
        playlist_info = self.get_playlist_info(self.url)
        if not playlist_info or not playlist_info.get('entries'):
            self.download_error.emit("无法获取播放列表信息")
            return
            
        self.progress_update.emit(f"播放列表信息已获取，共包含 {len(playlist_info.get('entries', []))} 个视频")
        
        # 根据范围下载视频
        start_index = self.options.get('start_index', 0)
        count = self.options.get('count', 1)
        
        # 检查索引范围
        total_videos = len(playlist_info['entries'])
        if start_index >= total_videos:
            self.download_error.emit(f"起始序号 {start_index + 1} 超出了播放列表范围（共 {total_videos} 个视频）")
            return
            
        # 计算实际下载范围
        end_index = min(start_index + count, total_videos)
        entries = playlist_info['entries'][start_index:end_index]
        
        format_choice = self.options.get('format_choice', '1080p')
        if format_choice == '自定义':
            format_choice = self.options.get('custom_format', '1080p')
            
        self.progress_update.emit(f"准备下载第 {start_index + 1} 到第 {end_index} 个视频，共 {len(entries)} 个")
        
        for i, entry in enumerate(entries):
            try:
                video_id = entry.get('id')
                if not video_id:
                    continue
                    
                video_url = f"https://www.youtube.com/watch?v={video_id}"
                video_info = self.get_video_info(video_url)
                if video_info:
                    title = video_info.get('title', f'video_{video_id}')
                    title = clean_filename(title)
                    
                    self.progress_update.emit(f"正在下载第 {i + 1}/{len(entries)} 个视频: {title}")
                    self.download_video(video_url, title, format_choice)
                    
                    # 添加延迟避免被限制
                    if i < len(entries) - 1:
                        self.progress_update.emit(f"等待{DOWNLOAD_CONFIG['delay_between_downloads']}秒后继续下载下一个视频...")
                        time.sleep(DOWNLOAD_CONFIG['delay_between_downloads'])
                else:
                    self.progress_update.emit(f"跳过视频 {video_url}：无法获取视频信息")
                    
            except Exception as e:
                self.progress_update.emit(f"下载视频时出错: {str(e)}")
                continue
                
        self.progress_update.emit(f"按范围下载完成，共下载了 {len(entries)} 个视频")
