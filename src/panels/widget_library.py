"""
Widget 库面板
左侧可折叠的 Widget 选择面板
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QLineEdit, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor


class WidgetLibraryItem(QFrame):
    """Widget 库项目"""

    clicked = pyqtSignal(str)  # widget_type

    def __init__(self, widget_type: str, label: str, description: str, icon: str, theme: str):
        super().__init__()
        self.widget_type = widget_type
        self.label_text = label
        self.theme = theme

        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(70)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        # 图标区域
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(
            f"font-size: 24px; "
            f"background-color: {'#0A84FF1A' if theme == 'dark' else '#0A84FF1A'}; "
            f"border-radius: 8px; "
            f"padding: 8px;"
        )
        layout.addWidget(icon_label)

        # 文本区域
        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        title_label = QLabel(label)
        title_label.setStyleSheet("font-weight: 600; font-size: 13px;")

        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 11px; color: #999999;")

        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)

        layout.addLayout(text_layout, 1)

        self._update_style()

    def _update_style(self):
        """更新样式"""
        if self.theme == 'dark':
            self.setStyleSheet("""
                WidgetLibraryItem {
                    background-color: #1A1A1A;
                    border: 1px solid #3A3A3A;
                    border-radius: 8px;
                }
                WidgetLibraryItem:hover {
                    border-color: #0A84FF;
                    background-color: #1f1f1f;
                }
            """)
        else:
            self.setStyleSheet("""
                WidgetLibraryItem {
                    background-color: #FFFFFF;
                    border: 1px solid #D1D5DB;
                    border-radius: 8px;
                }
                WidgetLibraryItem:hover {
                    border-color: #0A84FF;
                    background-color: #F9FAFB;
                }
            """)

    def mousePressEvent(self, event):
        """鼠标按下事件 - 开始拖拽"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 执行拖拽"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        # 创建拖拽对象
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(self.widget_type)
        drag.setMimeData(mime_data)

        # 创建拖拽图标
        pixmap = QPixmap(self.size())
        pixmap.fill(Qt.GlobalColor.transparent)
        painter = QPainter(pixmap)
        painter.setOpacity(0.7)
        self.render(painter)
        painter.end()

        drag.setPixmap(pixmap)
        drag.setHotSpot(event.pos())

        # 执行拖拽
        drag.exec(Qt.DropAction.CopyAction)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 点击添加"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.widget_type)

    def set_theme(self, theme: str):
        """设置主题"""
        self.theme = theme
        self._update_style()


class WidgetLibrary(QWidget):
    """Widget 库主面板"""

    widget_requested = pyqtSignal(str, float, float)  # type, x, y

    # Widget 定义
    WIDGETS = [
        {
            'type': 'oscilloscope',
            'label': 'Oscilloscope',
            'description': 'Multi-channel waveform viewer',
            'icon': '📊'
        },
        {
            'type': 'terminal',
            'label': 'Terminal',
            'description': 'Serial data console',
            'icon': '💻'
        },
        {
            'type': 'hex-viewer',
            'label': 'Hex Viewer',
            'description': 'Raw data in hexadecimal',
            'icon': '🔢'
        },
        {
            'type': 'gauge',
            'label': 'Gauge',
            'description': 'Circular meter display',
            'icon': '🎯'
        },
        {
            'type': 'data-table',
            'label': 'Data Table',
            'description': 'Live updating table',
            'icon': '📋'
        },
        {
            'type': 'packet-analyzer',
            'label': 'Packet Analyzer',
            'description': 'Protocol decoder',
            'icon': '📡'
        },
        {
            'type': 'chart',
            'label': 'Chart',
            'description': 'Line/Bar chart',
            'icon': '📈'
        },
    ]

    def __init__(self, theme: str = 'dark'):
        super().__init__()
        self.theme = theme
        self.is_collapsed = False

        self.setFixedWidth(280)
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

        title_label = QLabel("Widget Library")
        title_label.setStyleSheet("font-size: 12px; color: #999999; font-weight: 500;")
        header_layout.addWidget(title_label)

        # 折叠按钮
        collapse_btn = QPushButton("◀")
        collapse_btn.setFixedSize(24, 24)
        collapse_btn.clicked.connect(self._toggle_collapse)
        header_layout.addWidget(collapse_btn)

        layout.addWidget(header)

        # 搜索框
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(16, 0, 16, 12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search widgets...")
        self.search_input.textChanged.connect(self._filter_widgets)
        search_layout.addWidget(self.search_input)

        layout.addLayout(search_layout)

        # 滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(16, 0, 16, 16)
        self.scroll_layout.setSpacing(8)

        # 添加所有 Widget 项
        self.widget_items = []
        for widget_def in self.WIDGETS:
            item = WidgetLibraryItem(
                widget_def['type'],
                widget_def['label'],
                widget_def['description'],
                widget_def['icon'],
                self.theme
            )
            item.clicked.connect(lambda t=widget_def['type']: self.widget_requested.emit(t, 100, 100))
            self.scroll_layout.addWidget(item)
            self.widget_items.append(item)

        self.scroll_layout.addStretch()

        scroll.setWidget(scroll_content)
        layout.addWidget(scroll)

        # 提示区域
        tip_widget = QWidget()
        tip_layout = QVBoxLayout(tip_widget)
        tip_layout.setContentsMargins(16, 12, 16, 12)

        tip_label = QLabel("💡 Tip")
        tip_label.setStyleSheet("font-size: 11px; color: #999999;")
        tip_layout.addWidget(tip_label)

        tip_text = QLabel("Drag widgets onto the canvas or click to add them")
        tip_text.setStyleSheet("font-size: 10px; color: #666666;")
        tip_text.setWordWrap(True)
        tip_layout.addWidget(tip_text)

        layout.addWidget(tip_widget)

    def _filter_widgets(self, text: str):
        """过滤 Widget 列表"""
        for item in self.widget_items:
            if text.lower() in item.label_text.lower():
                item.show()
            else:
                item.hide()

    def _toggle_collapse(self):
        """切换折叠状态"""
        self.is_collapsed = not self.is_collapsed
        if self.is_collapsed:
            self.setFixedWidth(48)
        else:
            self.setFixedWidth(280)

    def set_theme(self, theme: str):
        """设置主题"""
        self.theme = theme
        for item in self.widget_items:
            item.set_theme(theme)
