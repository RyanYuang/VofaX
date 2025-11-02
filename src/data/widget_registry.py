# -*- coding: utf-8 -*-
"""
Widget 注册中心
管理所有可用的 Widget 类型，使用工厂模式创建 Widget 实例
"""

from typing import Dict, Type, Optional
from src.widgets.base_widget import BaseWidget
import logging

logger = logging.getLogger(__name__)


class WidgetRegistry:
    """
    Widget 注册中心 (单例模式)
    使用工厂模式创建 Widget 实例
    """

    _instance = None
    _registry: Dict[str, Type[BaseWidget]] = {}
    _metadata: Dict[str, Dict] = {}  # Widget 元数据

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def register(cls, widget_type: str, widget_class: Type[BaseWidget], metadata: Dict = None):
        """
        注册 Widget 类

        Args:
            widget_type: Widget 类型标识符 (e.g., 'oscilloscope', 'terminal')
            widget_class: Widget 类 (必须继承 BaseWidget)
            metadata: Widget 元数据 (名称、描述、图标等)

        Raises:
            ValueError: 如果 widget_class 不是 BaseWidget 的子类
            TypeError: 如果 widget_type 已注册
        """
        if not issubclass(widget_class, BaseWidget):
            raise ValueError(
                f"Widget class {widget_class.__name__} must inherit from BaseWidget"
            )

        if widget_type in cls._registry:
            logger.warning(f"Widget type '{widget_type}' is already registered. Overwriting...")

        cls._registry[widget_type] = widget_class

        # 存储元数据
        if metadata is None:
            metadata = {}

        cls._metadata[widget_type] = {
            'name': metadata.get('name', widget_type.replace('_', ' ').title()),
            'description': metadata.get('description', ''),
            'icon': metadata.get('icon', ''),
            'category': metadata.get('category', 'General'),
            'author': metadata.get('author', ''),
            'version': metadata.get('version', '1.0.0'),
        }

        logger.info(f"Registered widget type: {widget_type} ({widget_class.__name__})")

    @classmethod
    def unregister(cls, widget_type: str):
        """
        注销 Widget 类

        Args:
            widget_type: Widget 类型标识符
        """
        if widget_type in cls._registry:
            del cls._registry[widget_type]
            if widget_type in cls._metadata:
                del cls._metadata[widget_type]
            logger.info(f"Unregistered widget type: {widget_type}")
        else:
            logger.warning(f"Widget type '{widget_type}' not found in registry")

    @classmethod
    def create_widget(
        cls,
        widget_data: Dict,
        theme: str,
        channel_manager
    ) -> Optional[BaseWidget]:
        """
        工厂方法：根据类型创建 Widget 实例

        Args:
            widget_data: Widget 配置数据 (必须包含 'type' 字段)
            theme: 主题 ('dark' 或 'light')
            channel_manager: ChannelManager 实例

        Returns:
            Widget 实例，如果类型未注册则返回 None

        Raises:
            KeyError: 如果 widget_data 缺少 'type' 字段
            Exception: 如果 Widget 实例化失败
        """
        if 'type' not in widget_data:
            raise KeyError("widget_data must contain 'type' field")

        widget_type = widget_data['type']

        if widget_type not in cls._registry:
            logger.error(f"Unknown widget type: {widget_type}")
            return None

        widget_class = cls._registry[widget_type]

        try:
            widget = widget_class(widget_data, theme, channel_manager)
            logger.debug(f"Created widget instance: {widget_type} (ID: {widget_data.get('id', 'N/A')})")
            return widget
        except Exception as e:
            logger.error(f"Failed to create widget '{widget_type}': {e}", exc_info=True)
            return None

    @classmethod
    def get_registered_types(cls) -> list:
        """
        获取所有已注册的 Widget 类型

        Returns:
            Widget 类型列表
        """
        return list(cls._registry.keys())

    @classmethod
    def get_metadata(cls, widget_type: str) -> Dict:
        """
        获取 Widget 元数据

        Args:
            widget_type: Widget 类型

        Returns:
            元数据字典，不存在返回空字典
        """
        return cls._metadata.get(widget_type, {})

    @classmethod
    def get_all_metadata(cls) -> Dict[str, Dict]:
        """
        获取所有 Widget 的元数据

        Returns:
            {widget_type: metadata} 字典
        """
        return cls._metadata.copy()

    @classmethod
    def is_registered(cls, widget_type: str) -> bool:
        """
        检查 Widget 类型是否已注册

        Args:
            widget_type: Widget 类型

        Returns:
            是否已注册
        """
        return widget_type in cls._registry

    @classmethod
    def clear(cls):
        """清空注册表 (主要用于测试)"""
        cls._registry.clear()
        cls._metadata.clear()
        logger.info("Widget registry cleared")

    @classmethod
    def get_widgets_by_category(cls, category: str) -> Dict[str, Dict]:
        """
        按分类获取 Widget

        Args:
            category: 分类名称

        Returns:
            {widget_type: metadata} 字典
        """
        return {
            wtype: meta
            for wtype, meta in cls._metadata.items()
            if meta.get('category') == category
        }


def register_builtin_widgets():
    """
    注册内置 Widget
    应在应用启动时调用
    """
    from src.widgets.oscilloscope import OscilloscopeWidget
    from src.widgets.terminal import TerminalWidget
    from src.widgets.hex_viewer import HexViewerWidget
    from src.widgets.gauge import GaugeWidget
    from src.widgets.data_table import DataTableWidget
    from src.widgets.packet_analyzer import PacketAnalyzerWidget
    from src.widgets.chart import ChartWidget

    WidgetRegistry.register('oscilloscope', OscilloscopeWidget, {
        'name': 'Oscilloscope',
        'description': 'Multi-channel waveform display',
        'category': 'Visualization',
        'icon': 'Image_Src/Icon/OsillIcon.svg'  # 使用 SVG 图标路径
    })

    WidgetRegistry.register('terminal', TerminalWidget, {
        'name': 'Terminal',
        'description': 'Serial console with hex/ASCII display',
        'category': 'Communication',
        'icon': '💻'
    })

    WidgetRegistry.register('hex-viewer', HexViewerWidget, {
        'name': 'Hex Viewer',
        'description': 'Raw data in hexadecimal format',
        'category': 'Communication',
        'icon': '🔢'
    })

    WidgetRegistry.register('gauge', GaugeWidget, {
        'name': 'Gauge',
        'description': 'Circular meter for single values',
        'category': 'Visualization',
        'icon': '🎯'
    })

    WidgetRegistry.register('data-table', DataTableWidget, {
        'name': 'Data Table',
        'description': 'Live updating table view',
        'category': 'Visualization',
        'icon': '📋'
    })

    WidgetRegistry.register('packet-analyzer', PacketAnalyzerWidget, {
        'name': 'Packet Analyzer',
        'description': 'Protocol packet decoder',
        'category': 'Analysis',
        'icon': '🔍'
    })

    WidgetRegistry.register('chart', ChartWidget, {
        'name': 'Chart',
        'description': 'Line/bar chart for data history',
        'category': 'Visualization',
        'icon': '📈'
    })

    logger.info(f"Registered {len(WidgetRegistry.get_registered_types())} built-in widgets")
