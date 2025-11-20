"""
SerialThread - 串口通信线程
负责异步读写串口数据，解析协议
"""

from PyQt6.QtCore import QThread, pyqtSignal
import serial
import struct
import time
from typing import Optional, Dict, Union
import logging

logger = logging.getLogger(__name__)


class SerialThread(QThread):
    """
    串口通信线程 (QThread)
    支持多种协议格式：FireWater, JustFloat, ASCII
    """

    # 信号定义
    data_received = pyqtSignal(dict)  # {channel: value} 批量数据，value 可以是 float 或 str
    error_occurred = pyqtSignal(str)  # 错误信息
    connection_lost = pyqtSignal()  # 连接丢失
    rx_tx_stats = pyqtSignal(int, int)  # RX bytes, TX bytes

    # 协议常量
    PROTOCOL_FIREWATER = 'firewater'  # VOFA+ FireWater 格式
    PROTOCOL_JUSTFLOAT = 'justfloat'  # VOFA+ JustFloat 格式
    RAW_DATA = 'ascii'  # ASCII 格式 (e.g., "CH0:1.23,CH1:4.56\n")

    # FireWater 尾巴: 0x00 0x00 0x80 0x7F (float: inf)
    FIREWATER_TAIL = b'\n'

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        databits: int = 8,
        stopbits: int = 1,
        parity: str = 'N',
        protocol: str = RAW_DATA,
        channel_count: int = 15
    ):
        """
        初始化串口线程

        Args:
            port: 串口名称 (e.g., 'COM3', '/dev/ttyUSB0')
            baudrate: 波特率
            databits: 数据位
            stopbits: 停止位
            parity: 校验位 ('N', 'E', 'O', 'M', 'S')
            protocol: 协议类型
            channel_count: 通道数量 (FireWater/JustFloat)
        """
        super().__init__()

        self.port = port
        self.baudrate = baudrate
        self.databits = databits
        self.stopbits = stopbits
        self.parity = parity
        self.protocol = protocol
        self.channel_count = channel_count

        self.serial_port: Optional[serial.Serial] = None
        self.running = False

        # 统计
        self.rx_bytes = 0
        self.tx_bytes = 0

        # 缓冲区 (用于处理不完整数据包)
        self.buffer = bytearray()

    def run(self):
        """线程主循环 - 读取串口数据"""
        try:
            # 打开串口
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.databits,
                stopbits=self.stopbits,
                parity=self.parity,
                timeout=0.1,  # 100ms 超时
                write_timeout=1.0
            )

            if not self.serial_port.is_open:
                raise serial.SerialException(f"Failed to open {self.port}")

            logger.info(f"Serial port {self.port} opened successfully")
            self.running = True

            # 主循环
            while self.running:
                try:
                    # 读取数据
                    if self.serial_port.in_waiting > 0:
                            data = self.serial_port.read(self.serial_port.in_waiting)
                            if data:
                                self.rx_bytes += len(data)
                                # Debug: 打印接收到的原始数据（使用 INFO 级别确保能看到）
                                logger.info(f"[RX] Received {len(data)} bytes: {data.hex()}")
                                logger.info(f"[RX] ASCII preview: {data[:50]}")  # 前50字节的ASCII预览
                                self._process_data(data)

                                # 每秒更新一次统计
                                self.rx_tx_stats.emit(self.rx_bytes, self.tx_bytes)
                    # 短暂休眠，避免CPU占用过高
                    time.sleep(0.001)  # 1ms

                except serial.SerialException as e:
                    logger.error(f"Serial read error: {e}")
                    self.error_occurred.emit(f"Read error: {str(e)}")
                    self.connection_lost.emit()
                    break
                except Exception as e:
                    logger.error(f"Unexpected error in main loop: {e}")
                    self.error_occurred.emit(f"Serial Device disconnected!")
                    break

        except serial.SerialException as e:
            logger.error(f"Failed to open serial port: {e}")
            self.error_occurred.emit(f"Connection failed: {str(e)}")

        finally:
            self._close_port()

    def _process_data(self, data: bytes):
        """
        处理接收到的数据

        Args:
            data: 接收到的原始字节
        """
        # 添加到缓冲区
        self.buffer.extend(data)

        # 根据协议解析数据
        if self.protocol == self.PROTOCOL_FIREWATER:
            self._parse_firewater()
            logger.info("[FireWater]")
        elif self.protocol == self.PROTOCOL_JUSTFLOAT:
            self._parse_justfloat()
            logger.info("[justfloat]")
        elif self.protocol == self.RAW_DATA:
            self._parse_ascii()
            logger.info("[RAW]")

    def _parse_firewater(self):
        """
        解析 VOFA+ FireWater 协议
        格式: [Data_1],[Data_2],[Data_3]\n
        """
        while len(self.buffer) >= 4:
            # 查找尾巴
            tail_index = self.buffer.find(self.FIREWATER_TAIL)

            if tail_index == -1:
                # 未找到尾巴，等待更多数据
                logger.info(f"[FireWater] No tail found in buffer (size: {len(self.buffer)})")
                logger.info(f"[FireWater] Buffer preview (hex): {self.buffer[:64].hex()}")
                # 但防止缓冲区过大
                if len(self.buffer) > 1024:
                    logger.warning("Buffer overflow, clearing")
                    self.buffer.clear()
                break

            # 提取完整包 (不包含尾巴)
            packet = bytes(self.buffer[:tail_index])
            logger.debug(f"[FireWater] Found packet: {len(packet)} bytes at tail_index={tail_index}")

            # 移除已处理的数据
            self.buffer = self.buffer[tail_index + 4:]

            # 解析浮点数
            # float_count = len(packet) // 4
            # if float_count == 0 or float_count > self.channel_count:
            #     logger.warning(f"Invalid float count: {float_count}")
            #     continue

            try:
                # 解包
                unpack = self.buffer.split(',')
                print("=====",unpack,"=====")
                        

                # 构造数据字典 {I0: value0, I1: value1, ...}
                data_dict = {}
                for i, value in enumerate(values):
                    if i < self.channel_count:
                        data_dict[f'I{i}'] = float(value)

                # Debug: 打印解析后的数据（使用 INFO 确保能看到）
                logger.info(f"[FireWater] ✓ Parsed data: {data_dict}")

                # 发射信号
                self.data_received.emit(data_dict)
                logger.info(f"[FireWater] ✓ Emitted data_received signal")

            except struct.error as e:
                logger.error(f"Failed to unpack FireWater packet: {e}")

    def _parse_justfloat(self):
        """
        解析 VOFA+ JustFloat 协议
        格式: [float0][float1]...[floatN] (固定 N 个浮点数)
        """
        packet_size = self.channel_count * 4

        while len(self.buffer) >= packet_size:
            # 提取数据包
            packet = bytes(self.buffer[:packet_size])
            self.buffer = self.buffer[packet_size:]

            try:
                # 解包小端序浮点数
                values = struct.unpack(f'<{self.channel_count}f', packet)

                # 构造数据字典
                data_dict = {}
                for i, value in enumerate(values):
                    data_dict[f'I{i}'] = float(value)

                # 发射信号
                self.data_received.emit(data_dict)

            except struct.error as e:
                logger.error(f"Failed to unpack JustFloat packet: {e}")

    def _parse_ascii(self):
        """
        RAW_DATA 协议
        不对内容进行解析，直接把输入按文本原样显示
        """
        if not self.buffer:
            return

        try:
            # 直接把缓冲区内容解码为字符串；使用 errors='replace' 避免因为半个字符导致异常
            raw_text = self.buffer.decode('utf-8', errors='replace')
        except Exception as e:
            logger.warning(f"[RAW_DATA] Failed to decode buffer: {e}")
            self.buffer.clear()
            return

        if raw_text:
            logger.info(f"[RAW_DATA] Forwarding raw text ({len(raw_text)} chars)")
            self.data_received.emit({'RAW': raw_text})

        self.buffer.clear()

    def write(self, data: bytes) -> bool:
        """
        写入数据到串口

        Args:
            data: 要写入的字节

        Returns:
            是否写入成功
        """
        if not self.serial_port or not self.serial_port.is_open:
            return False

        try:
            written = self.serial_port.write(data)
            self.tx_bytes += written
            return written == len(data)
        except serial.SerialException as e:
            logger.error(f"Serial write error: {e}")
            self.error_occurred.emit(f"Write error: {str(e)}")
            return False

    def stop(self):
        """停止线程"""
        self.running = False
        self.wait(2000)  # 等待最多 2 秒

    def _close_port(self):
        """关闭串口"""
        if self.serial_port and self.serial_port.is_open:
            try:
                self.serial_port.close()
                logger.info(f"Serial port {self.port} closed")
            except Exception as e:
                logger.error(f"Failed to close serial port: {e}")

        self.serial_port = None
        self.running = False

    def get_stats(self) -> Dict[str, int]:
        """
        获取统计信息

        Returns:
            {'rx_bytes': int, 'tx_bytes': int}
        """
        return {
            'rx_bytes': self.rx_bytes,
            'tx_bytes': self.tx_bytes
        }

    def reset_stats(self):
        """重置统计信息"""
        self.rx_bytes = 0
        self.tx_bytes = 0
