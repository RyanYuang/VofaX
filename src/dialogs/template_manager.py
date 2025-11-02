"""
TemplateManager - 布局模板管理对话框
支持模板的新建、删除、重命名、加载
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QInputDialog, QMessageBox,
    QFileDialog
)
from PyQt6.QtCore import Qt, pyqtSignal
from pathlib import Path
import json
import shutil


class TemplateManager(QDialog):
    """布局模板管理器"""

    template_selected = pyqtSignal(str)  # template_path

    def __init__(self, theme: str = 'dark', parent=None):
        super().__init__(parent)
        self.theme = theme
        self.templates_dir = Path("layouts")

        # 确保模板目录存在
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        self.setWindowTitle("Template Manager")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        self._setup_ui()
        self._load_templates()
        self._apply_theme()

    def _setup_ui(self):
        """设置UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        # 标题
        title_label = QLabel("Layout Templates")
        title_label.setStyleSheet("font-size: 18px; font-weight: 600; padding: 8px 0;")
        layout.addWidget(title_label)

        # 模板列表
        self.template_list = QListWidget()
        self.template_list.itemDoubleClicked.connect(self._load_template)
        layout.addWidget(self.template_list)

        # 模板信息
        self.info_label = QLabel("No template selected")
        self.info_label.setStyleSheet("font-size: 12px; color: #9CA3AF; padding: 8px;")
        self.info_label.setWordWrap(True)
        layout.addWidget(self.info_label)

        # 按钮栏
        buttons_layout = QHBoxLayout()

        # 左侧按钮
        new_btn = QPushButton("📄 New")
        new_btn.setFixedHeight(40)
        new_btn.clicked.connect(self._new_template)
        buttons_layout.addWidget(new_btn)

        rename_btn = QPushButton("✏️ Rename")
        rename_btn.setFixedHeight(40)
        rename_btn.clicked.connect(self._rename_template)
        buttons_layout.addWidget(rename_btn)

        delete_btn = QPushButton("🗑️ Delete")
        delete_btn.setFixedHeight(40)
        delete_btn.clicked.connect(self._delete_template)
        buttons_layout.addWidget(delete_btn)

        buttons_layout.addStretch()

        # 右侧按钮
        load_btn = QPushButton("✅ Load Template")
        load_btn.setFixedHeight(40)
        load_btn.clicked.connect(self._load_selected)
        buttons_layout.addWidget(load_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(40)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)

        layout.addLayout(buttons_layout)

    def _load_templates(self):
        """加载模板列表"""
        self.template_list.clear()

        # 获取所有 JSON 文件
        if self.templates_dir.exists():
            for template_file in self.templates_dir.glob("*.json"):
                item = QListWidgetItem(template_file.stem)
                item.setData(Qt.ItemDataRole.UserRole, str(template_file))
                self.template_list.addItem(item)

        # 更新信息
        count = self.template_list.count()
        if count == 0:
            self.info_label.setText("No templates found. Create a new template to get started.")
        else:
            self.info_label.setText(f"{count} template(s) available. Double-click to load.")

    def _new_template(self):
        """新建模板"""
        name, ok = QInputDialog.getText(
            self,
            "New Template",
            "Template name:",
            text="my_template"
        )

        if ok and name:
            # 检查名称是否合法
            if not name.replace('_', '').replace('-', '').isalnum():
                QMessageBox.warning(
                    self,
                    "Invalid Name",
                    "Template name can only contain letters, numbers, hyphens, and underscores."
                )
                return

            template_path = self.templates_dir / f"{name}.json"

            # 检查是否已存在
            if template_path.exists():
                reply = QMessageBox.question(
                    self,
                    "Template Exists",
                    f"Template '{name}' already exists. Overwrite?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return

            # 创建空模板
            empty_layout = {
                "version": "1.0",
                "widgets": [],
                "theme": self.theme,
                "metadata": {
                    "name": name,
                    "created": "auto",
                    "description": "Custom template"
                }
            }

            try:
                with open(template_path, 'w', encoding='utf-8') as f:
                    json.dump(empty_layout, f, indent=2)

                self._load_templates()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Template '{name}' created successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to create template:\n{str(e)}"
                )

    def _rename_template(self):
        """重命名模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a template to rename.")
            return

        old_path = Path(current_item.data(Qt.ItemDataRole.UserRole))
        old_name = old_path.stem

        new_name, ok = QInputDialog.getText(
            self,
            "Rename Template",
            "New name:",
            text=old_name
        )

        if ok and new_name and new_name != old_name:
            # 检查名称是否合法
            if not new_name.replace('_', '').replace('-', '').isalnum():
                QMessageBox.warning(
                    self,
                    "Invalid Name",
                    "Template name can only contain letters, numbers, hyphens, and underscores."
                )
                return

            new_path = self.templates_dir / f"{new_name}.json"

            # 检查是否已存在
            if new_path.exists():
                QMessageBox.warning(
                    self,
                    "Template Exists",
                    f"A template named '{new_name}' already exists."
                )
                return

            try:
                shutil.move(str(old_path), str(new_path))
                self._load_templates()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Template renamed to '{new_name}'!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to rename template:\n{str(e)}"
                )

    def _delete_template(self):
        """删除模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a template to delete.")
            return

        template_path = Path(current_item.data(Qt.ItemDataRole.UserRole))
        template_name = template_path.stem

        reply = QMessageBox.question(
            self,
            "Delete Template",
            f"Are you sure you want to delete template '{template_name}'?\n\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                template_path.unlink()
                self._load_templates()
                QMessageBox.information(
                    self,
                    "Success",
                    f"Template '{template_name}' deleted successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete template:\n{str(e)}"
                )

    def _load_template(self, item: QListWidgetItem):
        """加载模板（双击）"""
        template_path = item.data(Qt.ItemDataRole.UserRole)
        self.template_selected.emit(template_path)
        self.accept()

    def _load_selected(self):
        """加载选中的模板"""
        current_item = self.template_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "No Selection", "Please select a template to load.")
            return

        self._load_template(current_item)

    def _apply_theme(self):
        """应用主题"""
        if self.theme == 'dark':
            self.setStyleSheet("""
                QDialog {
                    background-color: #1A1A1A;
                    color: #FFFFFF;
                }
                QListWidget {
                    background-color: #252525;
                    border: 1px solid #3A3A3A;
                    border-radius: 6px;
                    color: #FFFFFF;
                    padding: 4px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-radius: 4px;
                }
                QListWidget::item:selected {
                    background-color: #0A84FF;
                }
                QListWidget::item:hover {
                    background-color: #2A2A2A;
                }
                QPushButton {
                    background-color: #2A2A2A;
                    border: 1px solid #3A3A3A;
                    border-radius: 6px;
                    color: #FFFFFF;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #3A3A3A;
                    border-color: #0A84FF;
                }
            """)
        else:
            self.setStyleSheet("""
                QDialog {
                    background-color: #FFFFFF;
                    color: #1F2937;
                }
                QListWidget {
                    background-color: #F9FAFB;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    padding: 4px;
                }
                QListWidget::item {
                    padding: 8px;
                    border-radius: 4px;
                }
                QListWidget::item:selected {
                    background-color: #0A84FF;
                    color: #FFFFFF;
                }
                QListWidget::item:hover {
                    background-color: #F3F4F6;
                }
                QPushButton {
                    background-color: #FFFFFF;
                    border: 1px solid #D1D5DB;
                    border-radius: 6px;
                    color: #1F2937;
                    padding: 8px 16px;
                }
                QPushButton:hover {
                    background-color: #F3F4F6;
                    border-color: #0A84FF;
                }
            """)
