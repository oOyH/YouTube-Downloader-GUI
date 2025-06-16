"""
UI组件模块
包含各种可重用的UI组件和布局
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QRadioButton, QButtonGroup, QComboBox, 
    QTextEdit, QFileDialog, QGroupBox, QSpinBox, QDateEdit, 
    QCheckBox, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from config import (
    APP_CONFIG, QUALITY_CONFIG, BROWSER_CONFIG, UI_STYLES, 
    TEMPLATE_HELP_TEXT, DEFAULT_DOWNLOAD_DIR
)
from utils import format_timestamp


class URLInputGroup(QGroupBox):
    """URL输入组件"""
    
    def __init__(self):
        super().__init__("视频URL")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("输入YouTube视频或播放列表URL")
        layout.addWidget(self.url_input)
        self.setLayout(layout)
        
    def get_url(self):
        return self.url_input.text().strip()
        
    def set_url(self, url):
        self.url_input.setText(url)


class DownloadModeGroup(QGroupBox):
    """下载模式选择组件"""
    
    def __init__(self):
        super().__init__("下载模式")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 单选按钮组
        self.mode_group = QButtonGroup(self)
        
        # 单个视频模式
        self.single_radio = QRadioButton("下载单个视频")
        self.single_radio.setChecked(True)
        self.mode_group.addButton(self.single_radio, 1)
        layout.addWidget(self.single_radio)
        
        # 播放列表按日期下载模式
        self.date_radio = QRadioButton("根据日期下载播放列表视频")
        self.mode_group.addButton(self.date_radio, 2)
        date_layout = QHBoxLayout()
        date_layout.addWidget(self.date_radio)
        
        date_label = QLabel("起始日期:")
        date_label.setMinimumWidth(80)
        self.date_picker = QDateEdit()
        self.date_picker.setDate(QDate.currentDate().addDays(-7))
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setMinimumWidth(120)
        
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_picker)
        date_layout.addStretch()
        layout.addLayout(date_layout)
        
        # 播放列表按范围下载模式
        self.range_radio = QRadioButton("根据范围下载播放列表视频")
        self.mode_group.addButton(self.range_radio, 3)
        range_layout = QHBoxLayout()
        range_layout.addWidget(self.range_radio)
        
        start_label = QLabel("起始序号:")
        start_label.setMinimumWidth(80)
        self.start_spin = QSpinBox()
        self.start_spin.setMinimum(1)
        self.start_spin.setMaximum(9999)
        self.start_spin.setMinimumWidth(80)
        
        count_label = QLabel("数量:")
        count_label.setMinimumWidth(60)
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(9999)
        self.count_spin.setMinimumWidth(80)
        
        self.download_all = QCheckBox("下载全部剩余")
        self.download_all.stateChanged.connect(self._on_download_all_changed)
        
        range_layout.addWidget(start_label)
        range_layout.addWidget(self.start_spin)
        range_layout.addWidget(count_label)
        range_layout.addWidget(self.count_spin)
        range_layout.addWidget(self.download_all)
        range_layout.addStretch()
        
        layout.addLayout(range_layout)
        self.setLayout(layout)
        
    def _on_download_all_changed(self, state):
        self.count_spin.setEnabled(not state)
        
    def get_mode(self):
        """获取选择的模式"""
        if self.single_radio.isChecked():
            return 'single'
        elif self.date_radio.isChecked():
            return 'date'
        elif self.range_radio.isChecked():
            return 'range'
        return 'single'
        
    def get_mode_options(self):
        """获取模式相关选项"""
        options = {}
        
        if self.date_radio.isChecked():
            date = self.date_picker.date()
            options['date_after'] = date.toString('yyyyMMdd')
            
        elif self.range_radio.isChecked():
            options['start_index'] = self.start_spin.value() - 1  # 转换为0基索引
            if self.download_all.isChecked():
                options['count'] = 9999  # 大数值表示全部
            else:
                options['count'] = self.count_spin.value()
                
        return options


class QualityFormatGroup(QGroupBox):
    """视频质量和格式选择组件"""
    
    def __init__(self):
        super().__init__("视频质量和格式")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 第一行：质量选择
        quality_row = QHBoxLayout()
        quality_label = QLabel("选择质量:")
        quality_label.setMinimumWidth(80)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(QUALITY_CONFIG['quality_options'])
        self.quality_combo.setCurrentIndex(4)  # 默认1080p
        self.quality_combo.setMinimumWidth(120)
        self.quality_combo.currentIndexChanged.connect(self._on_quality_changed)
        
        self.custom_format = QLineEdit()
        self.custom_format.setPlaceholderText("自定义格式 (如 '248+251')")
        self.custom_format.setEnabled(False)
        self.custom_format.setMinimumWidth(200)
        
        quality_row.addWidget(quality_label)
        quality_row.addWidget(self.quality_combo)
        quality_row.addWidget(self.custom_format)
        quality_row.addStretch()
        layout.addLayout(quality_row)
        
        # 第二行：格式类型和编码选择
        format_row = QHBoxLayout()
        
        format_label = QLabel("格式类型:")
        format_label.setMinimumWidth(80)
        self.format_type_combo = QComboBox()
        self.format_type_combo.addItems(QUALITY_CONFIG['format_options'])
        self.format_type_combo.setCurrentIndex(0)
        self.format_type_combo.setMinimumWidth(120)
        self.format_type_combo.currentIndexChanged.connect(self._on_format_type_changed)
        
        codec_label = QLabel("音频编码:")
        codec_label.setMinimumWidth(80)
        self.audio_codec_combo = QComboBox()
        self.audio_codec_combo.addItems(QUALITY_CONFIG['audio_codec_options'])
        self.audio_codec_combo.setCurrentIndex(0)
        self.audio_codec_combo.setMinimumWidth(80)
        
        self.formats_button = QPushButton("查看可用格式")
        
        format_row.addWidget(format_label)
        format_row.addWidget(self.format_type_combo)
        format_row.addWidget(codec_label)
        format_row.addWidget(self.audio_codec_combo)
        format_row.addWidget(self.formats_button)
        format_row.addStretch()
        layout.addLayout(format_row)
        
        self.setLayout(layout)
        
    def _on_quality_changed(self, index):
        self.custom_format.setEnabled(index == len(QUALITY_CONFIG['quality_options']) - 1)
        
    def _on_format_type_changed(self, index):
        """处理格式类型变化"""
        format_type = self.format_type_combo.currentText()
        
        # 如果选择仅音频，禁用视频质量选择
        if format_type == "仅音频":
            self.quality_combo.setEnabled(False)
            self.audio_codec_combo.clear()
            self.audio_codec_combo.addItems(["最佳", "Opus", "AAC"])
        else:
            self.quality_combo.setEnabled(True)
            # 根据格式类型调整音频编码选项
            if format_type == "WebM (VP9)":
                self.audio_codec_combo.clear()
                self.audio_codec_combo.addItems(["最佳", "Opus"])
            elif format_type in ["MP4 (H.264)", "MP4 (AV1)"]:
                self.audio_codec_combo.clear()
                self.audio_codec_combo.addItems(["最佳", "AAC", "Opus"])
            else:  # 自动选择
                self.audio_codec_combo.clear()
                self.audio_codec_combo.addItems(["最佳", "Opus", "AAC"])
                
    def get_quality_options(self):
        """获取质量选项"""
        quality = self.quality_combo.currentText()
        format_type = self.format_type_combo.currentText()
        audio_codec = self.audio_codec_combo.currentText()
        
        options = {
            'format_choice': quality,
            'format_type': format_type,
            'audio_codec': audio_codec
        }
        
        if quality == "自定义":
            options['custom_format'] = self.custom_format.text().strip() or '248+251'
            
        return options


class CookieSourceGroup(QGroupBox):
    """Cookie来源选择组件"""
    
    def __init__(self):
        super().__init__("Cookie 来源")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Cookie来源选择单选按钮组
        self.cookie_source_group = QButtonGroup(self)
        self.browser_radio = QRadioButton("从浏览器获取")
        self.file_radio = QRadioButton("从文件获取")
        self.browser_radio.setChecked(True)
        self.cookie_source_group.addButton(self.browser_radio)
        self.cookie_source_group.addButton(self.file_radio)
        
        self.browser_radio.toggled.connect(self._on_cookie_source_changed)
        
        layout.addWidget(self.browser_radio)
        
        # 浏览器选择
        browser_layout = QHBoxLayout()
        browser_label = QLabel("选择浏览器:")
        browser_label.setMinimumWidth(100)
        self.browser_combo = QComboBox()
        self.browser_combo.addItems(BROWSER_CONFIG['supported_browsers'])
        self.browser_combo.setMinimumWidth(150)
        browser_layout.addWidget(browser_label)
        browser_layout.addWidget(self.browser_combo)
        browser_layout.addStretch()
        layout.addLayout(browser_layout)
        
        layout.addWidget(self.file_radio)
        
        # Cookie文件选择
        file_layout = QHBoxLayout()
        self.cookie_file_input = QLineEdit()
        self.cookie_file_input.setPlaceholderText("选择 cookies.txt 文件")
        self.cookie_file_input.setEnabled(False)
        
        self.cookie_file_button = QPushButton("浏览...")
        self.cookie_file_button.setEnabled(False)
        
        self.export_cookie_btn = QPushButton("从浏览器导出")
        self.export_cookie_btn.setEnabled(False)
        
        self.test_cookie_btn = QPushButton("测试Cookie")
        self.test_cookie_btn.setEnabled(False)
        
        file_layout.addWidget(self.cookie_file_input)
        file_layout.addWidget(self.cookie_file_button)
        file_layout.addWidget(self.export_cookie_btn)
        file_layout.addWidget(self.test_cookie_btn)
        layout.addLayout(file_layout)
        
        # Cookie使用说明
        help_layout = QHBoxLayout()
        help_label = QLabel("💡 提示: 推荐使用'Get cookies.txt LOCALLY'浏览器插件导出cookie文件")
        help_label.setStyleSheet(UI_STYLES['help_text'])
        help_label.setWordWrap(True)
        help_layout.addWidget(help_label)
        layout.addLayout(help_layout)
        
        self.setLayout(layout)
        
    def _on_cookie_source_changed(self, browser_checked):
        """处理Cookie来源选择变化"""
        self.browser_combo.setEnabled(browser_checked)
        self.cookie_file_input.setEnabled(not browser_checked)
        self.cookie_file_button.setEnabled(not browser_checked)
        self.export_cookie_btn.setEnabled(not browser_checked)
        self.test_cookie_btn.setEnabled(not browser_checked)
        
    def get_cookie_options(self):
        """获取Cookie选项"""
        options = {
            'use_browser': self.browser_radio.isChecked()
        }
        
        if options['use_browser']:
            options['browser'] = self.browser_combo.currentText()
        else:
            options['cookie_file'] = self.cookie_file_input.text().strip()
            
        return options


class OutputOptionsGroup(QGroupBox):
    """输出选项组件"""
    
    def __init__(self):
        super().__init__("输出选项")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # 下载目录选择
        dir_layout = QHBoxLayout()
        dir_label = QLabel("保存目录:")
        self.dir_input = QLineEdit(DEFAULT_DOWNLOAD_DIR)
        self.dir_input.setReadOnly(True)
        self.dir_btn = QPushButton("选择目录")
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.dir_input)
        dir_layout.addWidget(self.dir_btn)
        layout.addLayout(dir_layout)
        
        # 输出模板
        template_layout = QHBoxLayout()
        template_label = QLabel("输出模板:")
        self.template_input = QLineEdit()
        self.template_input.setPlaceholderText("例如: %(title)s-%(id)s.%(ext)s")
        self.template_help_btn = QPushButton("?")
        self.template_help_btn.setFixedWidth(30)
        self.template_help_btn.clicked.connect(self._show_template_help)
        template_layout.addWidget(template_label)
        template_layout.addWidget(self.template_input)
        template_layout.addWidget(self.template_help_btn)
        layout.addLayout(template_layout)
        
        # 下载记录选项
        archive_layout = QHBoxLayout()
        self.use_archive = QCheckBox("使用下载记录")
        self.use_archive.toggled.connect(self._on_archive_toggled)
        self.archive_input = QLineEdit()
        self.archive_input.setEnabled(False)
        self.archive_input.setPlaceholderText("下载记录文件路径")
        self.archive_btn = QPushButton("选择文件")
        self.archive_btn.clicked.connect(self._select_archive_file)
        self.archive_btn.setEnabled(False)
        archive_layout.addWidget(self.use_archive)
        archive_layout.addWidget(self.archive_input)
        archive_layout.addWidget(self.archive_btn)
        layout.addLayout(archive_layout)
        
        self.setLayout(layout)
        
    def _show_template_help(self):
        """显示输出模板帮助信息"""
        QMessageBox.information(None, "输出模板帮助", TEMPLATE_HELP_TEXT.strip())
        
    def _on_archive_toggled(self, checked):
        self.archive_input.setEnabled(checked)
        self.archive_btn.setEnabled(checked)
        
    def _select_archive_file(self):
        """选择归档文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "选择下载记录文件",
            f"download_archive_{format_timestamp()}.txt",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        if file_path:
            self.archive_input.setText(file_path)
            
    def get_output_options(self):
        """获取输出选项"""
        options = {
            'download_dir': self.dir_input.text().strip()
        }
        
        if self.template_input.text().strip():
            options['output_template'] = self.template_input.text().strip()
            
        if self.use_archive.isChecked() and self.archive_input.text().strip():
            options['download_archive'] = self.archive_input.text().strip()
            
        return options


class LogDisplayGroup(QGroupBox):
    """日志显示组件"""
    
    def __init__(self):
        super().__init__("下载日志")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(200)
        self.log_text.setMaximumHeight(300)
        self.log_text.setFont(QFont(*APP_CONFIG['log_font']))
        
        # 添加日志控制按钮
        log_controls = QHBoxLayout()
        self.clear_log_btn = QPushButton("清空日志")
        self.save_log_btn = QPushButton("保存日志")
        self.auto_scroll_checkbox = QCheckBox("自动滚动")
        self.auto_scroll_checkbox.setChecked(True)
        
        log_controls.addWidget(self.clear_log_btn)
        log_controls.addWidget(self.save_log_btn)
        log_controls.addWidget(self.auto_scroll_checkbox)
        log_controls.addStretch()
        
        layout.addWidget(self.log_text)
        layout.addLayout(log_controls)
        self.setLayout(layout)
        
    def append_log(self, text):
        """添加日志并自动滚动"""
        self.log_text.append(text)
        if self.auto_scroll_checkbox.isChecked():
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        
    def save_log(self):
        """保存日志到文件"""
        file_path, _ = QFileDialog.getSaveFileName(
            None,
            "保存日志文件",
            f"download_log_{format_timestamp()}.txt",
            "文本文件 (*.txt);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(None, "保存成功", f"日志已保存到:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(None, "保存失败", f"保存日志时出错:\n{str(e)}")
