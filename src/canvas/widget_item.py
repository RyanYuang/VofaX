"""
WidgetItem - 画布上的 Widget 容器
负责拖拽、调整大小、选中状态管理
"""

from PyQt6.QtWidgets import (
    QGraphicsProxyWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF, QEvent
from PyQt6.QtGui import QPainter, QPen, QColor, QCursor
from typing import Dict, Any

from ..widgets.oscilloscope import OscilloscopeWidget
from ..widgets.terminal import TerminalWidget
from ..widgets.hex_viewer import HexViewerWidget
from ..widgets.gauge import GaugeWidget
from ..widgets.data_table import DataTableWidget
from ..widgets.packet_analyzer import PacketAnalyzerWidget
from ..widgets.chart import ChartWidget


class DraggableContainer(QFrame):
    """可拖拽的容器 - 在标题栏区域转发鼠标事件到 QGraphicsProxyWidget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.proxy_widget = None  # 将在 WidgetItem 中设置
        self.title_bar_height = 40  # 标题栏高度
        self.is_dragging = False
        self.drag_start_pos = None

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否在标题栏区域
            if event.pos().y() <= self.title_bar_height:
                # 在标题栏区域，开始拖拽
                self.is_dragging = True
                self.drag_start_pos = event.pos()

                # 通知 proxy widget 被选中
                if self.proxy_widget:
                    self.proxy_widget.selected.emit(self.proxy_widget)
                    self.proxy_widget.drag_opacity = 0.5
                    self.proxy_widget.update()

                event.accept()
                return

        # 不在标题栏区域，传递给子 widget
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_dragging and (event.buttons() & Qt.MouseButton.LeftButton):
            if self.proxy_widget and self.drag_start_pos:
                # 计算移动距离
                delta = event.pos() - self.drag_start_pos

                # 移动 proxy widget
                new_pos = self.proxy_widget.pos() + QPointF(delta.x(), delta.y())
                self.proxy_widget.setPos(new_pos)

                # 更新数据
                self.proxy_widget.widget_data['x'] = new_pos.x()
                self.proxy_widget.widget_data['y'] = new_pos.y()

                event.accept()
                return
        elif self.is_dragging:
            # 鼠标按钮已经释放，结束拖拽
            self._end_drag()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            if self.is_dragging:
                self._end_drag()
                event.accept()
                return

        super().mouseReleaseEvent(event)

    def _end_drag(self):
        """结束拖拽"""
        self.is_dragging = False
        self.drag_start_pos = None

        # 恢复透明度
        if self.proxy_widget:
            self.proxy_widget.drag_opacity = 1.0
            self.proxy_widget.update()


class WidgetItem(QGraphicsProxyWidget):
    """Widget 容器图形项"""

    selected = pyqtSignal(object)  # 选中信号
    geometry_changed = pyqtSignal(object)  # 几何变更信号

    RESIZE_HANDLE_SIZE = 8  # 调整大小手柄尺寸 (8x8px)
    SELECTION_BORDER_WIDTH = 2  # 选中边框宽度
    SELECTION_COLOR = QColor(10, 132, 255)  # 选中颜色 #0A84FF

    def __init__(self, widget_data: Dict, theme: str, channel_manager):
        super().__init__()

        self.widget_data = widget_data
        self.theme = theme
        self.channel_manager = channel_manager
        self.is_selected = False
        self.resize_mode = None  # None, 'nw', 'n', 'ne', 'e', 'se', 's', 'sw', 'w'
        self.drag_opacity = 1.0  # 拖拽透明度

        # 设置标志
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsMovable, True)
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsSelectable, True)
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.setAcceptHoverEvents(True)

        # 创建 Widget
        self._create_widget()

        # 设置位置和大小
        self.setPos(widget_data['x'], widget_data['y'])

    def _create_widget(self):
        """根据类型创建 Widget"""
        # 创建容器（使用自定义的可拖拽容器）
        container = DraggableContainer()
        container.proxy_widget = self  # 设置 proxy widget 引用
        container.setObjectName("widgetContainer")

        # 设置基础样式
        self._update_container_style(container, selected=False)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏（带拖拽手柄）
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(40)
        # 设置鼠标跟踪以支持拖拽
        title_bar.setMouseTracking(True)
        title_bar.setStyleSheet(f"""
            QWidget#titleBar {{
                background-color: {'#2A2A2A' if self.theme == 'dark' else '#F9FAFB'};
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom: 1px solid {'#3A3A3A' if self.theme == 'dark' else '#E5E7EB'};
            }}
        """)
        # 存储引用以便后续使用
        self.title_bar = title_bar

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(12, 8, 12, 8)
        title_layout.setSpacing(8)

        # 拖拽手柄图标 (GripVertical)
        grip_icon = self._create_grip_icon()
        title_layout.addWidget(grip_icon)

        # 标题文字
        title_label = QLabel(self.widget_data['title'])
        title_label.setStyleSheet(f"""
            color: {'#E5E7EB' if self.theme == 'dark' else '#1F2937'};
            font-weight: 500;
            font-size: 14px;
        """)
        title_layout.addWidget(title_label)

        title_layout.addStretch()

        layout.addWidget(title_bar, 0)

        # 实际 Widget 内容
        widget_type = self.widget_data['type']
        widget_class_map = {
            'oscilloscope': OscilloscopeWidget,
            'terminal': TerminalWidget,
            'hex-viewer': HexViewerWidget,
            'gauge': GaugeWidget,
            'data-table': DataTableWidget,
            'packet-analyzer': PacketAnalyzerWidget,
            'chart': ChartWidget,
        }

        widget_class = widget_class_map.get(widget_type)
        if widget_class:
            self.content_widget = widget_class(
                self.widget_data,
                self.theme,
                self.channel_manager
            )
        else:
            # 默认占位符
            self.content_widget = QLabel(f"Widget: {widget_type}")
            self.content_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ← 确保内容 Widget 可见
        self.content_widget.setMinimumHeight(100)
        
        # ← 关键修复：强制显示 content_widget
        self.content_widget.setVisible(True)
        self.content_widget.show()
        
        layout.addWidget(self.content_widget, 1)
        

        # 设置容器尺寸
        container.setFixedSize(
            self.widget_data['width'],
            self.widget_data['height']
        )
        
        # ← 容器需要最小高度，否则layout会被压缩
        container.setMinimumHeight(150)

        # 注意：不添加阴影效果，因为 QGraphicsDropShadowEffect 在 QGraphicsProxyWidget 上
        # 会导致内容不可见（Qt 已知问题）
        # self._add_shadow_effect(container)
        
        # 设置代理
        self.setWidget(container)
        
        # 强制显示所有内容（确保可见性）
        container.setVisible(True)
        container.show()
        self.setVisible(True)
        self.show()
        
        # 禁用缓存以避免渲染问题
        from PyQt6.QtWidgets import QGraphicsItem
        self.setCacheMode(QGraphicsItem.CacheMode.NoCache)

    def _create_grip_icon(self):
        """创建拖拽手柄图标 (GripVertical)"""
        grip = QLabel()
        grip.setFixedSize(16, 16)

        # 使用样式绘制两列圆点
        grip.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                qproperty-text: "⋮⋮";
                color: {'#6B7280' if self.theme == 'dark' else '#9CA3AF'};
                font-size: 12px;
                font-weight: bold;
                letter-spacing: -2px;
            }}
        """)

        grip.setText("⋮⋮")
        grip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        grip.setCursor(Qt.CursorShape.SizeAllCursor)

        return grip

    def _update_container_style(self, container: QFrame, selected: bool = False):
        """更新容器样式"""
        if selected:
            # 选中状态：蓝色边框
            border_color = "#0A84FF"
            border_width = 2
        else:
            # 未选中状态：灰色边框
            if self.theme == 'dark':
                border_color = "#3A3A3A"
            else:
                border_color = "#E5E7EB"
            border_width = 1

        bg_color = '#1E1E1E' if self.theme == 'dark' else '#FFFFFF'

        container.setStyleSheet(f"""
            QFrame#widgetContainer {{
                background-color: {bg_color};
                border: {border_width}px solid {border_color};
                border-radius: 8px;
            }}
        """)

    def _add_shadow_effect(self, widget: QWidget):
        """为 Widget 添加阴影效果"""
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(12)
        shadow.setColor(QColor(0, 0, 0, int(38 * 0.15)))  # 15% 透明度
        shadow.setOffset(0, 4)  # 垂直偏移 4px
        widget.setGraphicsEffect(shadow)

    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.is_selected = selected
        self.update()

        # 更新边框样式
        if hasattr(self, 'widget') and self.widget():
            container = self.widget()
            self._update_container_style(container, selected=selected)

    def update_widget(self, updates: Dict[str, Any]):
        """更新 Widget 数据"""
        self.widget_data.update(updates)

        # 更新位置和大小
        if 'x' in updates or 'y' in updates:
            self.setPos(
                updates.get('x', self.widget_data['x']),
                updates.get('y', self.widget_data['y'])
            )

        if 'width' in updates or 'height' in updates:
            if self.widget():
                self.widget().setFixedSize(
                    updates.get('width', self.widget_data['width']),
                    updates.get('height', self.widget_data['height'])
                )

        # 更新标题
        if 'title' in updates and self.widget():
            title_bar = self.widget().findChild(QWidget, "titleBar")
            if title_bar:
                title_label = title_bar.findChild(QLabel)
                if title_label:
                    title_label.setText(updates['title'])

        # 通知内容 Widget 更新
        if hasattr(self.content_widget, 'update_config'):
            self.content_widget.update_config(self.widget_data)

    def set_theme(self, theme: str):
        """设置主题"""
        self.theme = theme
        # 重新创建 Widget 以应用新主题
        old_widget = self.widget()
        self._create_widget()
        if old_widget:
            old_widget.deleteLater()

    def paint(self, painter: QPainter, option, widget):
        """绘制 Widget（添加选中效果和调整大小手柄）"""
        # 设置透明度
        painter.setOpacity(self.drag_opacity)

        super().paint(painter, option, widget)

        if self.is_selected:
            rect = self.boundingRect()

            # 绘制选中边框外框（2px 蓝色 ring + shadow）
            painter.save()
            painter.setOpacity(1.0)  # 边框不透明

            # 绘制阴影效果
            shadow_pen = QPen(QColor(10, 132, 255, 51))  # 20% 透明度
            shadow_pen.setWidth(6)
            painter.setPen(shadow_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRoundedRect(rect.adjusted(-3, -3, 3, 3), 10, 10)

            painter.restore()

            # 绘制 8 个调整手柄（8x8px 白色方块）
            painter.save()
            painter.setOpacity(1.0)

            handle_size = self.RESIZE_HANDLE_SIZE
            half_size = handle_size / 2

            handles = [
                ('nw', rect.left() - half_size, rect.top() - half_size),           # 左上
                ('n',  rect.center().x() - half_size, rect.top() - half_size),     # 上中
                ('ne', rect.right() - half_size, rect.top() - half_size),          # 右上
                ('e',  rect.right() - half_size, rect.center().y() - half_size),   # 右中
                ('se', rect.right() - half_size, rect.bottom() - half_size),       # 右下
                ('s',  rect.center().x() - half_size, rect.bottom() - half_size),  # 下中
                ('sw', rect.left() - half_size, rect.bottom() - half_size),        # 左下
                ('w',  rect.left() - half_size, rect.center().y() - half_size),    # 左中
            ]

            for handle_id, x, y in handles:
                handle_rect = QRectF(x, y, handle_size, handle_size)

                # 白色方块 + 蓝色边框
                painter.setBrush(QColor(255, 255, 255))
                painter.setPen(QPen(self.SELECTION_COLOR, 1.5))
                painter.drawRect(handle_rect)

            painter.restore()

    def _get_handle_at_pos(self, pos: QPointF) -> str:
        """获取鼠标位置对应的调整手柄"""
        if not self.is_selected:
            return None

        rect = self.boundingRect()
        handle_size = self.RESIZE_HANDLE_SIZE
        half_size = handle_size / 2

        handles = [
            ('nw', rect.left() - half_size, rect.top() - half_size),
            ('n',  rect.center().x() - half_size, rect.top() - half_size),
            ('ne', rect.right() - half_size, rect.top() - half_size),
            ('e',  rect.right() - half_size, rect.center().y() - half_size),
            ('se', rect.right() - half_size, rect.bottom() - half_size),
            ('s',  rect.center().x() - half_size, rect.bottom() - half_size),
            ('sw', rect.left() - half_size, rect.bottom() - half_size),
            ('w',  rect.left() - half_size, rect.center().y() - half_size),
        ]

        for handle_id, x, y in handles:
            handle_rect = QRectF(x, y, handle_size, handle_size)
            if handle_rect.contains(pos):
                return handle_id

        return None

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否点击了调整大小手柄
            handle = self._get_handle_at_pos(event.pos())
            if handle:
                self.resize_mode = handle
                self.resize_start_pos = event.pos()
                self.resize_start_rect = self.boundingRect()
                event.accept()
                return

            # 开始拖拽 - 设置半透明
            self.drag_opacity = 0.5
            self.update()

            # 发射选中信号
            self.selected.emit(self)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.resize_mode:
            # 调整大小逻辑
            delta = event.pos() - self.resize_start_pos
            rect = self.resize_start_rect
            new_x, new_y = self.pos().x(), self.pos().y()
            new_width = int(rect.width())
            new_height = int(rect.height())

            # 根据不同手柄调整大小和位置
            if 'n' in self.resize_mode:  # 上边
                new_height = max(150, int(rect.height() - delta.y()))
                new_y = self.pos().y() + (rect.height() - new_height)
            if 's' in self.resize_mode:  # 下边
                new_height = max(150, int(rect.height() + delta.y()))
            if 'w' in self.resize_mode:  # 左边
                new_width = max(200, int(rect.width() - delta.x()))
                new_x = self.pos().x() + (rect.width() - new_width)
            if 'e' in self.resize_mode:  # 右边
                new_width = max(200, int(rect.width() + delta.x()))

            # 更新位置和大小
            if new_x != self.pos().x() or new_y != self.pos().y():
                self.setPos(new_x, new_y)
                self.widget_data['x'] = new_x
                self.widget_data['y'] = new_y

            if self.widget():
                self.widget().setFixedSize(new_width, new_height)
                self.widget_data['width'] = new_width
                self.widget_data['height'] = new_height

            self.update()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        # 恢复不透明
        self.drag_opacity = 1.0
        self.update()

        if self.resize_mode:
            self.resize_mode = None
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def itemChange(self, change, value):
        """Item 变更事件"""
        if change == QGraphicsProxyWidget.GraphicsItemChange.ItemPositionChange:
            # 更新位置数据
            new_pos = value
            self.widget_data['x'] = new_pos.x()
            self.widget_data['y'] = new_pos.y()
            self.geometry_changed.emit(self)

        return super().itemChange(change, value)

    def hoverMoveEvent(self, event):
        """鼠标悬停移动 - 更新光标"""
        if self.is_selected:
            handle = self._get_handle_at_pos(event.pos())
            if handle:
                # 根据手柄位置设置光标
                cursor_map = {
                    'nw': Qt.CursorShape.SizeFDiagCursor,  # ↖↘
                    'ne': Qt.CursorShape.SizeBDiagCursor,  # ↗↙
                    'sw': Qt.CursorShape.SizeBDiagCursor,  # ↙↗
                    'se': Qt.CursorShape.SizeFDiagCursor,  # ↘↖
                    'n':  Qt.CursorShape.SizeVerCursor,    # ↕
                    's':  Qt.CursorShape.SizeVerCursor,    # ↕
                    'w':  Qt.CursorShape.SizeHorCursor,    # ↔
                    'e':  Qt.CursorShape.SizeHorCursor,    # ↔
                }
                self.setCursor(QCursor(cursor_map.get(handle, Qt.CursorShape.ArrowCursor)))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
        else:
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))

        super().hoverMoveEvent(event)
