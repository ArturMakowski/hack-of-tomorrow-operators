// Utility functions for formatting
export function formatCurrency(value: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(value)
}

export function formatNumber(value: number): string {
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: 0,
  }).format(value)
}

// Mock data generator for the energy management dashboard

// Helper function to generate timestamps
function generateTimestamps(count: number, interval: number, unit: "hour" | "day" | "week" | "month") {
  const now = new Date()
  const timestamps = []

  for (let i = count - 1; i >= 0; i--) {
    const date = new Date(now)

    switch (unit) {
      case "hour":
        date.setHours(date.getHours() - i * interval)
        break
      case "day":
        date.setDate(date.getDate() - i * interval)
        break
      case "week":
        date.setDate(date.getDate() - i * interval * 7)
        break
      case "month":
        date.setMonth(date.getMonth() - i * interval)
        break
    }

    timestamps.push(date.toISOString())
  }

  return timestamps
}

// Generate random number within range
function randomInRange(min: number, max: number) {
  return Math.floor(Math.random() * (max - min + 1)) + min
}

// Generate consumption data
function generateConsumptionData(timestamps: string[]) {
  return timestamps.map((timestamp) => {
    const date = new Date(timestamp)
    const hour = date.getHours()

    // Simulate daily patterns
    const timeMultiplier = hour >= 8 && hour <= 20 ? 1.5 : 0.7

    const residential = randomInRange(20, 40) * timeMultiplier
    const commercial = randomInRange(40, 80) * timeMultiplier
    const industrial = randomInRange(60, 120) * timeMultiplier

    return {
      timestamp,
      residential,
      commercial,
      industrial,
      total: residential + commercial + industrial,
    }
  })
}

// Generate production data
function generateProductionData(timestamps: string[]) {
  return timestamps.map((timestamp) => {
    const date = new Date(timestamp)
    const hour = date.getHours()

    // Solar production depends on time of day
    const solarMultiplier = hour >= 8 && hour <= 16 ? (1 - Math.abs(hour - 12) / 8) * 2 : 0.1

    const solar = randomInRange(20, 60) * solarMultiplier
    const wind = randomInRange(15, 45)
    const hydro = randomInRange(30, 50)
    const thermal = randomInRange(40, 70)

    return {
      timestamp,
      solar,
      wind,
      hydro,
      thermal,
      total: solar + wind + hydro + thermal,
    }
  })
}

// Generate storage data
function generateStorageData(timestamps: string[], consumption: any[], production: any[]) {
  const batteryCapacity = 500
  let currentLevel = randomInRange(200, 300)

  return timestamps.map((timestamp, index) => {
    const totalConsumption = consumption[index].total
    const totalProduction = production[index].total

    // Calculate charging/discharging based on production vs consumption
    const energyDifference = totalProduction - totalConsumption
    const chargingRate = energyDifference > 0 ? energyDifference * 0.8 : 0
    const dischargingRate = energyDifference < 0 ? Math.abs(energyDifference) * 0.8 : 0

    // Update battery level
    currentLevel = Math.min(batteryCapacity, Math.max(0, currentLevel + chargingRate - dischargingRate))

    return {
      timestamp,
      batteryLevel: Math.round(currentLevel),
      batteryCapacity,
      chargingRate: Math.round(chargingRate),
      dischargingRate: Math.round(dischargingRate),
    }
  })
}

// Generate grid interaction data
function generateGridData(timestamps: string[], consumption: any[], production: any[]) {
  return timestamps.map((timestamp, index) => {
    const totalConsumption = consumption[index].total
    const totalProduction = production[index].total

    // Calculate import/export based on production vs consumption
    const energyDifference = totalProduction - totalConsumption
    const importValue = energyDifference < 0 ? Math.abs(energyDifference) : 0
    const exportValue = energyDifference > 0 ? energyDifference : 0

    // Random price fluctuations
    const basePrice = 0.12 // Base price per kWh
    const priceVariation = (Math.random() - 0.5) * 0.05
    const price = basePrice + priceVariation

    return {
      timestamp,
      import: Math.round(importValue),
      export: Math.round(exportValue),
      netExchange: Math.round(exportValue - importValue),
      price: Number.parseFloat(price.toFixed(3)),
    }
  })
}

// Generate AI decisions
function generateAIDecisions() {
  const categories = ["storage", "grid", "production", "consumption"]
  const storageActions = [
    "Increased battery charging rate",
    "Reduced battery discharge rate",
    "Optimized storage capacity utilization",
    "Scheduled preventive maintenance",
  ]
  const gridActions = [
    "Reduced grid import during peak hours",
    "Increased grid export during high price period",
    "Balanced load distribution",
    "Negotiated better grid exchange rates",
  ]
  const productionActions = [
    "Adjusted solar panel angles",
    "Optimized wind turbine operation",
    "Scheduled maintenance for hydro generators",
    "Reduced thermal generation during low demand",
  ]
  const consumptionActions = [
    "Shifted non-critical loads to off-peak hours",
    "Implemented demand response program",
    "Reduced HVAC consumption during peak hours",
    "Optimized industrial process scheduling",
  ]

  const decisions = []

  // Generate 20 random decisions
  for (let i = 0; i < 20; i++) {
    const category = categories[Math.floor(Math.random() * categories.length)] as
      | "storage"
      | "grid"
      | "production"
      | "consumption"
    let action = ""

    switch (category) {
      case "storage":
        action = storageActions[Math.floor(Math.random() * storageActions.length)]
        break
      case "grid":
        action = gridActions[Math.floor(Math.random() * gridActions.length)]
        break
      case "production":
        action = productionActions[Math.floor(Math.random() * productionActions.length)]
        break
      case "consumption":
        action = consumptionActions[Math.floor(Math.random() * consumptionActions.length)]
        break
    }

    // Generate random timestamp within the last 24 hours
    const timestamp = new Date()
    timestamp.setHours(timestamp.getHours() - Math.floor(Math.random() * 24))

    const decision = {
      id: `decision-${i}`,
      timestamp: timestamp.toISOString(),
      category,
      action,
      reasoning: getRandomReasoning(category, action),
      impact: {
        energySavings: category !== "grid" ? randomInRange(5, 50) : undefined,
        costSavings: randomInRange(10, 200) / 10,
        co2Reduction: category === "production" || category === "consumption" ? randomInRange(2, 30) : undefined,
      },
    }

    decisions.push(decision)
  }

  return decisions
}

// Generate reasoning for AI decisions
function getRandomReasoning(category: string, action: string): string {
  const storageReasonings = [
    "Forecasted increased renewable production in the next 4 hours.",
    "Battery state of health analysis indicated optimal charging conditions.",
    "Predicted grid price increase during peak demand hours.",
    "Detected potential grid instability based on frequency analysis.",
  ]

  const gridReasonings = [
    "Real-time pricing data indicated favorable export conditions.",
    "Detected grid congestion patterns in the local distribution network.",
    "Forecasted demand spike in the next 2 hours based on historical patterns.",
    "Identified opportunity for arbitrage between import and export prices.",
  ]

  const productionReasonings = [
    "Weather forecast indicated optimal conditions for renewable generation.",
    "Detected efficiency decrease in generation equipment.",
    "Optimized for lowest carbon intensity per kWh produced.",
    "Balanced production mix to minimize operational costs.",
  ]

  const consumptionReasonings = [
    "Identified non-critical loads that could be shifted to off-peak hours.",
    "Detected abnormal consumption patterns indicating potential inefficiencies.",
    "Forecasted demand response event from grid operator.",
    "Optimized consumption schedule based on production and storage availability.",
  ]

  let reasonings
  switch (category) {
    case "storage":
      reasonings = storageReasonings
      break
    case "grid":
      reasonings = gridReasonings
      break
    case "production":
      reasonings = productionReasonings
      break
    case "consumption":
      reasonings = consumptionReasonings
      break
    default:
      reasonings = storageReasonings
  }

  return reasonings[Math.floor(Math.random() * reasonings.length)]
}

// Main function to generate all data
export function fetchEnergyData(
  timeGranularity: "hourly" | "daily" | "weekly" | "monthly",
  comparisonPeriod: "none" | "previous" | "baseline" = "none",
) {
  let timestamps: string[] = []

  switch (timeGranularity) {
    case "hourly":
      timestamps = generateTimestamps(24, 1, "hour")
      break
    case "daily":
      timestamps = generateTimestamps(30, 1, "day")
      break
    case "weekly":
      timestamps = generateTimestamps(12, 1, "week")
      break
    case "monthly":
      timestamps = generateTimestamps(12, 1, "month")
      break
  }

  const consumption = generateConsumptionData(timestamps)
  const production = generateProductionData(timestamps)
  const storage = generateStorageData(timestamps, consumption, production)
  const grid = generateGridData(timestamps, consumption, production)
  const decisions = generateAIDecisions()

  // Generate new data for hackathon metrics
  const energyBalance = generateEnergyBalanceMetrics(consumption, production, storage, grid, comparisonPeriod)
  const financial = generateFinancialImpactData(timestamps, grid, comparisonPeriod)
  const storageOptimization = generateStorageOptimizationData(timestamps, storage, comparisonPeriod)
  const tokens = generateTokenEconomyData(timestamps, grid, comparisonPeriod)

  return {
    energyBalance,
    financial,
    storage: storageOptimization,
    tokens,
    decisions,
  }
}

// Generate energy balance metrics
function generateEnergyBalanceMetrics(
  consumption: any[],
  production: any[],
  storage: any[],
  grid: any[],
  comparisonPeriod: string,
) {
  const totalConsumption = consumption.reduce((sum, item) => sum + item.total, 0)
  const totalProduction = production.reduce((sum, item) => sum + item.total, 0)
  const gridBought = grid.reduce((sum, item) => sum + item.import, 0)
  const gridSold = grid.reduce((sum, item) => sum + item.export, 0)
  const storageUsed = storage.reduce((sum, item) => sum + item.dischargingRate, 0)

  // Calculate metrics with AI impact
  const selfSufficiencyRate = Math.min(1, totalProduction / totalConsumption)

  // Simulate improvement based on comparison period
  let gridDependencyReduction = 25
  let efficiencyImprovement = 18

  if (comparisonPeriod === "previous") {
    gridDependencyReduction = 15
    efficiencyImprovement = 12
  } else if (comparisonPeriod === "baseline") {
    gridDependencyReduction = 35
    efficiencyImprovement = 28
  }

  return {
    totalConsumption,
    totalProduction,
    gridBought,
    gridSold,
    storageUsed,
    gridDependencyReduction,
    efficiencyImprovement,
    selfSufficiencyRate,
  }
}

// Generate financial impact data
function generateFinancialImpactData(timestamps: string[], grid: any[], comparisonPeriod: string) {
  return timestamps.map((timestamp, index) => {
    const gridItem = grid[index]
    const date = new Date(timestamp)
    const hour = date.getHours()

    // Base price varies by time of day
    const basePrice = hour >= 17 && hour <= 21 ? 0.25 : 0.15

    // Calculate costs and revenues
    const costBought = gridItem.import * basePrice
    const revenueSold = gridItem.export * (basePrice * 0.8)

    // Token economy impact
    const tokenCosts = gridItem.import * 0.05
    const tokenRevenue = gridItem.export * 0.08

    // Calculate net savings
    const netSavings = revenueSold + tokenRevenue - costBought - tokenCosts

    // AI impact varies by comparison period
    let aiImpactMultiplier = 0.2
    if (comparisonPeriod === "previous") {
      aiImpactMultiplier = 0.15
    } else if (comparisonPeriod === "baseline") {
      aiImpactMultiplier = 0.3
    }

    const aiImpact = Math.abs(netSavings) * aiImpactMultiplier

    return {
      timestamp,
      costBought: -costBought, // Negative to show as cost
      revenueSold,
      tokenCosts: -tokenCosts, // Negative to show as cost
      tokenRevenue,
      netSavings,
      aiImpact,
    }
  })
}

// Generate storage optimization data
function generateStorageOptimizationData(timestamps: string[], storageData: any[], comparisonPeriod: string) {
  // Generate timeseries data
  const timeseries = timestamps.map((timestamp, index) => {
    const storageItem = storageData[index]
    const date = new Date(timestamp)
    const hour = date.getHours()

    // Calculate optimal level based on time of day
    // Higher during off-peak, lower during peak hours
    const optimalLevel = hour >= 9 && hour <= 20 ? storageItem.batteryCapacity * 0.3 : storageItem.batteryCapacity * 0.7

    return {
      timestamp,
      storageLevel: storageItem.batteryLevel,
      energyAdded: storageItem.chargingRate,
      energyRetrieved: storageItem.dischargingRate,
      optimalLevel,
    }
  })

  // Calculate metrics
  const totalCapacity = storageData[0].batteryCapacity
  const averageLevel = timeseries.reduce((sum, item) => sum + item.storageLevel, 0) / timeseries.length
  const averageUtilization = (averageLevel / totalCapacity) * 100

  // Efficiency and savings vary by comparison period
  let cycleEfficiency = 92
  let costSavings = 125.75
  let peakShavingEvents = 8

  if (comparisonPeriod === "previous") {
    cycleEfficiency = 88
    costSavings = 95.5
    peakShavingEvents = 6
  } else if (comparisonPeriod === "baseline") {
    cycleEfficiency = 95
    costSavings = 185.25
    peakShavingEvents = 12
  }

  return {
    timeseries,
    metrics: {
      averageUtilization,
      cycleEfficiency,
      costSavings,
      peakShavingEvents,
    },
  }
}

// Generate token economy data
function generateTokenEconomyData(timestamps: string[], grid: any[], comparisonPeriod: string) {
  let tokenBalance = 5000
  const baseTokenPrice = 0.12

  // Generate timeseries data
  const timeseries = timestamps.map((timestamp, index) => {
    const gridItem = grid[index]
    const date = new Date(timestamp)

    // Calculate token metrics
    const tokensEarned = gridItem.export * 2.5
    const tokensBurned = gridItem.import * 1.2
    const gridTokensBurned = gridItem.import * 0.8

    // Update token balance
    tokenBalance = tokenBalance + tokensEarned - tokensBurned - gridTokensBurned

    // Token price fluctuates slightly
    const priceVariation = (Math.random() - 0.5) * 0.02
    const tokenPrice = baseTokenPrice + priceVariation

    return {
      timestamp,
      tokenBalance,
      tokensEarned,
      tokensBurned,
      gridTokensBurned,
      tokenPrice,
    }
  })

  // Calculate aggregate metrics
  const totalTokensEarned = timeseries.reduce((sum, item) => sum + item.tokensEarned, 0)
  const totalTokensBurned = timeseries.reduce((sum, item) => sum + item.tokensBurned + item.gridTokensBurned, 0)
  const netTokenChange = totalTokensEarned - totalTokensBurned

  // Token value change varies by comparison period
  let tokenValueChange = 5.2

  if (comparisonPeriod === "previous") {
    tokenValueChange = 2.8
  } else if (comparisonPeriod === "baseline") {
    tokenValueChange = 12.5
  }

  return {
    timeseries,
    metrics: {
      totalTokensEarned,
      totalTokensBurned,
      netTokenChange,
      tokenValueChange,
    },
  }
}

