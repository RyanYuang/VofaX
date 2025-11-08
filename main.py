#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
UniScope - Universal Serial Debugging Hub
主程序入口

Author: UniScope Team
License: MIT
"""

import sys
import logging
import argparse
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from src.main_window import MainWindow
from src.data.widget_registry import register_builtin_widgets
from src.utils.plugin_loader import PluginLoader


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='UniScope - Universal Serial Debugging Hub')
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set logging level (default: INFO)'
    )
    return parser.parse_args()


def main():
    """应用程序主函数"""
    # 解析命令行参数
    args = parse_args()

    # 配置日志
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger(__name__)

    # 启用高DPI支持
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("UniScope")
    app.setOrganizationName("UniScope")
    app.setApplicationVersion("0.2.0")

    # 注册内置 Widget
    logger.info("Registering built-in widgets...")
    register_builtin_widgets()

    # 加载插件
    logger.info("Loading plugins...")
    plugin_loader = PluginLoader("plugins")
    plugin_count = plugin_loader.load_all_plugins()
    logger.info(f"Loaded {plugin_count} plugin(s)")

    # 创建主窗口
    window = MainWindow()
    window.show()

    logger.info("UniScope started successfully")

    # 进入事件循环
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
