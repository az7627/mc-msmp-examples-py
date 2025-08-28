# Minecraft Server Management Protocol Examples

Language: English (US) / [简体中文（中国大陆）](./README-zh_cn.md)

Python examples for Minecraft's new Server Management Protocol (25w35a+). Features a GUI client, code snippets & a notification listener. A modern WebSocket alternative to RCON.

> [!WARNING]
> **Security Warning: No Authentication!**
> 
> The current implementation of the Minecraft Server Management Protocol has no authentication mechanism. 
> 
> NEVER expose the MSMP port (default: 25585) to the public internet! Anyone with access to this port can gain full control of your Minecraft server.

## Features

- Graphical User Interface (GUI) for easy server management
- Code examples for common operations
- Real-time notification listener for server events
- WebSocket-based JSON-RPC implementation

## Quick Start

1. Enable the management API in your server properties:

```
management-server-enabled=true
management-server-host=localhost
management-server-port=25585
```

2. Clone this repository:

```
git clone https://github.com/your-username/mc-msmp-examples-py.git
```

3. Install dependencies:

```
pip install -r requirements.txt
```

4. Run the GUI:

```
python management-server-gui.py
```

## Project Structure

management-server-gui.py    # Main GUI application
simple-example.py           # Basic code examples
notification-listener.py    # Server event listener
discover.json               # Protocol schema
README.md                   # This file

## License

MIT