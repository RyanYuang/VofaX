# -*- coding: utf-8 -*-
"""
Inspector 配置面板
右侧 Widget 属性编辑面板 - 优化版
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QLineEdit, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QFrame,
    QSlider, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from typing import Dict, Any, List


class SectionLabel(QLabel):
    """分组标题标签"""

    def __init__(self, text: str, parent=None):
        super().__init__(text.upper(), parent)
        self.setStyleSheet("""
            color: #9CA3AF;
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.5px;
        """)


class StyledInput(QLineEdit):
    """统一样式的输入框"""

    def __init__(self, theme: str = 'dark', parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setFixedHeight(40)
        self._apply_style()

    def _apply_style(self):
        if self.theme == 'dark':
            self.setStyleSheet("""
                QLineEdit {
                    background-color: #1A1A1A;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #FFFFFF;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #0A84FF;
                }
            """)
        else:
            self.setStyleSheet("""
                QLineEdit {
                    background-color: #FFFFFF;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #1F2937;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #0A84FF;
                }
            """)


class StyledSpinBox(QSpinBox):
    """统一样式的数字输入框"""

    def __init__(self, theme: str = 'dark', parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setFixedHeight(40)
        self._apply_style()

    def _apply_style(self):
        if self.theme == 'dark':
            self.setStyleSheet("""
                QSpinBox {
                    background-color: #1A1A1A;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #FFFFFF;
                    font-size: 14px;
                }
                QSpinBox:focus {
                    border-color: #0A84FF;
                }
            """)
        else:
            self.setStyleSheet("""
                QSpinBox {
                    background-color: #FFFFFF;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #1F2937;
                    font-size: 14px;
                }
                QSpinBox:focus {
                    border-color: #0A84FF;
                }
            """)


class StyledComboBox(QComboBox):
    """统一样式的下拉框"""

    def __init__(self, theme: str = 'dark', parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setFixedHeight(40)
        self._apply_style()

    def _apply_style(self):
        if self.theme == 'dark':
            self.setStyleSheet("""
                QComboBox {
                    background-color: #1A1A1A;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #FFFFFF;
                    font-size: 14px;
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
                }
            """)
        else:
            self.setStyleSheet("""
                QComboBox {
                    background-color: #FFFFFF;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    padding: 8px 12px;
                    color: #1F2937;
                    font-size: 14px;
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
                }
            """)


class ChannelButton(QPushButton):
    """通道选择按钮"""

    def __init__(self, channel: str, theme: str = 'dark', parent=None):
        super().__init__(channel, parent)
        self.channel = channel
        self.theme = theme
        self.is_selected = False
        self.setCheckable(True)
        self.setFixedHeight(32)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._update_style()

    def setChecked(self, checked: bool):
        super().setChecked(checked)
        self.is_selected = checked
        self._update_style()

    def _update_style(self):
        if self.is_selected:
            # 选中状态：蓝色
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0A84FF;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: #0066CC;
                }
            """)
        else:
            # 未选中状态：灰色
            if self.theme == 'dark':
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #1A1A1A;
                        color: #9CA3AF;
                        border: none;
                        border-radius: 4px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #2A2A2A;
                    }
                """)
            else:
                self.setStyleSheet("""
                    QPushButton {
                        background-color: #FFFFFF;
                        color: #6B7280;
                        border: 1px solid #E5E7EB;
                        border-radius: 4px;
                        font-size: 12px;
                    }
                    QPushButton:hover {
                        background-color: #F3F4F6;
                    }
                """)


class InspectorPanel(QWidget):
    """Inspector 配置面板类 - 优化版"""

    config_changed = pyqtSignal(dict)  # 发射配置变更

    def __init__(self, theme: str = 'dark'):
        super().__init__()
        self.theme = theme
        self.current_widget = None
        self.channel_buttons: List[ChannelButton] = []

        self.setFixedWidth(320)
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        header = self._create_header()
        layout.addWidget(header)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(16, 16, 16, 16)
        self.scroll_layout.setSpacing(20)

        scroll.setWidget(self.scroll_content)
        layout.addWidget(scroll)

        # 底部按钮
        footer = self._create_footer()
        layout.addWidget(footer)

    def _create_header(self) -> QWidget:
        """创建标题栏"""
        header = QWidget()
        header.setFixedHeight(56)
        header.setObjectName("inspectorHeader")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(16, 12, 16, 12)

        # 图标 + 标题
        from PyQt6.QtWidgets import QLabel
        icon_label = QLabel("⚙️")
        icon_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(icon_label)

        title_label = QLabel("Widget Inspector")
        title_label.setStyleSheet("font-size: 14px; font-weight: 500;")
        layout.addWidget(title_label)

        layout.addStretch()

        return header

    def _create_footer(self) -> QWidget:
        """创建底部按钮栏"""
        footer = QWidget()
        footer.setObjectName("inspectorFooter")

        layout = QVBoxLayout(footer)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Duplicate 按钮
        duplicate_btn = QPushButton("📋 Duplicate Widget")
        duplicate_btn.setObjectName("duplicateButton")
        duplicate_btn.setFixedHeight(40)
        duplicate_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        duplicate_btn.clicked.connect(self._on_duplicate)
        layout.addWidget(duplicate_btn)

        # Delete 按钮
        delete_btn = QPushButton("🗑️ Delete Widget")
        delete_btn.setObjectName("deleteButton")
        delete_btn.setFixedHeight(40)
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(self._on_delete)
        layout.addWidget(delete_btn)

        return footer

    def set_widget(self, widget_data: Dict[str, Any]):
        """
        设置要编辑的 Widget

        Args:
            widget_data: Widget 数据字典
        """
        self.current_widget = widget_data

        # 清除现有内容
        self._clear_form()

        # 添加配置项
        self._add_title_section(widget_data)
        self._add_separator()
        self._add_data_binding_section(widget_data)
        self._add_separator()
        self._add_settings_section(widget_data)

        self.scroll_layout.addStretch()

    def _clear_form(self):
        """清除表单内容"""
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.channel_buttons.clear()

    def _add_separator(self):
        """添加分隔线"""
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFixedHeight(1)
        self.scroll_layout.addWidget(separator)

    def _add_title_section(self, widget_data: Dict):
        """添加标题编辑区域"""
        section_label = SectionLabel("Widget Title")
        self.scroll_layout.addWidget(section_label)

        title_input = StyledInput(self.theme)
        title_input.setText(widget_data.get('title', ''))
        title_input.textChanged.connect(lambda t: self._update_config('title', t))
        self.scroll_layout.addWidget(title_input)

    def _add_data_binding_section(self, widget_data: Dict):
        """添加数据绑定区域"""
        section_label = SectionLabel("Data Source Binding")
        self.scroll_layout.addWidget(section_label)

        # Channels 标签
        channels_label = QLabel("Channels")
        channels_label.setStyleSheet("font-size: 12px; margin-top: 8px; margin-bottom: 4px;")
        self.scroll_layout.addWidget(channels_label)

        # 通道按钮网格 (3列)
        channels_widget = QWidget()
        channels_grid = QGridLayout(channels_widget)
        channels_grid.setContentsMargins(0, 0, 0, 0)
        channels_grid.setSpacing(8)

        channel_options = ['I0', 'I1', 'I2', 'I3', 'I4', 'I5', 'I6', 'I7',
                          'I8', 'I9', 'I10', 'I11', 'I12', 'I13', 'I14']
        current_channels = widget_data.get('dataBinding', {}).get('channels', [])

        for i, channel in enumerate(channel_options):
            row = i // 3
            col = i % 3
            btn = ChannelButton(channel, self.theme)
            btn.setChecked(channel in current_channels)
            btn.clicked.connect(self._update_channels)
            channels_grid.addWidget(btn, row, col)
            self.channel_buttons.append(btn)

        self.scroll_layout.addWidget(channels_widget)

    def _add_settings_section(self, widget_data: Dict):
        """添加 Widget 特定配置"""
        section_label = SectionLabel("Widget Settings")
        self.scroll_layout.addWidget(section_label)

        widget_type = widget_data.get('type', '')
        config = widget_data.get('config', {})

        if widget_type == 'oscilloscope':
            self._add_oscilloscope_settings(config)
        elif widget_type == 'terminal':
            self._add_terminal_settings(config)
        elif widget_type == 'hex-viewer':
            self._add_hex_viewer_settings(config)
        elif widget_type == 'gauge':
            self._add_gauge_settings(config)
        elif widget_type == 'data-table':
            self._add_data_table_settings(config)
        elif widget_type == 'packet-analyzer':
            self._add_packet_analyzer_settings(config)
        elif widget_type == 'chart':
            self._add_chart_settings(config)

    def _add_oscilloscope_settings(self, config: Dict):
        """示波器配置"""
        # Time Base
        label = QLabel(f"Time Base: {config.get('timeBase', 50)}ms/div")
        label.setStyleSheet("font-size: 12px; margin-top: 4px;")
        self.scroll_layout.addWidget(label)

        slider = QSlider(Qt.Orientation.Horizontal)
        slider.setRange(10, 1000)
        slider.setValue(config.get('timeBase', 50))
        slider.setFixedHeight(32)

        def update_timebase(value):
            label.setText(f"Time Base: {value}ms/div")
            self._update_widget_config('timeBase', value)

        slider.valueChanged.connect(update_timebase)
        self.scroll_layout.addWidget(slider)

        self.scroll_layout.addSpacing(12)

        # Y-Axis
        yaxis_label = QLabel("Y-Axis")
        yaxis_label.setStyleSheet("font-size: 12px; margin-top: 4px;")
        self.scroll_layout.addWidget(yaxis_label)

        yaxis_combo = StyledComboBox(self.theme)
        yaxis_combo.addItems(['auto', 'fixed'])
        yaxis_combo.setCurrentText(config.get('yAxis', 'auto'))
        yaxis_combo.currentTextChanged.connect(lambda v: self._update_widget_config('yAxis', v))
        self.scroll_layout.addWidget(yaxis_combo)

        self.scroll_layout.addSpacing(12)

        # Show Grid
        grid_layout = QHBoxLayout()
        grid_label = QLabel("Show Grid")
        grid_label.setStyleSheet("font-size: 12px;")
        grid_layout.addWidget(grid_label)
        grid_layout.addStretch()

        grid_check = QCheckBox()
        grid_check.setChecked(config.get('showGrid', True))
        grid_check.stateChanged.connect(lambda s: self._update_widget_config('showGrid', bool(s)))
        grid_layout.addWidget(grid_check)

        grid_widget = QWidget()
        grid_widget.setLayout(grid_layout)
        self.scroll_layout.addWidget(grid_widget)

    def _add_terminal_settings(self, config: Dict):
        """终端配置"""
        # Display Mode
        mode_label = QLabel("Display Mode")
        mode_label.setStyleSheet("font-size: 12px; margin-top: 4px;")
        self.scroll_layout.addWidget(mode_label)

        mode_combo = StyledComboBox(self.theme)
        mode_combo.addItems(['ascii', 'hex', 'decimal'])
        mode_combo.setCurrentText(config.get('displayMode', 'ascii'))
        mode_combo.currentTextChanged.connect(lambda v: self._update_widget_config('displayMode', v))
        self.scroll_layout.addWidget(mode_combo)

        self.scroll_layout.addSpacing(12)

        # Auto-scroll
        scroll_layout = QHBoxLayout()
        scroll_label = QLabel("Auto-scroll")
        scroll_label.setStyleSheet("font-size: 12px;")
        scroll_layout.addWidget(scroll_label)
        scroll_layout.addStretch()

        scroll_check = QCheckBox()
        scroll_check.setChecked(config.get('autoScroll', True))
        scroll_check.stateChanged.connect(lambda s: self._update_widget_config('autoScroll', bool(s)))
        scroll_layout.addWidget(scroll_check)

        scroll_widget = QWidget()
        scroll_widget.setLayout(scroll_layout)
        self.scroll_layout.addWidget(scroll_widget)

    def _add_hex_viewer_settings(self, config: Dict):
        """十六进制查看器配置"""
        bytes_label = QLabel("Bytes per Row")
        bytes_label.setStyleSheet("font-size: 12px; margin-top: 4px;")
        self.scroll_layout.addWidget(bytes_label)

        bytes_combo = StyledComboBox(self.theme)
        bytes_combo.addItems(['8', '16', '32'])
        bytes_combo.setCurrentText(str(config.get('bytesPerRow', 16)))
        bytes_combo.currentTextChanged.connect(lambda v: self._update_widget_config('bytesPerRow', int(v)))
        self.scroll_layout.addWidget(bytes_combo)

    def _add_gauge_settings(self, config: Dict):
        """仪表盘配置"""
        # Min Value
        min_label = QLabel("Min Value")
        min_label.setStyleSheet("font-size: 12px; margin-top: 4px;")
        self.scroll_layout.addWidget(min_label)

        min_input = StyledInput(self.theme)
        min_input.setText(str(config.get('min', 0)))
        min_input.textChanged.connect(lambda v: self._update_widget_config('min', float(v) if v else 0))
        self.scroll_layout.addWidget(min_input)

        self.scroll_layout.addSpacing(12)

        # Max Value
        max_label = QLabel("Max Value")
        max_label.setStyleSheet("font-size: 12px; margin-top: 4px;")
        self.scroll_layout.addWidget(max_label)

        max_input = StyledInput(self.theme)
        max_input.setText(str(config.get('max', 100)))
        max_input.textChanged.connect(lambda v: self._update_widget_config('max', float(v) if v else 100))
        self.scroll_layout.addWidget(max_input)

        self.scroll_layout.addSpacing(12)

        # Unit
        unit_label = QLabel("Unit")
        unit_label.setStyleSheet("font-size: 12px; margin-top: 4px;")
        self.scroll_layout.addWidget(unit_label)

        unit_input = StyledInput(self.theme)
        unit_input.setPlaceholderText("e.g., °C, kPa, %")
        unit_input.setText(config.get('unit', ''))
        unit_input.textChanged.connect(lambda v: self._update_widget_config('unit', v))
        self.scroll_layout.addWidget(unit_input)

    def _add_data_table_settings(self, config: Dict):
        """数据表配置"""
        rows_label = QLabel("Max Rows")
        rows_label.setStyleSheet("font-size: 12px; margin-top: 4px;")
        self.scroll_layout.addWidget(rows_label)

        rows_input = StyledInput(self.theme)
        rows_input.setText(str(config.get('maxRows', 100)))
        rows_input.textChanged.connect(lambda v: self._update_widget_config('maxRows', int(v) if v else 100))
        self.scroll_layout.addWidget(rows_input)

    def _add_packet_analyzer_settings(self, config: Dict):
        """包分析器配置"""
        protocol_label = QLabel("Protocol")
        protocol_label.setStyleSheet("font-size: 12px; margin-top: 4px;")
        self.scroll_layout.addWidget(protocol_label)

        protocol_combo = StyledComboBox(self.theme)
        protocol_combo.addItems(['custom', 'modbus', 'ascii'])
        protocol_combo.setCurrentText(config.get('protocol', 'custom'))
        protocol_combo.currentTextChanged.connect(lambda v: self._update_widget_config('protocol', v))
        self.scroll_layout.addWidget(protocol_combo)

    def _add_chart_settings(self, config: Dict):
        """图表配置"""
        chart_label = QLabel("Chart Type")
        chart_label.setStyleSheet("font-size: 12px; margin-top: 4px;")
        self.scroll_layout.addWidget(chart_label)

        chart_combo = StyledComboBox(self.theme)
        chart_combo.addItems(['line', 'bar'])
        chart_combo.setCurrentText(config.get('chartType', 'line'))
        chart_combo.currentTextChanged.connect(lambda v: self._update_widget_config('chartType', v))
        self.scroll_layout.addWidget(chart_combo)

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
                btn.channel for btn in self.channel_buttons if btn.isChecked()
            ]
            if 'dataBinding' not in self.current_widget:
                self.current_widget['dataBinding'] = {}
            self.current_widget['dataBinding']['channels'] = selected_channels
            self.config_changed.emit({'dataBinding': self.current_widget['dataBinding']})

    def _on_delete(self):
        """删除 Widget"""
        self.hide()
        # TODO: 发射删除信号

    def _on_duplicate(self):
        """复制 Widget"""
        # TODO: 发射复制信号
        pass

    def set_theme(self, theme: str):
        """设置主题"""
        self.theme = theme
        self._apply_theme()

        # 重新加载当前 Widget 以应用主题
        if self.current_widget:
            widget_data = self.current_widget
            self.set_widget(widget_data)

    def _apply_theme(self):
        """应用主题样式"""
        if self.theme == 'dark':
            self.setStyleSheet("""
                InspectorPanel {
                    background-color: #252525;
                    border-left: 1px solid #374151;
                }

                QWidget#inspectorHeader {
                    background-color: #252525;
                    border-bottom: 1px solid #374151;
                    color: #FFFFFF;
                }

                QWidget#inspectorFooter {
                    background-color: #252525;
                    border-top: 1px solid #374151;
                }

                QFrame#separator {
                    background-color: #374151;
                }

                QLabel {
                    color: #FFFFFF;
                }

                QPushButton#duplicateButton {
                    background-color: transparent;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    color: #FFFFFF;
                    font-size: 14px;
                }

                QPushButton#duplicateButton:hover {
                    background-color: #374151;
                }

                QPushButton#deleteButton {
                    background-color: transparent;
                    border: 1px solid #FF453A;
                    border-radius: 6px;
                    color: #FF453A;
                    font-size: 14px;
                }

                QPushButton#deleteButton:hover {
                    background-color: #FF453A;
                    color: #FFFFFF;
                }

                QScrollArea {
                    background-color: #252525;
                    border: none;
                }

                QCheckBox {
                    color: #FFFFFF;
                }

                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                    border: 1px solid #374151;
                    background-color: #1A1A1A;
                }

                QCheckBox::indicator:checked {
                    background-color: #0A84FF;
                    border-color: #0A84FF;
                }

                QSlider::groove:horizontal {
                    border: none;
                    height: 4px;
                    background-color: #374151;
                    border-radius: 2px;
                }

                QSlider::handle:horizontal {
                    background-color: #0A84FF;
                    border: none;
                    width: 16px;
                    height: 16px;
                    margin: -6px 0;
                    border-radius: 8px;
                }

                QSlider::handle:horizontal:hover {
                    background-color: #0066CC;
                }
            """)
        else:  # light theme
            self.setStyleSheet("""
                InspectorPanel {
                    background-color: #F9FAFB;
                    border-left: 1px solid #E5E7EB;
                }

                QWidget#inspectorHeader {
                    background-color: #F9FAFB;
                    border-bottom: 1px solid #E5E7EB;
                    color: #1F2937;
                }

                QWidget#inspectorFooter {
                    background-color: #F9FAFB;
                    border-top: 1px solid #E5E7EB;
                }

                QFrame#separator {
                    background-color: #E5E7EB;
                }

                QLabel {
                    color: #1F2937;
                }

                QPushButton#duplicateButton {
                    background-color: transparent;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    color: #1F2937;
                    font-size: 14px;
                }

                QPushButton#duplicateButton:hover {
                    background-color: #F3F4F6;
                }

                QPushButton#deleteButton {
                    background-color: transparent;
                    border: 1px solid #FF453A;
                    border-radius: 6px;
                    color: #FF453A;
                    font-size: 14px;
                }

                QPushButton#deleteButton:hover {
                    background-color: #FF453A;
                    color: #FFFFFF;
                }

                QScrollArea {
                    background-color: #F9FAFB;
                    border: none;
                }

                QCheckBox {
                    color: #1F2937;
                }

                QCheckBox::indicator {
                    width: 20px;
                    height: 20px;
                    border-radius: 4px;
                    border: 1px solid #D1D5DB;
                    background-color: #FFFFFF;
                }

                QCheckBox::indicator:checked {
                    background-color: #0A84FF;
                    border-color: #0A84FF;
                }

                QSlider::groove:horizontal {
                    border: none;
                    height: 4px;
                    background-color: #E5E7EB;
                    border-radius: 2px;
                }

                QSlider::handle:horizontal {
                    background-color: #0A84FF;
                    border: none;
                    width: 16px;
                    height: 16px;
                    margin: -6px 0;
                    border-radius: 8px;
                }

                QSlider::handle:horizontal:hover {
                    background-color: #0066CC;
                }
            """)
