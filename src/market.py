import random
import numpy as np

class MarketEnvironment:
    """
    MarketEnvironment 负责维护市场状态、计算价格冲击以及管理信息传播网络。
    """
    def __init__(self, initial_price: float, sensitivity: float = 0.005, noise_level: float = 0.5):
        self.price = initial_price
        self.sensitivity = sensitivity  # 价格对订单流的敏感度 (Price Impact)
        self.noise_level = noise_level  # 市场随机噪音
        self.round_history = []
        
    def calculate_price_impact(self, buy_vol: int, sell_vol: int):
        """
        根据净订单流 (Net Order Flow) 更新价格。
        使用简化的线性冲击模型 (Linear Impact Model)。
        """
        net_flow = buy_vol - sell_vol
        
        # 核心公式: P_t+1 = P_t * (1 + lambda * NetFlow) + Noise
        impact = net_flow * self.sensitivity
        noise = random.uniform(-self.noise_level, self.noise_level)
        
        # 更新价格 (防止价格为负)
        prev_price = self.price
        self.price = max(1.0, self.price * (1 + impact) + noise)
        
        return self.price, (self.price - prev_price)

    def gossip_protocol(self, agents, decisions):
        """
        执行流言传播机制 (Gossip Protocol)。
        目前实现：随机配对传播 (Random Pairwise Exchange)。
        """
        # 只有做出了决策且有新流言的 Agent 才会传播
        active_spreaders = [
            (i, d['mutated_rumor']) 
            for i, d in enumerate(decisions) 
            if d and d.get('mutated_rumor')
        ]
        
        if not active_spreaders:
            return

        # 随机选择接收者 (Target)
        # 在更复杂的版本中，这里可以是 Small-world Network 或 Scale-free Network
        for sender_id, rumor in active_spreaders:
            # 随机选 1-2 个接收者，排除自己
            potential_targets = [a for a in agents if a.id != sender_id]
            if potential_targets:
                targets = random.sample(potential_targets, k=min(2, len(potential_targets)))
                for target in targets:
                    target.receive_message(rumor)

    def log_round(self, round_num, price, volatility, buy_vol, sell_vol):
        self.round_history.append({
            "round": round_num,
            "price": price,
            "volatility": volatility,
            "volume": buy_vol + sell_vol
        })