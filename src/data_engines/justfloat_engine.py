"""
JustFloatEngine - JustFloat 协议解析引擎
格式: 连续的浮点数二进制流（小端序）
"""

from .base_engine import BaseDataEngine, ParseResult
from typing import Dict
import struct
import logging

logger = logging.getLogger(__name__)


class JustFloatEngine(BaseDataEngine):
    """
    JustFloat 协议解析引擎

    协议格式:
        - 固定数量的浮点数（4字节，小端序）
        - 无分隔符，无结束符
        - 按字节流连续排列: [float1][float2][float3]...
        - packet_size = channel_count * 4 bytes

    示例:
        channel_count = 3
        输入: b'\\x00\\x00\\x9c\\x3f\\x00\\x00\\x90\\x40\\x00\\x00\\xfc\\x40'
              (1.234, 4.5, 7.875 in little-endian)
        输出: {'I0': 1.234, 'I1': 4.5, 'I2': 7.875}
    """

    FLOAT_SIZE = 4  # 单精度浮点数大小

    def __init__(self, channel_count: int = 15, **kwargs):
        """
        初始化 JustFloat 引擎

        Args:
            channel_count: 通道数量
            **kwargs: 额外配置
                - byte_order: 字节序（'little' 或 'big'，默认 'little'）
        """
        super().__init__(channel_count, **kwargs)
        self.byte_order = kwargs.get('byte_order', 'little')
        self.packet_size = channel_count * self.FLOAT_SIZE

        # 构造struct格式字符串
        endian_char = '<' if self.byte_order == 'little' else '>'
        self.format_string = f'{endian_char}{channel_count}f'

        logger.info(f"JustFloat engine initialized: {channel_count} channels, "
                   f"packet size {self.packet_size} bytes, {self.byte_order} endian")

    def parse(self, buffer: bytearray) -> ParseResult:
        """
        解析 JustFloat 协议数据

        Args:
            buffer: 待解析的字节数组

        Returns:
            ParseResult: 解析结果
        """
        if len(buffer) < self.packet_size:
            # 数据不足，等待更多数据
            logger.debug(f"Insufficient data: {len(buffer)} < {self.packet_size} bytes")
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=0,
                error_message=f"Insufficient data ({len(buffer)}/{self.packet_size} bytes)"
            )

        # 提取数据包
        packet = bytes(buffer[:self.packet_size])

        try:
            # 解包浮点数
            values = struct.unpack(self.format_string, packet)

            # 构造数据字典
            data_dict = {}
            for i, value in enumerate(values):
                channel_name = f'I{i}'
                data_dict[channel_name] = float(value)

            logger.info(f"[JustFloat] Parsed {len(data_dict)} channels: {data_dict}")

            return ParseResult(
                success=True,
                data=data_dict,
                consumed_bytes=self.packet_size,
                error_message=None
            )

        except struct.error as e:
            logger.error(f"Failed to unpack JustFloat packet: {e}")
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=self.packet_size,  # 丢弃错误数据包
                error_message=f"Unpack error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error parsing JustFloat packet: {e}")
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=self.packet_size,
                error_message=f"Parse error: {str(e)}"
            )

    def get_name(self) -> str:
        """获取引擎名称"""
        return "justfloat"

    def get_description(self) -> str:
        """获取引擎描述"""
        return "VOFA+ JustFloat Protocol (binary float stream)"

    def get_config_schema(self) -> Dict:
        """获取配置schema"""
        schema = super().get_config_schema()
        schema.update({
            'byte_order': {
                'type': 'str',
                'default': 'little',
                'options': ['little', 'big'],
                'description': 'Byte order (endianness)'
            }
        })
        return schema
