"""
PacketAnalyzerWidget - 协议分析器 Widget
解析和显示数据包
"""

from PyQt6.QtWidgets import QVBoxLayout, QTextEdit, QLabel, QHBoxLayout
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt
from typing import Dict
from datetime import datetime

from .base_widget import BaseWidget


class PacketAnalyzerWidget(BaseWidget):
    """协议分析器 Widget"""

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__(widget_data, theme, channel_manager)
        self.packet_count = 0
        self.error_count = 0
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # 统计信息
        stats_layout = QHBoxLayout()

        self.packet_label = QLabel(f"Packets: {self.packet_count}")
        self.error_label = QLabel(f"Errors: {self.error_count}")
        self.error_label.setStyleSheet("color: #FF453A;")

        stats_layout.addWidget(self.packet_label)
        stats_layout.addWidget(self.error_label)
        stats_layout.addStretch()

        layout.addLayout(stats_layout)

        # 数据包显示区域
        self.packet_display = QTextEdit()
        self.packet_display.setReadOnly(True)
        self.packet_display.setFont(QFont("Consolas", 9))

        if self.theme == 'dark':
            self.packet_display.setStyleSheet("""
                QTextEdit {
                    background-color: #0D0D0D;
                    color: #00FF00;
                    border: 1px solid #3A3A3A;
                    border-radius: 4px;
                }
            """)
        else:
            self.packet_display.setStyleSheet("""
                QTextEdit {
                    background-color: #FFFFFF;
                    color: #000000;
                    border: 1px solid #D1D5DB;
                    border-radius: 4px;
                }
            """)

        layout.addWidget(self.packet_display, 1)

    def _on_data_update(self, data: Dict[str, float]):
        """接收数据更新"""
        for channel in self.get_bound_channels():
            if channel in data:
                self._analyze_packet(channel, data[channel])

    def _analyze_packet(self, channel: str, value: float):
        """分析数据包"""
        self.packet_count += 1
        self.packet_label.setText(f"Packets: {self.packet_count}")

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        protocol = self.widget_data['config'].get('protocol', 'custom')

        if protocol == 'modbus':
            # 简单的 Modbus 模拟解析
            packet_info = self._parse_modbus(value)
        else:
            # 自定义协议
            packet_info = f"Channel: {channel}, Value: {value:.2f}, Raw: 0x{int(value):02X}"

        # 添加到显示
        self.packet_display.append(f"[{timestamp}] Packet #{self.packet_count}: {packet_info}\n")

        # 自动滚动
        self.packet_display.verticalScrollBar().setValue(
            self.packet_display.verticalScrollBar().maximum()
        )

    def _parse_modbus(self, value: float) -> str:
        """解析 Modbus 包（简化版）"""
        byte_val = int(value) & 0xFF

        # 简化的 Modbus 解析
        function_codes = {
            0x01: "Read Coils",
            0x03: "Read Holding Registers",
            0x06: "Write Single Register",
            0x10: "Write Multiple Registers"
        }

        func = function_codes.get(byte_val, "Unknown Function")
        return f"Function: {func} (0x{byte_val:02X})"
