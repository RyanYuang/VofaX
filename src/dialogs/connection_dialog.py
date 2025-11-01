# -*- coding: utf-8 -*-
"""
ConnectionDialog - 串口连接对话框
基于 Figma 设计的现代化连接配置界面
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QComboBox, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon
import serial.tools.list_ports


class ConnectionDialog(QDialog):
    """串口连接配置对话框"""

    # 信号: 连接成功 (port, baudrate, databits, stopbits, parity)
    connected = pyqtSignal(str, int, int, int, str)

    def __init__(self, theme: str = 'dark', parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setWindowTitle("Serial Connection")
        self.setFixedWidth(480)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._setup_ui()
        self._apply_theme()
        self._scan_ports()

    def _setup_ui(self):
        """设置UI"""
        # 主容器
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 内容容器 (用于圆角和背景)
        content_frame = QFrame()
        content_frame.setObjectName("contentFrame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)

        # 1. 标题栏
        header = self._create_header()
        content_layout.addWidget(header)

        # 2. 表单区域
        form = self._create_form()
        content_layout.addWidget(form)

        # 3. 底部按钮栏
        footer = self._create_footer()
        content_layout.addWidget(footer)

        main_layout.addWidget(content_frame)

    def _create_header(self) -> QFrame:
        """创建标题栏"""
        header = QFrame()
        header.setObjectName("header")
        header.setFixedHeight(56)
        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 12, 16, 12)

        # 标题
        title = QLabel("Serial Connection")
        title.setObjectName("dialogTitle")
        title.setStyleSheet("font-size: 16px; font-weight: 500;")
        layout.addWidget(title)

        layout.addStretch()

        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setObjectName("closeButton")
        close_btn.setFixedSize(32, 32)
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

        return header

    def _create_form(self) -> QFrame:
        """创建表单区域"""
        form = QFrame()
        form.setObjectName("formArea")
        layout = QVBoxLayout(form)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 端口选择
        port_group = self._create_port_group()
        layout.addWidget(port_group)

        # 波特率选择
        baudrate_group = self._create_baudrate_group()
        layout.addWidget(baudrate_group)

        # 串口参数 (3列布局)
        params_group = self._create_params_group()
        layout.addWidget(params_group)

        return form

    def _create_port_group(self) -> QFrame:
        """创建端口选择组"""
        group = QFrame()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 标签
        label = QLabel("PORT")
        label.setObjectName("fieldLabel")
        label.setStyleSheet("font-size: 11px; color: #9CA3AF; font-weight: 500;")
        layout.addWidget(label)

        # 端口下拉框 + 刷新按钮
        port_layout = QHBoxLayout()
        port_layout.setSpacing(8)

        self.port_combo = QComboBox()
        self.port_combo.setObjectName("portCombo")
        self.port_combo.setFixedHeight(40)
        self.port_combo.setPlaceholderText("Select port...")
        port_layout.addWidget(self.port_combo)

        # 刷新按钮
        self.refresh_btn = QPushButton("🔄")
        self.refresh_btn.setObjectName("refreshButton")
        self.refresh_btn.setFixedSize(40, 40)
        self.refresh_btn.setToolTip("Scan for ports")
        self.refresh_btn.clicked.connect(self._scan_ports)
        port_layout.addWidget(self.refresh_btn)

        layout.addLayout(port_layout)

        return group

    def _create_baudrate_group(self) -> QFrame:
        """创建波特率选择组"""
        group = QFrame()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 标签
        label = QLabel("BAUD RATE")
        label.setObjectName("fieldLabel")
        label.setStyleSheet("font-size: 11px; color: #9CA3AF; font-weight: 500;")
        layout.addWidget(label)

        # 波特率下拉框
        self.baudrate_combo = QComboBox()
        self.baudrate_combo.setObjectName("baudrateCombo")
        self.baudrate_combo.setFixedHeight(40)
        self.baudrate_combo.addItems([
            '9600', '19200', '38400', '57600',
            '115200', '230400', '460800', '921600'
        ])
        self.baudrate_combo.setCurrentText('115200')
        layout.addWidget(self.baudrate_combo)

        return group

    def _create_params_group(self) -> QFrame:
        """创建串口参数组 (Parity, Data Bits, Stop Bits)"""
        group = QFrame()
        layout = QGridLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setHorizontalSpacing(12)
        layout.setVerticalSpacing(8)

        # Parity
        parity_label = QLabel("PARITY")
        parity_label.setObjectName("fieldLabel")
        parity_label.setStyleSheet("font-size: 11px; color: #9CA3AF; font-weight: 500;")
        layout.addWidget(parity_label, 0, 0)

        self.parity_combo = QComboBox()
        self.parity_combo.setObjectName("parityCombo")
        self.parity_combo.setFixedHeight(40)
        self.parity_combo.addItems(['None', 'Even', 'Odd', 'Mark', 'Space'])
        layout.addWidget(self.parity_combo, 1, 0)

        # Data Bits
        databits_label = QLabel("DATA BITS")
        databits_label.setObjectName("fieldLabel")
        databits_label.setStyleSheet("font-size: 11px; color: #9CA3AF; font-weight: 500;")
        layout.addWidget(databits_label, 0, 1)

        self.databits_combo = QComboBox()
        self.databits_combo.setObjectName("databitsCombo")
        self.databits_combo.setFixedHeight(40)
        self.databits_combo.addItems(['5', '6', '7', '8'])
        self.databits_combo.setCurrentText('8')
        layout.addWidget(self.databits_combo, 1, 1)

        # Stop Bits
        stopbits_label = QLabel("STOP BITS")
        stopbits_label.setObjectName("fieldLabel")
        stopbits_label.setStyleSheet("font-size: 11px; color: #9CA3AF; font-weight: 500;")
        layout.addWidget(stopbits_label, 0, 2)

        self.stopbits_combo = QComboBox()
        self.stopbits_combo.setObjectName("stopbitsCombo")
        self.stopbits_combo.setFixedHeight(40)
        self.stopbits_combo.addItems(['1', '1.5', '2'])
        layout.addWidget(self.stopbits_combo, 1, 2)

        return group

    def _create_footer(self) -> QFrame:
        """创建底部按钮栏"""
        footer = QFrame()
        footer.setObjectName("footer")
        footer.setFixedHeight(72)
        layout = QHBoxLayout(footer)
        layout.setContentsMargins(24, 16, 24, 16)
        layout.setSpacing(12)

        layout.addStretch()

        # 取消按钮
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.setFixedHeight(40)
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)

        # 连接按钮
        connect_btn = QPushButton("🔌 Connect")
        connect_btn.setObjectName("connectButton")
        connect_btn.setFixedHeight(40)
        connect_btn.setFixedWidth(120)
        connect_btn.clicked.connect(self._on_connect)
        layout.addWidget(connect_btn)

        return footer

    def _scan_ports(self):
        """扫描可用串口"""
        self.port_combo.clear()

        # 获取系统所有可用串口
        ports = serial.tools.list_ports.comports()

        if not ports:
            self.port_combo.addItem("No ports found")
            self.port_combo.setEnabled(False)
            return

        self.port_combo.setEnabled(True)
        for port in ports:
            # 显示: "COM3 - USB Serial Device"
            display_text = f"{port.device}"
            if port.description and port.description != "n/a":
                display_text += f" - {port.description}"
            self.port_combo.addItem(display_text, port.device)

        # 动画效果: 短暂旋转刷新按钮
        self.refresh_btn.setEnabled(False)
        QTimer.singleShot(500, lambda: self.refresh_btn.setEnabled(True))

    def _on_connect(self):
        """连接按钮点击"""
        if self.port_combo.count() == 0 or not self.port_combo.isEnabled():
            return

        # 获取选中的端口 (从 userData)
        port = self.port_combo.currentData()
        if not port:
            # Fallback: 解析显示文本
            port = self.port_combo.currentText().split()[0]

        baudrate = int(self.baudrate_combo.currentText())
        databits = int(self.databits_combo.currentText())

        # 停止位转换
        stopbits_map = {'1': 1, '1.5': 1.5, '2': 2}
        stopbits = stopbits_map[self.stopbits_combo.currentText()]

        # 校验位转换
        parity_map = {
            'None': 'N',
            'Even': 'E',
            'Odd': 'O',
            'Mark': 'M',
            'Space': 'S'
        }
        parity = parity_map[self.parity_combo.currentText()]

        # 发射连接信号
        self.connected.emit(port, baudrate, databits, int(stopbits), parity)
        self.accept()

    def _apply_theme(self):
        """应用主题样式"""
        if self.theme == 'dark':
            self.setStyleSheet("""
                QDialog {
                    background: transparent;
                }

                QFrame#contentFrame {
                    background-color: #252525;
                    border-radius: 12px;
                    border: 1px solid #374151;
                }

                QFrame#header {
                    background-color: #252525;
                    border-bottom: 1px solid #374151;
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                }

                QLabel#dialogTitle {
                    color: #FFFFFF;
                }

                QPushButton#closeButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    color: #9CA3AF;
                    font-size: 18px;
                }

                QPushButton#closeButton:hover {
                    background-color: #374151;
                    color: #FFFFFF;
                }

                QFrame#formArea {
                    background-color: transparent;
                }

                QComboBox {
                    background-color: #1A1A1A;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #FFFFFF;
                    font-size: 14px;
                }

                QComboBox:hover {
                    border-color: #4B5563;
                }

                QComboBox:focus {
                    border-color: #0A84FF;
                }

                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }

                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 5px solid #9CA3AF;
                    margin-right: 8px;
                }

                QComboBox QAbstractItemView {
                    background-color: #1A1A1A;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    selection-background-color: #0A84FF;
                    color: #FFFFFF;
                    padding: 4px;
                }

                QPushButton#refreshButton {
                    background-color: #1A1A1A;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    color: #9CA3AF;
                    font-size: 16px;
                }

                QPushButton#refreshButton:hover {
                    background-color: #374151;
                }

                QPushButton#refreshButton:pressed {
                    background-color: #4B5563;
                }

                QFrame#footer {
                    background-color: #252525;
                    border-top: 1px solid #374151;
                    border-bottom-left-radius: 12px;
                    border-bottom-right-radius: 12px;
                }

                QPushButton#cancelButton {
                    background-color: transparent;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    color: #FFFFFF;
                    font-size: 14px;
                    padding: 8px 16px;
                }

                QPushButton#cancelButton:hover {
                    background-color: #374151;
                }

                QPushButton#connectButton {
                    background-color: #30D158;
                    border: none;
                    border-radius: 6px;
                    color: #FFFFFF;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 8px 16px;
                }

                QPushButton#connectButton:hover {
                    background-color: #28A745;
                }

                QPushButton#connectButton:pressed {
                    background-color: #20803A;
                }
            """)
        else:  # light theme
            self.setStyleSheet("""
                QDialog {
                    background: transparent;
                }

                QFrame#contentFrame {
                    background-color: #FFFFFF;
                    border-radius: 12px;
                    border: 1px solid #E5E7EB;
                }

                QFrame#header {
                    background-color: #FFFFFF;
                    border-bottom: 1px solid #E5E7EB;
                    border-top-left-radius: 12px;
                    border-top-right-radius: 12px;
                }

                QLabel#dialogTitle {
                    color: #1F2937;
                }

                QPushButton#closeButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    color: #6B7280;
                    font-size: 18px;
                }

                QPushButton#closeButton:hover {
                    background-color: #F3F4F6;
                    color: #1F2937;
                }

                QFrame#formArea {
                    background-color: transparent;
                }

                QComboBox {
                    background-color: #FFFFFF;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #1F2937;
                    font-size: 14px;
                }

                QComboBox:hover {
                    border-color: #9CA3AF;
                }

                QComboBox:focus {
                    border-color: #0A84FF;
                }

                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }

                QComboBox::down-arrow {
                    image: none;
                    border-left: 4px solid transparent;
                    border-right: 4px solid transparent;
                    border-top: 5px solid #6B7280;
                    margin-right: 8px;
                }

                QComboBox QAbstractItemView {
                    background-color: #FFFFFF;
                    border: 1px solid #E5E7EB;
                    border-radius: 6px;
                    selection-background-color: #0A84FF;
                    color: #1F2937;
                    padding: 4px;
                }

                QPushButton#refreshButton {
                    background-color: #FFFFFF;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    color: #6B7280;
                    font-size: 16px;
                }

                QPushButton#refreshButton:hover {
                    background-color: #F3F4F6;
                }

                QPushButton#refreshButton:pressed {
                    background-color: #E5E7EB;
                }

                QFrame#footer {
                    background-color: #FFFFFF;
                    border-top: 1px solid #E5E7EB;
                    border-bottom-left-radius: 12px;
                    border-bottom-right-radius: 12px;
                }

                QPushButton#cancelButton {
                    background-color: transparent;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    color: #1F2937;
                    font-size: 14px;
                    padding: 8px 16px;
                }

                QPushButton#cancelButton:hover {
                    background-color: #F3F4F6;
                }

                QPushButton#connectButton {
                    background-color: #34C759;
                    border: none;
                    border-radius: 6px;
                    color: #FFFFFF;
                    font-size: 14px;
                    font-weight: 500;
                    padding: 8px 16px;
                }

                QPushButton#connectButton:hover {
                    background-color: #2FAD4E;
                }

                QPushButton#connectButton:pressed {
                    background-color: #289944;
                }
            """)

    def get_connection_params(self) -> dict:
        """获取连接参数"""
        return {
            'port': self.port_combo.currentData() or self.port_combo.currentText().split()[0],
            'baudrate': int(self.baudrate_combo.currentText()),
            'databits': int(self.databits_combo.currentText()),
            'stopbits': {'1': 1, '1.5': 1.5, '2': 2}[self.stopbits_combo.currentText()],
            'parity': {'None': 'N', 'Even': 'E', 'Odd': 'O', 'Mark': 'M', 'Space': 'S'}[self.parity_combo.currentText()]
        }
