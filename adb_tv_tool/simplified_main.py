#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化版ADB电视工具主程序入口
专注核心功能：APK安装和屏幕截图
"""

import sys
import os
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """主函数"""
    try:
        print("=" * 60)
        print("ADB电视工具 - 简化版")
        print("功能特性:")
        print("• 设备连接管理 (连接/断开指定IP)")
        print("• APK文件安装")  
        print("• 屏幕截图获取")
        print("• 实时指令执行监控")
        print("=" * 60)
        
        # 导入并运行简化版应用
        from adb_tv_tool.ui.simplified_main_window import SimplifiedADBTVToolApp
        
        print("启动简化版界面...")
        app = SimplifiedADBTVToolApp()
        result = app.run()
        
        print("应用程序已退出")
        return result
        
    except Exception as e:
        import traceback
        print(f"程序启动失败: {e}")
        print(f"详细错误: {traceback.format_exc()}")
        
        # 尝试显示错误对话框
        try:
            from PyQt6.QtWidgets import QApplication, QMessageBox
            qt_app = QApplication([])
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Icon.Critical)
            msg_box.setWindowTitle("程序启动失败")
            msg_box.setText(f"程序启动时发生错误:\n{str(e)}")
            msg_box.exec()
        except:
            pass
        
        return 1

if __name__ == "__main__":
    sys.exit(main())