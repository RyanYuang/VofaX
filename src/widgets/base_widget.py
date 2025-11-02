"""
BaseWidget - 所有 Widget 的基类
定义统一接口 + 更新节流机制
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, QTimer
from typing import Dict, List, Any
from abc import ABC, abstractmethod, ABCMeta
import time


class QABCMeta(type(QWidget), ABCMeta):
    """合并 QWidget 和 ABC 的元类"""
    pass


class BaseWidget(QWidget, ABC, metaclass=QABCMeta):
    """Widget 基类（带更新节流）"""

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__()
        self.widget_data = widget_data
        self.theme = theme
        self.channel_manager = channel_manager

        # 更新节流机制
        self.update_interval = 50  # 默认 50ms (20Hz)
        self.pending_data = {}  # 待处理的数据
        self.last_update_time = 0

        # 更新定时器
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._process_pending_updates)
        self.update_timer.start(self.update_interval)

        # 订阅通道更新
        if channel_manager:
            self._subscribe_channels()

    def _subscribe_channels(self):
        """订阅绑定的通道数据"""
        if self.channel_manager:
            self.channel_manager.batch_updated.connect(self._on_data_received)

    def _on_data_received(self, data: Dict[str, float]):
        """
        数据接收回调（节流前）

        Args:
            data: {channel: value} 字典
        """
        # 缓存数据，等待定时器触发批量更新
        for channel, value in data.items():
            if channel in self.get_bound_channels():
                self.pending_data[channel] = value

    def _process_pending_updates(self):
        """处理待更新的数据（节流后）"""
        if self.pending_data:
            # 调用子类的更新方法
            self._on_data_update(self.pending_data.copy())
            self.pending_data.clear()

    @abstractmethod
    def _on_data_update(self, data: Dict[str, float]):
        """
        数据更新回调（已节流）

        Args:
            data: {channel: value} 字典
        """
        pass

    def set_update_interval(self, interval_ms: int):
        """
        设置更新间隔

        Args:
            interval_ms: 更新间隔（毫秒）
        """
        self.update_interval = interval_ms
        if self.update_timer:
            self.update_timer.setInterval(interval_ms)

    def get_bound_channels(self) -> List[str]:
        """获取绑定的通道列表"""
        return self.widget_data.get('dataBinding', {}).get('channels', [])

    def update_config(self, widget_data: Dict):
        """
        更新配置

        Args:
            widget_data: 新的 Widget 数据
        """
        self.widget_data = widget_data
        # 子类可以重写此方法以响应配置变更
