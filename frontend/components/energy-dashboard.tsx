"use client";

import { useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { fetchEnergyData } from "@/lib/data";

export default function EnergyDashboard() {
  const [timeGranularity, setTimeGranularity] = useState<
    "hourly" | "daily" | "weekly" | "monthly"
  >("daily");
  const [comparisonPeriod, setComparisonPeriod] = useState<
    "none" | "previous" | "baseline"
  >("previous");
  const energyData = fetchEnergyData(timeGranularity, comparisonPeriod);

  return (
    <div className="container mx-auto py-6 space-y-8">
      <div className="flex flex-col space-y-2">
        <h1 className="text-3xl font-bold tracking-tight">
          AI Energy Management Dashboard
        </h1>
        <p className="text-muted-foreground">
          Showcasing AI agent's impact on energy efficiency, cost reduction, and
          token economy
        </p>
      </div>

      <div className="flex flex-col sm:flex-row justify-between gap-4">
        <TimeGranularitySelector
          value={timeGranularity}
          onChange={(value) =>
            setTimeGranularity(
              value as "hourly" | "daily" | "weekly" | "monthly"
            )
          }
        />
        <TimeComparisonSelector
          value={comparisonPeriod}
          onChange={(value) =>
            setComparisonPeriod(value as "none" | "previous" | "baseline")
          }
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <EnergyBalanceMetrics data={energyData.energyBalance} />
      </div>

      <Tabs defaultValue="financial" className="space-y-4">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="financial">Financial Impact</TabsTrigger>
          <TabsTrigger value="storage">Storage Optimization</TabsTrigger>
          <TabsTrigger value="token">Token Economy</TabsTrigger>
        </TabsList>

        <TabsContent value="financial" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Financial Impact</CardTitle>
              <CardDescription>
                Cost reduction and revenue generation metrics
              </CardDescription>
            </CardHeader>
            <CardContent className="pl-2">
              <FinancialImpactMetrics
                data={energyData.financial}
                timeGranularity={timeGranularity}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="storage" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Storage Optimization</CardTitle>
              <CardDescription>
                Battery storage utilization and efficiency
              </CardDescription>
            </CardHeader>
            <CardContent className="pl-2">
              <StorageOptimizationChart
                data={energyData.storage}
                timeGranularity={timeGranularity}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="token" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Token Economy</CardTitle>
              <CardDescription>
                Token balance, earnings, and expenditures
              </CardDescription>
            </CardHeader>
            <CardContent className="pl-2">
              <TokenEconomyChart
                data={energyData.tokens}
                timeGranularity={timeGranularity}
              />
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Card>
        <CardHeader>
          <CardTitle>AI Decision Impact Log</CardTitle>
          <CardDescription>
            Key decisions and their measurable impact on efficiency and costs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <AIDecisionLog decisions={energyData.decisions} />
        </CardContent>
      </Card>
    </div>
  );
}
