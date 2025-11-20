#!/usr/bin/env python3
"""
Demo Virtual Serial Device
虚拟串口测试设备 - 用于测试 UniScope 串口通信功能

功能:
- 模拟真实串口设备
- 支持多种协议: FireWater, JustFloat, ASCII
- 生成模拟波形数据 (正弦波、方波、三角波、随机噪声)
- 支持虚拟串口对 (使用 socat 或 com0com)

使用方法:
1. 安装虚拟串口工具:
   macOS/Linux: brew install socat
   Windows: 下载 com0com (https://sourceforge.net/projects/com0com/)

2. 创建虚拟串口对:
   macOS/Linux: socat -d -d pty,raw,echo=0 pty,raw,echo=0
   输出示例: /dev/ttys002 <-> /dev/ttys003

3. 运行 Demo 设备:
   python demo_device.py --port /dev/ttys002 --protocol firewater

4. 在 UniScope 中连接:
   连接到 /dev/ttys003
"""

import argparse
import serial
import struct
import time
import math
import random
import sys
from typing import List, Dict
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class WaveformGenerator:
    """波形生成器"""

    def __init__(self, channel_count: int = 15):
        self.channel_count = channel_count
        self.t = 0  # 时间步进
        self.dt = 0.01  # 时间增量

    def generate(self) -> List[float]:
        """
        生成多通道波形数据

        Returns:
            List[float]: 15个通道的数据值
        """
        data = []

        # I0: 慢速正弦波 (频率 0.5 Hz, 幅度 2.0)
        data.append(2.0 * math.sin(2 * math.pi * 0.5 * self.t))

        # I1: 快速正弦波 (频率 2 Hz, 幅度 1.5)
        data.append(1.5 * math.sin(2 * math.pi * 2 * self.t))

        # I2: 方波 (频率 1 Hz, 幅度 3.0)
        square = 3.0 if math.sin(2 * math.pi * 1 * self.t) >= 0 else -3.0
        data.append(square)

        # I3: 三角波 (频率 0.5 Hz, 幅度 2.5)
        triangle = 2.5 * (2 / math.pi) * math.asin(math.sin(2 * math.pi * 0.5 * self.t))
        data.append(triangle)

        # I4: 锯齿波 (频率 1 Hz, 幅度 2.0)
        sawtooth = 2.0 * ((self.t * 1) % 1.0 - 0.5)
        data.append(sawtooth)

        # I5: 高斯噪声 (均值 0, 标准差 0.5)
        data.append(random.gauss(0, 0.5))

        # I6: 复合波 (正弦 + 余弦)
        composite = math.sin(2 * math.pi * 1 * self.t) + 0.5 * math.cos(2 * math.pi * 3 * self.t)
        data.append(composite)

        # I7: 衰减振荡
        damped = math.exp(-0.5 * self.t) * math.sin(2 * math.pi * 2 * self.t)
        data.append(damped)

        # I8: 步进信号
        step = math.floor(self.t) % 5
        data.append(float(step))

        # I9: 脉冲信号 (每5秒一个脉冲)
        pulse = 5.0 if (self.t % 5) < 0.1 else 0.0
        data.append(pulse)

        # I10-I14: 随机常数或慢速变化
        for i in range(5):
            slow_sine = 1.0 * math.sin(2 * math.pi * 0.1 * self.t + i)
            data.append(slow_sine)

        # 时间步进
        self.t += self.dt

        return data[:self.channel_count]


class DemoSerialDevice:
    """Demo 虚拟串口设备"""

    # 协议常量
    PROTOCOL_FIREWATER = 'firewater'
    PROTOCOL_JUSTFLOAT = 'justfloat'
    RAW_DATA = 'ascii'

    # FireWater 尾巴
    FIREWATER_TAIL = b'\x00\x00\x80\x7f'

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        protocol: str = PROTOCOL_FIREWATER,
        frequency: int = 100,  # Hz (发送频率)
        channel_count: int = 15
    ):
        """
        初始化 Demo 设备

        Args:
            port: 虚拟串口名称
            baudrate: 波特率
            protocol: 协议类型 (firewater, justfloat, ascii)
            frequency: 数据发送频率 (Hz)
            channel_count: 通道数量
        """
        self.port = port
        self.baudrate = baudrate
        self.protocol = protocol
        self.frequency = frequency
        self.channel_count = channel_count

        self.serial_port: Optional[serial.Serial] = None
        self.running = False
        self.waveform_gen = WaveformGenerator(channel_count)

        # 统计
        self.tx_bytes = 0
        self.tx_packets = 0

    def connect(self) -> bool:
        """连接虚拟串口"""
        try:
            self.serial_port = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            logger.info(f"✅ Connected to {self.port} @ {self.baudrate} baud")
            logger.info(f"📡 Protocol: {self.protocol.upper()}")
            logger.info(f"⚡ Frequency: {self.frequency} Hz")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect: {e}")
            return False

    def disconnect(self):
        """断开连接"""
        if self.serial_port and self.serial_port.is_open:
            self.serial_port.close()
            logger.info(f"Disconnected from {self.port}")

    def send_firewater_packet(self, data: List[float]):
        """
        发送 FireWater 格式数据包

        格式: [float1][float2]...[floatN][tail]
        尾巴: 0x00 0x00 0x80 0x7F (float: inf)
        """
        packet = b''
        for value in data:
            packet += struct.pack('<f', value)  # 小端 float
        packet += self.FIREWATER_TAIL

        self.serial_port.write(packet)
        self.tx_bytes += len(packet)
        self.tx_packets += 1

    def send_justfloat_packet(self, data: List[float]):
        """
        发送 JustFloat 格式数据包

        格式: [float1][float2]...[floatN]
        没有尾巴，直接发送固定数量的 float
        """
        packet = b''
        for value in data:
            packet += struct.pack('<f', value)

        self.serial_port.write(packet)
        self.tx_bytes += len(packet)
        self.tx_packets += 1

    def send_ascii_packet(self, data: List[float]):
        """
        发送 ASCII 格式数据包

        格式: "I0:1.23,I1:4.56,...,I14:7.89\n"
        """
        parts = [f"I{i}:{value:.3f}" for i, value in enumerate(data)]
        packet = ','.join(parts) + '\n'

        self.serial_port.write(packet.encode('utf-8'))
        self.tx_bytes += len(packet)
        self.tx_packets += 1

    def run(self):
        """运行设备（发送数据循环）"""
        if not self.serial_port or not self.serial_port.is_open:
            logger.error("Serial port not connected")
            return

        self.running = True
        interval = 1.0 / self.frequency  # 发送间隔
        last_stats_time = time.time()

        logger.info(f"🚀 Starting data transmission...")
        logger.info(f"Press Ctrl+C to stop\n")

        try:
            while self.running:
                start_time = time.time()

                # 生成波形数据
                data = self.waveform_gen.generate()

                # 根据协议发送数据
                if self.protocol == self.PROTOCOL_FIREWATER:
                    self.send_firewater_packet(data)
                elif self.protocol == self.PROTOCOL_JUSTFLOAT:
                    self.send_justfloat_packet(data)
                elif self.protocol == self.RAW_DATA:
                    self.send_ascii_packet(data)

                # 打印统计信息 (每秒一次)
                current_time = time.time()
                if current_time - last_stats_time >= 1.0:
                    logger.info(
                        f"📊 TX: {self.tx_packets} packets, "
                        f"{self.tx_bytes} bytes, "
                        f"{self.tx_bytes / (current_time - last_stats_time):.1f} B/s"
                    )
                    last_stats_time = current_time
                    self.tx_bytes = 0
                    self.tx_packets = 0

                # 精确控制发送频率
                elapsed = time.time() - start_time
                sleep_time = max(0, interval - elapsed)
                time.sleep(sleep_time)

        except KeyboardInterrupt:
            logger.info("\n⏹️  Stopped by user")
        except Exception as e:
            logger.error(f"❌ Error: {e}")
        finally:
            self.running = False
            self.disconnect()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='UniScope Demo Virtual Serial Device',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # FireWater 协议 (默认)
  python demo_device.py --port /dev/ttys002

  # JustFloat 协议, 50 Hz
  python demo_device.py --port COM3 --protocol justfloat --frequency 50

  # ASCII 协议, 115200 波特率
  python demo_device.py --port /dev/ttyUSB0 --protocol ascii --baudrate 115200

注意:
  - macOS/Linux 需要先创建虚拟串口对: socat -d -d pty,raw,echo=0 pty,raw,echo=0
  - Windows 需要安装 com0com: https://sourceforge.net/projects/com0com/
        """
    )

    parser.add_argument(
        '--port', '-p',
        type=str,
        required=True,
        help='虚拟串口名称 (e.g., COM3, /dev/ttys002)'
    )

    parser.add_argument(
        '--baudrate', '-b',
        type=int,
        default=115200,
        choices=[9600, 19200, 38400, 57600, 115200, 230400, 460800, 921600],
        help='波特率 (default: 115200)'
    )

    parser.add_argument(
        '--protocol',
        type=str,
        default='firewater',
        choices=['firewater', 'justfloat', 'ascii'],
        help='协议类型 (default: firewater)'
    )

    parser.add_argument(
        '--frequency', '-f',
        type=int,
        default=100,
        help='数据发送频率 (Hz, default: 100)'
    )

    parser.add_argument(
        '--channels', '-c',
        type=int,
        default=15,
        help='通道数量 (default: 15)'
    )

    args = parser.parse_args()

    # 创建并运行设备
    device = DemoSerialDevice(
        port=args.port,
        baudrate=args.baudrate,
        protocol=args.protocol,
        frequency=args.frequency,
        channel_count=args.channels
    )

    if device.connect():
        device.run()


if __name__ == '__main__':
    main()
