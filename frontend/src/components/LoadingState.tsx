export const LoadingState = () => {
  return (
    <div className="loading-state">
      <div className="skeleton-header">
        <div className="skeleton-title"></div>
        <div className="skeleton-subtitle"></div>
      </div>
      <div className="metrics-grid">
        <div className="metric-card skeleton-card"></div>
        <div className="metric-card skeleton-card"></div>
        <div className="metric-card skeleton-card"></div>
      </div>
    </div>
  );
};
