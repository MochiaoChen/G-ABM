class FinancialAgent:
    def __init__(self, agent_id, system_prompt, llm_client, initial_cash=10000, initial_shares=50):
        self.id = agent_id
        self.system_prompt = system_prompt
        self.llm = llm_client
        self.cash = initial_cash
        self.shares = initial_shares
        self.cost_basis = 100.0
        self.inbox = []

    def receive_message(self, msg):
        self.inbox.append(msg)

    def act(self, current_price):
        # 1. 状态计算
        market_val = self.shares * current_price
        unrealized = market_val - (self.shares * self.cost_basis)
        status = "PROFIT" if unrealized > 0 else "LOSS"
        
        rumor = self.inbox[-1] if self.inbox else "No new rumors."
        self.inbox = [] # Clear inbox

        # 2. 构建 Context
        context = f"""
        **Market Status:** Price: ${current_price:.2f}
        **Your Portfolio:** Cash: ${self.cash:.0f}, PnL: {status} (${unrealized:.0f})
        **Rumor Wire:** "{rumor}"
        """

        # 3. LLM 决策
        decision = self.llm.generate_decision(self.system_prompt, context)
        
        if not decision:
            return None

        # 4. 执行交易逻辑 (简化版)
        action = decision.get("action", "HOLD").upper()
        qty = int(decision.get("quantity", 0))

        real_qty = 0
        if action == "BUY":
            max_buy = int(self.cash // current_price)
            real_qty = min(qty, max_buy)
            cost = real_qty * current_price
            self.cash -= cost
            if self.shares + real_qty > 0:
                self.cost_basis = (self.shares * self.cost_basis + cost) / (self.shares + real_qty)
            self.shares += real_qty
            
        elif action == "SELL":
            real_qty = min(qty, self.shares)
            self.cash += real_qty * current_price
            self.shares -= real_qty

        # 注入真实执行结果
        decision['real_action'] = action
        decision['real_qty'] = real_qty
        return decision