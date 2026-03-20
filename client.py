"""德州扑克游戏客户端"""

import asyncio
import json
from typing import Dict, Any, Optional


class TexasHoldEmClient:
    """德州扑克游戏客户端"""
    def __init__(self, host: str = "localhost", port: int = 8888):
        """初始化客户端
        
        Args:
            host: 服务端主机地址
            port: 服务端端口号
        """
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None
        self.player_name = None
        self.message_queue = asyncio.Queue()
        self.is_listening = False
        self.chat_handlers = []  # 聊天消息处理器列表

    def register_chat_handler(self, handler):
        """注册聊天消息处理器
        
        Args:
            handler: 处理器函数，接收一个参数（消息内容）
        """
        self.chat_handlers.append(handler)

    async def connect(self):
        """连接到服务端"""
        try:
            self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
            print(f"连接到服务端 {self.host}:{self.port}")
            # 启动消息监听
            self.is_listening = True
            asyncio.create_task(self.listen_for_messages())
            return True
        except Exception as e:
            print(f"连接服务端失败: {e}")
            return False

    async def register(self, player_name: str):
        """注册玩家
        
        Args:
            player_name: 玩家名称
        
        Returns:
            bool: 注册是否成功
        """
        if not self.writer:
            print("未连接到服务端")
            return False

        # 发送注册消息
        register_msg = {"type": "register", "name": player_name}
        self.writer.write(json.dumps(register_msg).encode() + b"\n")
        await self.writer.drain()

        # 等待响应
        while True:
            msg = await self.message_queue.get()
            if msg.get("type") == "register_success":
                self.player_name = player_name
                print(f"注册成功，玩家名称: {self.player_name}")
                return True
            elif msg.get("type") == "error":
                print(f"注册失败: {msg.get('message', '未知错误')}")
                return False

    async def send_action(self, action: str, amount: int = 0):
        """发送玩家动作
        
        Args:
            action: 动作类型
            amount: 金额（仅在raise时使用）
        """
        if not self.writer or not self.player_name:
            print("未连接到服务端或未注册")
            return

        action_msg = {
            "type": "action",
            "player_name": self.player_name,
            "action": action,
            "amount": amount
        }
        self.writer.write(json.dumps(action_msg).encode() + b"\n")
        await self.writer.drain()

    async def send_chat(self, content: str, to_player: str = "all"):
        """发送聊天消息给其他Agent
        
        Args:
            content: 消息内容
            to_player: 目标玩家名称，默认为"all"（广播给所有玩家）
        """
        if not self.writer or not self.player_name:
            print("未连接到服务端或未注册")
            return

        import time
        chat_msg = {
            "type": "chat",
            "from": self.player_name,
            "to": to_player,
            "content": content,
            "timestamp": int(time.time())
        }
        self.writer.write(json.dumps(chat_msg).encode() + b"\n")
        await self.writer.drain()
        print(f"[{self.player_name}] 发送消息给 {to_player}: {content}")

    async def get_game_state(self) -> Optional[Dict[str, Any]]:
        """获取游戏状态
        
        Returns:
            Dict[str, Any]: 游戏状态
        """
        if not self.writer:
            print("未连接到服务端")
            return None

        # 发送获取游戏状态的请求
        get_state_msg = {"type": "get_game_state"}
        self.writer.write(json.dumps(get_state_msg).encode() + b"\n")
        await self.writer.drain()

        # 等待响应
        while True:
            msg = await self.message_queue.get()
            if msg.get("type") == "game_state":
                return msg.get("game_state")
            elif msg.get("type") == "error":
                print(f"获取游戏状态失败: {msg.get('message', '未知错误')}")
                return None

    async def listen_for_messages(self):
        """监听服务端消息"""
        if not self.reader:
            print("未连接到服务端")
            return

        try:
            while self.is_listening:
                data = await self.reader.read(1024)
                if not data:
                    break

                message = data.decode().strip()
                try:
                    msg = json.loads(message)
                    # 将消息放入队列
                    await self.message_queue.put(msg)
                    # 处理消息
                    await self.handle_message(msg)
                except json.JSONDecodeError:
                    print(f"无效的JSON消息: {message}")
        except Exception as e:
            print(f"监听消息时出错: {e}")

    async def handle_message(self, msg: Dict[str, Any]):
        """处理服务端消息
        
        Args:
            msg: 消息内容
        """
        msg_type = msg.get("type")

        if msg_type == "player_joined":
            player_name = msg.get("player_name")
            print(f"玩家 {player_name} 加入游戏")
        elif msg_type == "action":
            player_name = msg.get("player_name")
            action = msg.get("action")
            amount = msg.get("amount", 0)
            if action == "raise":
                print(f"玩家 {player_name} 选择了 {action} (金额: {amount})")
            else:
                print(f"玩家 {player_name} 选择了 {action}")
        elif msg_type == "chat":
            # 处理聊天消息
            from_player = msg.get("from")
            to_player = msg.get("to")
            content = msg.get("content")
            print(f"[聊天] {from_player} -> {to_player}: {content}")
            
            # 调用所有注册的聊天消息处理器
            for handler in self.chat_handlers:
                try:
                    await handler(msg)
                except Exception as e:
                    print(f"处理聊天消息时出错: {e}")
        elif msg_type == "game_state":
            # 游戏状态更新，这里可以根据需要处理
            pass
        else:
            print(f"收到未知类型的消息: {msg_type}")

    async def close(self):
        """关闭连接"""
        self.is_listening = False
        if self.writer:
            self.writer.close()
            await self.writer.wait_closed()
            print("连接已关闭")
