"""德州扑克游戏服务端"""

import asyncio
import json
import socket
from typing import Dict, List, Any


class TexasHoldEmServer:
    """德州扑克游戏服务端"""
    def __init__(self, host: str = "localhost", port: int = 8888):
        """初始化服务端
        
        Args:
            host: 主机地址
            port: 端口号
        """
        self.host = host
        self.port = port
        self.server = None
        self.clients = {}
        self.game_state = {
            "players": [],
            "chips": {},
            "pot": 0,
            "current_bet": 0,
            "community_cards": [],
            "player_cards": {},
            "round": "preflop",
            "action_history": []
        }

    async def start(self):
        """启动服务端"""
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        print(f"服务端启动在 {self.host}:{self.port}")
        async with self.server:
            await self.server.serve_forever()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理客户端连接
        
        Args:
            reader: 输入流
            writer: 输出流
        """
        addr = writer.get_extra_info('peername')
        print(f"客户端 {addr} 连接")

        try:
            while True:
                data = await reader.read(1024)
                if not data:
                    break

                message = data.decode().strip()
                print(f"收到来自 {addr} 的消息: {message}")

                # 解析消息
                try:
                    msg = json.loads(message)
                    await self.process_message(msg, writer, addr)
                except json.JSONDecodeError:
                    print(f"无效的JSON消息: {message}")
                    response = {"type": "error", "message": "无效的JSON格式"}
                    writer.write(json.dumps(response).encode() + b"\n")
                    await writer.drain()

        except Exception as e:
            print(f"处理客户端 {addr} 时出错: {e}")
        finally:
            print(f"客户端 {addr} 断开连接")
            writer.close()
            await writer.wait_closed()

    async def process_message(self, msg: Dict[str, Any], writer: asyncio.StreamWriter, addr: tuple):
        """处理消息
        
        Args:
            msg: 消息内容
            writer: 输出流
            addr: 客户端地址
        """
        msg_type = msg.get("type")

        if msg_type == "register":
            await self.handle_register(msg, writer, addr)
        elif msg_type == "action":
            await self.handle_action(msg)
        elif msg_type == "get_game_state":
            await self.handle_get_game_state(writer)
        elif msg_type == "chat":
            await self.handle_chat(msg)
        else:
            response = {"type": "error", "message": "未知的消息类型"}
            writer.write(json.dumps(response).encode() + b"\n")
            await writer.drain()

    async def handle_register(self, msg: Dict[str, Any], writer: asyncio.StreamWriter, addr: tuple):
        """处理注册消息
        
        Args:
            msg: 消息内容
            writer: 输出流
            addr: 客户端地址
        """
        player_name = msg.get("name")
        if not player_name:
            response = {"type": "error", "message": "缺少玩家名称"}
            writer.write(json.dumps(response).encode() + b"\n")
            await writer.drain()
            return

        # 注册玩家
        if player_name not in self.game_state["players"]:
            self.game_state["players"].append(player_name)
            self.game_state["chips"][player_name] = 1000
            self.game_state["player_cards"][player_name] = []

        # 保存客户端连接
        self.clients[player_name] = writer

        response = {"type": "register_success", "player_name": player_name}
        writer.write(json.dumps(response).encode() + b"\n")
        await writer.drain()

        # 广播新玩家加入
        await self.broadcast({"type": "player_joined", "player_name": player_name})

    async def handle_action(self, msg: Dict[str, Any]):
        """处理玩家动作
        
        Args:
            msg: 消息内容
        """
        player_name = msg.get("player_name")
        action = msg.get("action")
        amount = msg.get("amount", 0)

        if not player_name or not action:
            return

        # 记录动作
        action_desc = f"{player_name} 选择了 {action}"
        if action == "raise" and amount > 0:
            action_desc += f" (金额: {amount})"
        self.game_state["action_history"].append(action_desc)

        # 更新游戏状态
        if action == "raise":
            self.game_state["current_bet"] += amount
            self.game_state["chips"][player_name] -= amount
            self.game_state["pot"] += amount
        elif action == "call":
            diff = self.game_state["current_bet"]
            if diff > self.game_state["chips"][player_name]:
                diff = self.game_state["chips"][player_name]
            self.game_state["chips"][player_name] -= diff
            self.game_state["pot"] += diff
        elif action == "all_in":
            all_in_amount = self.game_state["chips"][player_name]
            self.game_state["pot"] += all_in_amount
            self.game_state["chips"][player_name] = 0
            if all_in_amount > self.game_state["current_bet"]:
                self.game_state["current_bet"] = all_in_amount

        # 广播动作
        await self.broadcast({"type": "action", "player_name": player_name, "action": action, "amount": amount})

    async def handle_get_game_state(self, writer: asyncio.StreamWriter):
        """处理获取游戏状态的请求
        
        Args:
            writer: 输出流
        """
        response = {"type": "game_state", "game_state": self.game_state}
        writer.write(json.dumps(response).encode() + b"\n")
        await writer.drain()

    async def handle_chat(self, msg: Dict[str, Any]):
        """处理Agent之间的聊天消息
        
        Args:
            msg: 消息内容
        """
        from_player = msg.get("from")
        to_player = msg.get("to")
        content = msg.get("content")

        if not from_player or not content:
            return

        # 构建聊天消息
        chat_msg = {
            "type": "chat",
            "from": from_player,
            "to": to_player,
            "content": content,
            "timestamp": msg.get("timestamp")
        }

        # 如果to_player是"all"或None，则广播给所有Agent
        if to_player == "all" or to_player is None:
            await self.broadcast(chat_msg, exclude=from_player)
        else:
            # 发送给指定的Agent
            if to_player in self.clients:
                try:
                    writer = self.clients[to_player]
                    writer.write(json.dumps(chat_msg).encode() + b"\n")
                    await writer.drain()
                except Exception as e:
                    print(f"发送消息给 {to_player} 时出错: {e}")

    async def broadcast(self, message: Dict[str, Any], exclude: str = None):
        """广播消息给所有客户端
        
        Args:
            message: 消息内容
            exclude: 排除的玩家名称
        """
        for player_name, writer in self.clients.items():
            if exclude and player_name == exclude:
                continue
            try:
                writer.write(json.dumps(message).encode() + b"\n")
                await writer.drain()
            except Exception as e:
                print(f"广播消息给 {player_name} 时出错: {e}")


if __name__ == "__main__":
    server = TexasHoldEmServer()
    asyncio.run(server.start())
