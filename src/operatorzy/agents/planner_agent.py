class PlannerAgent:
    def __init__(self, grid_costs, lookahead=4, grid_price_threshold=0.6, sell_price_threshold=0.35, high_prod_threshold=1.5):
        self.grid_costs = grid_costs
        self.lookahead = lookahead
        self.grid_price_threshold = grid_price_threshold
        self.sell_price_threshold = sell_price_threshold
        self.high_prod_threshold = high_prod_threshold  # What counts as 'high' production now

    def decide(self, step, net_energy, consumption, production, storage_levels, future_data):
        current_hour = step % 24
        grid_price = self.grid_costs[current_hour]['purchase']
        sale_price = self.grid_costs[current_hour]['sale']

        storage_not_full = any(level < 0.95 for level in storage_levels)
        storage_has_energy = any(level > 0.1 for level in storage_levels)

        future_net_energy = sum(f['production'] - f['consumption'] for f in future_data[:self.lookahead])
        future_peak_price = max([self.grid_costs[(step + i) % 24]['purchase'] for i in range(1, self.lookahead + 1)])

        # CASE 1: High current production → prefer to store or sell
        if production > self.high_prod_threshold:
            if storage_not_full:
                return {'store_energy': True, 'discharge': False, 'sell_energy': False}
            elif sale_price >= self.sell_price_threshold:
                return {'store_energy': False, 'discharge': False, 'sell_energy': True}

        # CASE 2: Future deficit + expensive grid → charge now or discharge later
        if future_net_energy < 0 and future_peak_price >= self.grid_price_threshold:
            if net_energy > 0 and storage_not_full:
                return {'store_energy': True, 'discharge': False, 'sell_energy': False}
            elif net_energy < 0 and storage_has_energy:
                return {'store_energy': False, 'discharge': True, 'sell_energy': False}
            else:
                return {'store_energy': False, 'discharge': False, 'sell_energy': False}

        # CASE 3: High consumption and low current production → discharge if possible
        if consumption > 1.0 and production < 0.5 and grid_price > self.grid_price_threshold and storage_has_energy:
            return {'store_energy': False, 'discharge': True, 'sell_energy': False}

        # CASE 4: Surplus now and future has no need → sell if price is attractive
        if net_energy > 0:
            if sale_price >= self.sell_price_threshold or not storage_not_full:
                return {'store_energy': False, 'discharge': False, 'sell_energy': True}
            elif storage_not_full:
                return {'store_energy': True, 'discharge': False, 'sell_energy': False}

        # CASE 5: Moderate deficit now, expect future surplus → wait or use grid
        if net_energy < 0 and future_net_energy > 0:
            return {'store_energy': False, 'discharge': False, 'sell_energy': False}

        # CASE 6: Default fallback
        return {'store_energy': False, 'discharge': False, 'sell_energy': False}
