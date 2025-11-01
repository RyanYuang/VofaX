"""
OscilloscopeWidget - 示波器 Widget
多通道波形显示
"""

from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np
from collections import deque
from typing import Dict

from .base_widget import BaseWidget


class OscilloscopeWidget(BaseWidget):
    """示波器 Widget"""

    COLORS = ['#0A84FF', '#FF9F0A', '#30D158', '#BF5AF2', '#FF453A', '#64D2FF', '#FFD60A', '#FF375F']

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__(widget_data, theme, channel_manager)

        # 数据缓冲区
        self.time_window = widget_data['config'].get('timeBase', 50) / 1000  # 转换为秒
        self.max_points = 200
        self.data_buffers = {}  # {channel: deque}

        # 初始化通道缓冲区
        for channel in self.get_bound_channels():
            self.data_buffers[channel] = deque(maxlen=self.max_points)

        self._setup_ui()

        # 定时更新（模拟数据）
        self.timer = QTimer()
        self.timer.timeout.connect(self._generate_mock_data)
        self.timer.start(50)  # 50ms 更新一次

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # 创建 matplotlib figure
        self.figure = Figure(figsize=(5, 3), facecolor='#1A1A1A' if self.theme == 'dark' else '#FFFFFF')
        self.canvas = FigureCanvasQTAgg(self.figure)

        self.ax = self.figure.add_subplot(111)
        self._style_plot()

        layout.addWidget(self.canvas)

        # 初始化线条
        self.lines = {}
        for idx, channel in enumerate(self.get_bound_channels()):
            line, = self.ax.plot([], [],
                               color=self.COLORS[idx % len(self.COLORS)],
                               linewidth=2,
                               label=channel)
            self.lines[channel] = line

        if self.lines:
            self.ax.legend(loc='upper right',
                          facecolor='#252525' if self.theme == 'dark' else '#FFFFFF',
                          edgecolor='#3A3A3A' if self.theme == 'dark' else '#E0E0E0',
                          labelcolor='#FFFFFF' if self.theme == 'dark' else '#000000')

    def _style_plot(self):
        """设置图表样式"""
        bg_color = '#1A1A1A' if self.theme == 'dark' else '#FFFFFF'
        grid_color = '#2A2A2A' if self.theme == 'dark' else '#E0E0E0'
        text_color = '#FFFFFF' if self.theme == 'dark' else '#000000'

        self.ax.set_facecolor(bg_color)
        self.ax.set_xlabel('Time (ms)', color=text_color)
        self.ax.set_ylabel('Value', color=text_color)

        self.ax.tick_params(colors=text_color)
        self.ax.spines['bottom'].set_color(text_color)
        self.ax.spines['left'].set_color(text_color)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        if self.widget_data['config'].get('showGrid', True):
            self.ax.grid(True, color=grid_color, linestyle='--', linewidth=0.5, alpha=0.7)

    def _generate_mock_data(self):
        """生成模拟数据（用于演示）"""
        # 模拟正弦波数据
        t = len(self.data_buffers.get(self.get_bound_channels()[0], [])) if self.get_bound_channels() else 0

        for idx, channel in enumerate(self.get_bound_channels()):
            value = np.sin(t * 0.1 + idx) * 2 + np.random.randn() * 0.1
            if channel not in self.data_buffers:
                self.data_buffers[channel] = deque(maxlen=self.max_points)
            self.data_buffers[channel].append(value)

        self._update_plot()

    def _on_data_update(self, data: Dict[str, float]):
        """接收真实数据更新"""
        for channel in self.get_bound_channels():
            if channel in data:
                if channel not in self.data_buffers:
                    self.data_buffers[channel] = deque(maxlen=self.max_points)
                self.data_buffers[channel].append(data[channel])

        self._update_plot()

    def _update_plot(self):
        """更新图表"""
        for channel, line in self.lines.items():
            if channel in self.data_buffers and self.data_buffers[channel]:
                y_data = list(self.data_buffers[channel])
                x_data = list(range(len(y_data)))
                line.set_data(x_data, y_data)

        # 自动调整坐标轴
        self.ax.relim()
        self.ax.autoscale_view()

        self.canvas.draw_idle()

    def update_config(self, widget_data: Dict):
        """更新配置"""
        super().update_config(widget_data)

        # 更新时基
        self.time_window = widget_data['config'].get('timeBase', 50) / 1000

        # 更新网格
        self._style_plot()

        # 更新通道
        new_channels = self.get_bound_channels()
        # 移除不再绑定的通道
        for channel in list(self.lines.keys()):
            if channel not in new_channels:
                self.lines[channel].remove()
                del self.lines[channel]
                if channel in self.data_buffers:
                    del self.data_buffers[channel]

        # 添加新通道
        for idx, channel in enumerate(new_channels):
            if channel not in self.lines:
                line, = self.ax.plot([], [],
                                   color=self.COLORS[idx % len(self.COLORS)],
                                   linewidth=2,
                                   label=channel)
                self.lines[channel] = line
                self.data_buffers[channel] = deque(maxlen=self.max_points)

        # 更新图例
        if self.lines:
            self.ax.legend()

        self.canvas.draw()
