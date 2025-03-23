import matplotlib.pyplot as plt
import os
import pandas as pd

def load_profiles(directory):
    profiles = {}
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            filepath = os.path.join(directory, filename)
            df = pd.read_csv(filepath)
            ppe = filename.split('_')[-1].split('.')[0]  # Wyciągnij nazwę PPE z nazwy pliku
            profiles[ppe] = df
    return profiles

def load_storages(filepath):
    storages = []
    df = pd.read_csv(filepath, comment='#')
    for _, row in df.iterrows():
        storages.append({'id': row['id'], 'capacity': row['capacity']})
    return storages

def save_results_to_csv(cooperative, time_labels, results_dir, formatted_date):
    data = {
        'Time': time_labels,
        'Total Consumption': cooperative.history_consumption,
        'Total Production': cooperative.history_production,
        'Token Balance': cooperative.history_token_balance,
        'P2P Price': cooperative.history_p2p_price,
        'Grid Price': cooperative.history_grid_price,
        'Purchase Price': cooperative.history_purchase_price,
        'Energy Deficit': cooperative.history_energy_deficit,
        'Energy Surplus': cooperative.history_energy_surplus
    }
    
    # Add storage levels to the data dictionary
    for storage_name, storage_levels in cooperative.history_storage.items():
        data[f'Storage Level {storage_name}'] = storage_levels
    
    df = pd.DataFrame(data)
    df.to_csv(results_dir / f'simulation_results_{formatted_date}.csv', index=False)
    

def plot_results(self, steps, labels, results_dir, formatted_date):
    fig, ax = plt.subplots(6, 1, figsize=(15, 30))
    
    ax[0].plot(range(steps), self.history_consumption, label='Total Consumption')
    ax[0].plot(range(steps), self.history_production, label='Total Production')
    ax[0].set_title('Energy Consumption and Production')
    ax[0].set_xlabel('Time')
    ax[0].set_ylabel('Energy (kWh)')
    ax[0].legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax[0].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[0].set_xticklabels(labels[::max(1, steps // 30)], rotation=90)
    
    ax[1].plot(range(steps), self.history_p2p_price, label='P2P Price')
    ax[1].plot(range(steps), self.history_purchase_price, label='Purchase Grid Price')
    ax[1].plot(range(steps), self.history_grid_price, label='Sale Grid Price')

    ax[1].set_title('Energy Prices Over Time')
    ax[1].set_xlabel('Time')
    ax[1].set_ylabel('Price (Tokens/kWh)')
    ax[1].legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax[1].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[1].set_xticklabels(labels[::max(1, steps // 30)], rotation=90)
    
    for storage_name, storage_levels in self.history_storage.items():
        ax[2].plot(range(steps), storage_levels, label=f'Storage Level {storage_name}')
    ax[2].set_title('Storage Levels Over Time')
    ax[2].set_xlabel('Time')
    ax[2].set_ylabel('Energy (kWh)')
    ax[2].legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax[2].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[2].set_xticklabels(labels[::max(1, steps // 30)], rotation=90)
    
    ax[3].plot(range(steps), self.history_energy_deficit, label='Energy Deficit')
    ax[3].set_title('Energy Deficit Over Time')
    ax[3].set_xlabel('Time')
    ax[3].set_ylabel('Energy (kWh)')
    ax[3].legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax[3].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[3].set_xticklabels(labels[::max(1, steps // 30)], rotation=90)
    
    ax[4].plot(range(steps), self.history_energy_surplus, label='Energy Surplus')
    ax[4].set_title('Energy Surplus Over Time')
    ax[4].set_xlabel('Time')
    ax[4].set_ylabel('Energy (kWh)')
    ax[4].legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax[4].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[4].set_xticklabels(labels[::max(1, steps // 30)], rotation=90)

    ax[5].plot(range(steps), self.history_token_balance, label='Token Balance')
    ax[5].set_title('Token Balance Over Time')
    ax[5].set_xlabel('Time')
    ax[5].set_ylabel('Tokens')
    ax[5].legend(loc='upper left', bbox_to_anchor=(1, 1))
    ax[5].set_xticks(range(0, steps, max(1, steps // 30)))
    ax[5].set_xticklabels(labels[::max(1, steps // 30)], rotation=90)
    
    plt.tight_layout()
    plt.savefig(results_dir / f'simulation_plots_{formatted_date}.png')  # Save the plot to a file
    