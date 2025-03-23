# src/models/ai_cooperative.py

from operatorzy.models.cooperative import Cooperative
from operatorzy.utils.helper_functions import load_profiles


class AICooperative(Cooperative):
    def __init__(self, config, initial_token_balance):
        """Initialize the AI-enhanced Cooperative."""
        super().__init__(config, initial_token_balance)
        self.prediction_accuracy = []
        self.optimization_gains = []
        self.p2p_trades = []
        self.grid_trades = []
        self.storage_efficiency = []
        self.energy_bought_from_grid = []
        self.cost_from_grid = []
        self.tokens_burned_due_to_grid = []

    def simulate_step_with_ai(
        self,
        step,
        p2p_price,
        min_price,
        token_mint_rate,
        token_burn_rate,
        hourly_data,
        grid_costs,
        forecasts=None,
        storage_strategy=None,
        community_members=None,
    ):
        """Simulate a step with AI-enhanced decision making."""
        # Get current data
        hourly_data_step = hourly_data[step]
        consumption = hourly_data_step["consumption"]
        production = hourly_data_step["production"]
        date = hourly_data_step["date"]

        # Get grid prices
        hour = step % 24
        grid_price = grid_costs[hour]["purchase"]
        sale_price = grid_costs[hour]["sale"]

        # Calculate net energy balance
        net_energy = production - consumption

        # Initialize variables
        energy_surplus = 0
        minted_tokens = 0
        energy_deficit = 0
        burned_tokens = 0
        energy_bought_from_storages = 0
        energy_bought_from_grid = 0
        cost_from_storages = 0
        cost_from_grid = 0
        energy_sold_to_grid = 0
        tokens_gained_from_grid = 0
        energy_added_to_storage = 0
        tokens_used_for_storage = 0
        p2p_energy_traded = 0
        p2p_tokens_exchanged = 0

        # Track P2P trading
        self.p2p_trades = getattr(self, "p2p_trades", [])

        # Determine optimal energy allocation
        if community_members:
            # If we have community members, prioritize P2P trading
            allocation = self.trading_agent.decide_energy_allocation(
                net_energy,
                sum(s.capacity - s.current_level for s in self.storages),
                grid_costs,
                hour,
                forecasts,
                community_members,
            )

            # Process P2P trading first
            if allocation.get("p2p_trade", 0) > 0:
                # We're selling energy to other community members
                p2p_energy_traded = allocation["p2p_trade"]
                p2p_tokens_exchanged = p2p_energy_traded * p2p_price
                self.community_token_balance += p2p_tokens_exchanged
                net_energy -= p2p_energy_traded

                # Record P2P trade
                self.p2p_trades.append(
                    {
                        "step": step,
                        "date": date,
                        "type": "sell",
                        "amount": p2p_energy_traded,
                        "price": p2p_price,
                        "tokens": p2p_tokens_exchanged,
                    }
                )

            elif allocation.get("p2p_trade", 0) < 0:
                # We're buying energy from other community members
                p2p_energy_traded = -allocation["p2p_trade"]
                p2p_tokens_exchanged = p2p_energy_traded * p2p_price
                self.community_token_balance -= p2p_tokens_exchanged
                net_energy += p2p_energy_traded

                # Record P2P trade
                self.p2p_trades.append(
                    {
                        "step": step,
                        "date": date,
                        "type": "buy",
                        "amount": p2p_energy_traded,
                        "price": p2p_price,
                        "tokens": p2p_tokens_exchanged,
                    }
                )

        # Apply AI-enhanced storage strategy if provided
        if storage_strategy and net_energy > 0:
            # If we have surplus and strategy recommends storing
            if storage_strategy.get("charge_strategy", 0) > 0:
                # Prioritize storage over selling to grid
                for storage in self.storages:
                    charged_energy = storage.charge(net_energy)
                    net_energy -= charged_energy
                    if charged_energy > 0:
                        tokens_used_for_storage += charged_energy * p2p_price
                        self.community_token_balance += charged_energy * p2p_price
                        energy_added_to_storage += charged_energy
                    if net_energy <= 0:
                        break

                # If there's still surplus, sell to grid as last resort
                if net_energy > 0:
                    energy_surplus = net_energy
                    energy_sold_to_grid = energy_surplus
                    tokens_gained_from_grid = energy_sold_to_grid * sale_price
                    self.community_token_balance += tokens_gained_from_grid

            # If strategy recommends selling to grid
            else:
                # Sell directly to grid if price is good
                energy_surplus = net_energy
                energy_sold_to_grid = energy_surplus
                tokens_gained_from_grid = energy_sold_to_grid * sale_price
                self.community_token_balance += tokens_gained_from_grid

        elif storage_strategy and net_energy < 0:
            # If we have deficit and strategy recommends discharging
            if storage_strategy.get("charge_strategy", 0) < 0:
                # Prioritize storage over buying from grid
                for storage in self.storages:
                    discharged_energy = storage.discharge(-net_energy)
                    net_energy += discharged_energy
                    if discharged_energy > 0:
                        self.community_token_balance -= discharged_energy * p2p_price
                        energy_bought_from_storages += discharged_energy
                        cost_from_storages += discharged_energy * p2p_price
                    if net_energy >= 0:
                        break

                # If there's still deficit, buy from grid as last resort
                if net_energy < 0:
                    energy_deficit = -net_energy
                    required_tokens = energy_deficit * grid_price
                    if self.community_token_balance >= required_tokens:
                        self.community_token_balance -= required_tokens
                        burned_tokens = energy_deficit * token_burn_rate
                        self.community_token_balance -= burned_tokens
                        energy_bought_from_grid = energy_deficit
                        cost_from_grid = energy_deficit * grid_price
                    else:
                        # If not enough tokens, buy as much as possible
                        affordable_energy = self.community_token_balance / grid_price
                        energy_deficit -= affordable_energy
                        self.community_token_balance = 0
                        burned_tokens = affordable_energy * token_burn_rate
                        energy_bought_from_grid = affordable_energy
                        cost_from_grid = affordable_energy * grid_price

            # If strategy recommends buying from grid
            else:
                energy_deficit = -net_energy
                required_tokens = energy_deficit * grid_price
                if self.community_token_balance >= required_tokens:
                    self.community_token_balance -= required_tokens
                    burned_tokens = energy_deficit * token_burn_rate
                    self.community_token_balance -= burned_tokens
                    energy_bought_from_grid = energy_deficit
                    cost_from_grid = energy_deficit * grid_price
                else:
                    # If not enough tokens, buy as much as possible
                    affordable_energy = self.community_token_balance / grid_price
                    energy_deficit -= affordable_energy
                    self.community_token_balance = 0
                    burned_tokens = affordable_energy * token_burn_rate
                    energy_bought_from_grid = affordable_energy
                    cost_from_grid = affordable_energy * grid_price

        else:
            # Fall back to default behavior if no AI strategy is provided
            super().simulate_step(
                step,
                p2p_price,
                min_price,
                token_mint_rate,
                token_burn_rate,
                hourly_data,
                grid_costs,
            )
            return

        # Calculate tokens minted from renewable energy consumption
        if consumption > 0:
            renewable_consumed = min(consumption, production)
            minted_tokens = renewable_consumed * token_mint_rate
            self.community_token_balance += minted_tokens

        # Log the negotiation details
        log_entry = f"=== Current step: {date} ===\n"
        log_entry += f"Total consumption: {consumption:.2f} kWh\n"
        log_entry += f"Total production: {production:.2f} kWh\n"
        log_entry += f"Energy surplus: {max(0, production - consumption):.2f} kWh\n"
        log_entry += f"Tokens minted in this step: {minted_tokens:.2f}\n"
        log_entry += f"P2P energy traded: {p2p_energy_traded:.2f} kWh, tokens exchanged: {p2p_tokens_exchanged:.2f}\n"
        log_entry += f"Energy added to storage: {energy_added_to_storage:.2f} kWh, tokens used: {tokens_used_for_storage:.2f}\n"
        log_entry += f"Energy got from storages: {energy_bought_from_storages:.2f} kWh, cost: {cost_from_storages:.2f} CT\n"
        log_entry += f"Energy bought from grid: {energy_bought_from_grid:.2f} kWh, cost: {cost_from_grid:.2f} CT\n"
        log_entry += f"Energy sold to grid: {energy_sold_to_grid:.2f} kWh, price: {sale_price:.2f} CT/kWh, tokens gained: {tokens_gained_from_grid:.2f}\n"
        log_entry += f"Tokens burned due to grid: {burned_tokens:.2f}\n"
        log_entry += f"Purchase grid price for this step: {grid_price:.2f} CT/kWh\n"
        log_entry += f"Sale grid price for this step: {sale_price:.2f} CT/kWh\n"
        log_entry += f"P2P price for this step: {p2p_price:.2f} CT/kWh\n"
        for storage in self.storages:
            log_entry += f"Storage {storage.name} level after intervention: {storage.current_level:.2f} kWh\n"
        log_entry += f"Token balance: {self.community_token_balance:.2f} CT\n"
        self.logs.append(log_entry)

        # Update history
        self.history_consumption.append(consumption)
        self.history_production.append(production)
        self.history_token_balance.append(self.community_token_balance)
        self.history_p2p_price.append(p2p_price)
        self.history_grid_price.append(sale_price)
        self.history_purchase_price.append(grid_price)
        self.history_p2p_energy = getattr(self, "history_p2p_energy", [])
        self.history_p2p_energy.append(p2p_energy_traded)
        for storage in self.storages:
            self.history_storage[storage.name].append(storage.current_level)
        self.history_energy_deficit.append(energy_deficit)
        self.history_energy_surplus.append(energy_surplus)
        self.history_energy_sold_to_grid.append(energy_sold_to_grid)
        self.history_tokens_gained_from_grid.append(tokens_gained_from_grid)
