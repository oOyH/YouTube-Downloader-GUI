"""
主题和样式管理器
提供统一的UI主题和样式管理
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QObject, pyqtSignal as Signal
from PyQt5.QtGui import QPalette, QColor


class ThemeManager(QObject):
    """主题管理器"""
    
    theme_changed = Signal(str)  # 主题变化信号
    
    def __init__(self):
        super().__init__()
        self.current_theme = 'light'
        self.themes = self._load_themes()
        
    def _load_themes(self):
        """加载主题定义"""
        return {
            'light': {
                'name': '浅色主题',
                'colors': {
                    'primary': '#007bff',
                    'secondary': '#6c757d',
                    'success': '#28a745',
                    'danger': '#dc3545',
                    'warning': '#ffc107',
                    'info': '#17a2b8',
                    'light': '#f8f9fa',
                    'dark': '#343a40',
                    'background': '#ffffff',
                    'surface': '#f8f9fa',
                    'text': '#212529',
                    'text_secondary': '#6c757d'
                },
                'styles': self._get_light_styles()
            },
            'dark': {
                'name': '深色主题',
                'colors': {
                    'primary': '#0d6efd',
                    'secondary': '#6c757d',
                    'success': '#198754',
                    'danger': '#dc3545',
                    'warning': '#ffc107',
                    'info': '#0dcaf0',
                    'light': '#f8f9fa',
                    'dark': '#212529',
                    'background': '#212529',
                    'surface': '#343a40',
                    'text': '#ffffff',
                    'text_secondary': '#adb5bd'
                },
                'styles': self._get_dark_styles()
            },
            'blue': {
                'name': '蓝色主题',
                'colors': {
                    'primary': '#2196F3',
                    'secondary': '#607D8B',
                    'success': '#4CAF50',
                    'danger': '#F44336',
                    'warning': '#FF9800',
                    'info': '#00BCD4',
                    'light': '#ECEFF1',
                    'dark': '#263238',
                    'background': '#FAFAFA',
                    'surface': '#FFFFFF',
                    'text': '#212121',
                    'text_secondary': '#757575'
                },
                'styles': self._get_blue_styles()
            }
        }
        
    def _get_light_styles(self):
        """获取浅色主题样式"""
        return {
            'main_window': """
                QMainWindow {
                    background-color: #ffffff;
                    color: #212529;
                }
            """,
            'group_box': """
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #dee2e6;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #f8f9fa;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #495057;
                }
            """,
            'button_primary': """
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-height: 32px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
                QPushButton:pressed {
                    background-color: #004085;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """,
            'button_success': """
                QPushButton {
                    background-color: #28a745;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-height: 32px;
                }
                QPushButton:hover {
                    background-color: #218838;
                }
                QPushButton:pressed {
                    background-color: #1e7e34;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """,
            'button_danger': """
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-height: 32px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
                QPushButton:pressed {
                    background-color: #bd2130;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """,
            'input': """
                QLineEdit, QTextEdit, QComboBox {
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    padding: 6px 12px;
                    background-color: #ffffff;
                    color: #495057;
                }
                QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                    border-color: #80bdff;
                    outline: 0;
                    box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
                }
            """,
            'progress_bar': """
                QProgressBar {
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    text-align: center;
                    background-color: #e9ecef;
                }
                QProgressBar::chunk {
                    background-color: #007bff;
                    border-radius: 3px;
                }
            """,
            'log_text': """
                QTextEdit {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 4px;
                    color: #495057;
                    font-family: 'Consolas', 'Monaco', monospace;
                }
            """
        }
        
    def _get_dark_styles(self):
        """获取深色主题样式"""
        return {
            'main_window': """
                QMainWindow {
                    background-color: #212529;
                    color: #ffffff;
                }
            """,
            'group_box': """
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #495057;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 10px;
                    background-color: #343a40;
                    color: #ffffff;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #adb5bd;
                }
            """,
            'button_primary': """
                QPushButton {
                    background-color: #0d6efd;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-height: 32px;
                }
                QPushButton:hover {
                    background-color: #0b5ed7;
                }
                QPushButton:pressed {
                    background-color: #0a58ca;
                }
                QPushButton:disabled {
                    background-color: #6c757d;
                }
            """,
            # 其他样式类似，但使用深色配色
        }
        
    def _get_blue_styles(self):
        """获取蓝色主题样式"""
        # 类似于浅色主题，但使用蓝色配色方案
        return self._get_light_styles()  # 简化实现
        
    def get_current_theme(self):
        """获取当前主题"""
        return self.current_theme
        
    def get_theme_names(self):
        """获取所有主题名称"""
        return [theme['name'] for theme in self.themes.values()]
        
    def set_theme(self, theme_name):
        """设置主题"""
        if theme_name in self.themes:
            self.current_theme = theme_name
            self._apply_theme()
            self.theme_changed.emit(theme_name)
            
    def _apply_theme(self):
        """应用当前主题"""
        app = QApplication.instance()
        if app:
            theme = self.themes[self.current_theme]
            
            # 设置应用程序样式表
            stylesheet = self._build_stylesheet(theme['styles'])
            app.setStyleSheet(stylesheet)
            
            # 设置调色板（可选）
            self._set_palette(theme['colors'])
            
    def _build_stylesheet(self, styles):
        """构建样式表"""
        stylesheet = ""
        for selector, style in styles.items():
            stylesheet += style + "\n"
        return stylesheet
        
    def _set_palette(self, colors):
        """设置调色板"""
        app = QApplication.instance()
        if app:
            palette = QPalette()
            
            # 设置基本颜色
            palette.setColor(QPalette.Window, QColor(colors['background']))
            palette.setColor(QPalette.WindowText, QColor(colors['text']))
            palette.setColor(QPalette.Base, QColor(colors['surface']))
            palette.setColor(QPalette.AlternateBase, QColor(colors['light']))
            palette.setColor(QPalette.Text, QColor(colors['text']))
            palette.setColor(QPalette.Button, QColor(colors['surface']))
            palette.setColor(QPalette.ButtonText, QColor(colors['text']))
            palette.setColor(QPalette.Highlight, QColor(colors['primary']))
            palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))
            
            app.setPalette(palette)
            
    def get_color(self, color_name):
        """获取当前主题的颜色"""
        theme = self.themes.get(self.current_theme, {})
        colors = theme.get('colors', {})
        return colors.get(color_name, '#000000')
        
    def get_style(self, style_name):
        """获取当前主题的样式"""
        theme = self.themes.get(self.current_theme, {})
        styles = theme.get('styles', {})
        return styles.get(style_name, '')


class StyleHelper:
    """样式辅助类"""
    
    @staticmethod
    def create_card_style(background_color='#ffffff', border_color='#dee2e6'):
        """创建卡片样式"""
        return f"""
            QWidget {{
                background-color: {background_color};
                border: 1px solid {border_color};
                border-radius: 8px;
                padding: 16px;
            }}
        """
        
    @staticmethod
    def create_shadow_style():
        """创建阴影样式"""
        return """
            QWidget {
                border: none;
                background-color: rgba(0, 0, 0, 0.1);
                border-radius: 4px;
            }
        """
        
    @staticmethod
    def create_gradient_style(start_color, end_color):
        """创建渐变样式"""
        return f"""
            QWidget {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {start_color}, stop: 1 {end_color});
            }}
        """
        
    @staticmethod
    def create_hover_effect(normal_color, hover_color):
        """创建悬停效果"""
        return f"""
            QPushButton {{
                background-color: {normal_color};
                transition: background-color 0.3s ease;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
        """


# 全局主题管理器实例
_theme_manager = None

def get_theme_manager():
    """获取全局主题管理器实例"""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager
