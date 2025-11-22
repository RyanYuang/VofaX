"""
BaseDataEngine - 数据引擎基类
定义统一的协议解析接口
"""

from abc import ABC, abstractmethod
from typing import Dict, Union, Optional, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ParseResult:
    """解析结果数据类"""
    success: bool                           # 是否成功解析
    data: Dict[str, Union[float, str]]     # 解析出的数据 {channel: value}
    consumed_bytes: int                     # 消耗的字节数
    error_message: Optional[str] = None     # 错误信息


class BaseDataEngine(ABC):
    """
    数据引擎抽象基类

    所有协议解析引擎都应该继承此类并实现抽象方法

    设计原则:
    - 单一职责: 只负责协议解析，不处理串口通信
    - 无状态: 缓冲区由外部管理，引擎只负责解析
    - 可扩展: 用户可以轻松添加自定义协议
    """

    def __init__(self, channel_count: int = 15, **kwargs):
        """
        初始化数据引擎

        Args:
            channel_count: 通道数量 (默认15个: I0-I14)
            **kwargs: 引擎特定的配置参数
        """
        self.channel_count = channel_count
        self.config = kwargs
        logger.info(f"Initialized {self.__class__.__name__} with {channel_count} channels")

    @abstractmethod
    def parse(self, buffer: bytearray) -> ParseResult:
        """
        解析缓冲区数据

        Args:
            buffer: 待解析的字节数组

        Returns:
            ParseResult: 解析结果
            - success: 是否成功解析出完整数据包
            - data: 解析出的数据字典 {channel: value}
            - consumed_bytes: 从buffer中消耗的字节数（用于清理buffer）
            - error_message: 错误信息（如果失败）

        注意:
            - 如果buffer中没有完整数据包，返回success=False, consumed_bytes=0
            - 如果解析失败但需要丢弃错误数据，设置consumed_bytes为要丢弃的字节数
            - 引擎不应该修改buffer，由调用者根据consumed_bytes清理
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        获取引擎名称

        Returns:
            引擎名称（唯一标识）
        """
        pass

    @abstractmethod
    def get_description(self) -> str:
        """
        获取引擎描述

        Returns:
            引擎的详细描述
        """
        pass

    def get_channel_names(self) -> List[str]:
        """
        获取通道名称列表

        Returns:
            通道名称列表，默认为 ['I0', 'I1', ..., 'I14']
        """
        return [f'I{i}' for i in range(self.channel_count)]

    def validate_config(self) -> bool:
        """
        验证引擎配置是否有效

        Returns:
            配置是否有效
        """
        return self.channel_count > 0

    def reset(self):
        """
        重置引擎状态（如果引擎有内部状态）

        默认实现为空，有状态的引擎应该重写此方法
        """
        pass

    def get_config_schema(self) -> Dict:
        """
        获取引擎的配置schema（用于UI生成）

        Returns:
            配置schema字典

        示例:
            {
                'channel_count': {'type': 'int', 'default': 15, 'min': 1, 'max': 32},
                'encoding': {'type': 'str', 'default': 'utf-8', 'options': ['utf-8', 'ascii']}
            }
        """
        return {
            'channel_count': {
                'type': 'int',
                'default': 15,
                'min': 1,
                'max': 32,
                'description': 'Number of data channels'
            }
        }
