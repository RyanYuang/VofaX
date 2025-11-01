"""
GaugeWidget - 仪表盘 Widget
圆形仪表显示单通道数据
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QConicalGradient
from typing import Dict
import math

from .base_widget import BaseWidget


class GaugeWidget(BaseWidget):
    """仪表盘 Widget"""

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__(widget_data, theme, channel_manager)
        self.current_value = 0.0
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 仪表盘绘制区域
        self.gauge_widget = GaugeDisplay(
            self.current_value,
            self.widget_data['config'].get('min', 0),
            self.widget_data['config'].get('max', 100),
            self.widget_data['config'].get('unit', ''),
            self.theme
        )

        layout.addWidget(self.gauge_widget, 1)

    def _on_data_update(self, data: Dict[str, float]):
        """接收数据更新"""
        channels = self.get_bound_channels()
        if channels and channels[0] in data:
            self.current_value = data[channels[0]]
            self.gauge_widget.set_value(self.current_value)


class GaugeDisplay(QWidget):
    """仪表盘显示组件"""

    def __init__(self, value: float, min_val: float, max_val: float, unit: str, theme: str):
        super().__init__()
        self.value = value
        self.min_val = min_val
        self.max_val = max_val
        self.unit = unit
        self.theme = theme
        self.setMinimumSize(200, 200)

    def set_value(self, value: float):
        """设置值"""
        self.value = max(self.min_val, min(self.max_val, value))
        self.update()

    def paintEvent(self, event):
        """绘制仪表盘"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        width = self.width()
        height = self.height()
        size = min(width, height)

        # 中心点
        cx = width / 2
        cy = height / 2
        radius = size / 2 - 20

        # 背景圆
        bg_color = QColor(26, 26, 26) if self.theme == 'dark' else QColor(245, 245, 245)
        painter.setBrush(bg_color)
        painter.setPen(QPen(QColor(58, 58, 58) if self.theme == 'dark' else QColor(224, 224, 224), 2))
        painter.drawEllipse(int(cx - radius), int(cy - radius), int(radius * 2), int(radius * 2))

        # 刻度弧
        start_angle = 225 * 16  # Qt 使用1/16度
        span_angle = -270 * 16

        # 绘制刻度
        painter.setPen(QPen(QColor(58, 58, 58) if self.theme == 'dark' else QColor(209, 213, 219), 8))
        painter.drawArc(int(cx - radius + 10), int(cy - radius + 10),
                       int((radius - 10) * 2), int((radius - 10) * 2),
                       start_angle, span_angle)

        # 绘制值弧
        value_ratio = (self.value - self.min_val) / (self.max_val - self.min_val) if self.max_val != self.min_val else 0
        value_angle = int(value_ratio * -270 * 16)

        painter.setPen(QPen(QColor(10, 132, 255), 8))
        painter.drawArc(int(cx - radius + 10), int(cy - radius + 10),
                       int((radius - 10) * 2), int((radius - 10) * 2),
                       start_angle, value_angle)

        # 绘制中心值文本
        painter.setPen(QColor(255, 255, 255) if self.theme == 'dark' else QColor(0, 0, 0))
        painter.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        value_text = f"{self.value:.1f}"
        text_rect = painter.fontMetrics().boundingRect(value_text)
        painter.drawText(int(cx - text_rect.width() / 2), int(cy - 10), value_text)

        # 绘制单位
        painter.setFont(QFont("Arial", 12))
        unit_rect = painter.fontMetrics().boundingRect(self.unit)
        painter.drawText(int(cx - unit_rect.width() / 2), int(cy + 20), self.unit)

        # 绘制最小/最大值
        painter.setFont(QFont("Arial", 10))
        painter.setPen(QColor(153, 153, 153))
        painter.drawText(int(cx - radius), int(cy + radius + 15), f"{self.min_val:.0f}")
        max_text = f"{self.max_val:.0f}"
        max_rect = painter.fontMetrics().boundingRect(max_text)
        painter.drawText(int(cx + radius - max_rect.width()), int(cy + radius + 15), max_text)
