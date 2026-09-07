// Temporary mock adapter for missing dashboard endpoints
import type { TimeSeriesTrend } from "../types";

export const getMockIndiaAqiTrend = (period: "24H" | "7D" | "30D" = "24H"): TimeSeriesTrend[] => {
  const data: TimeSeriesTrend[] = [];
  const now = new Date();
  const count = period === "24H" ? 24 : period === "7D" ? 7 : 30;
  const stepMs = period === "24H" ? 60 * 60 * 1000 : 24 * 60 * 60 * 1000;
  
  for (let i = count; i >= 0; i--) {
    const d = new Date(now.getTime() - i * stepMs);
    data.push({
      timestamp: d.toISOString(),
      value: 110 + Math.sin(i * 0.5) * 20 + Math.random() * 10,
      observation_count: 28,
    });
  }
  return data;
};

export const getMockIndiaTempTrend = (period: "24H" | "7D" | "30D" = "24H"): TimeSeriesTrend[] => {
  const data: TimeSeriesTrend[] = [];
  const now = new Date();
  const count = period === "24H" ? 24 : period === "7D" ? 7 : 30;
  const stepMs = period === "24H" ? 60 * 60 * 1000 : 24 * 60 * 60 * 1000;
  
  for (let i = count; i >= 0; i--) {
    const d = new Date(now.getTime() - i * stepMs);
    const hour = d.getHours();
    const temp = 25 + Math.sin(((hour - 6) / 24) * Math.PI * 2) * 8 + Math.random() * 2;
    data.push({
      timestamp: d.toISOString(),
      value: period === "24H" ? temp : 28 + Math.sin(i * 0.2) * 5 + Math.random() * 3,
      observation_count: 28,
    });
  }
  return data;
};

export type PipelineRunMock = {
  id: number;
  time: string;
  type: string;
  status: "Success" | "Failed" | "Running";
};

export const getMockRecentPipelineRuns = (): PipelineRunMock[] => {
  const now = new Date();
  return [
    { id: 1, time: new Date(now.getTime() - 10 * 60000).toISOString(), type: "Air Quality", status: "Success" },
    { id: 2, time: new Date(now.getTime() - 20 * 60000).toISOString(), type: "Weather", status: "Success" },
    { id: 3, time: new Date(now.getTime() - 30 * 60000).toISOString(), type: "Air Quality", status: "Success" },
    { id: 4, time: new Date(now.getTime() - 40 * 60000).toISOString(), type: "Weather", status: "Success" },
  ];
};
