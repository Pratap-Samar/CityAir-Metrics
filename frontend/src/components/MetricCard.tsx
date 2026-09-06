import React from "react";

type MetricCardProps = {
  title: string;
  value: React.ReactNode;
  subtitle: string;
  icon?: React.ReactNode;
};

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
}) => {
  return (
    <article className="metric-card">
      <div className="metric-header">
        <p className="metric-title">{title}</p>
        {icon && <span className="metric-icon">{icon}</span>}
      </div>
      <strong className="metric-value">{value}</strong>
      <span className="metric-subtitle">{subtitle}</span>
    </article>
  );
};
