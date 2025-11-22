"""
ASCIIEngine - ASCII/RAW 文本协议解析引擎
用于显示原始文本数据，不解析为通道
"""

from .base_engine import BaseDataEngine, ParseResult
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ASCIIEngine(BaseDataEngine):
    """
    ASCII/RAW 文本协议解析引擎

    协议格式:
        - 不对数据进行结构化解析
        - 直接将原始字节流解码为文本
        - 输出到特殊通道 'RAW'
        - 适用于终端显示、日志查看等场景

    示例:
        输入: b'Hello World\nDebug: value=123\n'
        输出: {'RAW': 'Hello World\nDebug: value=123\n'}
    """

    def __init__(self, channel_count: int = 15, **kwargs):
        """
        初始化 ASCII 引擎

        Args:
            channel_count: 通道数量（ASCII引擎不使用此参数）
            **kwargs: 额外配置
                - encoding: 字符编码（默认 'utf-8'）
                - batch_size: 每次处理的最大字节数（默认 1024）
                - decode_errors: 解码错误处理方式（默认 'replace'）
        """
        super().__init__(channel_count, **kwargs)
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.batch_size = kwargs.get('batch_size', 1024)
        self.decode_errors = kwargs.get('decode_errors', 'replace')

        logger.info(f"ASCII engine initialized: encoding={self.encoding}, "
                   f"batch_size={self.batch_size}")

    def parse(self, buffer: bytearray) -> ParseResult:
        """
        解析 ASCII 文本数据

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

        # 限制每次处理的数据量
        process_size = min(len(buffer), self.batch_size)
        data_to_process = bytes(buffer[:process_size])

        try:
            # 解码为文本
            text = data_to_process.decode(self.encoding, errors=self.decode_errors)

            if text:
                logger.info(f"[ASCII] Decoded {len(text)} characters ({process_size} bytes)")

                return ParseResult(
                    success=True,
                    data={'RAW': text},
                    consumed_bytes=process_size,
                    error_message=None
                )
            else:
                # 空文本，但消耗了字节
                return ParseResult(
                    success=False,
                    data={},
                    consumed_bytes=process_size,
                    error_message="Decoded to empty string"
                )

        except Exception as e:
            logger.error(f"Failed to decode ASCII data: {e}")
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=process_size,  # 丢弃错误数据
                error_message=f"Decode error: {str(e)}"
            )

    def get_name(self) -> str:
        """获取引擎名称"""
        return "ascii"

    def get_description(self) -> str:
        """获取引擎描述"""
        return "ASCII/RAW text protocol (no parsing, display as-is)"

    def get_channel_names(self) -> list:
        """ASCII引擎只有一个特殊通道"""
        return ['RAW']

    def get_config_schema(self) -> Dict:
        """获取配置schema"""
        return {
            'encoding': {
                'type': 'str',
                'default': 'utf-8',
                'options': ['utf-8', 'ascii', 'latin-1', 'gbk'],
                'description': 'Character encoding'
            },
            'batch_size': {
                'type': 'int',
                'default': 1024,
                'min': 64,
                'max': 8192,
                'description': 'Maximum bytes to process per parse() call'
            },
            'decode_errors': {
                'type': 'str',
                'default': 'replace',
                'options': ['replace', 'ignore', 'strict'],
                'description': 'How to handle decode errors'
            }
        }
