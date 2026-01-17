# -*- coding: utf-8 -*-
"""
内容区域组件
根据不同侧边栏选项显示对应的功能界面
"""

import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget, QLabel, 
                             QFrame, QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal

from adb_tv_tool.ui.content_pages import (
    EnvironmentCheckPage, DeviceConnectPage, ScreenMirrorPage,
    AppManagerPage, APKImportPage, InstallExecutePage,
    ResultSummaryPage, SettingsPage
)
from adb_tv_tool.utils.style import AppleStyle


class ContentArea(QWidget):
    """内容区域组件"""
    
    # 信号定义
    status_updated = pyqtSignal(str)  # 状态更新信号
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.content_area")
        self.current_page = None
        self.pages = {}
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)
        
        # 创建堆叠窗口部件
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # 初始化所有页面
        self.init_pages()
        
        # 设置样式
        self.apply_styles()
        
        self.logger.info("内容区域UI初始化完成")
    
    def init_pages(self):
        """初始化所有内容页面"""
        # 环境检测页面
        env_page = EnvironmentCheckPage()
        self.add_page("环境检测", env_page)
        
        # 设备连接页面
        device_page = DeviceConnectPage()
        self.add_page("设备连接", device_page)
        
        # 投屏预览页面
        screen_page = ScreenMirrorPage()
        self.add_page("投屏预览", screen_page)
        
        # 应用管理页面
        app_page = AppManagerPage()
        self.add_page("应用管理", app_page)
        
        # APK导入页面
        apk_page = APKImportPage()
        self.add_page("APK导入", apk_page)
        
        # 安装执行页面
        install_page = InstallExecutePage()
        self.add_page("安装执行", install_page)
        
        # 结果汇总页面
        result_page = ResultSummaryPage()
        self.add_page("结果汇总", result_page)
        
        # 系统设置页面
        settings_page = SettingsPage()
        self.add_page("系统设置", settings_page)
        
        # 默认显示环境检测页面
        self.show_content("环境检测")
    
    def add_page(self, page_name, page_widget):
        """添加页面到堆叠窗口"""
        # 创建滚动区域包装页面
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameStyle(QFrame.Shape.NoFrame)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 设置页面部件
        scroll_area.setWidget(page_widget)
        
        # 添加到堆叠窗口
        index = self.stacked_widget.addWidget(scroll_area)
        self.pages[page_name] = index
        
        # 连接页面的状态更新信号
        if hasattr(page_widget, 'status_updated'):
            page_widget.status_updated.connect(self.status_updated)
    
    def show_content(self, content_name):
        """显示指定内容页面"""
        if content_name in self.pages:
            index = self.pages[content_name]
            self.stacked_widget.setCurrentIndex(index)
            self.current_page = content_name
            
            # 通知当前页面激活
            current_widget = self.stacked_widget.currentWidget().widget()
            if hasattr(current_widget, 'on_activated'):
                current_widget.on_activated()
            
            self.logger.info(f"切换到内容页面: {content_name}")
        else:
            self.logger.warning(f"未知的内容页面: {content_name}")
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            ContentArea {{
                background-color: {AppleStyle.COLORS["background"]};
            }}
        """)
    
    def cleanup(self):
        """清理资源"""
        for i in range(self.stacked_widget.count()):
            widget = self.stacked_widget.widget(i)
            if hasattr(widget.widget(), 'cleanup'):
                widget.widget().cleanup()
        
        self.logger.info("内容区域资源清理完成")


class ContentPage(QWidget):
    """内容页面基类"""
    
    # 信号定义
    status_updated = pyqtSignal(str)
    
    def __init__(self, title="", description=""):
        super().__init__()
        self.title = title
        self.description = description
        self.logger = logging.getLogger("ui.content_page")
        
    def setup_ui(self):
        """设置页面UI（子类重写）"""
        pass
    
    def on_activated(self):
        """页面激活时的回调（子类重写）"""
        pass
    
    def cleanup(self):
        """清理页面资源（子类重写）"""
        pass


# 内容页面已经在开头导入，直接使用导入的类


if __name__ == "__main__":
    # 测试内容区域
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    # 应用苹果风格
    from adb_tv_tool.utils.style import apply_apple_style
    apply_apple_style(app)
    
    window = QMainWindow()
    content_area = ContentArea()
    window.setCentralWidget(content_area)
    window.show()
    
    sys.exit(app.exec())