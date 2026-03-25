import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  Users,
  MapPin,
  TrendingUp,
  Clock,
  Calendar,
  CloudRain,
  Sun,
  Car,
  Navigation
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar
} from 'recharts';
import {
  getDashboardStatistics,
  getRiskFactors,
  getRiskyLocations,
  getSeverityAnalysis,
  getTimeTrends
} from '../services/api';
import toast from 'react-hot-toast';
import './Dashboard.css';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [statistics, setStatistics] = useState(null);
  const [riskFactors, setRiskFactors] = useState(null);
  const [riskyLocations, setRiskyLocations] = useState([]);
  const [severityAnalysis, setSeverityAnalysis] = useState(null);
  const [timeTrends, setTimeTrends] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [stats, factors, locations, severity, trends] = await Promise.all([
        getDashboardStatistics(),
        getRiskFactors(),
        getRiskyLocations(10),
        getSeverityAnalysis(),
        getTimeTrends()
      ]);

      setStatistics(stats);
      setRiskFactors(factors);
      setRiskyLocations(locations);
      setSeverityAnalysis(severity);
      setTimeTrends(trends);
      
      toast.success('Dashboard loaded successfully!');
    } catch (error) {
      console.error('Error loading dashboard:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading Dashboard...</p>
      </div>
    );
  }

  const COLORS = {
    fatal: '#ef4444',
    serious: '#f59e0b',
    slight: '#10b981',
    primary: '#6366f1',
    secondary: '#8b5cf6',
    tertiary: '#ec4899'
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1
      }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: { duration: 0.5 }
    }
  };

  return (
    <div className="dashboard">
      <motion.div
        className="dashboard-header"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <div>
          <h1 className="dashboard-title">
            <span className="gradient-text">Analytics Dashboard</span>
          </h1>
          <p className="dashboard-subtitle">
            Comprehensive accident risk analysis and insights
          </p>
        </div>
        <button className="btn btn-primary" onClick={loadDashboardData}>
          <TrendingUp size={18} />
          Refresh Data
        </button>
      </motion.div>

      {/* Statistics Cards */}
      <motion.div
        className="stats-grid"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        <motion.div className="stat-card" variants={itemVariants}>
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
            <AlertTriangle />
          </div>
          <div className="stat-content">
            <p className="stat-label">Total Accidents</p>
            <h3 className="stat-value">{statistics?.total_accidents?.toLocaleString()}</h3>
            <span className="stat-change">All-time data</span>
          </div>
        </motion.div>

        <motion.div className="stat-card" variants={itemVariants}>
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' }}>
            <Users />
          </div>
          <div className="stat-content">
            <p className="stat-label">Total Casualties</p>
            <h3 className="stat-value">{statistics?.total_casualties?.toLocaleString()}</h3>
            <span className="stat-change">Across all incidents</span>
          </div>
        </motion.div>

        <motion.div className="stat-card" variants={itemVariants}>
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' }}>
            <MapPin />
          </div>
          <div className="stat-content">
            <p className="stat-label">High Risk Areas</p>
            <h3 className="stat-value">{statistics?.high_risk_locations?.toLocaleString()}</h3>
            <span className="stat-change">Critical locations</span>
          </div>
        </motion.div>

        <motion.div className="stat-card" variants={itemVariants}>
          <div className="stat-icon" style={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' }}>
            <Car />
          </div>
          <div className="stat-content">
            <p className="stat-label">Avg Vehicles</p>
            <h3 className="stat-value">{statistics?.avg_vehicles_per_accident?.toFixed(2)}</h3>
            <span className="stat-change">Per accident</span>
          </div>
        </motion.div>
      </motion.div>

      {/* Severity Distribution */}
      <motion.div
        className="chart-section"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3, duration: 0.6 }}
      >
        <div className="chart-card">
          <h2 className="chart-title">Severity Distribution</h2>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={[
                  { name: 'Fatal', value: statistics?.severity_distribution?.fatal, color: COLORS.fatal },
                  { name: 'Serious', value: statistics?.severity_distribution?.serious, color: COLORS.serious },
                  { name: 'Slight', value: statistics?.severity_distribution?.slight, color: COLORS.slight }
                ]}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {[
                  { name: 'Fatal', value: statistics?.severity_distribution?.fatal, color: COLORS.fatal },
                  { name: 'Serious', value: statistics?.severity_distribution?.serious, color: COLORS.serious },
                  { name: 'Slight', value: statistics?.severity_distribution?.slight, color: COLORS.slight }
                ].map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h2 className="chart-title">
            <Clock size={20} />
            Most Dangerous Time
          </h2>
          <div className="time-stats">
            <div className="time-stat-item">
              <Clock className="time-icon" />
              <div>
                <p className="time-label">Peak Hour</p>
                <h3 className="time-value">{statistics?.most_dangerous_hour}:00</h3>
              </div>
            </div>
            <div className="time-stat-item">
              <Calendar className="time-icon" />
              <div>
                <p className="time-label">Peak Day</p>
                <h3 className="time-value">{statistics?.most_dangerous_day}</h3>
              </div>
            </div>
          </div>
        </div>
      </motion.div>

      {/* Hourly Distribution */}
      {timeTrends?.hourly && (
        <motion.div
          className="chart-card full-width"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4, duration: 0.6 }}
        >
          <h2 className="chart-title">Accidents by Hour of Day</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={timeTrends.hourly}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis
                dataKey="hour"
                stroke="var(--text-secondary)"
                label={{ value: 'Hour', position: 'insideBottom', offset: -5 }}
              />
              <YAxis stroke="var(--text-secondary)" />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)'
                }}
              />
              <Bar dataKey="accident_count" fill={COLORS.primary} radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      )}

      {/* Daily and Monthly Trends */}
      <div className="chart-row">
        {timeTrends?.daily && (
          <motion.div
            className="chart-card"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            <h2 className="chart-title">Accidents by Day of Week</h2>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={timeTrends.daily}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="day" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                    color: 'var(--text-primary)'
                  }}
                />
                <Bar dataKey="accident_count" fill={COLORS.secondary} radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>
        )}

        {timeTrends?.monthly && (
          <motion.div
            className="chart-card"
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.5, duration: 0.6 }}
          >
            <h2 className="chart-title">Monthly Trend</h2>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={timeTrends.monthly}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                <XAxis dataKey="month" stroke="var(--text-secondary)" />
                <YAxis stroke="var(--text-secondary)" />
                <Tooltip
                  contentStyle={{
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                    color: 'var(--text-primary)'
                  }}
                />
                <Line
                  type="monotone"
                  dataKey="accident_count"
                  stroke={COLORS.tertiary}
                  strokeWidth={3}
                  dot={{ fill: COLORS.tertiary, r: 5 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </motion.div>
        )}
      </div>

      {/* Risk Factors */}
      {riskFactors && (
        <motion.div
          className="chart-card full-width"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6, duration: 0.6 }}
        >
          <h2 className="chart-title">
            <CloudRain size={20} />
            Weather Conditions Impact
          </h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={riskFactors.weather_conditions}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="condition" stroke="var(--text-secondary)" angle={0} textAnchor="end" height={80} />
              <YAxis stroke="var(--text-secondary)" />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border)',
                  borderRadius: '8px',
                  color: 'var(--text-primary)'
                }}
              />
              <Bar dataKey="count" fill="#f59e0b" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </motion.div>
      )}

      {/* Top Risky Locations */}
      <motion.div
        className="chart-card full-width"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.7, duration: 0.6 }}
      >
        <h2 className="chart-title">
          <Navigation size={20} />
          Top 10 Risky Locations
        </h2>
        <div className="locations-table">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Coordinates</th>
                <th>Accidents</th>
                <th>Casualties</th>
                <th>Risk Score</th>
                <th>Level</th>
              </tr>
            </thead>
            <tbody>
              {riskyLocations.map((location) => (
                <tr key={location.rank}>
                  <td>
                    <div className="rank-badge">#{location.rank}</div>
                  </td>
                  <td>
                    <div className="location-coords">
                      <span>{location.lat.toFixed(4)}</span>
                      <span className="coord-separator">|</span>
                      <span>{location.lon.toFixed(4)}</span>
                    </div>
                  </td>
                  <td>
                    <strong>{location.accident_count}</strong>
                  </td>
                  <td>{location.total_casualties}</td>
                  <td>
                    <span className="risk-score">{location.risk_score.toFixed(2)}</span>
                  </td>
                  <td>
                    <span className={`risk-badge ${location.risk_level.toLowerCase()}`}>
                      {location.risk_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </motion.div>
    </div>
  );
};

export default Dashboard;