import numpy as np
import random

class HybridEnergyAgent:
    def __init__(
        self,
        grid_costs,
        forecast_horizon=15,
        sell_threshold=0.2,
        grid_price_threshold=0.3,
        peak_morning=(6, 9),
        peak_evening=(17, 21),
        high_production_threshold=0.7,
        high_consumption_threshold=0.8,
        aggressive_mode=True,
        montecarlo_trials=100,
        chaos_mode=True
    ):
        self.grid_costs = grid_costs
        self.forecast_horizon = forecast_horizon
        self.sell_threshold = sell_threshold
        self.grid_price_threshold = grid_price_threshold
        self.peak_morning = peak_morning
        self.peak_evening = peak_evening
        self.high_production_threshold = high_production_threshold
        self.high_consumption_threshold = high_consumption_threshold
        self.aggressive_mode = aggressive_mode
        self.montecarlo_trials = montecarlo_trials
        self.chaos_mode = chaos_mode  # unleash wild behavior for massive gains

    def in_peak(self, hour):
        return self.peak_morning[0] <= hour < self.peak_morning[1] or \
               self.peak_evening[0] <= hour < self.peak_evening[1]

    def forecast_net_energy(self, net_energy_history):
        window = min(len(net_energy_history), self.forecast_horizon)
        if window == 0:
            return 0
        return np.mean(net_energy_history[-window:])

    def montecarlo_expected_gain(self, sale_price, discharge_probability=0.6):
        gains = []
        for _ in range(self.montecarlo_trials):
            sell = random.random() < discharge_probability
            gamble_multiplier = 1 + random.uniform(-0.2, 0.9)  # even more volatile gamble
            gains.append(sale_price * gamble_multiplier if sell else -sale_price * 0.2)  # small penalty if it fails
        return np.mean(gains)

    def decide(self, step, net_energy, consumption, production, storage_levels, net_energy_history):
        hour = step % 24
        sale_price = self.grid_costs[hour]['sale']
        grid_price = self.grid_costs[hour]['purchase']

        forecast = self.forecast_net_energy(net_energy_history)
        storage_not_full = any(level < 0.9 for level in storage_levels)
        storage_has_energy = any(level > 0.1 for level in storage_levels)
        storage_full = all(level > 0.9 for level in storage_levels)

        decision = {'store_energy': False, 'discharge': False, 'sell_energy': False}

        # 1. Always use storage to cover deficit
        if net_energy < 0 and storage_has_energy:
            decision['discharge'] = True

        # 2. Monte Carlo + Chaos: sell if simulated outcome is juicy
        expected_gain = self.montecarlo_expected_gain(sale_price, discharge_probability=0.9 if self.chaos_mode else 0.6)
        if (expected_gain >= self.sell_threshold or storage_full) and storage_has_energy:
            decision['sell_energy'] = True

        # 3. Store excess if we have production
        if net_energy > 0 and storage_not_full and production >= self.high_production_threshold:
            decision['store_energy'] = True

        # 4. If high consumption and grid is expensive → discharge
        if consumption >= self.high_consumption_threshold and grid_price >= self.grid_price_threshold and storage_has_energy:
            decision['discharge'] = True

        # 5. Forecast says surplus is coming, free up space now
        if forecast > 0.5 and storage_full and sale_price >= self.sell_threshold:
            decision['sell_energy'] = True

        # 6. Aggressive mode: always gamble with prices
        if self.aggressive_mode:
            if random.random() < 0.6 and sale_price >= self.sell_threshold * 0.7 and storage_has_energy:
                decision['sell_energy'] = True
            if random.random() < 0.5 and grid_price >= self.grid_price_threshold * 0.7 and storage_has_energy:
                decision['discharge'] = True

        # 7. Chaos Mode: wild coin flips and occasional madness
        if self.chaos_mode and storage_has_energy:
            if random.random() < 0.33:
                decision['sell_energy'] = True
            if random.random() < 0.33:
                decision['discharge'] = True
            if random.random() < 0.1 and storage_not_full:
                decision['store_energy'] = True

        return decision