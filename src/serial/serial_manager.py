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
        engine_name: str = 'firewater',
        engine_config: Optional[Dict] = None
    ) -> bool:
        """
        连接串口

        Args:
            port: 串口名称
            baudrate: 波特率
            databits: 数据位
            stopbits: 停止位
            parity: 校验位
            engine_name: 数据引擎名称
            engine_config: 引擎配置参数

        Returns:
            是否成功开始连接
        """
        # 如果线程已存在且参数相同，直接恢复
        if self.serial_thread and self.serial_thread.isRunning():
            if (self.current_port == port and self.current_baudrate == baudrate):
                logger.info("Resuming existing serial thread...")
                success = self.serial_thread.resume(port, baudrate)
                if success:
                    self.is_connected = True
                    self.connected.emit(port, baudrate)
                    logger.info(f"Serial connection resumed: {port} @ {baudrate}")
                return success
            else:
                # 参数变化，先暂停旧连接，然后用新参数恢复
                logger.info("Port/baudrate changed, updating connection...")
                self.serial_thread.pause()
                success = self.serial_thread.resume(port, baudrate)
                if success:
                    self.is_connected = True
                    self.current_port = port
                    self.current_baudrate = baudrate
                    self.connected.emit(port, baudrate)
                    logger.info(f"Serial connection updated: {port} @ {baudrate}")
                return success

        # 如果已连接，先断开
        if self.is_connected:
            logger.warning("Already connected, disconnecting first")
            self.disconnect()

        try:
            # 创建串口线程（使用新的数据引擎架构）
            self.serial_thread = SerialThread(
                port=port,
                baudrate=baudrate,
                databits=databits,
                stopbits=stopbits,
                parity=parity,
                engine_name=engine_name,
                engine_config=engine_config
            )

            # 连接信号
            self.serial_thread.data_received.connect(self._on_data_received)
            self.serial_thread.error_occurred.connect(self._on_error)
            self.serial_thread.connection_lost.connect(self._on_connection_lost)
            self.serial_thread.rx_tx_stats.connect(self._on_rx_tx_stats)

            # 启动线程
            logger.info(f"[Serial_Thread] is_Running: {self.serial_thread.isRunning()}")
            if not self.serial_thread.isRunning():
                logger.info(f"[Serial_Thread] Starting new thread!")
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
        """断开串口连接（暂停线程，不销毁）"""
        if not self.is_connected or not self.serial_thread:
            return

        logger.info("Disconnecting serial port (pausing thread)...")
        # 发射断开信号
        self.disconnected.emit()



        # 更新状态
        self.is_connected = False
        # 保留 current_port 和 current_baudrate 供快速重连

        # 重置通道管理器
        self.channel_manager.reset()
        
        # 暂停线程（关闭串口但保持线程运行）
        self.serial_thread.pause()


        logger.info("Serial port disconnected (thread paused)")

    def _destroy_thread(self):
        """完全销毁线程（仅在参数变更或程序退出时调用）"""
        if not self.serial_thread:
            return

        logger.info("Destroying serial thread...")
        self.serial_thread.stop()
        if self.serial_thread.isRunning():
            self.serial_thread.wait(3000)  # 等待最多3秒
        self.serial_thread.deleteLater()
        self.serial_thread = None
        logger.info("Serial thread destroyed")

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

        # 只暂停线程，不销毁
        if self.serial_thread:
            self.serial_thread.pause()

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

    def set_engine(self, engine_name: str, engine_config: Optional[Dict] = None) -> bool:
        """
        设置/切换数据引擎

        Args:
            engine_name: 引擎名称 ('firewater', 'justfloat', 'ascii', 或自定义引擎)
            engine_config: 引擎配置参数

        Returns:
            是否切换成功
        """
        if not self.serial_thread:
            logger.warning("No serial thread to set engine")
            return False

        return self.serial_thread.set_engine(engine_name, engine_config)

    def get_engine_info(self) -> Dict:
        """
        获取当前引擎信息

        Returns:
            引擎信息字典
        """
        if self.serial_thread:
            return self.serial_thread.get_engine_info()
        return {}
