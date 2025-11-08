"""
WidgetItem - 画布上的 Widget 容器
负责拖拽、调整大小、选中状态管理
"""

from PyQt6.QtWidgets import (
    QGraphicsProxyWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QFrame, QGraphicsDropShadowEffect, QPushButton, QApplication
)
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


class DraggableContainer(QFrame):
    """可拖拽的容器 - 在标题栏区域转发鼠标事件到 QGraphicsProxyWidget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.proxy_widget = None  # 将在 WidgetItem 中设置
        self.title_bar_height = 48  # 标题栏高度（增大到 48px）
        self.is_dragging = False
        self.drag_start_pos = None

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 优先检查是否点击了调整大小手柄（通过 proxy_widget 检查）
            if self.proxy_widget:
                # 转换 QPoint 到 QPointF
                pos_f = QPointF(event.pos())
                handle = self.proxy_widget._get_handle_at_pos(pos_f)
                if handle:
                    # 点击了调整手柄，不拦截事件，让 WidgetItem 处理
                    print(f"点击了调整手柄: {handle}")
                    super().mousePressEvent(event)
                    return

            # 检查是否锁定
            if self.proxy_widget and self.proxy_widget.is_locked:
                # 锁定状态下不允许拖拽，但仍然传递选中事件
                if self.proxy_widget:
                    self.proxy_widget.selected.emit(self.proxy_widget)
                super().mousePressEvent(event)
                return

            # 检查是否在标题栏区域的可移动区域（扩大范围：整个标题栏左侧区域）
            # 拖拽区域：X: 8-120px, Y: 8-48px (增大范围)
            if (event.pos().y() <= self.title_bar_height and event.pos().y() >= 8 and
                event.pos().x() <= 120 and event.pos().x() >= 8):
                print("点击了可移动区域")
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

                # 计算原始新位置
                original_new_pos = self.proxy_widget.pos() + QPointF(delta.x(), delta.y())

                # 获取 GraphicsView 和其他 widgets
                scene = self.proxy_widget.scene()
                if scene and hasattr(scene, 'views') and scene.views():
                    view = scene.views()[0]

                    # 获取当前 widget 的矩形（在新位置）
                    current_rect = self.proxy_widget.boundingRect()
                    current_rect.moveTopLeft(original_new_pos)

                    # 收集其他 widgets 的矩形
                    other_rects = []
                    if hasattr(view, 'widget_items'):
                        for item in view.widget_items:
                            if item != self.proxy_widget:
                                item_rect = item.boundingRect()
                                item_rect.moveTopLeft(item.pos())
                                other_rects.append(item_rect)

                    # 应用智能对齐
                    if hasattr(view, 'snap_helper'):
                        snapped_pos, snap_lines = view.snap_helper.snap_position(
                            current_rect, other_rects, original_new_pos
                        )
                        new_pos = snapped_pos
                        view.snap_lines = snap_lines
                        view.viewport().update()  # 触发重绘以显示对齐线
                    else:
                        new_pos = original_new_pos
                else:
                    new_pos = original_new_pos

                # 移动 proxy widget
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

            # 清除对齐辅助线
            scene = self.proxy_widget.scene()
            if scene and hasattr(scene, 'views') and scene.views():
                view = scene.views()[0]
                if hasattr(view, 'snap_lines'):
                    view.snap_lines = []
                    view.viewport().update()


class WidgetItem(QGraphicsProxyWidget):
    """Widget 容器图形项"""

    selected = pyqtSignal(object)  # 选中信号
    geometry_changed = pyqtSignal(object)  # 几何变更信号

    RESIZE_HANDLE_SIZE = 10  # 调整大小手柄尺寸 (16x16px，放大以便点击)
    RESIZE_HANDLE_CLICK_PADDING = 10  # 手柄点击区域额外扩展像素 (增加到16px)
    RESIZE_HANDLE_INSET = 1  # 手柄内缩距离（从边界往内移动的像素）
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
        self.is_locked = False  # 锁定状态（不可移动/调整大小）
        self.current_cursor = None  # 当前设置的光标

        # 设置标志
        self.setFlag(QGraphicsProxyWidget.GraphicsItemFlag.ItemIsMovable, False)  # 禁用内置拖拽，使用自定义拖拽
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
        title_bar.setFixedHeight(48)  # 增大到 48px
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
        title_layout.setContentsMargins(12, 12, 12, 12)  # 增大 padding
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

        # 固定按钮（📌图钉图标）
        self.lock_btn = QPushButton("📌" if not self.is_locked else "🔒")
        self.lock_btn.setFixedSize(24, 24)
        self.lock_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.lock_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {'rgba(255, 255, 255, 0.1)' if self.theme == 'dark' else 'rgba(0, 0, 0, 0.05)'};
            }}
        """)
        self.lock_btn.clicked.connect(self._toggle_lock)
        self.lock_btn.setToolTip("Lock position" if not self.is_locked else "Unlock position")
        title_layout.addWidget(self.lock_btn)

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
        """创建拖拽手柄图标 (GripVertical) - 增大尺寸"""
        grip = QLabel()
        grip.setFixedSize(24, 24)  # 增大到 24x24

        # 使用样式绘制两列圆点
        grip.setStyleSheet(f"""
            QLabel {{
                background-color: transparent;
                qproperty-text: "⋮⋮";
                color: {'#6B7280' if self.theme == 'dark' else '#9CA3AF'};
                font-size: 18px;
                font-weight: bold;
                letter-spacing: -5px;
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

    def _toggle_lock(self):
        """切换锁定状态"""
        self.is_locked = not self.is_locked

        # 更新按钮图标和提示
        self.lock_btn.setText("🔒" if self.is_locked else "📌")
        self.lock_btn.setToolTip("Unlock position" if self.is_locked else "Lock position")

        # 锁定状态通过 DraggableContainer.mousePressEvent 和 _get_handle_at_pos 中的 is_locked 检查来控制
        # 不需要设置 ItemIsMovable，因为我们使用自定义拖拽

        # 更新拖拽手柄和调整大小手柄的可见性
        self.update()  # 触发重绘

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

        # 获取容器引用
        container = self.widget()
        if not container:
            # 如果没有容器，重新创建
            self._create_widget()
            return

        # 保存当前位置和大小
        current_pos = self.pos()
        current_width = self.widget_data['width']
        current_height = self.widget_data['height']

        # 更新容器样式
        self._update_container_style(container, selected=self.is_selected)

        # 更新标题栏样式
        title_bar = container.findChild(QWidget, "titleBar")
        if title_bar:
            title_bar.setStyleSheet(f"""
                QWidget#titleBar {{
                    background-color: {'#2A2A2A' if self.theme == 'dark' else '#F9FAFB'};
                    border-top-left-radius: 8px;
                    border-top-right-radius: 8px;
                    border-bottom: 1px solid {'#3A3A3A' if self.theme == 'dark' else '#E5E7EB'};
                }}
            """)

            # 更新标题文字颜色
            for label in title_bar.findChildren(QLabel):
                if label.text() == self.widget_data['title']:
                    label.setStyleSheet(f"""
                        color: {'#E5E7EB' if self.theme == 'dark' else '#1F2937'};
                        font-weight: 500;
                        font-size: 14px;
                    """)
                    break

            # 更新拖拽手柄颜色
            for label in title_bar.findChildren(QLabel):
                if label.text() == "⋮⋮":
                    label.setStyleSheet(f"""
                        QLabel {{
                            background-color: transparent;
                            qproperty-text: "⋮⋮";
                            color: {'#6B7280' if self.theme == 'dark' else '#9CA3AF'};
                            font-size: 12px;
                            font-weight: bold;
                            letter-spacing: -2px;
                        }}
                    """)
                    break

            # 更新锁定按钮样式
            for btn in title_bar.findChildren(QPushButton):
                if btn.text() in ["📌", "🔒"]:
                    btn.setStyleSheet(f"""
                        QPushButton {{
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            font-size: 14px;
                        }}
                        QPushButton:hover {{
                            background-color: {'rgba(255, 255, 255, 0.1)' if self.theme == 'dark' else 'rgba(0, 0, 0, 0.05)'};
                        }}
                    """)
                    self.lock_btn = btn  # 保存引用
                    break

        # 重新创建内容 widget（因为它们需要 theme 参数）
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
        if widget_class and self.content_widget:
            # 移除旧的内容 widget
            layout = container.layout()
            if layout:
                layout.removeWidget(self.content_widget)
                self.content_widget.deleteLater()

                # 创建新的内容 widget
                self.content_widget = widget_class(
                    self.widget_data,
                    self.theme,
                    self.channel_manager
                )
                self.content_widget.setMinimumHeight(100)
                self.content_widget.setVisible(True)
                self.content_widget.show()

                # 添加回布局（在标题栏之后）
                layout.addWidget(self.content_widget, 1)

        # 确保位置和大小保持不变
        self.setPos(current_pos)
        container.setFixedSize(current_width, current_height)

        # 触发重绘
        self.update()

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

            # 绘制 8 个调整手柄（仅在未锁定时）
            if not self.is_locked:
                painter.save()
                painter.setOpacity(1.0)

                handle_size = self.RESIZE_HANDLE_SIZE
                half_size = handle_size / 2
                inset = self.RESIZE_HANDLE_INSET  # 内缩距离

                # 手柄位置：从边界内缩 inset 像素
                handles = [
                    ('nw', rect.left() + inset, rect.top() + inset),                      # 左上
                    ('n',  rect.center().x() - half_size, rect.top() + inset),            # 上中
                    ('ne', rect.right() - handle_size - inset, rect.top() + inset),       # 右上
                    ('e',  rect.right() - handle_size - inset, rect.center().y() - half_size),  # 右中
                    ('se', rect.right() - handle_size - inset, rect.bottom() - handle_size - inset),  # 右下
                    ('s',  rect.center().x() - half_size, rect.bottom() - handle_size - inset),  # 下中
                    ('sw', rect.left() + inset, rect.bottom() - handle_size - inset),     # 左下
                    ('w',  rect.left() + inset, rect.center().y() - half_size),           # 左中
                ]

                # 启用抗锯齿
                painter.setRenderHint(QPainter.RenderHint.Antialiasing)

                for _, x, y in handles:
                    handle_rect = QRectF(x, y, handle_size, handle_size)

                    # 绘制阴影 (轻微模糊效果)
                    shadow_color = QColor(0, 0, 0, 40)
                    painter.setBrush(shadow_color)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawRoundedRect(handle_rect.adjusted(1, 1, 1, 1), 2, 2)

                    # 白色圆角方块
                    painter.setBrush(QColor(255, 255, 255))
                    painter.setPen(QPen(self.SELECTION_COLOR, 2))
                    painter.drawRoundedRect(handle_rect, 2, 2)

                painter.restore()

    def _get_handle_at_pos(self, pos: QPointF) -> str:
        """获取鼠标位置对应的调整手柄（带容错范围）"""
        if not self.is_selected or self.is_locked:
            return None

        # 获取 Widget 的矩形
        rect = self.boundingRect()
        handle_size = self.RESIZE_HANDLE_SIZE
        half_size = handle_size / 2
        inset = self.RESIZE_HANDLE_INSET  # 内缩距离
        # 增加点击区域的容错范围
        click_padding = self.RESIZE_HANDLE_CLICK_PADDING

        # 手柄位置：从边界内缩 inset 像素（与绘制位置一致）
        handles = [
            ('nw', rect.left() + inset, rect.top() + inset),
            ('n',  rect.center().x() - half_size, rect.top() + inset),
            ('ne', rect.right() - handle_size - inset, rect.top() + inset),
            ('e',  rect.right() - handle_size - inset, rect.center().y() - half_size),
            ('se', rect.right() - handle_size - inset, rect.bottom() - handle_size - inset),
            ('s',  rect.center().x() - half_size, rect.bottom() - handle_size - inset),
            ('sw', rect.left() + inset, rect.bottom() - handle_size - inset),
            ('w',  rect.left() + inset, rect.center().y() - half_size),
        ]

        for handle_id, x, y in handles:
            # 扩展点击区域 - 现在是 48x48 像素 (16 + 16*2)
            handle_rect = QRectF(
                x - click_padding,
                y - click_padding,
                handle_size + click_padding * 2,
                handle_size + click_padding * 2
            )
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
                # 保存开始时的位置，用于计算相对偏移
                self.resize_start_widget_pos = (self.widget_data['x'], self.widget_data['y'])
                event.accept()
                return

            # 发射选中信号（不再设置透明度，由 DraggableContainer 处理）
            self.selected.emit(self)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.resize_mode:
            print(f"[RESIZE] Mode: {self.resize_mode}, start_pos: {self.resize_start_pos}, current_pos: {event.pos()}")

            # 调整大小逻辑
            delta = event.pos() - self.resize_start_pos
            rect = self.resize_start_rect

            # 使用保存的初始位置作为基准（不使用 widget_data，因为它会被更新）
            start_x, start_y = self.resize_start_widget_pos
            new_x, new_y = start_x, start_y
            new_width = int(rect.width())
            new_height = int(rect.height())

            # 根据不同手柄调整大小（先计算原始大小，不限制最小值）
            # 注意：调整上边和左边时，需要同时调整位置以保持对边固定
            if 'n' in self.resize_mode:  # 上边 - 向上拉伸
                delta_height = -delta.y()  # 向上为负
                new_height = int(rect.height() + delta_height)
                # 调整 Y 位置使底边保持固定
                new_y = start_y + (rect.height() - new_height)
                print(f"[RESIZE] North: delta_y={delta.y()}, old_height={rect.height()}, new_height={new_height}, start_y={start_y}, new_y={new_y}")

            if 's' in self.resize_mode:  # 下边 - 向下拉伸
                new_height = int(rect.height() + delta.y())
                # Y 位置不变，顶边固定
                print(f"[RESIZE] South: delta_y={delta.y()}, new_height={new_height}")

            if 'w' in self.resize_mode:  # 左边 - 向左拉伸
                delta_width = -delta.x()  # 向左为负
                new_width = int(rect.width() + delta_width)
                # 调整 X 位置使右边保持固定
                new_x = start_x + (rect.width() - new_width)
                print(f"[RESIZE] West: delta_x={delta.x()}, old_width={rect.width()}, new_width={new_width}, start_x={start_x}, new_x={new_x}")

            if 'e' in self.resize_mode:  # 右边 - 向右拉伸
                new_width = int(rect.width() + delta.x())
                # X 位置不变，左边固定
                print(f"[RESIZE] East: delta_x={delta.x()}, new_width={new_width}")

            # 应用智能对齐到边缘位置
            scene = self.scene()
            if scene and hasattr(scene, 'views') and scene.views():
                view = scene.views()[0]

                # 构建调整后的矩形
                resized_rect = QRectF(new_x, new_y, new_width, new_height)

                # 收集其他 widgets 的矩形
                other_rects = []
                if hasattr(view, 'widget_items'):
                    for item in view.widget_items:
                        if item != self:
                            item_rect = item.boundingRect()
                            item_rect.moveTopLeft(item.pos())
                            other_rects.append(item_rect)

                # 应用智能对齐（使用新的边缘对齐方法）
                if hasattr(view, 'snap_helper'):
                    snap_result = view.snap_helper.snap_resize_edges(
                        resized_rect, other_rects, self.resize_mode
                    )

                    # 根据对齐结果调整边缘位置
                    if snap_result['right'] is not None:
                        # 右边缘对齐
                        new_width = int(snap_result['right'] - new_x)

                    if snap_result['left'] is not None:
                        # 左边缘对齐
                        original_right = start_x + rect.width()
                        new_x = snap_result['left']
                        new_width = int(original_right - new_x)

                    if snap_result['bottom'] is not None:
                        # 下边缘对齐
                        new_height = int(snap_result['bottom'] - new_y)

                    if snap_result['top'] is not None:
                        # 上边缘对齐
                        original_bottom = start_y + rect.height()
                        new_y = snap_result['top']
                        new_height = int(original_bottom - new_y)

                    # 更新对齐线
                    view.snap_lines = snap_result['snap_lines']
                    view.viewport().update()

            # 应用最小尺寸限制
            new_width = max(200, new_width)
            new_height = max(150, new_height)

            # 更新位置（只在调整上边或左边时才改变位置）
            if new_x != self.pos().x() or new_y != self.pos().y():
                self.setPos(new_x, new_y)
                self.widget_data['x'] = new_x
                self.widget_data['y'] = new_y
                print(f"[RESIZE] Position changed to: ({new_x}, {new_y})")

            # 更新大小
            if self.widget() and (new_width != rect.width() or new_height != rect.height()):
                container = self.widget()
                container.setMinimumSize(new_width, new_height)
                container.setMaximumSize(new_width, new_height)
                container.setFixedSize(new_width, new_height)

                self.widget_data['width'] = new_width
                self.widget_data['height'] = new_height

                # 强制更新布局
                container.updateGeometry()
                print(f"[RESIZE] Size changed to: {new_width}x{new_height}")

            self.update()
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        if self.resize_mode:
            self.resize_mode = None

            # 清除对齐辅助线
            scene = self.scene()
            if scene and hasattr(scene, 'views') and scene.views():
                view = scene.views()[0]
                if hasattr(view, 'snap_lines'):
                    view.snap_lines = []
                    view.viewport().update()

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

    def _set_cursor_shape(self, cursor_shape):
        """设置光标形状（强制更新）"""
        if self.current_cursor != cursor_shape:
            self.current_cursor = cursor_shape
            cursor = QCursor(cursor_shape)
            # 尝试多种方式设置光标
            self.setCursor(cursor)  # 设置 item 光标
            if self.widget():
                self.widget().setCursor(cursor)  # 设置内部 widget 光标
            # 如果在 GraphicsView 中，也设置 view 的光标
            if self.scene() and self.scene().views():
                for view in self.scene().views():
                    view.viewport().setCursor(cursor)
            print(f"[DEBUG] 🖱️ Cursor changed to: {cursor_shape}")

    def hoverMoveEvent(self, event):
        """鼠标悬停移动 - 更新光标"""
        # 获取详细调试信息
        rect = self.boundingRect()
        pos = event.pos()

        # 只在边缘区域才打印，减少输出
        near_edge = (pos.x() < 50 or pos.x() > rect.width() - 50 or
                    pos.y() < 50 or pos.y() > rect.height() - 50)

        if near_edge:
            print(f"[DEBUG] Hover pos: ({pos.x():.1f}, {pos.y():.1f}), "
                  f"rect: ({rect.width():.1f}x{rect.height():.1f}), "
                  f"selected: {self.is_selected}, locked: {self.is_locked}")

        # 检查是否在调整手柄上（仅当选中且未锁定时显示）
        handle = self._get_handle_at_pos(pos)
        if handle:
            print(f"[DEBUG] ✓ On handle: {handle} at pos ({pos.x():.1f}, {pos.y():.1f})")
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
            cursor_shape = cursor_map.get(handle, Qt.CursorShape.ArrowCursor)
            self._set_cursor_shape(cursor_shape)
        else:
            # 检查是否在标题栏区域（拖拽手柄区域）
            if self.is_selected and not self.is_locked and pos.y() <= 48 and pos.x() <= 120:
                self._set_cursor_shape(Qt.CursorShape.SizeAllCursor)
            else:
                self._set_cursor_shape(Qt.CursorShape.ArrowCursor)

        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        """鼠标离开事件 - 恢复默认光标"""
        self._set_cursor_shape(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)
