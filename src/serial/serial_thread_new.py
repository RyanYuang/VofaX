"""
SerialThread - 串口通信线程（重构版）
负责异步读写串口数据，使用可插拔的数据引擎进行协议解析
"""

from PyQt6.QtCore import QThread, pyqtSignal
import serial
import time
from typing import Optional, Dict, Union
import logging

from ..data_engines import BaseDataEngine, get_engine_manager

logger = logging.getLogger(__name__)


class SerialThread(QThread):
    """
    串口通信线程 (QThread)

    职责:
    - 异步读取串口数据
    - 使用数据引擎解析协议
    - 发射解析后的数据信号

    与旧版区别:
    - 协议解析逻辑分离到独立的数据引擎
    - 支持运行时切换引擎
    - 更容易添加自定义协议
    """

    # 信号定义
    data_received = pyqtSignal(dict)  # {channel: value} 批量数据
    error_occurred = pyqtSignal(str)  # 错误信息
    connection_lost = pyqtSignal()  # 连接丢失
    rx_tx_stats = pyqtSignal(int, int)  # RX bytes, TX bytes

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        databits: int = 8,
        stopbits: int = 1,
        parity: str = 'N',
        engine_name: str = 'firewater',
        engine_config: Optional[Dict] = None
    ):
        """
        初始化串口线程

        Args:
            port: 串口名称 (e.g., 'COM3', '/dev/ttyUSB0')
            baudrate: 波特率
            databits: 数据位
            stopbits: 停止位
            parity: 校验位 ('N', 'E', 'O', 'M', 'S')
            engine_name: 数据引擎名称
            engine_config: 引擎配置参数
        """
        super().__init__()

        # 串口参数
        self.port = port
        self.baudrate = baudrate
        self.databits = databits
        self.stopbits = stopbits
        self.parity = parity

        # 数据引擎
        self.engine_name = engine_name
        self.engine_config = engine_config or {}
        self.engine: Optional[BaseDataEngine] = None
        self._init_engine()

        # 串口对象
        self.serial_port: Optional[serial.Serial] = None
        self.running = False
        self.paused = False

        # 统计
        self.rx_bytes = 0
        self.tx_bytes = 0

        # 缓冲区
        self.buffer = bytearray()

    def _init_engine(self):
        """初始化数据引擎"""
        manager = get_engine_manager()
        self.engine = manager.create_engine(self.engine_name, **self.engine_config)

        if self.engine is None:
            logger.error(f"Failed to create engine '{self.engine_name}', falling back to 'ascii'")
            self.engine = manager.create_engine('ascii')

        logger.info(f"Initialized data engine: {self.engine.get_name()}")

    def set_engine(self, engine_name: str, engine_config: Optional[Dict] = None) -> bool:
        """
        切换数据引擎

        Args:
            engine_name: 新引擎名称
            engine_config: 新引擎配置

        Returns:
            是否切换成功
        """
        manager = get_engine_manager()
        new_engine = manager.create_engine(engine_name, **(engine_config or {}))

        if new_engine is None:
            logger.error(f"Failed to create engine '{engine_name}'")
            return False

        # 重置旧引擎
        if self.engine:
            self.engine.reset()

        # 切换引擎
        self.engine = new_engine
        self.engine_name = engine_name
        self.engine_config = engine_config or {}

        # 清空缓冲区（避免旧数据干扰）
        self.buffer.clear()

        logger.info(f"Switched to engine: {engine_name}")
        return True

    def run(self):
        """线程主循环 - 读取串口数据"""
        logger.info("Serial thread started")

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
                    # 如果暂停，只休眠不读取数据
                    if self.paused:
                        time.sleep(0.1)
                        continue

                    # 读取数据
                    if self.serial_port.in_waiting > 0:
                        data = self.serial_port.read(self.serial_port.in_waiting)
                        if data:
                            self.rx_bytes += len(data)
                            logger.debug(f"[RX] Received {len(data)} bytes: {data.hex()}")

                            # 处理数据
                            self._process_data(data)

                            # 更新统计
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
                    self.error_occurred.emit(f"Serial device disconnected!")
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

        # 使用数据引擎解析
        while len(self.buffer) > 0:
            result = self.engine.parse(self.buffer)

            # 清理已消耗的数据
            if result.consumed_bytes > 0:
                self.buffer = self.buffer[result.consumed_bytes:]
                logger.debug(f"Consumed {result.consumed_bytes} bytes, buffer remaining: {len(self.buffer)}")

            # 如果成功解析，发射信号
            if result.success and result.data:
                logger.info(f"[{self.engine.get_name()}] Parsed data: {result.data}")
                self.data_received.emit(result.data)

            # 如果没有消耗字节且未成功，说明需要等待更多数据
            if result.consumed_bytes == 0 and not result.success:
                break

            # 如果有错误消息，记录日志
            if result.error_message:
                logger.warning(f"Parse warning: {result.error_message}")

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

    def pause(self):
        """暂停串口读取（不关闭串口，线程继续运行）"""
        logger.info("Pausing serial thread...")
        self.paused = True

    def resume(self, port: str = None, baudrate: int = None):
        """恢复串口读取（重新打开串口）"""
        if port:
            self.port = port
        if baudrate:
            self.baudrate = baudrate

        logger.info(f"Resuming serial thread on {self.port} @ {self.baudrate}...")

        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=self.databits,
                stopbits=self.stopbits,
                parity=self.parity,
                timeout=0.1,
                write_timeout=1.0
            )

            if not self.serial_port.is_open:
                raise serial.SerialException(f"Failed to open {self.port}")

            self.paused = False
            self.buffer.clear()  # 清空旧缓冲区
            logger.info("Serial port reopened and resumed")
            return True

        except serial.SerialException as e:
            logger.error(f"Failed to resume serial port: {e}")
            self.error_occurred.emit(f"Resume failed: {str(e)}")
            return False

    def stop(self):
        """完全停止线程（用于程序退出）"""
        logger.info("Stopping serial thread...")
        self.running = False
        self.paused = False

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
        """获取统计信息"""
        return {
            'rx_bytes': self.rx_bytes,
            'tx_bytes': self.tx_bytes
        }

    def reset_stats(self):
        """重置统计信息"""
        self.rx_bytes = 0
        self.tx_bytes = 0

    def get_engine_info(self) -> Dict:
        """获取当前引擎信息"""
        if self.engine is None:
            return {}

        return {
            'name': self.engine.get_name(),
            'description': self.engine.get_description(),
            'channels': self.engine.get_channel_names()
        }
