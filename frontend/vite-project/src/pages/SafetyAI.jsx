"use client";
import { useState, useRef, useEffect } from "react";
import "./SafetyAI.css";
import { MessageSquare, Send, Clock, BarChart2, MapPin, PieChart, TrendingUp, Download } from "lucide-react";
import { BarChart, Bar, LineChart, Line, PieChart as RechartsPie, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const COLORS = ['#ef4444', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899'];

export default function SafetyAI() {
  const [query, setQuery] = useState("");
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const chatEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history]);

  const handleSubmit = async () => {
    if (!query.trim() || isLoading) return;

    // Add user query to history
    const userMessage = { type: "user", text: query, timestamp: new Date() };
    setHistory((prev) => [...prev, userMessage]);
    
    const currentQuery = query;
    setQuery("");
    setIsLoading(true);

    try {
      const res = await fetch("http://localhost:8000/safety_ai/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: currentQuery }),
      });
      const data = await res.json();

      // Add AI response with visualization
      const aiMessage = {
        type: "ai",
        text: data.response,
        data: data.data,
        visualization: data.visualization,
        intent: data.intent,
        timestamp: new Date()
      };
      
      setHistory((prev) => [...prev, aiMessage]);
    } catch (err) {
      console.error("Error fetching AI response:", err);
      setHistory((prev) => [
        ...prev,
        { 
          type: "ai", 
          text: "Sorry, I couldn't process your request. Please make sure the backend server is running.",
          timestamp: new Date()
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const renderVisualization = (viz) => {
    if (!viz || !viz.data) return null;

    switch (viz.type) {
      case "bar":
        return (
          <div className="viz-container">
            <h4>{viz.data.title}</h4>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={viz.data.labels.map((label, idx) => ({
                name: label,
                value: viz.data.values[idx]
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="value" fill="#3b82f6" name={viz.data.yLabel || "Count"} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        );

      case "pie":
        return (
          <div className="viz-container">
            <h4>{viz.data.title}</h4>
            <ResponsiveContainer width="100%" height={300}>
              <RechartsPie>
                <Pie
                  data={viz.data.labels.map((label, idx) => ({
                    name: label,
                    value: viz.data.values[idx]
                  }))}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {viz.data.labels.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </RechartsPie>
            </ResponsiveContainer>
          </div>
        );

      case "line":
        return (
          <div className="viz-container">
            <h4>{viz.data.title}</h4>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={viz.data.labels.map((label, idx) => ({
                name: label,
                value: viz.data.values[idx]
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="value" stroke="#10b981" strokeWidth={2} name={viz.data.yLabel || "Count"} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        );

      case "map":
        return (
          <div className="viz-container">
            <h4>{viz.data.title}</h4>
            <div className="map-locations">
              {viz.data.locations.slice(0, 5).map((loc, idx) => (
                <div key={idx} className="location-item">
                  <MapPin size={16} />
                  <span>
                    Location {idx + 1}: {loc.accident_count} accidents (Risk: {loc.risk_score.toFixed(2)})
                  </span>
                </div>
              ))}
            </div>
          </div>
        );

      case "table":
        return (
          <div className="viz-container">
            <h4>Data Summary</h4>
            <pre className="data-table">{JSON.stringify(viz.data, null, 2)}</pre>
          </div>
        );

      default:
        return null;
    }
  };

  const suggestedQueries = [
    "How many fatal accidents occurred?",
    "What time of day has most accidents?",
    "Show me the most dangerous locations",
    "How does weather affect accidents?",
    "Which speed limits have most accidents?",
    "What are monthly accident trends?"
  ];

  return (
    <div className="safety-wrapper">
      <div className="chat-container">
        <div className="chat-header">
          <h1>
            <MessageSquare className="header-icon" />
            Ask Safety AI
          </h1>
          <p>Natural language queries for road safety intelligence with interactive visualizations</p>
        </div>

        <div className="chat-card">
          {history.length === 0 && (
            <div className="chat-welcome">
              <div className="welcome-icon">
                <BarChart2 size={60} />
              </div>
              <h2>Welcome to Safety AI</h2>
              <p>
                Ask questions about accident patterns, risk factors, and safety trends.
                I'll analyze the data and provide actionable insights with visualizations.
              </p>
              
              <div className="suggested-queries">
                <h3>Try asking:</h3>
                <div className="query-chips">
                  {suggestedQueries.map((q, idx) => (
                    <button
                      key={idx}
                      className="query-chip"
                      onClick={() => setQuery(q)}
                    >
                      {q}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Chat history */}
          <div className="chat-history">
            {history.map((item, index) => (
              <div
                key={index}
                className={`chat-message ${item.type}`}
              >
                <div className="message-header">
                  <span className="message-sender">
                    {item.type === "user" ? "You" : "Safety AI"}
                  </span>
                  <span className="message-time">
                    {item.timestamp?.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                
                <div className="message-content">
                  {item.text}
                </div>

                {item.visualization && (
                  <div className="message-visualization">
                    {renderVisualization(item.visualization)}
                  </div>
                )}

                {item.intent && (
                  <div className="message-intent">
                    Intent: <span className="intent-badge">{item.intent}</span>
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="chat-message ai loading">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                  Analyzing your query...
                </div>
              </div>
            )}
            
            <div ref={chatEndRef} />
          </div>

          <div className="chat-input-section">
            <input
              type="text"
              placeholder="Ask about accident trends, risk factors, locations..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
              disabled={isLoading}
            />
            <button onClick={handleSubmit} disabled={isLoading || !query.trim()}>
              <Send size={16} /> Send
            </button>
          </div>
        </div>
      </div>

      <div className="history-panel">
        <h3>
          <Clock size={18} /> Chat History
        </h3>
        {history.length === 0 ? (
          <p className="no-history">No queries yet. Start by asking a question!</p>
        ) : (
          <div className="history-list">
            {history.filter(h => h.type === "user").map((item, idx) => (
              <div key={idx} className="history-item" onClick={() => setQuery(item.text)}>
                <span className="history-icon">💬</span>
                <span className="history-text">{item.text.substring(0, 50)}...</span>
              </div>
            ))}
          </div>
        )}
        
        {history.length > 0 && (
          <button 
            className="clear-history-btn"
            onClick={() => setHistory([])}
          >
            Clear History
          </button>
        )}
      </div>
    </div>
  );
}