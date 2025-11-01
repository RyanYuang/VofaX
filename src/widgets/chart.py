"""
ChartWidget - 图表 Widget
Line/Bar 历史数据图表
"""

from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import QTimer
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from collections import deque
from typing import Dict

from .base_widget import BaseWidget


class ChartWidget(BaseWidget):
    """图表 Widget"""

    COLORS = ['#0A84FF', '#FF9F0A', '#30D158', '#BF5AF2', '#FF453A', '#64D2FF', '#FFD60A', '#FF375F']

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__(widget_data, theme, channel_manager)

        self.max_points = 100
        self.data_buffers = {}  # {channel: deque}

        # 初始化通道缓冲区
        for channel in self.get_bound_channels():
            self.data_buffers[channel] = deque(maxlen=self.max_points)

        self._setup_ui()

        # 定时更新（用于重绘）
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_chart)
        self.timer.start(500)  # 500ms 更新一次

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # 创建 matplotlib figure
        self.figure = Figure(figsize=(5, 3), facecolor='#1A1A1A' if self.theme == 'dark' else '#FFFFFF')
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.ax = self.figure.add_subplot(111)
        self._style_chart()

        layout.addWidget(self.canvas)

    def _style_chart(self):
        """设置图表样式"""
        bg_color = '#1A1A1A' if self.theme == 'dark' else '#FFFFFF'
        grid_color = '#2A2A2A' if self.theme == 'dark' else '#E0E0E0'
        text_color = '#FFFFFF' if self.theme == 'dark' else '#000000'

        self.ax.set_facecolor(bg_color)
        self.ax.set_xlabel('Time', color=text_color)
        self.ax.set_ylabel('Value', color=text_color)

        self.ax.tick_params(colors=text_color)
        self.ax.spines['bottom'].set_color(text_color)
        self.ax.spines['left'].set_color(text_color)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        self.ax.grid(True, color=grid_color, linestyle='--', linewidth=0.5, alpha=0.7)

    def _on_data_update(self, data: Dict[str, float]):
        """接收数据更新"""
        for channel in self.get_bound_channels():
            if channel in data:
                if channel not in self.data_buffers:
                    self.data_buffers[channel] = deque(maxlen=self.max_points)
                self.data_buffers[channel].append(data[channel])

    def _update_chart(self):
        """更新图表"""
        self.ax.clear()
        self._style_chart()

        chart_type = self.widget_data['config'].get('chartType', 'line')

        for idx, (channel, buffer) in enumerate(self.data_buffers.items()):
            if buffer:
                data = list(buffer)
                x = list(range(len(data)))
                color = self.COLORS[idx % len(self.COLORS)]

                if chart_type == 'line':
                    self.ax.plot(x, data, color=color, linewidth=2, label=channel, marker='o', markersize=3)
                elif chart_type == 'bar':
                    self.ax.bar([xi + idx * 0.2 for xi in x], data, width=0.2, color=color, label=channel)

        if self.data_buffers:
            self.ax.legend(loc='upper left',
                          facecolor='#252525' if self.theme == 'dark' else '#FFFFFF',
                          edgecolor='#3A3A3A' if self.theme == 'dark' else '#E0E0E0',
                          labelcolor='#FFFFFF' if self.theme == 'dark' else '#000000')

        self.canvas.draw_idle()

    def update_config(self, widget_data: Dict):
        """更新配置"""
        super().update_config(widget_data)

        # 更新通道
        new_channels = self.get_bound_channels()
        for channel in new_channels:
            if channel not in self.data_buffers:
                self.data_buffers[channel] = deque(maxlen=self.max_points)

        # 移除不再绑定的通道
        for channel in list(self.data_buffers.keys()):
            if channel not in new_channels:
                del self.data_buffers[channel]

        self._update_chart()
