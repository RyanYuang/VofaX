"""
ColorPicker - 颜色选择器组件
支持预设颜色 + 自定义颜色对话框
"""

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QColorDialog, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPainter, QBrush


class ColorSwatch(QPushButton):
    """颜色色块按钮"""

    color_selected = pyqtSignal(str)  # hex color

    def __init__(self, color: str, size: int = 32, parent=None):
        super().__init__(parent)
        self.color = color
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._on_clicked)
        self._update_style()

    def _update_style(self):
        """更新样式"""
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.color};
                border: 2px solid #3A3A3A;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                border-color: #0A84FF;
            }}
            QPushButton:checked {{
                border-color: #0A84FF;
                border-width: 3px;
            }}
        """)

    def set_color(self, color: str):
        """设置颜色"""
        self.color = color
        self._update_style()

    def _on_clicked(self):
        """点击回调"""
        self.color_selected.emit(self.color)


class ColorPicker(QWidget):
    """颜色选择器组件"""

    color_changed = pyqtSignal(str)  # hex color

    # 预设颜色
    PRESET_COLORS = [
        '#0A84FF',  # Blue
        '#FF9F0A',  # Orange
        '#30D158',  # Green
        '#BF5AF2',  # Purple
        '#FF453A',  # Red
        '#64D2FF',  # Cyan
        '#FFD60A',  # Yellow
        '#FF375F',  # Pink
        '#FFFFFF',  # White
        '#999999',  # Gray
        '#666666',  # Dark Gray
        '#333333',  # Darker Gray
    ]

    def __init__(self, current_color: str = '#0A84FF', theme: str = 'dark', parent=None):
        super().__init__(parent)
        self.current_color = current_color
        self.theme = theme
        self.swatches = []
        self._setup_ui()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # 当前颜色显示
        current_layout = QHBoxLayout()

        label = QLabel("Current Color:")
        label.setStyleSheet("font-size: 12px; color: #9CA3AF;")
        current_layout.addWidget(label)

        self.current_swatch = ColorSwatch(self.current_color, size=24)
        self.current_swatch.setCheckable(False)
        current_layout.addWidget(self.current_swatch)

        self.current_label = QLabel(self.current_color.upper())
        self.current_label.setStyleSheet("font-size: 12px; color: #FFFFFF; margin-left: 8px;")
        current_layout.addWidget(self.current_label)

        current_layout.addStretch()
        layout.addLayout(current_layout)

        # 预设颜色网格
        preset_label = QLabel("Preset Colors:")
        preset_label.setStyleSheet("font-size: 12px; color: #9CA3AF; margin-top: 4px;")
        layout.addWidget(preset_label)

        grid_widget = QWidget()
        grid_layout = QHBoxLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(6)

        for color in self.PRESET_COLORS:
            swatch = ColorSwatch(color)
            swatch.setCheckable(True)
            swatch.color_selected.connect(self._on_color_selected)
            self.swatches.append(swatch)
            grid_layout.addWidget(swatch)

            # 设置当前颜色为选中
            if color.lower() == self.current_color.lower():
                swatch.setChecked(True)

        grid_layout.addStretch()
        layout.addWidget(grid_widget)

        # 自定义颜色按钮
        custom_btn = QPushButton("🎨 Custom Color...")
        custom_btn.setFixedHeight(32)
        custom_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        custom_btn.clicked.connect(self._show_color_dialog)

        if self.theme == 'dark':
            custom_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1A1A1A;
                    border: 1px solid #374151;
                    border-radius: 4px;
                    color: #FFFFFF;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #2A2A2A;
                    border-color: #0A84FF;
                }
            """)
        else:
            custom_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #D1D5DB;
                    border-radius: 4px;
                    color: #1F2937;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #F3F4F6;
                    border-color: #0A84FF;
                }
            """)

        layout.addWidget(custom_btn)

    def _on_color_selected(self, color: str):
        """颜色选择回调"""
        self.set_color(color)
        self.color_changed.emit(color)

        # 更新选中状态
        for swatch in self.swatches:
            swatch.setChecked(swatch.color.lower() == color.lower())

    def _show_color_dialog(self):
        """显示颜色对话框"""
        current_qcolor = QColor(self.current_color)
        color = QColorDialog.getColor(current_qcolor, self, "Select Color")

        if color.isValid():
            hex_color = color.name()
            self.set_color(hex_color)
            self.color_changed.emit(hex_color)

            # 取消预设颜色的选中状态
            for swatch in self.swatches:
                swatch.setChecked(False)

    def set_color(self, color: str):
        """设置当前颜色"""
        self.current_color = color
        self.current_swatch.set_color(color)
        self.current_label.setText(color.upper())

    def get_color(self) -> str:
        """获取当前颜色"""
        return self.current_color
