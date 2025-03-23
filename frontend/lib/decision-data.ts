import decisionData from "./decision-data.json";
import { z } from "zod";

const AIDecisionSchema = z.object({
  action: z.enum(["BUY", "SELL", "STORE", "HOLD"]),
  amount: z.number().min(0),
});

const EnergyDecisionSchema = z.object({
  step: z.string().regex(/^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$/),
  total_consumption: z.number().min(0),
  total_production: z.number().min(0),
  energy_bought_from_grid: z.number().min(0),
  cost_from_grid: z.number().min(0),
  energy_sold_to_grid: z.number().min(0),
  tokens_gained_from_grid: z.number().min(0),
  tokens_burned_due_to_grid: z.number().min(0),
  storage_S1_level: z.number().min(0).max(20),
  storage_S2_level: z.number().min(0).max(10),
  token_balance: z.number(),
  ai_decision: AIDecisionSchema,
});

const DecisionDataSchema = z.object({
  data: z.array(EnergyDecisionSchema),
});

// Parse and validate the data
const parsedData = DecisionDataSchema.parse(decisionData);

export type AIDecision = z.infer<typeof AIDecisionSchema>;
export type EnergyDecision = z.infer<typeof EnergyDecisionSchema>;
export const energyDecisionData = parsedData.data as EnergyDecision[];
