import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Activity, BarChart3, Map } from 'lucide-react';
import './Navbar.css';

const Navbar = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: BarChart3, label: 'Dashboard' },
    { path: '/map', icon: Map, label: 'Risk Map' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <Activity className="brand-icon" />
          <span className="brand-text">
            <span className="gradient-text">AI Road Risk</span> Intelligence
          </span>
        </Link>

        <div className="navbar-links">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-link ${isActive ? 'active' : ''}`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>

        <div className="navbar-status">
          <div className="status-indicator"></div>
          <span className="status-text">System Active</span>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;