"""
WidgetItem - 画布上的 Widget 容器
负责拖拽、调整大小、选中状态管理
"""

from PyQt6.QtWidgets import QGraphicsProxyWidget, QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, pyqtSignal, QRectF, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QCursor
from typing import Dict, Any

from ..widgets.oscilloscope import OscilloscopeWidget
from ..widgets.terminal import TerminalWidget
from ..widgets.hex_viewer import HexViewerWidget
from ..widgets.gauge import GaugeWidget
from ..widgets.data_table import DataTableWidget
from ..widgets.packet_analyzer import PacketAnalyzerWidget
from ..widgets.chart import ChartWidget


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
        # 创建容器
        container = QFrame()
        container.setStyleSheet(f"""
            QFrame {{
                background-color: {'#252525' if self.theme == 'dark' else '#FFFFFF'};
                border: 2px solid {'#3A3A3A' if self.theme == 'dark' else '#E0E0E0'};
                border-radius: 8px;
            }}
        """)

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 标题栏
        title_bar = QWidget()
        title_bar.setStyleSheet(f"""
            background-color: {'#1A1A1A' if self.theme == 'dark' else '#F5F5F5'};
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            padding: 8px 12px;
        """)
        title_layout = QVBoxLayout(title_bar)
        title_layout.setContentsMargins(8, 6, 8, 6)

        title_label = QLabel(self.widget_data['title'])
        title_label.setStyleSheet(f"""
            color: {'#FFFFFF' if self.theme == 'dark' else '#000000'};
            font-weight: 600;
            font-size: 13px;
        """)
        title_layout.addWidget(title_label)

        layout.addWidget(title_bar)

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

        layout.addWidget(self.content_widget, 1)

        # 设置容器尺寸
        container.setFixedSize(
            self.widget_data['width'],
            self.widget_data['height']
        )

        # 设置代理
        self.setWidget(container)

    def set_selected(self, selected: bool):
        """设置选中状态"""
        self.is_selected = selected
        self.update()

        # 更新边框样式
        if hasattr(self, 'widget') and self.widget():
            container = self.widget()
            if selected:
                container.setStyleSheet(f"""
                    QFrame {{
                        background-color: {'#252525' if self.theme == 'dark' else '#FFFFFF'};
                        border: 2px solid #0A84FF;
                        border-radius: 8px;
                    }}
                """)
            else:
                container.setStyleSheet(f"""
                    QFrame {{
                        background-color: {'#252525' if self.theme == 'dark' else '#FFFFFF'};
                        border: 2px solid {'#3A3A3A' if self.theme == 'dark' else '#E0E0E0'};
                        border-radius: 8px;
                    }}
                """)

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
            title_bar = self.widget().findChild(QWidget)
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
