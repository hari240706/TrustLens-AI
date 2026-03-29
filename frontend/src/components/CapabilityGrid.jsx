import React from 'react';
import { Globe, Search, Lock, BrainCircuit } from 'lucide-react';
import './CapabilityGrid.css';

const capabilities = [
  {
    id: 1,
    title: 'URL Analysis',
    desc: 'Deep packet inspection of destination URLs, evaluating query string anomalies and known malicious signatures.',
    icon: Globe,
    color: 'cyan'
  },
  {
    id: 2,
    title: 'Domain Intel',
    desc: 'Cross-referencing WHOIS data, registration age, and DNS records against global threat intelligence feeds.',
    icon: Search,
    color: 'violet'
  },
  {
    id: 3,
    title: 'SSL Verification',
    desc: 'Cryptographic validation of certificate chains, issuer trust, and detection of self-signed or revoked certs.',
    icon: Lock,
    color: 'cyan'
  },
  {
    id: 4,
    title: 'Intent Engine',
    desc: 'Heuristic modeling to predict the likely goal of the target site (Phishing, Malware Drop, C2 Beacon).',
    icon: BrainCircuit,
    color: 'violet'
  }
];

const CapabilityGrid = () => {
  return (
    <section className="capability-grid-section">
      <div className="capability-grid">
        {capabilities.map((cap) => {
          const Icon = cap.icon;
          const glassClass = cap.color === 'violet' ? 'violet' : '';
          return (
            <div key={cap.id} className={`capability-card aero-glass ${glassClass}`}>
              <div className="card-icon">
                <Icon size={20} className="text-white" />
              </div>
              <h3 className="card-title">{cap.title}</h3>
              <p className="card-desc">{cap.desc}</p>
            </div>
          );
        })}
      </div>
    </section>
  );
};

export default CapabilityGrid;
