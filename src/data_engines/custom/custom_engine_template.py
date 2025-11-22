"""
自定义数据引擎示例模板

用户可以复制此文件并修改，创建自己的协议解析引擎

使用方法:
1. 复制此文件到 src/data_engines/custom/ 目录
2. 重命名文件 (例如: my_protocol_engine.py)
3. 修改类名和实现 parse() 方法
4. 重启应用，引擎会自动加载
"""

import sys
from pathlib import Path

# 添加父目录到路径（用于导入基类）
sys.path.insert(0, str(Path(__file__).parent.parent))

from base_engine import BaseDataEngine, ParseResult
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class CustomProtocolEngine(BaseDataEngine):
    """
    自定义协议引擎模板

    请根据您的协议格式修改以下内容:
    1. 类名
    2. get_name() 返回的引擎名称
    3. get_description() 返回的描述
    4. parse() 方法的实现逻辑
    """

    def __init__(self, channel_count: int = 15, **kwargs):
        """
        初始化自定义引擎

        Args:
            channel_count: 通道数量
            **kwargs: 自定义配置参数
        """
        super().__init__(channel_count, **kwargs)

        # 添加您的自定义配置
        # 例如:
        # self.delimiter = kwargs.get('delimiter', ',')
        # self.encoding = kwargs.get('encoding', 'utf-8')

    def parse(self, buffer: bytearray) -> ParseResult:
        """
        解析协议数据

        Args:
            buffer: 待解析的字节数组

        Returns:
            ParseResult 包含:
            - success: 是否成功解析
            - data: 解析出的数据字典 {channel: value}
            - consumed_bytes: 消耗的字节数
            - error_message: 错误信息（可选）

        示例实现（请根据实际协议修改）:
        """

        # 示例: 假设协议格式为 "CH0:1.23;CH1:4.56;CH2:7.89\\n"

        if len(buffer) == 0:
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=0,
                error_message="Empty buffer"
            )

        # 查找数据包结束符 (示例: \\n)
        end_index = buffer.find(b'\\n')

        if end_index == -1:
            # 没有完整数据包，等待更多数据
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=0,
                error_message="Incomplete packet"
            )

        # 提取数据包
        packet = bytes(buffer[:end_index])
        consumed = end_index + 1

        try:
            # 解码为字符串
            packet_str = packet.decode('utf-8')

            # 解析数据 (示例: "CH0:1.23;CH1:4.56")
            data_dict = {}
            pairs = packet_str.split(';')

            for pair in pairs:
                if ':' in pair:
                    channel, value_str = pair.split(':', 1)
                    channel = channel.strip()
                    value = float(value_str.strip())
                    data_dict[channel] = value

            logger.info(f"[CustomProtocol] Parsed {len(data_dict)} channels: {data_dict}")

            return ParseResult(
                success=True,
                data=data_dict,
                consumed_bytes=consumed,
                error_message=None
            )

        except Exception as e:
            logger.error(f"Failed to parse custom protocol: {e}")
            return ParseResult(
                success=False,
                data={},
                consumed_bytes=consumed,  # 丢弃错误数据包
                error_message=f"Parse error: {str(e)}"
            )

    def get_name(self) -> str:
        """返回引擎名称（唯一标识）"""
        return "custom_protocol"  # 修改为您的协议名称

    def get_description(self) -> str:
        """返回引擎描述"""
        return "Custom Protocol Engine Example"  # 修改为您的描述

    def get_config_schema(self) -> Dict:
        """
        定义配置参数（可选）

        这些配置会显示在UI中供用户调整
        """
        schema = super().get_config_schema()
        schema.update({
            # 添加自定义配置项
            # 例如:
            # 'delimiter': {
            #     'type': 'str',
            #     'default': ',',
            #     'description': 'Field delimiter character'
            # }
        })
        return schema


# =====================================================================
# 高级示例: Modbus RTU 协议引擎
# =====================================================================

class ModbusRTUEngine(BaseDataEngine):
    """
    Modbus RTU 协议解析引擎示例

    协议格式:
    [Address][Function][Data...][CRC_Low][CRC_High]
    """

    def __init__(self, channel_count: int = 15, **kwargs):
        super().__init__(channel_count, **kwargs)
        self.slave_address = kwargs.get('slave_address', 1)

    def parse(self, buffer: bytearray) -> ParseResult:
        """解析 Modbus RTU 响应"""

        # Modbus 最小帧长度: 地址(1) + 功能码(1) + 数据(N) + CRC(2)
        MIN_FRAME_SIZE = 5

        if len(buffer) < MIN_FRAME_SIZE:
            return ParseResult(False, {}, 0, "Insufficient data")

        # 提取地址和功能码
        address = buffer[0]
        function_code = buffer[1]

        # 根据功能码确定帧长度
        if function_code == 0x03 or function_code == 0x04:  # Read Holding/Input Registers
            if len(buffer) < 3:
                return ParseResult(False, {}, 0, "Incomplete frame")

            byte_count = buffer[2]
            frame_size = 3 + byte_count + 2  # 地址 + 功能码 + 字节数 + 数据 + CRC

            if len(buffer) < frame_size:
                return ParseResult(False, {}, 0, f"Need {frame_size} bytes, got {len(buffer)}")

            # 提取数据
            data_bytes = bytes(buffer[3:3+byte_count])

            # 验证 CRC (简化示例，实际需要实现CRC-16/Modbus)
            # crc_received = struct.unpack('<H', buffer[3+byte_count:3+byte_count+2])[0]
            # if not self._verify_crc(buffer[:3+byte_count], crc_received):
            #     return ParseResult(False, {}, frame_size, "CRC error")

            # 解析寄存器值 (16位大端序整数)
            data_dict = {}
            for i in range(0, byte_count, 2):
                register_value = int.from_bytes(data_bytes[i:i+2], byteorder='big')
                channel_name = f'I{i//2}'
                data_dict[channel_name] = float(register_value)

            logger.info(f"[ModbusRTU] Parsed {len(data_dict)} registers")

            return ParseResult(True, data_dict, frame_size, None)

        else:
            # 未支持的功能码
            return ParseResult(False, {}, 1, f"Unsupported function code: 0x{function_code:02X}")

    def get_name(self) -> str:
        return "modbus_rtu"

    def get_description(self) -> str:
        return "Modbus RTU Protocol (Read Holding/Input Registers)"


# =====================================================================
# 使用说明
# =====================================================================
"""
1. 创建自定义引擎:
   - 复制此文件到 src/data_engines/custom/
   - 重命名为 my_engine.py
   - 修改类名和实现

2. 引擎会在启动时自动加载

3. 在代码中使用:
   ```python
   from serial.serial_thread_new import SerialThread

   thread = SerialThread(
       port='COM3',
       baudrate=115200,
       engine_name='custom_protocol',  # 使用自定义引擎
       engine_config={'delimiter': ';'}  # 传递配置
   )
   thread.start()
   ```

4. 运行时切换引擎:
   ```python
   thread.set_engine('modbus_rtu', {'slave_address': 1})
   ```
"""
