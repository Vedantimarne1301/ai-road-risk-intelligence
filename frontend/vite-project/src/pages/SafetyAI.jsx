"use client";
import { useState } from "react";
import "./SafetyAI.css";
import { MessageSquare, Send, Clock } from "lucide-react";

export default function SafetyAI() {
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState([]);

  const handleSubmit = () => {
    if (!query.trim()) return;

    setHistory([...history, query]);
    setQuery("");
  };

  return (
    <div className="safety-wrapper">

      {/* Main Chat Section */}
      <div className="chat-container">
        <div className="chat-header">
          <h1>Ask Safety AI</h1>
          <p>Natural language queries for road safety intelligence</p>
        </div>

        <div className="chat-card">
          <div className="chat-welcome">
            <MessageSquare size={40} />
            <h2>Welcome to Safety AI</h2>
            <p>
              Ask questions about accident patterns, risk factors, and safety trends.
              I'll analyze the data and provide actionable insights.
            </p>
          </div>

          <div className="chat-input-section">
            <input
              type="text"
              placeholder="Ask about accident trends, risk factors..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button onClick={handleSubmit}>
              <Send size={16} /> Send
            </button>
          </div>
        </div>
      </div>

      {/* History Panel */}
      <div className="history-panel">
        <h3><Clock size={18} /> Query History</h3>
        {history.length === 0 ? (
          <p className="no-history">No queries yet</p>
        ) : (
          history.map((item, index) => (
            <div key={index} className="history-item">
              {item}
            </div>
          ))
        )}
      </div>

    </div>
  );
}