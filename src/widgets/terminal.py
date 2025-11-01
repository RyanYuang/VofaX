"""
TerminalWidget - 终端 Widget
显示串口数据（ASCII/HEX/Decimal）
"""

from PyQt6.QtWidgets import QVBoxLayout, QTextEdit, QHBoxLayout, QLineEdit, QPushButton, QComboBox
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from typing import Dict
from datetime import datetime

from .base_widget import BaseWidget


class TerminalWidget(BaseWidget):
    """终端 Widget"""

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__(widget_data, theme, channel_manager)
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 显示区域
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Consolas", 10))

        if self.theme == 'dark':
            self.text_display.setStyleSheet("""
                QTextEdit {
                    background-color: #0D0D0D;
                    color: #00FF00;
                    border: 1px solid #3A3A3A;
                    border-radius: 4px;
                }
            """)
        else:
            self.text_display.setStyleSheet("""
                QTextEdit {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #D1D5DB;
                    border-radius: 4px;
                }
            """)

        layout.addWidget(self.text_display, 1)

        # 输入区域
        input_layout = QHBoxLayout()

        # 显示模式选择
        self.mode_combo = QComboBox()
        self.mode_combo.addItems(['ASCII', 'HEX', 'Decimal'])
        self.mode_combo.setCurrentText(self.widget_data['config'].get('displayMode', 'ASCII').upper())
        input_layout.addWidget(self.mode_combo)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter data to send...")
        input_layout.addWidget(self.input_field, 1)

        send_btn = QPushButton("Send")
        send_btn.clicked.connect(self._send_data)
        input_layout.addWidget(send_btn)

        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.text_display.clear)
        input_layout.addWidget(clear_btn)

        layout.addLayout(input_layout)

    def _on_data_update(self, data: Dict[str, float]):
        """接收数据更新"""
        for channel in self.get_bound_channels():
            if channel in data:
                self._append_data(channel, data[channel])

    def _append_data(self, channel: str, value: float):
        """添加数据到显示区域"""
        mode = self.mode_combo.currentText().lower()
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        if mode == 'ascii':
            # 将数值转换为 ASCII 字符（如果可能）
            try:
                char = chr(int(value)) if 32 <= int(value) <= 126 else '.'
                text = f"[{timestamp}] {channel}: {char} ({int(value)})\n"
            except:
                text = f"[{timestamp}] {channel}: {value:.2f}\n"
        elif mode == 'hex':
            text = f"[{timestamp}] {channel}: 0x{int(value):02X}\n"
        else:  # decimal
            text = f"[{timestamp}] {channel}: {value:.2f}\n"

        self.text_display.append(text.strip())

        # 自动滚动
        if self.widget_data['config'].get('autoScroll', True):
            self.text_display.verticalScrollBar().setValue(
                self.text_display.verticalScrollBar().maximum()
            )

    def _send_data(self):
        """发送数据"""
        data = self.input_field.text()
        if data:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.text_display.append(f"[{timestamp}] TX: {data}")
            self.input_field.clear()

            # TODO: 实际发送到串口
