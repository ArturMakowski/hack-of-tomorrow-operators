# src/agents/energy_optimization_agent.py

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler

from operatorzy.models.cooperative import Cooperative


class EnergyOptimizationAgent:
    def __init__(self, config, initial_token_balance=100):
        """Initialize the Energy Optimization Agent with configuration."""
        self.cooperative = Cooperative(config, initial_token_balance)
        self.storages = self.cooperative.storages
        self.consumption_model = None
        self.production_model = None
        self.price_model = None
        self.scaler_consumption = StandardScaler()
        self.scaler_production = StandardScaler()
        self.scaler_price = StandardScaler()
        self.forecast_horizon = 24  # Hours to forecast ahead
        self.historical_data = []
        self.token_balance = initial_token_balance
        self.storage_strategy = (
            "dynamic"  # Can be 'dynamic', 'conservative', 'aggressive'
        )

    def train_forecasting_models(self, historical_data):
        """Train machine learning models to forecast consumption, production, and prices."""
        # Prepare data
        X = self._prepare_features(historical_data)
        y_consumption = np.array([d["consumption"] for d in historical_data])
        y_production = np.array([d["production"] for d in historical_data])
        y_price = np.array([d["grid_price"] for d in historical_data])

        # Scale data
        X_scaled = self.scaler_consumption.fit_transform(X)
        y_consumption_scaled = self.scaler_consumption.fit_transform(
            y_consumption.reshape(-1, 1)
        ).flatten()
        y_production_scaled = self.scaler_production.fit_transform(
            y_production.reshape(-1, 1)
        ).flatten()
        y_price_scaled = self.scaler_price.fit_transform(
            y_price.reshape(-1, 1)
        ).flatten()

        # Train models
        self.consumption_model = RandomForestRegressor(n_estimators=100)
        self.consumption_model.fit(X_scaled, y_consumption_scaled)

        self.production_model = RandomForestRegressor(n_estimators=100)
        self.production_model.fit(X_scaled, y_production_scaled)

        self.price_model = RandomForestRegressor(n_estimators=100)
        self.price_model.fit(X_scaled, y_price_scaled)

        print("Forecasting models trained successfully")

    def _prepare_features(self, data):
        """Extract features from historical data for model training."""
        features = []
        for i, d in enumerate(data):
            hour = int(d["hour"].split("-")[0])
            # Create time-based features
            hour_sin = np.sin(2 * np.pi * hour / 24)
            hour_cos = np.cos(2 * np.pi * hour / 24)

            # Add previous values as features if available
            prev_consumption = data[i - 1]["consumption"] if i > 0 else 0
            prev_production = data[i - 1]["production"] if i > 0 else 0

            # Create feature vector
            feature = [hour_sin, hour_cos, prev_consumption, prev_production]
            features.append(feature)
        return np.array(features)

    def forecast(self, current_data, horizon=24):
        """Forecast consumption, production, and prices for the next 'horizon' hours."""
        forecasts = []

        # Start with current data
        last_data = current_data
        X = self._prepare_features([last_data])
        X_scaled = self.scaler_consumption.transform(X)

        for h in range(horizon):
            # Predict next values
            consumption_pred = self.scaler_consumption.inverse_transform(
                self.consumption_model.predict(X_scaled).reshape(-1, 1)
            ).flatten()[0]

            production_pred = self.scaler_production.inverse_transform(
                self.production_model.predict(X_scaled).reshape(-1, 1)
            ).flatten()[0]

            price_pred = self.scaler_price.inverse_transform(
                self.price_model.predict(X_scaled).reshape(-1, 1)
            ).flatten()[0]

            # Create forecast entry
            hour_parts = last_data["hour"].split("-")
            hour = int(hour_parts[0])
            next_hour = (hour + 1) % 24
            forecast_hour = f"{next_hour:02d}:00"

            forecast = {
                "hour": forecast_hour,
                "consumption": max(0, consumption_pred),  # Ensure non-negative
                "production": max(0, production_pred),  # Ensure non-negative
                "grid_price": max(0.1, price_pred),  # Ensure reasonable price
            }
            forecasts.append(forecast)

            # Update for next iteration
            last_data = forecast
            X = self._prepare_features([last_data])
            X_scaled = self.scaler_consumption.transform(X)

        return forecasts

    def optimize_storage_strategy(self, current_data, forecasts, grid_costs):
        """Determine optimal storage charging/discharging strategy based on forecasts."""
        # Extract current hour to get grid prices
        current_hour = int(current_data["hour"].split("-")[0])

        # Make sure we handle the grid_costs array safely
        grid_costs_len = len(grid_costs)
        current_hour_index = current_hour % grid_costs_len
        current_purchase_price = grid_costs[current_hour_index]["purchase"]
        current_sale_price = grid_costs[current_hour_index]["sale"]

        # Calculate current energy balance
        current_net_energy = current_data["production"] - current_data["consumption"]

        # Analyze future energy balance and prices
        future_deficit_hours = []
        future_surplus_hours = []
        future_high_price_hours = []
        future_low_price_hours = []

        # Calculate average prices safely
        avg_purchase_price = sum(gc["purchase"] for gc in grid_costs) / grid_costs_len
        avg_sale_price = sum(gc["sale"] for gc in grid_costs) / grid_costs_len

        # Analyze forecasts to identify patterns
        for i, forecast in enumerate(forecasts[: min(24, len(forecasts))]):
            forecast_hour = (current_hour + i + 1) % 24
            forecast_hour_index = forecast_hour % grid_costs_len
            forecast_net_energy = forecast["production"] - forecast["consumption"]
            forecast_purchase_price = grid_costs[forecast_hour_index]["purchase"]
            forecast_sale_price = grid_costs[forecast_hour_index]["sale"]

            if forecast_net_energy < 0:
                future_deficit_hours.append(
                    (
                        i,
                        forecast_hour,
                        abs(forecast_net_energy),
                        forecast_purchase_price,
                    )
                )
            else:
                future_surplus_hours.append(
                    (i, forecast_hour, forecast_net_energy, forecast_sale_price)
                )

            if forecast_purchase_price > avg_purchase_price * 1.1:
                future_high_price_hours.append(
                    (i, forecast_hour, forecast_purchase_price)
                )
            if forecast_sale_price > avg_sale_price * 1.1:
                future_high_price_hours.append((i, forecast_hour, forecast_sale_price))

        # Sort by price (highest first) and proximity (closest first)
        # Only sort if lists are not empty
        if future_deficit_hours:
            future_deficit_hours.sort(key=lambda x: (-x[3], x[0]))
        if future_surplus_hours:
            future_surplus_hours.sort(key=lambda x: (-x[3], x[0]))

        # Calculate total storage capacity and current level
        total_capacity = (
            sum(storage.capacity for storage in self.storages) if self.storages else 0
        )
        total_current_level = (
            sum(storage.current_level for storage in self.storages)
            if self.storages
            else 0
        )

        # Determine charging strategy
        charge_strategy = 0  # 0: normal, 1: aggressive charge, -1: aggressive discharge

        # If we have current surplus and high prices coming soon, charge aggressively
        if (
            current_net_energy > 0
            and future_deficit_hours
            and future_deficit_hours[0][3] > current_purchase_price * 1.2
        ):
            charge_strategy = 1

        # If we have current deficit but low prices now and higher prices coming, discharge minimally
        elif (
            current_net_energy < 0
            and current_purchase_price < avg_purchase_price * 0.9
            and future_high_price_hours
        ):
            charge_strategy = -1

        # If storage is nearly full and high sale prices are coming, prepare to discharge
        elif (
            total_capacity > 0
            and total_current_level > total_capacity * 0.8
            and future_high_price_hours
        ):
            charge_strategy = -1

        return {
            "charge_strategy": charge_strategy,
            "future_deficit_hours": future_deficit_hours,
            "future_surplus_hours": future_surplus_hours,
            "future_high_price_hours": future_high_price_hours,
        }

    def execute_optimal_strategy(
        self,
        step,
        hourly_data,
        grid_costs,
        p2p_base_price,
        token_mint_rate,
        token_burn_rate,
    ):
        """Execute the optimal energy management strategy for the current step."""
        current_data = hourly_data[step]

        # Add current data to historical data for future model training
        if "grid_price" not in current_data:
            current_data["grid_price"] = grid_costs[step % len(grid_costs)]["purchase"]
        self.historical_data.append(current_data)

        # Train models if we have enough historical data
        if (
            len(self.historical_data) >= 24
            and step % 24 == 0
            and self.consumption_model is None
        ):
            self.train_forecasting_models(self.historical_data)

        # Generate forecasts if models are trained
        forecasts = []
        if self.consumption_model is not None:
            forecasts = self.forecast(current_data)

        # Optimize storage strategy based on forecasts and current conditions
        strategy = {}
        if forecasts:
            strategy = self.optimize_storage_strategy(
                current_data, forecasts, grid_costs
            )

        # Dynamically adjust p2p price based on market conditions
        dynamic_p2p_price = p2p_base_price
        if strategy.get("charge_strategy") == 1:
            # Increase p2p price when we want to charge storage (incentivize selling to community)
            dynamic_p2p_price = p2p_base_price * 1.1
        elif strategy.get("charge_strategy") == -1:
            # Decrease p2p price when we want to discharge storage (incentivize buying from community)
            dynamic_p2p_price = p2p_base_price * 0.9

        # Execute the simulation step with our optimized strategy
        self.cooperative.simulate_step(
            step,
            dynamic_p2p_price,
            min_price=0.2,
            token_mint_rate=token_mint_rate,
            token_burn_rate=token_burn_rate,
            hourly_data=hourly_data,
            grid_costs=grid_costs,
        )

        return {
            "step": step,
            "strategy": strategy,
            "dynamic_p2p_price": dynamic_p2p_price,
            "token_balance": self.cooperative.community_token_balance,
        }
