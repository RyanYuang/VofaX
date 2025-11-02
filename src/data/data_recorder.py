"""
DataRecorder - 数据录制器
支持 CSV/JSON/TXT 格式录制串口数据
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from PyQt6.QtCore import QObject, pyqtSignal


class DataRecorder(QObject):
    """数据录制器"""

    # 信号
    recording_started = pyqtSignal(str)  # file_path
    recording_paused = pyqtSignal()
    recording_resumed = pyqtSignal()
    recording_stopped = pyqtSignal(str, int)  # file_path, data_count
    error_occurred = pyqtSignal(str)  # error_message

    # 支持的格式
    SUPPORTED_FORMATS = ['csv', 'json', 'txt']

    def __init__(self, channel_manager=None):
        super().__init__()
        self.channel_manager = channel_manager

        # 录制状态
        self.is_recording = False
        self.is_paused = False

        # 录制配置
        self.file_path: Optional[str] = None
        self.file_format: str = 'csv'
        self.max_file_size_mb: float = 100.0  # 默认 100MB 限制
        self.auto_timestamp: bool = True

        # 录制数据
        self.data_buffer: List[Dict] = []
        self.data_count: int = 0
        self.channels: List[str] = []

        # 文件句柄
        self.file_handle = None

        # 订阅通道更新
        if self.channel_manager:
            self.channel_manager.batch_updated.connect(self._on_data_received)

    def start_recording(self, file_path: str = None, file_format: str = 'csv',
                       channels: List[str] = None, max_file_size_mb: float = 100.0):
        """
        开始录制

        Args:
            file_path: 文件路径（None 则自动生成）
            file_format: 文件格式 (csv/json/txt)
            channels: 要录制的通道列表（None 则录制所有）
            max_file_size_mb: 最大文件大小（MB）
        """
        if self.is_recording:
            self.error_occurred.emit("Already recording")
            return False

        # 验证格式
        if file_format not in self.SUPPORTED_FORMATS:
            self.error_occurred.emit(f"Unsupported format: {file_format}")
            return False

        # 生成文件路径
        if file_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = f"recording_{timestamp}.{file_format}"

        # 确保目录存在
        os.makedirs(os.path.dirname(file_path) if os.path.dirname(file_path) else '.', exist_ok=True)

        # 保存配置
        self.file_path = file_path
        self.file_format = file_format
        self.max_file_size_mb = max_file_size_mb
        self.channels = channels or []
        self.data_buffer.clear()
        self.data_count = 0

        # 打开文件
        try:
            if file_format == 'csv':
                self._start_csv_recording()
            elif file_format == 'json':
                self._start_json_recording()
            elif file_format == 'txt':
                self._start_txt_recording()

            self.is_recording = True
            self.is_paused = False
            self.recording_started.emit(self.file_path)
            return True

        except Exception as e:
            self.error_occurred.emit(f"Failed to start recording: {str(e)}")
            return False

    def pause_recording(self):
        """暂停录制"""
        if not self.is_recording:
            return False

        if self.is_paused:
            # 恢复录制
            self.is_paused = False
            self.recording_resumed.emit()
        else:
            # 暂停录制
            self.is_paused = True
            self.recording_paused.emit()

        return True

    def stop_recording(self):
        """停止录制"""
        if not self.is_recording:
            return False

        try:
            # 写入剩余数据
            if self.file_format == 'json':
                self._finalize_json_recording()
            elif self.file_handle:
                self.file_handle.flush()

            # 关闭文件
            if self.file_handle:
                self.file_handle.close()
                self.file_handle = None

            # 重置状态
            self.is_recording = False
            self.is_paused = False

            # 发射信号
            self.recording_stopped.emit(self.file_path, self.data_count)

            return True

        except Exception as e:
            self.error_occurred.emit(f"Failed to stop recording: {str(e)}")
            return False

    def _on_data_received(self, data: Dict[str, float]):
        """接收通道数据"""
        if not self.is_recording or self.is_paused:
            return

        # 检查文件大小限制
        if self._check_file_size_limit():
            self.stop_recording()
            self.error_occurred.emit(f"File size limit reached ({self.max_file_size_mb}MB)")
            return

        # 过滤通道
        if self.channels:
            data = {ch: val for ch, val in data.items() if ch in self.channels}

        # 添加时间戳
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]

        # 写入数据
        try:
            if self.file_format == 'csv':
                self._write_csv_row(timestamp, data)
            elif self.file_format == 'json':
                self._buffer_json_row(timestamp, data)
            elif self.file_format == 'txt':
                self._write_txt_row(timestamp, data)

            self.data_count += 1

        except Exception as e:
            self.error_occurred.emit(f"Failed to write data: {str(e)}")

    def _start_csv_recording(self):
        """开始 CSV 录制"""
        self.file_handle = open(self.file_path, 'w', encoding='utf-8')

        # 写入表头
        if self.channels:
            header = "Timestamp," + ",".join(self.channels)
        else:
            # 等待第一条数据确定通道
            header = "Timestamp"

        self.file_handle.write(header + "\n")
        self.file_handle.flush()

    def _write_csv_row(self, timestamp: str, data: Dict[str, float]):
        """写入 CSV 行"""
        # 第一次写入时确定通道顺序
        if not self.channels and data:
            self.channels = sorted(data.keys())
            # 重写表头
            self.file_handle.seek(0)
            header = "Timestamp," + ",".join(self.channels)
            self.file_handle.write(header + "\n")

        # 写入数据行
        values = [timestamp]
        for channel in self.channels:
            values.append(str(data.get(channel, '')))

        self.file_handle.write(",".join(values) + "\n")

        # 每 10 行刷新一次
        if self.data_count % 10 == 0:
            self.file_handle.flush()

    def _start_json_recording(self):
        """开始 JSON 录制"""
        self.file_handle = open(self.file_path, 'w', encoding='utf-8')
        self.data_buffer.clear()

    def _buffer_json_row(self, timestamp: str, data: Dict[str, float]):
        """缓存 JSON 行"""
        row = {"timestamp": timestamp}
        row.update(data)
        self.data_buffer.append(row)

        # 每 100 条刷新一次
        if len(self.data_buffer) >= 100:
            self._flush_json_buffer()

    def _flush_json_buffer(self):
        """刷新 JSON 缓冲区"""
        # JSON 格式在停止时才写入
        pass

    def _finalize_json_recording(self):
        """完成 JSON 录制"""
        output = {
            "metadata": {
                "start_time": self.data_buffer[0]["timestamp"] if self.data_buffer else "",
                "end_time": self.data_buffer[-1]["timestamp"] if self.data_buffer else "",
                "format_version": "1.0",
                "channels": self.channels or [],
                "data_count": self.data_count
            },
            "data": self.data_buffer
        }

        json.dump(output, self.file_handle, indent=2, ensure_ascii=False)
        self.file_handle.flush()

    def _start_txt_recording(self):
        """开始 TXT 录制"""
        self.file_handle = open(self.file_path, 'w', encoding='utf-8')

        # 写入文件头
        self.file_handle.write(f"# UniScope Data Recording\n")
        self.file_handle.write(f"# Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        if self.channels:
            self.file_handle.write(f"# Channels: {', '.join(self.channels)}\n")
        self.file_handle.write(f"# ─────────────────────────────────────────\n\n")
        self.file_handle.flush()

    def _write_txt_row(self, timestamp: str, data: Dict[str, float]):
        """写入 TXT 行"""
        # 格式：[timestamp] CH0=1.23, CH1=4.56, ...
        values = [f"{ch}={val:.2f}" for ch, val in sorted(data.items())]
        line = f"[{timestamp}] {', '.join(values)}\n"

        self.file_handle.write(line)

        # 每 10 行刷新一次
        if self.data_count % 10 == 0:
            self.file_handle.flush()

    def _check_file_size_limit(self) -> bool:
        """检查文件大小是否超过限制"""
        if self.file_path and os.path.exists(self.file_path):
            size_mb = os.path.getsize(self.file_path) / (1024 * 1024)
            return size_mb >= self.max_file_size_mb
        return False

    def get_recording_info(self) -> Dict:
        """获取录制信息"""
        file_size = 0
        if self.file_path and os.path.exists(self.file_path):
            file_size = os.path.getsize(self.file_path)

        return {
            "is_recording": self.is_recording,
            "is_paused": self.is_paused,
            "file_path": self.file_path,
            "file_format": self.file_format,
            "data_count": self.data_count,
            "file_size_bytes": file_size,
            "file_size_mb": file_size / (1024 * 1024),
            "channels": self.channels
        }
