"""
FireWaterEngine - FireWater 协议解析引擎
格式: [Data_1],[Data_2],[Data_3],...,[Data_N]\n
"""

from .base_engine import BaseDataEngine, ParseResult
from typing import Dict, Union
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class FireWaterEngine(BaseDataEngine):
    """
    FireWater 协议解析引擎

    协议格式:
        - 数据以逗号分隔: value1,value2,value3,...
        - 以换行符 \n (0x0A) 结尾
        - 每个值转换为 float 类型
        - 按顺序映射到通道: I0, I1, I2, ...

    示例:
        输入: b'1.23,4.56,7.89\n'
        输出: {'I0': 1.23, 'I1': 4.56, 'I2': 7.89}
    """

    TAIL_BYTE = b'\n'  # 换行符作为包尾
    MAX_BUFFER_SIZE = 4096  # 最大缓冲区大小（防止溢出）

    def __init__(self, channel_count: int = 15, **kwargs):
        """
        初始化 FireWater 引擎

        Args:
            channel_count: 通道数量
            **kwargs: 额外配置
                - encoding: 字符编码（默认 'utf-8'）
                - max_packet_size: 最大数据包大小（默认 4096）
        """
        super().__init__(channel_count, **kwargs)
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.max_packet_size = kwargs.get('max_packet_size', self.MAX_BUFFER_SIZE)

    def parse(self, buffer: bytearray) -> ParseResult:
        """
        解析 FireWater 协议数据

        Args:
            buffer: 待解析的字节数组

        Returns:
            ParseResult: 解析结果
        """
        if len(buffer) == 0:
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=0,
                error_message="Empty buffer"
            )

        # 防止缓冲区溢出
        if len(buffer) > self.max_packet_size:
            logger.warning(f"Buffer overflow ({len(buffer)} bytes), clearing")
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=len(buffer),  # 清空整个buffer
                error_message=f"Buffer overflow (>{self.max_packet_size} bytes)"
            )

        # 查找换行符
        tail_index = buffer.find(self.TAIL_BYTE)

        if tail_index == -1:
            # 没有完整数据包，等待更多数据
            logger.debug(f"No complete packet found in buffer (size: {len(buffer)})")
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=0,
                error_message="Incomplete packet"
            )

        # 提取完整数据包（不包含换行符）
        packet = bytes(buffer[:tail_index])
        consumed = tail_index + len(self.TAIL_BYTE)

        logger.debug(f"Found packet: {len(packet)} bytes, tail at index {tail_index}")

        try:
            # 解码为字符串
            packet_str = packet.decode(self.encoding)

            # 按逗号分割
            values_str = packet_str.split(',')

            # 转换为字典
            data_dict = {}
            for i, value_str in enumerate(values_str):
                if i >= self.channel_count:
                    logger.warning(f"Received more values ({len(values_str)}) than channels ({self.channel_count})")
                    break

                # 去除空格并转换为float
                value_str = value_str.strip()
                if value_str:  # 忽略空字符串
                    try:
                        value = float(value_str)
                        channel_name = f'I{i}'
                        data_dict[channel_name] = value
                    except ValueError as e:
                        logger.warning(f"Failed to parse value '{value_str}' at index {i}: {e}")
                        continue

            logger.info(f"[FireWater] Parsed {len(data_dict)} channels: {data_dict}")

            return ParseResult(
                success=True,
                data=data_dict,
                consumed_bytes=consumed,
                error_message=None
            )

        except UnicodeDecodeError as e:
            logger.error(f"Failed to decode packet: {e}")
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=consumed,  # 丢弃错误数据包
                error_message=f"Decode error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error parsing FireWater packet: {e}")
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=consumed,
                error_message=f"Parse error: {str(e)}"
            )

    def get_name(self) -> str:
        """获取引擎名称"""
        return "firewater"

    def get_description(self) -> str:
        """获取引擎描述"""
        return "VOFA+ FireWater Protocol (CSV format with newline terminator)"

    def get_config_schema(self) -> Dict:
        """获取配置schema"""
        schema = super().get_config_schema()
        schema.update({
            'encoding': {
                'type': 'str',
                'default': 'utf-8',
                'options': ['utf-8', 'ascii', 'latin-1'],
                'description': 'Character encoding'
            },
            'max_packet_size': {
                'type': 'int',
                'default': 4096,
                'min': 256,
                'max': 65536,
                'description': 'Maximum packet size in bytes'
            }
        })
        return schema
