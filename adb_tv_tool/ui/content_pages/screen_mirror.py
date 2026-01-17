# -*- coding: utf-8 -*-
"""
投屏预览页面
实时预览电视屏幕
"""

import logging
import subprocess
import threading
import time
import os
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QFrame, QGroupBox, QFileDialog,
                             QMessageBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QPixmap, QImage

from adb_tv_tool.utils.style import AppleStyle
from adb_tv_tool.utils.adb_manager import get_adb_manager


class ScreenMirrorManager:
    """屏幕镜像管理器"""
    
    def __init__(self):
        self.logger = logging.getLogger("screen.mirror")
        self.is_mirroring = False
        self.mirror_thread = None
        self.current_mode = "流畅模式"  # 流畅模式/高清模式
        self.quality = "中"  # 低/中/高
        
    def start_mirroring(self, device_serial=None):
        """开始屏幕镜像"""
        if self.is_mirroring:
            self.logger.warning("屏幕镜像已在运行")
            return False
        
        self.is_mirroring = True
        self.mirror_thread = threading.Thread(target=self._mirror_loop, args=(device_serial,))
        self.mirror_thread.daemon = True
        self.mirror_thread.start()
        
        self.logger.info("屏幕镜像已启动")
        return True
    
    def stop_mirroring(self):
        """停止屏幕镜像"""
        self.is_mirroring = False
        if self.mirror_thread and self.mirror_thread.is_alive():
            self.mirror_thread.join(timeout=5)
        
        self.logger.info("屏幕镜像已停止")
    
    def set_mode(self, mode):
        """设置镜像模式"""
        self.current_mode = mode
        self.logger.info(f"镜像模式已设置为: {mode}")
    
    def set_quality(self, quality):
        """设置镜像质量"""
        self.quality = quality
        self.logger.info(f"镜像质量已设置为: {quality}")
    
    def _mirror_loop(self, device_serial):
        """镜像循环（线程中运行）"""
        self.logger.debug("镜像线程启动")
        
        try:
            while self.is_mirroring:
                # 获取屏幕截图
                screenshot_data = self._capture_screen(device_serial)
                if screenshot_data:
                    # 这里应该发送信号给UI更新图像
                    # self.screenshot_captured.emit(screenshot_data)
                    pass
                
                # 根据模式设置延迟
                if self.current_mode == "流畅模式":
                    time.sleep(0.2)  # 5 FPS
                else:  # 高清模式
                    time.sleep(0.05)  # 20 FPS
                    
        except Exception as e:
            self.logger.error(f"镜像线程出错: {str(e)}")
        finally:
            self.logger.debug("镜像线程结束")
    
    def _capture_screen(self, device_serial):
        """捕获屏幕截图"""
        try:
            # 直接使用subprocess运行ADB命令，避免编码问题
            cmd = [str(get_adb_manager().builtin_adb_path)]
            if device_serial:
                cmd.extend(["-s", device_serial])
            cmd.extend(["exec-out", "screencap", "-p"])
            
            result = subprocess.run(cmd, capture_output=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                return result.stdout
            return None
        except Exception as e:
            self.logger.error(f"屏幕截图失败: {str(e)}")
            return None
    
    def take_screenshot(self, device_serial=None, save_path=None):
        """拍摄屏幕截图并保存"""
        try:
            screenshot_data = self._capture_screen(device_serial)
            if screenshot_data and save_path:
                # 确保目录存在
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                
                with open(save_path, 'wb') as f:
                    f.write(screenshot_data)
                self.logger.info(f"截图已保存: {save_path}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"截图保存失败: {str(e)}")
            return False


class ScreenMirrorPage(QWidget):
    """投屏预览页面"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.screen_mirror")
        self.mirror_manager = ScreenMirrorManager()
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
        
        title = QLabel("投屏预览")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        title_layout.addWidget(title)
        
        desc = QLabel("实时预览电视屏幕，支持流畅和高清两种模式")
        desc.setStyleSheet(f"font-size: 14px; color: {AppleStyle.COLORS['text_secondary']};")
        title_layout.addWidget(desc)
        
        layout.addLayout(title_layout)
        
        # 状态区域
        status_frame = QFrame()
        status_frame.setStyleSheet(AppleStyle.get_card_style())
        status_layout = QHBoxLayout(status_frame)
        
        status_label = QLabel("投屏状态:")
        status_label.setStyleSheet(f"font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        status_layout.addWidget(status_label)
        
        self.mirror_status = QLabel("未启动")
        self.mirror_status.setStyleSheet(f"color: {AppleStyle.COLORS['primary']}; font-weight: bold;")
        status_layout.addWidget(self.mirror_status)
        
        status_layout.addStretch()
        
        # 设备信息
        self.device_info = QLabel("未连接设备")
        self.device_info.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']};")
        status_layout.addWidget(self.device_info)
        
        layout.addWidget(status_frame)
        
        # 投屏显示区域
        screen_group = QGroupBox("电视屏幕")
        screen_layout = QVBoxLayout(screen_group)
        
        # 屏幕显示区域（占位）
        self.screen_display = QLabel()
        self.screen_display.setStyleSheet(f"""
            QLabel {{
                background-color: {AppleStyle.COLORS["surface"]};
                border: 2px dashed {AppleStyle.COLORS["border"]};
                border-radius: 16px;
                min-height: 400px;
                font-family: Microsoft YaHei;
                font-size: 14px;
                padding: 20px;
            }}
        """)
        self.screen_display.setText("点击\"开始投屏\"查看电视屏幕")
        screen_layout.addWidget(self.screen_display)
        
        layout.addWidget(screen_group)
        
        # 控制区域
        control_group = QGroupBox("投屏控制")
        control_layout = QVBoxLayout(control_group)
        
        # 模式选择（已禁用）
        mode_layout = QHBoxLayout()
        mode_label = QLabel("投屏模式:")
        mode_layout.addWidget(mode_label)
        
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(["功能已禁用"])
        self.mode_combo.setEnabled(False)
        self.mode_combo.currentTextChanged.connect(self.on_mode_changed)
        mode_layout.addWidget(self.mode_combo)
        mode_layout.addStretch()
        
        control_layout.addLayout(mode_layout)
        
        # 质量选择（已禁用）
        quality_layout = QHBoxLayout()
        quality_label = QLabel("清晰度:")
        quality_layout.addWidget(quality_label)
        
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["功能已禁用"])
        self.quality_combo.setEnabled(False)
        self.quality_combo.currentTextChanged.connect(self.on_quality_changed)
        quality_layout.addWidget(self.quality_combo)
        quality_layout.addStretch()
        
        control_layout.addLayout(quality_layout)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.screenshot_button = QPushButton("📸 截图")
        self.screenshot_button.setProperty("class", "primary")
        self.screenshot_button.clicked.connect(self.take_screenshot)
        self.screenshot_button.setMinimumHeight(40)
        button_layout.addWidget(self.screenshot_button)
        
        button_layout.addStretch()
        
        control_layout.addLayout(button_layout)
        layout.addWidget(control_group)
        
        # 信息区域
        info_group = QGroupBox("截图信息")
        info_layout = QVBoxLayout(info_group)
        
        self.info_text = QLabel()
        self.info_text.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']}; font-size: 12px;")
        self.info_text.setText("""
        • 点击"截图"按钮获取电视屏幕截图
        • 截图将自动保存到 screenshots 文件夹
        • 支持PNG格式，保持原始分辨率
        • 需要设备已连接并开启ADB调试
        """)
        info_layout.addWidget(self.info_text)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        self.apply_styles()
        
        self.logger.info("投屏预览页面UI初始化完成")
    
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
    
    def set_connected_device(self, device):
        """设置当前连接的设备"""
        self.connected_device = device
        if device:
            self.device_info.setText(f"设备: {device.get('name', '未知设备')}")
        else:
            self.device_info.setText("未连接设备")
    
    def take_screenshot(self):
        """拍摄截图并保存"""
        if not self.connected_device:
            self._show_message("请先连接设备")
            return
        
        device_serial = self.connected_device.get('serial')
        
        # 创建截图保存目录
        screenshots_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        save_path = os.path.join(screenshots_dir, filename)
        
        # 执行截图
        success = self.mirror_manager.take_screenshot(device_serial, save_path)
        
        if success:
            self._show_message(f"截图已保存: {filename}")
            
            # 显示截图预览
            try:
                pixmap = QPixmap(save_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        self.screen_display.width(),
                        self.screen_display.height(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    self.screen_display.setPixmap(scaled_pixmap)
                    self.screen_display.setText("")
            except Exception as e:
                self.logger.error(f"预览截图失败: {e}")
                self.screen_display.setText("截图成功，预览失败")
        else:
            self._show_message("截图失败，请检查设备连接")
    
    def start_mirroring(self):
        """开始投屏（已禁用）"""
        self._show_message("实时投屏功能已禁用，请使用截图功能")
    
    def stop_mirroring(self):
        """停止投屏（已禁用）"""
        self._show_message("实时投屏功能已禁用")
    
    def on_mode_changed(self, mode):
        """模式改变回调（已禁用）"""
        self._show_message("模式选择功能已禁用")

    def on_quality_changed(self, quality):
        """质量改变回调（已禁用）"""
        self._show_message("质量选择功能已禁用")
    
    def _show_message(self, message):
        """显示消息（简化版本）"""
        self.logger.info(message)
        # 这里可以通过状态栏或其他方式显示消息
    
    def on_activated(self):
        """页面激活时的回调"""
        self.logger.debug("投屏预览页面已激活")
        # 检查设备连接状态
        # 这里应该从其他页面获取设备连接状态
    
    def cleanup(self):
        """清理资源"""
        self.mirror_manager.stop_mirroring()
        self.logger.debug("投屏预览页面资源已清理")