from .storage import Storage
from operatorzy.agents.smart_agent import SmartAgent

# from operatorzy.agents.profit_maximizing_agent import ProfitMaximizingAgent
# from operatorzy.agents.planner_agent import PlannerAgent
# from operatorzy.agents.active_storage_agent import ActiveStorageAgent
# from operatorzy.agents.forecasting_agent import ForecastingTraderAgent
# from operatorzy.agents.ultimate_energy_agent import UltimateEnergyAgent
from operatorzy.agents.ultimate_energy_agent_v2 import UltimateEnergyAgentV2

# from operatorzy.agents.hybrid_energy_agent import HybridEnergyAgent
import json


class Cooperative:
    def __init__(self, config, initial_token_balance):
        self.agent = None
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
        self.frontend_data = []

        self.net_energy_history = []

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
        # self.agent = SmartAgent(grid_costs)
        # self.agent = ProfitMaximizingAgent(grid_costs)
        # self.agent = PlannerAgent(grid_costs)
        # self.agent = ActiveStorageAgent(grid_costs)
        # self.agent = ForecastingTraderAgent(grid_costs)
        # self.agent = UltimateEnergyAgent(grid_costs)
        self.agent = UltimateEnergyAgentV2(grid_costs)
        # self.agent = HybridEnergyAgent(grid_costs)

        hourly_data_step = hourly_data[step]
        consumption = hourly_data_step["consumption"]
        production = hourly_data_step["production"]
        date = hourly_data_step["date"]

        grid_price = grid_costs[step % len(grid_costs)]["purchase"]
        sale_price = grid_costs[step % len(grid_costs)]["sale"]

        # Calculate net energy balance
        net_energy = production - consumption

        # self.net_energy_history.append(net_energy)

        # future_data = hourly_data[step + 1:step + 1 + self.agent.lookahead]

        # decision = self.agent.decide(
        #     step=step,
        #     net_energy=net_energy,
        #     consumption=consumption,
        #     production=production,
        #     storage_levels=[s.current_level / s.capacity for s in self.storages]  # normalize 0–1
        # )

        # decision = self.agent.decide(
        #     step=step,
        #     net_energy=net_energy,
        #     consumption=consumption,
        #     production=production,
        #     storage_levels=[s.current_level / s.capacity for s in self.storages],
        #     future_data=future_data
        # )

        # decision = self.agent.decide(
        #     step=step,
        #     net_energy=net_energy,
        #     consumption=consumption,
        #     production=production,
        #     storage_levels=[s.current_level / s.capacity for s in self.storages]
        # )

        # decision = self.agent.decide(
        #     step=step,
        #     net_energy=net_energy,
        #     consumption=consumption,
        #     production=production,
        #     storage_levels=[s.current_level / s.capacity for s in self.storages],
        #     net_energy_history=self.net_energy_history
        # )

        self.net_energy_history.append(net_energy)

        decision = self.agent.decide(
            step=step,
            net_energy=net_energy,
            consumption=consumption,
            production=production,
            storage_levels=[s.current_level / s.capacity for s in self.storages],
            net_energy_history=self.net_energy_history,
        )

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

        # # Update storage level
        # if net_energy > 0:
        #     if consumption > 0:
        #         # Mint tokens for renewable use
        #         minted_tokens = consumption * token_mint_rate
        #         self.community_token_balance += minted_tokens
        #
        #     if decision['store_energy']:
        #         for storage in self.storages:
        #             charged_energy = storage.charge(net_energy)
        #             net_energy -= charged_energy
        #             if charged_energy > 0:
        #                 tokens_used_for_storage += charged_energy * p2p_base_price
        #                 self.community_token_balance += charged_energy * p2p_base_price
        #                 energy_added_to_storage += charged_energy
        #             if net_energy <= 0:
        #                 break
        #
        #     if net_energy > 0:
        #         energy_sold_to_grid = net_energy
        #         tokens_gained_from_grid = energy_sold_to_grid * sale_price
        #         self.community_token_balance += tokens_gained_from_grid
        #
        # elif net_energy < 0:
        #     if consumption > 0:
        #         minted_tokens = (consumption - production) * token_mint_rate
        #         self.community_token_balance += minted_tokens
        #
        #     if decision['discharge']:
        #         for storage in self.storages:
        #             discharged_energy = storage.discharge(-net_energy)
        #             net_energy += discharged_energy
        #             if discharged_energy > 0:
        #                 self.community_token_balance -= discharged_energy * p2p_base_price
        #                 energy_bought_from_storages += discharged_energy
        #                 cost_from_storages += discharged_energy * p2p_base_price
        #             if net_energy >= 0:
        #                 break
        #
        #     if net_energy < 0:
        #         energy_deficit = -net_energy
        #         required_tokens = energy_deficit * grid_price
        #         if self.community_token_balance >= required_tokens:
        #             self.community_token_balance -= required_tokens
        #             burned_tokens = energy_deficit * token_burn_rate
        #             self.community_token_balance -= burned_tokens
        #             energy_bought_from_grid = energy_deficit
        #             cost_from_grid = energy_deficit * grid_price
        #         else:
        #             affordable_energy = self.community_token_balance / grid_price
        #             energy_deficit -= affordable_energy
        #             self.community_token_balance = 0
        #             burned_tokens = affordable_energy * token_burn_rate
        #             energy_bought_from_grid = affordable_energy
        #             cost_from_grid = affordable_energy * grid_price
        if net_energy > 0:
            if consumption > 0:
                minted_tokens = consumption * token_mint_rate
                self.community_token_balance += minted_tokens

            if decision["store_energy"]:
                for storage in self.storages:
                    charged_energy = storage.charge(net_energy)
                    net_energy -= charged_energy
                    if charged_energy > 0:
                        tokens_used_for_storage += charged_energy * p2p_base_price
                        self.community_token_balance += charged_energy * p2p_base_price
                        energy_added_to_storage += charged_energy
                    if net_energy <= 0:
                        break

            if decision["sell_energy"] and net_energy > 0:
                energy_sold_to_grid = net_energy
                tokens_gained_from_grid = energy_sold_to_grid * sale_price
                self.community_token_balance += tokens_gained_from_grid

        elif net_energy < 0:
            if consumption > 0:
                minted_tokens = (consumption - production) * token_mint_rate
                self.community_token_balance += minted_tokens

            if decision["discharge"]:
                for storage in self.storages:
                    discharged_energy = storage.discharge(-net_energy)
                    net_energy += discharged_energy
                    if discharged_energy > 0:
                        self.community_token_balance -= (
                            discharged_energy * p2p_base_price
                        )
                        energy_bought_from_storages += discharged_energy
                        cost_from_storages += discharged_energy * p2p_base_price
                    if net_energy >= 0:
                        break

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
                    affordable_energy = self.community_token_balance / grid_price
                    energy_deficit -= affordable_energy
                    self.community_token_balance = 0
                    burned_tokens = affordable_energy * token_burn_rate
                    energy_bought_from_grid = affordable_energy
                    cost_from_grid = affordable_energy * grid_price

        # SAVE DATA IN JSON TO HAVE IT ON THE FRONTEND
        self.frontend_data.append(
            {
                "step": hourly_data[step][
                    "date"
                ],  # assuming timestamp is a string like "2023-06-01 02:00"
                "total_consumption": round(consumption, 2),
                "total_production": round(production, 2),
                "energy_bought_from_grid": round(energy_bought_from_grid, 2),
                "cost_from_grid": round(cost_from_grid, 2),
                "energy_sold_to_grid": round(energy_sold_to_grid, 2),
                "tokens_gained_from_grid": round(tokens_gained_from_grid, 2),
                "tokens_burned_due_to_grid": round(burned_tokens, 2),
                "storage_S1_level": round(self.storages[0].current_level, 2),
                "storage_S2_level": round(self.storages[1].current_level, 2)
                if len(self.storages) > 1
                else 0.0,
                "token_balance": round(self.community_token_balance, 2),
                "ai_decision": {
                    "action": self._get_ai_action_label(decision, net_energy),
                    "amount": round(abs(net_energy), 2),
                },
            }
        )

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
        with open("frontend_output.json", "w") as f:
            json.dump({"data": self.frontend_data}, f, indent=2)

    def save_logs(self, filename):
        with open(filename, "w") as f:
            for log in self.logs:
                f.write(log + "\n")

    @staticmethod
    def _get_ai_action_label(decision, net_energy):
        if decision.get("sell_energy"):
            return "SELL"
        elif decision.get("discharge"):
            return "DISCHARGE"
        elif decision.get("store_energy"):
            return "STORE"
        elif net_energy < 0:
            return "BUY"
        elif net_energy > 0:
            return "HOLD"
        return "IDLE"
