# -*- coding: utf-8 -*-
"""
插件加载器
动态加载 plugins/ 目录下的 Widget 插件
"""

import json
import importlib.util
import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

from src.data.widget_registry import WidgetRegistry

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Widget 插件加载器
    扫描 plugins/ 目录并动态加载符合规范的插件
    """

    def __init__(self, plugin_dir: str = "plugins"):
        """
        初始化插件加载器

        Args:
            plugin_dir: 插件目录路径
        """
        self.plugin_dir = Path(plugin_dir)
        self.loaded_plugins: Dict[str, Dict] = {}  # {plugin_name: manifest}

    def load_all_plugins(self) -> int:
        """
        加载所有插件

        Returns:
            成功加载的插件数量
        """
        if not self.plugin_dir.exists():
            logger.warning(f"Plugin directory not found: {self.plugin_dir}")
            self.plugin_dir.mkdir(parents=True, exist_ok=True)
            return 0

        success_count = 0

        for plugin_path in self.plugin_dir.iterdir():
            if plugin_path.is_dir() and not plugin_path.name.startswith('_'):
                try:
                    if self.load_plugin(plugin_path):
                        success_count += 1
                except Exception as e:
                    logger.error(f"Error loading plugin from {plugin_path}: {e}", exc_info=True)

        logger.info(f"Loaded {success_count} plugin(s) from {self.plugin_dir}")
        return success_count

    def load_plugin(self, plugin_path: Path) -> bool:
        """
        加载单个插件

        Args:
            plugin_path: 插件目录路径

        Returns:
            是否加载成功
        """
        manifest_path = plugin_path / "manifest.json"

        if not manifest_path.exists():
            logger.warning(f"Manifest not found in {plugin_path}, skipping")
            return False

        # 读取 manifest
        try:
            manifest = self._load_manifest(manifest_path)
        except Exception as e:
            logger.error(f"Failed to load manifest from {manifest_path}: {e}")
            return False

        # 验证 manifest
        if not self._validate_manifest(manifest):
            logger.error(f"Invalid manifest in {plugin_path}")
            return False

        # 动态导入 Widget 类
        try:
            widget_class = self._import_widget_class(plugin_path, manifest)
        except Exception as e:
            logger.error(f"Failed to import widget class: {e}", exc_info=True)
            return False

        # 注册到 WidgetRegistry
        try:
            widget_type = manifest['widget_type']
            metadata = {
                'name': manifest.get('name', widget_type),
                'description': manifest.get('description', ''),
                'icon': manifest.get('icon', ''),
                'category': manifest.get('category', 'Plugin'),
                'author': manifest.get('author', ''),
                'version': manifest.get('version', '1.0.0'),
            }

            WidgetRegistry.register(widget_type, widget_class, metadata)

            self.loaded_plugins[manifest['name']] = manifest
            logger.info(f"Successfully loaded plugin: {manifest['name']} v{manifest['version']}")
            return True

        except Exception as e:
            logger.error(f"Failed to register widget: {e}", exc_info=True)
            return False

    def _load_manifest(self, manifest_path: Path) -> Dict:
        """
        读取 manifest.json

        Args:
            manifest_path: manifest.json 路径

        Returns:
            manifest 字典
        """
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _validate_manifest(self, manifest: Dict) -> bool:
        """
        验证 manifest 是否合法

        Args:
            manifest: manifest 字典

        Returns:
            是否合法
        """
        required_fields = ['name', 'version', 'widget_type', 'entry_point']

        for field in required_fields:
            if field not in manifest:
                logger.error(f"Manifest missing required field: {field}")
                return False

        return True

    def _import_widget_class(self, plugin_path: Path, manifest: Dict):
        """
        动态导入 Widget 类

        Args:
            plugin_path: 插件目录路径
            manifest: manifest 字典

        Returns:
            Widget 类

        Raises:
            ImportError: 如果导入失败
        """
        entry_point = manifest['entry_point']  # e.g., "widget.MyWidget"

        # 解析 entry_point
        if '.' not in entry_point:
            raise ValueError(f"Invalid entry_point format: {entry_point}")

        module_name, class_name = entry_point.rsplit('.', 1)

        # 构建模块路径
        module_file = plugin_path / f"{module_name.replace('.', '/')}.py"

        if not module_file.exists():
            raise FileNotFoundError(f"Module file not found: {module_file}")

        # 动态导入模块
        spec = importlib.util.spec_from_file_location(
            f"plugins.{plugin_path.name}.{module_name}",
            module_file
        )

        if spec is None or spec.loader is None:
            raise ImportError(f"Failed to load spec for {module_file}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        # 获取类
        if not hasattr(module, class_name):
            raise AttributeError(f"Class '{class_name}' not found in {module_file}")

        widget_class = getattr(module, class_name)

        return widget_class

    def reload_plugin(self, plugin_name: str) -> bool:
        """
        重新加载插件 (用于开发调试)

        Args:
            plugin_name: 插件名称

        Returns:
            是否重新加载成功
        """
        if plugin_name not in self.loaded_plugins:
            logger.error(f"Plugin not loaded: {plugin_name}")
            return False

        manifest = self.loaded_plugins[plugin_name]
        widget_type = manifest['widget_type']

        # 注销旧插件
        WidgetRegistry.unregister(widget_type)

        # 重新加载
        plugin_path = self.plugin_dir / plugin_name
        return self.load_plugin(plugin_path)

    def unload_plugin(self, plugin_name: str) -> bool:
        """
        卸载插件

        Args:
            plugin_name: 插件名称

        Returns:
            是否卸载成功
        """
        if plugin_name not in self.loaded_plugins:
            logger.error(f"Plugin not loaded: {plugin_name}")
            return False

        manifest = self.loaded_plugins[plugin_name]
        widget_type = manifest['widget_type']

        # 从 Registry 注销
        WidgetRegistry.unregister(widget_type)

        # 从已加载列表移除
        del self.loaded_plugins[plugin_name]

        logger.info(f"Unloaded plugin: {plugin_name}")
        return True

    def get_loaded_plugins(self) -> List[Dict]:
        """
        获取已加载的插件列表

        Returns:
            插件 manifest 列表
        """
        return list(self.loaded_plugins.values())

    def get_plugin_info(self, plugin_name: str) -> Optional[Dict]:
        """
        获取插件信息

        Args:
            plugin_name: 插件名称

        Returns:
            插件 manifest，不存在返回 None
        """
        return self.loaded_plugins.get(plugin_name)


def create_example_plugin():
    """
    创建示例插件目录结构 (用于开发引导)
    """
    example_dir = Path("plugins/example_widget")
    example_dir.mkdir(parents=True, exist_ok=True)

    # 创建 __init__.py
    (example_dir / "__init__.py").write_text("")

    # 创建 widget.py
    widget_code = '''"""
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
'''

    (example_dir / "widget.py").write_text(widget_code)

    # 创建 manifest.json
    manifest = {
        "name": "Example Widget",
        "version": "1.0.0",
        "author": "UniScope Team",
        "description": "An example widget plugin",
        "widget_type": "example_widget",
        "entry_point": "widget.ExampleWidget",
        "category": "Example",
        "icon": "⭐",
        "requires": []
    }

    (example_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding='utf-8'
    )

    logger.info(f"Created example plugin at {example_dir}")
