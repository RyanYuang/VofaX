"""
Inspector 配置面板
右侧 Widget 属性编辑面板
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QLineEdit, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QGroupBox,
    QFormLayout, QSlider, QColorDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor
from typing import Dict, Any


class InspectorPanel(QWidget):
    """Inspector 配置面板类"""

    config_changed = pyqtSignal(dict)  # 发射配置变更

    def __init__(self, theme: str = 'dark'):
        super().__init__()
        self.theme = theme
        self.current_widget = None

        self.setFixedWidth(320)
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        header = QWidget()
        header.setFixedHeight(50)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(16, 12, 16, 12)

        title_label = QLabel("Widget Inspector")
        title_label.setStyleSheet("font-size: 12px; color: #999999; font-weight: 500;")
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # 关闭按钮
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(24, 24)
        close_btn.clicked.connect(self.hide)
        header_layout.addWidget(close_btn)

        layout.addWidget(header)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(16, 12, 16, 16)
        self.scroll_layout.setSpacing(16)

        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)

        # 底部按钮
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(16, 12, 16, 12)

        delete_btn = QPushButton("Delete")
        delete_btn.setStyleSheet("background-color: #FF453A;")
        delete_btn.clicked.connect(self._on_delete)
        button_layout.addWidget(delete_btn)

        duplicate_btn = QPushButton("Duplicate")
        duplicate_btn.clicked.connect(self._on_duplicate)
        button_layout.addWidget(duplicate_btn)

        layout.addWidget(button_widget)

    def set_widget(self, widget_data: Dict[str, Any]):
        """
        设置要编辑的 Widget

        Args:
            widget_data: Widget 数据字典
        """
        self.current_widget = widget_data

        # 清除现有内容
        self._clear_form()

        # 基本信息组
        self._add_basic_info_group(widget_data)

        # 数据绑定组
        self._add_data_binding_group(widget_data)

        # 配置组（根据 Widget 类型动态生成）
        self._add_config_group(widget_data)

        self.scroll_layout.addStretch()

    def _clear_form(self):
        """清除表单内容"""
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _add_basic_info_group(self, widget_data: Dict):
        """添加基本信息组"""
        group = QGroupBox("Basic Properties")
        form = QFormLayout(group)

        # 名称
        name_input = QLineEdit(widget_data.get('name', ''))
        name_input.textChanged.connect(lambda t: self._update_config('name', t))
        form.addRow("Name:", name_input)

        # 标题
        title_input = QLineEdit(widget_data.get('title', ''))
        title_input.textChanged.connect(lambda t: self._update_config('title', t))
        form.addRow("Title:", title_input)

        # 位置
        x_spin = QSpinBox()
        x_spin.setRange(0, 10000)
        x_spin.setValue(int(widget_data.get('x', 0)))
        x_spin.valueChanged.connect(lambda v: self._update_config('x', v))
        form.addRow("X Position:", x_spin)

        y_spin = QSpinBox()
        y_spin.setRange(0, 10000)
        y_spin.setValue(int(widget_data.get('y', 0)))
        y_spin.valueChanged.connect(lambda v: self._update_config('y', v))
        form.addRow("Y Position:", y_spin)

        # 尺寸
        width_spin = QSpinBox()
        width_spin.setRange(100, 2000)
        width_spin.setValue(int(widget_data.get('width', 500)))
        width_spin.valueChanged.connect(lambda v: self._update_config('width', v))
        form.addRow("Width:", width_spin)

        height_spin = QSpinBox()
        height_spin.setRange(100, 2000)
        height_spin.setValue(int(widget_data.get('height', 350)))
        height_spin.valueChanged.connect(lambda v: self._update_config('height', v))
        form.addRow("Height:", height_spin)

        # 刷新率
        refresh_layout = QHBoxLayout()
        refresh_slider = QSlider(Qt.Orientation.Horizontal)
        refresh_slider.setRange(10, 1000)
        refresh_slider.setValue(widget_data.get('refreshRate', 50))
        refresh_label = QLabel(f"{refresh_slider.value()} ms")

        def update_refresh_rate(value):
            refresh_label.setText(f"{value} ms")
            self._update_config('refreshRate', value)

        refresh_slider.valueChanged.connect(update_refresh_rate)
        refresh_layout.addWidget(refresh_slider)
        refresh_layout.addWidget(refresh_label)

        form.addRow("Refresh Rate:", refresh_layout)

        # 颜色选择器
        color_layout = QHBoxLayout()
        current_color = widget_data.get('color', '#00ff00')
        color_btn = QPushButton()
        color_btn.setFixedSize(60, 24)
        color_btn.setStyleSheet(f"background-color: {current_color}; border: 1px solid #666;")

        def choose_color():
            color = QColorDialog.getColor(QColor(current_color), self, "Choose Color")
            if color.isValid():
                hex_color = color.name()
                color_btn.setStyleSheet(f"background-color: {hex_color}; border: 1px solid #666;")
                self._update_config('color', hex_color)

        color_btn.clicked.connect(choose_color)
        color_layout.addWidget(color_btn)
        color_layout.addStretch()

        form.addRow("Color:", color_layout)

        self.scroll_layout.addWidget(group)

    def _add_data_binding_group(self, widget_data: Dict):
        """添加数据绑定组"""
        group = QGroupBox("Data Binding")
        layout = QVBoxLayout(group)

        # 通道选择（复选框列表）
        channels_label = QLabel("Channels (I0-I14):")
        layout.addWidget(channels_label)

        channels_widget = QWidget()
        channels_layout = QVBoxLayout(channels_widget)
        channels_layout.setSpacing(4)

        current_channels = widget_data.get('dataBinding', {}).get('channels', [])

        self.channel_checkboxes = []
        for i in range(15):
            channel = f"I{i}"
            cb = QCheckBox(channel)
            cb.setChecked(channel in current_channels)
            cb.stateChanged.connect(lambda state, ch=channel: self._update_channels())
            channels_layout.addWidget(cb)
            self.channel_checkboxes.append(cb)

        layout.addWidget(channels_widget)

        self.scroll_layout.addWidget(group)

    def _add_config_group(self, widget_data: Dict):
        """根据 Widget 类型添加配置组"""
        widget_type = widget_data.get('type', '')
        config = widget_data.get('config', {})

        group = QGroupBox("Widget Configuration")
        form = QFormLayout(group)

        if widget_type == 'oscilloscope':
            # 时基
            timebase_spin = QSpinBox()
            timebase_spin.setRange(10, 1000)
            timebase_spin.setValue(config.get('timeBase', 50))
            timebase_spin.valueChanged.connect(lambda v: self._update_widget_config('timeBase', v))
            form.addRow("Time Base (ms):", timebase_spin)

            # Y轴范围
            yaxis_combo = QComboBox()
            yaxis_combo.addItems(['auto', 'manual'])
            yaxis_combo.setCurrentText(config.get('yAxis', 'auto'))
            yaxis_combo.currentTextChanged.connect(lambda v: self._update_widget_config('yAxis', v))
            form.addRow("Y Axis:", yaxis_combo)

            # 显示网格
            grid_check = QCheckBox()
            grid_check.setChecked(config.get('showGrid', True))
            grid_check.stateChanged.connect(lambda s: self._update_widget_config('showGrid', bool(s)))
            form.addRow("Show Grid:", grid_check)

        elif widget_type == 'terminal':
            # 显示模式
            mode_combo = QComboBox()
            mode_combo.addItems(['ascii', 'hex', 'decimal'])
            mode_combo.setCurrentText(config.get('displayMode', 'ascii'))
            mode_combo.currentTextChanged.connect(lambda v: self._update_widget_config('displayMode', v))
            form.addRow("Display Mode:", mode_combo)

            # 自动滚动
            scroll_check = QCheckBox()
            scroll_check.setChecked(config.get('autoScroll', True))
            scroll_check.stateChanged.connect(lambda s: self._update_widget_config('autoScroll', bool(s)))
            form.addRow("Auto Scroll:", scroll_check)

        elif widget_type == 'hex-viewer':
            # 每行字节数
            bytes_spin = QSpinBox()
            bytes_spin.setRange(8, 32)
            bytes_spin.setValue(config.get('bytesPerRow', 16))
            bytes_spin.valueChanged.connect(lambda v: self._update_widget_config('bytesPerRow', v))
            form.addRow("Bytes Per Row:", bytes_spin)

        elif widget_type == 'gauge':
            # 最小值
            min_spin = QDoubleSpinBox()
            min_spin.setRange(-10000, 10000)
            min_spin.setValue(config.get('min', 0))
            min_spin.valueChanged.connect(lambda v: self._update_widget_config('min', v))
            form.addRow("Minimum:", min_spin)

            # 最大值
            max_spin = QDoubleSpinBox()
            max_spin.setRange(-10000, 10000)
            max_spin.setValue(config.get('max', 100))
            max_spin.valueChanged.connect(lambda v: self._update_widget_config('max', v))
            form.addRow("Maximum:", max_spin)

            # 单位
            unit_input = QLineEdit(config.get('unit', ''))
            unit_input.textChanged.connect(lambda v: self._update_widget_config('unit', v))
            form.addRow("Unit:", unit_input)

        elif widget_type == 'data-table':
            # 最大行数
            rows_spin = QSpinBox()
            rows_spin.setRange(10, 10000)
            rows_spin.setValue(config.get('maxRows', 100))
            rows_spin.valueChanged.connect(lambda v: self._update_widget_config('maxRows', v))
            form.addRow("Max Rows:", rows_spin)

        elif widget_type == 'packet-analyzer':
            # 协议类型
            protocol_combo = QComboBox()
            protocol_combo.addItems(['custom', 'modbus', 'ascii'])
            protocol_combo.setCurrentText(config.get('protocol', 'custom'))
            protocol_combo.currentTextChanged.connect(lambda v: self._update_widget_config('protocol', v))
            form.addRow("Protocol:", protocol_combo)

        elif widget_type == 'chart':
            # 图表类型
            chart_combo = QComboBox()
            chart_combo.addItems(['line', 'bar'])
            chart_combo.setCurrentText(config.get('chartType', 'line'))
            chart_combo.currentTextChanged.connect(lambda v: self._update_widget_config('chartType', v))
            form.addRow("Chart Type:", chart_combo)

        self.scroll_layout.addWidget(group)

    def _update_config(self, key: str, value: Any):
        """更新基本配置"""
        if self.current_widget:
            self.current_widget[key] = value
            self.config_changed.emit({key: value})

    def _update_widget_config(self, key: str, value: Any):
        """更新 Widget 配置"""
        if self.current_widget:
            if 'config' not in self.current_widget:
                self.current_widget['config'] = {}
            self.current_widget['config'][key] = value
            self.config_changed.emit({'config': self.current_widget['config']})

    def _update_channels(self):
        """更新通道绑定"""
        if self.current_widget:
            selected_channels = [
                cb.text() for cb in self.channel_checkboxes if cb.isChecked()
            ]
            if 'dataBinding' not in self.current_widget:
                self.current_widget['dataBinding'] = {}
            self.current_widget['dataBinding']['channels'] = selected_channels
            self.config_changed.emit({'dataBinding': self.current_widget['dataBinding']})

    def _on_delete(self):
        """删除 Widget"""
        # 通过信号通知主窗口删除
        self.hide()
        # TODO: 发射删除信号

    def _on_duplicate(self):
        """复制 Widget"""
        # TODO: 发射复制信号
        pass

    def set_theme(self, theme: str):
        """设置主题"""
        self.theme = theme
