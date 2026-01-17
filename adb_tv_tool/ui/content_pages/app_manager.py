# -*- coding: utf-8 -*-
"""
应用管理页面
查看和管理电视应用
"""

import logging

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QFrame, QGroupBox,
                             QLineEdit, QListWidget, QListWidgetItem,
                             QMessageBox)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont

from adb_tv_tool.utils.style import AppleStyle
from adb_tv_tool.utils.adb_manager import get_adb_manager
from adb_tv_tool.utils.device_manager import get_device_manager, get_current_device


class AppManagerPage(QWidget):
    """应用管理页面"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.app_manager")
        self.connected_device = None
        self.setup_ui()
        
        # 注册设备变化监听器
        device_manager = get_device_manager()
        device_manager.add_listener(self.on_device_changed)
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        
        title = QLabel("应用管理")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        title_layout.addWidget(title)
        
        desc = QLabel("查看和管理电视应用，支持批量卸载操作")
        desc.setStyleSheet(f"font-size: 14px; color: {AppleStyle.COLORS['text_secondary']};")
        title_layout.addWidget(desc)
        
        layout.addLayout(title_layout)
        
        # 控制区域
        control_group = QGroupBox("应用管理控制")
        control_layout = QVBoxLayout(control_group)
        
        # 搜索和筛选
        filter_layout = QHBoxLayout()
        
        # 搜索框
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("输入应用名称或包名搜索...")
        self.search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(self.search_input)
        
        filter_layout.addLayout(search_layout)
        
        # 应用类型筛选
        type_layout = QHBoxLayout()
        type_label = QLabel("应用类型:")
        type_layout.addWidget(type_label)
        
        self.type_combo = QComboBox()
        self.type_combo.addItems(["全部应用", "第三方应用", "系统应用"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        
        filter_layout.addLayout(type_layout)
        
        # 排序方式
        sort_layout = QHBoxLayout()
        sort_label = QLabel("排序:")
        sort_layout.addWidget(sort_label)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["按名称", "按安装时间", "按大小"])
        self.sort_combo.currentTextChanged.connect(self.on_sort_changed)
        sort_layout.addWidget(self.sort_combo)
        
        filter_layout.addLayout(sort_layout)
        
        filter_layout.addStretch()
        control_layout.addLayout(filter_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("刷新列表")
        self.refresh_button.clicked.connect(self.refresh_apps)
        button_layout.addWidget(self.refresh_button)
        
        self.uninstall_button = QPushButton("卸载选中")
        self.uninstall_button.setProperty("class", "primary")
        self.uninstall_button.clicked.connect(self.uninstall_apps)
        self.uninstall_button.setEnabled(False)
        button_layout.addWidget(self.uninstall_button)
        
        button_layout.addStretch()
        control_layout.addLayout(button_layout)
        
        layout.addWidget(control_group)
        
        # 应用列表区域
        apps_group = QGroupBox("应用列表")
        apps_layout = QVBoxLayout(apps_group)
        
        # 应用列表（网格布局占位）
        self.apps_list = QListWidget()
        self.apps_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.apps_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.apps_list.setGridSize(QSize(120, 140))
        self.apps_list.setSpacing(10)
        self.apps_list.itemSelectionChanged.connect(self.on_selection_changed)
        apps_layout.addWidget(self.apps_list)
        
        layout.addWidget(apps_group)
        
        # 应用信息区域
        info_group = QGroupBox("应用详情")
        info_layout = QVBoxLayout(info_group)
        
        self.app_info = QLabel("选择应用查看详细信息")
        self.app_info.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']};")
        self.app_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.app_info.setMinimumHeight(100)
        info_layout.addWidget(self.app_info)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        self.apply_styles()
        
        # 初始化占位数据
        self.setup_placeholder_data()
        
        self.logger.info("应用管理页面UI初始化完成")
    
    def apply_styles(self):
        """应用样式"""
        group_style = AppleStyle.get_card_style()
        for group in self.findChildren(QGroupBox):
            group.setStyleSheet(f"""
                QGroupBox {{
                    {group_style}
                    font-weight: bold;
                    margin-top: 10px;
                }}
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }}
            """)
        
        # 应用列表样式
        self.apps_list.setStyleSheet(f"""
            QListWidget {{
                background-color: {AppleStyle.COLORS['background']};
                border: 1px solid {AppleStyle.COLORS['border']};
                border-radius: {AppleStyle.BORDER_RADIUS['medium']}px;
            }}
            QListWidget::item {{
                border: 1px solid {AppleStyle.COLORS['divider']};
                border-radius: {AppleStyle.BORDER_RADIUS['medium']}px;
                padding: 10px;
                margin: 5px;
            }}
            QListWidget::item:hover {{
                background-color: {AppleStyle.COLORS['surface']};
                border-color: {AppleStyle.COLORS['primary']};
            }}
            QListWidget::item:selected {{
                background-color: {AppleStyle.COLORS['primary']};
                color: white;
            }}
        """)
    
    def setup_placeholder_data(self):
        """设置占位数据"""
        placeholder_apps = [
            {"name": "设置", "package": "com.android.settings", "type": "系统", "version": "1.0"},
            {"name": "文件管理器", "package": "com.android.filemanager", "type": "系统", "version": "2.1"},
            {"name": "当贝市场", "package": "com.dangbei.tv", "type": "第三方", "version": "4.0"},
            {"name": "腾讯视频", "package": "com.tencent.video", "type": "第三方", "version": "8.5"},
            {"name": "爱奇艺", "package": "com.qiyi.tv", "type": "第三方", "version": "9.0"},
        ]
        
        for app in placeholder_apps:
            self.add_app_item(app)
    
    def add_app_item(self, app_info):
        """添加应用项到列表"""
        item = QListWidgetItem()
        item.setSizeHint(QSize(100, 120))
        
        # 创建自定义的应用项部件
        app_widget = self.create_app_widget(app_info)
        self.apps_list.addItem(item)
        self.apps_list.setItemWidget(item, app_widget)
    
    def create_app_widget(self, app_info):
        """创建应用项部件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # 应用图标（占位）
        icon_label = QLabel("📱")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                background-color: {AppleStyle.COLORS['surface']};
                border-radius: {AppleStyle.BORDER_RADIUS['circle']}px;
                min-width: 64px;
                min-height: 64px;
            }}
        """)
        layout.addWidget(icon_label)
        
        # 应用名称
        name_label = QLabel(app_info["name"])
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet(f"""
            QLabel {{
                font-size: 12px;
                font-weight: bold;
                color: {AppleStyle.COLORS['text_primary']};
            }}
        """)
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # 应用信息
        info_label = QLabel(f"v{app_info['version']} | {app_info['type']}")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet(f"""
            QLabel {{
                font-size: 9px;
                color: {AppleStyle.COLORS['text_secondary']};
            }}
        """)
        layout.addWidget(info_label)
        
        return widget
    
    def refresh_apps(self):
        """刷新应用列表 - 从设备获取真实应用列表"""
        self.apps_list.clear()
        
        if not self.connected_device:
            self.show_message("请先连接设备")
            self.setup_placeholder_data()
            return
        
        try:
            device_serial = self.connected_device.get('serial')
            apps = self.get_installed_apps(device_serial)
            
            if apps:
                for app in apps:
                    self.add_app_item(app)
                self.logger.info(f"已加载 {len(apps)} 个应用")
            else:
                self.show_message("未找到应用或获取失败，显示示例数据")
                self.setup_placeholder_data()
                
        except Exception as e:
            self.logger.error(f"获取应用列表失败: {e}")
            self.show_message("获取应用列表失败，显示示例数据")
            self.setup_placeholder_data()
    
    def get_installed_apps(self, device_serial):
        """从设备获取已安装应用列表"""
        try:
            adb_manager = get_adb_manager()
            
            # 获取所有已安装应用
            args = ["-s", device_serial, "shell", "pm", "list", "packages", "-3"]  # 只获取第三方应用
            result = adb_manager.run_adb_command(args, timeout=10)
            
            apps = []
            if result['success'] and result['stdout']:
                lines = result['stdout'].strip().split('\n')
                for line in lines:
                    if line.startswith('package:'):
                        package_name = line.replace('package:', '').strip()
                        
                        # 获取应用详细信息
                        app_info = self.get_app_info(device_serial, package_name)
                        if app_info:
                            apps.append(app_info)
            
            return apps
            
        except Exception as e:
            self.logger.error(f"获取应用列表错误: {e}")
            return []
    
    def get_app_info(self, device_serial, package_name):
        """获取应用详细信息"""
        try:
            adb_manager = get_adb_manager()
            
            # 获取应用名称
            args = ["-s", device_serial, "shell", "dumpsys", "package", package_name, "|", "grep", "versionName"]
            result = adb_manager.run_adb_command(args, timeout=5)
            
            version = "1.0"
            if result['success'] and result['stdout']:
                # 解析版本信息
                version_line = result['stdout'].strip()
                if 'versionName=' in version_line:
                    version = version_line.split('versionName=')[1].split()[0]
            
            # 简化名称（使用包名的最后一部分）
            app_name = package_name.split('.')[-1].capitalize()
            
            return {
                "name": app_name,
                "package": package_name,
                "type": "第三方",
                "version": version
            }
            
        except Exception as e:
            self.logger.error(f"获取应用信息错误: {e}")
            return {
                "name": package_name,
                "package": package_name,
                "type": "第三方", 
                "version": "1.0"
            }
    
    def on_search_changed(self, text):
        """搜索文本改变回调"""
        self.logger.debug(f"搜索条件改变: {text}")
        # 实现搜索过滤逻辑
    
    def on_type_changed(self, type_text):
        """应用类型改变回调"""
        self.logger.debug(f"应用类型过滤: {type_text}")
        # 实现类型过滤逻辑
    
    def on_sort_changed(self, sort_text):
        """排序方式改变回调"""
        self.logger.debug(f"排序方式: {sort_text}")
        # 实现排序逻辑
    
    def on_selection_changed(self):
        """选择改变回调"""
        selected_items = self.apps_list.selectedItems()
        self.uninstall_button.setEnabled(len(selected_items) > 0)
        
        if selected_items:
            # 显示选中应用的详细信息
            self.app_info.setText(f"已选中 {len(selected_items)} 个应用")
        else:
            self.app_info.setText("选择应用查看详细信息")
    
    def uninstall_apps(self):
        """卸载选中应用"""
        selected_items = self.apps_list.selectedItems()
        if selected_items:
            self.logger.info(f"开始卸载 {len(selected_items)} 个应用")
            # 实现卸载逻辑
    
    def on_activated(self):
        """页面激活时的回调"""
        self.logger.debug("应用管理页面已激活")
        
        # 获取当前设备信息
        current_device = get_current_device()
        if current_device:
            self.connected_device = {
                'serial': current_device.serial,
                'name': current_device.name or '未知设备',
                'model': current_device.model or '未知型号'
            }
            self.logger.info(f"页面激活，当前设备: {self.connected_device['name']}")
            self.refresh_apps()
        else:
            self.logger.info("页面激活，未连接设备，显示示例数据")
            self.connected_device = None
            self.setup_placeholder_data()
    
    def on_device_changed(self, device_info):
        """设备状态变化回调"""
        if device_info:
            self.connected_device = {
                'serial': device_info.serial,
                'name': device_info.name or '未知设备',
                'model': device_info.model or '未知型号'
            }
            self.logger.info(f"设备已连接: {self.connected_device['name']}")
            # 如果当前正在显示应用管理页面，自动刷新应用列表
            self.refresh_apps()
        else:
            self.connected_device = None
            self.logger.info("设备已断开连接")
            # 清除应用列表，显示占位数据
            self.apps_list.clear()
            self.setup_placeholder_data()
    
    def show_message(self, message):
        """显示消息"""
        self.logger.info(message)
        # 使用简单的日志显示，避免对话框导致的线程问题
        print(f"应用管理页面提示: {message}")
    
    def cleanup(self):
        """清理资源"""
        # 移除设备监听器
        device_manager = get_device_manager()
        device_manager.remove_listener(self.on_device_changed)
        
        self.logger.debug("应用管理页面资源已清理")