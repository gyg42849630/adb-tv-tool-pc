#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版ADB电视工具主窗口
集成设备连接、APK安装、屏幕截图功能
"""

import sys
import os
import time
from pathlib import Path
import logging

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QFrame, QTextEdit, QLineEdit,
                             QTabWidget, QGroupBox, QListWidget, QListWidgetItem,
                             QProgressBar, QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon

from adb_tv_tool.utils.style import AppleStyle
from adb_tv_tool.utils.adb_manager import get_adb_manager
from adb_tv_tool.utils.device_manager import get_device_manager, set_current_device, clear_current_device


class SimplifiedMainWindow(QMainWindow):
    """简化版主窗口 - 集成核心功能"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.simplified_main")
        self.current_device = None
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("ADB电视工具 - 简化版")
        self.setMinimumSize(900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        
        title = QLabel("ADB电视工具")
        title.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        title_layout.addWidget(title)
        
        desc = QLabel("简化的电视设备管理工具 - 专注APK安装和屏幕截图")
        desc.setStyleSheet(f"font-size: 14px; color: {AppleStyle.COLORS['text_secondary']};")
        title_layout.addWidget(desc)
        
        layout.addLayout(title_layout)
        
        # 设备连接区域
        device_frame = self.create_device_connection_frame()
        layout.addWidget(device_frame)
        
        # 功能选项卡
        self.tab_widget = QTabWidget()
        
        # APK安装页面
        apk_tab = self.create_apk_install_tab()
        self.tab_widget.addTab(apk_tab, "APK安装")
        
        # 屏幕截图页面
        screenshot_tab = self.create_screenshot_tab()
        self.tab_widget.addTab(screenshot_tab, "屏幕截图")
        
        layout.addWidget(self.tab_widget)
        
        # 指令监控区域
        log_frame = self.create_command_log_frame()
        layout.addWidget(log_frame)
        
        # 设置样式
        self.apply_styles()
        
        self.logger.info("简化版主窗口初始化完成")
    
    def create_device_connection_frame(self):
        """创建设备连接区域"""
        frame = QFrame()
        frame.setStyleSheet(AppleStyle.get_card_style())
        layout = QVBoxLayout(frame)
        
        # 标题
        title = QLabel("设备连接管理")
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        layout.addWidget(title)
        
        # IP地址输入和连接控制
        ip_layout = QHBoxLayout()
        
        ip_label = QLabel("设备IP:")
        ip_layout.addWidget(ip_label)
        
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("输入电视设备IP地址 (如: 192.168.1.100:5555)")
        self.ip_input.setText("192.168.1.100:5555")  # 默认IP
        ip_layout.addWidget(self.ip_input)
        
        self.connect_button = QPushButton("连接设备")
        # 直接设置按钮样式，确保文字可见
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #007AFF;
                color: white;
                font-weight: bold;
                border: 1px solid #0055CC;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0056CC;
            }
            QPushButton:pressed {
                background-color: #004499;
            }
        """)
        ip_layout.addWidget(self.connect_button)
        
        self.disconnect_button = QPushButton("断开设备")
        # 为断开设备按钮也设置独立样式，避免悬停时文字消失
        self.disconnect_button.setStyleSheet("""
            QPushButton {
                background-color: #8E8E93;
                color: white;
                font-weight: bold;
                border: 1px solid #6C6C70;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #6C6C70;
                color: white;
            }
            QPushButton:pressed {
                background-color: #4A4A4E;
            }
            QPushButton:disabled {
                background-color: #C7C7CC;
                color: #8E8E93;
            }
        """)
        self.disconnect_button.setEnabled(False)
        ip_layout.addWidget(self.disconnect_button)
        
        layout.addLayout(ip_layout)
        
        # 设备状态显示
        self.device_status = QLabel("设备状态: 未连接")
        self.device_status.setStyleSheet(f"font-size: 14px; color: {AppleStyle.COLORS['text_secondary']};")
        layout.addWidget(self.device_status)
        
        return frame
    
    def create_apk_install_tab(self):
        """创建APK安装页面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # APK文件选择
        file_layout = QHBoxLayout()
        
        file_label = QLabel("APK文件:")
        file_layout.addWidget(file_label)
        
        self.apk_path_input = QLineEdit()
        self.apk_path_input.setPlaceholderText("选择APK文件路径...")
        file_layout.addWidget(self.apk_path_input)
        
        self.browse_button = QPushButton("浏览")
        file_layout.addWidget(self.browse_button)
        
        self.install_button = QPushButton("安装APK")
        self.install_button.setProperty("class", "primary")
        file_layout.addWidget(self.install_button)
        
        layout.addLayout(file_layout)
        
        # 安装进度
        self.install_progress = QProgressBar()
        self.install_progress.setVisible(False)
        layout.addWidget(self.install_progress)
        
        layout.addStretch()
        
        return widget
    
    def create_screenshot_tab(self):
        """创建屏幕截图页面"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 截图控制
        screenshot_layout = QHBoxLayout()
        
        self.screenshot_button = QPushButton("获取截图")
        self.screenshot_button.setProperty("class", "primary")
        screenshot_layout.addWidget(self.screenshot_button)
        
        self.save_screenshot_button = QPushButton("保存截图")
        self.save_screenshot_button.setEnabled(False)
        screenshot_layout.addWidget(self.save_screenshot_button)
        
        screenshot_layout.addStretch()
        layout.addLayout(screenshot_layout)
        
        # 截图显示区域
        screenshot_group = QGroupBox("屏幕截图预览")
        screenshot_group_layout = QVBoxLayout(screenshot_group)
        
        self.screenshot_label = QLabel("截图将显示在这里")
        self.screenshot_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.screenshot_label.setStyleSheet(f"""
            QLabel {{
                background-color: {AppleStyle.COLORS['surface']};
                border: 2px dashed {AppleStyle.COLORS['border']};
                border-radius: {AppleStyle.BORDER_RADIUS['medium']}px;
                min-height: 300px;
            }}
        """)
        screenshot_group_layout.addWidget(self.screenshot_label)
        
        layout.addWidget(screenshot_group)
        
        layout.addStretch()
        
        return widget
    
    def create_command_log_frame(self):
        """创建指令监控区域"""
        frame = QFrame()
        frame.setStyleSheet(AppleStyle.get_card_style())
        layout = QVBoxLayout(frame)
        
        # 标题
        title = QLabel("ADB指令执行过程")
        title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        layout.addWidget(title)
        
        # 日志显示
        self.command_log = QTextEdit()
        self.command_log.setReadOnly(True)
        self.command_log.setMaximumHeight(200)
        self.command_log.setPlaceholderText("ADB命令执行过程和结果将显示在这里...")
        layout.addWidget(self.command_log)
        
        # 控制按钮
        control_layout = QHBoxLayout()
        
        self.clear_log_button = QPushButton("清空日志")
        control_layout.addWidget(self.clear_log_button)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        return frame
    
    def setup_connections(self):
        """设置信号连接"""
        # 设备连接
        self.connect_button.clicked.connect(self.connect_device)
        self.disconnect_button.clicked.connect(self.disconnect_device)
        
        # APK安装
        self.browse_button.clicked.connect(self.browse_apk_file)
        self.install_button.clicked.connect(self.install_apk)
        
        # 屏幕截图
        self.screenshot_button.clicked.connect(self.take_screenshot)
        self.save_screenshot_button.clicked.connect(self.save_screenshot)
        
        # 日志控制
        self.clear_log_button.clicked.connect(self.command_log.clear)
        
        # 设备管理器监听
        device_manager = get_device_manager()
        device_manager.add_listener(self.on_device_changed)
    
    def on_device_changed(self, device_info):
        """设备状态变化回调"""
        if device_info:
            self.current_device = device_info
            self.device_status.setText(f"设备状态: 已连接 ({device_info.name})")
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
            self.log_command(f"📱 设备已连接: {device_info.name} ({device_info.serial})")
        else:
            self.current_device = None
            self.device_status.setText("设备状态: 未连接")
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.log_command("📱 设备已断开")
    
    def connect_device(self):
        """连接设备"""
        ip_address = self.ip_input.text().strip()
        if not ip_address:
            self.log_command("❌ 请输入设备IP地址")
            return
        
        self.log_command(f"🔗 正在连接设备: {ip_address}")
        
        try:
            adb_manager = get_adb_manager()
            result = adb_manager.run_adb_command(["connect", ip_address], timeout=10)
            
            if result['success'] and "connected" in result.get('stdout', ''):
                # 设置设备信息
                set_current_device(
                    serial=ip_address,
                    name=f"电视设备 ({ip_address})",
                    model="未知型号",
                    status="connected"
                )
                self.log_command(f"✅ 设备连接成功: {ip_address}")
            else:
                self.log_command(f"❌ 设备连接失败: {result.get('stderr', '未知错误')}")
                
        except Exception as e:
            self.log_command(f"❌ 连接过程出错: {str(e)}")
    
    def disconnect_device(self):
        """断开设备连接"""
        if self.current_device:
            try:
                adb_manager = get_adb_manager()
                device_serial = self.current_device.serial  # 先保存序列号
                
                self.log_command(f"🔄 正在断开设备: {device_serial}")
                result = adb_manager.run_adb_command(["disconnect", device_serial], timeout=5)
                
                if result['success']:
                    self.log_command(f"✅ ADB断开成功: {device_serial}")
                    clear_current_device()
                    self.log_command(f"✅ 设备状态已清除: {device_serial}")
                else:
                    self.log_command(f"❌ 断开失败: {result.get('stderr', '未知错误')}")
                    
            except Exception as e:
                self.log_command(f"❌ 断开过程出错: {str(e)}")
    
    def browse_apk_file(self):
        """浏览APK文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择APK文件", 
            "", 
            "APK Files (*.apk);;All Files (*)"
        )
        
        if file_path:
            self.apk_path_input.setText(file_path)
            self.log_command(f"📦 选择APK文件: {os.path.basename(file_path)}")
    
    def install_apk(self):
        """安装APK"""
        if not self.current_device:
            self.log_command("❌ 请先连接设备")
            return
        
        apk_path = self.apk_path_input.text().strip()
        if not apk_path or not os.path.exists(apk_path):
            self.log_command("❌ 请选择有效的APK文件")
            return
        
        self.log_command(f"📦 开始安装APK: {os.path.basename(apk_path)}")
        self.install_progress.setVisible(True)
        
        try:
            adb_manager = get_adb_manager()
            result = adb_manager.run_adb_command(
                ["-s", self.current_device.serial, "install", "-r", apk_path], 
                timeout=60
            )
            
            if result['success'] and "Success" in result.get('stdout', ''):
                self.log_command("✅ APK安装成功")
            else:
                self.log_command(f"❌ APK安装失败: {result.get('stderr', '未知错误')}")
                
        except Exception as e:
            self.log_command(f"❌ 安装过程出错: {str(e)}")
        
        self.install_progress.setVisible(False)
    
    def take_screenshot(self):
        """获取屏幕截图"""
        if not self.current_device:
            self.log_command("❌ 请先连接设备")
            return
        
        self.log_command("?? 正在获取屏幕截图...")
        
        try:
            adb_manager = get_adb_manager()
            
            # 方法1: 使用exec-out获取二进制数据
            self.log_command("尝试方法1: exec-out直接获取二进制数据...")
            try:
                result = adb_manager.run_adb_command(
                    ["-s", self.current_device.serial, "exec-out", "screencap", "-p"], 
                    timeout=15,
                    text=False  # 强制使用二进制模式
                )
                
                if result['success'] and result['stdout']:
                    # 直接使用二进制数据
                    screenshot_data = result['stdout']
                    
                    # 详细诊断信息
                    self.log_command(f"🔍 方法1: 收到数据长度: {len(screenshot_data)} 字节")
                    
                    # 处理可能的调试信息前缀
                    png_header = b'\x89PNG\r\n\x1a\n'
                    png_start = screenshot_data.find(png_header)
                    
                    if png_start != -1:
                        # 找到PNG头，跳过前面的调试信息
                        self.log_command(f"🔍 方法1: 在位置 {png_start} 找到PNG文件头")
                        self.screenshot_data = screenshot_data[png_start:]
                        pixmap = QPixmap()
                        if pixmap.loadFromData(self.screenshot_data, "PNG"):
                            # 缩放显示
                            scaled_pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio)
                            self.screenshot_label.setPixmap(scaled_pixmap)
                            self.save_screenshot_button.setEnabled(True)
                            self.log_command("✅ 截图获取成功 (方法1 - 直接二进制)")
                            return
                        else:
                            self.log_command("⚠️ 方法1: QPixmap加载失败，尝试方法2...")
                    else:
                        self.log_command(f"⚠️ 方法1: 无效的PNG数据头")
                        if len(screenshot_data) > 0:
                            # 显示数据开头用于诊断
                            header_preview = screenshot_data[:min(100, len(screenshot_data))]
                            if b'\x00' in header_preview:
                                self.log_command(f"⚠️ 方法1: 数据包含二进制内容，可能不是PNG")
                            else:
                                # 尝试解码为文本查看错误信息
                                try:
                                    text_preview = header_preview.decode('utf-8', errors='ignore')
                                    self.log_command(f"⚠️ 方法1: 数据开头文本: {repr(text_preview)}")
                                except:
                                    self.log_command(f"⚠️ 方法1: 数据头无法解码为文本")
                else:
                    error_info = f"返回码: {result.get('returncode', '未知')}, "
                    error_info += f"错误: {result.get('stderr', '无')}"
                    self.log_command(f"⚠️ 方法1: ADB命令失败 - {error_info}")
                    
            except Exception as e:
                self.log_command(f"⚠️ 方法1: 执行异常: {str(e)}")
            
            self.log_command("⚠️ 方法1失败，尝试方法2...")
            
            # 方法2: 保存到临时文件再读取
            self.log_command("尝试方法2: 保存到设备临时文件...")
            temp_file = f"/sdcard/screenshot_temp_{int(time.time())}.png"
            result = adb_manager.run_adb_command(
                ["-s", self.current_device.serial, "shell", "screencap", "-p", temp_file], 
                timeout=10
            )
            
            if result['success']:
                # 从设备拉取文件
                result = adb_manager.run_adb_command(
                    ["-s", self.current_device.serial, "pull", temp_file, "."], 
                    timeout=15,
                    text=False
                )
                
                if result['success'] and result['stdout']:
                    # 读取本地文件
                    local_filename = os.path.basename(temp_file)
                    if os.path.exists(local_filename):
                        with open(local_filename, 'rb') as f:
                            self.screenshot_data = f.read()
                        
                        pixmap = QPixmap(local_filename)
                        if not pixmap.isNull():
                            # 缩放显示
                            scaled_pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio)
                            self.screenshot_label.setPixmap(scaled_pixmap)
                            self.save_screenshot_button.setEnabled(True)
                            
                            # 清理临时文件
                            try:
                                os.remove(local_filename)
                                adb_manager.run_adb_command(
                                    ["-s", self.current_device.serial, "shell", "rm", temp_file], 
                                    timeout=5
                                )
                            except:
                                pass
                            
                            self.log_command("✅ 截图获取成功 (方法2)")
                            return
                        else:
                            self.log_command("❌ 方法2: 本地文件读取失败")
                    else:
                        self.log_command("❌ 方法2: 文件拉取失败")
                else:
                    self.log_command(f"❌ 方法2: 文件拉取失败: {result.get('stderr', '未知错误')}")
            else:
                self.log_command(f"❌ 方法2: 截图保存失败: {result.get('stderr', '未知错误')}")
            
            # 所有方法都失败
            self.log_command("❌ 所有截图方法都失败")
            
        except Exception as e:
            self.log_command(f"❌ 截图过程出错: {str(e)}")
    
    def save_screenshot(self):
        """保存截图到文件"""
        if hasattr(self, 'screenshot_data'):
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存截图",
                f"screenshot_{self.current_device.serial.replace(':', '_')}.png",
                "PNG Files (*.png);;All Files (*)"
            )
            
            if file_path:
                try:
                    with open(file_path, 'wb') as f:
                        f.write(self.screenshot_data)
                    self.log_command(f"💾 截图已保存: {file_path}")
                except Exception as e:
                    self.log_command(f"❌ 保存截图失败: {str(e)}")
    
    def log_command(self, message):
        """记录指令执行日志"""
        self.command_log.append(f"{message}")
        # 自动滚动到底部
        self.command_log.verticalScrollBar().setValue(
            self.command_log.verticalScrollBar().maximum()
        )
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {AppleStyle.COLORS['background']};
            }}
        """)
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 清理设备管理器监听器
        device_manager = get_device_manager()
        device_manager.remove_listener(self.on_device_changed)
        
        # 断开设备连接
        if self.current_device:
            clear_current_device()
        
        self.logger.info("简化版主窗口已关闭")
        event.accept()


class SimplifiedADBTVToolApp:
    """简化版应用程序类"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.setup_application()
    
    def setup_application(self):
        """配置应用程序"""
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import Qt
        
        # 设置高DPI支持
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # 创建QApplication实例
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("ADB TV Tool - Simplified")
        self.app.setApplicationVersion("1.0.0")
        
        # 设置字体
        font = QFont("Segoe UI", 10)
        self.app.setFont(font)
        
        # 应用苹果风格样式
        from adb_tv_tool.utils.style import apply_apple_style
        apply_apple_style(self.app)
    
    def run(self):
        """运行应用程序"""
        try:
            # 创建并显示主窗口
            self.main_window = SimplifiedMainWindow()
            self.main_window.show()
            
            # 运行应用程序
            return self.app.exec()
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"应用程序启动失败: {e}")
            print(f"错误详情: {error_details}")
            return 1


def main():
    """主函数"""
    app = SimplifiedADBTVToolApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()