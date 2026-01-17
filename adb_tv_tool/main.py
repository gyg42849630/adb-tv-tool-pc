#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强版 ADB 电视 APP 安装工具 - 主程序入口
采用苹果风格界面设计，支持投屏预览、应用管理等功能
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon

from adb_tv_tool.ui.main_window import MainWindow
from adb_tv_tool.utils.logger import setup_logging
from adb_tv_tool.utils.style import apply_apple_style


class ADBTVToolApp:
    """主应用程序类"""
    
    def __init__(self):
        self.app = None
        self.main_window = None
        self.setup_application()
    
    def setup_application(self):
        """配置应用程序"""
        # 设置高DPI支持
        QApplication.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # 创建QApplication实例
        self.app = QApplication(sys.argv)
        self.app.setApplicationName("ADB TV Tool")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("Comate")
        
        # 设置字体（使用系统默认字体，Windows下可以后续替换为San Francisco）
        font = QFont("Segoe UI", 10)  # Windows系统字体
        self.app.setFont(font)
        
        # 应用苹果风格样式
        apply_apple_style(self.app)
        
        # 设置应用程序图标（后续添加）
        # self.app.setWindowIcon(QIcon("resources/icons/app_icon.ico"))
    
    def setup_logging(self):
        """配置日志系统"""
        setup_logging()
    
    def create_main_window(self):
        """创建主窗口"""
        self.main_window = MainWindow()
        return self.main_window
    
    def run(self):
        """运行应用程序"""
        try:
            # 记录启动过程
            print("ADB TV Tool 开始启动...")
            logging.info("ADB TV Tool 开始启动")
            
            # 配置日志
            self.setup_logging()
            print("日志配置完成")
            
            # 创建并显示主窗口
            print("创建主窗口...")
            window = self.create_main_window()
            print("主窗口创建完成")
            
            window.show()
            print("主窗口显示完成")
            print("进入Qt事件循环...")
            
            # 运行应用程序
            result = self.app.exec()
            print(f"应用程序退出，返回值: {result}")
            return result
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_msg = f"应用程序启动失败: {e}"
            logging.error(error_msg)
            logging.error(f"错误详情: {error_details}")
            print(error_msg)
            print(f"错误详情: {error_details}")
            
            # 尝试显示错误对话框
            try:
                from PyQt6.QtWidgets import QMessageBox
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setText("应用程序启动失败")
                msg.setInformativeText(str(e))
                msg.setWindowTitle("错误")
                msg.exec()
            except Exception as dialog_error:
                print(f"显示错误对话框失败: {dialog_error}")
            
            return 1


def main():
    """主函数"""
    app = ADBTVToolApp()
    sys.exit(app.run())


if __name__ == "__main__":
    main()