# Hack of Tomorrow - Energy AI Agents Simulation

A simulation platform for AI energy management agents that optimize grid operations through intelligent decision-making.

## Overview

This project demonstrates how AI agents can make autonomous decisions to optimize energy consumption, production, and storage in a simulated environment. The platform visualizes agent decisions and their impact on energy efficiency, costs, and token economy.

## Directory Structure

```text
arturmakowski-hack-of-tomorrow-operators/
├── README.md               # This file
├── CHANGELOG.md            # Project version history and changes
├── .dockerignore           # Files excluded from Docker builds
├── data/                   # Data storage for simulation inputs/outputs
├── docker/                 # Docker configuration files
├── docs/                   # Project documentation
├── energy-ai-agents-simulation/ # Core simulation engine
├── frontend/               # Next.js web interface
└── src/                    # Source code for operators
    └── operatorzy/         # Python modules for energy operators
```

## Features

- **AI Decision Explorer**: Visualize and analyze AI agent decisions in real-time
- **Energy Dashboard**: Monitor energy production, consumption, and grid interactions
- **Token Economy**: Track token balances, earnings, and expenditures in the simulation
- **Storage Optimization**: Visualize battery storage utilization and efficiency

## Frontend

The frontend is built with Next.js and includes:

- **Decision Explorer**: Interactive visualization of AI agent decisions and their impacts
- **Energy Dashboard**: Real-time monitoring of energy metrics
- **Component Library**: Built with shadcn/ui and Tailwind CSS for a responsive interface
- **Data Visualization**: Charts and graphs powered by Recharts

## Getting Started

### Prerequisites

- Node.js (v18+)
- Python 3.8+
- Docker (optional)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/arturmakowski-hack-of-tomorrow-operators.git
   cd arturmakowski-hack-of-tomorrow-operators
   ```

2. Set up the frontend:

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

3. Set up the simulation environment:

   ```bash
   # Install Python dependencies
   pip install -r requirements.txt
   ```

### Running the Simulation

```bash
# Start the simulation
python -m energy-ai-agents-simulation.run

# In a separate terminal, run the frontend
cd frontend
npm run dev
```

## Architecture

The system consists of:

1. **Energy AI Agents**: Autonomous decision-makers that optimize energy usage
2. **Simulation Engine**: Simulates energy production, consumption, and market dynamics
3. **Frontend Interface**: Visualizes agent decisions and their impacts
4. **Token Economy**: Incentivizes efficient energy management

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- This project was created as part of the Hack of Tomorrow hackathon
- Special thanks to all contributors and participants
