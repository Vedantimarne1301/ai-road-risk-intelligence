import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, CircleMarker } from 'react-leaflet';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MapPin,
  AlertTriangle,
  Lightbulb,
  X,
  Loader,
  Filter,
  Layers,
  Maximize2,
  Minimize2
} from 'lucide-react';
import L from 'leaflet';
import { getClusteredHeatmap, predictLocationRisk } from '../services/api';
import toast from 'react-hot-toast';
import './MapView.css';

// Fix Leaflet icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const MapClickHandler = ({ onMapClick }) => {
  useMapEvents({
    click: (e) => {
      onMapClick(e.latlng);
    },
  });
  return null;
};

const MapView = () => {
  const [heatmapData, setHeatmapData] = useState([]);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [mapLoading, setMapLoading] = useState(true);
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [filterSeverity, setFilterSeverity] = useState('all');
  const [expandedView, setExpandedView] = useState(false); // NEW: Toggle for expanded view

  // Center of India
  const center = [20.5937, 78.9629];

  useEffect(() => {
    loadHeatmapData();
  }, []);

  const loadHeatmapData = async () => {
    setMapLoading(true);
    try {
      const data = await getClusteredHeatmap(0.1);
      setHeatmapData(data);
      toast.success('Heatmap loaded successfully!');
    } catch (error) {
      console.error('Error loading heatmap:', error);
      toast.error('Failed to load heatmap data');
    } finally {
      setMapLoading(false);
    }
  };

  const handleMapClick = async (latlng) => {
    setSelectedLocation(latlng);
    setLoading(true);
    setPrediction(null);
    setExpandedView(true); // Automatically expand when prediction loads

    try {
      const result = await predictLocationRisk(latlng.lat, latlng.lng);
      setPrediction(result);
      toast.success('Risk prediction completed!');
    } catch (error) {
      console.error('Error predicting risk:', error);
      toast.error('Failed to predict risk for this location');
      setExpandedView(false);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (riskLevel) => {
    const colors = {
      Low: '#10b981',
      Medium: '#f59e0b',
      High: '#ef4444'
    };
    return colors[riskLevel] || '#6366f1';
  };

  const getHeatmapColor = (intensity) => {
    if (intensity > 0.7) return '#ef4444';
    if (intensity > 0.4) return '#f59e0b';
    return '#10b981';
  };

  const filteredHeatmapData = heatmapData.filter(point => {
    if (filterSeverity === 'all') return true;
    if (filterSeverity === 'high') return point.intensity > 0.7;
    if (filterSeverity === 'medium') return point.intensity > 0.4 && point.intensity <= 0.7;
    if (filterSeverity === 'low') return point.intensity <= 0.4;
    return true;
  });

  return (
    <div className="map-view">
      {/* Sidebar - Collapsed Controls */}
      <motion.div
        className={`map-sidebar ${expandedView ? 'collapsed' : ''}`}
        initial={{ x: -300 }}
        animate={{ x: 0 }}
        transition={{ duration: 0.5 }}
      >
        <div className="sidebar-header">
          <h2 className="sidebar-title">
            <MapPin className="title-icon" />
            <span className="gradient-text">Risk Map</span>
          </h2>
          <p className="sidebar-subtitle">Click anywhere on the map to analyze risk</p>
        </div>

        {/* Controls */}
        {!expandedView && (
          <div className="map-controls">
            <div className="control-group">
              <div className="control-header">
                <Layers size={18} />
                <span>Map Layers</span>
              </div>
              <label className="control-checkbox">
                <input
                  type="checkbox"
                  checked={showHeatmap}
                  onChange={(e) => setShowHeatmap(e.target.checked)}
                />
                <span>Show Accident Heatmap</span>
              </label>
            </div>

            <div className="control-group">
              <div className="control-header">
                <Filter size={18} />
                <span>Filter by Risk</span>
              </div>
              <div className="filter-buttons">
                <button
                  className={`filter-btn ${filterSeverity === 'all' ? 'active' : ''}`}
                  onClick={() => setFilterSeverity('all')}
                >
                  All
                </button>
                <button
                  className={`filter-btn high ${filterSeverity === 'high' ? 'active' : ''}`}
                  onClick={() => setFilterSeverity('high')}
                >
                  High
                </button>
                <button
                  className={`filter-btn medium ${filterSeverity === 'medium' ? 'active' : ''}`}
                  onClick={() => setFilterSeverity('medium')}
                >
                  Medium
                </button>
                <button
                  className={`filter-btn low ${filterSeverity === 'low' ? 'active' : ''}`}
                  onClick={() => setFilterSeverity('low')}
                >
                  Low
                </button>
              </div>
            </div>

            <div className="legend">
              <h3 className="legend-title">Risk Levels</h3>
              <div className="legend-items">
                <div className="legend-item">
                  <div className="legend-color" style={{ background: '#ef4444' }}></div>
                  <span>High Risk</span>
                </div>
                <div className="legend-item">
                  <div className="legend-color" style={{ background: '#f59e0b' }}></div>
                  <span>Medium Risk</span>
                </div>
                <div className="legend-item">
                  <div className="legend-color" style={{ background: '#10b981' }}></div>
                  <span>Low Risk</span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Loading State */}
        <AnimatePresence>
          {loading && (
            <motion.div
              className="prediction-loading"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <Loader className="spinning" size={48} />
              <p>Analyzing location risk...</p>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* EXPANDED RISK ANALYSIS PANEL - THIS IS THE KEY CHANGE */}
      <AnimatePresence>
        {prediction && !loading && expandedView && (
          <motion.div
            className="risk-analysis-expanded"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.4 }}
          >
            <div className="expanded-container">
              {/* Header */}
              <div className="expanded-header">
                <div className="header-content">
                  <AlertTriangle size={32} style={{ color: getRiskColor(prediction.risk_level) }} />
                  <div>
                    <h2 className="expanded-title">Risk Analysis Report</h2>
                    <p className="expanded-subtitle">
                      <MapPin size={16} />
                      {selectedLocation.lat.toFixed(4)}, {selectedLocation.lng.toFixed(4)}
                    </p>
                  </div>
                </div>
                <div className="header-actions">
                  <button 
                    className="action-btn"
                    onClick={() => setExpandedView(false)}
                    title="Minimize"
                  >
                    <Minimize2 size={20} />
                  </button>
                  <button 
                    className="action-btn close"
                    onClick={() => {
                      setPrediction(null);
                      setExpandedView(false);
                    }}
                  >
                    <X size={20} />
                  </button>
                </div>
              </div>

              {/* Main Content Grid */}
              <div className="expanded-content">
                {/* Risk Level - Hero Section */}
                <div 
                  className="risk-hero-card"
                  style={{ 
                    borderColor: getRiskColor(prediction.risk_level),
                    background: `linear-gradient(135deg, ${getRiskColor(prediction.risk_level)}15 0%, ${getRiskColor(prediction.risk_level)}05 100%)`
                  }}
                >
                  <div className="risk-hero-icon" style={{ borderColor: getRiskColor(prediction.risk_level) }}>
                    <AlertTriangle size={80} style={{ color: getRiskColor(prediction.risk_level) }} />
                  </div>
                  <div className="risk-hero-content">
                    <p className="risk-hero-label">RISK LEVEL</p>
                    <h1 
                      className="risk-hero-value" 
                      style={{ color: getRiskColor(prediction.risk_level) }}
                    >
                      {prediction.risk_level}
                    </h1>
                    <p className="risk-hero-confidence">
                      Confidence Score: <strong>{(prediction.risk_score * 100).toFixed(1)}%</strong>
                    </p>
                  </div>
                </div>

                {/* Explanation Section */}
                {prediction.explanation && (
                  <div className="expanded-section explanation-section">
                    <div className="section-header">
                      <AlertTriangle size={24} />
                      <h3>Risk Explanation</h3>
                    </div>
                    <p className="explanation-content">
                      {prediction.explanation.risk_summary}
                    </p>
                    
                    {prediction.explanation.primary_drivers && (
                      <div className="risk-drivers">
                        <h4>Primary Risk Factors</h4>
                        <div className="drivers-grid">
                          {prediction.explanation.primary_drivers.map((factor, idx) => (
                            <div key={idx} className="driver-card">
                              <div className="driver-number">{idx + 1}</div>
                              <p className="driver-text">{factor.replace(/_/g, ' ')}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {/* Recommendations Section */}
                {prediction.recommendation && (
                  <div className="expanded-section recommendations-section">
                    <div className="section-header">
                      <Lightbulb size={24} />
                      <h3>Safety Recommendations</h3>
                    </div>
                    <div className="recommendations-grid">
                      {prediction.recommendation.recommended_actions.map((action, idx) => (
                        <div key={idx} className="recommendation-card">
                          <div className="rec-number">{idx + 1}</div>
                          <p className="rec-text">{action}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Map Container */}
      <div className={`map-container-wrapper ${expandedView ? 'dimmed' : ''}`}>
        {mapLoading && (
          <div className="map-loading-overlay">
            <div className="spinner"></div>
            <p>Loading map data...</p>
          </div>
        )}

        <MapContainer
          center={center}
          zoom={5}
          className="map-container"
          style={{ height: '100%', width: '100%' }}
        >
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
          />

          <MapClickHandler onMapClick={handleMapClick} />

          {/* Heatmap Markers */}
          {showHeatmap && filteredHeatmapData.map((point, idx) => (
            <CircleMarker
              key={idx}
              center={[point.lat, point.lon]}
              radius={Math.max(5, point.intensity * 15)}
              fillColor={getHeatmapColor(point.intensity)}
              color={getHeatmapColor(point.intensity)}
              fillOpacity={0.6}
              opacity={0.8}
              weight={1}
            >
              <Popup>
                <div className="custom-popup">
                  <h4>Accident Cluster</h4>
                  <p><strong>Accidents:</strong> {point.accident_count}</p>
                  <p><strong>Casualties:</strong> {point.total_casualties}</p>
                  <p><strong>Risk:</strong> {point.severity_label}</p>
                </div>
              </Popup>
            </CircleMarker>
          ))}

          {/* Selected Location Marker */}
          {selectedLocation && (
            <Marker position={[selectedLocation.lat, selectedLocation.lng]}>
              <Popup>
                <div className="custom-popup">
                  <h4>Selected Location</h4>
                  <p>Analyzing risk...</p>
                </div>
              </Popup>
            </Marker>
          )}
        </MapContainer>
      </div>
    </div>
  );
};

export default MapView;