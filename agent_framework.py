"""Agent决策框架"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple


class BaseAgent(ABC):
    """基础Agent类"""
    def __init__(self, name: str):
        """初始化Agent
        
        Args:
            name: Agent名称
        """
        self.name = name
    
    @abstractmethod
    async def make_decision(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """做出决策
        
        Args:
            game_state: 游戏状态
        
        Returns:
            Tuple[str, int]: 动作和金额
        """
        pass
    
    def evaluate_hand(self, hand: list) -> int:
        """评估手牌强度
        
        Args:
            hand: 手牌
        
        Returns:
            int: 手牌强度评分
        """
        # 这里简化实现，实际应该根据德州扑克规则评估手牌强度
        # 例如：皇家同花顺、同花顺、四条、葫芦等
        return 0
    
    def analyze_game_state(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """分析游戏状态
        
        Args:
            game_state: 游戏状态
        
        Returns:
            Dict[str, Any]: 分析结果
        """
        analysis = {
            "pot_size": game_state.get("pot", 0),
            "current_bet": game_state.get("current_bet", 0),
            "community_cards": game_state.get("community_cards", []),
            "action_history": game_state.get("action_history", []),
            "players": game_state.get("players", []),
            "chips": game_state.get("chips", {})
        }
        return analysis


class AggressiveAgent(BaseAgent):
    """激进型Agent"""
    async def make_decision(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """做出决策
        
        Args:
            game_state: 游戏状态
        
        Returns:
            Tuple[str, int]: 动作和金额
        """
        analysis = self.analyze_game_state(game_state)
        
        # 激进型策略：有好牌就加注
        hand_strength = self.evaluate_hand(game_state.get("player_cards", {}).get(self.name, []))
        
        if hand_strength > 70:
            # 强牌，大额加注
            return "raise", min(analysis["chips"].get(self.name, 0), analysis["pot_size"] * 2)
        elif hand_strength > 40:
            # 中等牌，小额加注
            return "raise", min(analysis["chips"].get(self.name, 0), analysis["pot_size"])
        elif hand_strength > 20:
            # 弱牌，跟注
            return "call", 0
        else:
            # 很差的牌，弃牌
            return "fold", 0


class ConservativeAgent(BaseAgent):
    """保守型Agent"""
    async def make_decision(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """做出决策
        
        Args:
            game_state: 游戏状态
        
        Returns:
            Tuple[str, int]: 动作和金额
        """
        analysis = self.analyze_game_state(game_state)
        
        # 保守型策略：只在有很强的牌时才下注
        hand_strength = self.evaluate_hand(game_state.get("player_cards", {}).get(self.name, []))
        
        if hand_strength > 85:
            # 非常强的牌，加注
            return "raise", min(analysis["chips"].get(self.name, 0), analysis["pot_size"])
        elif hand_strength > 60:
            # 强牌，跟注
            return "call", 0
        else:
            # 其他情况，弃牌
            return "fold", 0


class TechnicalAgent(BaseAgent):
    """技术型Agent"""
    async def make_decision(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """做出决策
        
        Args:
            game_state: 游戏状态
        
        Returns:
            Tuple[str, int]: 动作和金额
        """
        analysis = self.analyze_game_state(game_state)
        
        # 技术型策略：分析对手行为
        hand_strength = self.evaluate_hand(game_state.get("player_cards", {}).get(self.name, []))
        opponent_actions = self.analyze_opponent_actions(analysis["action_history"])
        
        # 根据对手行为调整策略
        if opponent_actions.get("aggressive", False):
            # 对手很激进，需要更谨慎
            if hand_strength > 75:
                return "raise", min(analysis["chips"].get(self.name, 0), analysis["pot_size"])
            elif hand_strength > 50:
                return "call", 0
            else:
                return "fold", 0
        else:
            # 对手比较保守，可以更主动
            if hand_strength > 60:
                return "raise", min(analysis["chips"].get(self.name, 0), analysis["pot_size"] * 1.5)
            elif hand_strength > 30:
                return "call", 0
            else:
                return "fold", 0
    
    def analyze_opponent_actions(self, action_history: list) -> Dict[str, bool]:
        """分析对手行为
        
        Args:
            action_history: 动作历史
        
        Returns:
            Dict[str, bool]: 对手行为分析
        """
        aggressive_count = 0
        total_actions = 0
        
        for action in action_history:
            if "raise" in action or "all_in" in action:
                aggressive_count += 1
            total_actions += 1
        
        return {
            "aggressive": aggressive_count / total_actions > 0.3 if total_actions > 0 else False
        }


class LuckyAgent(BaseAgent):
    """幸运型Agent"""
    async def make_decision(self, game_state: Dict[str, Any]) -> Tuple[str, int]:
        """做出决策
        
        Args:
            game_state: 游戏状态
        
        Returns:
            Tuple[str, int]: 动作和金额
        """
        analysis = self.analyze_game_state(game_state)
        
        # 幸运型策略：喜欢冒险尝试
        hand_strength = self.evaluate_hand(game_state.get("player_cards", {}).get(self.name, []))
        
        import random
        luck_factor = random.random()  # 幸运因子
        
        if hand_strength > 50 or luck_factor > 0.7:
            # 中等牌或运气好，加注或全下
            if luck_factor > 0.8:
                return "all_in", 0
            else:
                return "raise", min(analysis["chips"].get(self.name, 0), analysis["pot_size"] * 1.5)
        elif hand_strength > 20 or luck_factor > 0.5:
            # 弱牌或运气一般，跟注
            return "call", 0
        else:
            # 很差的牌且运气不好，弃牌
            return "fold", 0
