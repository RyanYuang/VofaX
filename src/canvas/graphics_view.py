"""
GraphicsView 画布
支持拖拽、缩放、网格吸附的主画布
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush
from typing import Dict, List, Any
import json

from .widget_item import WidgetItem


class GraphicsView(QGraphicsView):
    """主画布类"""

    widget_selected = pyqtSignal(object)  # 选中的 Widget 数据或 None

    def __init__(self, theme: str = 'dark', grid_snap: bool = True, channel_manager=None):
        super().__init__()

        self.theme = theme
        self.grid_snap = grid_snap
        self.channel_manager = channel_manager
        self.grid_size = 20  # 网格大小
        self._updating_position = False  # 防止递归标志

        # 画布拖动相关
        self.pan_enabled = True  # 画布拖动是否启用
        self.is_panning = False  # 是否正在拖动画布
        self.pan_start_pos = QPointF()  # 拖动起始位置

        # 创建场景
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, 5000, 5000)
        self.setScene(self.scene)

        # Widget 项列表
        self.widget_items: List[WidgetItem] = []
        self.selected_item: WidgetItem = None

        # 配置视图
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setAcceptDrops(True)

        # 应用主题
        self._apply_theme()

        # 创建悬浮锁定按钮
        self._create_floating_lock_button()

    def _create_floating_lock_button(self):
        """创建悬浮锁定按钮"""
        from PyQt6.QtWidgets import QPushButton

        self.lock_button = QPushButton(self)
        self.lock_button.setFixedSize(56, 56)
        self.lock_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # 更新按钮图标和样式
        self._update_lock_button()

        # 连接点击事件
        self.lock_button.clicked.connect(self._toggle_pan_lock)

        # 初始位置（右下角）
        self._position_lock_button()

    def _update_lock_button(self):
        """更新锁定按钮样式"""
        # 图标：🔓 解锁 / 🔒 锁定
        icon = "🔓" if self.pan_enabled else "🔒"

        if self.theme == 'dark':
            bg_color = "#374151" if self.pan_enabled else "#EF4444"
            hover_color = "#4B5563" if self.pan_enabled else "#DC2626"
        else:
            bg_color = "#D1D5DB" if self.pan_enabled else "#EF4444"
            hover_color = "#9CA3AF" if self.pan_enabled else "#DC2626"

        self.lock_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: none;
                border-radius: 28px;
                color: #FFFFFF;
                font-size: 24px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                background-color: {hover_color};
                transform: scale(0.95);
            }}
        """)
        self.lock_button.setText(icon)

    def _position_lock_button(self):
        """定位锁定按钮到右下角"""
        margin = 20
        x = self.width() - self.lock_button.width() - margin
        y = self.height() - self.lock_button.height() - margin
        self.lock_button.move(x, y)

    def _toggle_pan_lock(self):
        """切换画布拖动锁定状态"""
        self.pan_enabled = not self.pan_enabled
        self._update_lock_button()

        # 如果锁定时正在拖动，则停止拖动
        if not self.pan_enabled and self.is_panning:
            self.is_panning = False
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)

    def _apply_theme(self):
        """应用主题样式"""
        if self.theme == 'dark':
            self.setBackgroundBrush(QBrush(QColor(26, 26, 26)))
        else:
            self.setBackgroundBrush(QBrush(QColor(249, 250, 251)))

        # 更新锁定按钮主题
        if hasattr(self, 'lock_button'):
            self._update_lock_button()

    def drawBackground(self, painter: QPainter, rect):
        """绘制背景网格"""
        super().drawBackground(painter, rect)

        if not self.grid_snap:
            return

        # 绘制网格点
        painter.save()

        if self.theme == 'dark':
            pen = QPen(QColor(42, 42, 42))
        else:
            pen = QPen(QColor(209, 213, 219))

        pen.setWidth(1)
        painter.setPen(pen)

        left = int(rect.left()) - (int(rect.left()) % self.grid_size)
        top = int(rect.top()) - (int(rect.top()) % self.grid_size)

        # 绘制网格点
        for x in range(left, int(rect.right()), self.grid_size):
            for y in range(top, int(rect.bottom()), self.grid_size):
                painter.drawPoint(x, y)

        painter.restore()

    def add_widget(self, widget_type: str, x: float = 100, y: float = 100):
        """
        添加新 Widget

        Args:
            widget_type: Widget 类型
            x, y: 位置
        """
        # 默认配置
        default_configs = {
            'oscilloscope': {'width': 500, 'height': 350, 'title': 'Oscilloscope',
                           'config': {'timeBase': 50, 'yAxis': 'auto', 'showGrid': True}},
            'terminal': {'width': 500, 'height': 400, 'title': 'Terminal',
                        'config': {'displayMode': 'ascii', 'autoScroll': True}},
            'hex-viewer': {'width': 450, 'height': 350, 'title': 'Hex Viewer',
                         'config': {'bytesPerRow': 16}},
            'gauge': {'width': 280, 'height': 280, 'title': 'Gauge',
                     'config': {'min': 0, 'max': 100, 'unit': ''}},
            'data-table': {'width': 600, 'height': 350, 'title': 'Data Table',
                         'config': {'maxRows': 100}},
            'packet-analyzer': {'width': 500, 'height': 400, 'title': 'Packet Analyzer',
                              'config': {'protocol': 'custom'}},
            'chart': {'width': 500, 'height': 350, 'title': 'Chart',
                     'config': {'chartType': 'line'}},
        }

        config = default_configs.get(widget_type, {})

        widget_data = {
            'id': f'widget_{len(self.widget_items)}_{id(self)}',
            'type': widget_type,
            'x': x,
            'y': y,
            'width': config.get('width', 500),
            'height': config.get('height', 350),
            'title': config.get('title', 'Widget'),
            'config': config.get('config', {}),
            'dataBinding': {'channels': ['I0']},
        }

        # 创建 WidgetItem
        widget_item = WidgetItem(
            widget_data,
            self.theme,
            self.channel_manager
        )

        # 连接信号
        widget_item.selected.connect(self._on_item_selected)
        widget_item.geometry_changed.connect(self._on_item_geometry_changed)

        # 添加到场景
        self.scene.addItem(widget_item)
        self.widget_items.append(widget_item)

        # 选中新添加的 Widget
        self._select_item(widget_item)

    def _on_item_selected(self, item: WidgetItem):
        """处理 Widget 选中事件"""
        self._select_item(item)

    def _select_item(self, item: WidgetItem):
        """选中指定 Widget"""
        # 取消之前的选中
        if self.selected_item:
            self.selected_item.set_selected(False)

        # 选中新的
        self.selected_item = item
        if item:
            item.set_selected(True)
            self.widget_selected.emit(item.widget_data)
        else:
            self.widget_selected.emit(None)

    def _on_item_geometry_changed(self, item: WidgetItem):
        """Widget 几何属性变更"""
        # 防止递归
        if self._updating_position:
            return

        # 可以在这里添加网格吸附逻辑
        if self.grid_snap:
            self._updating_position = True
            try:
                pos = item.pos()
                snapped_x = round(pos.x() / self.grid_size) * self.grid_size
                snapped_y = round(pos.y() / self.grid_size) * self.grid_size
                item.setPos(snapped_x, snapped_y)
            finally:
                self._updating_position = False

    def update_selected_widget(self, updates: Dict[str, Any]):
        """
        更新选中的 Widget 配置

        Args:
            updates: 更新的属性字典
        """
        if self.selected_item:
            self.selected_item.update_widget(updates)

    def clear_widgets(self):
        """清除所有 Widgets"""
        for item in self.widget_items:
            self.scene.removeItem(item)
        self.widget_items.clear()
        self.selected_item = None
        self.widget_selected.emit(None)

    def get_layout(self) -> Dict:
        """
        获取当前布局数据

        Returns:
            布局数据字典
        """
        widgets_data = []
        for item in self.widget_items:
            widgets_data.append(item.widget_data.copy())

        return {
            'version': '1.0',
            'widgets': widgets_data
        }

    def load_layout(self, layout_data: Dict):
        """
        加载布局数据

        Args:
            layout_data: 布局数据字典
        """
        # 清除现有 Widgets
        self.clear_widgets()

        # 加载 Widgets
        for widget_data in layout_data.get('widgets', []):
            widget_item = WidgetItem(
                widget_data,
                self.theme,
                self.channel_manager
            )

            widget_item.selected.connect(self._on_item_selected)
            widget_item.geometry_changed.connect(self._on_item_geometry_changed)

            self.scene.addItem(widget_item)
            self.widget_items.append(widget_item)

    def set_theme(self, theme: str):
        """设置主题"""
        self.theme = theme
        self._apply_theme()

        # 更新所有 Widget 的主题
        for item in self.widget_items:
            item.set_theme(theme)

        # 更新悬浮按钮主题
        if hasattr(self, 'lock_button'):
            self._update_lock_button()

    def set_grid_snap(self, enabled: bool):
        """设置网格吸附"""
        self.grid_snap = enabled
        self.viewport().update()

    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """拖拽移动事件"""
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """拖拽释放事件 - 添加新 Widget"""
        if event.mimeData().hasText():
            widget_type = event.mimeData().text()
            pos = self.mapToScene(event.position().toPoint())

            self.add_widget(widget_type, pos.x(), pos.y())
            event.acceptProposedAction()

    def mousePressEvent(self, event):
        """鼠标按下事件"""
        # 中键拖动画布
        if event.button() == Qt.MouseButton.MiddleButton and self.pan_enabled:
            self.is_panning = True
            self.pan_start_pos = event.pos()
            self.viewport().setCursor(Qt.CursorShape.ClosedHandCursor)
            event.accept()
            return

        super().mousePressEvent(event)

        # 左键点击空白区域取消选中
        if event.button() == Qt.MouseButton.LeftButton:
            item = self.itemAt(event.pos())
            if not item:
                self._select_item(None)

    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        # 中键拖动画布
        if self.is_panning:
            delta = event.pos() - self.pan_start_pos
            self.pan_start_pos = event.pos()

            # 更新滚动条
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        # 中键释放
        if event.button() == Qt.MouseButton.MiddleButton and self.is_panning:
            self.is_panning = False
            self.viewport().setCursor(Qt.CursorShape.ArrowCursor)
            event.accept()
            return

        super().mouseReleaseEvent(event)

    def resizeEvent(self, event):
        """窗口大小变化时重新定位悬浮按钮"""
        super().resizeEvent(event)
        if hasattr(self, 'lock_button'):
            self._position_lock_button()
