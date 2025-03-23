class SmartAgent:
    def __init__(self, grid_costs, window=3):
        self.grid_costs = grid_costs
        self.window = window

    def predict_demand(self, history):
        if len(history) < self.window:
            return sum(history) / len(history)
        return sum(history[-self.window:]) / self.window

    def should_store_energy(self, current_hour, storage_levels, production):
        """Store energy if price is expected to rise and storage has room.
           If production is low, prioritize storage over selling."""
        future_hours = range(current_hour+1, min(current_hour+4, 24))
        future_prices = [self.grid_costs[h % 24]['purchase'] for h in future_hours]
        current_price = self.grid_costs[current_hour % 24]['purchase']
        storage_not_full = any(level < 0.95 for level in storage_levels)

        low_production = production < 0.5  # tune this threshold

        return (max(future_prices) > current_price or low_production) and storage_not_full

    def should_discharge(self, current_hour, storage_levels, consumption):
        grid_price = self.grid_costs[current_hour % 24]['purchase']
        storage_has_energy = any(level > 0.1 for level in storage_levels)
        return grid_price > 0.6 and storage_has_energy and consumption > 0.5

    def decide(self, step, net_energy, consumption, production, storage_levels):
        current_hour = step % 24

        if net_energy > 0:
            return {
                'store_energy': self.should_store_energy(current_hour, storage_levels, production),
                'discharge': False
            }

        elif net_energy < 0:
            return {
                'store_energy': False,
                'discharge': self.should_discharge(current_hour, storage_levels, consumption)
            }

        return {
            'store_energy': False,
            'discharge': False
        }
