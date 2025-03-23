# src/simulation/run_ai_energy_community.py

import sys
import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
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
from operatorzy.agents.fetchai_integration import FetchAIIntegration


def load_grid_costs(filepath):
    """Load grid costs from CSV file."""
    grid_costs = []
    with open(filepath, "r") as file:
        reader = pd.read_csv(file)
        for i, row in reader.iterrows():
            grid_costs.append(
                {
                    "hour": row["Hour"],
                    "purchase": float(str(row["Purchase"]).replace(",", ".")),
                    "sale": float(str(row["Sale"]).replace(",", ".")),
                }
            )
    return grid_costs


def main():
    """Main function to run the AI-powered energy community."""
    if len(sys.argv) < 5:
        print(
            "Usage: python run_ai_energy_community.py <storage_file> <profiles_dir> <logs_dir> <grid_costs_file>"
        )
        sys.exit(1)

    storage_file = sys.argv[1]
    profiles_dir = sys.argv[2]
    logs_dir = sys.argv[3]
    grid_costs_file = sys.argv[4]

    print("Initializing AI-powered energy community...")

    # Load configurations
    storages = load_storages(storage_file)
    config = {"storages": storages}

    # Load profiles
    profiles = load_profiles(profiles_dir)

    # Load grid costs
    grid_costs = load_grid_costs(grid_costs_file)

    # Initialize Fetch.ai integration
    fetch_integration = FetchAIIntegration(num_agents=3)

    # Initialize AI agents
    optimization_agent = EnergyOptimizationAgent(config, initial_token_balance=100)
    storage_agent = StorageManagementAgent(optimization_agent.cooperative.storages)
    trading_agent = EnergyTradingAgent()
    forecasting_agent = DemandForecastingAgent()

    # Determine simulation steps
    steps = len(next(iter(profiles.values())))

    # Prepare hourly data
    hourly_data = []
    time_labels = []
    for hour in range(steps):
        total_consumption = 0
        total_production = 0
        for ppe, profile in profiles.items():
            total_consumption += profile.iloc[hour]["consumption"]
            total_production += profile.iloc[hour]["production"]
        date = profile.iloc[hour]["hour"]
        time_labels.append(date)
        hourly_data.append(
            {
                "hour": hour,
                "consumption": total_consumption,
                "production": total_production,
                "date": date,
            }
        )

    # Set simulation parameters
    token_mint_rate = 0.1
    token_burn_rate = 0.1

    # Create directories
    log_dir = Path(logs_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Timestamp for file naming
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d_%H-%M-%S")

    # Open log file
    log_file = open(log_dir / f"ai_community_{formatted_date}.log", "w")
    log_file.write("=== AI-POWERED ENERGY COMMUNITY SIMULATION ===\n\n")

    print("Running simulation...")

    # Run simulation
    for step in range(steps):
        current_data = hourly_data[step]
        hour = step % 24

        # Add data to forecasting agent
        forecasting_agent.add_historical_data(current_data)

        # Train models periodically
        if step % 24 == 0 and step >= 24:
            forecasting_agent.train_models()

        # Generate forecasts
        forecasts = []
        if forecasting_agent.consumption_model is not None:
            forecasts = forecasting_agent.forecast(current_data)

        # Calculate storage levels
        total_capacity = sum(
            storage.capacity for storage in optimization_agent.storages
        )
        total_current_level = sum(
            storage.current_level for storage in optimization_agent.storages
        )
        storage_level_percentage = (
            total_current_level / total_capacity if total_capacity > 0 else 0
        )

        # Update storage thresholds
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

        #
