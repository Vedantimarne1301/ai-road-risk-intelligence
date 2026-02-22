"use client";

import { useState } from "react";
import "./SafetyAI.css";
import { Send } from "lucide-react";

export default function SafetyAI() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!query.trim()) return;

    const userMessage = { type: "user", text: query };
    setMessages((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const response = await fetch("http://localhost:8000/ask-safety-ai", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: query }),
      });

      const data = await response.json();

      const aiMessage = { type: "ai", text: data.answer };
      setMessages((prev) => [...prev, aiMessage]);

    } catch (error) {
      console.error("Error:", error);
      setMessages((prev) => [
        ...prev,
        { type: "ai", text: "Error connecting to AI server." }
      ]);
    }

    setQuery("");
    setLoading(false);
  };

  return (
    <div className="safety-wrapper">
      <div className="chat-card">

        <h1 className="chat-title">AI Safety Assistant</h1>

        <div className="chat-messages">
          {messages.length === 0 && (
            <p className="welcome-text">
              Ask about accident trends, risk zones, speed limits, traffic control...
            </p>
          )}

          {messages.map((msg, index) => (
            <div
              key={index}
              className={`message ${msg.type}`}
            >
              {msg.text}
            </div>
          ))}

          {loading && (
            <div className="message ai">
              Analyzing...
            </div>
          )}
        </div>

        <div className="chat-input">
          <input
            type="text"
            placeholder="Ask safety question..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          />
          <button onClick={handleSubmit}>
            <Send size={16} />
          </button>
        </div>

      </div>
    </div>
  );
}