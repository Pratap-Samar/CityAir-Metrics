import React, { useEffect, useState } from "react";
import type { PipelineStatus } from "../types";

const API_URL = "http://localhost:8000";

export const PipelineStatusIndicator: React.FC = () => {
  const [status, setStatus] = useState<PipelineStatus | null>(null);
  const [isOffline, setIsOffline] = useState(false);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_URL}/pipeline/status`);
        if (!response.ok) {
          setIsOffline(true);
          return;
        }
        const data = await response.json();
        setStatus(data);
        setIsOffline(false);
      } catch {
        setIsOffline(true);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  let label = "Checking status...";
  let indicatorClass = "status-indicator-gray";

  if (isOffline) {
    label = "Pipeline offline";
    indicatorClass = "status-indicator-red";
  } else if (status) {
    if (status.is_active) {
      label = "Pipeline active";
      indicatorClass = "status-indicator-green";
    } else {
      label = "Pipeline idle";
      indicatorClass = "status-indicator-gray";
    }
  }

  return (
    <div className="pipeline-status">
      <div className={`status-dot ${indicatorClass}`} />
      <span>{label}</span>
    </div>
  );
};
