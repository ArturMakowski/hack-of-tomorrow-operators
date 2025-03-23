# src/utils/ai_visualization.py

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path


def plot_ai_results(cooperative, steps, labels, results_dir, formatted_date):
    """Generate enhanced plots for AI-powered simulation results."""
    fig, ax = plt.subplots(8, 1, figsize=(15, 40))

    # Plot 1: Energy Consumption and Production
    ax[0].plot(range(steps), cooperative.history_consumption, label="Total Consumption")
    ax[0].plot(range(steps), cooperative.history_production, label="Total Production")
    ax[0].fill_between(
        range(steps),
        cooperative.history_production,
        cooperative.history_consumption,
        where=(
            np.array(cooperative.history_production)
            > np.array(cooperative.history_consumption)
        ),
        color="green",
        alpha=0.3,
        label="Surplus",
    )
    ax[0].fill_between(
        range(steps),
        cooperative.history_production,
        cooperative.history_consumption,
        where=(
            np.array(cooperative.history_production)
            < np.array(cooperative.history_consumption)
        ),
        color="red",
        alpha=0.3,
        label="Deficit",
    )
    ax[0].set_title("Energy Consumption and Production")
    ax[0].set_xlabel("Time")
    ax[0].set_ylabel("Energy (kWh)")
    ax[0].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[0].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[0].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[0].grid(True, linestyle="--", alpha=0.7)

    # Plot 2: Energy Prices
    ax[1].plot(
        range(steps), cooperative.history_p2p_price, label="P2P Price", color="green"
    )
    ax[1].plot(
        range(steps),
        cooperative.history_purchase_price,
        label="Purchase Grid Price",
        color="red",
    )
    ax[1].plot(
        range(steps),
        cooperative.history_grid_price,
        label="Sale Grid Price",
        color="blue",
    )
    ax[1].set_title("Energy Prices Over Time")
    ax[1].set_xlabel("Time")
    ax[1].set_ylabel("Price (Tokens/kWh)")
    ax[1].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[1].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[1].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[1].grid(True, linestyle="--", alpha=0.7)

    # Plot 3: Storage Levels with Capacity Lines
    for storage_name, storage_levels in cooperative.history_storage.items():
        ax[2].plot(range(steps), storage_levels, label=f"Storage Level {storage_name}")
        # Add capacity line
        storage_capacity = next(
            (s.capacity for s in cooperative.storages if s.name == storage_name), 0
        )
        ax[2].axhline(
            y=storage_capacity,
            linestyle="--",
            color="gray",
            alpha=0.5,
            label=f"{storage_name} Capacity",
        )

    ax[2].set_title("Storage Levels Over Time")
    ax[2].set_xlabel("Time")
    ax[2].set_ylabel("Energy (kWh)")
    ax[2].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[2].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[2].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[2].grid(True, linestyle="--", alpha=0.7)

    # src/utils/ai_visualization.py (continued)

    # Plot 4: Energy Deficit
    ax[3].plot(
        range(steps),
        cooperative.history_energy_deficit,
        label="Energy Deficit",
        color="red",
    )
    ax[3].set_title("Energy Deficit Over Time")
    ax[3].set_xlabel("Time")
    ax[3].set_ylabel("Energy (kWh)")
    ax[3].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[3].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[3].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[3].grid(True, linestyle="--", alpha=0.7)

    # Plot 5: Energy Surplus
    ax[4].plot(
        range(steps),
        cooperative.history_energy_surplus,
        label="Energy Surplus",
        color="green",
    )
    ax[4].set_title("Energy Surplus Over Time")
    ax[4].set_xlabel("Time")
    ax[4].set_ylabel("Energy (kWh)")
    ax[4].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[4].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[4].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[4].grid(True, linestyle="--", alpha=0.7)

    # Plot 6: Token Balance
    ax[5].plot(
        range(steps),
        cooperative.history_token_balance,
        label="Token Balance",
        color="purple",
    )
    ax[5].set_title("Token Balance Over Time")
    ax[5].set_xlabel("Time")
    ax[5].set_ylabel("Tokens")
    ax[5].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[5].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[5].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[5].grid(True, linestyle="--", alpha=0.7)

    # Plot 7: Energy Sold to Grid
    ax[6].plot(
        range(steps),
        cooperative.history_energy_sold_to_grid,
        label="Energy Sold to Grid",
        color="blue",
    )
    ax[6].set_title("Energy Sold to Grid Over Time")
    ax[6].set_xlabel("Time")
    ax[6].set_ylabel("Energy (kWh)")
    ax[6].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[6].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[6].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[6].grid(True, linestyle="--", alpha=0.7)

    # Plot 8: Tokens Gained from Grid
    ax[7].plot(
        range(steps),
        cooperative.history_tokens_gained_from_grid,
        label="Tokens Gained from Grid",
        color="orange",
    )
    ax[7].set_title("Tokens Gained from Grid Over Time")
    ax[7].set_xlabel("Time")
    ax[7].set_ylabel("Tokens")
    ax[7].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[7].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[7].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[7].grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.savefig(results_dir / f"ai_simulation_plots_{formatted_date}.png")

    # Create additional analysis plots
    create_analysis_plots(cooperative, steps, labels, results_dir, formatted_date)


def create_analysis_plots(cooperative, steps, labels, results_dir, formatted_date):
    """Create additional analysis plots."""
    # Calculate metrics
    renewable_percentage = []
    grid_dependency = []
    storage_utilization = []

    for i in range(steps):
        if cooperative.history_consumption[i] > 0:
            renewable_used = min(
                cooperative.history_production[i], cooperative.history_consumption[i]
            )
            renewable_percentage.append(
                renewable_used / cooperative.history_consumption[i] * 100
            )

            grid_energy = cooperative.history_energy_deficit[i]
            grid_dependency.append(
                grid_energy / cooperative.history_consumption[i] * 100
                if cooperative.history_consumption[i] > 0
                else 0
            )
        else:
            renewable_percentage.append(0)
            grid_dependency.append(0)

        total_capacity = sum(storage.capacity for storage in cooperative.storages)
        total_used = sum(
            cooperative.history_storage[storage.name][i]
            for storage in cooperative.storages
        )
        storage_utilization.append(
            total_used / total_capacity * 100 if total_capacity > 0 else 0
        )

    # Create figure
    fig, ax = plt.subplots(3, 1, figsize=(15, 18))

    # Plot 1: Renewable Energy Percentage
    ax[0].plot(
        range(steps), renewable_percentage, label="Renewable Energy %", color="green"
    )
    ax[0].set_title("Renewable Energy Percentage Over Time")
    ax[0].set_xlabel("Time")
    ax[0].set_ylabel("Percentage (%)")
    ax[0].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[0].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[0].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[0].grid(True, linestyle="--", alpha=0.7)
    ax[0].set_ylim(0, 100)

    # Plot 2: Grid Dependency
    ax[1].plot(range(steps), grid_dependency, label="Grid Dependency %", color="red")
    ax[1].set_title("Grid Dependency Percentage Over Time")
    ax[1].set_xlabel("Time")
    ax[1].set_ylabel("Percentage (%)")
    ax[1].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[1].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[1].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[1].grid(True, linestyle="--", alpha=0.7)
    ax[1].set_ylim(0, 100)

    # Plot 3: Storage Utilization
    ax[2].plot(
        range(steps), storage_utilization, label="Storage Utilization %", color="blue"
    )
    ax[2].set_title("Storage Utilization Percentage Over Time")
    ax[2].set_xlabel("Time")
    ax[2].set_ylabel("Percentage (%)")
    ax[2].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[2].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[2].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[2].grid(True, linestyle="--", alpha=0.7)
    ax[2].set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig(results_dir / f"ai_analysis_plots_{formatted_date}.png")

    # Create token economy analysis
    create_token_economy_analysis(
        cooperative, steps, labels, results_dir, formatted_date
    )


def create_token_economy_analysis(
    cooperative, steps, labels, results_dir, formatted_date
):
    """Create token economy analysis plots."""
    # Calculate token metrics
    token_minted = []
    token_burned = []
    token_net_gain = []

    # Extract token information from logs
    for log in cooperative.logs:
        minted = 0
        burned = 0

        for line in log.split("\n"):
            if "Tokens minted" in line:
                try:
                    minted = float(line.split(":")[1].strip())
                except:
                    minted = 0
            if "Tokens burned" in line:
                try:
                    burned = float(line.split(":")[1].strip())
                except:
                    burned = 0

        token_minted.append(minted)
        token_burned.append(burned)
        token_net_gain.append(minted - burned)

    # Pad lists if needed
    while len(token_minted) < steps:
        token_minted.append(0)
        token_burned.append(0)
        token_net_gain.append(0)

    # Create figure
    fig, ax = plt.subplots(3, 1, figsize=(15, 18))

    # Plot 1: Tokens Minted
    ax[0].plot(range(steps), token_minted, label="Tokens Minted", color="green")
    ax[0].set_title("Tokens Minted Over Time")
    ax[0].set_xlabel("Time")
    ax[0].set_ylabel("Tokens")
    ax[0].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[0].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[0].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[0].grid(True, linestyle="--", alpha=0.7)

    # Plot 2: Tokens Burned
    ax[1].plot(range(steps), token_burned, label="Tokens Burned", color="red")
    ax[1].set_title("Tokens Burned Over Time")
    ax[1].set_xlabel("Time")
    ax[1].set_ylabel("Tokens")
    ax[1].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[1].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[1].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[1].grid(True, linestyle="--", alpha=0.7)

    # Plot 3: Net Token Gain
    ax[2].plot(range(steps), token_net_gain, label="Net Token Gain", color="blue")
    ax[2].set_title("Net Token Gain Over Time")
    ax[2].set_xlabel("Time")
    ax[2].set_ylabel("Tokens")
    ax[2].legend(loc="upper left", bbox_to_anchor=(1, 1))
    ax[2].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[2].set_xticklabels(labels[:: max(1, steps // 30)], rotation=90)
    ax[2].grid(True, linestyle="--", alpha=0.7)

    plt.tight_layout()
    plt.savefig(results_dir / f"token_economy_analysis_{formatted_date}.png")
