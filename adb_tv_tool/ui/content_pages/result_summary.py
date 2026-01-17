# -*- coding: utf-8 -*-
"""
结果汇总页面
查看操作结果和日志
"""

import logging
import json
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QTableWidget, QTableWidgetItem,
                             QGroupBox, QHeaderView, QTabWidget, QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from adb_tv_tool.utils.style import AppleStyle


class ResultSummaryPage(QWidget):
    """结果汇总页面"""
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger("ui.result_summary")
        self.operation_history = []
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(8)
        
        title = QLabel("结果汇总")
        title.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {AppleStyle.COLORS['text_primary']};")
        title_layout.addWidget(title)
        
        desc = QLabel("查看操作记录、安装结果和系统日志")
        desc.setStyleSheet(f"font-size: 14px; color: {AppleStyle.COLORS['text_secondary']};")
        title_layout.addWidget(desc)
        
        layout.addLayout(title_layout)
        
        # 统计信息区域
        stats_group = QGroupBox("操作统计")
        stats_layout = QHBoxLayout(stats_group)
        
        # 统计卡片
        stats_cards = [
            ("总操作数", "total_operations", "0"),
            ("成功操作", "success_operations", "0"),
            ("失败操作", "failed_operations", "0"),
            ("成功率", "success_rate", "0%")
        ]
        
        self.stats_labels = {}
        
        for label_text, key, default_value in stats_cards:
            card = QFrame()
            card.setStyleSheet(AppleStyle.get_card_style())
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(15, 10, 15, 10)
            
            value_label = QLabel(default_value)
            value_label.setStyleSheet(f"""
                font-size: 24px; 
                font-weight: bold; 
                color: {AppleStyle.COLORS['primary']};
            """)
            card_layout.addWidget(value_label)
            
            name_label = QLabel(label_text)
            name_label.setStyleSheet(f"color: {AppleStyle.COLORS['text_secondary']};")
            card_layout.addWidget(name_label)
            
            stats_layout.addWidget(card)
            self.stats_labels[key] = value_label
        
        layout.addWidget(stats_group)
        
        # 选项卡区域
        self.tab_widget = QTabWidget()
        
        # 操作记录选项卡
        self.operations_tab = self.create_operations_tab()
        self.tab_widget.addTab(self.operations_tab, "操作记录")
        
        # 安装结果选项卡
        self.install_results_tab = self.create_install_results_tab()
        self.tab_widget.addTab(self.install_results_tab, "安装结果")
        
        # 系统日志选项卡
        self.system_logs_tab = self.create_system_logs_tab()
        self.tab_widget.addTab(self.system_logs_tab, "系统日志")
        
        layout.addWidget(self.tab_widget)
        
        # 控制按钮区域
        control_layout = QHBoxLayout()
        
        self.refresh_button = QPushButton("刷新数据")
        self.refresh_button.clicked.connect(self.refresh_data)
        control_layout.addWidget(self.refresh_button)
        
        self.export_button = QPushButton("导出报告")
        self.export_button.clicked.connect(self.export_report)
        control_layout.addWidget(self.export_button)
        
        self.clear_button = QPushButton("清空记录")
        self.clear_button.clicked.connect(self.clear_records)
        control_layout.addWidget(self.clear_button)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        layout.addStretch()
        
        self.apply_styles()
        
        # 加载示例数据
        self.load_sample_data()
        
        self.logger.info("结果汇总页面UI初始化完成")
    
    def create_operations_tab(self):
        """创建操作记录选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 操作记录表格
        self.operations_table = QTableWidget()
        self.operations_table.setColumnCount(5)
        self.operations_table.setHorizontalHeaderLabels([
            "时间", "操作类型", "设备", "结果", "详情"
        ])
        
        # 设置表格属性
        self.operations_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.operations_table.setAlternatingRowColors(True)
        self.operations_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.operations_table)
        
        return tab
    
    def create_install_results_tab(self):
        """创建安装结果选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 安装结果表格
        self.install_table = QTableWidget()
        self.install_table.setColumnCount(6)
        self.install_table.setHorizontalHeaderLabels([
            "时间", "应用名称", "版本", "设备", "结果", "错误信息"
        ])
        
        self.install_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.install_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.install_table)
        
        return tab
    
    def create_system_logs_tab(self):
        """创建系统日志选项卡"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # 日志显示区域
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        layout.addWidget(self.logs_text)
        
        # 日志控制
        log_control_layout = QHBoxLayout()
        
        self.clear_logs_button = QPushButton("清空日志")
        self.clear_logs_button.clicked.connect(self.clear_logs)
        log_control_layout.addWidget(self.clear_logs_button)
        
        self.save_logs_button = QPushButton("保存日志")
        self.save_logs_button.clicked.connect(self.save_logs)
        log_control_layout.addWidget(self.save_logs_button)
        
        log_control_layout.addStretch()
        layout.addLayout(log_control_layout)
        
        return tab
    
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
        
        # 表格样式
        table_style = f"""
            QTableWidget {{
                background-color: {AppleStyle.COLORS['background']};
                border: 1px solid {AppleStyle.COLORS['border']};
                border-radius: {AppleStyle.BORDER_RADIUS['medium']}px;
                gridline-color: {AppleStyle.COLORS['divider']};
            }}
            QTableWidget::item {{
                padding: 8px;
                border-bottom: 1px solid {AppleStyle.COLORS['divider']};
            }}
            QTableWidget::item:selected {{
                background-color: {AppleStyle.COLORS['primary']};
                color: white;
            }}
        """
        
        self.operations_table.setStyleSheet(table_style)
        self.install_table.setStyleSheet(table_style)
    
    def load_sample_data(self):
        """加载示例数据"""
        # 示例操作记录
        sample_operations = [
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "设备连接",
                "device": "小米电视 (192.168.1.100)",
                "result": "成功",
                "details": "USB连接"
            },
            {
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "type": "应用安装",
                "device": "小米电视 (192.168.1.100)", 
                "result": "成功",
                "details": "安装 3 个应用"
            }
        ]
        
        for op in sample_operations:
            self.add_operation_record(op)
        
        # 更新统计信息
        self.update_stats()
    
    def add_operation_record(self, operation):
        """添加操作记录"""
        row = self.operations_table.rowCount()
        self.operations_table.insertRow(row)
        
        self.operations_table.setItem(row, 0, QTableWidgetItem(operation["time"]))
        self.operations_table.setItem(row, 1, QTableWidgetItem(operation["type"]))
        self.operations_table.setItem(row, 2, QTableWidgetItem(operation["device"]))
        
        result_item = QTableWidgetItem(operation["result"])
        if operation["result"] == "成功":
            result_item.setForeground(Qt.GlobalColor.green)
        else:
            result_item.setForeground(Qt.GlobalColor.red)
        self.operations_table.setItem(row, 3, result_item)
        
        self.operations_table.setItem(row, 4, QTableWidgetItem(operation["details"]))
        
        self.operation_history.append(operation)
    
    def update_stats(self):
        """更新统计信息"""
        total = len(self.operation_history)
        success = len([op for op in self.operation_history if op["result"] == "成功"])
        failed = total - success
        rate = (success / total * 100) if total > 0 else 0
        
        self.stats_labels["total_operations"].setText(str(total))
        self.stats_labels["success_operations"].setText(str(success))
        self.stats_labels["failed_operations"].setText(str(failed))
        self.stats_labels["success_rate"].setText(f"{rate:.1f}%")
    
    def refresh_data(self):
        """刷新数据"""
        self.logger.info("刷新结果数据")
        # 实际实现中应该重新加载数据
    
    def export_report(self):
        """导出报告"""
        self.logger.info("导出操作报告")
        # 实现报告导出功能
    
    def clear_records(self):
        """清空记录"""
        self.operations_table.setRowCount(0)
        self.install_table.setRowCount(0)
        self.operation_history.clear()
        self.update_stats()
        self.logger.info("操作记录已清空")
    
    def clear_logs(self):
        """清空日志"""
        self.logs_text.clear()
        self.logs_text.append("日志已清空")
    
    def save_logs(self):
        """保存日志"""
        self.logs_text.append("日志已保存")
    
    def on_activated(self):
        """页面激活时的回调"""
        self.logger.debug("结果汇总页面已激活")
        self.refresh_data()
    
    def cleanup(self):
        """清理资源"""
        self.logger.debug("结果汇总页面资源已清理")