"""
OscilloscopeWidget - 示波器 Widget (PyQtGraph 版本)
多通道波形显示 + 高性能实时绘图
"""

from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QCheckBox
from PyQt6.QtCore import QTimer
import pyqtgraph as pg
import numpy as np
from collections import deque
from typing import Dict, Optional, Union

from .base_widget import BaseWidget
from ..components.styled_button import SmallButton


class OscilloscopeWidget(BaseWidget):
    """示波器 Widget (PyQtGraph 高性能版)"""

    COLORS = ['#0A84FF', '#FF9F0A', '#30D158', '#BF5AF2', '#FF453A', '#64D2FF', '#FFD60A', '#FF375F']

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__(widget_data, theme, channel_manager)

        # 数据缓冲区
        self.time_window = widget_data['config'].get('timeBase', 50) / 1000  # 转换为秒
        self.max_points = 1000  # PyQtGraph 可以处理更多点
        self.data_buffers = {}  # {channel: deque}
        self.protocol = self._get_protocol()

        # 性能优化标志
        self.enable_opengl = False  # 可选的 OpenGL 加速
        self.enable_antialias = True  # 抗锯齿

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
        layout.setSpacing(8)

        # 配置 PyQtGraph 全局选项
        pg.setConfigOptions(antialias=self.enable_antialias)

        # 创建 PlotWidget
        self.plot_widget = pg.PlotWidget()

        # 启用 OpenGL 加速（可选）
        if self.enable_opengl:
            try:
                self.plot_widget.useOpenGL(True)
            except:
                pass  # OpenGL 不可用时静默失败

        # 获取 PlotItem
        self.plot_item = self.plot_widget.getPlotItem()

        # 设置样式
        self._style_plot()

        # 初始化曲线
        self.curves = {}
        for idx, channel in enumerate(self.get_bound_channels()):
            color = self.COLORS[idx % len(self.COLORS)]
            curve = self.plot_item.plot(
                pen=pg.mkPen(color=color, width=2),
                name=channel
            )
            self.curves[channel] = curve

        # 添加图例
        if self.curves:
            self.plot_item.addLegend(offset=(10, 10))

        layout.addWidget(self.plot_widget)

        # 控制按钮栏
        controls_layout = QHBoxLayout()

        # 自动缩放按钮
        self.auto_scale_btn = SmallButton("Auto Scale", self.theme)
        self.auto_scale_btn.clicked.connect(self._auto_scale)
        controls_layout.addWidget(self.auto_scale_btn)

        # 清除数据按钮
        self.clear_btn = SmallButton("Clear", self.theme)
        self.clear_btn.clicked.connect(self._clear_data)
        controls_layout.addWidget(self.clear_btn)

        # OpenGL 开关
        self.opengl_checkbox = QCheckBox("OpenGL")
        self.opengl_checkbox.setChecked(self.enable_opengl)
        self.opengl_checkbox.stateChanged.connect(self._toggle_opengl)
        controls_layout.addWidget(self.opengl_checkbox)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

    def _style_plot(self):
        """设置图表样式"""
        # 背景颜色
        if self.theme == 'dark':
            self.plot_widget.setBackground('#1A1A1A')
            text_color = '#FFFFFF'
            grid_color = '#2A2A2A'
        else:
            self.plot_widget.setBackground('#FFFFFF')
            text_color = '#000000'
            grid_color = '#E0E0E0'

        # 坐标轴标签
        self.plot_item.setLabel('left', 'Value', color=text_color)
        self.plot_item.setLabel('bottom', 'Samples', color=text_color)

        # 坐标轴样式
        self.plot_item.getAxis('left').setPen(pg.mkPen(color=text_color, width=1))
        self.plot_item.getAxis('bottom').setPen(pg.mkPen(color=text_color, width=1))
        self.plot_item.getAxis('left').setTextPen(pg.mkPen(color=text_color))
        self.plot_item.getAxis('bottom').setTextPen(pg.mkPen(color=text_color))

        # 网格
        if self.widget_data['config'].get('showGrid', True):
            self.plot_item.showGrid(x=True, y=True, alpha=0.3)

        # 设置坐标轴范围
        self.plot_item.setXRange(0, self.max_points)
        self.plot_item.setYRange(-5, 5)

        # 启用鼠标交互
        self.plot_item.enableAutoRange(axis='xy', enable=False)
        self.plot_item.setMouseEnabled(x=True, y=True)  # 允许缩放
        self.plot_widget.setMenuEnabled(False)  # 禁用右键菜单

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

    def _on_data_update(self, data: Dict[str, Union[float, str]]):
        """接收真实数据更新（已节流）"""
        processed_data = self._prepare_protocol_data(data)

        # 添加数据到缓冲区
        for channel in self.get_bound_channels():
            if channel in processed_data:
                if channel not in self.data_buffers:
                    self.data_buffers[channel] = deque(maxlen=self.max_points)
                self.data_buffers[channel].append(processed_data[channel])

        # 高性能更新图表
        self._update_plot()

    def _update_plot(self):
        """高性能更新图表（PyQtGraph 自动优化）"""
        for channel, curve in self.curves.items():
            if channel in self.data_buffers and self.data_buffers[channel]:
                y_data = np.array(self.data_buffers[channel])
                x_data = np.arange(len(y_data))

                # PyQtGraph 的 setData 已经高度优化
                # 内部使用 C++ 实现，比 matplotlib 快 5-10x
                curve.setData(x_data, y_data)

    def _auto_scale(self):
        """自动缩放"""
        # 启用自动范围
        self.plot_item.enableAutoRange(axis='xy', enable=True)

        # 重新计算范围
        self.plot_item.autoRange()

        # 禁用自动范围（允许用户手动缩放）
        self.plot_item.enableAutoRange(axis='xy', enable=False)

    def _clear_data(self):
        """清除数据"""
        for channel in self.data_buffers:
            self.data_buffers[channel].clear()

        for curve in self.curves.values():
            curve.setData([], [])

    def _toggle_opengl(self, state):
        """切换 OpenGL 加速"""
        try:
            self.plot_widget.useOpenGL(state == 2)  # Qt.CheckState.Checked = 2
            self.enable_opengl = (state == 2)
        except Exception as e:
            print(f"OpenGL toggle failed: {e}")

    def update_config(self, widget_data: Dict):
        """更新配置"""
        super().update_config(widget_data)
        self.protocol = self._get_protocol()

        # 更新时基
        self.time_window = widget_data['config'].get('timeBase', 50) / 1000

        # 更新网格
        if self.widget_data['config'].get('showGrid', True):
            self.plot_item.showGrid(x=True, y=True, alpha=0.3)
        else:
            self.plot_item.showGrid(x=False, y=False)

        # 更新通道
        new_channels = self.get_bound_channels()

        # 移除不再绑定的通道
        for channel in list(self.curves.keys()):
            if channel not in new_channels:
                self.plot_item.removeItem(self.curves[channel])
                del self.curves[channel]
                if channel in self.data_buffers:
                    del self.data_buffers[channel]

        # 添加新通道
        for idx, channel in enumerate(new_channels):
            if channel not in self.curves:
                color = self.COLORS[idx % len(self.COLORS)]
                curve = self.plot_item.plot(
                    pen=pg.mkPen(color=color, width=2),
                    name=channel
                )
                self.curves[channel] = curve
                self.data_buffers[channel] = deque(maxlen=self.max_points)

        # 更新图例
        self.plot_item.clear()
        for channel, curve in self.curves.items():
            self.plot_item.addItem(curve)
        if self.curves:
            self.plot_item.addLegend(offset=(10, 10))

    def enable_mock_data(self, enabled: bool = True):
        """启用/禁用模拟数据（调试用）"""
        if enabled:
            self.mock_timer.start(20)  # 50Hz
        else:
            self.mock_timer.stop()

    def _get_protocol(self) -> str:
        """读取 Inspector 中配置的协议"""
        return self.widget_data.get('config', {}).get('protocol', 'FireWater').lower()

    def _prepare_protocol_data(self, data: Dict[str, Union[float, str]]) -> Dict[str, float]:
        """
        根据配置的协议转换数据。
        FireWater/JustFloat 数据可直接使用，ASCII 需要从 RAW 文本解析。
        """
        processed = {
            k: float(v) for k, v in data.items()
            if k != 'RAW' and isinstance(v, (int, float))
        }

        if self.protocol == 'ascii' and 'RAW' in data:
            ascii_values = self._parse_ascii_payload(str(data['RAW']))
            processed.update(ascii_values)

        return processed

    def _parse_ascii_payload(self, raw_text: str) -> Dict[str, float]:
        """解析 ASCII 文本，提取通道数据（格式: CH0:1.23,CH1:4.56）"""
        parsed = {}
        if not raw_text:
            return parsed

        for line in raw_text.replace('\r', '\n').split('\n'):
            if not line.strip():
                continue

            for segment in line.split(','):
                part = segment.strip()
                if not part or ':' not in part:
                    continue

                name, value = part.split(':', 1)
                channel = self._normalize_channel_name(name)
                if not channel:
                    continue

                try:
                    parsed[channel] = float(value.strip())
                except ValueError:
                    continue

        return parsed

    def _normalize_channel_name(self, name: str) -> Optional[str]:
        """将 CH0/CH1 等文本映射到 I0/I1 通道名称"""
        cleaned = name.strip().upper()
        if cleaned.startswith('CH'):
            suffix = cleaned[2:].strip()
        elif cleaned.startswith('I'):
            suffix = cleaned[1:].strip()
        else:
            suffix = ''

        if suffix.isdigit():
            return f'I{int(suffix)}'

        # 未能识别出编号时返回原始名称，保证尽量兼容
        return cleaned if cleaned else None
