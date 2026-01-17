# -*- coding: utf-8 -*-
"""
侧边栏组件
简洁的苹果风格导航
"""

import logging
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem, 
                             QLabel, QFrame, QPushButton, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QBrush, QColor

from adb_tv_tool.utils.style import AppleStyle


class Sidebar(QWidget):
    """侧边栏导航组件"""
    
    # 信号定义
    current_item_changed = pyqtSignal(str)
    
    # 侧边栏项目配置
    SIDEBAR_ITEMS = [
        {
            "name": "环境检测",
            "icon": "🔍",
            "description": "检查ADB环境和设备状态"
        },
        {
            "name": "设备连接", 
            "icon": "📱",
            "description": "连接和管理电视设备"
        },
        {
            "name": "投屏预览",
            "icon": "📺", 
            "description": "实时预览电视屏幕"
        },
        {
            "name": "应用管理",
            "icon": "📦",
            "description": "查看和管理电视应用"
        },
        {
            "name": "APK导入",
            "icon": "📎",
            "description": "导入APK文件进行安装"
        },
        {
            "name": "安装执行", 
            "icon": "⚡",
            "description": "执行APK安装操作"
        },
        {
            "name": "结果汇总",
            "icon": "📊",
            "description": "查看操作结果和日志"
        },
        {
            "name": "系统设置",
            "icon": "⚙️",
            "description": "工具设置和配置"
        }
    ]
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.sidebar")
        self.current_item = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置UI界面"""
        # 设置固定宽度
        self.setFixedWidth(280)  # 增加侧边栏宽度
        
        # 创建主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 20, 0, 20)
        layout.setSpacing(0)
        
        # 添加标题
        title_label = QLabel("功能导航")
        title_font = QFont("Microsoft YaHei", 18, QFont.Weight.DemiBold)  # 增大标题字体
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFixedHeight(50)  # 增加标题高度
        layout.addWidget(title_label)
        
        # 创建导航列表
        self.nav_list = QListWidget()
        self.nav_list.setFrameStyle(QListWidget.Shape.NoFrame)
        self.nav_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.nav_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 添加导航项目
        for i, item_data in enumerate(self.SIDEBAR_ITEMS):
            list_item = QListWidgetItem()
            
            # 创建自定义的列表项部件
            widget = QWidget()
            widget.setMinimumWidth(220)  # 增加最小宽度确保完整显示
            widget.setMinimumHeight(40)  # 设置最小高度
            layout_h = QHBoxLayout(widget)
            layout_h.setContentsMargins(20, 8, 20, 8)  # 调整边距
            layout_h.setSpacing(15)  # 增加图标和文字间距
            
            # 图标标签
            icon_label = QLabel(item_data["icon"])
            icon_label.setFixedSize(28, 28)  # 增大图标尺寸
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("font-size: 16px;")  # 设置图标字体大小
            
            # 文本标签
            name_label = QLabel(item_data["name"])
            name_font = QFont("Microsoft YaHei", 12, QFont.Weight.Medium)  # 调整字体大小
            name_label.setFont(name_font)
            name_label.setMinimumWidth(120)  # 设置文字最小宽度
            name_label.setSizePolicy(
                QSizePolicy.Policy.Expanding, 
                QSizePolicy.Policy.Preferred
            )
            name_label.setWordWrap(False)  # 禁止文字换行
            
            layout_h.addWidget(icon_label)
            layout_h.addWidget(name_label)
            layout_h.addStretch()
            
            list_item.setSizeHint(widget.sizeHint())
            self.nav_list.addItem(list_item)
            self.nav_list.setItemWidget(list_item, widget)
        
        layout.addWidget(self.nav_list)
        
        # 添加底部信息
        bottom_info = QLabel("ADB TV Tool v1.0.0")
        bottom_info_font = QFont("Microsoft YaHei", 10, QFont.Weight.Normal)
        bottom_info.setFont(bottom_info_font)
        bottom_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        bottom_info.setFixedHeight(30)
        
        layout.addWidget(bottom_info)
        
        # 应用样式
        self.apply_styles()
        
        self.logger.info("侧边栏UI初始化完成")
    
    def setup_connections(self):
        """设置信号连接"""
        self.nav_list.currentRowChanged.connect(self.on_current_row_changed)
        
        # 默认选中第一个项目
        if self.nav_list.count() > 0:
            self.nav_list.setCurrentRow(0)
    
    def apply_styles(self):
        """应用样式"""
        # 简单实用的样式
        self.setStyleSheet(f"""
            * {{
                color: {AppleStyle.COLORS["text_primary"]};
                font-family: Microsoft YaHei;
                font-size: 13px;
            }}
            QListWidget {{
                background: transparent;
                border: none;
                outline: none;
            }}
            QListWidget::item {{
                border: none;
                background: transparent;
                margin: 2px;
            }}
            QListWidget::item:selected {{
                background: {AppleStyle.COLORS["primary_dark"]};
                border-radius: 8px;
            }}
            QListWidget::item:selected QLabel {{
                color: #F0F0F0;  /* 浅灰色替代纯白 */
                font-weight: bold;
            }}
            QListWidget::item:hover {{
                background: {AppleStyle.COLORS["surface"]};
                border-radius: 8px;
            }}
            QLabel {{
                background: transparent;
            }}
            QListWidget::item:hover QLabel {{
                color: {AppleStyle.COLORS["primary"]};
            }}
        """)
    
    def on_current_row_changed(self, row):
        """当前行改变槽函数"""
        if 0 <= row < len(self.SIDEBAR_ITEMS):
            item_name = self.SIDEBAR_ITEMS[row]["name"]
            self.current_item = item_name
            self.current_item_changed.emit(item_name)
    
    def get_current_item(self):
        """获取当前选中的项目"""
        return self.current_item


if __name__ == "__main__":
    # 测试侧边栏
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow
    
    app = QApplication(sys.argv)
    
    # 应用苹果风格
    from adb_tv_tool.utils.style import apply_apple_style
    apply_apple_style(app)
    
    window = QMainWindow()
    sidebar = Sidebar()
    window.setCentralWidget(sidebar)
    window.show()
    
    sys.exit(app.exec())