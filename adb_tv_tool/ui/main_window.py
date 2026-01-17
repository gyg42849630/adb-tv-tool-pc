# -*- coding: utf-8 -*-
"""
主窗口界面
实现苹果风格的侧边栏导航布局
"""

import logging
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QSplitter, QLabel, QFrame, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap

from adb_tv_tool.ui.sidebar import Sidebar
from adb_tv_tool.ui.content_area import ContentArea
from adb_tv_tool.ui.status_bar import StatusBar
from adb_tv_tool.utils.style import AppleStyle


class MainWindow(QMainWindow):
    """主窗口类"""
    
    # 信号定义
    sidebar_item_changed = pyqtSignal(str)  # 侧边栏选项改变
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.main_window")
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("ADB TV Tool - 电视应用管理工具")
        self.setMinimumSize(1200, 800)
        
        # 设置窗口图标（后续添加）
        # self.setWindowIcon(QIcon("resources/icons/app_icon.ico"))
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建分割器（侧边栏和内容区域）
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        main_layout.addWidget(self.splitter)
        
        # 创建侧边栏
        self.sidebar = Sidebar()
        self.sidebar.setMaximumWidth(280)
        self.sidebar.setMinimumWidth(200)
        
        # 创建内容区域
        self.content_area = ContentArea()
        
        # 添加到分割器
        self.splitter.addWidget(self.sidebar)
        self.splitter.addWidget(self.content_area)
        
        # 设置分割器比例
        self.splitter.setStretchFactor(0, 0)  # 侧边栏不拉伸
        self.splitter.setStretchFactor(1, 1)  # 内容区域拉伸
        
        # 创建状态栏
        self.status_bar = StatusBar()
        self.setStatusBar(self.status_bar)
        
        # 设置样式
        self.apply_styles()
        
        self.logger.info("主窗口UI初始化完成")
    
    def apply_styles(self):
        """应用样式"""
        # 设置窗口背景色
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {AppleStyle.COLORS["background"]};
            }}
        """)
        
        # 设置分割器样式
        self.splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #E5E5EA;
                width: 1px;
            }
            QSplitter::handle:hover {
                background-color: #C6C6C8;
            }
        """)
    
    def setup_connections(self):
        """设置信号连接"""
        # 侧边栏选项改变信号
        self.sidebar.current_item_changed.connect(self.on_sidebar_item_changed)
        self.sidebar.current_item_changed.connect(self.sidebar_item_changed)
        
        # 内容区域状态更新信号
        self.content_area.status_updated.connect(self.status_bar.update_status)
    
    def on_sidebar_item_changed(self, item_name):
        """侧边栏选项改变槽函数"""
        self.logger.info(f"切换到功能界面: {item_name}")
        
        # 更新内容区域显示对应的功能界面
        self.content_area.show_content(item_name)
        
        # 更新窗口标题
        self.setWindowTitle(f"ADB TV Tool - {item_name}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        self.logger.info("应用程序正在关闭...")
        
        # 清理资源
        self.content_area.cleanup()
        
        # 接受关闭事件
        event.accept()


class TitleBar(QFrame):
    """自定义标题栏（苹果风格）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置标题栏UI"""
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 5, 20, 5)
        layout.setSpacing(10)
        
        # 应用图标和标题
        icon_label = QLabel()
        # icon_label.setPixmap(QPixmap("resources/icons/app_icon.png").scaled(24, 24))
        icon_label.setFixedSize(24, 24)
        
        title_label = QLabel("ADB TV Tool")
        title_font = QFont(*AppleStyle.FONT_CONFIG["title"])
        title_label.setFont(title_font)
        
        layout.addWidget(icon_label)
        layout.addWidget(title_label)
        layout.addStretch()
        
        # 工具栏按钮（刷新、导出、帮助）
        # 后续添加具体按钮
        
        self.apply_styles()
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            TitleBar {{
                background-color: {AppleStyle.COLORS["background"]};
                border-bottom: 1px solid {AppleStyle.COLORS["divider"]};
            }}
        """)


if __name__ == "__main__":
    # 测试主窗口
    import sys
    from PyQt6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # 应用苹果风格
    from adb_tv_tool.utils.style import apply_apple_style
    apply_apple_style(app)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())