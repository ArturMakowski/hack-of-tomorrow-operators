class ActiveStorageAgent:
    def __init__(self, grid_costs, sell_price_threshold=0.3, grid_price_threshold=0.5):
        self.grid_costs = grid_costs
        self.sell_price_threshold = sell_price_threshold
        self.grid_price_threshold = grid_price_threshold

    def decide(self, step, net_energy, consumption, production, storage_levels):
        current_hour = step % 24
        sale_price = self.grid_costs[current_hour]['sale']
        grid_price = self.grid_costs[current_hour]['purchase']

        storage_not_full = any(level < 0.95 for level in storage_levels)
        storage_has_energy = any(level > 0.05 for level in storage_levels)

        should_store = False
        should_sell = False
        should_discharge = False

        # 🌞 Surplus: try storing, or sell if storage is full
        if net_energy > 0:
            if storage_not_full:
                should_store = True
            elif sale_price >= self.sell_price_threshold:
                should_sell = True

        # 🌒 Deficit: use storage if available
        elif net_energy < 0:
            if storage_has_energy:
                should_discharge = True

        # 🔥 If sale price is great and storage is full → sell even without new surplus
        if not should_sell and sale_price >= self.sell_price_threshold and all(level > 0.9 for level in storage_levels):
            should_sell = True

        return {
            'store_energy': should_store,
            'discharge': should_discharge,
            'sell_energy': should_sell
        }
