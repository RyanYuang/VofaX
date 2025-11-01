"""
BaseWidget - 所有 Widget 的基类
定义统一接口
"""

from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject
from typing import Dict, List, Any
from abc import ABC, abstractmethod, ABCMeta


class QABCMeta(type(QWidget), ABCMeta):
    """合并 QWidget 和 ABC 的元类"""
    pass


class BaseWidget(QWidget, ABC, metaclass=QABCMeta):
    """Widget 基类"""

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__()
        self.widget_data = widget_data
        self.theme = theme
        self.channel_manager = channel_manager

        # 订阅通道更新
        if channel_manager:
            self._subscribe_channels()

    def _subscribe_channels(self):
        """订阅绑定的通道数据"""
        if self.channel_manager:
            self.channel_manager.batch_updated.connect(self._on_data_update)

    @abstractmethod
    def _on_data_update(self, data: Dict[str, float]):
        """
        数据更新回调

        Args:
            data: {channel: value} 字典
        """
        pass

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
