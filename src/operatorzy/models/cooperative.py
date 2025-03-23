from .storage import Storage


class Cooperative:
    def __init__(self, config, initial_token_balance):
        self.storages = [
            Storage(**storage_config) for storage_config in config.get("storages", [])
        ]
        self.token_balances = {"community": initial_token_balance}
        for storage in self.storages:
            self.token_balances[storage.name] = initial_token_balance
        self.community_token_balance = initial_token_balance
        self.history_consumption = []
        self.history_production = []
        self.history_token_balance = []
        self.history_p2p_price = []
        self.history_grid_price = []
        self.history_storage = {storage.name: [] for storage in self.storages}
        self.history_energy_deficit = []
        self.history_energy_surplus = []
        self.history_energy_sold_to_grid = []
        self.history_tokens_gained_from_grid = []
        self.history_purchase_price = []
        self.logs = []

    def simulate_step(
        self,
        step,
        p2p_base_price,
        min_price,
        token_mint_rate,
        token_burn_rate,
        hourly_data,
        grid_costs,
    ):
        hourly_data_step = hourly_data[step]
        consumption = hourly_data_step["consumption"]
        production = hourly_data_step["production"]
        date = hourly_data_step["date"]

        grid_price = grid_costs[step % len(grid_costs)]["purchase"]
        sale_price = grid_costs[step % len(grid_costs)]["sale"]

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

        # Update storage level
        if net_energy > 0:
            for storage in self.storages:
                charged_energy = storage.charge(net_energy)
                net_energy -= charged_energy
                if charged_energy > 0:
                    tokens_used_for_storage += charged_energy * p2p_base_price
                    self.community_token_balance += charged_energy * p2p_base_price
                    energy_added_to_storage += charged_energy
                if net_energy <= 0:
                    break
            if net_energy > 0:
                energy_surplus = net_energy
                for storage in self.storages:
                    if storage.current_level >= net_energy:
                        storage.discharge(net_energy)
                        minted_tokens = net_energy * token_mint_rate
                        self.community_token_balance += minted_tokens
                        break
                # Sell surplus energy to the grid
                energy_sold_to_grid = energy_surplus
                tokens_gained_from_grid = energy_sold_to_grid * sale_price
                self.community_token_balance += tokens_gained_from_grid

        elif net_energy < 0:
            for storage in self.storages:
                discharged_energy = storage.discharge(-net_energy)
                net_energy += discharged_energy
                if discharged_energy > 0:
                    self.community_token_balance -= discharged_energy * p2p_base_price
                    energy_bought_from_storages += discharged_energy
                    cost_from_storages += discharged_energy * p2p_base_price
                if net_energy >= 0:
                    break

            # If there is still a deficit, buy from the grid
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

        # Log the negotiation details
        log_entry = f"=== Current step: {date} ===\n"
        log_entry += f"Total consumption: {consumption:.2f} kWh\n"
        log_entry += f"Total production: {production:.2f} kWh\n"
        log_entry += f"Energy surplus: {max(0, production - consumption):.2f} kWh\n"
        log_entry += f"Tokens minted in this step: {minted_tokens:.2f}\n"
        log_entry += f"Energy added to storage: {energy_added_to_storage:.2f} kWh, tokens used: {tokens_used_for_storage:.2f}\n"
        log_entry += f"Energy got from storages: {energy_bought_from_storages:.2f} kWh, cost: {cost_from_storages:.2f} CT\n"
        log_entry += f"Energy bought from grid: {energy_bought_from_grid:.2f} kWh, cost: {cost_from_grid:.2f} CT\n"
        log_entry += f"Energy sold to grid: {energy_sold_to_grid:.2f} kWh, price: {sale_price:.2f} CT/kWh, tokens gained: {tokens_gained_from_grid:.2f}\n"
        log_entry += f"Tokens burned due to grid: {burned_tokens:.2f}\n"
        log_entry += f"Purchase grid price for this step: {grid_price:.2f} CT/kWh\n"
        log_entry += f"Sale grid price for this step: {sale_price:.2f} CT/kWh\n"
        for storage in self.storages:
            log_entry += f"Storage {storage.name} level after intervention: {storage.current_level:.2f} kWh\n"
        log_entry += f"Token balance: {self.community_token_balance:.2f} CT\n"
        self.logs.append(log_entry)

        # Update history
        self.history_consumption.append(consumption)
        self.history_production.append(production)
        self.history_token_balance.append(self.community_token_balance)
        self.history_p2p_price.append(p2p_base_price)
        self.history_grid_price.append(sale_price)
        self.history_purchase_price.append(grid_price)
        for storage in self.storages:
            self.history_storage[storage.name].append(storage.current_level)
        self.history_energy_deficit.append(energy_deficit)
        self.history_energy_surplus.append(energy_surplus)
        self.history_energy_sold_to_grid.append(energy_sold_to_grid)
        self.history_tokens_gained_from_grid.append(tokens_gained_from_grid)

    def simulate(
        self,
        steps,
        p2p_base_price,
        grid_price,
        min_price,
        token_mint_rate,
        token_burn_rate,
        hourly_data,
    ):
        for step in range(steps):
            self.simulate_step(
                step,
                p2p_base_price,
                grid_price,
                min_price,
                token_mint_rate,
                token_burn_rate,
                hourly_data,
            )

    def save_logs(self, filename):
        with open(filename, "w") as f:
            for log in self.logs:
                f.write(log + "\n")
