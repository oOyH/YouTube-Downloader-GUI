"""
进度显示组件
提供更好的下载进度可视化和用户反馈
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QProgressBar, QPushButton, QFrame
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont


class ProgressWidget(QWidget):
    """下载进度显示组件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.reset_progress()
        
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        
        # 主进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 状态信息行
        status_layout = QHBoxLayout()
        
        # 下载状态
        self.status_label = QLabel("准备就绪")
        self.status_label.setFont(QFont("Arial", 9))
        status_layout.addWidget(self.status_label)
        
        status_layout.addStretch()
        
        # 下载速度
        self.speed_label = QLabel("")
        self.speed_label.setFont(QFont("Arial", 9))
        self.speed_label.setStyleSheet("color: #666;")
        status_layout.addWidget(self.speed_label)
        
        # 预计剩余时间
        self.eta_label = QLabel("")
        self.eta_label.setFont(QFont("Arial", 9))
        self.eta_label.setStyleSheet("color: #666;")
        status_layout.addWidget(self.eta_label)
        
        layout.addLayout(status_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setVisible(False)
        layout.addWidget(line)
        self.separator_line = line
        
        self.setLayout(layout)
        
    def show_progress(self):
        """显示进度组件"""
        self.progress_bar.setVisible(True)
        self.separator_line.setVisible(True)
        self.status_label.setText("正在下载...")
        
    def hide_progress(self):
        """隐藏进度组件"""
        self.progress_bar.setVisible(False)
        self.separator_line.setVisible(False)
        self.reset_progress()
        
    def reset_progress(self):
        """重置进度"""
        self.progress_bar.setValue(0)
        self.status_label.setText("准备就绪")
        self.speed_label.setText("")
        self.eta_label.setText("")
        
    def update_progress(self, percentage):
        """更新进度百分比"""
        self.progress_bar.setValue(percentage)
        if percentage > 0:
            self.status_label.setText(f"下载中... {percentage}%")
            
    def update_speed(self, speed):
        """更新下载速度"""
        self.speed_label.setText(f"速度: {speed}")
        
    def update_eta(self, eta):
        """更新预计剩余时间"""
        self.eta_label.setText(f"剩余: {eta}")
        
    def set_status(self, status):
        """设置状态文本"""
        self.status_label.setText(status)
        
    def set_completed(self):
        """设置为完成状态"""
        self.progress_bar.setValue(100)
        self.status_label.setText("下载完成")
        self.speed_label.setText("")
        self.eta_label.setText("")
        
    def set_error(self, error_msg):
        """设置为错误状态"""
        self.status_label.setText(f"错误: {error_msg}")
        self.status_label.setStyleSheet("color: red;")
        self.speed_label.setText("")
        self.eta_label.setText("")
        
    def set_cancelled(self):
        """设置为取消状态"""
        self.status_label.setText("已取消")
        self.status_label.setStyleSheet("color: orange;")
        self.speed_label.setText("")
        self.eta_label.setText("")


class BatchProgressWidget(QWidget):
    """批量下载进度组件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.reset()
        
    def setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout()
        
        # 总体进度
        overall_layout = QHBoxLayout()
        overall_layout.addWidget(QLabel("总进度:"))
        
        self.overall_progress = QProgressBar()
        self.overall_progress.setMinimum(0)
        self.overall_progress.setMaximum(100)
        overall_layout.addWidget(self.overall_progress)
        
        self.overall_label = QLabel("0/0")
        overall_layout.addWidget(self.overall_label)
        
        layout.addLayout(overall_layout)
        
        # 当前项目进度
        self.current_progress = ProgressWidget()
        layout.addWidget(self.current_progress)
        
        self.setLayout(layout)
        self.setVisible(False)
        
    def start_batch(self, total_items):
        """开始批量下载"""
        self.total_items = total_items
        self.completed_items = 0
        self.overall_progress.setMaximum(total_items)
        self.overall_progress.setValue(0)
        self.overall_label.setText(f"0/{total_items}")
        self.setVisible(True)
        self.current_progress.show_progress()
        
    def update_current_item(self, item_name):
        """更新当前下载项目"""
        self.current_progress.set_status(f"正在下载: {item_name}")
        
    def complete_current_item(self):
        """完成当前项目"""
        self.completed_items += 1
        self.overall_progress.setValue(self.completed_items)
        self.overall_label.setText(f"{self.completed_items}/{self.total_items}")
        self.current_progress.set_completed()
        
        # 短暂延迟后重置当前进度
        QTimer.singleShot(1000, self.current_progress.reset_progress)
        
    def finish_batch(self):
        """完成批量下载"""
        self.current_progress.hide_progress()
        self.current_progress.set_status("批量下载完成")
        
        # 延迟隐藏整个组件
        QTimer.singleShot(3000, self.hide)
        
    def reset(self):
        """重置状态"""
        self.total_items = 0
        self.completed_items = 0
        self.overall_progress.setValue(0)
        self.overall_label.setText("0/0")
        self.current_progress.reset_progress()
        self.setVisible(False)
        
    def update_progress(self, percentage):
        """更新当前项目进度"""
        self.current_progress.update_progress(percentage)
        
    def update_speed(self, speed):
        """更新下载速度"""
        self.current_progress.update_speed(speed)
        
    def update_eta(self, eta):
        """更新预计剩余时间"""
        self.current_progress.update_eta(eta)
        
    def set_error(self, error_msg):
        """设置错误状态"""
        self.current_progress.set_error(error_msg)
        
    def set_cancelled(self):
        """设置取消状态"""
        self.current_progress.set_cancelled()
        self.current_progress.set_status("批量下载已取消")


class StatusIndicator(QWidget):
    """状态指示器组件"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.status_dot = QLabel("●")
        self.status_dot.setFont(QFont("Arial", 12))
        self.status_text = QLabel("就绪")
        self.status_text.setFont(QFont("Arial", 9))
        
        layout.addWidget(self.status_dot)
        layout.addWidget(self.status_text)
        layout.addStretch()
        
        self.setLayout(layout)
        self.set_ready()
        
    def set_ready(self):
        """设置为就绪状态"""
        self.status_dot.setStyleSheet("color: #28a745;")  # 绿色
        self.status_text.setText("就绪")
        
    def set_downloading(self):
        """设置为下载状态"""
        self.status_dot.setStyleSheet("color: #007bff;")  # 蓝色
        self.status_text.setText("下载中")
        
    def set_completed(self):
        """设置为完成状态"""
        self.status_dot.setStyleSheet("color: #28a745;")  # 绿色
        self.status_text.setText("完成")
        
    def set_error(self):
        """设置为错误状态"""
        self.status_dot.setStyleSheet("color: #dc3545;")  # 红色
        self.status_text.setText("错误")
        
    def set_cancelled(self):
        """设置为取消状态"""
        self.status_dot.setStyleSheet("color: #ffc107;")  # 黄色
        self.status_text.setText("已取消")
        
    def set_custom(self, text, color="#666"):
        """设置自定义状态"""
        self.status_dot.setStyleSheet(f"color: {color};")
        self.status_text.setText(text)
