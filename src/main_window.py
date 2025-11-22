"""
UniScope 主窗口
负责整体布局和顶层UI组件
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QMenuBar, QMenu, QStatusBar, QToolBar, QLabel,
    QMessageBox, QFileDialog, QGraphicsOpacityEffect
)
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QVariantAnimation
from PyQt6.QtGui import QAction, QKeySequence, QColor
import json
from pathlib import Path
from typing import Optional

from .panels.widget_library import WidgetLibrary
from .panels.inspector import InspectorPanel
from .canvas.graphics_view import GraphicsView
from .utils.theme import ThemeManager
from .data.channel_manager import ChannelManager
from .data.data_recorder import DataRecorder
from .dialogs.connection_dialog import ConnectionDialog
from .dialogs.recording_dialog import RecordingDialog
from .dialogs.template_manager import TemplateManager
from .components.top_bar import TopBar
from .serial.serial_manager import SerialManager


class MainWindow(QMainWindow):
    """UniScope 主窗口类"""
    # 信号定义
    theme_changed = pyqtSignal(str)  # 'dark' or 'light'

    def __init__(self):
        super().__init__()
        self.setWindowTitle("UniScope - Universal Serial Debugging Hub")
        self.setGeometry(100, 100, 1400, 900)

        # 初始化管理器
        self.theme_manager = ThemeManager()
        self.channel_manager = ChannelManager()
        self.serial_manager = SerialManager(self.channel_manager)
        self.data_recorder = DataRecorder(self.channel_manager)
        

        # 状态变量
        self.current_theme = 'dark'
        self.is_connected = False
        self.grid_snap = True
        self.current_layout_path = None
        self.is_transitioning = False  # 主题过渡标志

        # 创建主题过渡遮罩
        self.transition_overlay = None

        # 连接串口管理器信号
        self.serial_manager.connected.connect(self._on_serial_connected)
        self.serial_manager.disconnected.connect(self._on_serial_disconnected)
        self.serial_manager.error_occurred.connect(self._on_serial_error)
        self.serial_manager.connection_lost.connect(self._on_serial_connection_lost)
        self.serial_manager.rx_tx_stats.connect(self.update_rx_tx)
        self.serial_manager.data_received_signal.connect(self._on_rx_activity)
        self.serial_manager.data_sent_signal.connect(self._on_tx_activity)

        # 构建UI
        self._create_top_bar()
        self._create_status_bar()
        self._create_central_widget()

        # 应用初始主题
        self._apply_theme(self.current_theme)

    def _create_top_bar(self):
        """创建顶部栏"""
        self.top_bar = TopBar(self.current_theme)

        # 连接信号
        self.top_bar.template_requested.connect(self._load_template)
        self.top_bar.save_layout_requested.connect(self._save_layout)
        self.top_bar.export_data_requested.connect(self._export_data)
        self.top_bar.recording_clicked.connect(self._show_recording_dialog)
        self.top_bar.grid_snap_toggled.connect(self._toggle_grid_snap)
        self.top_bar.theme_toggled.connect(self._toggle_theme)
        self.top_bar.connection_clicked.connect(self._show_connection_dialog)

        # 设置为中央 Widget 的上方
        # 注意: 我们会在 _create_central_widget 中将 top_bar 添加到主布局

    def _create_menu_bar_old(self):
        """创建菜单栏"""
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("&File")

        new_action = QAction("&New Layout", self)
        new_action.setShortcut(QKeySequence.StandardKey.New)
        new_action.triggered.connect(self._new_layout)
        file_menu.addAction(new_action)

        open_action = QAction("&Open Layout...", self)
        open_action.setShortcut(QKeySequence.StandardKey.Open)
        open_action.triggered.connect(self._open_layout)
        file_menu.addAction(open_action)

        save_action = QAction("&Save Layout", self)
        save_action.setShortcut(QKeySequence.StandardKey.Save)
        save_action.triggered.connect(self._save_layout)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save Layout &As...", self)
        save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        save_as_action.triggered.connect(self._save_layout_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        export_action = QAction("&Export Data...", self)
        export_action.triggered.connect(self._export_data)
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Templates Menu
        templates_menu = menubar.addMenu("&Templates")

        debug_template = QAction("Debug Layout", self)
        debug_template.triggered.connect(lambda: self._load_template('debug'))
        templates_menu.addAction(debug_template)

        sensor_template = QAction("Sensor Dashboard", self)
        sensor_template.triggered.connect(lambda: self._load_template('sensor'))
        templates_menu.addAction(sensor_template)

        protocol_template = QAction("Protocol Analyzer", self)
        protocol_template.triggered.connect(lambda: self._load_template('protocol'))
        templates_menu.addAction(protocol_template)

        # View Menu
        view_menu = menubar.addMenu("&View")

        theme_action = QAction("Toggle &Theme", self)
        theme_action.setShortcut("Ctrl+T")
        theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_action)

        grid_action = QAction("Toggle &Grid Snap", self)
        grid_action.setShortcut("Ctrl+G")
        grid_action.setCheckable(True)
        grid_action.setChecked(self.grid_snap)
        grid_action.triggered.connect(self._toggle_grid_snap)
        view_menu.addAction(grid_action)

        # Connection Menu
        connection_menu = menubar.addMenu("&Connection")

        connect_action = QAction("&Connect...", self)
        connect_action.setShortcut("Ctrl+Shift+C")
        connect_action.triggered.connect(self._show_connection_dialog)
        connection_menu.addAction(connect_action)

        disconnect_action = QAction("&Disconnect", self)
        disconnect_action.triggered.connect(self._disconnect)
        connection_menu.addAction(disconnect_action)

        # Help Menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About UniScope", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_tool_bar(self):
        """创建工具栏"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, toolbar)

        # 连接状态指示器
        self.connection_label = QLabel("⚫ Disconnected")
        toolbar.addWidget(self.connection_label)

        toolbar.addSeparator()

        # 网格吸附开关
        grid_action = QAction("Grid Snap", self)
        grid_action.setCheckable(True)
        grid_action.setChecked(self.grid_snap)
        grid_action.triggered.connect(self._toggle_grid_snap)
        toolbar.addAction(grid_action)

        toolbar.addSeparator()

        # 主题切换
        theme_action = QAction("🌙 Dark", self)
        theme_action.triggered.connect(self._toggle_theme)
        toolbar.addAction(theme_action)

    def _create_status_bar(self):
        """创建状态栏"""
        statusbar = self.statusBar()

        self.status_label = QLabel("Ready")
        statusbar.addWidget(self.status_label)

        # RX/TX 计数器
        self.rx_label = QLabel("RX: 0 B")
        self.tx_label = QLabel("TX: 0 B")
        statusbar.addPermanentWidget(self.rx_label)
        statusbar.addPermanentWidget(self.tx_label)

    def _create_central_widget(self):
        """创建中心部件（主要布局）"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 主垂直布局 (TopBar + 内容区域)
        main_v_layout = QVBoxLayout(central_widget)
        main_v_layout.setContentsMargins(0, 0, 0, 0)
        main_v_layout.setSpacing(0)

        # 添加 TopBar
        main_v_layout.addWidget(self.top_bar)

        # 内容区域水平布局
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 左侧：Widget 库
        self.widget_library = WidgetLibrary(self.current_theme)
        main_layout.addWidget(self.widget_library)

        # 中间：画布
        self.canvas = GraphicsView(
            theme=self.current_theme,
            grid_snap=self.grid_snap,
            channel_manager=self.channel_manager
        )
        main_layout.addWidget(self.canvas, 1)  # stretch=1

        # 右侧：Inspector 面板（初始隐藏）
        self.inspector = InspectorPanel(self.current_theme, self.channel_manager)
        self.inspector.setVisible(False)
        main_layout.addWidget(self.inspector)

        # 连接信号
        self.widget_library.widget_requested.connect(self.canvas.add_widget)
        self.canvas.widget_selected.connect(self._on_widget_selected)
        self.inspector.config_changed.connect(self.canvas.update_selected_widget)
        self.inspector.delete_requested.connect(self.canvas.delete_selected_widget)
        self.inspector.duplicate_requested.connect(self.canvas.duplicate_selected_widget)

        # 将内容区域添加到主布局
        main_v_layout.addLayout(main_layout)

    def _apply_theme(self, theme: str):
        """应用主题样式"""
        stylesheet = self.theme_manager.get_stylesheet(theme)
        self.setStyleSheet(stylesheet)
        self.theme_changed.emit(theme)

    # ==================== Slots ====================

    def _toggle_theme(self):
        """切换主题（带颜色渐变动画）"""
        if self.is_transitioning:
            return  # 如果正在过渡，忽略请求

        self.is_transitioning = True

        # 确定起始和结束颜色
        if self.current_theme == 'dark':
            # 从暗色切换到亮色：黑色 → 白色
            start_color = QColor('#0D0D0D')
            end_color = QColor('#FAFAFA')
        else:
            # 从亮色切换到暗色：白色 → 黑色
            start_color = QColor('#FAFAFA')
            end_color = QColor('#0D0D0D')

        # 创建过渡遮罩
        if not self.transition_overlay:
            self.transition_overlay = QWidget(self.centralWidget())
            self.transition_overlay.setObjectName("themeTransitionOverlay")

        # 设置遮罩几何和样式
        self.transition_overlay.setGeometry(self.centralWidget().rect())
        self.transition_overlay.raise_()

        # 创建透明度效果
        opacity_effect = QGraphicsOpacityEffect(self.transition_overlay)
        self.transition_overlay.setGraphicsEffect(opacity_effect)
        opacity_effect.setOpacity(1.0)

        self.transition_overlay.setStyleSheet(f"background-color: {start_color.name()};")
        self.transition_overlay.show()

        # 追踪是否已切换主题
        self._theme_switched = False

        # 保存起始和结束颜色，用于手动插值
        self._start_color = start_color
        self._end_color = end_color

        # 使用整数动画（0-1000）来驱动颜色插值
        def update_color(value):
            # value 范围 0-1000，映射到 0.0-1.0
            progress = value / 1000.0

            # 手动插值 RGB 分量
            r = int(self._start_color.red() + (self._end_color.red() - self._start_color.red()) * progress)
            g = int(self._start_color.green() + (self._end_color.green() - self._start_color.green()) * progress)
            b = int(self._start_color.blue() + (self._end_color.blue() - self._start_color.blue()) * progress)

            interpolated_color = QColor(r, g, b)

            if self.transition_overlay and self.transition_overlay.isVisible():
                self.transition_overlay.setStyleSheet(f"background-color: {interpolated_color.name()};")

        # 创建颜色动画（使用整数 0-1000）
        self.color_animation = QVariantAnimation(self)
        self.color_animation.setDuration(600)
        self.color_animation.setStartValue(0)
        self.color_animation.setEndValue(1000)
        self.color_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.color_animation.valueChanged.connect(update_color)

        # 使用定时器在中途切换主题（更可靠）
        QTimer.singleShot(300, self._perform_theme_switch_if_needed)

        # 动画完成后淡出遮罩
        def on_animation_finished():
            if self.transition_overlay:
                opacity_effect = self.transition_overlay.graphicsEffect()
                if opacity_effect:
                    self.fade_out_animation = QPropertyAnimation(opacity_effect, b"opacity")
                    self.fade_out_animation.setDuration(200)
                    self.fade_out_animation.setStartValue(1.0)
                    self.fade_out_animation.setEndValue(0.0)
                    self.fade_out_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

                    def on_fade_out_finished():
                        self._cleanup_transition()

                    self.fade_out_animation.finished.connect(on_fade_out_finished)
                    self.fade_out_animation.start()
                else:
                    self._cleanup_transition()
            else:
                self._cleanup_transition()

        self.color_animation.finished.connect(on_animation_finished)

        # 开始颜色渐变动画
        self.color_animation.start()

    def _perform_theme_switch_if_needed(self):
        """在动画中途切换主题（只执行一次）"""
        if not self._theme_switched:
            self._perform_theme_switch()
            self._theme_switched = True

    def _perform_theme_switch(self):
        """执行实际的主题切换"""
        # 切换主题
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        self._apply_theme(self.current_theme)
        self.top_bar.set_theme(self.current_theme)
        self.canvas.set_theme(self.current_theme)
        self.widget_library.set_theme(self.current_theme)
        self.inspector.set_theme(self.current_theme)

    def _cleanup_transition(self):
        """清理过渡效果"""
        if self.transition_overlay:
            self.transition_overlay.hide()
            # 重置透明度
            opacity_effect = self.transition_overlay.graphicsEffect()
            if opacity_effect:
                opacity_effect.setOpacity(1.0)

        self.is_transitioning = False
        if hasattr(self, '_theme_switched'):
            delattr(self, '_theme_switched')

    def resizeEvent(self, event):
        """窗口大小调整事件"""
        super().resizeEvent(event)

        # 更新过渡遮罩的大小
        if self.transition_overlay and self.centralWidget():
            self.transition_overlay.setGeometry(self.centralWidget().rect())

    def _toggle_grid_snap(self, checked: bool):
        """切换网格吸附"""
        self.grid_snap = checked
        self.canvas.set_grid_snap(checked)

    def _new_layout(self):
        """新建布局"""
        reply = QMessageBox.question(
            self, 'New Layout',
            'Clear current layout and start fresh?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.canvas.clear_widgets()
            self.current_layout_path = None
            self.status_label.setText("New layout created")

    def _open_layout(self):
        """打开布局文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Layout",
            "layouts",
            "Layout Files (*.json)"
        )
        if file_path:
            self._load_layout_from_file(file_path)

    def _save_layout(self):
        """保存布局"""
        if self.current_layout_path:
            self._save_layout_to_file(self.current_layout_path)
        else:
            self._save_layout_as()

    def _save_layout_as(self):
        """另存为布局"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Layout As",
            "layouts/my_layout.json",
            "Layout Files (*.json)"
        )
        if file_path:
            self._save_layout_to_file(file_path)

    def _load_layout_from_file(self, file_path: str):
        """从文件加载布局"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                layout_data = json.load(f)

            self.canvas.load_layout(layout_data)
            self.current_layout_path = file_path
            self.status_label.setText(f"Layout loaded: {Path(file_path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load layout:\n{str(e)}")

    def _save_layout_to_file(self, file_path: str):
        """保存布局到文件"""
        try:
            layout_data = self.canvas.get_layout()
            layout_data['theme'] = self.current_theme

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(layout_data, f, indent=2)

            self.current_layout_path = file_path
            self.status_label.setText(f"Layout saved: {Path(file_path).name}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save layout:\n{str(e)}")

    def _load_template(self, template_name: str = None):
        """加载预设模板或打开模板管理器"""
        # 如果提供了模板名称，直接加载
        if template_name:
            template_path = f"layouts/{template_name}.json"
            if Path(template_path).exists():
                self._load_layout_from_file(template_path)
            else:
                QMessageBox.warning(self, "Template Not Found", f"Template '{template_name}' not found.")
        else:
            # 打开模板管理器
            self._show_template_manager()

    def _show_template_manager(self):
        """显示模板管理器"""
        dialog = TemplateManager(self.current_theme, self)
        dialog.template_selected.connect(self._load_layout_from_file)
        dialog.exec()

    def _export_data(self):
        """导出数据"""
        QMessageBox.information(self, "Export Data", "Data export feature coming soon!")

    def _show_connection_dialog(self):
        """显示连接对话框"""
        dialog = ConnectionDialog(self.current_theme, self)
        dialog.connected.connect(self._on_serial_connect)
        dialog.disconnect.connect(self._disconnect)
        self.serial_manager.connected.connect(dialog.on_connect_succeeded)
        self.serial_manager.disconnected.connect(dialog.on_disconnect)
        # 居中显示
        dialog.move(
            self.geometry().center() - dialog.rect().center()
        )

        dialog.exec()

    def _show_recording_dialog(self):
        """显示录制对话框"""
        # 创建对话框（如果不存在）
        if not hasattr(self, 'recording_dialog') or self.recording_dialog is None:
            self.recording_dialog = RecordingDialog(
                self.data_recorder,
                self.channel_manager,
                self.current_theme,
                self
            )

        # 显示对话框
        self.recording_dialog.show()
        self.recording_dialog.raise_()
        self.recording_dialog.activateWindow()

    def _on_serial_connect(self, port: str, baudrate: int, databits: int, stopbits: int, parity: str):
        """串口连接请求回调（来自 ConnectionDialog）"""
        # 使用 SerialManager 连接串口
        success = self.serial_manager.connect(
            port=port,
            baudrate=baudrate,
            databits=databits,
            stopbits=int(stopbits),
            parity=parity,
            protocol='ascii',  # 使用 ASCII 协议解析文本数据
            channel_count=15
        )

        if not success:
            QMessageBox.critical(
                self,
                "Connection Failed",
                f"Failed to connect to {port}"
            )

    def _on_serial_connected(self, port: str, baudrate: int):
        """串口连接成功回调"""
        self.is_connected = True

        # 更新 TopBar 连接状态
        self.top_bar.set_connected(True, f"{port} @ {baudrate}")

        # 更新状态栏
        self.status_label.setText(f"Connected to {port}")

    def _on_serial_disconnected(self):
        """串口断开回调"""
        self.is_connected = False

        # 更新 TopBar 连接状态
        self.top_bar.set_connected(False, "")

        # 更新状态栏
        self.status_label.setText("Disconnected")

        # 重置 RX/TX 统计
        self.update_rx_tx(0, 0)

    def _on_serial_error(self, error_msg: str):
        """串口错误回调"""
        QMessageBox.critical(
            self,
            "Serial Error",
            f"Serial communication error:\n{error_msg}"
        )
        self._disconnect()

    def _on_serial_connection_lost(self):
        """连接丢失回调"""
        self.is_connected = False

        # 更新 UI
        self.top_bar.set_connected(False, "")
        self.status_label.setText("Connection lost")
        

        # 显示警告
        QMessageBox.warning(
            self,
            "Connection Lost",
            "Serial connection has been lost.\n"
            "Please check the device and reconnect."
        )

    def _disconnect(self):
        """断开连接"""
        self.serial_manager.disconnect()
        

    def _show_about(self):
        """显示关于对话框"""
        QMessageBox.about(
            self,
            "About UniScope",
            "<h3>UniScope v0.1.0</h3>"
            "<p>Universal Serial Debugging Hub</p>"
            "<p>A versatile tool for protocol debugging, "
            "real-time data visualization, and serial communication.</p>"
            "<p><b>License:</b> MIT</p>"
            "<p><b>Author:</b> UniScope Team</p>"
        )

    def _on_widget_selected(self, widget_data: Optional[dict]):
        """Widget 选中时更新 Inspector"""
        if widget_data:
            self.inspector.set_widget(widget_data)
            self.inspector.setVisible(True)
        else:
            self.inspector.setVisible(False)

    def update_rx_tx(self, rx_bytes: int, tx_bytes: int):
        """更新 RX/TX 统计"""
        self.rx_label.setText(f"RX: {rx_bytes} B")
        self.tx_label.setText(f"TX: {tx_bytes} B")

    def _on_rx_activity(self):
        """RX 活动回调 - 闪烁 RX 指示灯"""
        if hasattr(self.top_bar, 'rx_indicator'):
            self.top_bar.rx_indicator.flash()

    def _on_tx_activity(self):
        """TX 活动回调 - 闪烁 TX 指示灯"""
        if hasattr(self.top_bar, 'tx_indicator'):
            self.top_bar.tx_indicator.flash()

    def closeEvent(self, event):
        """窗口关闭事件 - 清理资源"""
        # 完全销毁串口线程
        if self.serial_manager.serial_thread:
            self.serial_manager._destroy_thread()
        event.accept()
