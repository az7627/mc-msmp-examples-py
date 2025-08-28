# Minecraft 服务端管理协议示例

语言：[English (US)](./README.md) / 简体中文（中国大陆）

Minecraft 新服务端管理协议(25w35a+)的 Python 示例。包含 GUI 工具、代码片段和通知监听器。一个基于 WebSocket 的现代 RCON 替代方案。

> [!WARNING]
> **安全警告：无身份验证！**
> 
> 当前版本的 Minecraft 服务端管理协议没有任何身份验证方案。
> 
> 请勿将 MSMP 端口（默认：25585）暴露在公网中！任何能访问此端口的人都能获得你 Minecraft 服务器的完全控制权。

## 功能特性

- 图形用户界面 (GUI)，便于服务器管理
- 常见操作的代码示例
- 实时通知监听器，监听服务器事件
- 基于 WebSocket 的 JSON-RPC 实现

## 快速开始

1. 在服务器配置文件中启用管理 API：

```
management-server-enabled=true
management-server-host=localhost
management-server-port=25585
```

2. 克隆此仓库：

```
git clone https://github.com/your-username/mc-msmp-examples-py.git
```

3. 安装依赖：

```
pip install -r requirements.txt
```

4. 运行 GUI：

```
python management-server-gui.py
```

## 项目结构

management-server-gui.py    # 主 GUI 应用程序
simple-example.py           # 基础代码示例
notification-listener.py    # 服务器事件监听器
discover.json               # 协议模式定义
README-zh_cn.md            # 本文件

## 许可证

MIT