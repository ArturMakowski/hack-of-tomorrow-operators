# operatorzy/simulation/ai_energy_community_simulation.py

import sys
import csv
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from operatorzy.models.cooperative import Cooperative
from operatorzy.models.storage import Storage
from operatorzy.utils.helper_functions import (
    plot_results,
    save_results_to_csv,
    load_profiles,
    load_storages,
)
from operatorzy.agents.energy_optimization_agent import EnergyOptimizationAgent
from operatorzy.agents.storage_management_agent import StorageManagementAgent
from operatorzy.agents.energy_trading_agent import EnergyTradingAgent
from operatorzy.agents.demand_forecasting_agent import DemandForecastingAgent
from operatorzy.models.ai_cooperative import AICooperative
from operatorzy.utils.json_output import generate_dashboard_json


def load_grid_costs(filepath):
    """Load grid costs from CSV file."""
    grid_costs = []
    with open(filepath, "r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            grid_costs.append(
                {
                    "hour": row["Hour"],
                    "purchase": float(row["Purchase"].replace(",", ".")),
                    "sale": float(row["Sale"].replace(",", ".")),
                }
            )
    return grid_costs


def main():
    """Main function to run the AI-powered energy community simulation."""
    if len(sys.argv) < 5:
        print(
            "Usage: python ai_energy_community_simulation.py <storage_file> <profiles_dir> <logs_dir> <grid_costs_file>"
        )
        sys.exit(1)

    storage_file = sys.argv[1]
    profiles_dir = sys.argv[2]
    logs_dir = sys.argv[3]
    grid_costs_file = sys.argv[4]

    # Load storage configurations
    storages = load_storages(storage_file)
    config = {"storages": storages}

    # Load energy profiles
    profiles = load_profiles(profiles_dir)

    # Load grid costs
    grid_costs = load_grid_costs(grid_costs_file)

    # Initialize our AI agents
    optimization_agent = EnergyOptimizationAgent(config, initial_token_balance=100)
    storage_agent = StorageManagementAgent(optimization_agent.cooperative.storages)
    trading_agent = EnergyTradingAgent()
    forecasting_agent = DemandForecastingAgent()

    # Create an AI-enhanced cooperative
    ai_cooperative = AICooperative(config, initial_token_balance=100)

    # Determine the number of steps based on the number of hours in the profiles
    steps = len(next(iter(profiles.values())))

    # Prepare hourly data based on the loaded profiles
    hourly_data = []
    time_labels = []
    for hour in range(steps):
        total_consumption = 0
        total_production = 0
        for ppe, profile in profiles.items():
            total_consumption += profile.iloc[hour]["consumption"]
            total_production += profile.iloc[hour]["production"]
        date = profile.iloc[hour][
            "hour"
        ]  # Assuming 'hour' column contains date information
        time_labels.append(date)
        hourly_data.append(
            {
                "hour": date,
                "consumption": total_consumption,
                "production": total_production,
                "date": date,
            }
        )

    # Initialize simulation parameters
    token_mint_rate = 0.1  # Tokens minted per kWh of renewable energy consumed
    token_burn_rate = 0.1  # Tokens burned per kWh of grid energy consumed

    # Create logs directory if it doesn't exist
    log_dir = Path(logs_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create results directory
    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Timestamp for file naming
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Open log file
    log_file = open(log_dir / f"ai_simulation_{formatted_date}.log", "w")

    # Run the simulation
    print("Starting AI-powered energy community simulation...")
    log_file.write("=== AI-POWERED ENERGY COMMUNITY SIMULATION ===\n\n")

    # Track performance metrics
    total_tokens_minted = 0
    total_tokens_burned = 0
    total_energy_from_grid = 0
    total_energy_to_grid = 0
    total_energy_stored = 0
    total_energy_from_storage = 0

    for step in range(steps):
        current_data = hourly_data[step]
        hour = step % 24

        # Add current data to forecasting agent
        forecasting_agent.add_historical_data(current_data)

        # Train forecasting models every 24 hours or when we have enough data
        if step % 24 == 0 and step >= 24:
            forecasting_agent.train_models()

        # Generate forecasts if models are trained
        forecasts = []
        if forecasting_agent.consumption_model is not None:
            forecasts = forecasting_agent.forecast(current_data)

        # Calculate total storage capacity and current level
        total_capacity = sum(
            storage.capacity for storage in optimization_agent.storages
        )
        total_current_level = sum(
            storage.current_level for storage in optimization_agent.storages
        )
        storage_level_percentage = (
            total_current_level / total_capacity if total_capacity > 0 else 0
        )

        # Update storage thresholds based on grid costs and forecasts
        storage_agent.update_thresholds(grid_costs, forecasts)

        # Calculate optimal P2P price
        net_energy = current_data["production"] - current_data["consumption"]
        p2p_price = trading_agent.calculate_optimal_p2p_price(
            grid_costs,
            hour,
            optimization_agent.cooperative.community_token_balance,
            net_energy,
            storage_level_percentage,
        )

        # Decide on energy allocation strategy
        energy_allocation = trading_agent.decide_energy_allocation(
            net_energy,
            total_capacity - total_current_level,  # Available storage capacity
            grid_costs,
            hour,
            forecasts,
        )

        # Optimize storage allocation if we're charging or discharging
        storage_allocation = {}
        if energy_allocation["to_storage"] > 0 or energy_allocation["from_storage"] > 0:
            storage_allocation, remaining_energy = (
                storage_agent.optimize_storage_allocation(
                    energy_allocation["to_storage"] - energy_allocation["from_storage"],
                    grid_costs,
                    hour,
                )
            )

        # Get storage strategy from optimization agent
        storage_strategy = {}
        if forecasts:
            storage_strategy = optimization_agent.optimize_storage_strategy(
                current_data, forecasts, grid_costs
            )

        # Execute the simulation step with our optimized strategy using AI cooperative
        ai_cooperative.simulate_step_with_ai(
            step,
            p2p_price,  # Our dynamically calculated P2P price
            min_price=0.2,
            token_mint_rate=token_mint_rate,
            token_burn_rate=token_burn_rate,
            hourly_data=hourly_data,
            grid_costs=grid_costs,
            forecasts=forecasts,
            storage_strategy=storage_strategy,
        )

        # Log the step results
        log_entry = f"=== Step {step} (Hour: {current_data['date']}) ===\n"
        log_entry += f"Consumption: {current_data['consumption']:.2f} kWh, Production: {current_data['production']:.2f} kWh\n"
        log_entry += f"Net energy: {net_energy:.2f} kWh\n"
        log_entry += f"Optimal P2P price: {p2p_price:.4f} CT/kWh\n"
        log_entry += f"Grid purchase price: {grid_costs[hour]['purchase']:.4f} CT/kWh, Sale price: {grid_costs[hour]['sale']:.4f} CT/kWh\n"
        log_entry += f"Storage level: {total_current_level:.2f}/{total_capacity:.2f} kWh ({storage_level_percentage * 100:.1f}%)\n"

        if forecasts:
            log_entry += f"Forecast for next hour: Consumption {forecasts[0]['consumption']:.2f} kWh, Production {forecasts[0]['production']:.2f} kWh\n"

        log_entry += f"Energy allocation: {energy_allocation}\n"
        log_entry += f"Storage allocation: {storage_allocation}\n"
        log_entry += f"Community token balance: {ai_cooperative.community_token_balance:.2f} CT\n\n"

        log_file.write(log_entry)

        # Update performance metrics
        total_energy_from_grid += energy_allocation.get("from_grid", 0)
        total_energy_to_grid += energy_allocation.get("to_grid", 0)
        total_energy_stored += energy_allocation.get("to_storage", 0)
        total_energy_from_storage += energy_allocation.get("from_storage", 0)

        # Print progress
        if step % 10 == 0:
            print(
                f"Completed step {step}/{steps} - Token balance: {ai_cooperative.community_token_balance:.2f} CT"
            )

    # Write summary statistics
    log_file.write("=== SIMULATION SUMMARY ===\n")
    log_file.write(f"Total steps: {steps}\n")
    log_file.write(
        f"Final community token balance: {ai_cooperative.community_token_balance:.2f} CT\n"
    )
    log_file.write(
        f"Total energy consumed: {sum(ai_cooperative.history_consumption):.2f} kWh\n"
    )
    log_file.write(
        f"Total energy produced: {sum(ai_cooperative.history_production):.2f} kWh\n"
    )
    log_file.write(f"Total energy from grid: {total_energy_from_grid:.2f} kWh\n")
    log_file.write(f"Total energy sold to grid: {total_energy_to_grid:.2f} kWh\n")
    log_file.write(f"Total energy stored: {total_energy_stored:.2f} kWh\n")
    log_file.write(f"Total energy from storage: {total_energy_from_storage:.2f} kWh\n")

    # Close log file
    log_file.close()

    # Save results to CSV
    save_results_to_csv(ai_cooperative, time_labels, results_dir, formatted_date)

    # Plot results
    ai_cooperative.plot_results = plot_results.__get__(ai_cooperative)
    ai_cooperative.plot_results(steps, time_labels, results_dir, formatted_date)

    print(
        f"Simulation completed. Final community token balance: {ai_cooperative.community_token_balance:.2f} CT"
    )
    print(f"Results saved to {results_dir}")
    print(f"Logs saved to {log_dir}")

    # Add this code at the end of the main function, before the final print statements
    # Generate JSON for dashboard
    dashboard_data = generate_dashboard_json(
        ai_cooperative, hourly_data, time_labels, results_dir, formatted_date
    )
    print(
        f"Dashboard JSON data saved to {results_dir / f'dashboard_data_{formatted_date}.json'}"
    )


if __name__ == "__main__":
    main()
