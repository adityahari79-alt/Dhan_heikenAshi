class PositionManager:
    def __init__(self, entry_price, profit_target_pct=10, stop_loss_pct=1, trailing_stop_pct=1):
        self.entry_price = entry_price
        self.profit_target = entry_price * (1 + profit_target_pct / 100)
        self.stop_loss = entry_price * (1 - stop_loss_pct / 100)
        self.trailing_stop_pct = trailing_stop_pct
        self.highest_price = entry_price

    def update(self, current_price):
        # Update trailing stop loss if price moves in favor
        if current_price > self.highest_price:
            self.highest_price = current_price
            self.stop_loss = self.highest_price * (1 - self.trailing_stop_pct / 100)

        # Check if exit conditions are met
        if current_price >= self.profit_target:
            return 'TAKE_PROFIT'
        elif current_price <= self.stop_loss:
            return 'STOP_LOSS'
        else:
            return None
