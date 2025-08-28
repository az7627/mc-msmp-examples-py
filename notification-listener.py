import asyncio
import websockets
import json
import logging
import colorlog

colorlog.basicConfig(
    format='%(log_color)s[%(asctime)s %(levelname)s]\t %(message)s',
    level=logging.DEBUG,
    log_colors={
        'DEBUG': 'green',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)

class MinecraftManagementClient:
    def __init__(self, host="localhost", port=25585):
        self.uri = f"ws://{host}:{port}"
        self.websocket = None
        
    async def connect(self):
        """连接到 Minecraft 服务器管理协议"""
        try:
            self.websocket = await websockets.connect(self.uri)
            logging.info(f"已连接到 Minecraft 服务器管理协议: {self.uri}")
            return True
        except Exception as e:
            logging.error(f"连接失败: {e}")
            return False
    
    async def listen_for_notifications(self):
        """监听服务器通知"""
        if not self.websocket:
            logging.error("未连接到服务器")
            return
            
        try:
            logging.info("开始监听服务器通知...")
            
            # 持续监听消息
            async for message in self.websocket:
                data = json.loads(message)
                
                # 检查是否是通知（通知通常没有 'id' 字段）
                if "method" in data and data["method"].startswith("notification:"):
                    await self.handle_notification(data)
                else:
                    # 这是对之前请求的响应
                    logging.info(f"收到响应: {data}")
                    
        except websockets.exceptions.ConnectionClosed:
            logging.info("连接已关闭")
        except Exception as e:
            logging.error(f"监听过程中发生错误: {e}")
    
    async def handle_notification(self, notification):
        """处理不同类型的通知"""
        method = notification["method"]
        params = notification.get("params", [])
        
        logging.info(f"收到通知: {method}")
        
        # 根据通知类型进行不同处理
        if method == "notification:players/joined":
            player = params[0] if params else {}
            player_name = player.get("name", "未知玩家")
            player_id = player.get("id", "未知ID")
            logging.info(f"🎮 玩家 {player_name} ({player_id}) 加入了游戏!")
            
        elif method == "notification:players/left":
            player = params[0] if params else {}
            player_name = player.get("name", "未知玩家")
            logging.info(f"👋 玩家 {player_name} 离开了游戏")
            
        elif method == "notification:allowlist/added":
            player = params[0] if params else {}
            player_name = player.get("name", "未知玩家")
            logging.info(f"✅ 玩家 {player_name} 已被添加到白名单")
            
        elif method == "notification:allowlist/removed":
            player = params[0] if params else {}
            player_name = player.get("name", "未知玩家")
            logging.info(f"❌ 玩家 {player_name} 已被从白名单移除")
            
        elif method == "notification:operators/added":
            operator = params[0] if params else {}
            player_name = operator.get("player", {}).get("name", "未知玩家")
            level = operator.get("permissionLevel", "未知")
            logging.info(f"⭐ 玩家 {player_name} 被设置为管理员 (权限等级: {level})")
            
        elif method == "notification:operators/removed":
            operator = params[0] if params else {}
            player_name = operator.get("player", {}).get("name", "未知玩家")
            logging.info(f"🔻 玩家 {player_name} 的管理员权限已被移除")
            
        elif method == "notification:gamerules/updated":
            gamerule = params[0] if params else {}
            rule_key = gamerule.get("key", "未知规则")
            rule_value = gamerule.get("value", "未知值")
            logging.info(f"⚙️ 游戏规则 {rule_key} 已被修改为: {rule_value}")
            
        elif method == "notification:server/started":
            logging.info("🟢 服务器已启动")
            
        elif method == "notification:server/stopping":
            logging.info("🔴 服务器正在关闭")
            
        elif method == "notification:server/saving":
            logging.info("💾 服务器正在保存")
            
        elif method == "notification:server/saved":
            logging.info("✅ 服务器保存完成")
            
        elif method == "notification:server/status":
            status = params[0] if params else {}
            player_count = len(status.get("players", []))
            started = status.get("started", False)
            status_msg = "运行中" if started else "未运行"
            logging.info(f"📊 服务器状态心跳: {status_msg}, 在线玩家: {player_count}")
            
        else:
            # 处理其他未知类型的通知
            logging.info(f"未知通知类型: {method}, 参数: {params}")
    
    async def close(self):
        """关闭连接"""
        if self.websocket:
            await self.websocket.close()
            logging.info("连接已关闭")

async def main():
    # 创建客户端实例
    client = MinecraftManagementClient("localhost", 25585)
    
    # 连接到服务器
    if not await client.connect():
        return
        
    try:
        # 开始监听通知
        await client.listen_for_notifications()
    except KeyboardInterrupt:
        logging.info("用户中断程序")
    finally:
        # 确保连接被正确关闭
        await client.close()

if __name__ == "__main__":
    # 使用 asyncio.run() 运行主函数
    asyncio.run(main())