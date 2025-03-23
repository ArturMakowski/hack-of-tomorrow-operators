class ProfitMaximizingAgent:
    def __init__(self, grid_costs, sale_threshold=0.3, grid_price_threshold=0.6):
        self.grid_costs = grid_costs
        self.sale_threshold = sale_threshold
        self.grid_price_threshold = grid_price_threshold

    def decide(self, step, net_energy, consumption, production, storage_levels):
        current_hour = step % 24
        grid_price = self.grid_costs[current_hour]['purchase']
        sale_price = self.grid_costs[current_hour]['sale']

        should_store = False
        should_discharge = False
        should_sell = False

        storage_not_full = any(level < 0.95 for level in storage_levels)
        storage_has_energy = any(level > 0.1 for level in storage_levels)

        # 👍 Use production and consumption to inform the strategy
        high_production = production > 1.0
        high_consumption = consumption > 1.0

        if net_energy > 0:
            # More energy than needed (surplus)
            if sale_price >= self.sale_threshold or not storage_not_full or high_production:
                should_sell = True
            elif storage_not_full:
                should_store = True

        elif net_energy < 0:
            # Not enough energy (deficit)
            if grid_price >= self.grid_price_threshold and storage_has_energy:
                should_discharge = True
            elif high_consumption and storage_has_energy:
                should_discharge = True

        return {
            'store_energy': should_store,
            'discharge': should_discharge,
            'sell_energy': should_sell
        }
