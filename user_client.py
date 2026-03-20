"""用户客户端"""

import asyncio
from client import TexasHoldEmClient


async def main():
    """主函数"""
    # 创建客户端
    client = TexasHoldEmClient()
    
    # 连接到服务端
    if not await client.connect():
        return
    
    # 注册玩家
    player_name = input("请输入你的玩家名称: ")
    if not await client.register(player_name):
        await client.close()
        return
    
    # 启动消息监听
    asyncio.create_task(client.listen_for_messages())
    
    # 游戏主循环
    try:
        while True:
            # 获取游戏状态
            game_state = await client.get_game_state()
            if not game_state:
                await asyncio.sleep(1)
                continue
            
            # 显示游戏状态
            print("\n=== 当前游戏状态 ===")
            print(f"回合: {game_state.get('round', 'preflop')}")
            print(f"底池: {game_state.get('pot', 0)}")
            print(f"当前下注: {game_state.get('current_bet', 0)}")
            print(f"公共牌: {' '.join(game_state.get('community_cards', []))}")
            print(f"你的筹码: {game_state.get('chips', {}).get(player_name, 0)}")
            print("\n玩家行动历史:")
            for action in game_state.get('action_history', [])[-5:]:  # 显示最近5个行动
                print(f"- {action}")
            
            # 等待用户输入
            print("\n请选择你的动作:")
            print("1. fold (弃牌)")
            print("2. check (过牌)")
            print("3. call (跟注)")
            print("4. raise (加注)")
            print("5. all_in (全下)")
            
            choice = input("请输入选项编号: ")
            
            action_map = {
                "1": "fold",
                "2": "check",
                "3": "call",
                "4": "raise",
                "5": "all_in"
            }
            
            action = action_map.get(choice, "fold")
            amount = 0
            
            if action == "raise":
                amount_str = input("请输入加注金额: ")
                try:
                    amount = int(amount_str)
                except ValueError:
                    amount = 50
            
            # 发送动作
            print(f"你选择了 {action}" + (f" (金额: {amount})" if amount > 0 else ""))
            await client.send_action(action, amount)
            
            # 等待一段时间再进行下一步
            await asyncio.sleep(2)
    except KeyboardInterrupt:
        print("你退出游戏")
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
