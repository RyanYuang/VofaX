"""
Widget 库面板 (优化版)
左侧可折叠的 Widget 选择面板 + 平滑动画
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QScrollArea, QLineEdit, QFrame,
    QTabWidget, QSizePolicy, QComboBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QMimeData, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtGui import QDrag, QPixmap, QPainter, QColor, QFont, QImage, QIcon
from PyQt6.QtSvg import QSvgRenderer
from pathlib import Path
import os

base_path = os.path.dirname(os.path.abspath(__file__))

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
    EXPANDED_WIDTH = 300
    COLLAPSED_WIDTH = 68

    def __init__(self, theme: str = 'dark'):
        super().__init__()
        # 定义QT组件
        self.Serial_Info_Label = None
        self.connect_label = None
        self.widget_items = None
        self.widgetlib_scroll = None
        self.Icons_Normal = None
        self.Protocol_layout = None
        self.Protocol_widget = None
        self.port_layout = None
        self.port_widget = None
        self.Search_Input = None
        self.Widget_Libary_Layout = None
        self.Widget_Library = None
        self.Tab = None
        self.Icons_Active = None
        self.scroll_layout = None
        self.search_layout = None
        self.search_Widget = None
        self.Icon_Base_Path = None
        self.theme = theme
        self.is_collapsed = False

        self.setFixedWidth(self.EXPANDED_WIDTH)
        self._setup_ui()
        self._setup_animation()
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

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

    def TabBar_onChanged(self,index):
        for i in range(self.Tab.count()):
            print(i)
            if i == index:
                icon_path = self.Icon_Base_Path + self.Icons_Active[i]
            else:
                icon_path = self.Icon_Base_Path + self.Icons_Normal[i]
            self.Tab.tabBar().setTabIcon(i,QIcon(icon_path))

    def _setup_ui(self):
        """设置UI"""

        # 创建整个部件的布局样式
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Header部分
        self.header_widget = QWidget(self)
        self.header_layout = QHBoxLayout(self.header_widget)
        self.header_layout.setContentsMargins(0, 14, 0, 14)

        # 获取资源绝对路径
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "../../Image_Src/Icon/Left_Side/Widget_Active.png")
        print(icon_path)
        # 创建ICON
        self.Icon_Label = QLabel(self.header_widget)
        self.Icon_Label.setPixmap(QPixmap(icon_path))
        self.Icon_Label.setFixedSize(16,16)
        self.Icon_Label.setScaledContents(True)
        self.Icon_Label.setProperty("Icon_Label",True)
        self.Icon_Label.move(16,20)


        # Header Text
        self.header_text = QLabel(self.header_widget)
        self.header_text.setText("Widget Libary")
        self.header_text.setFont(QFont('Arimo', 14))
        self.header_text.setContentsMargins(40,0,0,0)

        # Header Btn
        self.header_fold_btn = QPushButton(self.header_widget)
        # 获取资源的绝对位置
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "../../Image_Src/Icon/Left_Side/Fold.png")
        # 创建ICON
        Icon = QIcon(icon_path)
        self.header_fold_btn.setIcon(Icon)
        self.header_fold_btn.setIconSize(QSize(24, 24))
        self.header_fold_btn.setFixedSize(30, 30)
        self.header_fold_btn.setStyleSheet(
            """
                QPushButton
                {
                    background-color: transparent;
                    margin-right: 20px;
                }
            """
        )
        self.header_fold_btn.clicked.connect(self.collapse)

        # 添加页面标签到head layout
        self.header_layout.addWidget(self.header_text)
        self.header_layout.addWidget(self.header_fold_btn)
        # 添加head widget到main layout
        self.main_layout.addWidget(self.header_widget)

        # 初始化TabBar
        self.setup_sidebar()
        # 初始化widgetlibrary
        self.Setup_Widget_Library()
        # 初始化port页面
        self.setup_port()





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
        # self.title_label.hide()

        # 隐藏搜索框
        # self.sear.hide()

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

    def setup_sidebar(self):
        # Tab部分
        # 创建 Widget_Libary的widget
        self.Widget_Library = QWidget()
        # 创建Widget_Libary的layout
        self.Widget_Libary_Layout = QVBoxLayout(self.Widget_Library)
        self.Widget_Libary_Layout.setContentsMargins(16, 6, 0, 0)

        # 创建Port视图的widget
        self.port_widget = QWidget()
        self.port_layout = QVBoxLayout(self.port_widget)

        # 创建 Protocol视图的Widget
        self.Protocol_widget = QWidget()
        self.Protocol_layout = QVBoxLayout(self.Protocol_widget)

        # TabBar
        self.Tab = QTabWidget(self)
        self.Icon_Base_Path = base_path + "/../../Image_Src/Icon/Left_Side/"
        self.Icons_Normal = ["Widget_Normal.png", "Port_Normal.png", "Protocol_Normal.png"]
        self.Icons_Active = ["Widget_Active.png", "Port_Active.png", "Protocol_Active.png"]
        icon = QIcon()
        # 添加Widget Tabbar Icon
        icon_path = os.path.join(base_path, "../../Image_Src/Icon/Left_Side/Widget_Active.png")
        icon.addPixmap(QPixmap(icon_path))
        self.Tab.addTab(self.Widget_Library, icon, "Widget")

        # 添加Port Tabbar Icon
        icon = QIcon()
        icon_path = os.path.join(base_path, "../../Image_Src/Icon/Left_Side/Port_Normal.png")
        icon.addPixmap(QPixmap(icon_path))
        icon.addPixmap(QPixmap(icon_path), QIcon.Mode.Selected, QIcon.State.On)

        self.Tab.addTab(self.port_widget, icon, "Port")

        # 添加Protocol Tabbar Icon
        icon = QIcon()
        icon_path = os.path.join(base_path, "../../Image_Src/Icon/Left_Side/Protocol_Normal.png")
        icon.addPixmap(QPixmap(icon_path))
        self.Tab.addTab(self.Protocol_widget, icon, "Protocol")

        # 设置样式
        self.Tab.setTabPosition(QTabWidget.TabPosition.North)  # 标签在顶部
        self.Tab.tabBar().setExpanding(True)  # 标签横向填充
        self.Tab.setFixedWidth(self.EXPANDED_WIDTH)
        self.Tab.tabBar().setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        # 分配三个Tab的大小
        self.Tab.tabBar().setFixedWidth(300)
        # 添加CSS样式使标签贴顶并填充
        self.Tab.setStyleSheet("""
            background-color: transparent;
            QTabWidget::pane {
                border: none;
                top: 0px;
                margin-top: 0px;
            }
            QTabWidget::tab-bar {
                background-color: transparent;
                left: -10px;


            }
            QTabBar::tab {
                background-color: #2A2A2A;
                color: #999999;
                margin: 0px;

                border: none;
                border-bottom: 2px solid #3A3A3A;
            }
            QTabBar::tab:selected {
                background-color: #1A1A1A;
                color: #0A84FF;
                border-bottom: 2px solid #0A84FF;
            }
            QTabBar::tab:hover {
                background-color: #333333;
            }
        """)
        self.main_layout.addWidget(self.Tab)
        self.Tab.currentChanged.connect(self.TabBar_onChanged)
    def Setup_Widget_Library(self):
        # Widget Tab 样式
        # SearchBar
        self.search_Widget = QWidget(self.Widget_Library)
        self.search_Widget.setFixedHeight(36)
        self.search_Widget.setContentsMargins(0, 0, 0, 0)
        self.search_layout = QHBoxLayout(self.search_Widget)
        self.search_layout.setContentsMargins(0, 0, 0, 0)
        # Search Icon
        self.Search_Input = QLineEdit(self.search_Widget)
        self.Search_Input.setPlaceholderText("Search Widget")
        icon_path = os.path.join(base_path, "../../Image_Src/Icon/Left_Side/Search.png")
        icon = QIcon(icon_path)
        self.Search_Input.addAction(icon, QLineEdit.ActionPosition.LeadingPosition)
        self.search_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        self.search_layout.addWidget(self.Search_Input)
        # 滚动区域
        self.widgetlib_scroll = QScrollArea(self.Widget_Library)
        self.widgetlib_scroll.setWidgetResizable(True)
        self.widgetlib_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.widgetlib_scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.widgetlib_scroll.setAutoFillBackground(True)
        self.widgetlib_scroll.setStyleSheet("background-color: transparent;")
        self.widgetlib_scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(scroll_content)
        self.scroll_layout.setSpacing(0)
        self.main_layout.addWidget(self.widgetlib_scroll)
        self.Widget_Libary_Layout.addWidget(self.search_Widget)
        self.Widget_Libary_Layout.addWidget(self.widgetlib_scroll)
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


        self.widgetlib_scroll.setWidget(scroll_content)

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

        self.Widget_Library.setStyleSheet("""
            QWidget 
            {
                background-color: transparent;
            }
            QScrollArea
            {
                background-color: transparent;
            }
        """)

    def setup_port(self):
        # 设置整体页面layout对齐模式
        self.port_layout.setContentsMargins(0, 0, 16, 0)
        self.port_layout.setSpacing(0)
        self.port_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 创建一个新的外部容器存储这个connect_status
        



        # 初始化链接状态部件
        self.connect_status = QWidget()
        self.connect_status.setObjectName("ConnectStatus")
        self.connect_status.setMinimumWidth(200)
        self.connect_status.setFixedHeight(78)  # 减小高度
        # self.connect_status.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # 初始化链接状态部件垂直布局
        connect_widget_layout = QVBoxLayout(self.connect_status)
        connect_widget_layout.setContentsMargins(17, 0, 17, 0)
        connect_widget_layout.setSpacing(0)  # 设置间距为0
        # 初始化链接状态链接label
        self.connect_label = QLabel("Unconnected")
        self.connect_label.setFont(QFont("Arial", 14))
        connect_widget_layout.addWidget(self.connect_label)

        # 串口信息Label
        self.Serial_Info_Label = QLabel("COM3 @115200 Baund")
        self.Serial_Info_Label.setFont(QFont("Arial", 12))
        self.Serial_Info_Label.setStyleSheet("""
            QLabel
            {
                color: rgb(153, 161, 175);
            }
        """)
        self.connect_status.setStyleSheet("""
        #ConnectStatus {
            background-color: rgba(12, 40, 25, 0.85);   /* 深绿色、轻微透明 */
            border: 2px solid rgba(48, 209, 88, 0.35);  /* 内发光风格绿色边框 */
            border-radius: 10px;                        /* 大圆角 */
            padding: 8px;                               /* 减小内间距 */
        }

        #ConnectStatus QLabel {
            background: transparent;                    /* 防止 QLabel 继承背景 */
        }
        """)
        connect_widget_layout.addWidget(self.connect_label)
        connect_widget_layout.addWidget(self.Serial_Info_Label)
        connect_widget_layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)
        connect_widget_layout.setContentsMargins(10, 0, 0, 0)  # 减小边距
        # 使 connect_status 在 port_widget 中垂直居中并水平居中
        # self.port_layout.addStretch()
        self.port_layout.addWidget(self.connect_status, 0, Qt.AlignmentFlag.AlignHCenter)
        # self.port_layout.addStretch()
        # ####################################################################
        # #                           初始化选项
        # ####################################################################
        #
        # # 创建滚动区域
        # scroll = QScrollArea(self.port_widget)
        # scroll.setWidgetResizable(True)
        # scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # scroll.setFrameShape(QFrame.Shape.NoFrame)
        # scroll.setAutoFillBackground(True)
        # scroll.setStyleSheet("background-color: transparent;")
        # scroll.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        # scroll.setContentsMargins(0, 0, 0, 0)
        #
        # # 创建 Combos 容器
        # self.Combos = QWidget()
        # Combos_layout = QVBoxLayout(self.Combos)
        # self.Combos.setContentsMargins(0, 0, 0, 0)  # 合适的边距
        # Combos_layout.setSpacing(8)  # 控件之间的间距
        #
        # # Serial Port 选择器
        # Combo_Container = QWidget()
        # Combo_Container.setStyleSheet(" border-radius: 6px;")
        # Combo_Container_layout = QVBoxLayout(Combo_Container)
        # Combo_Container_layout.setContentsMargins(8, 8, 8, 8)
        # Combo_Container_layout.setSpacing(4)
        #
        # Label = QLabel("Serial Port")
        # Label.setStyleSheet("color: white; font-weight: bold;")
        # self.Serial_Selector = QComboBox()
        # self.Serial_Selector.addItem("COM3 @115200 Bund")
        # self.Serial_Selector.addItem("COM4 @115200 Bund")
        # self.Serial_Selector.setStyleSheet("""
        #     QComboBox {
        #         color: white;
        #         border: 1px solid #5D5D5D;
        #         border-radius: 4px;
        #         padding: 4px;
        #     }
        #     QComboBox::drop-down {
        #         border: none;
        #     }
        # """)
        #
        # Combo_Container_layout.addWidget(Label)
        # Combo_Container_layout.addWidget(self.Serial_Selector)
        # Combos_layout.addWidget(Combo_Container)
        #
        # # Baud Rate 选择器
        # Combo_Container = QWidget()
        # Combo_Container.setStyleSheet(" border-radius: 6px;")
        # Combo_Container_layout = QVBoxLayout(Combo_Container)
        # Combo_Container_layout.setContentsMargins(8, 8, 8, 8)
        # Combo_Container_layout.setSpacing(4)
        #
        # Label = QLabel("Baud Rate")
        # Label.setStyleSheet("color: white; font-weight: bold;")
        # self.BaundRate_Selector = QComboBox()
        # self.BaundRate_Selector.addItem("9600")
        # self.BaundRate_Selector.addItem("115200")
        # self.BaundRate_Selector.setStyleSheet("""
        #     QComboBox {
        #         color: white;
        #         border: 1px solid #5D5D5D;
        #         border-radius: 4px;
        #         padding: 4px;
        #     }
        #     QComboBox::drop-down {
        #         border: none;
        #     }
        # """)
        #
        # Combo_Container_layout.addWidget(Label)
        # Combo_Container_layout.addWidget(self.BaundRate_Selector)
        # Combos_layout.addWidget(Combo_Container)
        #
        # # Data Bits 选择器
        # Combo_Container = QWidget()
        # Combo_Container.setStyleSheet(" border-radius: 6px;")
        # Combo_Container_layout = QVBoxLayout(Combo_Container)
        # Combo_Container_layout.setContentsMargins(8, 8, 8, 8)
        # Combo_Container_layout.setSpacing(4)
        #
        # Label = QLabel("Data Bits")
        # Label.setStyleSheet("color: white; font-weight: bold;")
        # self.DataBits_Selector = QComboBox()
        # self.DataBits_Selector.addItem("8")
        # self.DataBits_Selector.addItem("7")
        # self.DataBits_Selector.setStyleSheet("""
        #     QComboBox {
        #         color: white;
        #         border: 1px solid #5D5D5D;
        #         border-radius: 4px;
        #         padding: 4px;
        #     }
        #     QComboBox::drop-down {
        #         border: none;
        #     }
        # """)
        #
        # Combo_Container_layout.addWidget(Label)
        # Combo_Container_layout.addWidget(self.DataBits_Selector)
        # Combos_layout.addWidget(Combo_Container)
        #
        # # Parity 选择器
        # Combo_Container = QWidget()
        # Combo_Container.setStyleSheet(" border-radius: 6px;")
        # Combo_Container_layout = QVBoxLayout(Combo_Container)
        # Combo_Container_layout.setContentsMargins(8, 8, 8, 8)
        # Combo_Container_layout.setSpacing(4)
        #
        # Label = QLabel("Parity")
        # Label.setStyleSheet("color: white; font-weight: bold;")
        # self.Parity_Selector = QComboBox()
        # self.Parity_Selector.addItem("None")
        # self.Parity_Selector.addItem("Odd")
        # self.Parity_Selector.addItem("Even")
        # self.Parity_Selector.setStyleSheet("""
        #     QComboBox {
        #
        #         color: white;
        #         border: 1px solid #5D5D5D;
        #         border-radius: 4px;
        #         padding: 4px;
        #     }
        #     QComboBox::drop-down {
        #         border: none;
        #     }
        # """)
        #
        # Combo_Container_layout.addWidget(Label)
        # Combo_Container_layout.addWidget(self.Parity_Selector)
        # Combos_layout.addWidget(Combo_Container)
        #
        # # Stop Bits 选择器
        # Combo_Container = QWidget()
        # Combo_Container.setStyleSheet("backgrborder-radius: 6px;")
        # Combo_Container_layout = QVBoxLayout(Combo_Container)
        # Combo_Container_layout.setContentsMargins(8, 8, 8, 8)
        # Combo_Container_layout.setSpacing(4)
        #
        # Label = QLabel("Stop Bits")
        # Label.setStyleSheet("color: white; font-weight: bold;")
        # self.StopBits_Selector = QComboBox()
        # self.StopBits_Selector.addItem("1")
        # self.StopBits_Selector.addItem("2")
        # self.StopBits_Selector.setStyleSheet("""
        #     QComboBox {
        #         color: white;
        #         border: 1px solid #5D5D5D;
        #         border-radius: 4px;
        #         padding: 4px;
        #     }
        #     QComboBox::drop-down {
        #         border: none;
        #     }
        # """)
        #
        # Combo_Container_layout.addWidget(Label)
        # Combo_Container_layout.addWidget(self.StopBits_Selector)
        # Combos_layout.addWidget(Combo_Container)
        #
        # # 添加伸展空间以防止控件被拉伸
        # Combos_layout.addStretch()
        #
        # # 将 Combos 设置为滚动区域的 widget
        # scroll.setWidget(self.Combos)
        #
        # # 将滚动区域添加到 port_layout
        # self.port_layout.addWidget(scroll)