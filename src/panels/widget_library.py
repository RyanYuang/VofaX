"""
Widget 库面板 (优化版)
左侧可折叠的 Widget 选择面板 + 平滑动画
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QLineEdit, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor
from PyQt6.QtSvg import QSvgRenderer
from pathlib import Path


class WidgetLibraryItem(QFrame):
    """Widget 库项目"""

    clicked = pyqtSignal(str)  # widget_type
    Item_Width = 250

    def __init__(self, widget_type: str, label: str, description: str, icon: str, theme: str):
        super().__init__()
        self.widget_type = widget_type
        self.label_text = label
        self.description_text = description
        self.icon_text = icon
        self.theme = theme

        # 拖拽相关
        self.drag_start_position = None
        self.is_dragging = False

        self.setFrameStyle(QFrame.Shape.Box)
        self.setLineWidth(1)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(70)
        self.setFixedWidth(self.Item_Width)

        self.move(0,10)


        self._setup_ui()
        self._update_style()

    def _setup_ui(self):
        """设置UI"""
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(12, 8, 12, 8)

        # 图标区域
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(32, 32)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 检查是否是 SVG 文件路径
        if self.icon_text.endswith('.svg'):
            # 加载 SVG 图标
            self._load_svg_icon()
        else:
            # 使用 emoji 文本
            self.icon_label.setText(self.icon_text)
            self.icon_label.setStyleSheet(
                f"font-size: 24px; "
                f"background-color: {'#0A84FF1A' if self.theme == 'dark' else '#0A84FF1A'}; "
                f"border-radius: 8px; "
                f"padding: 8px;"
            )

        self.main_layout.addWidget(self.icon_label)

        # 文本区域
        self.text_layout = QVBoxLayout()
        self.text_layout.setSpacing(2)

        self.title_label = QLabel(self.label_text)
        self.title_label.setStyleSheet("font-weight: 600; font-size: 13px;")

        self.desc_label = QLabel(self.description_text)
        self.desc_label.setStyleSheet("font-size: 11px; color: #999999;")

        self.text_layout.addWidget(self.title_label)
        self.text_layout.addWidget(self.desc_label)

        self.main_layout.addLayout(self.text_layout, 1)

    def _load_svg_icon(self):
        """加载 SVG 图标"""
        svg_path = Path(self.icon_text)
        if svg_path.exists():
            # 使用 QSvgRenderer 渲染 SVG 到 QPixmap
            renderer = QSvgRenderer(str(svg_path))
            pixmap = QPixmap(25, 25)  # SVG 渲染为 40x40
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            self.icon_label.setPixmap(pixmap)
            self.icon_label.setStyleSheet(
                f"background-color: {'#0A84FF1A' if self.theme == 'dark' else '#0A84FF1A'}; "
                f"border-radius: 8px; "
                f"padding: 4px;"
            )
        else:
            # SVG 文件不存在，使用默认emoji
            self.icon_label.setText("📊")
            self.icon_label.setStyleSheet(
                f"font-size: 24px; "
                f"background-color: {'#0A84FF1A' if self.theme == 'dark' else '#0A84FF1A'}; "
                f"border-radius: 8px; "
                f"padding: 8px;"
            )

    def set_compact_mode(self, compact: bool):
        """设置紧凑模式（折叠时）"""
        if compact:
            # 折叠模式：只显示图标
            self.title_label.hide()
            self.desc_label.hide()
            self.setFixedHeight(56)
            self.main_layout.setContentsMargins(4, 4, 4, 4)

            # 设置 Tooltip 显示完整信息
            self.setToolTip(f"{self.label_text}\n{self.description_text}")
        else:
            # 展开模式：显示完整信息
            self.title_label.show()
            self.desc_label.show()
            self.setFixedHeight(70)
            self.main_layout.setContentsMargins(12, 8, 12, 8)
            self.setToolTip("")

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
        """鼠标按下事件 - 记录起始位置"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_start_position = event.pos()
            self.is_dragging = False

    def mouseMoveEvent(self, event):
        """鼠标移动事件 - 执行拖拽"""
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return

        if self.drag_start_position is None:
            return

        # 检查移动距离是否足够开始拖拽（避免误触）
        if (event.pos() - self.drag_start_position).manhattanLength() < 10:
            return

        # 标记为正在拖拽
        self.is_dragging = True

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

        # 重置拖拽状态
        self.is_dragging = False

    def mouseReleaseEvent(self, event):
        """鼠标释放事件 - 仅在未拖拽时触发点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 只有在没有拖拽的情况下才触发点击
            if not self.is_dragging:
                self.clicked.emit(self.widget_type)

            # 重置状态
            self.drag_start_position = None
            self.is_dragging = False

    def set_theme(self, theme: str):
        """设置主题"""
        self.theme = theme
        self._update_style()


class WidgetLibrary(QWidget):
    """Widget 库主面板（带平滑折叠动画）"""

    widget_requested = pyqtSignal(str, float, float)  # type, x, y
    collapsed_changed = pyqtSignal(bool)  # 折叠状态变化

    # 宽度常量
    EXPANDED_WIDTH = 280
    COLLAPSED_WIDTH = 68

    def __init__(self, theme: str = 'dark'):
        super().__init__()
        self.theme = theme
        self.is_collapsed = False

        self.setFixedWidth(self.EXPANDED_WIDTH)
        self._setup_ui()
        self._setup_animation()

    def _get_widgets_from_registry(self):
        """从 WidgetRegistry 获取 widget 列表"""
        from src.data.widget_registry import WidgetRegistry

        widgets = []
        for widget_type in WidgetRegistry.get_registered_types():
            metadata = WidgetRegistry.get_metadata(widget_type)
            widgets.append({
                'type': widget_type,
                'label': metadata.get('name', widget_type),
                'description': metadata.get('description', ''),
                'icon': metadata.get('icon', '📦')
            })
        return widgets

    def _setup_ui(self):
        """设置UI"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # 标题栏
        self.header = QWidget()
        self.header.setFixedHeight(50)
        header_layout = QHBoxLayout(self.header)
        header_layout.setContentsMargins(16, 12, 16, 12)

        self.title_label = QLabel("Widget Library")
        self.title_label.setStyleSheet("font-size: 12px; color: #999999; font-weight: 500;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # 折叠按钮
        self.collapse_btn = QPushButton("◀")
        self.collapse_btn.setFixedSize(24, 24)
        self.collapse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.collapse_btn.setToolTip("Collapse panel (Ctrl+B)")
        self.collapse_btn.clicked.connect(self.toggle_collapse)
        header_layout.addWidget(self.collapse_btn)

        self.main_layout.addWidget(self.header)

        # 搜索框
        self.search_widget = QWidget()
        search_layout = QHBoxLayout(self.search_widget)
        search_layout.setContentsMargins(16, 0, 16, 12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search widgets...")
        self.search_input.textChanged.connect(self._filter_widgets)
        search_layout.addWidget(self.search_input)

        self.main_layout.addWidget(self.search_widget)

        # 滚动区域
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setContentsMargins(16, 0, 16, 16)
        self.scroll_layout.setSpacing(8)

        # 添加所有 Widget 项
        self.widget_items = []
        widgets = self._get_widgets_from_registry()
        for widget_def in widgets:
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

        self.scroll.setWidget(scroll_content)
        self.main_layout.addWidget(self.scroll)

        # 提示区域
        self.tip_widget = QWidget()
        tip_layout = QVBoxLayout(self.tip_widget)
        tip_layout.setContentsMargins(16, 12, 16, 12)

        self.tip_label = QLabel("💡 Tip")
        self.tip_label.setStyleSheet("font-size: 11px; color: #999999;")
        tip_layout.addWidget(self.tip_label)

        self.tip_text = QLabel("Drag widgets onto the canvas or click to add them")
        self.tip_text.setStyleSheet("font-size: 10px; color: #666666;")
        self.tip_text.setWordWrap(True)
        tip_layout.addWidget(self.tip_text)

        self.main_layout.addWidget(self.tip_widget)

    def _setup_animation(self):
        """设置折叠动画"""
        self.collapse_animation = QPropertyAnimation(self, b"maximumWidth")
        self.collapse_animation.setDuration(250)  # 250ms 动画
        self.collapse_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.collapse_animation.finished.connect(self._on_animation_finished)

    def toggle_collapse(self):
        """切换折叠状态（带动画）"""
        if self.collapse_animation.state() == QPropertyAnimation.State.Running:
            return  # 防止动画冲突

        self.is_collapsed = not self.is_collapsed

        if self.is_collapsed:
            # 折叠
            self._prepare_collapse()
            self.collapse_animation.setStartValue(self.EXPANDED_WIDTH)
            self.collapse_animation.setEndValue(self.COLLAPSED_WIDTH)
        else:
            # 展开
            self.collapse_animation.setStartValue(self.COLLAPSED_WIDTH)
            self.collapse_animation.setEndValue(self.EXPANDED_WIDTH)

        self.collapse_animation.start()

        # 更新按钮图标
        self.collapse_btn.setText("▶" if self.is_collapsed else "◀")
        self.collapse_btn.setToolTip("Expand panel (Ctrl+B)" if self.is_collapsed else "Collapse panel (Ctrl+B)")

        # 发射状态变化信号
        self.collapsed_changed.emit(self.is_collapsed)

    def _prepare_collapse(self):
        """准备折叠（隐藏不必要的元素）"""
        # 隐藏标题文字
        self.title_label.hide()

        # 隐藏搜索框
        self.search_widget.hide()

        # 隐藏提示区域
        self.tip_widget.hide()

        # 切换 Widget 项为紧凑模式
        for item in self.widget_items:
            item.set_compact_mode(True)

        # 调整布局边距
        self.scroll_layout.setContentsMargins(8, 0, 8, 8)
        self.scroll_layout.setSpacing(4)

    def _prepare_expand(self):
        """准备展开（显示所有元素）"""
        # 显示标题文字
        self.title_label.show()

        # 显示搜索框
        self.search_widget.show()

        # 显示提示区域
        self.tip_widget.show()

        # 切换 Widget 项为完整模式
        for item in self.widget_items:
            item.set_compact_mode(False)

        # 恢复布局边距
        self.scroll_layout.setContentsMargins(16, 0, 16, 16)
        self.scroll_layout.setSpacing(8)

    def _on_animation_finished(self):
        """动画完成回调"""
        # 设置最终宽度
        if self.is_collapsed:
            self.setFixedWidth(self.COLLAPSED_WIDTH)
        else:
            self.setFixedWidth(self.EXPANDED_WIDTH)
            self._prepare_expand()

    def collapse(self):
        """折叠面板"""
        if not self.is_collapsed:
            self.toggle_collapse()

    def expand(self):
        """展开面板"""
        if self.is_collapsed:
            self.toggle_collapse()

    def _filter_widgets(self, text: str):
        """过滤 Widget 列表"""
        for item in self.widget_items:
            if text.lower() in item.label_text.lower():
                item.show()
            else:
                item.hide()

    def set_theme(self, theme: str):
        """设置主题"""
        self.theme = theme
        for item in self.widget_items:
            item.set_theme(theme)

    def sizeHint(self):
        """建议大小"""
        if self.is_collapsed:
            return QSize(self.COLLAPSED_WIDTH, 600)
        else:
            return QSize(self.EXPANDED_WIDTH, 600)
