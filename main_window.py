"""
主窗口模块
包含应用程序的主窗口类和相关逻辑
"""

import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QFileDialog, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from config import APP_CONFIG, UI_STYLES
from ui_components import (
    URLInputGroup, DownloadModeGroup, QualityFormatGroup,
    CookieSourceGroup, OutputOptionsGroup, LogDisplayGroup
)
from progress_widget import ProgressWidget, BatchProgressWidget, StatusIndicator
from download_thread import DownloadThread
from cookie_manager import CookieManager
from config_manager import ConfigManager, OptionsBuilder, SessionManager
from command_builder import CommandPresets
from utils import run_subprocess


class YouTubeDownloaderMainWindow(QMainWindow):
    """YouTube下载器主窗口"""
    
    def __init__(self):
        super().__init__()
        self.download_thread = None
        self.cookie_manager = CookieManager()
        self.config_manager = ConfigManager()
        self.session_manager = SessionManager()
        self.setup_ui()
        self.connect_signals()
        self.load_saved_settings()
        
    def setup_ui(self):
        """设置用户界面"""
        # 设置窗口属性
        self.setWindowTitle(APP_CONFIG['window_title'])
        self.setGeometry(*APP_CONFIG['window_position'], *APP_CONFIG['window_size'])
        
        # 设置应用图标
        if os.path.exists(APP_CONFIG['icon_file']):
            self.setWindowIcon(QIcon(APP_CONFIG['icon_file']))
            
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建滚动内容部件
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)
        
        # 创建主布局
        main_layout = QVBoxLayout(scroll_content)
        
        # 将滚动区域设置为中央部件的内容
        central_layout = QVBoxLayout(central_widget)
        central_layout.addWidget(scroll_area)
        
        # 创建UI组件
        self.url_group = URLInputGroup()
        main_layout.addWidget(self.url_group)
        
        # 创建并排的输出选项和流媒体选项区域
        options_row_layout = QHBoxLayout()
        self.output_group = OutputOptionsGroup()
        
        # 流媒体选项暂时简化，后续可以扩展
        # self.streaming_group = StreamingOptionsGroup()
        
        options_row_layout.addWidget(self.output_group)
        # options_row_layout.addWidget(self.streaming_group)
        main_layout.addLayout(options_row_layout)
        
        # 下载模式选择
        self.mode_group = DownloadModeGroup()
        main_layout.addWidget(self.mode_group)
        
        # 创建并排的视频质量和Cookie来源区域
        quality_cookie_row_layout = QHBoxLayout()
        self.quality_group = QualityFormatGroup()
        self.cookie_group = CookieSourceGroup()
        
        quality_cookie_row_layout.addWidget(self.quality_group)
        quality_cookie_row_layout.addWidget(self.cookie_group)
        main_layout.addLayout(quality_cookie_row_layout)
        
        # 下载控制按钮区域
        self.setup_download_buttons(main_layout)

        # 进度显示区域
        self.progress_widget = ProgressWidget()
        main_layout.addWidget(self.progress_widget)

        # 批量进度显示区域
        self.batch_progress_widget = BatchProgressWidget()
        main_layout.addWidget(self.batch_progress_widget)

        # 状态指示器
        status_layout = QHBoxLayout()
        self.status_indicator = StatusIndicator()
        status_layout.addWidget(self.status_indicator)
        status_layout.addStretch()
        main_layout.addLayout(status_layout)

        # 日志显示区域
        self.log_group = LogDisplayGroup()
        main_layout.addWidget(self.log_group)
        
    def setup_download_buttons(self, main_layout):
        """设置下载控制按钮"""
        button_layout = QHBoxLayout()
        
        # 下载/停止按钮
        self.download_button = QPushButton("开始下载")
        self.download_button.setFont(QFont(*APP_CONFIG['button_font'], QFont.Bold))
        self.download_button.setMinimumHeight(40)
        self.download_button.setMinimumWidth(120)
        self.download_button.setStyleSheet(UI_STYLES['download_button'])
        
        # 停止按钮
        self.stop_button = QPushButton("停止下载")
        self.stop_button.setFont(QFont(*APP_CONFIG['button_font'], QFont.Bold))
        self.stop_button.setMinimumHeight(40)
        self.stop_button.setMinimumWidth(120)
        self.stop_button.setEnabled(False)
        self.stop_button.setStyleSheet(UI_STYLES['stop_button'])
        
        # 居中显示按钮
        button_layout.addStretch()
        button_layout.addWidget(self.download_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
    def connect_signals(self):
        """连接信号槽"""
        # 下载按钮
        self.download_button.clicked.connect(self.start_download)
        self.stop_button.clicked.connect(self.stop_download)
        
        # 输出选项
        self.output_group.dir_btn.clicked.connect(self.select_download_dir)
        
        # Cookie选项
        self.cookie_group.cookie_file_button.clicked.connect(self.select_cookie_file)
        self.cookie_group.export_cookie_btn.clicked.connect(self.export_cookie_from_browser)
        self.cookie_group.test_cookie_btn.clicked.connect(self.test_current_cookie)
        
        # 质量选项
        self.quality_group.formats_button.clicked.connect(self.show_formats)
        
        # 日志控制
        self.log_group.clear_log_btn.clicked.connect(self.log_group.clear_log)
        self.log_group.save_log_btn.clicked.connect(self.log_group.save_log)
        
    def select_download_dir(self):
        """选择下载目录"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "选择下载目录",
            self.output_group.dir_input.text()
        )
        if directory:
            self.output_group.dir_input.setText(directory)
            
    def select_cookie_file(self):
        """选择cookies.txt文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择 cookies.txt 文件",
            "",
            "Cookie文件 (*.txt);;所有文件 (*.*)"
        )
        if file_path:
            # 验证cookie文件格式
            validation_result = self.cookie_manager.validate_cookie_file(file_path)
            if validation_result['is_valid']:
                self.cookie_group.cookie_file_input.setText(file_path)
                QMessageBox.information(
                    self,
                    "Cookie文件验证成功",
                    "Cookie文件格式正确，包含必要的YouTube认证信息。"
                )
            else:
                # 获取详细的问题诊断
                suggestions = self.cookie_manager.get_cookie_suggestions(file_path)
                error_msg = "Cookie文件验证失败！\n\n问题诊断：\n"
                for i, suggestion in enumerate(suggestions, 1):
                    error_msg += f"{i}. {suggestion}\n"
                    
                error_msg += "\n解决方案：\n"
                error_msg += "1. 确保在YouTube上完全登录\n"
                error_msg += "2. 使用'Get cookies.txt LOCALLY'浏览器插件\n"
                error_msg += "3. 导出时选择'youtube.com'域名\n"
                error_msg += "4. 确保导出的是最新的cookie文件"
                
                QMessageBox.warning(self, "Cookie文件问题", error_msg)
                
    def export_cookie_from_browser(self):
        """显示从浏览器导出cookie的说明"""
        instructions = self.cookie_manager.export_cookie_instructions()
        QMessageBox.information(self, "Cookie导出说明", instructions)
        
    def test_current_cookie(self):
        """测试当前Cookie配置"""
        try:
            # 设置Cookie管理器
            cookie_options = self.cookie_group.get_cookie_options()
            if cookie_options['use_browser']:
                self.cookie_manager.set_browser_mode(cookie_options['browser'])
            else:
                cookie_file = cookie_options.get('cookie_file')
                if not cookie_file:
                    QMessageBox.warning(self, "测试失败", "请先选择Cookie文件")
                    return
                self.cookie_manager.set_file_mode(cookie_file)
                
            # 执行测试
            def progress_callback(message):
                self.log_group.append_log(message)
                
            result = self.cookie_manager.test_cookie_validity(progress_callback)
            
            if result['success']:
                QMessageBox.information(self, "测试成功", result['message'])
            else:
                error_msg = result['message']
                if result['details']:
                    error_msg += "\n\n详细信息：\n" + "\n".join(result['details'])
                QMessageBox.warning(self, "测试失败", error_msg)
                
        except Exception as e:
            QMessageBox.critical(self, "测试出错", f"测试过程中出错：\n{str(e)}")
            
    def show_formats(self):
        """显示可用格式"""
        url = self.url_group.get_url()
        if not url:
            QMessageBox.warning(self, "提示", "请先输入视频URL")
            return
            
        try:
            # 设置Cookie管理器
            cookie_options = self.cookie_group.get_cookie_options()
            if cookie_options['use_browser']:
                self.cookie_manager.set_browser_mode(cookie_options['browser'])
            else:
                cookie_file = cookie_options.get('cookie_file')
                if cookie_file:
                    self.cookie_manager.set_file_mode(cookie_file)

            # 构建命令
            from utils import build_yt_dlp_command
            command = build_yt_dlp_command(
                base_args=["-F", "--no-warnings", "--no-playlist"],
                cookie_args=self.cookie_manager.get_cookie_args(),
                url=url
            )
            
            self.log_group.append_log("🔍 正在获取可用格式...")
            self.log_group.append_log(f"执行命令: {' '.join(command)}")
            
            # 执行命令
            result = run_subprocess(command, check=False)
            
            if result.returncode == 0:
                self.log_group.append_log("✅ 格式信息获取成功：")
                self.log_group.append_log(result.stdout)
            else:
                self.log_group.append_log("❌ 格式信息获取失败：")
                if result.stderr:
                    self.log_group.append_log(result.stderr)
                    
        except Exception as e:
            QMessageBox.critical(self, "获取格式失败", f"获取格式信息时出错：\n{str(e)}")
            
    def start_download(self):
        """开始下载"""
        url = self.url_group.get_url()
        if not url:
            QMessageBox.warning(self, "提示", "请输入视频URL")
            return

        try:
            # 收集所有选项 - 简化版本，避免复杂的构建器
            mode = self.mode_group.get_mode()
            mode_options = self.mode_group.get_mode_options()
            quality_options = self.quality_group.get_quality_options()
            cookie_options = self.cookie_group.get_cookie_options()
            output_options = self.output_group.get_output_options()

            # 合并所有选项
            options = {}
            options.update(mode_options)
            options.update(quality_options)
            options.update(cookie_options)
            options.update(output_options)
            
            # 创建下载线程
            self.download_thread = DownloadThread(url, mode, options)
            self.download_thread.progress_update.connect(self.log_group.append_log)
            self.download_thread.download_complete.connect(self.on_download_complete)
            self.download_thread.download_error.connect(self.on_download_error)

            # 连接新的进度信号
            self.download_thread.download_progress.connect(self.progress_widget.update_progress)
            self.download_thread.download_speed.connect(self.progress_widget.update_speed)
            self.download_thread.eta_update.connect(self.progress_widget.update_eta)
            
            # 更新UI状态
            self.download_button.setEnabled(False)
            self.download_button.setText("下载中...")
            self.stop_button.setEnabled(True)

            # 显示进度组件
            if mode in ['date', 'range']:
                # 批量下载模式
                estimated_count = self._estimate_download_count(mode, mode_options)
                self.batch_progress_widget.start_batch(estimated_count)
            else:
                # 单个下载模式
                self.progress_widget.show_progress()

            self.status_indicator.set_downloading()

            # 开始下载
            self.download_thread.start()
            self.log_group.append_log("🚀 开始下载任务...")
            
        except Exception as e:
            QMessageBox.critical(self, "启动下载失败", f"启动下载时出错：\n{str(e)}")
            self.reset_download_buttons()
            
    def stop_download(self):
        """停止下载"""
        if self.download_thread and self.download_thread.isRunning():
            self.log_group.append_log("🛑 正在停止下载...")

            # 使用优雅的停止方法
            self.download_thread.request_stop()
            self.download_thread.wait(5000)  # 等待5秒

            if self.download_thread.isRunning():
                self.download_thread.terminate()
                self.download_thread.wait(2000)
                if self.download_thread.isRunning():
                    self.download_thread.kill()
                    self.log_group.append_log("⚠️ 强制停止下载")
                else:
                    self.log_group.append_log("✅ 下载已停止")
            else:
                self.log_group.append_log("✅ 下载已停止")

            # 更新进度组件状态
            self.progress_widget.set_cancelled()
            self.batch_progress_widget.set_cancelled()
            self.status_indicator.set_cancelled()

            self.reset_download_buttons()
            self.download_thread = None
            
    def on_download_complete(self):
        """下载完成处理"""
        self.log_group.append_log("🎉 所有下载任务完成！")

        # 更新进度组件状态
        self.progress_widget.set_completed()
        self.batch_progress_widget.finish_batch()
        self.status_indicator.set_completed()

        self.reset_download_buttons()
        self.download_thread = None

    def on_download_error(self, error_message):
        """下载错误处理"""
        self.log_group.append_log(f"❌ 下载出错: {error_message}")

        # 更新进度组件状态
        self.progress_widget.set_error(error_message)
        self.batch_progress_widget.set_error(error_message)
        self.status_indicator.set_error()

        QMessageBox.critical(self, "下载错误", f"下载过程中出错：\n{error_message}")
        self.reset_download_buttons()
        self.download_thread = None

    def reset_download_buttons(self):
        """重置下载按钮状态"""
        self.download_button.setEnabled(True)
        self.download_button.setText("开始下载")
        self.stop_button.setEnabled(False)

        # 延迟隐藏进度组件
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(3000, self.progress_widget.hide_progress)

    def _estimate_download_count(self, mode, options):
        """估算下载数量"""
        if mode == 'range':
            return options.get('count', 1)
        elif mode == 'date':
            return 10  # 默认估算值，实际会在获取播放列表后更新
        return 1

    def load_saved_settings(self):
        """加载保存的设置"""
        try:
            # 加载下载设置
            download_options = self.config_manager.get_download_options()
            self.output_group.dir_input.setText(download_options.get('directory', ''))
            self.output_group.template_input.setText(download_options.get('output_template', ''))

            # 设置质量选项
            quality = download_options.get('quality', '1080p')
            quality_index = self.quality_group.quality_combo.findText(quality)
            if quality_index >= 0:
                self.quality_group.quality_combo.setCurrentIndex(quality_index)

            format_type = download_options.get('format_type', '自动选择')
            format_index = self.quality_group.format_type_combo.findText(format_type)
            if format_index >= 0:
                self.quality_group.format_type_combo.setCurrentIndex(format_index)

            # 加载Cookie设置
            cookie_options = self.config_manager.get_cookie_options()
            if cookie_options.get('use_browser', True):
                self.cookie_group.browser_radio.setChecked(True)
                browser = cookie_options.get('browser', 'Firefox')
                browser_index = self.cookie_group.browser_combo.findText(browser)
                if browser_index >= 0:
                    self.cookie_group.browser_combo.setCurrentIndex(browser_index)
            else:
                self.cookie_group.file_radio.setChecked(True)
                self.cookie_group.cookie_file_input.setText(cookie_options.get('cookie_file', ''))

            # 加载UI设置
            ui_options = self.config_manager.get_ui_options()
            self.log_group.auto_scroll_checkbox.setChecked(ui_options.get('auto_scroll_log', True))

        except Exception as e:
            print(f"加载设置失败: {e}")

    def save_current_settings(self):
        """保存当前设置"""
        try:
            # 保存下载设置
            self.config_manager.set_download_options(
                directory=self.output_group.dir_input.text(),
                output_template=self.output_group.template_input.text(),
                quality=self.quality_group.quality_combo.currentText(),
                format_type=self.quality_group.format_type_combo.currentText(),
                audio_codec=self.quality_group.audio_codec_combo.currentText(),
                custom_format=self.quality_group.custom_format.text()
            )

            # 保存Cookie设置
            self.config_manager.set_cookie_options(
                use_browser=self.cookie_group.browser_radio.isChecked(),
                browser=self.cookie_group.browser_combo.currentText(),
                cookie_file=self.cookie_group.cookie_file_input.text()
            )

            # 保存UI设置
            self.config_manager.set_ui_options(
                auto_scroll_log=self.log_group.auto_scroll_checkbox.isChecked()
            )

            # 保存到文件
            self.config_manager.save_config()

        except Exception as e:
            print(f"保存设置失败: {e}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        # 保存当前设置
        self.save_current_settings()

        # 停止下载线程
        if self.download_thread and self.download_thread.isRunning():
            self.stop_download()

        # 关闭任务管理器
        from task_manager import shutdown_task_manager
        shutdown_task_manager()

        event.accept()
