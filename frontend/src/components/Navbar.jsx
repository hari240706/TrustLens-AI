import React from 'react';
import { Shield } from 'lucide-react';
import '../App.css';

const Navbar = () => {
  return (
    <div className="navbar-container">
      <nav className="navbar-pill aero-glass animate-bob">
        <div className="brand">
          <Shield size={24} className="text-white" />
          <span>TrustLens</span>
        </div>
        <a href="#dashboard" className="nav-link">Dashboard</a>
        <a href="#agents" className="nav-link">Agents</a>
        <a href="#network" className="nav-link">Capabilities</a>
        <a href="#verdict" className="nav-link">Verdict</a>
      </nav>
    </div>
  );
};

export default Navbar;
