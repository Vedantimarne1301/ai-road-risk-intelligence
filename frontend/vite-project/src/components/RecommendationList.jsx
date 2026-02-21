import React from "react";

const Recommendation = ({ recommendation }) => {
  if (!recommendation) return null;

  const { recommended_actions } = recommendation;

  return (
    <div style={cardStyle}>
      <h3>Safety Recommendations</h3>

      <ul>
        {recommended_actions &&
          recommended_actions.map((action, index) => (
            <li key={index} style={{ marginBottom: "8px" }}>
              {action}
            </li>
          ))}
      </ul>
    </div>
  );
};

const cardStyle = {
  background: "white",
  padding: "15px",
  borderRadius: "10px",
  marginBottom: "20px",
  boxShadow: "0 2px 8px rgba(0,0,0,0.05)"
};

export default Recommendation;
