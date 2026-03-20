"""David Agent - 幸运型玩家"""

import asyncio
import sys
import os

# 添加父目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入AgentScope
import agentscope
from agentscope.agent import ReActAgent
from agentscope.model import OpenAIChatModel
from agentscope.formatter import OpenAIChatFormatter
from agentscope.memory import InMemoryMemory
from agentscope.message import Msg

# 导入客户端
from client import TexasHoldEmClient


# 全局变量，存储接收到的聊天消息
received_messages = []


async def chat_handler(msg):
    """处理接收到的聊天消息
    
    Args:
        msg: 消息内容
    """
    global received_messages
    from_player = msg.get("from")
    content = msg.get("content")
    
    # 将消息添加到列表中
    received_messages.append(f"{from_player}: {content}")
    
    # 只保留最近10条消息
    if len(received_messages) > 10:
        received_messages = received_messages[-10:]


async def main():
    """主函数"""
    # 初始化AgentScope
    agentscope.init()
    
    # 创建OpenAI模型
    model = OpenAIChatModel(
        model_name="deepseek-ai/DeepSeek-V3.2",
        api_key="sk-siwowhdendweuarvcstyyhjqthzqjdvkixsrmwwwmphnklgb",
        client_kwargs={"base_url": "https://api.siliconflow.cn/v1"},
        stream=True,
    )
    
    # 创建幸运型Agent
    agent = ReActAgent(
        name="David",
        sys_prompt="""你是一个幸运型的德州扑克玩家，名字是 David。
你喜欢冒险尝试，相信自己的运气。
可用的动作包括: fold(弃牌), check(过牌), call(跟注), raise(加注), all_in(全下)
请用中文回复，只返回动作名称。
示例回复格式: call
""",
        model=model,
        memory=InMemoryMemory(),
        formatter=OpenAIChatFormatter(),
    )
    
    # 创建客户端
    client = TexasHoldEmClient()
    
    # 注册聊天消息处理器
    client.register_chat_handler(chat_handler)
    
    # 连接到服务端
    if not await client.connect():
        return
    
    # 注册玩家
    if not await client.register("David"):
        await client.close()
        return
    
    # 模拟游戏过程
    try:
        while True:
            # 获取游戏状态
            game_state = await client.get_game_state()
            if not game_state:
                await asyncio.sleep(1)
                continue
            
            # 检查是否轮到自己行动
            # 这里简化处理，实际应该根据游戏状态判断
            await asyncio.sleep(2)
            
            # 构建游戏状态提示
            state = game_state.get("state", {})
            
            # 构建其他玩家的聊天消息
            chat_context = ""
            if received_messages:
                chat_context = f"""
- 其他玩家的聊天消息:
{chr(10).join(received_messages[-5:])}
"""
            
            prompt = f"""当前游戏状态:
- 回合: {state.get('round', 'preflop')}
- 你的手牌: {state.get('player_cards', {}).get('David', '未知')}
- 公共牌: {state.get('community_cards', '无')}
- 当前下注: {state.get('current_bet', 0)}
- 底池: {state.get('pot', 0)}
- 你的筹码: {state.get('chips', {}).get('David', 0)}
- 其他玩家行动历史:
{chr(10).join(state.get('action_history', []))}
{chat_context}
可选动作: fold, check, call, raise, all_in
请选择一个动作并说明理由，格式: 动作|加注金额(如果选择raise)
"""
            
            # 使用AgentScope的Agent做出决策
            msg = Msg(content=prompt, role="user", name="Dealer")
            response = await agent(msg)
            
            # 提取响应内容
            if hasattr(response, 'content'):
                reply = response.content
            else:
                reply = str(response)
            
            # 处理响应 - 可能是列表或字符串
            if isinstance(reply, list):
                # 如果是列表，取第一个元素
                reply = reply[0] if reply else ""
            
            # 确保reply是字符串
            reply = str(reply)
            
            # 处理响应
            parts = reply.split("|")
            action = parts[0].strip().lower()
            amount = 0
            if action == "raise" and len(parts) > 1:
                try:
                    amount = int(parts[1].strip())
                except ValueError:
                    amount = 50
            
            print(f"David 选择了 {action}" + (f" (金额: {amount})" if amount > 0 else ""))
            await client.send_action(action, amount)
            
            # 发送聊天消息给其他Agent
            if action == "all_in":
                await client.send_chat(f"我相信我的运气！全下！", "all")
            elif action in ["raise", "call"]:
                await client.send_chat(f"感觉不错，我选择{action}！", "all")
            elif action == "check":
                await client.send_chat(f"先看看情况，运气还在后头呢！", "all")
            
            # 等待一段时间再进行下一步
            await asyncio.sleep(5)
    except KeyboardInterrupt:
        print("David 退出游戏")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
