# -*- coding: utf-8 -*-
"""
环境检测页面
检查ADB环境和设备状态
"""

import logging
import subprocess
import sys
from pathlib import Path

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTextEdit, QFrame,
                             QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from adb_tv_tool.utils.style import AppleStyle
from adb_tv_tool.utils.adb_manager import get_adb_manager


class ADBEnvironmentChecker(QThread):
    """ADB环境检测线程"""
    
    # 信号定义
    check_started = pyqtSignal()
    check_finished = pyqtSignal(dict)
    progress_updated = pyqtSignal(int, str)
    log_message = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("adb.environment_checker")
    
    def run(self):
        """执行环境检测"""
        self.check_started.emit()
        results = {}
        
        try:
            # 检测ADB命令可用性
            self.progress_updated.emit(10, "检查ADB命令...")
            adb_available = self.check_adb_availability()
            results["adb_available"] = adb_available
            self.log_message.emit(f"ADB命令可用: {adb_available}")
            
            if adb_available:
                # 检测ADB版本
                self.progress_updated.emit(30, "检查ADB版本...")
                adb_version = self.get_adb_version()
                results["adb_version"] = adb_version
                self.log_message.emit(f"ADB版本: {adb_version}")
                
                # 检测设备连接
                self.progress_updated.emit(50, "扫描连接设备...")
                devices = self.get_connected_devices()
                results["devices"] = devices
                self.log_message.emit(f"发现设备数量: {len(devices)}")
                
                # 检测网络状态
                self.progress_updated.emit(70, "检查网络连接...")
                network_status = self.check_network_status()
                results["network_status"] = network_status
                self.log_message.emit(f"网络状态: {network_status}")
            else:
                results["adb_version"] = "未知"
                results["devices"] = []
                results["network_status"] = "未知"
            
            # 检测系统环境
            self.progress_updated.emit(90, "检查系统环境...")
            system_info = self.get_system_info()
            results["system_info"] = system_info
            self.log_message.emit(f"系统信息: {system_info}")
            
            self.progress_updated.emit(100, "检测完成")
            
        except Exception as e:
            self.log_message.emit(f"环境检测出错: {str(e)}")
            results["error"] = str(e)
        
        self.check_finished.emit(results)
    
    def check_adb_availability(self):
        """检测ADB命令是否可用"""
        try:
            adb_manager = get_adb_manager()
            return adb_manager.check_adb_availability()
        except Exception as e:
            self.log_message.emit(f"ADB命令检查异常: {str(e)}")
            return False
    
    def get_adb_version(self):
        """获取ADB版本信息"""
        try:
            adb_manager = get_adb_manager()
            result = adb_manager.run_adb_command(['version'], timeout=10)
            if result['success']:
                return result['stdout'].strip().split('\n')[0]
            return "未知"
        except Exception:
            return "未知"
    
    def get_connected_devices(self):
        """获取已连接的设备列表"""
        try:
            adb_manager = get_adb_manager()
            result = adb_manager.run_adb_command(['devices'], timeout=10)
            if result['success']:
                lines = result['stdout'].strip().split('\n')[1:]  # 跳过标题行
                devices = []
                for line in lines:
                    if line.strip() and not line.startswith('*'):
                        parts = line.split('\t')
                        if len(parts) >= 2:
                            devices.append({
                                "serial": parts[0],
                                "status": parts[1]
                            })
                return devices
            return []
        except Exception as e:
            self.log_message.emit(f"设备检测异常: {str(e)}")
            return []
    
    def check_network_status(self):
        """检查网络连接状态"""
        try:
            # 简单的网络连通性测试
            result = subprocess.run(["ping", "-n", "1", "8.8.8.8"], 
                                  capture_output=True, timeout=5)
            return "正常" if result.returncode == 0 else "异常"
        except Exception as e:
            self.log_message.emit(f"网络检测异常: {str(e)}")
            return "异常"
    
    def get_system_info(self):
        """获取系统信息"""
        try:
            system = sys.platform
            if system == "win32":
                import platform
                return f"Windows {platform.release()}"
            elif system == "darwin":
                import platform
                return f"macOS {platform.mac_ver()[0]}"
            elif system == "linux":
                import platform
                return f"Linux {platform.release()}"
            else:
                return system
        except Exception:
            return "未知"


class EnvironmentCheckPage(QWidget):
    """环境检测页面"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.environment_check")
        self.checker = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        
        title = QLabel("环境检测")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        title_layout.addWidget(title)
        
        desc = QLabel("检查ADB环境和设备连接状态，确保工具正常运行")
        desc.setStyleSheet(f"font-size: 14px; color: {AppleStyle.COLORS['text_secondary']};")
        title_layout.addWidget(desc)
        
        layout.addLayout(title_layout)
        
        # 控制按钮区域
        control_layout = QHBoxLayout()
        
        self.check_button = QPushButton("开始检测")
        self.check_button.setProperty("class", "primary")
        self.check_button.clicked.connect(self.start_check)
        control_layout.addWidget(self.check_button)
        
        self.reset_button = QPushButton("重置")
        self.reset_button.clicked.connect(self.reset_check)
        control_layout.addWidget(self.reset_button)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # 检测结果区域
        results_group = QGroupBox("检测结果")
        results_layout = QGridLayout(results_group)
        results_layout.setSpacing(10)
        
        # 各项检测结果标签
        self.result_labels = {}
        results = [
            ("ADB命令", "adb_available"),
            ("ADB版本", "adb_version"), 
            ("设备连接", "devices"),
            ("网络状态", "network_status"),
            ("系统环境", "system_info")
        ]
        
        for i, (label_text, key) in enumerate(results):
            label = QLabel(f"{label_text}:")
            label.setStyleSheet(f"font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
            results_layout.addWidget(label, i, 0)
            
            value_label = QLabel("待检测")
            value_label.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']};")
            results_layout.addWidget(value_label, i, 1)
            self.result_labels[key] = value_label
        
        layout.addWidget(results_group)
        
        # 日志区域
        log_group = QGroupBox("检测日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        self.apply_styles()
        
        self.logger.info("环境检测页面UI初始化完成")
    
    def apply_styles(self):
        """应用样式"""
        results_group_style = AppleStyle.get_card_style()
        self.findChild(QGroupBox).setStyleSheet(f"""
            QGroupBox {{
                {results_group_style}
                font-weight: bold;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """)
    
    def start_check(self):
        """开始环境检测"""
        self.check_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 清空之前的日志和结果
        self.log_text.clear()
        for label in self.result_labels.values():
            label.setText("检测中...")
            label.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']};")
        
        # 启动检测线程
        self.checker = ADBEnvironmentChecker()
        self.checker.check_started.connect(self.on_check_started)
        self.checker.progress_updated.connect(self.on_progress_updated)
        self.checker.log_message.connect(self.on_log_message)
        self.checker.check_finished.connect(self.on_check_finished)
        self.checker.start()
    
    def reset_check(self):
        """重置检测状态"""
        if self.checker and self.checker.isRunning():
            self.checker.terminate()
            self.checker.wait()
        
        self.check_button.setEnabled(True)
        self.reset_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        for key, label in self.result_labels.items():
            label.setText("待检测")
            label.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']};")
        
        self.log_text.clear()
    
    def on_check_started(self):
        """检测开始回调"""
        self.log_text.append("开始环境检测...")
    
    def on_progress_updated(self, progress, message):
        """进度更新回调"""
        self.progress_bar.setValue(progress)
        self.log_text.append(f"[{progress}%] {message}")
    
    def on_log_message(self, message):
        """日志消息回调"""
        self.log_text.append(message)
    
    def on_check_finished(self, results):
        """检测完成回调"""
        try:
            self.check_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            
            # 更新结果显示
            if "error" in results:
                self.log_text.append(f"检测出错: {results['error']}")
                return
            
            # 安全地更新各个检测项的结果
            for key, label in self.result_labels.items():
                try:
                    if key in results:
                        value = results[key]
                        if key == "adb_available":
                            display_value = "可用" if value else "不可用"
                            color = AppleStyle.COLORS["primary"] if value else "#FF6B6B"
                        elif key == "devices":
                            display_value = f"{len(value)}个设备" if isinstance(value, list) else str(value)
                            color = AppleStyle.COLORS["primary"] if value else "#FF6B6B"
                        elif key == "network_status":
                            display_value = str(value)
                            color = AppleStyle.COLORS["primary"] if value == "正常" else "#FF6B6B"
                        elif key == "adb_version":
                            display_value = str(value)
                            color = AppleStyle.COLORS["primary"] if value and value != "未知" else "#FF6B6B"
                        elif key == "system_info":
                            display_value = str(value)
                            color = AppleStyle.COLORS["primary"]
                        else:
                            display_value = str(value)
                            color = AppleStyle.COLORS["success"]
                        
                        label.setText(display_value)
                        label.setStyleSheet(f"color: {color};")
                    else:
                        # 如果结果中没有该键，显示为未知
                        label.setText("未知")
                        label.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']};")
                except Exception as e:
                    # 单个结果项处理出错，不影响整体
                    self.logger.error(f"更新结果项 {key} 时出错: {e}")
                    label.setText("错误")
                    label.setStyleSheet(f"color: #FF6B6B;")
            
            self.log_text.append("环境检测完成")
        except Exception as e:
            # 主逻辑出错，但确保界面不会崩溃
            self.logger.error(f"检测完成回调出错: {e}")
            self.log_text.append(f"结果显示错误: {str(e)}")
    
    def on_activated(self):
        """页面激活时的回调"""
        self.logger.debug("环境检测页面已激活")
        # 注意: 环境检测不会在激活时自动运行，需要手动点击"开始检测"按钮
        # 避免ADB命令导致的程序崩溃
        self.log_text.append("请点击'开始检测'按钮进行环境检查")
    
    def cleanup(self):
        """清理资源"""
        if self.checker and self.checker.isRunning():
            self.checker.terminate()
            self.checker.wait()
        
        self.logger.debug("环境检测页面资源已清理")