# src/agents/demand_forecasting_agent.py

import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler


class DemandForecastingAgent:
    def __init__(self):
        """Initialize the Demand Forecasting Agent."""
        self.consumption_model = None
        self.production_model = None
        self.scaler_consumption = StandardScaler()
        self.scaler_production = StandardScaler()
        self.historical_data = []
        self.forecast_horizon = 24  # Hours to forecast ahead

    def add_historical_data(self, data):
        """Add data to the historical dataset."""
        self.historical_data.append(data)

    def train_models(self):
        """Train forecasting models based on historical data."""
        if len(self.historical_data) < 24:  # Need at least a day of data
            return False

        # Extract features and targets
        hours = []
        consumption_values = []
        production_values = []

        for data in self.historical_data:
            hour = int(data["hour"].split("-")[0])
            hours.append(hour)
            consumption_values.append(data["consumption"])
            production_values.append(data["production"])

        # Convert to numpy arrays and reshape for scikit-learn
        X = np.array(hours).reshape(-1, 1)  # Reshape to 2D array with 1 feature
        y_consumption = np.array(consumption_values)
        y_production = np.array(production_values)

        # Scale the data
        self.scaler_consumption = StandardScaler()
        self.scaler_production = StandardScaler()

        X_consumption_scaled = self.scaler_consumption.fit_transform(X)
        X_production_scaled = self.scaler_production.fit_transform(X)

        # Train consumption model
        self.consumption_model = RandomForestRegressor(n_estimators=10, random_state=42)
        self.consumption_model.fit(X_consumption_scaled, y_consumption)

        # Train production model
        self.production_model = RandomForestRegressor(n_estimators=10, random_state=42)
        self.production_model.fit(X_production_scaled, y_production)

        return True

    def forecast(self, current_data):
        """Forecast energy production and consumption for the next 24 hours."""
        # Extract current hour and features
        hour_str = current_data["hour"]
        hour = int(hour_str.split("-")[0])

        forecasts = []

        # Create forecasts for the next 24 hours
        for i in range(1, 25):
            next_hour = (hour + i) % 24
            next_hour_str = f"{next_hour:02d}:00"

            # Create feature vector for consumption prediction
            # The error indicates we need to reshape this correctly for the scaler
            consumption_feature = np.array([next_hour]).reshape(
                -1, 1
            )  # Reshape to 2D array with 1 feature

            # Create feature vector for production prediction
            # Similarly, reshape for the production scaler
            production_feature = np.array([next_hour]).reshape(
                -1, 1
            )  # Reshape to 2D array with 1 feature

            # Transform features if scalers are available
            if (
                hasattr(self, "scaler_consumption")
                and self.scaler_consumption is not None
            ):
                consumption_feature_scaled = self.scaler_consumption.transform(
                    consumption_feature
                )
            else:
                consumption_feature_scaled = consumption_feature

            if (
                hasattr(self, "scaler_production")
                and self.scaler_production is not None
            ):
                production_feature_scaled = self.scaler_production.transform(
                    production_feature
                )
            else:
                production_feature_scaled = production_feature

            # Make predictions
            if self.consumption_model:
                predicted_consumption = self.consumption_model.predict(
                    consumption_feature_scaled
                )[0]
            else:
                # Fallback to simple time-based pattern if no model
                predicted_consumption = self._simple_consumption_pattern(next_hour)

            if self.production_model:
                predicted_production = self.production_model.predict(
                    production_feature_scaled
                )[0]
            else:
                # Fallback to simple time-based pattern if no model
                predicted_production = self._simple_production_pattern(next_hour)

            # Add forecast
            forecasts.append(
                {
                    "hour": next_hour_str,
                    "consumption": max(0, predicted_consumption),  # Ensure non-negative
                    "production": max(0, predicted_production),  # Ensure non-negative
                }
            )

        return forecasts
