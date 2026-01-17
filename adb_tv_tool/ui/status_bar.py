# -*- coding: utf-8 -*-
"""
状态栏组件
显示当前操作状态、进度和提示信息
"""

import logging
from PyQt6.QtWidgets import (QStatusBar, QLabel, QProgressBar, QHBoxLayout, 
                             QWidget, QSizePolicy)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

from adb_tv_tool.utils.style import AppleStyle


class StatusBar(QStatusBar):
    """自定义状态栏（苹果风格）"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.status_bar")
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """设置UI界面"""
        # 移除默认的样式
        self.setStyleSheet("")
        
        # 创建自定义状态栏内容
        self.status_widget = QWidget()
        self.status_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        layout = QHBoxLayout(self.status_widget)
        layout.setContentsMargins(20, 5, 20, 5)
        layout.setSpacing(20)
        
        # 左侧状态信息
        self.status_label = QLabel("就绪")
        self.status_label.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']}; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # 中间的进度信息（隐藏状态）
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']}; font-size: 12px;")
        self.progress_label.setVisible(False)
        layout.addWidget(self.progress_label)
        
        # 进度条（隐藏状态）
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        layout.addStretch()
        
        # 右侧提示信息
        self.hint_label = QLabel("")
        self.hint_label.setStyleSheet(f"color: {AppleStyle.COLORS['text_tertiary']}; font-size: 11px;")
        layout.addWidget(self.hint_label)
        
        # 设置自定义状态栏
        self.addPermanentWidget(self.status_widget, 1)
        
        # 设置样式
        self.apply_styles()
        
        self.logger.info("状态栏UI初始化完成")
    
    def setup_connections(self):
        """设置信号连接"""
        # 暂无需要连接的信号
    
    def apply_styles(self):
        """应用样式"""
        self.setStyleSheet(f"""
            StatusBar {{
                background-color: {AppleStyle.COLORS['blur_background']};
                border-top: 1px solid {AppleStyle.COLORS['divider']};
                color: {AppleStyle.COLORS['text_secondary']};
            }}
        """)
    
    def update_status(self, status_text):
        """更新状态信息"""
        self.status_label.setText(status_text)
        self.logger.debug(f"状态更新: {status_text}")
    
    def show_progress(self, progress_text, value=0, maximum=100):
        """显示进度条"""
        self.progress_label.setText(progress_text)
        self.progress_label.setVisible(True)
        
        self.progress_bar.setValue(value)
        self.progress_bar.setMaximum(maximum)
        self.progress_bar.setVisible(True)
        
        self.logger.debug(f"进度显示: {progress_text} ({value}/{maximum})")
    
    def update_progress(self, value, progress_text=None):
        """更新进度"""
        self.progress_bar.setValue(value)
        
        if progress_text:
            self.progress_label.setText(progress_text)
            self.logger.debug(f"进度更新: {progress_text} ({value}/{self.progress_bar.maximum()})")
    
    def hide_progress(self):
        """隐藏进度条"""
        self.progress_label.setVisible(False)
        self.progress_bar.setVisible(False)
        self.logger.debug("进度条隐藏")
    
    def show_hint(self, hint_text, timeout=3000):
        """显示临时提示信息"""
        self.hint_label.setText(hint_text)
        self.logger.debug(f"提示信息: {hint_text}")
        
        # 设置定时器自动清除提示
        if timeout > 0:
            QTimer.singleShot(timeout, self.clear_hint)
    
    def clear_hint(self):
        """清除提示信息"""
        self.hint_label.setText("")
        self.logger.debug("提示信息已清除")
    
    def show_success(self, message, timeout=2000):
        """显示成功状态"""
        self.update_status(f"✅ {message}")
        self.show_hint("操作成功", timeout)
        self.logger.info(f"成功: {message}")
    
    def show_error(self, message, timeout=5000):
        """显示错误状态"""
        self.update_status(f"❌ {message}")
        self.show_hint("操作失败，请查看日志", timeout)
        self.logger.error(f"错误: {message}")
    
    def show_warning(self, message, timeout=3000):
        """显示警告状态"""
        self.update_status(f"⚠️ {message}")
        self.show_hint("请注意操作风险", timeout)
        self.logger.warning(f"警告: {message}")
    
    def show_info(self, message, timeout=2000):
        """显示信息状态"""
        self.update_status(f"ℹ️ {message}")
        self.show_hint("", timeout)  # 清空提示
        self.logger.info(f"信息: {message}")
    
    def reset(self):
        """重置状态栏到初始状态"""
        self.update_status("就绪")
        self.hide_progress()
        self.clear_hint()
        self.logger.debug("状态栏已重置")


class NotificationManager:
    """通知管理器（用于显示苹果风格的通知）"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.logger = logging.getLogger("ui.notification")
    
    def show_notification(self, title, message, duration=3000, notification_type="info"):
        """显示通知"""
        # 后续实现苹果风格的通知弹窗
        # 目前使用状态栏提示
        status_bar = self.parent.statusBar() if self.parent else None
        if status_bar and hasattr(status_bar, 'show_hint'):
            status_bar.show_hint(f"{title}: {message}", duration)
        
        self.logger.info(f"通知: {title} - {message}")


if __name__ == "__main__":
    # 测试状态栏
    import sys
    from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
    
    class TestWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setup_ui()
        
        def setup_ui(self):
            central_widget = QWidget()
            layout = QVBoxLayout(central_widget)
            
            # 测试按钮
            btn_success = QPushButton("显示成功")
            btn_success.clicked.connect(lambda: self.statusBar().show_success("测试成功"))
            layout.addWidget(btn_success)
            
            btn_error = QPushButton("显示错误")
            btn_error.clicked.connect(lambda: self.statusBar().show_error("测试错误"))
            layout.addWidget(btn_error)
            
            btn_progress = QPushButton("显示进度")
            btn_progress.clicked.connect(self.test_progress)
            layout.addWidget(btn_progress)
            
            self.setCentralWidget(central_widget)
            
            # 设置自定义状态栏
            self.setStatusBar(StatusBar())
        
        def test_progress(self):
            status_bar = self.statusBar()
            status_bar.show_progress("处理中...", 0, 100)
            
            # 模拟进度更新
            import time
            for i in range(101):
                status_bar.update_progress(i, f"处理中... {i}%")
                QApplication.processEvents()
                time.sleep(0.02)
            
            status_bar.hide_progress()
            status_bar.show_success("处理完成")
    
    app = QApplication(sys.argv)
    
    # 应用苹果风格
    from adb_tv_tool.utils.style import apply_apple_style
    apply_apple_style(app)
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())