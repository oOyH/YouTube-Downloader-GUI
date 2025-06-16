"""
布局管理器
提供响应式和自适应的UI布局管理
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
    QSplitter, QScrollArea, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize, QRect
from PyQt5.QtGui import QResizeEvent


class ResponsiveLayout(QVBoxLayout):
    """响应式布局"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.breakpoints = {
            'xs': 576,   # 超小屏幕
            'sm': 768,   # 小屏幕
            'md': 992,   # 中等屏幕
            'lg': 1200,  # 大屏幕
            'xl': 1400   # 超大屏幕
        }
        self.current_breakpoint = 'lg'
        self.responsive_widgets = []
        
    def add_responsive_widget(self, widget, breakpoint_configs):
        """
        添加响应式组件
        
        Args:
            widget: 要添加的组件
            breakpoint_configs: 断点配置字典
                例如: {
                    'xs': {'visible': False},
                    'sm': {'visible': True, 'span': 12},
                    'md': {'visible': True, 'span': 6},
                    'lg': {'visible': True, 'span': 4}
                }
        """
        self.responsive_widgets.append({
            'widget': widget,
            'configs': breakpoint_configs
        })
        self.addWidget(widget)
        
    def update_layout(self, width):
        """根据宽度更新布局"""
        new_breakpoint = self._get_breakpoint(width)
        if new_breakpoint != self.current_breakpoint:
            self.current_breakpoint = new_breakpoint
            self._apply_breakpoint_configs()
            
    def _get_breakpoint(self, width):
        """根据宽度获取断点"""
        if width < self.breakpoints['xs']:
            return 'xs'
        elif width < self.breakpoints['sm']:
            return 'sm'
        elif width < self.breakpoints['md']:
            return 'md'
        elif width < self.breakpoints['lg']:
            return 'lg'
        else:
            return 'xl'
            
    def _apply_breakpoint_configs(self):
        """应用断点配置"""
        for item in self.responsive_widgets:
            widget = item['widget']
            configs = item['configs']
            
            if self.current_breakpoint in configs:
                config = configs[self.current_breakpoint]
                
                # 设置可见性
                if 'visible' in config:
                    widget.setVisible(config['visible'])
                    
                # 设置大小策略
                if 'size_policy' in config:
                    policy = config['size_policy']
                    widget.setSizePolicy(policy[0], policy[1])


class CardLayout(QFrame):
    """卡片布局"""
    
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.title = title
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                margin: 4px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)
        
        if self.title:
            from PyQt5.QtWidgets import QLabel
            from PyQt5.QtGui import QFont
            
            title_label = QLabel(self.title)
            title_font = QFont()
            title_font.setPointSize(12)
            title_font.setBold(True)
            title_label.setFont(title_font)
            title_label.setStyleSheet("color: #495057; margin-bottom: 8px;")
            layout.addWidget(title_label)
            
        self.content_layout = QVBoxLayout()
        layout.addLayout(self.content_layout)
        
        self.setLayout(layout)
        
    def add_content(self, widget):
        """添加内容"""
        self.content_layout.addWidget(widget)
        
    def add_content_layout(self, layout):
        """添加内容布局"""
        self.content_layout.addLayout(layout)


class TabbedLayout(QWidget):
    """标签页布局"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        from PyQt5.QtWidgets import QTabWidget
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: #ffffff;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #ffffff;
                border-bottom: 1px solid #ffffff;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    def add_tab(self, widget, title, icon=None):
        """添加标签页"""
        if icon:
            self.tab_widget.addTab(widget, icon, title)
        else:
            self.tab_widget.addTab(widget, title)


class SidebarLayout(QWidget):
    """侧边栏布局"""
    
    def __init__(self, sidebar_width=250, parent=None):
        super().__init__(parent)
        self.sidebar_width = sidebar_width
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 创建分割器
        self.splitter = QSplitter(Qt.Horizontal)
        
        # 侧边栏
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(self.sidebar_width)
        self.sidebar.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-right: 1px solid #dee2e6;
            }
        """)
        
        self.sidebar_layout = QVBoxLayout()
        self.sidebar_layout.setContentsMargins(16, 16, 16, 16)
        self.sidebar.setLayout(self.sidebar_layout)
        
        # 主内容区域
        self.main_content = QFrame()
        self.main_content.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
            }
        """)
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_content.setLayout(self.main_layout)
        
        # 添加到分割器
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.main_content)
        self.splitter.setSizes([self.sidebar_width, 800])
        
        layout.addWidget(self.splitter)
        self.setLayout(layout)
        
    def add_sidebar_widget(self, widget):
        """添加侧边栏组件"""
        self.sidebar_layout.addWidget(widget)
        
    def add_main_widget(self, widget):
        """添加主内容组件"""
        self.main_layout.addWidget(widget)
        
    def toggle_sidebar(self):
        """切换侧边栏显示/隐藏"""
        if self.sidebar.isVisible():
            self.sidebar.hide()
        else:
            self.sidebar.show()


class GridResponsiveLayout(QGridLayout):
    """响应式网格布局"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSpacing(16)
        self.items = []
        
    def add_responsive_item(self, widget, row_configs):
        """
        添加响应式项目
        
        Args:
            widget: 组件
            row_configs: 行配置字典
                例如: {
                    'xs': {'row': 0, 'col': 0, 'rowspan': 1, 'colspan': 12},
                    'md': {'row': 0, 'col': 0, 'rowspan': 1, 'colspan': 6},
                    'lg': {'row': 0, 'col': 0, 'rowspan': 1, 'colspan': 4}
                }
        """
        self.items.append({
            'widget': widget,
            'configs': row_configs
        })
        
    def update_grid(self, breakpoint):
        """更新网格布局"""
        # 清除现有布局
        for i in reversed(range(self.count())):
            self.itemAt(i).widget().setParent(None)
            
        # 重新添加组件
        for item in self.items:
            widget = item['widget']
            configs = item['configs']
            
            if breakpoint in configs:
                config = configs[breakpoint]
                self.addWidget(
                    widget,
                    config['row'],
                    config['col'],
                    config['rowspan'],
                    config['colspan']
                )


class FlowLayout(QVBoxLayout):
    """流式布局"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rows = []
        self.current_row = None
        self.max_items_per_row = 3
        
    def add_flow_widget(self, widget):
        """添加流式组件"""
        if not self.current_row or len(self.current_row.children()) >= self.max_items_per_row:
            self.current_row = QHBoxLayout()
            self.addLayout(self.current_row)
            self.rows.append(self.current_row)
            
        self.current_row.addWidget(widget)
        
    def set_max_items_per_row(self, max_items):
        """设置每行最大项目数"""
        self.max_items_per_row = max_items


class LayoutManager:
    """布局管理器"""
    
    @staticmethod
    def create_form_layout(items, columns=2):
        """
        创建表单布局
        
        Args:
            items: 表单项目列表 [(label, widget), ...]
            columns: 列数
        """
        from PyQt5.QtWidgets import QFormLayout, QLabel
        
        if columns == 1:
            layout = QFormLayout()
            for label_text, widget in items:
                if isinstance(label_text, str):
                    label = QLabel(label_text)
                    layout.addRow(label, widget)
                else:
                    layout.addRow(label_text, widget)
            return layout
        else:
            # 多列表单布局
            grid = QGridLayout()
            grid.setSpacing(16)
            
            for i, (label_text, widget) in enumerate(items):
                row = i // columns
                col = (i % columns) * 2
                
                if isinstance(label_text, str):
                    label = QLabel(label_text)
                    grid.addWidget(label, row, col)
                else:
                    grid.addWidget(label_text, row, col)
                    
                grid.addWidget(widget, row, col + 1)
                
            return grid
            
    @staticmethod
    def create_button_row(buttons, alignment=Qt.AlignCenter):
        """创建按钮行"""
        layout = QHBoxLayout()
        
        if alignment == Qt.AlignCenter:
            layout.addStretch()
            
        for button in buttons:
            layout.addWidget(button)
            
        if alignment == Qt.AlignCenter:
            layout.addStretch()
        elif alignment == Qt.AlignRight:
            layout.insertStretch(0)
            
        return layout
        
    @staticmethod
    def create_info_panel(title, content_widgets):
        """创建信息面板"""
        panel = CardLayout(title)
        
        for widget in content_widgets:
            panel.add_content(widget)
            
        return panel
        
    @staticmethod
    def add_spacing(layout, size=16):
        """添加间距"""
        from PyQt5.QtWidgets import QSpacerItem, QSizePolicy
        
        spacer = QSpacerItem(size, size, QSizePolicy.Minimum, QSizePolicy.Fixed)
        layout.addItem(spacer)
