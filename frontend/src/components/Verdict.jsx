import React from 'react';
import Tilt from 'react-parallax-tilt';
import './Verdict.css';

const Verdict = ({ score }) => {
  if (score === null) return null;

  const isMalicious = score >= 80;
  const isWarning = score >= 40 && score < 80;
  
  let label = 'SECURE';
  let colorClass = 'safe';
  let glassClass = 'cyan';

  if (isMalicious) {
    label = 'MALICIOUS THREAT';
    colorClass = 'malicious';
    glassClass = 'red';
  } else if (isWarning) {
    label = 'SUSPICIOUS';
    colorClass = 'warning';
    glassClass = 'violet';
  }

  return (
    <section className="verdict-container">
      <Tilt
        tiltMaxAngleX={10} 
        tiltMaxAngleY={10} 
        perspective={1000} 
        transitionSpeed={2000}
        scale={1.05}
        gyroscope={true}
      >
        <div className={`verdict-card aero-glass ${glassClass} ${isMalicious ? 'animate-pulse' : ''}`}>
          <div className="verdict-label" style={{ color: `var(--glow-${glassClass})` }}>
            {label}
          </div>
          
          <div 
            className={`score-hologram score-${colorClass}`} 
            data-score={score}
          >
            {score}
          </div>

          <p className="font-mono text-sm opacity-60">Risk Index Output</p>
          
          <button 
            className="action-btn"
            onClick={() => document.getElementById('logs')?.scrollIntoView({ behavior: 'smooth' })}
          >
            View Full Report
          </button>
        </div>
      </Tilt>
    </section>
  );
};

export default Verdict;
