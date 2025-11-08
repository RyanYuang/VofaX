"""
GraphicsView 画布
支持拖拽、缩放、网格吸附的主画布
"""

from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush, QIcon, QPixmap, QFontDatabase, QFont
from PyQt6.QtSvg import QSvgRenderer
from typing import Dict, List, Any
from pathlib import Path
import json

from .widget_item import WidgetItem
from ..utils.snap_helper import SnapHelper


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

        # 初始化 SnapHelper
        self.snap_helper = SnapHelper(
            grid_size=self.grid_size,
            snap_threshold=8,
            enable_grid_snap=True,
            enable_widget_snap=True
        )
        self.snap_lines = []  # 当前显示的对齐辅助线

        # 加载 iconfont 字体
        self.icon_font = self._load_icon_font()

        # 画布拖动相关
        self.pan_enabled = True  # 画布拖动是否启用
        self.is_panning = False  # 是否正在拖动画布
        self.pan_start_pos = QPointF()  # 拖动起始位置

        # 缩放相关
        self.zoom_level = 1.0  # 当前缩放级别 (1.0 = 100%)
        self.min_zoom = 0.1  # 最小缩放 (10%)
        self.max_zoom = 5.0  # 最大缩放 (500%)
        self.zoom_step = 1.15  # 缩放步进系数

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

        # 创建悬浮缩放按钮
        self._create_floating_zoom_buttons()

    def _load_icon_font(self) -> QFont:
        """加载 iconfont 字体"""
        font_path = Path("Image_Src/Icon/Icon_lib/iconfont.ttf")
        if font_path.exists():
            font_id = QFontDatabase.addApplicationFont(str(font_path))
            if font_id != -1:
                families = QFontDatabase.applicationFontFamilies(font_id)
                if families:
                    font_family = families[0]
                    print(f"✓ Loaded iconfont: {font_family}")  # 调试信息
                    font = QFont(font_family)
                    font.setPixelSize(18)
                    return font
                else:
                    print("✗ Failed to get font families")
            else:
                print(f"✗ Failed to load font from {font_path}")
        else:
            print(f"✗ Font file not found: {font_path}")
        # 如果加载失败，返回默认字体
        print("✗ Using default font")
        return QFont()

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
        # 使用 SVG 图标：unlock.svg 解锁 / lock.svg 锁定
        icon_name = "unlock.svg" if self.pan_enabled else "lock.svg"
        icon_path = Path("Image_Src/Icon/Lock") / icon_name

        # 加载 SVG 图标
        if icon_path.exists():
            renderer = QSvgRenderer(str(icon_path))
            pixmap = QPixmap(32, 32)  # 图标大小 32x32
            pixmap.fill(Qt.GlobalColor.transparent)

            painter = QPainter(pixmap)
            renderer.render(painter)
            painter.end()

            # 设置图标
            self.lock_button.setIcon(QIcon(pixmap))
            self.lock_button.setIconSize(pixmap.size())
            self.lock_button.setText("")  # 清空文本

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

    def _create_floating_zoom_buttons(self):
        """创建悬浮缩放按钮组"""
        from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QLabel

        # 创建容器 Widget
        self.zoom_container = QWidget(self)
        zoom_layout = QVBoxLayout(self.zoom_container)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        zoom_layout.setSpacing(4)

        # 放大按钮
        self.zoom_in_btn = QPushButton("+")
        self.zoom_in_btn.setFixedSize(44, 44)
        self.zoom_in_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_in_btn.clicked.connect(self._on_zoom_in)
        zoom_layout.addWidget(self.zoom_in_btn)

        # 缩放百分比显示（可点击重置）
        self.zoom_percentage_label = QLabel("100%")
        self.zoom_percentage_label.setFixedSize(44, 28)
        self.zoom_percentage_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.zoom_percentage_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_percentage_label.mousePressEvent = lambda _: self._on_zoom_reset()
        zoom_layout.addWidget(self.zoom_percentage_label)

        # 缩小按钮
        self.zoom_out_btn = QPushButton("−")
        self.zoom_out_btn.setFixedSize(44, 44)
        self.zoom_out_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_out_btn.clicked.connect(self._on_zoom_out)
        zoom_layout.addWidget(self.zoom_out_btn)

        # 适应窗口按钮
        self.zoom_fit_btn = QPushButton("⊡")
        self.zoom_fit_btn.setFixedSize(44, 44)
        self.zoom_fit_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.zoom_fit_btn.setToolTip("Zoom to Fit")
        self.zoom_fit_btn.clicked.connect(self._on_zoom_fit)
        zoom_layout.addWidget(self.zoom_fit_btn)

        # 更新样式
        self._update_zoom_buttons_style()

        # 初始位置（锁定按钮上方）
        self._position_zoom_buttons()

    def _update_zoom_buttons_style(self):
        """更新缩放按钮样式"""
        if self.theme == 'dark':
            bg_color = "#374151"
            hover_color = "#4B5563"
            text_color = "#FFFFFF"
            label_bg = "#1F2937"
        else:
            bg_color = "#E5E7EB"
            hover_color = "#9CA3AF"
            text_color = "#1F2937"
            label_bg = "#FFFFFF"

        button_style = f"""
            QPushButton {{
                background-color: {bg_color};
                color: {text_color};
                border: none;
                border-radius: 22px;
                font-size: 18px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {hover_color};
            }}
            QPushButton:pressed {{
                transform: scale(0.95);
            }}
        """

        label_style = f"""
            QLabel {{
                background-color: {label_bg};
                color: {text_color};
                border: 1px solid {bg_color};
                border-radius: 14px;
                font-size: 11px;
                font-weight: 500;
            }}
        """

        self.zoom_in_btn.setStyleSheet(button_style)
        self.zoom_out_btn.setStyleSheet(button_style)
        self.zoom_fit_btn.setStyleSheet(button_style)
        self.zoom_percentage_label.setStyleSheet(label_style)

    def _position_zoom_buttons(self):
        """定位缩放按钮组到锁定按钮上方"""
        margin = 20
        spacing = 12  # 缩放按钮组和锁定按钮之间的间距

        # 计算容器高度
        container_height = self.zoom_container.sizeHint().height()

        x = self.width() - self.zoom_container.width() - margin
        y = self.height() - self.lock_button.height() - container_height - margin - spacing

        self.zoom_container.move(x, y)

    def _on_zoom_in(self):
        """放大按钮点击"""
        if not self.pan_enabled:  # 锁定时禁用缩放
            return
        self.zoom_in()

    def _on_zoom_out(self):
        """缩小按钮点击"""
        if not self.pan_enabled:  # 锁定时禁用缩放
            return
        self.zoom_out()

    def _on_zoom_reset(self):
        """重置缩放"""
        if not self.pan_enabled:  # 锁定时禁用缩放
            return
        self.zoom_reset()

    def _on_zoom_fit(self):
        """适应窗口"""
        if not self.pan_enabled:  # 锁定时禁用缩放
            return
        self.zoom_to_fit()

    def _update_zoom_percentage_display(self):
        """更新缩放百分比显示"""
        percentage = self.get_zoom_percentage()
        self.zoom_percentage_label.setText(f"{percentage}%")

    def _apply_theme(self):
        """应用主题样式"""
        if self.theme == 'dark':
            self.setBackgroundBrush(QBrush(QColor(26, 26, 26)))
        else:
            self.setBackgroundBrush(QBrush(QColor(249, 250, 251)))

        # 更新锁定按钮主题
        if hasattr(self, 'lock_button'):
            self._update_lock_button()

        # 更新缩放按钮主题
        if hasattr(self, 'zoom_container'):
            self._update_zoom_buttons_style()

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

    def drawForeground(self, painter: QPainter, rect):
        """绘制前景（对齐辅助线）"""
        super().drawForeground(painter, rect)

        if not self.snap_lines:
            return

        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 对齐线颜色：亮蓝色，半透明
        pen = QPen(QColor(10, 132, 255, 180))  # #0A84FF with 70% opacity
        pen.setWidth(2)
        pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)

        scene_rect = self.sceneRect()

        for orientation, position in self.snap_lines:
            if orientation == 'h':  # 水平线
                painter.drawLine(
                    int(scene_rect.left()), int(position),
                    int(scene_rect.right()), int(position)
                )
            elif orientation == 'v':  # 垂直线
                painter.drawLine(
                    int(position), int(scene_rect.top()),
                    int(position), int(scene_rect.bottom())
                )

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
                           'config': {'timeBase': 50, 'yAxis': 'auto', 'showGrid': True, 'protocol': 'FireWater'}},
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

    def delete_selected_widget(self):
        """删除当前选中的 Widget"""
        if self.selected_item:
            # 从场景中移除
            self.scene.removeItem(self.selected_item)
            # 从列表中移除
            self.widget_items.remove(self.selected_item)
            # 清空选中状态
            self.selected_item = None
            # 发射选中信号（None 表示无选中）
            self.widget_selected.emit(None)

    def duplicate_selected_widget(self):
        """复制当前选中的 Widget"""
        if self.selected_item:
            # 复制 widget 数据
            widget_data = self.selected_item.widget_data.copy()

            # 生成新的 ID
            widget_data['id'] = f'widget_{len(self.widget_items)}_{id(self)}'

            # 偏移位置（右下方 20px）
            widget_data['x'] += 20
            widget_data['y'] += 20

            # 深拷贝配置和数据绑定
            import copy
            widget_data['config'] = copy.deepcopy(widget_data.get('config', {}))
            widget_data['dataBinding'] = copy.deepcopy(widget_data.get('dataBinding', {}))

            # 创建新的 WidgetItem
            new_item = WidgetItem(
                widget_data,
                self.theme,
                self.channel_manager
            )

            # 连接信号
            new_item.selected.connect(self._on_item_selected)
            new_item.geometry_changed.connect(self._on_item_geometry_changed)

            # 添加到场景和列表
            self.scene.addItem(new_item)
            self.widget_items.append(new_item)

            # 选中新创建的 Widget
            self._select_item(new_item)

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

    def wheelEvent(self, event):
        """鼠标滚轮事件 - Ctrl+滚轮缩放画布"""
        # 检查是否按下 Ctrl 键
        modifiers = event.modifiers()
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            # Ctrl+滚轮缩放
            if not self.pan_enabled:  # 锁定时禁用缩放
                return

            # 获取滚轮角度
            angle_delta = event.angleDelta().y()

            if angle_delta == 0:
                return

            # 计算缩放因子
            if angle_delta > 0:
                # 向上滚动 - 放大
                zoom_factor = self.zoom_step
            else:
                # 向下滚动 - 缩小
                zoom_factor = 1.0 / self.zoom_step

            # 计算新的缩放级别
            new_zoom = self.zoom_level * zoom_factor

            # 限制缩放范围
            if new_zoom < self.min_zoom or new_zoom > self.max_zoom:
                return

            # 保存鼠标在场景中的位置（作为缩放中心）
            old_pos = self.mapToScene(event.position().toPoint())

            # 应用缩放
            self.scale(zoom_factor, zoom_factor)
            self.zoom_level = new_zoom

            # 调整视图，使鼠标位置保持不变
            new_pos = self.mapToScene(event.position().toPoint())
            delta = new_pos - old_pos
            self.translate(delta.x(), delta.y())

            # 更新缩放百分比显示
            self._update_zoom_percentage_display()

            event.accept()
        else:
            # 没有按下 Ctrl，使用默认滚动行为
            super().wheelEvent(event)

    def zoom_in(self):
        """放大画布"""
        new_zoom = self.zoom_level * self.zoom_step
        if new_zoom <= self.max_zoom:
            self.scale(self.zoom_step, self.zoom_step)
            self.zoom_level = new_zoom
            self._update_zoom_percentage_display()

    def zoom_out(self):
        """缩小画布"""
        new_zoom = self.zoom_level / self.zoom_step
        if new_zoom >= self.min_zoom:
            self.scale(1.0 / self.zoom_step, 1.0 / self.zoom_step)
            self.zoom_level = new_zoom
            self._update_zoom_percentage_display()

    def zoom_reset(self):
        """重置缩放到 100%"""
        self.resetTransform()
        self.zoom_level = 1.0
        self._update_zoom_percentage_display()

    def zoom_to_fit(self):
        """缩放以适应所有 Widget"""
        if not self.widget_items:
            return

        # 计算所有 Widget 的边界
        bounding_rect = None
        for item in self.widget_items:
            item_rect = item.sceneBoundingRect()
            if bounding_rect is None:
                bounding_rect = item_rect
            else:
                bounding_rect = bounding_rect.united(item_rect)

        if bounding_rect:
            # 添加边距
            margin = 50
            bounding_rect.adjust(-margin, -margin, margin, margin)

            # 适应视图
            self.fitInView(bounding_rect, Qt.AspectRatioMode.KeepAspectRatio)

            # 更新缩放级别
            self.zoom_level = self.transform().m11()
            self._update_zoom_percentage_display()

    def get_zoom_percentage(self) -> int:
        """获取当前缩放百分比"""
        return int(self.zoom_level * 100)

    def resizeEvent(self, event):
        """窗口大小变化时重新定位悬浮按钮"""
        super().resizeEvent(event)
        if hasattr(self, 'lock_button'):
            self._position_lock_button()
        if hasattr(self, 'zoom_container'):
            self._position_zoom_buttons()
