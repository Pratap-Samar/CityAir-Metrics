import React from "react";
import { AlertCircle, RefreshCw } from "lucide-react";

type ErrorStateProps = {
  message: string;
  onRetry: () => void;
};

export const ErrorState: React.FC<ErrorStateProps> = ({ message, onRetry }) => {
  return (
    <div className="error-state">
      <AlertCircle size={48} className="error-icon" />
      <h2>Data could not be loaded</h2>
      <p>{message}</p>
      <button onClick={onRetry} className="action-button">
        <RefreshCw size={20} />
        <span>Try again</span>
      </button>
    </div>
  );
};
