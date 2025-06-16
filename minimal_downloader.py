#!/usr/bin/env python3
"""
YouTube下载器 - 最小工作版本
基于原始代码的简化版本
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox

class MinimalYouTubeDownloader(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube下载器 - 最小版本")
        self.setGeometry(100, 100, 600, 400)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # 添加标签
        label = QLabel("YouTube下载器正在修复中...")
        label.setStyleSheet("font-size: 16px; padding: 20px;")
        layout.addWidget(label)
        
        # 添加按钮
        btn_original = QPushButton("运行原始版本")
        btn_original.clicked.connect(self.run_original)
        layout.addWidget(btn_original)
        
        btn_help = QPushButton("查看帮助")
        btn_help.clicked.connect(self.show_help)
        layout.addWidget(btn_help)
    
    def run_original(self):
        """运行原始版本"""
        try:
            os.system("python ytd_gui_fixed.py")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"无法运行原始版本: {str(e)}")
    
    def show_help(self):
        """显示帮助"""
        help_text = """
YouTube下载器使用帮助：

1. 如果重构版本有问题，请使用原始版本：
   python ytd_gui_fixed.py

2. 确保已安装依赖：
   pip install PyQt5 yt-dlp

3. 如果仍有问题，请检查：
   - Python版本 (需要3.7+)
   - 网络连接
   - yt-dlp是否为最新版本

4. 重构版本文档：
   - README.md - 项目说明
   - USER_GUIDE.md - 使用指南
   - REFACTOR_SUMMARY.md - 重构说明
        """
        QMessageBox.information(self, "帮助", help_text)

def main():
    app = QApplication(sys.argv)
    window = MinimalYouTubeDownloader()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
