# -*- coding: utf-8 -*-
"""
安装执行页面
执行APK安装操作
"""

import logging
import subprocess
import threading
import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QProgressBar, QTextEdit, QGroupBox,
                             QCheckBox, QFrame)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from adb_tv_tool.utils.style import AppleStyle


class InstallWorker(QThread):
    """安装工作线程"""
    
    # 信号定义
    install_started = pyqtSignal()
    install_progress = pyqtSignal(int, str)
    install_finished = pyqtSignal(bool, str)
    log_message = pyqtSignal(str)
    
    def __init__(self, apk_files, device_serial=None, options=None):
        super().__init__()
        self.apk_files = apk_files
        self.device_serial = device_serial
        self.options = options or {}
        self.logger = logging.getLogger("install.worker")
    
    def run(self):
        """执行安装"""
        self.install_started.emit()
        success_count = 0
        total_count = len(self.apk_files)
        
        try:
            for i, apk_file in enumerate(self.apk_files):
                current_num = i + 1
                progress = int((current_num - 1) / total_count * 100)
                
                self.install_progress.emit(progress, f"正在安装 {current_num}/{total_count}")
                self.log_message.emit(f"安装文件: {apk_file}")
                
                if self.install_apk(apk_file):
                    success_count += 1
                    self.log_message.emit(f"✓ 安装成功: {apk_file}")
                else:
                    self.log_message.emit(f"✗ 安装失败: {apk_file}")
                
                time.sleep(0.5)  # 避免安装过快
            
            # 完成安装
            self.install_progress.emit(100, "安装完成")
            
            if success_count == total_count:
                self.install_finished.emit(True, f"全部 {total_count} 个应用安装成功")
            else:
                self.install_finished.emit(False, f"完成 {success_count}/{total_count} 个应用安装")
                
        except Exception as e:
            self.install_finished.emit(False, f"安装过程出错: {str(e)}")
    
    def install_apk(self, apk_file):
        """安装单个APK文件"""
        try:
            adb_cmd = ["adb"]
            if self.device_serial:
                adb_cmd.extend(["-s", self.device_serial])
            
            adb_cmd.extend(["install", "-r"])  # -r 表示替换已安装的应用
            
            # 添加选项
            if self.options.get("force_install", False):
                adb_cmd.append("-f")  # 强制安装
            if self.options.get("allow_downgrade", False):
                adb_cmd.append("-d")  # 允许降级安装
            
            adb_cmd.append(apk_file)
            
            result = subprocess.run(adb_cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0 and "Success" in result.stdout:
                return True
            else:
                self.log_message.emit(f"安装错误: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log_message.emit("安装超时")
            return False
        except Exception as e:
            self.log_message.emit(f"安装异常: {str(e)}")
            return False


class InstallExecutePage(QWidget):
    """安装执行页面"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.install_execute")
        self.install_worker = None
        self.connected_device = None
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        
        title = QLabel("安装执行")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        title_layout.addWidget(title)
        
        desc = QLabel("执行APK安装操作，支持批量安装和安装选项配置")
        desc.setStyleSheet(f"font-size: 14px; color: {AppleStyle.COLORS['text_secondary']};")
        title_layout.addWidget(desc)
        
        layout.addLayout(title_layout)
        
        # 安装状态区域
        status_group = QGroupBox("安装状态")
        status_layout = QVBoxLayout(status_group)
        
        # 进度信息
        progress_layout = QHBoxLayout()
        
        self.progress_label = QLabel("准备安装")
        self.progress_label.setStyleSheet(f"font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        progress_layout.addWidget(self.progress_label)
        
        progress_layout.addStretch()
        
        self.install_count = QLabel("0/0")
        self.install_count.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']};")
        progress_layout.addWidget(self.install_count)
        
        status_layout.addLayout(progress_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        status_layout.addWidget(self.progress_bar)
        
        layout.addWidget(status_group)
        
        # 安装选项区域
        options_group = QGroupBox("安装选项")
        options_layout = QVBoxLayout(options_group)
        
        # 安装选项
        self.force_install_check = QCheckBox("强制安装（-f）")
        self.force_install_check.setToolTip("强制安装即使版本较旧或签名不同")
        options_layout.addWidget(self.force_install_check)
        
        self.allow_downgrade_check = QCheckBox("允许降级安装（-d）")
        self.allow_downgrade_check.setToolTip("允许安装比当前版本更旧的应用")
        options_layout.addWidget(self.allow_downgrade_check)
        
        self.replace_existing_check = QCheckBox("替换已安装应用（-r）")
        self.replace_existing_check.setChecked(True)
        self.replace_existing_check.setToolTip("如果应用已存在则替换安装")
        options_layout.addWidget(self.replace_existing_check)
        
        layout.addWidget(options_group)
        
        # 控制按钮区域
        control_group = QGroupBox("安装控制")
        control_layout = QHBoxLayout(control_group)
        
        self.start_button = QPushButton("开始安装")
        self.start_button.setProperty("class", "primary")
        self.start_button.clicked.connect(self.start_installation)
        control_layout.addWidget(self.start_button)
        
        self.pause_button = QPushButton("暂停安装")
        self.pause_button.clicked.connect(self.pause_installation)
        self.pause_button.setEnabled(False)
        control_layout.addWidget(self.pause_button)
        
        self.stop_button = QPushButton("停止安装")
        self.stop_button.clicked.connect(self.stop_installation)
        self.stop_button.setEnabled(False)
        control_layout.addWidget(self.stop_button)
        
        control_layout.addStretch()
        layout.addWidget(control_group)
        
        # 安装日志区域
        log_group = QGroupBox("安装日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(300)
        log_layout.addWidget(self.log_text)
        
        # 日志控制
        log_control_layout = QHBoxLayout()
        
        self.clear_log_button = QPushButton("清空日志")
        self.clear_log_button.clicked.connect(self.clear_log)
        log_control_layout.addWidget(self.clear_log_button)
        
        self.save_log_button = QPushButton("保存日志")
        self.save_log_button.clicked.connect(self.save_log)
        log_control_layout.addWidget(self.save_log_button)
        
        log_control_layout.addStretch()
        log_layout.addLayout(log_control_layout)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        self.apply_styles()
        
        self.logger.info("安装执行页面UI初始化完成")
    
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
    
    def set_apk_files(self, apk_files):
        """设置要安装的APK文件"""
        self.apk_files = apk_files
        self.install_count.setText(f"0/{len(apk_files)}")
        self.log_text.append(f"已加载 {len(apk_files)} 个APK文件")
    
    def set_connected_device(self, device):
        """设置连接的设备"""
        self.connected_device = device
        if device:
            device_name = device.get('name', '未知设备')
            self.log_text.append(f"目标设备: {device_name}")
    
    def start_installation(self):
        """开始安装"""
        if not hasattr(self, 'apk_files') or not self.apk_files:
            self.log_text.append("错误: 没有可安装的APK文件")
            return
        
        if not self.connected_device:
            self.log_text.append("错误: 请先连接设备")
            return
        
        # 准备安装选项
        options = {
            "force_install": self.force_install_check.isChecked(),
            "allow_downgrade": self.allow_downgrade_check.isChecked(),
        }
        
        # 启动安装线程
        self.install_worker = InstallWorker(
            self.apk_files, 
            self.connected_device.get('serial'),
            options
        )
        
        self.install_worker.install_started.connect(self.on_install_started)
        self.install_worker.install_progress.connect(self.on_install_progress)
        self.install_worker.install_finished.connect(self.on_install_finished)
        self.install_worker.log_message.connect(self.on_log_message)
        self.install_worker.start()
        
        self.start_button.setEnabled(False)
        self.pause_button.setEnabled(True)
        self.stop_button.setEnabled(True)
    
    def pause_installation(self):
        """暂停安装"""
        # 暂停功能暂不实现
        self.log_text.append("暂停功能开发中")
    
    def stop_installation(self):
        """停止安装"""
        if self.install_worker and self.install_worker.isRunning():
            self.install_worker.terminate()
            self.install_worker.wait()
        
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        self.log_text.append("安装已停止")
    
    def on_install_started(self):
        """安装开始回调"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("安装进行中")
        self.log_text.append("开始安装APK文件...")
    
    def on_install_progress(self, progress, message):
        """安装进度回调"""
        self.progress_bar.setValue(progress)
        self.progress_label.setText(message)
        
        # 更新安装计数
        if "/" in message:
            parts = message.split()
            for part in parts:
                if "/" in part:
                    self.install_count.setText(part)
                    break
    
    def on_install_finished(self, success, message):
        """安装完成回调"""
        self.start_button.setEnabled(True)
        self.pause_button.setEnabled(False)
        self.stop_button.setEnabled(False)
        
        color = AppleStyle.COLORS["success"] if success else AppleStyle.COLORS["error"]
        self.progress_label.setText(message)
        self.progress_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        
        self.log_text.append(f"安装完成: {message}")
    
    def on_log_message(self, message):
        """日志消息回调"""
        self.log_text.append(message)
    
    def clear_log(self):
        """清空日志"""
        self.log_text.clear()
        self.log_text.append("日志已清空")
    
    def save_log(self):
        """保存日志"""
        self.log_text.append("日志保存功能开发中")
    
    def on_activated(self):
        """页面激活时的回调"""
        self.logger.debug("安装执行页面已激活")
    
    def cleanup(self):
        """清理资源"""
        if self.install_worker and self.install_worker.isRunning():
            self.install_worker.terminate()
            self.install_worker.wait()
        
        self.logger.debug("安装执行页面资源已清理")