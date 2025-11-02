"""
OscilloscopeWidget - 示波器 Widget (优化版)
多通道波形显示 + matplotlib blitting 优化
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
    """示波器 Widget (高性能版)"""

    COLORS = ['#0A84FF', '#FF9F0A', '#30D158', '#BF5AF2', '#FF453A', '#64D2FF', '#FFD60A', '#FF375F']

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__(widget_data, theme, channel_manager)

        # 数据缓冲区
        self.time_window = widget_data['config'].get('timeBase', 50) / 1000  # 转换为秒
        self.max_points = 500  # 增加到 500 点以获得更平滑的曲线
        self.data_buffers = {}  # {channel: deque}

        # 性能优化标志
        self.use_blitting = True  # 使用 blitting 优化
        self.background = None  # 背景缓存

        # 初始化通道缓冲区
        for channel in self.get_bound_channels():
            self.data_buffers[channel] = deque(maxlen=self.max_points)

        self._setup_ui()

        # 设置更新间隔为 50ms (20Hz) - 平衡性能和流畅度
        self.set_update_interval(50)

        # 模拟数据定时器（仅用于演示，实际数据来自串口）
        self.mock_timer = QTimer()
        self.mock_timer.timeout.connect(self._generate_mock_data)
        # self.mock_timer.start(20)  # 默认关闭模拟数据

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # 创建 matplotlib figure
        self.figure = Figure(figsize=(5, 3), facecolor='#1A1A1A' if self.theme == 'dark' else '#FFFFFF')
        self.canvas = FigureCanvasQTAgg(self.figure)

        # 关闭 matplotlib 的默认动画，我们使用 blitting 手动控制
        self.canvas.mpl_connect('draw_event', self._on_draw)

        self.ax = self.figure.add_subplot(111)
        self._style_plot()

        layout.addWidget(self.canvas)

        # 初始化线条
        self.lines = {}
        for idx, channel in enumerate(self.get_bound_channels()):
            line, = self.ax.plot([], [],
                               color=self.COLORS[idx % len(self.COLORS)],
                               linewidth=1.5,
                               label=channel,
                               animated=True)  # 启用动画优化
            self.lines[channel] = line

        if self.lines:
            self.ax.legend(loc='upper right',
                          facecolor='#252525' if self.theme == 'dark' else '#FFFFFF',
                          edgecolor='#3A3A3A' if self.theme == 'dark' else '#E0E0E0',
                          labelcolor='#FFFFFF' if self.theme == 'dark' else '#000000',
                          framealpha=0.8)

        # 初始化坐标轴范围
        self.ax.set_xlim(0, self.max_points)
        self.ax.set_ylim(-5, 5)

        # 绘制初始画布并缓存背景
        self.canvas.draw()

    def _style_plot(self):
        """设置图表样式"""
        bg_color = '#1A1A1A' if self.theme == 'dark' else '#FFFFFF'
        grid_color = '#2A2A2A' if self.theme == 'dark' else '#E0E0E0'
        text_color = '#FFFFFF' if self.theme == 'dark' else '#000000'

        self.ax.set_facecolor(bg_color)
        self.ax.set_xlabel('Samples', color=text_color, fontsize=9)
        self.ax.set_ylabel('Value', color=text_color, fontsize=9)

        self.ax.tick_params(colors=text_color, labelsize=8)
        self.ax.spines['bottom'].set_color(text_color)
        self.ax.spines['left'].set_color(text_color)
        self.ax.spines['top'].set_visible(False)
        self.ax.spines['right'].set_visible(False)

        if self.widget_data['config'].get('showGrid', True):
            self.ax.grid(True, color=grid_color, linestyle='--', linewidth=0.5, alpha=0.7)

    def _on_draw(self, event):
        """绘制事件回调 - 缓存背景"""
        if self.use_blitting:
            self.background = self.canvas.copy_from_bbox(self.ax.bbox)

    def _generate_mock_data(self):
        """生成模拟数据（用于演示）"""
        # 模拟正弦波数据
        t = len(self.data_buffers.get(self.get_bound_channels()[0], [])) if self.get_bound_channels() else 0

        mock_data = {}
        for idx, channel in enumerate(self.get_bound_channels()):
            value = np.sin(t * 0.05 + idx * 0.5) * 2 + np.random.randn() * 0.1
            mock_data[channel] = value

        # 使用节流后的更新机制
        self._on_data_received(mock_data)

    def _on_data_update(self, data: Dict[str, float]):
        """接收真实数据更新（已节流）"""
        # 添加数据到缓冲区
        for channel in self.get_bound_channels():
            if channel in data:
                if channel not in self.data_buffers:
                    self.data_buffers[channel] = deque(maxlen=self.max_points)
                self.data_buffers[channel].append(data[channel])

        # 高性能更新图表
        self._update_plot_fast()

    def _update_plot_fast(self):
        """高性能更新图表（使用 blitting）"""
        if not self.use_blitting or self.background is None:
            # Fallback: 完整重绘
            self._update_plot_full()
            return

        # 恢复背景
        self.canvas.restore_region(self.background)

        # 更新所有线条数据
        y_min, y_max = float('inf'), float('-inf')
        for channel, line in self.lines.items():
            if channel in self.data_buffers and self.data_buffers[channel]:
                y_data = list(self.data_buffers[channel])
                x_data = list(range(len(y_data)))
                line.set_data(x_data, y_data)

                # 计算 Y 轴范围
                if y_data:
                    y_min = min(y_min, min(y_data))
                    y_max = max(y_max, max(y_data))

                # 只重绘变化的线条
                self.ax.draw_artist(line)

        # 智能 Y 轴自动缩放（仅在必要时）
        if y_min != float('inf'):
            current_ylim = self.ax.get_ylim()
            margin = (y_max - y_min) * 0.1 or 1
            new_ylim = (y_min - margin, y_max + margin)

            # 仅当范围变化超过 10% 时才更新
            if abs(new_ylim[0] - current_ylim[0]) > abs(current_ylim[0]) * 0.1 or \
               abs(new_ylim[1] - current_ylim[1]) > abs(current_ylim[1]) * 0.1:
                self.ax.set_ylim(new_ylim)
                # 需要重新绘制背景
                self.canvas.draw()
                return

        # 刷新画布（只更新变化的部分）
        self.canvas.blit(self.ax.bbox)

    def _update_plot_full(self):
        """完整更新图表（Fallback）"""
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
                                   linewidth=1.5,
                                   label=channel,
                                   animated=True)
                self.lines[channel] = line
                self.data_buffers[channel] = deque(maxlen=self.max_points)

        # 更新图例
        if self.lines:
            self.ax.legend()

        # 重新绘制并缓存背景
        self.canvas.draw()

    def enable_mock_data(self, enabled: bool = True):
        """启用/禁用模拟数据（调试用）"""
        if enabled:
            self.mock_timer.start(20)  # 50Hz
        else:
            self.mock_timer.stop()
