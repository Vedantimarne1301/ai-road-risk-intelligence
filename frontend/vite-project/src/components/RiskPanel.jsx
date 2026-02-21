import React from "react";
import Explanation from "./ExpalanationCard";
import Recommendation from "./RecommendationList";

const RiskPanel = ({ data }) => {
  if (!data) {
    return (
      <div className="p-6">
        <h2 className="text-xl font-semibold mb-2">
          AI Road Risk Analysis
        </h2>
        <p className="text-gray-500">
          Select a location on the map to see prediction.
        </p>
      </div>
    );
  }

  const { risk_level, risk_score, explanation, recommendation } = data;

  const getColor = () => {
    if (risk_level === "High") return "bg-red-500";
    if (risk_level === "Medium") return "bg-yellow-500";
    return "bg-green-500";
  };

  return (
    <div className="p-6 space-y-6">

      <h2 className="text-xl font-semibold">
        AI Road Risk Analysis
      </h2>

      {/* Risk Summary */}
      <div className={`${getColor()} text-white p-4 rounded-xl shadow`}>
        <h3 className="text-lg font-bold">
          Risk Level: {risk_level}
        </h3>
        <p>
          Confidence: {(risk_score * 100).toFixed(2)}%
        </p>
      </div>

      <Explanation explanation={explanation} />
      <Recommendation recommendation={recommendation} />

    </div>
  );
};

export default RiskPanel;
