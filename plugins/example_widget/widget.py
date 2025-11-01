# -*- coding: utf-8 -*-
"""
Example Widget Plugin
"""

from src.widgets.base_widget import BaseWidget
from PyQt6.QtWidgets import QLabel, QVBoxLayout
from PyQt6.QtCore import Qt
from typing import Dict


class ExampleWidget(BaseWidget):
    """示例 Widget"""

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__(widget_data, theme, channel_manager)
        self._setup_ui()

    def _setup_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout(self)

        self.label = QLabel("Example Widget")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("font-size: 24px; color: #00ff00;")

        self.value_label = QLabel("0.00")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setStyleSheet("font-size: 48px;")

        layout.addWidget(self.label)
        layout.addWidget(self.value_label)

    def _on_data_update(self, data: Dict[str, float]):
        """数据更新回调"""
        channels = self.get_bound_channels()
        if channels and channels[0] in data:
            value = data[channels[0]]
            self.value_label.setText(f"{value:.2f}")
