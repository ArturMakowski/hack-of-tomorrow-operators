"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

const ChartContainer = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn("relative", className)} {...props} />
  },
)
ChartContainer.displayName = "ChartContainer"

const Chart = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(({ className, ...props }, ref) => {
  return <div ref={ref} className={cn("w-full h-full", className)} {...props} />
})
Chart.displayName = "Chart"

const ChartTooltipContent = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn("rounded-md border bg-popover p-4 text-popover-foreground shadow-md", className)}
        {...props}
      />
    )
  },
)
ChartTooltipContent.displayName = "ChartTooltipContent"

const ChartTooltip = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn("space-y-1", className)} {...props} />
  },
)
ChartTooltip.displayName = "ChartTooltip"

const ChartLegend = React.forwardRef<HTMLDivElement, React.HTMLAttributes<HTMLDivElement>>(
  ({ className, ...props }, ref) => {
    return <div ref={ref} className={cn("flex items-center text-sm", className)} {...props} />
  },
)
ChartLegend.displayName = "ChartLegend"

interface ChartLegendItemProps extends React.HTMLAttributes<HTMLDivElement> {
  name: string
  color: string
}

const ChartLegendItem = React.forwardRef<HTMLDivElement, ChartLegendItemProps>(
  ({ className, name, color, ...props }, ref) => {
    return (
      <div ref={ref} className={cn("flex items-center space-x-2", className)} {...props}>
        <span className="block h-4 w-4 rounded-full" style={{ backgroundColor: color }} />
        <span>{name}</span>
      </div>
    )
  },
)
ChartLegendItem.displayName = "ChartLegendItem"

export { Chart, ChartContainer, ChartTooltip, ChartTooltipContent, ChartLegend, ChartLegendItem }

