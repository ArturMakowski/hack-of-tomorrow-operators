from operatorzy.models.cooperative import Cooperative
from operatorzy.utils.helper_functions import (
    plot_results,
    save_results_to_csv,
    load_profiles,
    load_storages,
)
import sys
import csv
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


def load_grid_costs(filepath):
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


if __name__ == "__main__":
    if len(sys.argv) < 1:
        print("No required parameter: storage file path")
        sys.exit(1)
    if len(sys.argv) < 2:
        print("No required parameter: profiles directory path")
        sys.exit(1)
    if len(sys.argv) < 3:
        print("No required parameter: logs directory path")
        sys.exit(1)
    if len(sys.argv) < 4:
        print("No required parameter: grid costs file path")
        sys.exit(1)

    storages = load_storages(sys.argv[1])

    config = {"storages": storages}

    cooperative = Cooperative(config, initial_token_balance=100)

    # Load profiles
    profiles = load_profiles(sys.argv[2])

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
                "hour": hour,
                "consumption": total_consumption,
                "production": total_production,
                "date": date,
            }
        )

    # Load grid costs
    grid_costs = load_grid_costs(sys.argv[4])

    p2p_base_price = 0.5
    min_price = 0.2
    token_mint_rate = 0.1
    token_burn_rate = 0.1

    cooperative.simulate(
        len(hourly_data),
        p2p_base_price,
        1,
        min_price,
        token_mint_rate,
        token_burn_rate,
        hourly_data,
        grid_costs,
        profiles,
    )

    results_dir = Path("results")
    results_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d_%H:%M:%S")

    # Save results to CSV files
    save_results_to_csv(cooperative, time_labels, results_dir, formatted_date)

    # Save logs to a text file
    log_dir = Path(sys.argv[3])
    log_dir.mkdir(parents=True, exist_ok=True)

    cooperative.save_logs(str(log_dir / f"simulation_{formatted_date}.log"))

    # Generate labels for the X-axis
    labels = time_labels

    # Assign the modified method to the cooperative object
    cooperative.plot_results = plot_results.__get__(cooperative)

    cooperative.plot_results(len(hourly_data), labels, results_dir, formatted_date)
