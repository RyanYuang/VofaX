# -*- coding: utf-8 -*-
"""
TopBar - 顶部工具栏
基于 Figma 设计的现代化顶部栏
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
    QMenu, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QBrush, QAction


class ActivityIndicator(QWidget):
    """TX/RX 活动指示灯 (带闪烁动画)"""

    def __init__(self, label: str, color: QColor, parent=None):
        super().__init__(parent)
        self.label_text = label
        self.active_color = color
        self.inactive_color = QColor(60, 60, 60)  # 深灰色
        self.is_active = False
        self._opacity = 0.0

        self.setFixedSize(60, 24)

        # 闪烁定时器
        self.flash_timer = QTimer()
        self.flash_timer.timeout.connect(self._reset_indicator)
        self.flash_timer.setSingleShot(True)

    def flash(self):
        """触发闪烁效果"""
        self.is_active = True
        self._opacity = 1.0
        self.update()

        # 150ms 后重置
        self.flash_timer.stop()
        self.flash_timer.start(150)

    def _reset_indicator(self):
        """重置指示灯"""
        self.is_active = False
        self._opacity = 0.0
        self.update()

    def paintEvent(self, event):
        """绘制指示灯"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制圆形指示灯
        dot_radius = 4
        dot_x = 8
        dot_y = self.height() // 2

        # 根据状态选择颜色
        if self.is_active:
            color = self.active_color
            color.setAlphaF(self._opacity)
        else:
            color = self.inactive_color

        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(dot_x - dot_radius, dot_y - dot_radius, dot_radius * 2, dot_radius * 2)

        # 绘制文字标签
        painter.setPen(QPen(QColor(180, 180, 180)))
        painter.drawText(20, 0, 40, self.height(), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, self.label_text)


class ConnectionBadge(QWidget):
    """连接状态 Badge (带动画圆点)"""

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_connected = False
        self.port_text = "Not Connected"
        self.theme = 'dark'

        # 背景颜色（会在 paintEvent 中使用）
        self.bg_color = QColor("#0A84FF")  # 默认浅蓝色
        self.bg_color.setAlpha(180)  # 半透明
        self.hover_color = QColor("#0066CC")
        self.hover_color.setAlpha(200)
        self.is_hovered = False

        # 设置 objectName 以便精确控制样式
        self.setObjectName("connectionBadge")

        self.setFixedHeight(28)
        self.setMinimumWidth(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 启用鼠标跟踪以支持 hover 效果
        self.setMouseTracking(True)

        # 创建布局和标签
        from PyQt6.QtWidgets import QHBoxLayout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(35, 4, 12, 4)  # 左边留 22px 给圆点 (12px margin + 10px 圆点区域)
        layout.setSpacing(0)

        # 文字标签
        self.label = QLabel(self.port_text)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.label)

        # 动画圆点
        self._pulse_opacity = 1.0

        # 延迟创建动画，确保 Property 已注册
        self.pulse_animation = None
        QTimer.singleShot(0, self._init_animation)

        # 应用初始样式（灰色）
        self._update_style()

    def _init_animation(self):
        """初始化动画"""
        self.pulse_animation = QPropertyAnimation(self, b"pulseOpacity")
        self.pulse_animation.setDuration(1000)
        self.pulse_animation.setStartValue(1.0)
        self.pulse_animation.setEndValue(0.3)
        self.pulse_animation.setEasingCurve(QEasingCurve.Type.InOutSine)
        self.pulse_animation.setLoopCount(-1)  # 无限循环

    def setPulseOpacity(self, opacity: float):
        """设置脉动透明度"""
        self._pulse_opacity = opacity
        self.update()

    def getPulseOpacity(self) -> float:
        return self._pulse_opacity

    pulseOpacity = pyqtProperty(float, fget=getPulseOpacity, fset=setPulseOpacity)

    def set_connected(self, connected: bool, port_text: str = ""):
        """设置连接状态"""
        self.is_connected = connected
        if connected:
            self.port_text = port_text
            if self.pulse_animation:
                self.pulse_animation.start()
        else:
            self.port_text = "Not Connected"
            if self.pulse_animation:
                self.pulse_animation.stop()
            self._pulse_opacity = 1.0

        # 更新文字
        self.label.setText(self.port_text)
        self._update_style()
        self.update()

    def set_theme(self, theme: str):
        """设置主题"""
        self.theme = theme
        self._update_style()

    def _update_style(self):
        """更新样式"""
        if self.is_connected:
            # 连接状态：浅绿色
            self.bg_color = QColor("#30D158")
            self.bg_color.setAlpha(180)  # 半透明 (0-255, 180约为70%透明度)
            self.hover_color = QColor("#28A745")
            self.hover_color.setAlpha(200)  # hover时稍微不透明一点
            text_color = "#FFFFFF"
        else:
            # 未连接状态：浅蓝色
            self.bg_color = QColor("#0A84FF")
            self.bg_color.setAlpha(180)  # 半透明
            self.hover_color = QColor("#0066CC")
            self.hover_color.setAlpha(200)  # hover时稍微不透明一点
            text_color = "#FFFFFF"

        # 只设置文字颜色，背景色在 paintEvent 中绘制
        self.setStyleSheet(f"""
            QWidget#connectionBadge QLabel {{
                color: {text_color};
                font-size: 13px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
        """)
        self.update()  # 触发重绘

    def _get_hover_color(self, color: str) -> str:
        """获取 Hover 颜色"""
        hover_map = {
            "#30D158": "#28A745",  # 绿色 -> 深绿色（连接状态）
            "#0A84FF": "#0066CC",  # 蓝色 -> 深蓝色（未连接状态）
        }
        return hover_map.get(color, color)

    def paintEvent(self, event):
        """绘制事件 - 绘制背景和状态指示圆点"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制圆角矩形背景
        current_color = self.hover_color if self.is_hovered else self.bg_color
        painter.setBrush(QBrush(current_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 14, 14)

        # 圆点位置（在标签左侧）
        dot_x = 25  # 距离左边 16px
        dot_y = self.height() // 2
        dot_radius = 4  # 圆点半径

        if self.is_connected:
            # 连接状态：绿色圆点（带脉动动画）
            dot_color = QColor(48, 209, 88, int(self._pulse_opacity * 255))  # #30D158 绿色
        else:
            # 未连接状态：红色圆点（不闪烁）
            dot_color = QColor(255, 69, 58)  # #FF453A 红色

        painter.setBrush(QBrush(dot_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(dot_x - dot_radius, dot_y - dot_radius, dot_radius * 2, dot_radius * 2)

    def mousePressEvent(self, event):
        """鼠标点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

    def enterEvent(self, event):
        """鼠标进入"""
        self.is_hovered = True
        self.update()

    def leaveEvent(self, event):
        """鼠标离开"""
        self.is_hovered = False
        self.update()

    def sizeHint(self):
        """建议大小"""
        from PyQt6.QtCore import QSize
        return QSize(150, 28)


class LogoWidget(QWidget):
    """Logo Widget - 渐变蓝色方块 + Radar 图标"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)

    def paintEvent(self, event):
        """绘制 Logo"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 渐变背景
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor("#0A84FF"))
        gradient.setColorAt(1, QColor("#0066CC"))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 8, 8)

        # 绘制 Radar 图标 (简化版圆形 + 扇形)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        # 圆形
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = 8
        painter.drawEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)

        # 扫描线
        painter.drawLine(center_x, center_y, center_x + radius, center_y - radius)


class TopBar(QWidget):
    """顶部工具栏"""

    # 信号
    template_requested = pyqtSignal(str)  # 'debug', 'sensor', 'protocol'
    save_layout_requested = pyqtSignal()
    export_data_requested = pyqtSignal()
    recording_clicked = pyqtSignal()
    grid_snap_toggled = pyqtSignal(bool)
    theme_toggled = pyqtSignal()
    connection_clicked = pyqtSignal()

    def __init__(self, theme: str = 'dark', parent=None):
        super().__init__(parent)
        self.theme = theme
        self.grid_snap = True

        self.setFixedHeight(56)
        self._setup_ui()
        self._apply_theme()

    def _setup_ui(self):
        """设置UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # 左侧区域
        left_area = self._create_left_area()
        layout.addLayout(left_area)

        layout.addStretch()

        # 右侧区域
        right_area = self._create_right_area()
        layout.addLayout(right_area)

    def _create_left_area(self):
        """创建左侧区域 (Logo + 名称 + 连接状态 + TX/RX 指示灯)"""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Logo
        self.logo = LogoWidget()
        layout.addWidget(self.logo)

        # 应用名称
        app_name = QLabel("VOFAX")
        app_name.setObjectName("appName")
        app_name.setStyleSheet("font-size: 16px; font-weight: 500; font-family: 'Inter', 'SF Pro', sans-serif;")
        layout.addWidget(app_name)

        # 连接状态 Badge
        self.connection_badge = ConnectionBadge()
        self.connection_badge.set_theme(self.theme)
        self.connection_badge.clicked.connect(self.connection_clicked.emit)
        layout.addWidget(self.connection_badge)

        # 添加分隔线
        separator = self._create_separator()
        layout.addWidget(separator)

        # TX 指示灯 (橙色)
        self.tx_indicator = ActivityIndicator("TX", QColor(255, 165, 0))  # 橙色
        layout.addWidget(self.tx_indicator)

        # RX 指示灯 (绿色)
        self.rx_indicator = ActivityIndicator("RX", QColor(48, 209, 88))  # 绿色
        layout.addWidget(self.rx_indicator)

        return layout

    def _create_right_area(self):
        """创建右侧区域 (工具按钮)"""
        layout = QHBoxLayout()
        layout.setSpacing(8)

        # Templates 按钮（带下拉菜单）
        self.templates_btn = self._create_button("📁 Templates", "templatesButton")
        self.templates_menu = QMenu(self.templates_btn)
        
        # 添加预设模板选项
        debug_action = QAction("🔧 Debug Template", self.templates_btn)
        debug_action.triggered.connect(lambda: self.template_requested.emit('debug'))
        self.templates_menu.addAction(debug_action)
        
        sensor_action = QAction("📊 Sensor Template", self.templates_btn)
        sensor_action.triggered.connect(lambda: self.template_requested.emit('sensor'))
        self.templates_menu.addAction(sensor_action)
        
        protocol_action = QAction("📡 Protocol Template", self.templates_btn)
        protocol_action.triggered.connect(lambda: self.template_requested.emit('protocol'))
        self.templates_menu.addAction(protocol_action)
        
        self.templates_btn.setMenu(self.templates_menu)
        layout.addWidget(self.templates_btn)

        # Save Layout 按钮
        save_btn = self._create_button("💾 Save Layout", "saveButton")
        save_btn.clicked.connect(self.save_layout_requested.emit)
        layout.addWidget(save_btn)

        # Export Data 按钮
        export_btn = self._create_button("📥 Export Data", "exportButton")
        export_btn.clicked.connect(self.export_data_requested.emit)
        layout.addWidget(export_btn)

        # Recording 按钮
        recording_btn = self._create_button("🔴 Record", "recordingButton")
        recording_btn.clicked.connect(self.recording_clicked.emit)
        layout.addWidget(recording_btn)

        # 分隔线
        separator1 = self._create_separator()
        layout.addWidget(separator1)

        # Grid Snap 按钮
        self.grid_btn = self._create_button("⊞ Grid Snap", "gridButton", checkable=True)
        self.grid_btn.setChecked(self.grid_snap)
        self.grid_btn.clicked.connect(self._on_grid_toggle)
        layout.addWidget(self.grid_btn)

        # 分隔线
        separator = self._create_separator()
        layout.addWidget(separator)

        # 主题切换按钮
        self.theme_btn = self._create_icon_button("🌙", "themeButton")
        self.theme_btn.clicked.connect(self._on_theme_toggle)
        layout.addWidget(self.theme_btn)

        return layout

    def _create_button(self, text: str, object_name: str, checkable: bool = False) -> QPushButton:
        """创建按钮"""
        btn = QPushButton(text)
        btn.setObjectName(object_name)
        btn.setFixedHeight(32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        if checkable:
            btn.setCheckable(True)
        return btn

    def _create_icon_button(self, icon: str, object_name: str) -> QPushButton:
        """创建图标按钮"""
        btn = QPushButton(icon)
        btn.setObjectName(object_name)
        btn.setFixedSize(32, 32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        return btn

    def _create_separator(self) -> QFrame:
        """创建垂直分隔线"""
        separator = QFrame()
        separator.setObjectName("separator")
        separator.setFixedWidth(1)
        separator.setFixedHeight(24)
        separator.setFrameShape(QFrame.Shape.VLine)
        return separator

    def _on_grid_toggle(self, checked: bool):
        """Grid Snap 切换"""
        self.grid_snap = checked
        self._update_grid_button_style()
        self.grid_snap_toggled.emit(checked)

    def _on_theme_toggle(self):
        """主题切换"""
        self.theme_toggled.emit()

    def set_theme(self, theme: str):
        """设置主题"""
        self.theme = theme
        self.connection_badge.set_theme(theme)
        self._apply_theme()
        self._update_grid_button_style()
        self._update_theme_button()

        # 更新菜单主题
        self._update_menu_theme()

    def _update_theme_button(self):
        """更新主题按钮图标"""
        if self.theme == 'dark':
            self.theme_btn.setText("☀️")  # Sun icon for switching to light
        else:
            self.theme_btn.setText("🌙")  # Moon icon for switching to dark

    def _update_grid_button_style(self):
        """更新 Grid Snap 按钮样式"""
        if self.grid_snap:
            # 激活状态 - 蓝色背景
            self.grid_btn.setStyleSheet("""
                QPushButton#gridButton {
                    background-color: #0A84FF;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton#gridButton:hover {
                    background-color: #0066CC;
                }
            """)
        else:
            # 未激活状态 - 跟随主题
            if self.theme == 'dark':
                self.grid_btn.setStyleSheet("""
                    QPushButton#gridButton {
                        background-color: transparent;
                        color: #FFFFFF;
                        border: 1px solid #374151;
                        border-radius: 6px;
                        padding: 6px 12px;
                        font-size: 13px;
                    }
                    QPushButton#gridButton:hover {
                        background-color: #374151;
                    }
                """)
            else:
                self.grid_btn.setStyleSheet("""
                    QPushButton#gridButton {
                        background-color: transparent;
                        color: #1F2937;
                        border: 1px solid #D1D5DB;
                        border-radius: 6px;
                        padding: 6px 12px;
                        font-size: 13px;
                    }
                    QPushButton#gridButton:hover {
                        background-color: #F3F4F6;
                    }
                """)

    def _update_menu_theme(self):
        """更新下拉菜单主题"""
        if self.theme == 'dark':
            self.templates_menu.setStyleSheet("""
                QMenu {
                    background-color: #252525;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    color: #FFFFFF;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #0A84FF;
                }
            """)
        else:
            self.templates_menu.setStyleSheet("""
                QMenu {
                    background-color: #FFFFFF;
                    border: 1px solid #E5E7EB;
                    border-radius: 6px;
                    padding: 4px;
                }
                QMenu::item {
                    color: #1F2937;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QMenu::item:selected {
                    background-color: #0A84FF;
                    color: #FFFFFF;
                }
            """)

    def _apply_theme(self):
        """应用主题样式"""
        if self.theme == 'dark':
            self.setStyleSheet("""
                TopBar {
                    background-color: #252525;
                    border-bottom: 1px solid #374151;
                }

                QLabel#appName {
                    color: #FFFFFF;
                }

                QPushButton#templatesButton,
                QPushButton#saveButton,
                QPushButton#exportButton,
                QPushButton#recordingButton {
                    background-color: transparent;
                    color: #FFFFFF;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                }

                QPushButton#templatesButton:hover,
                QPushButton#saveButton:hover,
                QPushButton#exportButton:hover,
                QPushButton#recordingButton:hover {
                    background-color: #374151;
                }

                QPushButton#templatesButton::menu-indicator {
                    width: 0px;
                }

                QPushButton#themeButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                }

                QPushButton#themeButton:hover {
                    background-color: #374151;
                }

                QFrame#separator {
                    background-color: #4B5563;
                    border: none;
                }
            """)
            # 重新应用 ConnectionBadge 样式（防止被 TopBar 样式覆盖）
            self.connection_badge._update_style()
        else:  # light theme
            self.setStyleSheet("""
                TopBar {
                    background-color: #F9FAFB;
                    border-bottom: 1px solid #E5E7EB;
                }

                QLabel#appName {
                    color: #1F2937;
                }

                QPushButton#templatesButton,
                QPushButton#saveButton,
                QPushButton#exportButton,
                QPushButton#recordingButton {
                    background-color: transparent;
                    color: #1F2937;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                }

                QPushButton#templatesButton:hover,
                QPushButton#saveButton:hover,
                QPushButton#exportButton:hover,
                QPushButton#recordingButton:hover {
                    background-color: #F3F4F6;
                }

                QPushButton#templatesButton::menu-indicator {
                    width: 0px;
                }

                QPushButton#themeButton {
                    background-color: transparent;
                    border: none;
                    border-radius: 6px;
                    font-size: 16px;
                }

                QPushButton#themeButton:hover {
                    background-color: #E5E7EB;
                }

                QFrame#separator {
                    background-color: #9CA3AF;
                    border: none;
                }
            """)
            # 重新应用 ConnectionBadge 样式（防止被 TopBar 样式覆盖）
            self.connection_badge._update_style()

        self._update_grid_button_style()
        self._update_menu_theme()

    def set_connected(self, connected: bool, port_text: str = ""):
        """设置连接状态"""
        self.connection_badge.set_connected(connected, port_text)

    def set_grid_snap(self, enabled: bool):
        """设置网格吸附状态"""
        self.grid_snap = enabled
        self.grid_btn.setChecked(enabled)
        self._update_grid_button_style()
