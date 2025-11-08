"""
统一样式的按钮组件
确保整个应用的按钮风格一致
"""

from PyQt6.QtWidgets import QPushButton
from PyQt6.QtCore import Qt


class StyledButton(QPushButton):
    """统一样式的主按钮"""

    def __init__(self, text: str = "", theme: str = 'dark', parent=None):
        super().__init__(text, parent)
        self.theme = theme
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        """应用按钮样式（与主题管理器一致）"""
        if self.theme == 'dark':
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0A84FF;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #0066CC;
                }
                QPushButton:pressed {
                    background-color: #004999;
                }
                QPushButton:disabled {
                    background-color: #3A3A3A;
                    color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #0A84FF;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #0066CC;
                }
                QPushButton:pressed {
                    background-color: #004999;
                }
                QPushButton:disabled {
                    background-color: #E0E0E0;
                    color: #999999;
                }
            """)

    def set_theme(self, theme: str):
        """更新主题"""
        self.theme = theme
        self._apply_style()


class SecondaryButton(QPushButton):
    """次要按钮（灰色背景）"""

    def __init__(self, text: str = "", theme: str = 'dark', parent=None):
        super().__init__(text, parent)
        self.theme = theme
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        """应用次要按钮样式"""
        if self.theme == 'dark':
            self.setStyleSheet("""
                QPushButton {
                    background-color: #374151;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #4B5563;
                }
                QPushButton:pressed {
                    background-color: #2A2A2A;
                }
                QPushButton:disabled {
                    background-color: #3A3A3A;
                    color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #E5E7EB;
                    color: #1F2937;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: 500;
                    font-size: 13px;
                }
                QPushButton:hover {
                    background-color: #D1D5DB;
                }
                QPushButton:pressed {
                    background-color: #9CA3AF;
                }
                QPushButton:disabled {
                    background-color: #F3F4F6;
                    color: #9CA3AF;
                }
            """)

    def set_theme(self, theme: str):
        """更新主题"""
        self.theme = theme
        self._apply_style()


class SmallButton(QPushButton):
    """小按钮（紧凑型）"""

    def __init__(self, text: str = "", theme: str = 'dark', parent=None):
        super().__init__(text, parent)
        self.theme = theme
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style()

    def _apply_style(self):
        """应用小按钮样式"""
        if self.theme == 'dark':
            self.setStyleSheet("""
                QPushButton {
                    background-color: #374151;
                    color: #FFFFFF;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #4B5563;
                }
                QPushButton:pressed {
                    background-color: #2A2A2A;
                }
                QPushButton:disabled {
                    background-color: #3A3A3A;
                    color: #666666;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #E5E7EB;
                    color: #1F2937;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: 500;
                    font-size: 12px;
                }
                QPushButton:hover {
                    background-color: #D1D5DB;
                }
                QPushButton:pressed {
                    background-color: #9CA3AF;
                }
                QPushButton:disabled {
                    background-color: #F3F4F6;
                    color: #9CA3AF;
                }
            """)

    def set_theme(self, theme: str):
        """更新主题"""
        self.theme = theme
        self._apply_style()
