# -*- coding: utf-8 -*-
"""
苹果风格样式定义工具
提供macOS/iOS风格的UI样式配置
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtWidgets import QApplication, QStyleFactory



class AppleStyle:
    """苹果风格样式配置类"""
    
    # 苹果风格颜色定义
    COLORS = {
        "primary": "#007AFF",         # 苹果蓝
        "primary_dark": "#0066CC",    # 深蓝选中状态
        "primary_hover": "#0056CC",   # 悬停状态
        "primary_pressed": "#004499", # 按下状态
        
        "background": "#F5F5F7",      # 背景色
        "surface": "#FFFFFF",         # 表面色
        "card": "#FFFFFF",           # 卡片背景
        "text_primary": "#000000",    # 主文本
        "text_secondary": "#8E8E93", # 次要文本
        "text_tertiary": "#C7C7CC",  # 三级文本
        "border": "#C6C6C8",         # 边框
        "divider": "#E5E5EA",        # 分隔线
        
        "blur_background": "rgba(245, 245, 247, 0.8)",   # 磨砂玻璃背景
        "blur_border": "rgba(198, 198, 200, 0.3)",       # 磨砂玻璃边框
    }
    
    # 圆角配置
    BORDER_RADIUS = {
        "small": 4,
        "medium": 8,
        "large": 12,
        "circle": 50,
    }
    
    @classmethod
    def apply_to_app(cls, app):
        """应用苹果风格到整个应用程序"""
        # 设置字体 - 使用更兼容的字体设置
        font = QFont("Microsoft YaHei", 10)  # 使用微软雅黑，Windows兼容性更好
        app.setFont(font)
        
        # 设置调色板
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor(cls.COLORS["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(cls.COLORS["text_primary"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(cls.COLORS["card"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(cls.COLORS["text_primary"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(cls.COLORS["surface"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(cls.COLORS["text_primary"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(cls.COLORS["primary"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.white)
        
        app.setPalette(palette)
        
        # 使用简单样式，避免复杂的CSS
        try:
            # 使用极简样式表，只确保按钮文字可见
            print("⚠️ 使用极简样式表测试按钮显示")
            app.setStyleSheet(cls.get_minimal_stylesheet())
        except Exception as e:
            # 如果样式表有问题，使用基本的样式
            print(f"样式表错误: {e}")
            app.setStyleSheet("")
    
    @classmethod
    def get_global_stylesheet(cls):
        """获取简洁有效的全局样式表"""
        # 简化样式表，确保按钮文字能正常显示
        return f"""
        QMainWindow {{
            background-color: {cls.COLORS["background"]};
        }}
        
        /* 基础按钮样式 - 确保文字可见 */
        QPushButton {{
            background-color: {cls.COLORS["surface"]};
            color: {cls.COLORS["text_primary"]};
            border: 1px solid {cls.COLORS["border"]};
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 12px;
        }}
        
        QPushButton:hover {{
            background-color: {cls.COLORS["primary"]};
            color: white;
        }}
        
        QPushButton:pressed {{
            background-color: {cls.COLORS["primary_pressed"]};
        }}
        
        /* 主要按钮样式 */
        QPushButton[class="primary"] {{
            background-color: {cls.COLORS["primary"]};
            color: white;
            font-weight: bold;
        }}
        
        /* 输入框样式 */
        QLineEdit, QTextEdit, QComboBox {{
            background-color: {cls.COLORS["card"]};
            border: 1px solid {cls.COLORS["border"]};
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 12px;
        }}
        
        /* 标签样式 */
        QLabel {{
            color: {cls.COLORS["text_primary"]};
            font-size: 12px;
        }}
        """
    
    @classmethod
    def get_minimal_stylesheet(cls):
        """获取极简样式表，确保按钮文字可见"""
        # 完全简化的样式，确保按钮文字显示
        return """
        /* 完全简化样式表，确保按钮文字可见 */
        QPushButton {
            color: black;           /* 强制黑色文字 */
            background-color: white;  /* 白色背景 */
            border: 1px solid #ccc;  /* 简单边框 */
            padding: 8px 12px;
            font-size: 12px;
            font-family: Microsoft YaHei;
        }
        
        QPushButton:hover {
            background-color: #007AFF;
            color: white;
        }
        
        QPushButton[class="primary"] {
            background-color: #007AFF;
            color: white;
            font-weight: bold;
        }
        """

    @classmethod
    def get_card_style(cls):
        """获取卡片样式"""
        return f"""
        background-color: {cls.COLORS["card"]};
        border: 1px solid {cls.COLORS["border"]};
        border-radius: 8px;
        """


def apply_apple_style(app):
    """应用苹果风格样式的便捷函数"""
    AppleStyle.apply_to_app(app)


if __name__ == "__main__":
    # 测试样式
    app = QApplication([])
    apply_apple_style(app)
    app.exec()