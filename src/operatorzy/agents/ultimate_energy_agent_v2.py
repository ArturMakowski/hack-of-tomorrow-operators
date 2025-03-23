import numpy as np

class UltimateEnergyAgentV2:
    def __init__(
        self,
        grid_costs,
        forecast_horizon=6,
        sell_threshold=0.35,
        grid_threshold=0.6,
        morning_peak=(6, 9),
        evening_peak=(17, 21),
        high_demand_threshold=1.0,
        high_production_threshold=1.2
    ):
        self.grid_costs = grid_costs
        self.forecast_horizon = forecast_horizon
        self.sell_threshold = sell_threshold
        self.grid_threshold = grid_threshold
        self.morning_peak = morning_peak
        self.evening_peak = evening_peak
        self.high_demand_threshold = high_demand_threshold
        self.high_production_threshold = high_production_threshold

    def forecast_net_energy(self, net_energy_history):
        window = min(len(net_energy_history), self.forecast_horizon)
        if window == 0:
            return 0
        return np.mean(net_energy_history[-window:])

    def in_peak_hour(self, hour):
        return self.morning_peak[0] <= hour < self.morning_peak[1] or \
               self.evening_peak[0] <= hour < self.evening_peak[1]

    def decide(self, step, net_energy, consumption, production, storage_levels, net_energy_history):
        current_hour = step % 24
        sale_price = self.grid_costs[current_hour]['sale']
        grid_price = self.grid_costs[current_hour]['purchase']

        forecast = self.forecast_net_energy(net_energy_history)
        storage_not_full = any(level < 0.95 for level in storage_levels)
        storage_has_energy = any(level > 0.05 for level in storage_levels)
        all_storage_full = all(level > 0.95 for level in storage_levels)

        decision = {'store_energy': False, 'discharge': False, 'sell_energy': False}

        # ✅ 1. If there's ANY deficit → try discharging storage
        if net_energy < 0 and storage_has_energy:
            decision['discharge'] = True

        # 🌞 2. High production → store or sell
        if production > self.high_production_threshold:
            if storage_not_full:
                decision['store_energy'] = True
            elif sale_price >= self.sell_threshold:
                decision['sell_energy'] = True

        # 📈 3. Forecast deficit + peak + high grid → pre-discharge
        if forecast < -0.5 and self.in_peak_hour(current_hour) and grid_price >= self.grid_threshold:
            if storage_has_energy:
                decision['discharge'] = True

        # 💰 4. Forecast surplus + full battery → sell
        if forecast > 0.5 and all_storage_full and sale_price >= self.sell_threshold:
            decision['sell_energy'] = True

        # 🌼 5. Net surplus now → store or sell
        if net_energy > 0:
            if storage_not_full:
                decision['store_energy'] = True
            elif sale_price >= self.sell_threshold:
                decision['sell_energy'] = True

        # ⚡ 6. Sitting on full battery and sale price is high
        if all_storage_full and sale_price >= self.sell_threshold:
            decision['sell_energy'] = True

        return decision
