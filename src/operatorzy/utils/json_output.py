# src/utils/json_output.py

import json
import datetime
from pathlib import Path


def generate_dashboard_json(
    cooperative, hourly_data, time_labels, results_dir, formatted_date
):
    """Generate JSON data for frontend dashboard."""
    dashboard_data = {"data": []}

    for step in range(len(time_labels)):
        # Extract basic data
        hour_data = hourly_data[step]
        date_str = hour_data["date"]
        consumption = cooperative.history_consumption[step]
        production = cooperative.history_production[step]

        # Extract grid interactions from logs
        energy_bought_from_grid = 0
        cost_from_grid = 0
        energy_sold_to_grid = cooperative.history_energy_sold_to_grid[step]
        tokens_gained_from_grid = cooperative.history_tokens_gained_from_grid[step]
        tokens_burned_due_to_grid = 0

        # Parse log for this step to extract more detailed information
        if step < len(cooperative.logs):
            log = cooperative.logs[step]
            for line in log.split("\n"):
                if "Energy bought from grid:" in line:
                    try:
                        energy_bought_from_grid = float(
                            line.split(":")[1].split("kWh")[0].strip()
                        )
                    except:
                        pass
                if "cost:" in line and "grid" in line:
                    try:
                        cost_from_grid = float(
                            line.split(":")[2].split("CT")[0].strip()
                        )
                    except:
                        pass
                if "Tokens burned due to grid:" in line:
                    try:
                        tokens_burned_due_to_grid = float(line.split(":")[1].strip())
                    except:
                        pass

        # Get storage levels
        storage_levels = {}
        for storage_name in cooperative.history_storage:
            storage_levels[f"storage_{storage_name}_level"] = (
                cooperative.history_storage[storage_name][step]
            )

        # Determine AI decision
        ai_decision = determine_ai_decision(
            consumption,
            production,
            energy_bought_from_grid,
            energy_sold_to_grid,
            storage_levels,
        )

        # Create step data entry
        step_data = {
            "step": date_str,
            "total_consumption": round(consumption, 2),
            "total_production": round(production, 2),
            "energy_bought_from_grid": round(energy_bought_from_grid, 2),
            "cost_from_grid": round(cost_from_grid, 2),
            "energy_sold_to_grid": round(energy_sold_to_grid, 2),
            "tokens_gained_from_grid": round(tokens_gained_from_grid, 2),
            "tokens_burned_due_to_grid": round(tokens_burned_due_to_grid, 2),
            "token_balance": round(cooperative.history_token_balance[step], 2),
            "ai_decision": ai_decision,
        }

        # Add storage levels
        for storage_name, level in storage_levels.items():
            step_data[storage_name] = round(level, 2)

        dashboard_data["data"].append(step_data)

    # Write JSON to file
    with open(results_dir / f"dashboard_data_{formatted_date}.json", "w") as f:
        json.dump(dashboard_data, f, indent=2)

    return dashboard_data


def determine_ai_decision(
    consumption,
    production,
    energy_bought_from_grid,
    energy_sold_to_grid,
    storage_levels,
):
    """Determine the AI decision for the dashboard."""
    # Calculate net energy
    net_energy = production - consumption

    # Check if storage was used
    storage_used = False
    storage_charged = False
    storage_total = sum(storage_levels.values())

    # Determine the primary action
    if energy_sold_to_grid > 0:
        action = "SELL"
        amount = energy_sold_to_grid
        target = "GRID"
    elif energy_bought_from_grid > 0:
        action = "BUY"
        amount = energy_bought_from_grid
        target = "GRID"
    elif net_energy < 0 and energy_bought_from_grid < abs(net_energy):
        # Used storage to cover deficit
        action = "DISCHARGE"
        amount = abs(net_energy) - energy_bought_from_grid
        target = "STORAGE"
    elif net_energy > 0 and energy_sold_to_grid < net_energy:
        # Charged storage with surplus
        action = "CHARGE"
        amount = net_energy - energy_sold_to_grid
        target = "STORAGE"
    else:
        action = "BALANCE"
        amount = 0
        target = "COMMUNITY"

    # Create detailed decision object
    decision = {
        "action": action,
        "amount": round(amount, 2),
        "target": target,
        "reason": get_decision_reason(
            action, amount, consumption, production, storage_levels
        ),
        "forecast": {
            "expected_price_trend": "RISING"
            if action in ["CHARGE", "BUY"]
            else "FALLING",
            "expected_production": "HIGH" if production > consumption else "LOW",
        },
    }

    return decision


def get_decision_reason(action, amount, consumption, production, storage_levels):
    """Generate a reason for the AI decision."""
    if action == "BUY":
        return f"Energy deficit of {round(consumption - production, 2)} kWh with insufficient storage"
    elif action == "SELL":
        return f"Energy surplus of {round(production - consumption, 2)} kWh with optimal grid price"
    elif action == "CHARGE":
        return f"Energy surplus of {round(production - consumption, 2)} kWh stored for future use"
    elif action == "DISCHARGE":
        return f"Energy deficit of {round(consumption - production, 2)} kWh covered from storage"
    else:
        return "Community energy balance achieved"
