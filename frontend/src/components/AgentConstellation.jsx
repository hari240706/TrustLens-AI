import React from 'react';
import { motion } from 'framer-motion';
import Tilt from 'react-parallax-tilt';
import { BrainCircuit, Globe, Lock, ShieldCheck, Code, Network, Search, Zap } from 'lucide-react';
import './AgentConstellation.css';

const agents = [
  { id: 1, name: 'URL Analysis', icon: Globe, angle: 0 },
  { id: 2, name: 'Domain Intel', icon: Search, angle: 60 },
  { id: 3, name: 'SSL Check', icon: Lock, angle: 120 },
  { id: 4, name: 'Intent Engine', icon: BrainCircuit, angle: 180 },
  { id: 5, name: 'Code Inspector', icon: Code, angle: 240 },
  { id: 6, name: 'Network Tracer', icon: Network, angle: 300 },
];

const AgentConstellation = ({ isScanning }) => {
  const radius = 200; // Orbit radius
  const center = 250; // Center coordinate of the 500x500 container

  return (
    <section className="constellation-wrapper">
      <Tilt 
        tiltMaxAngleX={15} 
        tiltMaxAngleY={15} 
        perspective={1000} 
        transitionSpeed={2000}
        scale={1.02}
        gyroscope={true}
        className="tilt-wrapper"
      >
        <div className="constellation-container">
          
          {/* Filaments connection */}
          <svg className="filaments-svg">
            {agents.map((agent) => {
              const rad = (agent.angle * Math.PI) / 180;
              const x = center + radius * Math.cos(rad);
              const y = center + radius * Math.sin(rad);
              return (
                <g key={`line-${agent.id}`}>
                  <line 
                    x1={center} y1={center} 
                    x2={x} y2={y} 
                    className="filament-line"
                  />
                  {isScanning && (
                    <motion.line
                      x1={center} y1={center}
                      x2={x} y2={y}
                      className="filament-pulse"
                      initial={{ pathLength: 0, opacity: 0 }}
                      animate={{ pathLength: 1, opacity: [0, 1, 0] }}
                      transition={{ 
                        duration: 1.5, 
                        repeat: Infinity, 
                        ease: "easeInOut",
                        delay: agent.id * 0.2 // Stagger pulses
                      }}
                    />
                  )}
                </g>
              );
            })}
          </svg>

          {/* Orchestrator Core */}
          <div className="orchestrator-core aero-glass">
            <div className="core-pulse"></div>
            <ShieldCheck size={48} className="text-white" />
          </div>

          {/* Agent Nodes */}
          {agents.map((agent) => {
            const rad = (agent.angle * Math.PI) / 180;
            const x = radius * Math.cos(rad);
            const y = radius * Math.sin(rad);
            const Icon = agent.icon;

            return (
              <motion.div
                key={agent.id}
                className="agent-node aero-glass violet"
                style={{
                  x,
                  y,
                }}
                animate={{
                  y: [y - 5, y + 5, y - 5], // Independent floating bob
                }}
                transition={{
                  duration: 4 + (agent.id % 3),
                  repeat: Infinity,
                  ease: "easeInOut"
                }}
              >
                <Icon size={24} className={isScanning ? "animate-pulse" : ""} />
                <span className="agent-label">{agent.name}</span>
              </motion.div>
            );
          })}
          
        </div>
      </Tilt>
    </section>
  );
};

export default AgentConstellation;
