"""
主题管理器
提供 Dark/Light 主题的 QSS 样式表
"""


class ThemeManager:
    """主题样式管理类"""

    @staticmethod
    def get_stylesheet(theme: str) -> str:
        """
        获取指定主题的样式表

        Args:
            theme: 'dark' or 'light'

        Returns:
            QSS 样式表字符串
        """
        if theme == 'dark':
            return ThemeManager._dark_theme()
        else:
            return ThemeManager._light_theme()

    @staticmethod
    def _dark_theme() -> str:
        """深色主题样式"""
        return """
        /* UniScope Dark Theme */

        QMainWindow {
            background-color: #1A1A1A;
            color: #FFFFFF;
        }

        QMenuBar {
            background-color: #252525;
            color: #FFFFFF;
            border-bottom: 1px solid #3A3A3A;
        }

        QMenuBar::item:selected {
            background-color: #0A84FF;
        }

        QMenu {
            background-color: #252525;
            color: #FFFFFF;
            border: 1px solid #3A3A3A;
        }

        QMenu::item:selected {
            background-color: #0A84FF;
        }

        QToolBar {
            background-color: #252525;
            border-bottom: 1px solid #3A3A3A;
            spacing: 8px;
            padding: 4px;
        }

        QStatusBar {
            background-color: #252525;
            color: #999999;
            border-top: 1px solid #3A3A3A;
        }

        QLabel {
            color: #FFFFFF;
        }

        QPushButton {
            background-color: #0A84FF;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
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

        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #1A1A1A;
            color: #FFFFFF;
            border: 1px solid #3A3A3A;
            border-radius: 4px;
            padding: 6px;
        }

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border: 1px solid #0A84FF;
        }

        QComboBox {
            background-color: #1A1A1A;
            color: #FFFFFF;
            border: 1px solid #3A3A3A;
            border-radius: 4px;
            padding: 6px;
        }

        QComboBox::drop-down {
            border: none;
        }

        QComboBox QAbstractItemView {
            background-color: #252525;
            color: #FFFFFF;
            selection-background-color: #0A84FF;
        }

        QSpinBox, QDoubleSpinBox {
            background-color: #1A1A1A;
            color: #FFFFFF;
            border: 1px solid #3A3A3A;
            border-radius: 4px;
            padding: 6px;
        }

        QCheckBox, QRadioButton {
            color: #FFFFFF;
            spacing: 8px;
        }

        QCheckBox::indicator, QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #3A3A3A;
            border-radius: 4px;
        }

        QCheckBox::indicator:checked {
            background-color: #0A84FF;
            border-color: #0A84FF;
        }

        QScrollBar:vertical {
            background-color: #1A1A1A;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #3A3A3A;
            border-radius: 6px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #4A4A4A;
        }

        QScrollBar:horizontal {
            background-color: #1A1A1A;
            height: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:horizontal {
            background-color: #3A3A3A;
            border-radius: 6px;
            min-width: 30px;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #4A4A4A;
        }

        QTabWidget::pane {
            border: 1px solid #3A3A3A;
            background-color: #1E1E1E;
        }

        QTabBar::tab {
            background-color: #252525;
            color: #999999;
            padding: 8px 16px;
            border-bottom: 2px solid transparent;
        }

        QTabBar::tab:selected {
            color: #FFFFFF;
            border-bottom: 2px solid #0A84FF;
        }

        QTabBar::tab:hover {
            background-color: #2A2A2A;
        }

        QSplitter::handle {
            background-color: #3A3A3A;
        }

        QGroupBox {
            border: 1px solid #3A3A3A;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
            color: #FFFFFF;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: #999999;
        }
        """

    @staticmethod
    def _light_theme() -> str:
        """浅色主题样式"""
        return """
        /* UniScope Light Theme */

        QMainWindow {
            background-color: #FFFFFF;
            color: #000000;
        }

        QMenuBar {
            background-color: #F5F5F5;
            color: #000000;
            border-bottom: 1px solid #E0E0E0;
        }

        QMenuBar::item:selected {
            background-color: #0A84FF;
            color: #FFFFFF;
        }

        QMenu {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #E0E0E0;
        }

        QMenu::item:selected {
            background-color: #0A84FF;
            color: #FFFFFF;
        }

        QToolBar {
            background-color: #F5F5F5;
            border-bottom: 1px solid #E0E0E0;
            spacing: 8px;
            padding: 4px;
        }

        QStatusBar {
            background-color: #F5F5F5;
            color: #666666;
            border-top: 1px solid #E0E0E0;
        }

        QLabel {
            color: #000000;
        }

        QPushButton {
            background-color: #0A84FF;
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
            font-weight: 500;
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

        QLineEdit, QTextEdit, QPlainTextEdit {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #D1D5DB;
            border-radius: 4px;
            padding: 6px;
        }

        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
            border: 1px solid #0A84FF;
        }

        QComboBox {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #D1D5DB;
            border-radius: 4px;
            padding: 6px;
        }

        QComboBox::drop-down {
            border: none;
        }

        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            color: #000000;
            selection-background-color: #0A84FF;
            selection-color: #FFFFFF;
        }

        QSpinBox, QDoubleSpinBox {
            background-color: #FFFFFF;
            color: #000000;
            border: 1px solid #D1D5DB;
            border-radius: 4px;
            padding: 6px;
        }

        QCheckBox, QRadioButton {
            color: #000000;
            spacing: 8px;
        }

        QCheckBox::indicator, QRadioButton::indicator {
            width: 18px;
            height: 18px;
            border: 2px solid #D1D5DB;
            border-radius: 4px;
            background-color: #FFFFFF;
        }

        QCheckBox::indicator:checked {
            background-color: #0A84FF;
            border-color: #0A84FF;
        }

        QScrollBar:vertical {
            background-color: #F5F5F5;
            width: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:vertical {
            background-color: #D1D5DB;
            border-radius: 6px;
            min-height: 30px;
        }

        QScrollBar::handle:vertical:hover {
            background-color: #B0B0B0;
        }

        QScrollBar:horizontal {
            background-color: #F5F5F5;
            height: 12px;
            border-radius: 6px;
        }

        QScrollBar::handle:horizontal {
            background-color: #D1D5DB;
            border-radius: 6px;
            min-width: 30px;
        }

        QScrollBar::handle:horizontal:hover {
            background-color: #B0B0B0;
        }

        QTabWidget::pane {
            border: 1px solid #E0E0E0;
            background-color: #FFFFFF;
        }

        QTabBar::tab {
            background-color: #F5F5F5;
            color: #666666;
            padding: 8px 16px;
            border-bottom: 2px solid transparent;
        }

        QTabBar::tab:selected {
            color: #000000;
            border-bottom: 2px solid #0A84FF;
        }

        QTabBar::tab:hover {
            background-color: #E8E8E8;
        }

        QSplitter::handle {
            background-color: #E0E0E0;
        }

        QGroupBox {
            border: 1px solid #E0E0E0;
            border-radius: 6px;
            margin-top: 12px;
            padding-top: 12px;
            color: #000000;
        }

        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: #666666;
        }
        """
