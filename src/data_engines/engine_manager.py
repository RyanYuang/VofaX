"""
DataEngineManager - 数据引擎管理器
负责注册、选择和管理所有数据引擎
"""

from .base_engine import BaseDataEngine
from .firewater_engine import FireWaterEngine
from .justfloat_engine import JustFloatEngine
from .ascii_engine import ASCIIEngine
from typing import Dict, List, Optional, Type
import logging
import importlib
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class DataEngineManager:
    """
    数据引擎管理器（单例模式）

    功能:
    1. 管理所有内置引擎
    2. 支持动态加载用户自定义引擎
    3. 提供引擎创建和切换接口
    """

    _instance = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """初始化管理器"""
        if self._initialized:
            return

        # 注册的引擎类 {engine_name: engine_class}
        self._engine_classes: Dict[str, Type[BaseDataEngine]] = {}

        # 注册内置引擎
        self._register_builtin_engines()

        # 加载用户自定义引擎
        self._load_custom_engines()

        self._initialized = True
        logger.info(f"DataEngineManager initialized with {len(self._engine_classes)} engines")

    def _register_builtin_engines(self):
        """注册内置引擎"""
        builtin_engines = [
            FireWaterEngine,
            JustFloatEngine,
            ASCIIEngine
        ]

        for engine_class in builtin_engines:
            # 创建临时实例获取名称
            temp_instance = engine_class()
            engine_name = temp_instance.get_name()
            self._engine_classes[engine_name] = engine_class
            logger.info(f"Registered builtin engine: {engine_name} ({engine_class.__name__})")

    def _load_custom_engines(self):
        """
        加载用户自定义引擎

        从以下位置搜索:
        1. src/data_engines/custom/ 目录
        2. ~/.uniscope/engines/ 目录（用户配置目录）
        """
        search_paths = [
            Path(__file__).parent / 'custom',  # 项目内自定义引擎
            Path.home() / '.uniscope' / 'engines'  # 用户目录
        ]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            logger.info(f"Searching for custom engines in: {search_path}")

            # 查找所有 .py 文件（排除 __init__.py）
            for py_file in search_path.glob('*.py'):
                if py_file.name.startswith('__'):
                    continue

                try:
                    self._load_engine_from_file(py_file)
                except Exception as e:
                    logger.error(f"Failed to load custom engine from {py_file}: {e}")

    def _load_engine_from_file(self, file_path: Path):
        """
        从文件加载引擎类

        Args:
            file_path: 引擎文件路径
        """
        module_name = file_path.stem

        # 动态导入模块
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec is None or spec.loader is None:
            logger.warning(f"Cannot load module spec from {file_path}")
            return

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # 查找继承自 BaseDataEngine 的类
        for attr_name in dir(module):
            attr = getattr(module, attr_name)

            # 检查是否是类且继承自 BaseDataEngine
            if (isinstance(attr, type) and
                issubclass(attr, BaseDataEngine) and
                attr is not BaseDataEngine):

                # 创建实例获取名称
                try:
                    instance = attr()
                    engine_name = instance.get_name()

                    # 检查是否已存在
                    if engine_name in self._engine_classes:
                        logger.warning(f"Engine '{engine_name}' already registered, skipping")
                        continue

                    self._engine_classes[engine_name] = attr
                    logger.info(f"Loaded custom engine: {engine_name} ({attr.__name__}) from {file_path}")

                except Exception as e:
                    logger.error(f"Failed to instantiate custom engine {attr.__name__}: {e}")

    def register_engine(self, engine_class: Type[BaseDataEngine]) -> bool:
        """
        手动注册引擎

        Args:
            engine_class: 引擎类

        Returns:
            是否注册成功
        """
        try:
            instance = engine_class()
            engine_name = instance.get_name()

            if engine_name in self._engine_classes:
                logger.warning(f"Engine '{engine_name}' already registered")
                return False

            self._engine_classes[engine_name] = engine_class
            logger.info(f"Manually registered engine: {engine_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to register engine: {e}")
            return False

    def create_engine(self, engine_name: str, **kwargs) -> Optional[BaseDataEngine]:
        """
        创建引擎实例

        Args:
            engine_name: 引擎名称
            **kwargs: 引擎配置参数

        Returns:
            引擎实例，如果不存在返回 None
        """
        engine_class = self._engine_classes.get(engine_name)

        if engine_class is None:
            logger.error(f"Engine '{engine_name}' not found")
            return None

        try:
            instance = engine_class(**kwargs)
            logger.info(f"Created engine instance: {engine_name} with config {kwargs}")
            return instance

        except Exception as e:
            logger.error(f"Failed to create engine '{engine_name}': {e}")
            return None

    def get_available_engines(self) -> List[Dict]:
        """
        获取所有可用引擎的信息

        Returns:
            引擎信息列表，每个元素包含 name, description, class_name
        """
        engines_info = []

        for engine_name, engine_class in self._engine_classes.items():
            try:
                instance = engine_class()
                engines_info.append({
                    'name': engine_name,
                    'description': instance.get_description(),
                    'class_name': engine_class.__name__,
                    'config_schema': instance.get_config_schema()
                })
            except Exception as e:
                logger.error(f"Failed to get info for engine '{engine_name}': {e}")

        return engines_info

    def get_engine_names(self) -> List[str]:
        """
        获取所有引擎名称

        Returns:
            引擎名称列表
        """
        return list(self._engine_classes.keys())

    def has_engine(self, engine_name: str) -> bool:
        """
        检查引擎是否存在

        Args:
            engine_name: 引擎名称

        Returns:
            是否存在
        """
        return engine_name in self._engine_classes

    def get_engine_class(self, engine_name: str) -> Optional[Type[BaseDataEngine]]:
        """
        获取引擎类

        Args:
            engine_name: 引擎名称

        Returns:
            引擎类，如果不存在返回 None
        """
        return self._engine_classes.get(engine_name)

    def unregister_engine(self, engine_name: str) -> bool:
        """
        注销引擎

        Args:
            engine_name: 引擎名称

        Returns:
            是否注销成功
        """
        if engine_name not in self._engine_classes:
            logger.warning(f"Engine '{engine_name}' not registered")
            return False

        del self._engine_classes[engine_name]
        logger.info(f"Unregistered engine: {engine_name}")
        return True


# 全局管理器实例
_global_manager = None


def get_engine_manager() -> DataEngineManager:
    """
    获取全局引擎管理器实例

    Returns:
        DataEngineManager 单例
    """
    global _global_manager
    if _global_manager is None:
        _global_manager = DataEngineManager()
    return _global_manager
