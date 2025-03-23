"use client";

import { useState, useEffect, useRef } from "react";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import {
  ChevronLeft,
  ChevronRight,
  Zap,
  Battery,
  Coins,
  TrendingUp,
  TrendingDown,
  Clock,
  RotateCcw,
} from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { ScrollArea } from "@/components/ui/scroll-area";
import { formatCurrency, formatNumber, formatEnergy } from "@/lib/utils";
import { energyDecisionData, type EnergyDecision } from "@/lib/decision-data";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

type AIDecision = {
  action: "BUY" | "SELL" | "STORE" | "HOLD";
  amount: number;
};

const STORAGE_CONFIG = [
  { id: "S1", name: "Storage S1", maxCapacity: 20 },
  { id: "S2", name: "Storage S2", maxCapacity: 10 },
] as const;

export default function DecisionExplorer() {
  const [currentStep, setCurrentStep] = useState(0);
  const [previousData, setPreviousData] = useState<EnergyDecision | null>(null);
  const [highlightedFields, setHighlightedFields] = useState<string[]>([]);
  const [isPlaying, setIsPlaying] = useState(false);
  const currentDecisionRef = useRef<HTMLButtonElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const totalSteps = energyDecisionData.length;
  const currentData = energyDecisionData[currentStep];

  const getYAxisDomain = () => {
    const values = energyDecisionData
      .slice(0, currentStep + 1)
      .map((d) => d.token_balance);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const padding = (max - min) * 0.1;
    return [Math.floor(min - padding), Math.ceil(max + padding)];
  };

  useEffect(() => {
    if (currentStep > 0) {
      const prevData = energyDecisionData[currentStep - 1];
      setPreviousData(prevData);

      const changedFields: string[] = [];

      Object.keys(currentData).forEach((key) => {
        const currentValue = currentData[key as keyof EnergyDecision];
        const prevValue = prevData[key as keyof EnergyDecision];

        if (typeof currentValue === "number" && typeof prevValue === "number") {
          const change = Math.abs(currentValue - prevValue);
          const percentChange =
            prevValue !== 0 ? (change / Math.abs(prevValue)) * 100 : 0;

          // If the change is more than 5%, highlight the field
          if (percentChange > 5) {
            changedFields.push(key);
          }
        }
      });

      setHighlightedFields(changedFields);
    } else {
      setPreviousData(null);
      setHighlightedFields([]);
    }
  }, [currentStep, currentData]);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isPlaying && currentStep < totalSteps - 1) {
      interval = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= totalSteps - 1) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, 500);
    } else if (currentStep >= totalSteps - 1) {
      setIsPlaying(false);
    }
    return () => clearInterval(interval);
  }, [isPlaying, currentStep, totalSteps]);

  useEffect(() => {
    if (currentDecisionRef.current && scrollAreaRef.current) {
      const decisionElement = currentDecisionRef.current;
      const scrollArea = scrollAreaRef.current;
      const viewport = scrollArea.querySelector(
        "[data-radix-scroll-area-viewport]"
      );

      if (viewport) {
        const viewportRect = viewport.getBoundingClientRect();
        const decisionRect = decisionElement.getBoundingClientRect();

        const relativeTop = decisionRect.top - viewportRect.top;
        const viewportHeight = viewportRect.height;
        const decisionHeight = decisionRect.height;

        const targetScroll =
          viewport.scrollTop +
          relativeTop -
          viewportHeight / 2 +
          decisionHeight / 2;

        viewport.scrollTo({
          top: targetScroll,
          behavior: "smooth",
        });
      }
    }
  }, [currentStep]);

  const handlePlayPause = () => {
    if (!isPlaying && currentStep === totalSteps - 1) {
      setCurrentStep(0);
    }
    setIsPlaying(!isPlaying);
  };

  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      setIsPlaying(false);
    }
  };

  const handleNext = () => {
    if (currentStep < totalSteps - 1) {
      setCurrentStep(currentStep + 1);
      setIsPlaying(false);
    }
  };

  const getChange = (field: keyof EnergyDecision) => {
    if (
      !previousData ||
      typeof currentData[field] !== "number" ||
      typeof previousData[field] !== "number"
    ) {
      return null;
    }

    return currentData[field] - previousData[field];
  };

  const formatChange = (
    change: number | null,
    formatFn: (val: number) => string = (val) => val.toFixed(2)
  ) => {
    if (change === null) return null;

    const formattedValue =
      change > 0 ? `+${formatFn(change)}` : formatFn(change);
    const colorClass =
      change > 0
        ? "text-green-500"
        : change < 0
        ? "text-red-500"
        : "text-gray-500";

    return <span className={colorClass}>{formattedValue}</span>;
  };

  const data = energyDecisionData.toSorted((a, b) => {
    return new Date(b.step).getTime() - new Date(a.step).getTime();
  });

  const getDecisionIcon = (action: string) => {
    switch (action) {
      case "BUY":
        return <TrendingDown className="h-5 w-5 text-red-500" />;
      case "SELL":
        return <TrendingUp className="h-5 w-5 text-green-500" />;
      case "STORE":
        return <Battery className="h-5 w-5 text-blue-500" />;
      default:
        return <Zap className="h-5 w-5 text-orange-500" />;
    }
  };

  const getHourFromTimestamp = (timestamp: string) => {
    return timestamp.split(" ")[1];
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
      <Card className="lg:col-span-3 py-4">
        <CardContent className="flex flex-col px-4 gap-4">
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="icon"
              onClick={handlePrevious}
              disabled={currentStep === 0}
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={handlePlayPause}>
              {isPlaying ? (
                <div className="h-4 w-4 flex items-center justify-center gap-1">
                  <div className="h-3 w-0.5 bg-current" />
                  <div className="h-3 w-0.5 bg-current" />
                </div>
              ) : currentStep === totalSteps - 1 ? (
                <RotateCcw className="h-4 w-4" />
              ) : (
                <div className="h-4 w-4 flex items-center justify-center">
                  <div className="w-0 h-0 border-t-[6px] border-t-transparent border-l-[10px] border-l-current border-b-[6px] border-b-transparent ml-0.5" />
                </div>
              )}
            </Button>
            <Button
              variant="outline"
              size="icon"
              onClick={handleNext}
              disabled={currentStep === totalSteps - 1}
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            <div className="ml-auto font-medium flex items-center gap-2">
              <Clock className="h-4 w-4" />
              {getHourFromTimestamp(currentData.step)}
            </div>
          </div>

          <div className="border rounded-lg">
            <ScrollArea className="h-[500px] p-2" ref={scrollAreaRef}>
              <div className="space-y-1 p-1">
                {energyDecisionData.map((decision, index) => (
                  <Button
                    key={index}
                    ref={currentStep === index ? currentDecisionRef : null}
                    variant={currentStep === index ? "default" : "ghost"}
                    className="w-full justify-start text-left h-auto py-2"
                    onClick={() => setCurrentStep(index)}
                  >
                    <div className="flex items-center gap-2">
                      {getDecisionIcon(decision.ai_decision.action)}
                      <div>
                        <div className="font-medium">
                          {getHourFromTimestamp(decision.step)}
                        </div>
                        <div className="text-xs">
                          {decision.ai_decision.action}{" "}
                          {formatEnergy(decision.ai_decision.amount)}
                        </div>
                      </div>
                    </div>
                  </Button>
                ))}
              </div>
            </ScrollArea>
          </div>

          <div className="space-y-3">
            <div>
              <div className="text-sm text-muted-foreground mb-1">
                Token Balance
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <Coins className="h-4 w-4 mr-2 text-yellow-500" />
                  <span className="font-bold">
                    {formatNumber(currentData.token_balance)}
                  </span>
                </div>
                {formatChange(getChange("token_balance"), formatNumber)}
              </div>
            </div>

            <div>
              <div className="text-sm text-muted-foreground mb-2">Storage</div>
              <div className="space-y-2">
                {STORAGE_CONFIG.map((storage) => {
                  return (
                    <div key={storage.id}>
                      <div className="flex justify-between text-xs mb-1">
                        <span>{storage.name}</span>
                        <span>
                          {formatEnergy(
                            currentData[`storage_${storage.id}_level`]
                          )}
                        </span>
                      </div>
                      <Progress
                        value={
                          (currentData[`storage_${storage.id}_level`] /
                            storage.maxCapacity) *
                          100
                        }
                        className="h-2"
                      />
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className=" lg:col-span-9">
        <CardHeader className="mb-2">
          <CardTitle className="flex items-center gap-3">
            {getDecisionIcon(currentData.ai_decision.action)}
            <div>
              <span className="mr-2">Agent Decision:</span>
              <span className="text-orange-500">
                {currentData.ai_decision.action}
              </span>
              {currentData.ai_decision.amount > 0 && (
                <span className="ml-2 text-muted-foreground">
                  ({formatEnergy(currentData.ai_decision.amount)})
                </span>
              )}
            </div>
          </CardTitle>
          <CardDescription>
            {currentData.ai_decision.action === "BUY"
              ? "Purchasing energy from the grid due to consumption needs"
              : currentData.ai_decision.action === "SELL"
              ? "Selling excess energy back to the grid"
              : currentData.ai_decision.action === "STORE"
              ? "Storing excess energy for later use"
              : "Maintaining current energy balance"}
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <MetricCard
              title="Energy Consumption"
              value={formatEnergy(currentData.total_consumption)}
              change={getChange("total_consumption")}
              formatChange={(val) => formatEnergy(val)}
              highlighted={highlightedFields.includes("total_consumption")}
            />
            <MetricCard
              title="Energy Production"
              value={formatEnergy(currentData.total_production)}
              change={getChange("total_production")}
              formatChange={(val) => formatEnergy(val)}
              highlighted={highlightedFields.includes("total_production")}
            />
            <MetricCard
              title="Grid Energy"
              value={formatEnergy(
                currentData.energy_bought_from_grid -
                  currentData.energy_sold_to_grid
              )}
              change={
                getChange("energy_bought_from_grid") !== null &&
                getChange("energy_sold_to_grid") !== null
                  ? (getChange("energy_bought_from_grid") as number) -
                    (getChange("energy_sold_to_grid") as number)
                  : null
              }
              formatChange={(val) => formatEnergy(val)}
              highlighted={
                highlightedFields.includes("energy_bought_from_grid") ||
                highlightedFields.includes("energy_sold_to_grid")
              }
            />
            <MetricCard
              title="Grid Cost"
              value={formatCurrency(currentData.cost_from_grid)}
              change={getChange("cost_from_grid")}
              formatChange={(val) => formatCurrency(val)}
              highlighted={highlightedFields.includes("cost_from_grid")}
            />
            <MetricCard
              title="Tokens Burned"
              value={formatNumber(currentData.tokens_burned_due_to_grid)}
              change={getChange("tokens_burned_due_to_grid")}
              formatChange={(val) => formatNumber(val)}
              highlighted={highlightedFields.includes(
                "tokens_burned_due_to_grid"
              )}
            />
            <MetricCard
              title="Tokens Gained"
              value={formatNumber(currentData.tokens_gained_from_grid)}
              change={getChange("tokens_gained_from_grid")}
              formatChange={(val) => formatNumber(val)}
              highlighted={highlightedFields.includes(
                "tokens_gained_from_grid"
              )}
            />
          </div>

          <div>
            <Card className="p-4">
              <h2 className="text-lg font-medium mb-2">Token Balance</h2>
              <div className="h-[400px]">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={energyDecisionData}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis
                      dataKey="step"
                      tickFormatter={(value) => value.split(" ")[1]}
                      tick={{ fontSize: 12 }}
                    />
                    <YAxis
                      tickFormatter={(value) => formatNumber(value)}
                      tick={{ fontSize: 12 }}
                      domain={getYAxisDomain()}
                    />
                    <Tooltip
                      formatter={(value) => [
                        formatNumber(Number(value)),
                        "Token Balance",
                      ]}
                      labelFormatter={(label) => label.split(" ")[1]}
                    />
                    <Line
                      // key={currentStep}
                      type="monotone"
                      dataKey="token_balance"
                      stroke="#f97316"
                      strokeWidth={2}
                      dot={{ r: 4 }}
                      isAnimationActive={true}
                      animationDuration={750}
                      animationEasing="ease-in-out"
                      data={energyDecisionData.map((item, index) => ({
                        ...item,
                        token_balance:
                          index <= currentStep ? item.token_balance : null,
                      }))}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

interface MetricCardProps {
  title: string;
  value: string;
  change: number | null;
  formatChange: (val: number) => string;
  highlighted: boolean;
}

function MetricCard({
  title,
  value,
  change,
  formatChange,
  highlighted,
}: MetricCardProps) {
  return (
    <div
      className={`p-4 border rounded-lg ${
        highlighted ? "bg-yellow-50 border-yellow-200" : ""
      }`}
    >
      <div className="text-sm text-muted-foreground">{title}</div>
      <div className="flex items-center gap-2">
        <div className="text-xl font-bold">{value}</div>
        {change !== null && (
          <div className="text-sm">
            {change > 0 ? (
              <span className="text-green-500">+{formatChange(change)}</span>
            ) : change < 0 ? (
              <span className="text-red-500">{formatChange(change)}</span>
            ) : (
              <span className="text-gray-500">No change</span>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
