# src/agents/storage_management_agent.py


class StorageManagementAgent:
    def __init__(self, storages):
        """Initialize the Storage Management Agent."""
        self.storages = storages
        self.storage_history = {storage.name: [] for storage in storages}
        self.charge_thresholds = {
            storage.name: 0.7 for storage in storages
        }  # Default charge threshold
        self.discharge_thresholds = {
            storage.name: 0.3 for storage in storages
        }  # Default discharge threshold

    def update_thresholds(self, grid_costs, forecasts=None):
        """Update charging/discharging thresholds based on grid costs and forecasts."""
        # Calculate average grid prices
        avg_purchase = sum(gc["purchase"] for gc in grid_costs) / len(grid_costs)
        avg_sale = sum(gc["sale"] for gc in grid_costs) / len(grid_costs)

        # Find min and max prices
        min_purchase = min(gc["purchase"] for gc in grid_costs)
        max_purchase = max(gc["purchase"] for gc in grid_costs)
        min_sale = min(gc["sale"] for gc in grid_costs)
        max_sale = max(gc["sale"] for gc in grid_costs)

        # Update thresholds for each storage
        for storage in self.storages:
            # Base threshold on storage capacity - larger storages can be more conservative
            capacity_factor = storage.capacity / max(s.capacity for s in self.storages)

            # Adjust charge threshold - charge more when prices are low
            price_range = max_purchase - min_purchase
            if price_range > 0:
                price_position = (avg_purchase - min_purchase) / price_range
                # Lower threshold (more charging) when prices are low
                self.charge_thresholds[storage.name] = 0.8 - (
                    0.3 * price_position * capacity_factor
                )

            # Adjust discharge threshold - discharge more when prices are high
            price_range = max_sale - min_sale
            if price_range > 0:
                price_position = (avg_sale - min_sale) / price_range
                # Higher threshold (more discharging) when prices are high
                self.discharge_thresholds[storage.name] = 0.2 + (
                    0.3 * price_position * capacity_factor
                )

        return self.charge_thresholds, self.discharge_thresholds

    def optimize_storage_allocation(self, net_energy, grid_costs, hour):
        """Optimize how energy is allocated to different storage units."""
        # Get current grid prices
        current_purchase = grid_costs[hour % len(grid_costs)]["purchase"]
        current_sale = grid_costs[hour % len(grid_costs)]["sale"]

        # Calculate total available capacity and current level
        total_capacity = sum(storage.capacity for storage in self.storages)
        total_current = sum(storage.current_level for storage in self.storages)
        current_percentage = total_current / total_capacity if total_capacity > 0 else 0

        # Sort storages by different criteria depending on whether we're charging or discharging
        if net_energy > 0:  # We have surplus energy to store
            # Sort by available capacity (descending) and then by capacity (ascending)
            # This prioritizes filling smaller storages with more available capacity
            sorted_storages = sorted(
                self.storages,
                key=lambda s: (
                    (s.capacity - s.current_level) / s.capacity
                    if s.capacity > 0
                    else 0,
                    -s.capacity,
                ),
            )

            # If prices are very low, be more aggressive with charging
            if current_purchase < min(gc["purchase"] for gc in grid_costs) * 1.1:
                charge_factor = 1.0  # Charge at full capacity
            else:
                charge_factor = 0.8  # More conservative charging

            remaining_energy = net_energy
            allocation = {}

            for storage in sorted_storages:
                if remaining_energy <= 0:
                    break

                # Calculate how much to charge this storage
                available = storage.capacity - storage.current_level
                charge_amount = min(remaining_energy, available * charge_factor)

                if charge_amount > 0:
                    allocation[storage.name] = charge_amount
                    remaining_energy -= charge_amount

            return allocation, remaining_energy

        elif net_energy < 0:  # We need energy from storage
            # Sort by current level (descending) and then by capacity (descending)
            # This prioritizes discharging from larger storages with more energy
            sorted_storages = sorted(
                self.storages,
                key=lambda s: (
                    -s.current_level / s.capacity if s.capacity > 0 else 0,
                    -s.capacity,
                ),
            )

            # If prices are very high, be more aggressive with discharging
            if current_purchase > max(gc["purchase"] for gc in grid_costs) * 0.9:
                discharge_factor = 1.0  # Discharge as much as needed
            else:
                discharge_factor = 0.8  # More conservative discharging

            remaining_need = -net_energy
            allocation = {}

            for storage in sorted_storages:
                if remaining_need <= 0:
                    break

                # Calculate how much to discharge from this storage
                available = storage.current_level
                discharge_amount = min(remaining_need, available * discharge_factor)

                if discharge_amount > 0:
                    allocation[
                        storage.name
                    ] = -discharge_amount  # Negative for discharge
                    remaining_need -= discharge_amount

            return allocation, -remaining_need if remaining_need > 0 else 0

        else:  # No net energy change needed
            return {}, 0
