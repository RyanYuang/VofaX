# UniScope - Universal Serial Debugging Hub

UniScope 是一个功能强大的跨平台串口调试工具，提供可视化仪表板、实时数据绘图和协议分析功能。

## 快速开始

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
python main.py
```

## 功能特性

### 核心功能
- 🎨 **可拖拽仪表板** - 自由布局你的工作空间
- 📊 **7 种 Widget** - 示波器、终端、HEX查看器、仪表盘、数据表、协议分析器、图表
- 🔌 **多通道数据绑定** - I0-I14 共 15 个独立数据通道
- 🌓 **主题切换** - Dark/Light 主题支持
- 💾 **布局持久化** - JSON 格式保存/加载布局配置

### 智能交互
- ✨ **智能对齐系统** - 类似 Figma/macOS 的 Smart Snap 功能
  - 📏 网格吸附（20px 网格，8px 阈值）
  - 🎯 边缘和中心自动对齐
  - 🔵 实时蓝色辅助线显示
  - 🔧 拖拽和调整大小均支持对齐

### 可视化功能
- 📈 实时波形显示（示波器 Widget）
- 🎚️ 可调时基和 Y 轴范围
- 🔍 HEX/ASCII 数据查看
- 📊 多种图表类型支持

## 开发文档

- [开发计划](Doc/Develop_Plan.md)
- [开发日志](Doc/Develop_log.md)
- [架构指南](CLAUDE.md)

## 许可证

MIT License
