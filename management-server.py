import asyncio
import websockets
import json

async def manage_server():
    # 管理协议的 WebSocket 地址
    uri = "ws://localhost:25585"
    
    async with websockets.connect(uri) as websocket:
        print("已连接到 Minecraft 服务器管理协议。")
        
        # 1. 发现可用的方法（可选）
        discover_request = {
            "id": 1,
            "method": "rpc.discover"
        }
        await websocket.send(json.dumps(discover_request))
        discover_response = await websocket.recv()
        print("可用的方法列表:", discover_response)

        # 2. 获取当前在线玩家 - 使用正确的方法名
        get_players_request = {
            "id": 2,
            "method": "minecraft:players"
        }
        await websocket.send(json.dumps(get_players_request))
        players_response = await websocket.recv()
        print("在线玩家信息:", players_response)

        # 3. 踢出 az7627
        kick_players = {
            "id": 1,
            "method": "minecraft:players/kick",
            "params": [
                {
                    "message": {
                        "literal": "test"
                    },
                    "players": [
                        {
                            "name": "az7627"
                        }
                    ]
                }
            ]
        }
        print(kick_players)
        await websocket.send(json.dumps(kick_players))
        kick_response = await websocket.recv()
        print(kick_response)

        # 您可以继续发送其他请求...

# 使用 asyncio.run() 而不是 get_event_loop()
asyncio.run(manage_server())