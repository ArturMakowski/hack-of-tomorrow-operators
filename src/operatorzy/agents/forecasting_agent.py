import numpy as np

class ForecastingTraderAgent:
    def __init__(self, grid_costs, forecast_horizon=8, sell_threshold=0.15, grid_threshold=0.50, risk_level=0.85):
        self.grid_costs = grid_costs
        self.forecast_horizon = forecast_horizon
        self.sell_threshold = sell_threshold
        self.grid_threshold = grid_threshold
        self.risk_level = risk_level  # 0 = safe, 1 = aggressive

    def forecast_net_energy(self, net_energy_history):
        window = min(len(net_energy_history), self.forecast_horizon)
        if window == 0:
            return 0
        return np.mean(net_energy_history[-window:])

    def decide(self, step, net_energy, consumption, production, storage_levels, net_energy_history):
        current_hour = step % 24
        sale_price = self.grid_costs[current_hour]['sale']
        grid_price = self.grid_costs[current_hour]['purchase']

        forecast = self.forecast_net_energy(net_energy_history)
        storage_not_full = any(level < 0.95 for level in storage_levels)
        storage_has_energy = any(level > 0.05 for level in storage_levels)

        decision = {'store_energy': False, 'discharge': False, 'sell_energy': False}

        high_production = production > 1.0
        high_consumption = consumption > 1.0

        # 🌞 High production → store or sell
        if high_production:
            if storage_not_full:
                decision['store_energy'] = True
            elif sale_price >= self.sell_threshold * self.risk_level:
                decision['sell_energy'] = True

        # 🔮 Forecasted surplus + current surplus → sell
        elif net_energy > 0 and forecast > 0.5:
            if sale_price >= self.sell_threshold * self.risk_level:
                decision['sell_energy'] = True
            elif storage_not_full:
                decision['store_energy'] = True

        # 🌒 Deficit now or forecasted → discharge
        if net_energy < 0 or forecast < -0.5:
            if (grid_price >= self.grid_threshold * (2 - self.risk_level) or high_consumption) and storage_has_energy:
                decision['discharge'] = True

        # 💰 Backup plan: sell if storage is basically full and price is OK
        if not decision['sell_energy'] and all(level > 0.9 for level in storage_levels):
            if sale_price >= self.sell_threshold:
                decision['sell_energy'] = True

        return decision
