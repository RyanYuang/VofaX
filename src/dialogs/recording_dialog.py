"""
RecordingDialog - 数据录制控制对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QCheckBox, QGroupBox, QFileDialog,
    QSpinBox, QListWidget
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from typing import List


class RecordingDialog(QDialog):
    """数据录制控制对话框"""

    def __init__(self, data_recorder, channel_manager, theme: str = 'dark', parent=None):
        super().__init__(parent)
        self.data_recorder = data_recorder
        self.channel_manager = channel_manager
        self.theme = theme

        self.setWindowTitle("Data Recording")
        self.setModal(False)  # 非模态对话框
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self._setup_ui()
        self._connect_signals()
        self._update_status_timer()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # 录制状态区域
        status_group = QGroupBox("Recording Status")
        status_layout = QVBoxLayout(status_group)

        self.status_label = QLabel("⚪ Not Recording")
        self.status_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        status_layout.addWidget(self.status_label)

        self.info_label = QLabel("Data: 0 rows | File Size: 0 MB")
        self.info_label.setStyleSheet("color: #999999; font-size: 11px;")
        status_layout.addWidget(self.info_label)

        layout.addWidget(status_group)

        # 配置区域
        config_group = QGroupBox("Recording Configuration")
        config_layout = QVBoxLayout(config_group)

        # 文件路径
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("File Path:"))

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Auto-generate filename")
        path_layout.addWidget(self.path_input, 1)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_file)
        path_layout.addWidget(self.browse_btn)

        config_layout.addLayout(path_layout)

        # 文件格式
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Format:"))

        self.format_combo = QComboBox()
        self.format_combo.addItems(['CSV', 'JSON', 'TXT'])
        self.format_combo.setCurrentText('CSV')
        format_layout.addWidget(self.format_combo)

        format_layout.addStretch()
        config_layout.addLayout(format_layout)

        # 文件大小限制
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Max File Size (MB):"))

        self.max_size_spin = QSpinBox()
        self.max_size_spin.setRange(1, 1000)
        self.max_size_spin.setValue(100)
        self.max_size_spin.setSuffix(" MB")
        size_layout.addWidget(self.max_size_spin)

        size_layout.addStretch()
        config_layout.addLayout(size_layout)

        layout.addWidget(config_group)

        # 通道选择区域
        channels_group = QGroupBox("Channels to Record")
        channels_layout = QVBoxLayout(channels_group)

        self.select_all_checkbox = QCheckBox("Select All Channels")
        self.select_all_checkbox.setChecked(True)
        self.select_all_checkbox.stateChanged.connect(self._toggle_select_all)
        channels_layout.addWidget(self.select_all_checkbox)

        self.channels_list = QListWidget()
        self.channels_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self._populate_channels()
        channels_layout.addWidget(self.channels_list)

        layout.addWidget(channels_group)

        # 控制按钮区域
        buttons_layout = QHBoxLayout()

        self.start_btn = QPushButton("🔴 Start Recording")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.clicked.connect(self._start_recording)
        buttons_layout.addWidget(self.start_btn)

        self.pause_btn = QPushButton("⏸ Pause")
        self.pause_btn.setMinimumHeight(40)
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self._pause_recording)
        buttons_layout.addWidget(self.pause_btn)

        self.stop_btn = QPushButton("⏹ Stop")
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_recording)
        buttons_layout.addWidget(self.stop_btn)

        layout.addLayout(buttons_layout)

        # 应用主题
        self._apply_theme()

    def _populate_channels(self):
        """填充通道列表"""
        self.channels_list.clear()

        if self.channel_manager:
            channels = self.channel_manager.get_all_channels()
            for channel in channels:
                self.channels_list.addItem(channel)

        # 默认全选
        self.channels_list.selectAll()

    def _toggle_select_all(self, state):
        """切换全选"""
        if state == Qt.CheckState.Checked.value:
            self.channels_list.selectAll()
        else:
            self.channels_list.clearSelection()

    def _browse_file(self):
        """浏览文件"""
        file_format = self.format_combo.currentText().lower()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Recording File",
            f"recording.{file_format}",
            f"{file_format.upper()} Files (*.{file_format});;All Files (*)"
        )

        if file_path:
            self.path_input.setText(file_path)

    def _start_recording(self):
        """开始录制"""
        # 获取配置
        file_path = self.path_input.text() or None
        file_format = self.format_combo.currentText().lower()
        max_size_mb = self.max_size_spin.value()

        # 获取选中的通道
        selected_items = self.channels_list.selectedItems()
        channels = [item.text() for item in selected_items]

        if not channels:
            self.status_label.setText("⚠️ No channels selected")
            return

        # 开始录制
        success = self.data_recorder.start_recording(
            file_path=file_path,
            file_format=file_format,
            channels=channels,
            max_file_size_mb=max_size_mb
        )

        if success:
            self._update_ui_state(recording=True)

    def _pause_recording(self):
        """暂停/恢复录制"""
        self.data_recorder.pause_recording()

    def _stop_recording(self):
        """停止录制"""
        self.data_recorder.stop_recording()
        self._update_ui_state(recording=False)

    def _update_ui_state(self, recording: bool):
        """更新 UI 状态"""
        self.start_btn.setEnabled(not recording)
        self.pause_btn.setEnabled(recording)
        self.stop_btn.setEnabled(recording)

        # 禁用配置控件
        self.path_input.setEnabled(not recording)
        self.browse_btn.setEnabled(not recording)
        self.format_combo.setEnabled(not recording)
        self.max_size_spin.setEnabled(not recording)
        self.select_all_checkbox.setEnabled(not recording)
        self.channels_list.setEnabled(not recording)

    def _update_status_timer(self):
        """更新状态定时器"""
        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self._update_status)
        self.status_timer.start(500)  # 每 500ms 更新一次

    def _update_status(self):
        """更新录制状态"""
        info = self.data_recorder.get_recording_info()

        if info['is_recording']:
            if info['is_paused']:
                self.status_label.setText("⏸ Recording Paused")
                self.pause_btn.setText("▶ Resume")
            else:
                self.status_label.setText("🔴 Recording...")
                self.pause_btn.setText("⏸ Pause")

            # 更新统计信息
            data_count = info['data_count']
            file_size = info['file_size_mb']
            self.info_label.setText(f"Data: {data_count} rows | File Size: {file_size:.2f} MB")

            # 更新文件路径
            if info['file_path']:
                self.path_input.setText(info['file_path'])

        else:
            self.status_label.setText("⚪ Not Recording")
            self.info_label.setText("Data: 0 rows | File Size: 0 MB")

    def _connect_signals(self):
        """连接信号"""
        self.data_recorder.recording_started.connect(self._on_recording_started)
        self.data_recorder.recording_stopped.connect(self._on_recording_stopped)
        self.data_recorder.error_occurred.connect(self._on_error)

    def _on_recording_started(self, file_path: str):
        """录制开始回调"""
        self.status_label.setText("🔴 Recording...")
        self.path_input.setText(file_path)

    def _on_recording_stopped(self, file_path: str, data_count: int):
        """录制停止回调"""
        self.status_label.setText(f"✅ Recording Stopped ({data_count} rows)")
        self._update_ui_state(recording=False)

    def _on_error(self, error_message: str):
        """错误回调"""
        self.status_label.setText(f"⚠️ Error: {error_message}")

    def _apply_theme(self):
        """应用主题"""
        if self.theme == 'dark':
            self.setStyleSheet("""
                QDialog {
                    background-color: #1A1A1A;
                    color: #FFFFFF;
                }
                QGroupBox {
                    border: 1px solid #3A3A3A;
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 12px;
                    font-weight: 600;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 8px;
                    color: #FFFFFF;
                }
                QLineEdit, QComboBox, QSpinBox {
                    background-color: #252525;
                    border: 1px solid #3A3A3A;
                    border-radius: 4px;
                    padding: 6px;
                    color: #FFFFFF;
                }
                QPushButton {
                    background-color: #2A2A2A;
                    border: 1px solid #3A3A3A;
                    border-radius: 4px;
                    padding: 8px;
                    color: #FFFFFF;
                }
                QPushButton:hover {
                    background-color: #3A3A3A;
                    border-color: #0A84FF;
                }
                QPushButton:disabled {
                    background-color: #1A1A1A;
                    color: #666666;
                }
                QListWidget {
                    background-color: #252525;
                    border: 1px solid #3A3A3A;
                    border-radius: 4px;
                    color: #FFFFFF;
                }
            """)
        else:
            self.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    margin-top: 12px;
                    padding-top: 12px;
                    font-weight: 600;
                }
            """)
