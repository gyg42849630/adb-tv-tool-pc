# -*- coding: utf-8 -*-
"""
系统设置页面
工具设置和配置
"""

import logging
import json
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QLineEdit, QComboBox, QCheckBox,
                             QGroupBox, QSpinBox, QDoubleSpinBox, QSlider,
                             QTabWidget, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont

from adb_tv_tool.utils.style import AppleStyle


class SettingsManager:
    """设置管理器"""
    
    def __init__(self):
        self.settings = QSettings("Comate", "ADB TV Tool")
        self.default_settings = {
            "adb_path": "adb",
            "auto_connect": True,
            "scan_ip_range": "192.168.1.1-255",
            "mirror_fps": 5,
            "mirror_quality": "中",
            "install_timeout": 60,
            "log_level": "INFO",
            "theme": "auto",
            "language": "zh_CN"
        }
    
    def get_setting(self, key, default=None):
        """获取设置值"""
        if default is None:
            default = self.default_settings.get(key)
        return self.settings.value(key, default)
    
    def set_setting(self, key, value):
        """设置值"""
        self.settings.setValue(key, value)
    
    def save_settings(self):
        """保存设置到文件"""
        self.settings.sync()
    
    def reset_settings(self):
        """重置设置为默认值"""
        self.settings.clear()
        for key, value in self.default_settings.items():
            self.settings.setValue(key, value)


class SettingsPage(QWidget):
    """系统设置页面"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.settings")
        self.settings_manager = SettingsManager()
        self.setup_ui()
        self.load_settings()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        
        title = QLabel("系统设置")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        title_layout.addWidget(title)
        
        desc = QLabel("配置工具参数和个性化设置")
        desc.setStyleSheet(f"font-size: 14px; color: {AppleStyle.COLORS['text_secondary']};")
        title_layout.addWidget(desc)
        
        layout.addLayout(title_layout)
        
        # 选项卡区域
        self.tab_widget = QTabWidget()
        
        # 基本设置选项卡
        self.general_tab = self.create_general_tab()
        self.tab_widget.addTab(self.general_tab, "基本设置")
        
        # 设备设置选项卡
        self.device_tab = self.create_device_tab()
        self.tab_widget.addTab(self.device_tab, "设备设置")
        
        # 投屏设置选项卡
        self.mirror_tab = self.create_mirror_tab()
        self.tab_widget.addTab(self.mirror_tab, "投屏设置")
        
        # 安装设置选项卡
        self.install_tab = self.create_install_tab()
        self.tab_widget.addTab(self.install_tab, "安装设置")
        
        # 外观设置选项卡
        self.appearance_tab = self.create_appearance_tab()
        self.tab_widget.addTab(self.appearance_tab, "外观设置")
        
        layout.addWidget(self.tab_widget)
        
        # 控制按钮区域
        control_layout = QHBoxLayout()
        
        self.save_button = QPushButton("保存设置")
        self.save_button.setProperty("class", "primary")
        self.save_button.clicked.connect(self.save_settings)
        control_layout.addWidget(self.save_button)
        
        self.apply_button = QPushButton("应用设置")
        self.apply_button.clicked.connect(self.apply_settings)
        control_layout.addWidget(self.apply_button)
        
        self.reset_button = QPushButton("恢复默认")
        self.reset_button.clicked.connect(self.reset_settings)
        control_layout.addWidget(self.reset_button)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        layout.addStretch()
        
        self.apply_styles()
        
        self.logger.info("系统设置页面UI初始化完成")
    
    def create_general_tab(self):
        """创建基本设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # ADB路径设置
        adb_group = QGroupBox("ADB配置")
        adb_layout = QVBoxLayout(adb_group)
        
        adb_path_layout = QHBoxLayout()
        adb_label = QLabel("ADB路径:")
        adb_path_layout.addWidget(adb_label)
        
        self.adb_path_input = QLineEdit()
        self.adb_path_input.setPlaceholderText("自动检测系统ADB路径")
        adb_path_layout.addWidget(self.adb_path_input)
        
        self.adb_browse_button = QPushButton("浏览")
        self.adb_browse_button.clicked.connect(self.browse_adb_path)
        adb_path_layout.addWidget(self.adb_browse_button)
        
        adb_layout.addLayout(adb_path_layout)
        layout.addWidget(adb_group)
        
        # 日志设置
        log_group = QGroupBox("日志配置")
        log_layout = QVBoxLayout(log_group)
        
        log_level_layout = QHBoxLayout()
        log_label = QLabel("日志级别:")
        log_level_layout.addWidget(log_label)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItems(["DEBUG", "INFO", "WARNING", "ERROR"])
        log_level_layout.addWidget(self.log_level_combo)
        
        log_level_layout.addStretch()
        log_layout.addLayout(log_level_layout)
        
        self.auto_save_logs = QCheckBox("自动保存日志文件")
        log_layout.addWidget(self.auto_save_logs)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        return tab
    
    def create_device_tab(self):
        """创建设备设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 连接设置
        connect_group = QGroupBox("设备连接")
        connect_layout = QVBoxLayout(connect_group)
        
        self.auto_connect = QCheckBox("启动时自动连接上次设备")
        connect_layout.addWidget(self.auto_connect)
        
        self.auto_scan = QCheckBox("页面激活时自动扫描设备")
        connect_layout.addWidget(self.auto_scan)
        
        # IP扫描范围
        ip_layout = QHBoxLayout()
        ip_label = QLabel("IP扫描范围:")
        ip_layout.addWidget(ip_label)
        
        self.ip_range_input = QLineEdit()
        self.ip_range_input.setPlaceholderText("例如: 192.168.1.1-255")
        ip_layout.addWidget(self.ip_range_input)
        
        connect_layout.addLayout(ip_layout)
        layout.addWidget(connect_group)
        
        layout.addStretch()
        return tab
    
    def create_mirror_tab(self):
        """创建投屏设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 投屏质量设置
        quality_group = QGroupBox("投屏质量")
        quality_layout = QVBoxLayout(quality_group)
        
        # FPS设置
        fps_layout = QHBoxLayout()
        fps_label = QLabel("帧率 (FPS):")
        fps_layout.addWidget(fps_label)
        
        self.fps_slider = QSlider(Qt.Orientation.Horizontal)
        self.fps_slider.setRange(1, 30)
        self.fps_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.fps_slider.setTickInterval(5)
        fps_layout.addWidget(self.fps_slider)
        
        self.fps_label = QLabel("5")
        fps_layout.addWidget(self.fps_label)
        
        quality_layout.addLayout(fps_layout)
        
        # 质量设置
        quality_setting_layout = QHBoxLayout()
        quality_setting_label = QLabel("默认质量:")
        quality_setting_layout.addWidget(quality_setting_label)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["低", "中", "高"])
        quality_setting_layout.addWidget(self.quality_combo)
        
        quality_setting_layout.addStretch()
        quality_layout.addLayout(quality_setting_layout)
        
        layout.addWidget(quality_group)
        
        layout.addStretch()
        return tab
    
    def create_install_tab(self):
        """创建安装设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 安装超时设置
        timeout_group = QGroupBox("安装超时")
        timeout_layout = QVBoxLayout(timeout_group)
        
        timeout_setting_layout = QHBoxLayout()
        timeout_label = QLabel("安装超时时间(秒):")
        timeout_setting_layout.addWidget(timeout_label)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(10, 300)
        self.timeout_spin.setSuffix(" 秒")
        timeout_setting_layout.addWidget(self.timeout_spin)
        
        timeout_setting_layout.addStretch()
        timeout_layout.addLayout(timeout_setting_layout)
        
        layout.addWidget(timeout_group)
        
        # 安装选项
        options_group = QGroupBox("默认安装选项")
        options_layout = QVBoxLayout(options_group)
        
        self.default_force_install = QCheckBox("默认启用强制安装")
        options_layout.addWidget(self.default_force_install)
        
        self.default_allow_downgrade = QCheckBox("默认允许降级安装")
        options_layout.addWidget(self.default_allow_downgrade)
        
        layout.addWidget(options_group)
        
        layout.addStretch()
        return tab
    
    def create_appearance_tab(self):
        """创建外观设置选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        # 主题设置
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout(theme_group)
        
        theme_setting_layout = QHBoxLayout()
        theme_label = QLabel("主题:")
        theme_setting_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["自动", "浅色", "深色"])
        theme_setting_layout.addWidget(self.theme_combo)
        
        theme_setting_layout.addStretch()
        theme_layout.addLayout(theme_setting_layout)
        
        # 语言设置
        language_layout = QHBoxLayout()
        language_label = QLabel("语言:")
        language_layout.addWidget(language_label)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["中文", "English"])
        language_layout.addWidget(self.language_combo)
        
        language_layout.addStretch()
        theme_layout.addLayout(language_layout)
        
        layout.addWidget(theme_group)
        
        layout.addStretch()
        return tab
    
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
    
    def browse_adb_path(self):
        """浏览ADB路径"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "选择ADB执行文件", "", "Executable Files (*.exe)"
        )
        
        if file_path:
            self.adb_path_input.setText(file_path)
    
    def load_settings(self):
        """加载设置"""
        # ADB设置
        self.adb_path_input.setText(self.settings_manager.get_setting("adb_path"))
        
        # 设备设置
        self.auto_connect.setChecked(self.settings_manager.get_setting("auto_connect", True))
        self.auto_scan.setChecked(self.settings_manager.get_setting("auto_scan", True))
        self.ip_range_input.setText(self.settings_manager.get_setting("scan_ip_range"))
        
        # 投屏设置
        fps = int(self.settings_manager.get_setting("mirror_fps", 5))
        self.fps_slider.setValue(fps)
        self.fps_label.setText(str(fps))
        self.quality_combo.setCurrentText(self.settings_manager.get_setting("mirror_quality"))
        
        # 安装设置
        self.timeout_spin.setValue(int(self.settings_manager.get_setting("install_timeout", 60)))
        
        # 外观设置
        self.theme_combo.setCurrentText(self.settings_manager.get_setting("theme", "auto"))
        self.language_combo.setCurrentText(self.settings_manager.get_setting("language", "中文"))
        
        # 连接信号
        self.fps_slider.valueChanged.connect(lambda v: self.fps_label.setText(str(v)))
    
    def save_settings(self):
        """保存设置"""
        try:
            # 保存各项设置
            self.settings_manager.set_setting("adb_path", self.adb_path_input.text())
            self.settings_manager.set_setting("auto_connect", self.auto_connect.isChecked())
            self.settings_manager.set_setting("auto_scan", self.auto_scan.isChecked())
            self.settings_manager.set_setting("scan_ip_range", self.ip_range_input.text())
            self.settings_manager.set_setting("mirror_fps", self.fps_slider.value())
            self.settings_manager.set_setting("mirror_quality", self.quality_combo.currentText())
            self.settings_manager.set_setting("install_timeout", self.timeout_spin.value())
            self.settings_manager.set_setting("theme", self.theme_combo.currentText())
            self.settings_manager.set_setting("language", self.language_combo.currentText())
            
            self.settings_manager.save_settings()
            
            QMessageBox.information(self, "成功", "设置已保存")
            self.logger.info("设置已保存")
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存设置失败: {str(e)}")
            self.logger.error(f"保存设置失败: {str(e)}")
    
    def apply_settings(self):
        """应用设置（立即生效）"""
        self.save_settings()
        # 这里可以添加实时生效的设置逻辑
        self.logger.info("设置已应用")
    
    def reset_settings(self):
        """重置设置为默认值"""
        reply = QMessageBox.question(
            self, "确认", 
            "确定要恢复默认设置吗？这将清除所有自定义设置。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings_manager.reset_settings()
            self.load_settings()
            self.logger.info("设置已重置为默认值")
    
    def on_activated(self):
        """页面激活时的回调"""
        self.logger.debug("系统设置页面已激活")
        self.load_settings()
    
    def cleanup(self):
        """清理资源"""
        self.logger.debug("系统设置页面资源已清理")