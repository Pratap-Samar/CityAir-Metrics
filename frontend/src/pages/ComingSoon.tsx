import React from "react";

type ComingSoonProps = {
  title: string;
};

export const ComingSoon: React.FC<ComingSoonProps> = ({ title }) => {
  return (
    <div className="coming-soon">
      <h2>{title}</h2>
      <p>This feature is not yet available in the current phase.</p>
    </div>
  );
};
