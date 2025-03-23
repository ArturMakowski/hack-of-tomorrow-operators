import decisionData from "./decision-data.json";
import realData from "./real_data.json";
import realData1 from "./real_data1.json";

import { z } from "zod";

const AIDecisionSchema = z.object({
  action: z.enum(["BUY", "SELL", "STORE", "HOLD", "DISCHARGE"]),
  amount: z.number(),
});

const EnergyDecisionSchema = z.object({
  step: z.string().regex(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/),
  total_consumption: z.number(),
  total_production: z.number(),
  energy_bought_from_grid: z.number(),
  cost_from_grid: z.number(),
  energy_sold_to_grid: z.number(),
  tokens_gained_from_grid: z.number(),
  tokens_burned_due_to_grid: z.number(),
  storage_S1_level: z.number(),
  storage_S2_level: z.number(),
  token_balance: z.number(),
  ai_decision: AIDecisionSchema,
});

const DecisionDataSchema = z.object({
  data: z.array(EnergyDecisionSchema),
});

// Parse and validate the data
const parsedData = DecisionDataSchema.parse(realData1);

export type AIDecision = z.infer<typeof AIDecisionSchema>;
export type EnergyDecision = z.infer<typeof EnergyDecisionSchema>;
export const energyDecisionData = parsedData.data as EnergyDecision[];
