"""
DataTableWidget - 数据表格 Widget
实时更新的数据表格
"""

from PyQt6.QtWidgets import QVBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Dict
from datetime import datetime

from .base_widget import BaseWidget


class DataTableWidget(BaseWidget):
    """数据表格 Widget"""

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__(widget_data, theme, channel_manager)
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Time", "Channel", "Value"])

        # 设置表头自适应
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        self.table.setFont(QFont("Consolas", 9))

        if self.theme == 'dark':
            self.table.setStyleSheet("""
                QTableWidget {
                    background-color: #1A1A1A;
                    color: #FFFFFF;
                    gridline-color: #3A3A3A;
                    border: 1px solid #3A3A3A;
                }
                QHeaderView::section {
                    background-color: #252525;
                    color: #FFFFFF;
                    border: 1px solid #3A3A3A;
                    padding: 4px;
                }
            """)
        else:
            self.table.setStyleSheet("""
                QTableWidget {
                    background-color: #FFFFFF;
                    color: #000000;
                    gridline-color: #E0E0E0;
                    border: 1px solid #D1D5DB;
                }
                QHeaderView::section {
                    background-color: #F5F5F5;
                    color: #000000;
                    border: 1px solid #E0E0E0;
                    padding: 4px;
                }
            """)

        layout.addWidget(self.table)

    def _on_data_update(self, data: Dict[str, float]):
        """接收数据更新"""
        for channel in self.get_bound_channels():
            if channel in data:
                self._add_row(channel, data[channel])

    def _add_row(self, channel: str, value: float):
        """添加一行数据"""
        max_rows = self.widget_data['config'].get('maxRows', 100)

        # 如果超过最大行数，删除最旧的行
        if self.table.rowCount() >= max_rows:
            self.table.removeRow(0)

        # 添加新行
        row = self.table.rowCount()
        self.table.insertRow(row)

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        self.table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.table.setItem(row, 1, QTableWidgetItem(channel))
        self.table.setItem(row, 2, QTableWidgetItem(f"{value:.4f}"))

        # 滚动到底部
        self.table.scrollToBottom()
