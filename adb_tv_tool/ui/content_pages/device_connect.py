# -*- coding: utf-8 -*-
"""
设备连接页面
连接和管理电视设备
"""

import logging
import subprocess
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QFrame, QGroupBox,
                             QListWidget, QListWidgetItem, QLineEdit,
                             QProgressBar, QMessageBox, QTextEdit)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from adb_tv_tool.utils.style import AppleStyle
from adb_tv_tool.utils.adb_manager import get_adb_manager
from adb_tv_tool.utils.device_manager import get_device_manager, set_current_device, clear_current_device


class DeviceScanner(QThread):
    """设备扫描线程"""
    
    # 信号定义
    scan_started = pyqtSignal()
    scan_finished = pyqtSignal(list)
    device_found = pyqtSignal(dict)
    log_message = pyqtSignal(str)
    
    def __init__(self, scan_ip_range=False, ip_range=None):
        super().__init__()
        self.scan_ip_range = scan_ip_range
        self.ip_range = ip_range or "192.168.1.1-255"
        self.logger = logging.getLogger("adb.device_scanner")
    
    def run(self):
        """执行设备扫描"""
        self.scan_started.emit()
        devices = []
        
        try:
            # 扫描USB连接的设备
            self.log_message.emit("扫描USB连接设备...")
            usb_devices = self.scan_usb_devices()
            devices.extend(usb_devices)
            
            # 网络设备扫描已禁用
            if self.scan_ip_range:
                self.log_message.emit("网络设备扫描功能已禁用")
            
            self.scan_finished.emit(devices)
            
        except Exception as e:
            self.log_message.emit(f"设备扫描出错: {str(e)}")
            self.scan_finished.emit([])
    
    def scan_usb_devices(self):
        """扫描USB连接的设备"""
        try:
            adb_manager = get_adb_manager()
            result = adb_manager.run_adb_command(["devices"], timeout=10)
            if result['success']:
                devices = []
                lines = result['stdout'].strip().split('\n')[1:]
                for line in lines:
                    if line.strip() and not line.startswith('*'):
                        parts = line.split('\t')
                        if len(parts) >= 2 and parts[1] == "device":
                            devices.append({
                                "serial": parts[0],
                                "type": "USB",
                                "status": "已连接",
                                "name": self.get_device_name(parts[0])
                            })
                return devices
            return []
        except Exception as e:
            self.log_message.emit(f"USB设备扫描失败: {str(e)}")
            return []
    
    def scan_network_devices(self):
        """扫描网络设备（已禁用局域网扫描）"""
        self.log_message.emit("局域网设备扫描功能已禁用")
        return []
    
    def check_device_connectivity(self, ip):
        """检查设备连通性"""
        try:
            # 尝试连接设备
            adb_manager = get_adb_manager()
            result = adb_manager.run_adb_command(["connect", ip], timeout=5)
            return result['success'] and "connected" in result.get('stdout', '')
        except Exception:
            return False
    
    def get_device_info(self, ip):
        """获取设备详细信息"""
        try:
            adb_manager = get_adb_manager()
            
            # 获取设备型号
            model_result = adb_manager.run_adb_command(["-s", ip, "shell", "getprop", "ro.product.model"], timeout=5)
            model = model_result['stdout'].strip() if model_result['success'] else "未知型号"
            
            # 获取设备品牌
            brand_result = adb_manager.run_adb_command(["-s", ip, "shell", "getprop", "ro.product.brand"], timeout=5)
            brand = brand_result['stdout'].strip() if brand_result['success'] else "未知品牌"
            
            return {
                "serial": ip,
                "type": "网络",
                "status": "可连接",
                "name": f"{brand} {model}",
                "ip": ip
            }
        except Exception:
            return None
    
    def get_device_name(self, serial):
        """获取设备名称"""
        try:
            adb_manager = get_adb_manager()
            result = adb_manager.run_adb_command(["-s", serial, "shell", "getprop", "ro.product.model"], timeout=5)
            if result['success']:
                return result['stdout'].strip()
            return "未知设备"
        except Exception:
            return "未知设备"


class DeviceConnectPage(QWidget):
    """设备连接页面"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.device_connect")
        self.scanner = None
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
        
        title = QLabel("设备连接")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        title_layout.addWidget(title)
        
        desc = QLabel("扫描和连接电视设备，支持USB和网络连接")
        desc.setStyleSheet(f"font-size: 14px; color: {AppleStyle.COLORS['text_secondary']};")
        title_layout.addWidget(desc)
        
        layout.addLayout(title_layout)
        
        # 连接状态显示
        status_frame = QFrame()
        status_frame.setStyleSheet(AppleStyle.get_card_style())
        status_layout = QHBoxLayout(status_frame)
        
        status_label = QLabel("当前连接状态:")
        status_label.setStyleSheet(f"font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        status_layout.addWidget(status_label)
        
        self.connection_status = QLabel("未连接")
        self.connection_status.setStyleSheet(f"color: {AppleStyle.COLORS['primary']}; font-weight: bold;")
        status_layout.addWidget(self.connection_status)
        
        status_layout.addStretch()
        
        self.connect_button = QPushButton("连接设备")
        self.connect_button.setProperty("class", "primary")
        self.connect_button.clicked.connect(self.connect_device)
        status_layout.addWidget(self.connect_button)
        
        self.disconnect_button = QPushButton("断开连接")
        self.disconnect_button.clicked.connect(self.disconnect_device)
        self.disconnect_button.setEnabled(False)
        status_layout.addWidget(self.disconnect_button)
        
        layout.addWidget(status_frame)
        
        # 设备扫描区域
        scan_group = QGroupBox("设备扫描")
        scan_layout = QVBoxLayout(scan_group)
        
        # 扫描控制
        scan_control_layout = QHBoxLayout()
        
        self.scan_button = QPushButton("扫描设备")
        self.scan_button.clicked.connect(self.start_scan)
        scan_control_layout.addWidget(self.scan_button)
        
        self.stop_scan_button = QPushButton("停止扫描")
        self.stop_scan_button.clicked.connect(self.stop_scan)
        self.stop_scan_button.setEnabled(False)
        scan_control_layout.addWidget(self.stop_scan_button)
        
        scan_control_layout.addStretch()
        
        # IP范围设置（已禁用）
        ip_layout = QHBoxLayout()
        ip_label = QLabel("局域网扫描:")
        ip_layout.addWidget(ip_label)
        
        self.ip_range_input = QLineEdit("局域网扫描功能已禁用")
        self.ip_range_input.setEnabled(False)
        self.ip_range_input.setPlaceholderText("此功能已禁用")
        ip_layout.addWidget(self.ip_range_input)
        
        self.network_scan_check = QLabel("❌ 已禁用")
        ip_layout.addWidget(self.network_scan_check)
        
        scan_control_layout.addLayout(ip_layout)
        scan_layout.addLayout(scan_control_layout)
        
        # 进度条
        self.scan_progress = QProgressBar()
        self.scan_progress.setVisible(False)
        scan_layout.addWidget(self.scan_progress)
        
        # 设备列表
        self.device_list = QListWidget()
        self.device_list.itemDoubleClicked.connect(self.on_device_double_click)
        scan_layout.addWidget(self.device_list)
        
        layout.addWidget(scan_group)
        
        # 手动连接区域
        manual_group = QGroupBox("手动连接")
        manual_layout = QVBoxLayout(manual_group)
        
        manual_input_layout = QHBoxLayout()
        manual_label = QLabel("设备地址:")
        manual_input_layout.addWidget(manual_label)
        
        self.manual_input = QLineEdit()
        self.manual_input.setPlaceholderText("输入设备IP地址或序列号")
        manual_input_layout.addWidget(self.manual_input)
        
        self.manual_connect_button = QPushButton("连接")
        self.manual_connect_button.clicked.connect(self.manual_connect)
        manual_input_layout.addWidget(self.manual_connect_button)
        
        manual_layout.addLayout(manual_input_layout)
        layout.addWidget(manual_group)
        
        # 日志区域
        log_group = QGroupBox("连接日志")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        layout.addStretch()
        
        self.apply_styles()
        
        self.logger.info("设备连接页面UI初始化完成")
    
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
    
    def start_scan(self):
        """开始设备扫描"""
        self.scan_button.setEnabled(False)
        self.stop_scan_button.setEnabled(True)
        self.scan_progress.setVisible(True)
        self.device_list.clear()
        
        ip_range = self.ip_range_input.text().strip()
        self.scanner = DeviceScanner(scan_ip_range=True, ip_range=ip_range)
        self.scanner.scan_started.connect(self.on_scan_started)
        self.scanner.device_found.connect(self.on_device_found)
        self.scanner.scan_finished.connect(self.on_scan_finished)
        self.scanner.log_message.connect(self.on_log_message)
        self.scanner.start()
    
    def stop_scan(self):
        """停止设备扫描"""
        if self.scanner and self.scanner.isRunning():
            self.scanner.terminate()
            self.scanner.wait()
        
        self.scan_button.setEnabled(True)
        self.stop_scan_button.setEnabled(False)
        self.scan_progress.setVisible(False)
        self.log_text.append("扫描已停止")
    
    def on_scan_started(self):
        """扫描开始回调"""
        self.log_text.append("开始扫描设备...")
    
    def on_device_found(self, device):
        """发现设备回调"""
        item = QListWidgetItem(f"{device['name']} ({device['type']} - {device['serial']})")
        item.setData(Qt.ItemDataRole.UserRole, device)
        self.device_list.addItem(item)
        self.log_text.append(f"发现设备: {device['name']}")
    
    def on_scan_finished(self, devices):
        """扫描完成回调"""
        self.scan_button.setEnabled(True)
        self.stop_scan_button.setEnabled(False)
        self.scan_progress.setVisible(False)
        self.log_text.append(f"扫描完成，共发现 {len(devices)} 个设备")
    
    def on_device_double_click(self, item):
        """设备双击连接"""
        device = item.data(Qt.ItemDataRole.UserRole)
        if device:
            self.connect_to_device(device)
    
    def connect_to_device(self, device):
        """连接到指定设备"""
        try:
            self.log_text.append(f"正在连接设备: {device['name']}")
            adb_manager = get_adb_manager()
            
            # 先断开之前可能的连接
            adb_manager.run_adb_command(["disconnect", device['serial']], timeout=5)
            
            if device['type'] == '网络' or device['type'] == '手动':
                # 网络设备需要先连接
                self.log_text.append(f"执行连接命令: adb connect {device['serial']}")
                result = adb_manager.run_adb_command(["connect", device['serial']], timeout=10)
                
                if result['success']:
                    self.log_text.append(f"连接命令结果: {result.get('stdout', 'Empty')}")
                else:
                    self.log_text.append(f"连接失败: {result.get('stderr', 'Unknown error')}")
                
                if not result['success'] or "connected" not in result.get('stdout', ''):
                    return
            
            # 检查设备是否真正连接
            self.log_text.append("检查设备连接状态...")
            result = adb_manager.run_adb_command(["devices"], timeout=5)
            
            if result['success']:
                self.log_text.append(f"设备列表:\n{result.get('stdout', 'Empty')}")
                
                # 检查设备是否在列表中
                devices_output = result.get('stdout', '')
                if device['serial'] in devices_output and 'device' in devices_output:
                    self.connected_device = device
                    
                    # 设置全局设备管理器中的设备信息
                    set_current_device(
                        serial=device['serial'],
                        name=device['name'],
                        model=device.get('model', '未知型号'),
                        status='connected'
                    )
                    
                    self.connection_status.setText(f"已连接: {device['name']}")
                    self.connection_status.setStyleSheet(f"color: {AppleStyle.COLORS['primary']}; font-weight: bold;")
                    self.connect_button.setEnabled(False)
                    self.disconnect_button.setEnabled(True)
                    self.log_text.append("设备连接成功")
                    
                    # 获取设备的详细信息以更新名称
                    self.update_device_info(device['serial'])
                else:
                    self.log_text.append("设备连接成功但未在设备列表中找到，可能连接状态不稳定")
            else:
                self.log_text.append(f"获取设备列表失败: {result.get('stderr', 'Unknown error')}")
            
        except Exception as e:
            self.log_text.append(f"连接出错: {str(e)}")
            import traceback
            self.log_text.append(f"详细错误: {traceback.format_exc()}")
    
    def connect_device(self):
        """连接设备（从列表中选择）"""
        current_item = self.device_list.currentItem()
        if current_item:
            device = current_item.data(Qt.ItemDataRole.UserRole)
            self.connect_to_device(device)
        else:
            self.log_text.append("请先选择一个设备")
    def disconnect_device(self):
        """断开设备连接"""
        if self.connected_device:
            try:
                adb_manager = get_adb_manager()
                if self.connected_device['type'] == '网络':
                    adb_manager.run_adb_command(["disconnect", self.connected_device['serial']], timeout=5)
                
                self.connected_device = None
                clear_current_device()  # 清除全局设备信息
                self.connection_status.setText("未连接")
                self.connection_status.setStyleSheet("color: red; font-weight: bold;")
                self.connect_button.setEnabled(True)
                self.disconnect_button.setEnabled(False)
                self.log_text.append("设备已断开连接")
                
            except Exception as e:
                self.log_text.append(f"断开连接出错: {str(e)}")
    
    def manual_connect(self):
        """手动连接设备"""
        device_address = self.manual_input.text().strip()
        if not device_address:
            self.log_text.append("请输入设备地址")
            return
        
        device = {
            "serial": device_address,
            "type": "手动",
            "status": "待连接",
            "name": f"手动设备 ({device_address})"
        }
        self.connect_to_device(device)
    
    def on_log_message(self, message):
        """日志消息回调"""
        self.log_text.append(message)
    
    def on_activated(self):
        """页面激活时的回调"""
        self.logger.debug("设备连接页面已激活")
        # 页面激活时自动扫描设备
        self.start_scan()
    
    def update_device_info(self, device_serial):
        """更新设备详细信息"""
        try:
            adb_manager = get_adb_manager()
            
            # 获取设备型号
            model_result = adb_manager.run_adb_command(["-s", device_serial, "shell", "getprop", "ro.product.model"], timeout=5)
            if model_result['success']:
                model = model_result['stdout'].strip()
                
                # 获取设备品牌
                brand_result = adb_manager.run_adb_command(["-s", device_serial, "shell", "getprop", "ro.product.brand"], timeout=5)
                brand = brand_result['stdout'].strip() if brand_result['success'] else "未知品牌"
                
                # 更新设备信息
                if self.connected_device:
                    self.connected_device['model'] = model
                    self.connected_device['name'] = f"{brand} {model}"
                    
                    # 更新全局设备管理器
                    set_current_device(
                        serial=device_serial,
                        name=f"{brand} {model}",
                        model=model,
                        status='connected'
                    )
                    
                    # 更新界面显示
                    self.connection_status.setText(f"已连接: {brand} {model}")
                    
        except Exception as e:
            self.log_text.append(f"获取设备详细信息失败: {e}")
    
    def cleanup(self):
        """清理资源"""
        if self.scanner and self.scanner.isRunning():
            self.scanner.terminate()
            self.scanner.wait()
        
        if self.connected_device:
            self.disconnect_device()
        
        self.logger.debug("设备连接页面资源已清理")