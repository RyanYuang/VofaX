"""
通道管理器
管理 I0-I14 数据通道，分发数据到订阅的 Widgets
"""

from PyQt6.QtCore import QObject, pyqtSignal
from collections import deque
from typing import Dict, List, Deque, Union, Any
import time
import logging

logger = logging.getLogger(__name__)


class ChannelManager(QObject):
    """
    数据通道管理类
    使用观察者模式，Widget 订阅感兴趣的通道
    """

    # 信号：通道数据更新 (channel_name, value, timestamp)
    channel_updated = pyqtSignal(str, float, float)

    # 信号：批量更新 (dict of {channel: value})
    batch_updated = pyqtSignal(dict)

    def __init__(self, history_size: int = 1000):
        """
        初始化通道管理器

        Args:
            history_size: 每个通道保留的历史数据点数
        """
        super().__init__()

        self.history_size = history_size

        # 当前值字典 {channel_name: latest_value}
        self.current_values: Dict[str, float] = {}

        # 历史数据 {channel_name: deque[(timestamp, value)]}
        self.history: Dict[str, Deque[tuple]] = {}

        # 订阅者字典 {channel_name: set(subscriber_ids)}
        self.subscribers: Dict[str, set] = {}

        # 初始化 15 个通道 (I0-I14)
        for i in range(15):
            channel = f"I{i}"
            self.current_values[channel] = 0.0
            self.history[channel] = deque(maxlen=history_size)
            self.subscribers[channel] = set()

    def update_channel(self, channel: str, value: float):
        """
        更新单个通道数据

        Args:
            channel: 通道名称 (e.g., 'I0', 'I1')
            value: 新值
        """
        if channel not in self.current_values:
            # 动态添加新通道
            self.current_values[channel] = 0.0
            self.history[channel] = deque(maxlen=self.history_size)

        timestamp = time.time()

        # 更新当前值
        self.current_values[channel] = value

        # 添加到历史
        self.history[channel].append((timestamp, value))

        # 发射信号
        self.channel_updated.emit(channel, value, timestamp)

    def update_batch(self, data: Dict[str, Union[float, str]]):
        """
        批量更新多个通道

        Args:
            data: 字典 {channel: value}，value 可以是 float 或 str (RAW 文本)
        """
        logger.info(f"[ChannelManager] update_batch called with data: {data}")

        timestamp = time.time()

        for channel, value in data.items():
            if channel not in self.current_values:
                self.current_values[channel] = 0.0
                self.history[channel] = deque(maxlen=self.history_size)
                logger.debug(f"[ChannelManager] Added new channel: {channel}")

            self.current_values[channel] = value
            self.history[channel].append((timestamp, value))

        # 发射批量更新信号
        logger.info(f"[ChannelManager] Emitting batch_updated signal with {len(data)} channels")
        self.batch_updated.emit(data)
        logger.info(f"[ChannelManager] batch_updated signal emitted")

    def get_current_value(self, channel: str) -> float:
        """
        获取通道当前值

        Args:
            channel: 通道名称

        Returns:
            当前值，不存在返回 0.0
        """
        return self.current_values.get(channel, 0.0)

    def get_history(self, channel: str, count: int = None) -> List[tuple]:
        """
        获取通道历史数据

        Args:
            channel: 通道名称
            count: 获取最近N个点，None表示全部

        Returns:
            [(timestamp, value), ...] 列表
        """
        if channel not in self.history:
            return []

        history_list = list(self.history[channel])

        if count is not None:
            return history_list[-count:]
        return history_list

    def get_channels(self) -> List[str]:
        """
        获取所有通道名称列表

        Returns:
            通道名称列表
        """
        return list(self.current_values.keys())

    def get_active_channels(self) -> List[str]:
        """
        获取有数据的通道列表（历史记录不为空的通道）

        Returns:
            有数据的通道名称列表
        """
        return [channel for channel, hist in self.history.items() if len(hist) > 0]

    def clear_history(self, channel: str = None):
        """
        清除历史数据

        Args:
            channel: 通道名称，None表示清除所有通道
        """
        if channel:
            if channel in self.history:
                self.history[channel].clear()
        else:
            for ch in self.history:
                self.history[ch].clear()

    def subscribe(self, subscriber_id: str, channels: List[str]):
        """
        订阅通道数据

        Args:
            subscriber_id: 订阅者ID (通常是 Widget ID)
            channels: 要订阅的通道列表
        """
        for channel in channels:
            if channel not in self.subscribers:
                # 动态添加新通道
                self.current_values[channel] = 0.0
                self.history[channel] = deque(maxlen=self.history_size)
                self.subscribers[channel] = set()

            self.subscribers[channel].add(subscriber_id)

    def unsubscribe(self, subscriber_id: str, channels: List[str] = None):
        """
        取消订阅通道

        Args:
            subscriber_id: 订阅者ID
            channels: 要取消订阅的通道列表，None表示取消所有订阅
        """
        if channels is None:
            # 取消所有订阅
            for channel in self.subscribers:
                self.subscribers[channel].discard(subscriber_id)
        else:
            for channel in channels:
                if channel in self.subscribers:
                    self.subscribers[channel].discard(subscriber_id)

    def get_subscribers(self, channel: str) -> set:
        """
        获取通道的订阅者列表

        Args:
            channel: 通道名称

        Returns:
            订阅者ID集合
        """
        return self.subscribers.get(channel, set()).copy()

    def get_subscriber_count(self, channel: str) -> int:
        """
        获取通道的订阅者数量

        Args:
            channel: 通道名称

        Returns:
            订阅者数量
        """
        return len(self.subscribers.get(channel, set()))

    def reset(self):
        """重置所有通道为 0"""
        for channel in self.current_values:
            self.current_values[channel] = 0.0
        self.clear_history()
