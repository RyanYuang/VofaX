# -*- coding: utf-8 -*-
"""
TopBar - 顶部工具栏
基于 Figma 设计的现代化顶部栏
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton,
    QMenu, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPainter, QColor, QLinearGradient, QPen, QBrush


class ConnectionBadge(QWidget):
    """连接状态 Badge (带动画圆点)"""

    clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_connected = False
        self.port_text = "Not Connected"
        self.theme = 'dark'

        self.setFixedHeight(28)
        self.setMinimumWidth(120)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        # 创建布局和标签
        from PyQt6.QtWidgets import QHBoxLayout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(22, 4, 12, 4)  # 左边留 22px 给圆点 (12px margin + 10px 圆点区域)
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

    pulseOpacity = property(getPulseOpacity, setPulseOpacity)

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
            bg_color = "#30D158"
            text_color = "#FFFFFF"
        else:
            if self.theme == 'dark':
                bg_color = "#374151"
                text_color = "#9CA3AF"
            else:
                bg_color = "#E5E7EB"
                text_color = "#6B7280"

        self.setStyleSheet(f"""
            ConnectionBadge {{
                background-color: {bg_color};
                border-radius: 14px;
                padding: 0px;
            }}
            ConnectionBadge:hover {{
                background-color: {self._get_hover_color(bg_color)};
            }}
            QLabel {{
                color: {text_color};
                font-size: 13px;
                font-weight: 500;
                background: transparent;
                border: none;
            }}
        """)

    def _get_hover_color(self, color: str) -> str:
        """获取 Hover 颜色"""
        hover_map = {
            "#30D158": "#28A745",
            "#374151": "#4B5563",
            "#E5E7EB": "#D1D5DB"
        }
        return hover_map.get(color, color)

    def paintEvent(self, event):
        """绘制事件 - 绘制动画圆点"""
        super().paintEvent(event)

        if not self.is_connected:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制脉动圆点（在标签左侧）
        dot_x = 16  # 距离左边 16px
        dot_y = self.height() // 2
        dot_radius = 3

        # 圆点颜色
        dot_color = QColor(255, 255, 255, int(self._pulse_opacity * 255))
        painter.setBrush(QBrush(dot_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(dot_x - dot_radius, dot_y - dot_radius, dot_radius * 2, dot_radius * 2)

    def mousePressEvent(self, event):
        """鼠标点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()

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
        """创建左侧区域 (Logo + 名称 + 连接状态)"""
        layout = QHBoxLayout()
        layout.setSpacing(12)

        # Logo
        self.logo = LogoWidget()
        layout.addWidget(self.logo)

        # 应用名称
        app_name = QLabel("UniScope")
        app_name.setObjectName("appName")
        app_name.setStyleSheet("font-size: 16px; font-weight: 500; font-family: 'Inter', 'SF Pro', sans-serif;")
        layout.addWidget(app_name)

        # 连接状态 Badge
        self.connection_badge = ConnectionBadge()
        self.connection_badge.set_theme(self.theme)
        self.connection_badge.clicked.connect(self.connection_clicked.emit)
        layout.addWidget(self.connection_badge)

        return layout

    def _create_right_area(self):
        """创建右侧区域 (工具按钮)"""
        layout = QHBoxLayout()
        layout.setSpacing(8)

        # Templates 下拉菜单
        self.templates_btn = self._create_button("📁 Templates", "templatesButton")
        self.templates_menu = QMenu(self)
        self.templates_menu.addAction("Debug Mode", lambda: self.template_requested.emit('debug'))
        self.templates_menu.addAction("Sensor Monitor", lambda: self.template_requested.emit('sensor'))
        self.templates_menu.addAction("Protocol Test", lambda: self.template_requested.emit('protocol'))
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

        # 分隔线
        separator1 = self._create_separator()
        layout.addWidget(separator1)

        # Grid Snap 按钮
        self.grid_btn = self._create_button("⊞ Grid Snap", "gridButton", checkable=True)
        self.grid_btn.setChecked(self.grid_snap)
        self.grid_btn.clicked.connect(self._on_grid_toggle)
        layout.addWidget(self.grid_btn)

        # 分隔线
        separator2 = self._create_separator()
        layout.addWidget(separator2)

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
                QPushButton#exportButton {
                    background-color: transparent;
                    color: #FFFFFF;
                    border: 1px solid #374151;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                }

                QPushButton#templatesButton:hover,
                QPushButton#saveButton:hover,
                QPushButton#exportButton:hover {
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
                QPushButton#exportButton {
                    background-color: transparent;
                    color: #1F2937;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-size: 13px;
                }

                QPushButton#templatesButton:hover,
                QPushButton#saveButton:hover,
                QPushButton#exportButton:hover {
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
