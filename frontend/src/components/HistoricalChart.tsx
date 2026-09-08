import React from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { TimeSeriesTrend } from "../types";

type HistoricalChartProps = {
  data: TimeSeriesTrend[];
  dataKey: string;
  color: string;
  unit: string;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
};

export const HistoricalChart: React.FC<HistoricalChartProps> = ({
  data,
  dataKey,
  color,
  unit,
  loading,
  error,
  onRetry,
}) => {
  if (loading) {
    return (
      <div className="chart-loading-overlay">
        <p>Loading...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chart-error-overlay">
        <p>Error: {error}</p>
        <button onClick={onRetry} className="chart-retry-btn">
          Retry
        </button>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="chart-empty-overlay">
        <p>No data available</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height="100%">
      <AreaChart
        data={data}
        margin={{ top: 10, right: 0, left: -20, bottom: 0 }}
      >
        <CartesianGrid
          strokeDasharray="3 3"
          vertical={false}
          stroke="var(--border-color)"
        />
        <XAxis
          dataKey="timestamp"
          tickFormatter={(time) => {
            const date = new Date(time);
            return date.toLocaleDateString("en-US", {
              month: "short",
              day: "numeric",
            });
          }}
          stroke="#9ca3af"
          fontSize={10}
          tickLine={false}
          axisLine={false}
          dy={10}
        />
        <YAxis
          stroke="#9ca3af"
          fontSize={10}
          tickLine={false}
          axisLine={false}
          dx={-10}
        />
        <Tooltip
          // @ts-expect-error Recharts internal typing mismatch
          formatter={(value: number) => [`${Math.round(value)} ${unit}`, ""]}
          // @ts-expect-error Recharts internal typing mismatch
          labelFormatter={(label: string | number | Date) =>
            new Date(label).toLocaleString()
          }
          contentStyle={{
            backgroundColor: "#1f2937",
            border: "none",
            borderRadius: "6px",
            color: "#fff",
            fontSize: "0.8rem",
          }}
          itemStyle={{ color: "#fff" }}
        />
        <Area
          type="monotone"
          dataKey={dataKey}
          stroke={color}
          strokeWidth={2}
          fill={color}
          fillOpacity={0.15}
          activeDot={{ r: 4, fill: color, stroke: "var(--panel-bg)" }}
        />
      </AreaChart>
    </ResponsiveContainer>
  );
};
