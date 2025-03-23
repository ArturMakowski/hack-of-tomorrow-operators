# src/agents/energy_trading_agent.py


class EnergyTradingAgent:
    def __init__(self):
        """Initialize the Energy Trading Agent."""
        self.trade_history = []
        self.price_history = []
        self.min_price = 0.2
        self.max_price = 0.8

    def calculate_optimal_p2p_price(
        self, grid_costs, hour, community_balance, net_energy, storage_level_percentage
    ):
        """Calculate the optimal P2P energy trading price based on market conditions."""
        # Get current grid prices
        current_purchase = grid_costs[hour % len(grid_costs)]["purchase"]
        current_sale = grid_costs[hour % len(grid_costs)]["sale"]

        # Base P2P price is between grid purchase and sale price
        base_price = (current_purchase + current_sale) / 2

        # Adjust based on community token balance
        # If community has high balance, we can afford to be more generous
        balance_factor = 1.0
        if community_balance > 500:
            balance_factor = 0.9  # Lower prices when community is rich
        elif community_balance < 100:
            balance_factor = 1.1  # Higher prices when community needs tokens

        # Adjust based on net energy
        energy_factor = 1.0
        if net_energy > 0:  # Surplus
            energy_factor = 0.85  # Lower prices to encourage consumption
        elif net_energy < 0:  # Deficit
            energy_factor = 1.25  # Higher prices to encourage production

        # Adjust based on storage levels
        storage_factor = 1.0
        if storage_level_percentage > 0.8:  # Storage nearly full
            storage_factor = 0.9  # Lower prices to encourage consumption
        elif storage_level_percentage < 0.2:  # Storage nearly empty
            storage_factor = 1.1  # Higher prices to encourage production

        # Calculate final price
        p2p_price = base_price * balance_factor * energy_factor * storage_factor

        # Ensure price is within bounds
        p2p_price = max(self.min_price, min(self.max_price, p2p_price))

        # Record price for history
        self.price_history.append(
            {
                "hour": hour,
                "p2p_price": p2p_price,
                "grid_purchase": current_purchase,
                "grid_sale": current_sale,
            }
        )

        return p2p_price

    def decide_energy_allocation(
        self, net_energy, storage_capacity, grid_costs, hour, forecasts=None
    ):
        """Decide how to allocate energy between storage, grid, and community."""
        # Get current grid prices
        current_purchase = grid_costs[hour % len(grid_costs)]["purchase"]
        current_sale = grid_costs[hour % len(grid_costs)]["sale"]

        # Initialize allocation
        allocation = {
            "to_storage": 0,
            "from_storage": 0,
            "to_grid": 0,
            "from_grid": 0,
            "p2p_trade": 0,
        }

        # If we have forecasts, use them to make more informed decisions
        future_prices = []
        future_energy_balance = 0

        if forecasts:
            # Look at next 24 hours
            for i in range(min(24, len(forecasts))):
                forecast_hour = (hour + i + 1) % 24
                forecast_purchase = grid_costs[forecast_hour]["purchase"]
                forecast_sale = grid_costs[forecast_hour]["sale"]
                future_prices.append((forecast_purchase, forecast_sale))

                # Calculate forecasted energy balance
                if i < len(forecasts):
                    forecast_net = (
                        forecasts[i]["production"] - forecasts[i]["consumption"]
                    )
                    future_energy_balance += forecast_net

        # Handle surplus energy
        if net_energy > 0:
            # If storage is a better option than selling to grid
            # FIX: Check if future_prices is not empty before using max()
            if (
                future_prices
                and current_sale < max(future_prices, key=lambda x: x[0])[0] * 0.9
                and storage_capacity > 0
            ):
                # Store as much as possible
                allocation["to_storage"] = min(net_energy, storage_capacity)
                remaining = net_energy - allocation["to_storage"]

                # Sell remaining to grid
                if remaining > 0:
                    allocation["to_grid"] = remaining
            else:
                # Sell directly to grid if price is good
                allocation["to_grid"] = net_energy

        # Handle energy deficit
        elif net_energy < 0:
            deficit = -net_energy

            # If future prices will be higher, use storage now
            avg_future_purchase = (
                sum(p[0] for p in future_prices) / len(future_prices)
                if future_prices
                else current_purchase
            )
            if current_purchase > avg_future_purchase * 1.1:
                # Use storage first
                from_storage = min(deficit, storage_capacity)
                allocation["from_storage"] = from_storage
                remaining_deficit = deficit - from_storage

                # Buy remaining from grid
                if remaining_deficit > 0:
                    allocation["from_grid"] = remaining_deficit
            else:
                # Buy directly from grid if price is good
                allocation["from_grid"] = deficit

        # Record the trade
        self.trade_history.append(
            {
                "hour": hour,
                "net_energy": net_energy,
                "allocation": allocation,
                "grid_purchase": current_purchase,
                "grid_sale": current_sale,
            }
        )

        return allocation
