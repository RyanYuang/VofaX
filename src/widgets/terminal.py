"""
TerminalWidget - 终端 Widget (优化版)
显示串口数据（ASCII/HEX/Decimal）+ 批量更新优化
"""

from PyQt6.QtWidgets import QVBoxLayout, QPlainTextEdit, QHBoxLayout, QLineEdit, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from typing import Dict, List, Union
from datetime import datetime
from collections import deque

from .base_widget import BaseWidget
from ..components.styled_button import SmallButton


class TerminalWidget(BaseWidget):
    """终端 Widget (高性能版)"""

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__(widget_data, theme, channel_manager)

        # 性能优化配置
        self.max_lines = 1000  # 最大显示行数
        self.batch_size = 10  # 批量更新阈值
        self.pending_lines = deque()  # 待显示的行缓冲

        self._setup_ui()

        # 设置更新间隔为 100ms (10Hz) - Terminal 不需要太高频率
        self.set_update_interval(100)

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # 设置 Widget 本身的尺寸策略
        from PyQt6.QtWidgets import QSizePolicy
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # 设置最小尺寸
        self.setMinimumSize(200, 150)

        # 使用 QPlainTextEdit 替代 QTextEdit (性能更好)
        self.text_display = QPlainTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Consolas", 10))
        self.text_display.setMaximumBlockCount(self.max_lines)  # 限制最大行数

        if self.theme == 'dark':
            self.text_display.setStyleSheet("""
                QPlainTextEdit {
                    background-color: #0D0D0D;
                    color: #00FF00;
                    border: 1px solid #3A3A3A;
                    border-radius: 4px;
                }
            """)
        else:
            self.text_display.setStyleSheet("""
                QPlainTextEdit {
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

        send_btn = SmallButton("Send", self.theme)
        send_btn.clicked.connect(self._send_data)
        input_layout.addWidget(send_btn)

        clear_btn = SmallButton("Clear", self.theme)
        clear_btn.clicked.connect(self.text_display.clear)
        input_layout.addWidget(clear_btn)

        layout.addLayout(input_layout)

    def _on_data_update(self, data: Dict[str, Union[float, str]]):
        """接收数据更新（已节流）"""
        # Debug: 打印接收到的数据
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"[Terminal] Received data: {data}, bound channels: {self.get_bound_channels()}")

        # 处理 RAW 文本数据（ASCII 协议的原始文本）
        if 'RAW' in data:
            line = self._format_raw_line(data['RAW'])
            self.pending_lines.append(line)
            logger.info(f"[Terminal] Added RAW line: {line}")

        # 批量处理数据
        for channel in self.get_bound_channels():
            if channel in data:
                line = self._format_data_line(channel, data[channel])
                self.pending_lines.append(line)
                logger.info(f"[Terminal] Added line: {line}")

        # 批量追加到显示区域
        if len(self.pending_lines) >= self.batch_size:
            self._flush_pending_lines()

    def _process_pending_updates(self):
        """定时刷新待显示的行（从父类重写）"""
        super()._process_pending_updates()

        # 刷新剩余的待显示行
        if self.pending_lines:
            self._flush_pending_lines()

    def _flush_pending_lines(self):
        """批量刷新待显示的行"""
        if not self.pending_lines:
            return

        # 批量追加文本（性能优化）
        batch_text = "\n".join(self.pending_lines)
        self.text_display.appendPlainText(batch_text)
        self.pending_lines.clear()

        # 自动滚动
        if self.widget_data['config'].get('autoScroll', True):
            scrollbar = self.text_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())

    def _format_data_line(self, channel: str, value: float) -> str:
        """格式化数据行"""
        mode = self.mode_combo.currentText().lower()
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        if mode == 'ascii':
            # 将数值转换为 ASCII 字符（如果可能）
            try:
                int_value = int(value)
                char = chr(int_value) if 32 <= int_value <= 126 else '.'
                return f"[{timestamp}] {channel}: {char} ({int_value})"
            except:
                return f"[{timestamp}] {channel}: {value:.2f}"
        elif mode == 'hex':
            return f"[{timestamp}] {channel}: 0x{int(value):02X}"
        else:  # decimal
            return f"[{timestamp}] {channel}: {value:.2f}"

    def _format_raw_line(self, text: str) -> str:
        """格式化原始文本行"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        # 如果 text 已经是字符串就直接用，否则转换
        if isinstance(text, (int, float)):
            # 这是一个数字被当作字符串传递的情况
            return f"[{timestamp}] {text}"
        return f"[{timestamp}] {text}"

    def _send_data(self):
        """发送数据"""
        data = self.input_field.text()
        if data:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            self.text_display.appendPlainText(f"[{timestamp}] TX: {data}")
            self.input_field.clear()

            # TODO: 实际发送到串口
            # if self.channel_manager and hasattr(self.channel_manager, 'serial_manager'):
            #     self.channel_manager.serial_manager.write_string(data + '\n')

    def set_max_lines(self, max_lines: int):
        """设置最大显示行数"""
        self.max_lines = max_lines
        self.text_display.setMaximumBlockCount(max_lines)

    def set_batch_size(self, batch_size: int):
        """设置批量更新阈值"""
        self.batch_size = batch_size
