"""
YouTube下载器主程序入口
重构后的模块化版本
"""

import sys
import os
from PyQt5.QtWidgets import QApplication

# 添加当前目录到Python路径，确保可以导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main_window import YouTubeDownloaderMainWindow
from improved_main_window import ImprovedMainWindow


def main():
    """主函数"""
    # 创建应用程序
    app = QApplication(sys.argv)
    
    # 设置应用程序属性
    app.setApplicationName("YouTube下载器")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("YouTube Downloader")
    
    # 创建主窗口 - 可以选择使用改进版本
    if "--improved" in sys.argv:
        main_window = ImprovedMainWindow()
    else:
        main_window = YouTubeDownloaderMainWindow()
    main_window.show()
    
    # 运行应用程序
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
