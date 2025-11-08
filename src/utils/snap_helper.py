"""
SnapHelper - 智能对齐辅助类
提供网格对齐和 Widget 边缘/中心对齐功能
"""

from PyQt6.QtCore import QPointF, QRectF
from typing import List, Tuple, Optional


class SnapHelper:
    """智能对齐辅助类"""

    def __init__(self,
                 grid_size: int = 20,
                 snap_threshold: int = 8,
                 enable_grid_snap: bool = True,
                 enable_widget_snap: bool = True):
        """
        初始化对齐辅助类

        Args:
            grid_size: 网格大小（像素）
            snap_threshold: 吸附阈值（距离多少像素内会吸附）
            enable_grid_snap: 是否启用网格对齐
            enable_widget_snap: 是否启用 Widget 对齐
        """
        self.grid_size = grid_size
        self.snap_threshold = snap_threshold
        self.enable_grid_snap = enable_grid_snap
        self.enable_widget_snap = enable_widget_snap

        # 对齐辅助线信息
        self.snap_lines = []  # [(orientation, position), ...]
                             # orientation: 'h' 水平, 'v' 垂直

    def snap_position(self,
                     rect: QRectF,
                     other_rects: List[QRectF],
                     original_pos: QPointF) -> Tuple[QPointF, List[Tuple[str, float]]]:
        """
        计算吸附后的位置

        Args:
            rect: 当前 Widget 的矩形
            other_rects: 其他 Widget 的矩形列表
            original_pos: 原始位置

        Returns:
            (snapped_pos, snap_lines): 吸附后的位置和对齐线信息
        """
        snapped_x = original_pos.x()
        snapped_y = original_pos.y()
        snap_lines = []

        # 网格对齐
        if self.enable_grid_snap:
            grid_snapped_x = self._snap_to_grid(rect.x())
            grid_snapped_y = self._snap_to_grid(rect.y())

            if abs(grid_snapped_x - rect.x()) <= self.snap_threshold:
                snapped_x = grid_snapped_x
            if abs(grid_snapped_y - rect.y()) <= self.snap_threshold:
                snapped_y = grid_snapped_y

        # Widget 对齐
        if self.enable_widget_snap and other_rects:
            widget_snap = self._snap_to_widgets(rect, other_rects)

            if widget_snap['x'] is not None:
                snapped_x = widget_snap['x']
                if widget_snap['x_line'] is not None:
                    snap_lines.append(('v', widget_snap['x_line']))

            if widget_snap['y'] is not None:
                snapped_y = widget_snap['y']
                if widget_snap['y_line'] is not None:
                    snap_lines.append(('h', widget_snap['y_line']))

        self.snap_lines = snap_lines
        return QPointF(snapped_x, snapped_y), snap_lines

    def _snap_to_grid(self, value: float) -> float:
        """吸附到网格"""
        return round(value / self.grid_size) * self.grid_size

    def _snap_to_widgets(self,
                        rect: QRectF,
                        other_rects: List[QRectF]) -> dict:
        """
        吸附到其他 Widget 的边缘和中心

        Returns:
            {'x': snapped_x or None, 'y': snapped_y or None,
             'x_line': line_pos or None, 'y_line': line_pos or None}
        """
        result = {'x': None, 'y': None, 'x_line': None, 'y_line': None}

        # 当前 Widget 的关键点
        current_left = rect.left()
        current_right = rect.right()
        current_center_x = rect.center().x()
        current_top = rect.top()
        current_bottom = rect.bottom()
        current_center_y = rect.center().y()

        min_x_distance = self.snap_threshold + 1
        min_y_distance = self.snap_threshold + 1

        for other in other_rects:
            # 其他 Widget 的关键点
            other_left = other.left()
            other_right = other.right()
            other_center_x = other.center().x()
            other_top = other.top()
            other_bottom = other.bottom()
            other_center_y = other.center().y()

            # X 轴对齐检测
            x_alignments = [
                # (distance, snapped_x, line_position)
                (abs(current_left - other_left), other_left, other_left),  # 左对齐
                (abs(current_right - other_right), other_right - rect.width(), other_right),  # 右对齐
                (abs(current_center_x - other_center_x), other_center_x - rect.width() / 2, other_center_x),  # 中心对齐
                (abs(current_left - other_right), other_right, other_right),  # 左边贴右边
                (abs(current_right - other_left), other_left - rect.width(), other_left),  # 右边贴左边
            ]

            for distance, snap_x, line_x in x_alignments:
                if distance < min_x_distance:
                    min_x_distance = distance
                    result['x'] = snap_x
                    result['x_line'] = line_x

            # Y 轴对齐检测
            y_alignments = [
                # (distance, snapped_y, line_position)
                (abs(current_top - other_top), other_top, other_top),  # 顶部对齐
                (abs(current_bottom - other_bottom), other_bottom - rect.height(), other_bottom),  # 底部对齐
                (abs(current_center_y - other_center_y), other_center_y - rect.height() / 2, other_center_y),  # 中心对齐
                (abs(current_top - other_bottom), other_bottom, other_bottom),  # 顶部贴底部
                (abs(current_bottom - other_top), other_top - rect.height(), other_top),  # 底部贴顶部
            ]

            for distance, snap_y, line_y in y_alignments:
                if distance < min_y_distance:
                    min_y_distance = distance
                    result['y'] = snap_y
                    result['y_line'] = line_y

        # 如果距离超过阈值，不吸附
        if min_x_distance > self.snap_threshold:
            result['x'] = None
            result['x_line'] = None
        if min_y_distance > self.snap_threshold:
            result['y'] = None
            result['y_line'] = None

        return result

    def snap_resize_edges(self,
                         rect: QRectF,
                         other_rects: List[QRectF],
                         resize_mode: str) -> dict:
        """
        调整大小时对齐边缘

        Args:
            rect: 当前 Widget 的矩形（调整后的位置）
            other_rects: 其他 Widget 的矩形列表
            resize_mode: 调整模式 ('n', 's', 'e', 'w', 'ne', 'nw', 'se', 'sw')

        Returns:
            {'left': snapped_value or None, 'right': ..., 'top': ..., 'bottom': ...,
             'snap_lines': [(orientation, position), ...]}
        """
        result = {
            'left': None,
            'right': None,
            'top': None,
            'bottom': None,
            'snap_lines': []
        }

        # 当前边缘位置
        current_left = rect.left()
        current_right = rect.right()
        current_top = rect.top()
        current_bottom = rect.bottom()

        min_left_dist = self.snap_threshold + 1
        min_right_dist = self.snap_threshold + 1
        min_top_dist = self.snap_threshold + 1
        min_bottom_dist = self.snap_threshold + 1

        for other in other_rects:
            other_left = other.left()
            other_right = other.right()
            other_top = other.top()
            other_bottom = other.bottom()

            # 只对齐正在调整的边缘
            if 'w' in resize_mode:  # 调整左边缘
                # 左边缘可以对齐到其他组件的左边缘或右边缘
                distances = [
                    (abs(current_left - other_left), other_left, 'v', other_left),
                    (abs(current_left - other_right), other_right, 'v', other_right),
                ]
                for dist, snap_value, orientation, line_pos in distances:
                    if dist < min_left_dist:
                        min_left_dist = dist
                        result['left'] = snap_value
                        result['left_line'] = (orientation, line_pos)

            if 'e' in resize_mode:  # 调整右边缘
                # 右边缘可以对齐到其他组件的左边缘或右边缘
                distances = [
                    (abs(current_right - other_left), other_left, 'v', other_left),
                    (abs(current_right - other_right), other_right, 'v', other_right),
                ]
                for dist, snap_value, orientation, line_pos in distances:
                    if dist < min_right_dist:
                        min_right_dist = dist
                        result['right'] = snap_value
                        result['right_line'] = (orientation, line_pos)

            if 'n' in resize_mode:  # 调整上边缘
                # 上边缘可以对齐到其他组件的上边缘或下边缘
                distances = [
                    (abs(current_top - other_top), other_top, 'h', other_top),
                    (abs(current_top - other_bottom), other_bottom, 'h', other_bottom),
                ]
                for dist, snap_value, orientation, line_pos in distances:
                    if dist < min_top_dist:
                        min_top_dist = dist
                        result['top'] = snap_value
                        result['top_line'] = (orientation, line_pos)

            if 's' in resize_mode:  # 调整下边缘
                # 下边缘可以对齐到其他组件的上边缘或下边缘
                distances = [
                    (abs(current_bottom - other_top), other_top, 'h', other_top),
                    (abs(current_bottom - other_bottom), other_bottom, 'h', other_bottom),
                ]
                for dist, snap_value, orientation, line_pos in distances:
                    if dist < min_bottom_dist:
                        min_bottom_dist = dist
                        result['bottom'] = snap_value
                        result['bottom_line'] = (orientation, line_pos)

        # 收集对齐线并清除超出阈值的结果
        if min_left_dist <= self.snap_threshold and 'left_line' in result:
            result['snap_lines'].append(result['left_line'])
        else:
            result['left'] = None

        if min_right_dist <= self.snap_threshold and 'right_line' in result:
            result['snap_lines'].append(result['right_line'])
        else:
            result['right'] = None

        if min_top_dist <= self.snap_threshold and 'top_line' in result:
            result['snap_lines'].append(result['top_line'])
        else:
            result['top'] = None

        if min_bottom_dist <= self.snap_threshold and 'bottom_line' in result:
            result['snap_lines'].append(result['bottom_line'])
        else:
            result['bottom'] = None

        return result

    def get_snap_lines(self) -> List[Tuple[str, float]]:
        """获取当前的对齐辅助线"""
        return self.snap_lines

    def clear_snap_lines(self):
        """清除对齐辅助线"""
        self.snap_lines = []
