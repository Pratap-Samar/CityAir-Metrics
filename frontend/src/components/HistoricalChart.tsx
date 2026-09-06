import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { format, parseISO } from "date-fns";

type HistoricalChartProps = {
  title: string;
  data: Record<string, unknown>[];
  dataKey: string;
  color: string;
  unit: string;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
};

export const HistoricalChart = ({
  title,
  data,
  dataKey,
  color,
  unit,
  loading,
  error,
  onRetry
}: HistoricalChartProps) => {
  return (
    <article className="panel chart-panel">
      <div className="panel-header chart-header">
        <h2>{title}</h2>
        <div className="range-controls">
          <button className="range-button active">24H</button>
          <button className="range-button" disabled title="Coming soon">7D</button>
          <button className="range-button" disabled title="Coming soon">30D</button>
        </div>
      </div>

      <div className="chart-container">
        {loading && (
          <div className="chart-overlay">
            <div className="loading-spinner"></div>
            <p>Loading historical data...</p>
          </div>
        )}

        {error && !loading && (
          <div className="chart-overlay error-overlay">
            <p>Unable to load historical data.</p>
            <button onClick={onRetry} className="action-button small">Retry</button>
          </div>
        )}

        {!loading && !error && data.length === 0 && (
          <div className="chart-overlay">
            <p>No historical data available.</p>
          </div>
        )}

        {!loading && !error && data.length > 0 && (
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--chart-grid)" />
              <XAxis 
                dataKey="observed_at" 
                tickFormatter={(val: unknown) => val ? format(parseISO(String(val)), "HH:mm") : ""}
                stroke="var(--muted-text)"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                minTickGap={30}
              />
              <YAxis 
                stroke="var(--muted-text)"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(val) => `${val}`}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "var(--panel-bg)", 
                  borderColor: "var(--border-color)",
                  color: "var(--foreground)",
                  borderRadius: "8px",
                  boxShadow: "var(--shadow)"
                }}
                itemStyle={{ color: color, fontWeight: 600 }}
                labelFormatter={(val: unknown) => val ? format(parseISO(String(val)), "MMM d, HH:mm") : ""}
                formatter={(val: unknown) => [`${val} ${unit}`, title]}
              />
              <Line 
                type="monotone" 
                dataKey={dataKey} 
                stroke={color} 
                strokeWidth={3} 
                dot={false}
                activeDot={{ r: 6 }} 
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </article>
  );
};
