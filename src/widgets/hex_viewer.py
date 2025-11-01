"""
HexViewerWidget - 十六进制查看器 Widget
显示原始数据的十六进制表示
"""

from PyQt6.QtWidgets import QVBoxLayout, QTextEdit
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from typing import Dict
from collections import deque

from .base_widget import BaseWidget


class HexViewerWidget(BaseWidget):
    """十六进制查看器 Widget"""

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__(widget_data, theme, channel_manager)
        self.data_buffer = deque(maxlen=256)  # 保存最近256字节
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.hex_display = QTextEdit()
        self.hex_display.setReadOnly(True)
        self.hex_display.setFont(QFont("Consolas", 9))

        if self.theme == 'dark':
            self.hex_display.setStyleSheet("""
                QTextEdit {
                    background-color: #0D0D0D;
                    color: #00FF00;
                    border: 1px solid #3A3A3A;
                    border-radius: 4px;
                }
            """)
        else:
            self.hex_display.setStyleSheet("""
                QTextEdit {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #D1D5DB;
                    border-radius: 4px;
                }
            """)

        layout.addWidget(self.hex_display)

    def _on_data_update(self, data: Dict[str, float]):
        """接收数据更新"""
        for channel in self.get_bound_channels():
            if channel in data:
                # 将浮点数转换为字节
                byte_val = int(data[channel]) & 0xFF
                self.data_buffer.append(byte_val)

        self._update_display()

    def _update_display(self):
        """更新显示"""
        bytes_per_row = self.widget_data['config'].get('bytesPerRow', 16)

        lines = []
        lines.append("Offset   " + " ".join(f"{i:02X}" for i in range(bytes_per_row)) + "  ASCII")
        lines.append("-" * (10 + 3 * bytes_per_row + 2 + bytes_per_row))

        data_list = list(self.data_buffer)

        for i in range(0, len(data_list), bytes_per_row):
            chunk = data_list[i:i + bytes_per_row]

            # 地址
            offset = f"{i:08X}"

            # 十六进制
            hex_part = " ".join(f"{b:02X}" for b in chunk)
            hex_part = hex_part.ljust(3 * bytes_per_row - 1)

            # ASCII
            ascii_part = "".join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)

            lines.append(f"{offset}  {hex_part}  {ascii_part}")

        self.hex_display.setPlainText("\n".join(lines))
