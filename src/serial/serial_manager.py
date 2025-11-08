"""
SerialManager - 串口管理器
提供高层串口管理接口，桥接 SerialThread 和 ChannelManager
"""

from PyQt6.QtCore import QObject, pyqtSignal
from typing import Optional, Dict, Union
import logging

from .serial_thread import SerialThread
from ..data.channel_manager import ChannelManager

logger = logging.getLogger(__name__)


class SerialManager(QObject):
    """
    串口管理器
    负责管理串口线程，分发数据到 ChannelManager
    """

    # 信号定义
    connected = pyqtSignal(str, int)  # port, baudrate
    disconnected = pyqtSignal()
    error_occurred = pyqtSignal(str)  # 错误信息
    connection_lost = pyqtSignal()
    rx_tx_stats = pyqtSignal(int, int)  # RX bytes, TX bytes
    data_received_signal = pyqtSignal()  # RX 活动指示
    data_sent_signal = pyqtSignal()  # TX 活动指示

    def __init__(self, channel_manager: ChannelManager):
        """
        初始化串口管理器

        Args:
            channel_manager: 通道管理器实例
        """
        super().__init__()

        self.channel_manager = channel_manager
        self.serial_thread: Optional[SerialThread] = None
        self.is_connected = False

        # 连接参数
        self.current_port = None
        self.current_baudrate = None

    def connect(
        self,
        port: str,
        baudrate: int = 115200,
        databits: int = 8,
        stopbits: int = 1,
        parity: str = 'N',
        protocol: str = SerialThread.PROTOCOL_FIREWATER,
        channel_count: int = 15
    ) -> bool:
        """
        连接串口

        Args:
            port: 串口名称
            baudrate: 波特率
            databits: 数据位
            stopbits: 停止位
            parity: 校验位
            protocol: 协议类型
            channel_count: 通道数量

        Returns:
            是否成功开始连接
        """
        # 如果已连接，先断开
        if self.is_connected:
            logger.warning("Already connected, disconnecting first")
            self.disconnect()

        try:
            # 创建串口线程
            self.serial_thread = SerialThread(
                port=port,
                baudrate=baudrate,
                databits=databits,
                stopbits=stopbits,
                parity=parity,
                protocol=protocol,
                channel_count=channel_count
            )

            # 连接信号
            self.serial_thread.data_received.connect(self._on_data_received)
            self.serial_thread.error_occurred.connect(self._on_error)
            self.serial_thread.connection_lost.connect(self._on_connection_lost)
            self.serial_thread.rx_tx_stats.connect(self._on_rx_tx_stats)

            # 启动线程
            self.serial_thread.start()

            # 更新状态
            self.is_connected = True
            self.current_port = port
            self.current_baudrate = baudrate

            # 发射连接信号
            self.connected.emit(port, baudrate)

            logger.info(f"Serial connection initiated: {port} @ {baudrate}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect: {e}")
            self.error_occurred.emit(f"Connection failed: {str(e)}")
            return False

    def disconnect(self):
        """断开串口连接"""
        if not self.is_connected or not self.serial_thread:
            return

        logger.info("Disconnecting serial port...")

        # 停止线程
        self.serial_thread.stop()
        self.serial_thread = None

        # 更新状态
        self.is_connected = False
        self.current_port = None
        self.current_baudrate = None

        # 重置通道管理器
        self.channel_manager.reset()

        # 发射断开信号
        self.disconnected.emit()

        logger.info("Serial port disconnected")

    def write(self, data: bytes) -> bool:
        """
        写入数据到串口

        Args:
            data: 要写入的字节

        Returns:
            是否写入成功
        """
        if not self.is_connected or not self.serial_thread:
            logger.warning("Cannot write: not connected")
            return False

        return self.serial_thread.write(data)

    def write_string(self, text: str) -> bool:
        """
        写入字符串到串口

        Args:
            text: 要写入的文本

        Returns:
            是否写入成功
        """
        try:
            data = text.encode('utf-8')
            return self.write(data)
        except UnicodeEncodeError as e:
            logger.error(f"Failed to encode string: {e}")
            return False

    def get_connection_info(self) -> Optional[Dict[str, any]]:
        """
        获取当前连接信息

        Returns:
            连接信息字典或 None
        """
        if not self.is_connected:
            return None

        return {
            'port': self.current_port,
            'baudrate': self.current_baudrate,
            'is_connected': self.is_connected
        }

    def get_stats(self) -> Dict[str, int]:
        """
        获取统计信息

        Returns:
            {'rx_bytes': int, 'tx_bytes': int}
        """
        if self.serial_thread:
            return self.serial_thread.get_stats()
        return {'rx_bytes': 0, 'tx_bytes': 0}

    def reset_stats(self):
        """重置统计信息"""
        if self.serial_thread:
            self.serial_thread.reset_stats()

    # ==================== 私有方法 (信号处理) ====================

    def _on_data_received(self, data: Dict[str, Union[float, str]]):
        """
        处理接收到的数据

        Args:
            data: 通道数据字典 {channel: value}，value 可以是 float 或 str
        """
        logger.info(f"[SerialManager] _on_data_received called with data: {data}")

        # 分发数据到 ChannelManager
        self.channel_manager.update_batch(data)

        # 发射 RX 活动信号 (用于指示灯)
        logger.info(f"[SerialManager] Emitting data_received_signal for RX indicator")
        self.data_received_signal.emit()
        logger.info(f"[SerialManager] data_received_signal emitted")

    def _on_error(self, error_msg: str):
        """
        处理错误

        Args:
            error_msg: 错误信息
        """
        logger.error(f"Serial error: {error_msg}")
        self.error_occurred.emit(error_msg)

    def _on_connection_lost(self):
        """处理连接丢失"""
        logger.warning("Serial connection lost")
        self.is_connected = False

        # 清理线程
        if self.serial_thread:
            self.serial_thread.stop()
            self.serial_thread = None

        # 重置通道管理器
        self.channel_manager.reset()

        # 发射信号
        self.connection_lost.emit()

    def _on_rx_tx_stats(self, rx_bytes: int, tx_bytes: int):
        """
        处理 RX/TX 统计更新

        Args:
            rx_bytes: 接收字节数
            tx_bytes: 发送字节数
        """
        self.rx_tx_stats.emit(rx_bytes, tx_bytes)

    def set_protocol(self, protocol: str):
        """
        设置协议 (仅在未连接时有效)

        Args:
            protocol: 协议类型 ('firewater', 'justfloat', 'ascii')
        """
        if self.is_connected:
            logger.warning("Cannot change protocol while connected")
            return False

        # 可以在这里保存协议设置供下次连接使用
        return True
