# -*- coding: utf-8 -*-
"""
APK导入页面
导入APK文件进行安装
"""

import logging
import os
from pathlib import Path
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QListWidget, QListWidgetItem,
                             QGroupBox, QFileDialog, QProgressBar, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from adb_tv_tool.utils.style import AppleStyle


class APKImportPage(QWidget):
    """APK导入页面"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.apk_import")
        self.apk_files = []
        self.setup_ui()
        self.setup_drag_drop()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        
        title = QLabel("APK导入")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        title_layout.addWidget(title)
        
        desc = QLabel("导入APK文件，支持单个文件和批量导入")
        desc.setStyleSheet(f"font-size: 14px; color: {AppleStyle.COLORS['text_secondary']};")
        title_layout.addWidget(desc)
        
        layout.addLayout(title_layout)
        
        # 导入区域
        import_group = QGroupBox("APK导入")
        import_layout = QVBoxLayout(import_group)
        
        # 拖放区域
        self.drop_area = QFrame()
        self.drop_area.setStyleSheet(f"""
            QFrame {{
                background-color: {AppleStyle.COLORS['surface']};
                border: 2px dashed {AppleStyle.COLORS['border']};
                border-radius: {AppleStyle.BORDER_RADIUS['large']}px;
                min-height: 120px;
            }}
            QFrame:hover {{
                border-color: {AppleStyle.COLORS['primary']};
                background-color: {AppleStyle.COLORS['blur_background']};
            }}
        """)
        
        drop_layout = QVBoxLayout(self.drop_area)
        drop_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        drop_icon = QLabel("📎")
        drop_icon.setStyleSheet("font-size: 32px;")
        drop_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_layout.addWidget(drop_icon)
        
        drop_text = QLabel("拖放APK文件到这里\n或点击下方按钮选择文件")
        drop_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_text.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']};")
        drop_layout.addWidget(drop_text)
        
        import_layout.addWidget(self.drop_area)
        
        # 导入按钮
        button_layout = QHBoxLayout()
        
        self.select_files_button = QPushButton("选择文件")
        self.select_files_button.setProperty("class", "primary")
        self.select_files_button.clicked.connect(self.select_files)
        button_layout.addWidget(self.select_files_button)
        
        self.select_folder_button = QPushButton("选择文件夹")
        self.select_folder_button.clicked.connect(self.select_folder)
        button_layout.addWidget(self.select_folder_button)
        
        self.clear_button = QPushButton("清空列表")
        self.clear_button.clicked.connect(self.clear_list)
        button_layout.addWidget(self.clear_button)
        
        button_layout.addStretch()
        import_layout.addLayout(button_layout)
        
        layout.addWidget(import_group)
        
        # 文件列表区域
        files_group = QGroupBox("待安装APK文件")
        files_layout = QVBoxLayout(files_group)
        
        self.files_list = QListWidget()
        self.files_list.itemDoubleClicked.connect(self.on_file_double_click)
        files_layout.addWidget(self.files_list)
        
        # 文件统计
        stats_layout = QHBoxLayout()
        self.files_count = QLabel("0 个文件")
        self.files_count.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']};")
        stats_layout.addWidget(self.files_count)
        
        stats_layout.addStretch()
        
        self.install_button = QPushButton("开始安装")
        self.install_button.setProperty("class", "primary")
        self.install_button.clicked.connect(self.start_installation)
        self.install_button.setEnabled(False)
        stats_layout.addWidget(self.install_button)
        
        files_layout.addLayout(stats_layout)
        layout.addWidget(files_group)
        
        layout.addStretch()
        
        self.apply_styles()
        
        self.logger.info("APK导入页面UI初始化完成")
    
    def setup_drag_drop(self):
        """设置拖放支持"""
        self.setAcceptDrops(True)
        self.drop_area.setAcceptDrops(True)
    
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
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """拖放事件"""
        urls = event.mimeData().urls()
        apk_files = []
        
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.lower().endswith('.apk'):
                apk_files.append(file_path)
        
        if apk_files:
            self.add_apk_files(apk_files)
        
        event.acceptProposedAction()
    
    def select_files(self):
        """选择APK文件"""
        file_dialog = QFileDialog()
        files, _ = file_dialog.getOpenFileNames(
            self, "选择APK文件", "", "APK Files (*.apk)"
        )
        
        if files:
            self.add_apk_files(files)
    
    def select_folder(self):
        """选择文件夹（批量导入）"""
        folder_dialog = QFileDialog()
        folder = folder_dialog.getExistingDirectory(self, "选择包含APK文件的文件夹")
        
        if folder:
            apk_files = []
            for root, dirs, files in os.walk(folder):
                for file in files:
                    if file.lower().endswith('.apk'):
                        apk_files.append(os.path.join(root, file))
            
            if apk_files:
                self.add_apk_files(apk_files)
    
    def add_apk_files(self, file_paths):
        """添加APK文件到列表"""
        new_files = []
        for file_path in file_paths:
            if file_path not in self.apk_files:
                self.apk_files.append(file_path)
                new_files.append(file_path)
        
        if new_files:
            self.update_files_list()
            self.logger.info(f"添加了 {len(new_files)} 个APK文件")
    
    def update_files_list(self):
        """更新文件列表显示"""
        self.files_list.clear()
        
        for file_path in self.apk_files:
            file_name = os.path.basename(file_path)
            file_size = self.get_file_size(file_path)
            file_info = f"{file_name} ({file_size})"
            
            item = QListWidgetItem(file_info)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            self.files_list.addItem(item)
        
        self.files_count.setText(f"{len(self.apk_files)} 个文件")
        self.install_button.setEnabled(len(self.apk_files) > 0)
    
    def get_file_size(self, file_path):
        """获取文件大小"""
        try:
            size = os.path.getsize(file_path)
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size/1024:.1f} KB"
            else:
                return f"{size/(1024*1024):.1f} MB"
        except:
            return "未知大小"
    
    def clear_list(self):
        """清空文件列表"""
        self.apk_files.clear()
        self.files_list.clear()
        self.files_count.setText("0 个文件")
        self.install_button.setEnabled(False)
        self.logger.info("文件列表已清空")
    
    def on_file_double_click(self, item):
        """文件双击事件"""
        file_path = item.data(Qt.ItemDataRole.UserRole)
        self.logger.debug(f"双击文件: {file_path}")
        # 可以在这里实现文件预览或详细信息显示
    
    def start_installation(self):
        """开始安装APK"""
        if not self.apk_files:
            return
        
        self.logger.info(f"开始安装 {len(self.apk_files)} 个APK文件")
        # 这里应该跳转到安装执行页面或开始安装流程
    
    def on_activated(self):
        """页面激活时的回调"""
        self.logger.debug("APK导入页面已激活")
    
    def cleanup(self):
        """清理资源"""
        self.logger.debug("APK导入页面资源已清理")