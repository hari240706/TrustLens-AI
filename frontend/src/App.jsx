import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import AgentConstellation from './components/AgentConstellation';
import CapabilityGrid from './components/CapabilityGrid';
import LiveFeedTerminal from './components/LiveFeedTerminal';
import Verdict from './components/Verdict';
import './App.css';

const App = () => {
  const [isScanning, setIsScanning] = useState(false);
  const [logs, setLogs] = useState([]);
  const [score, setScore] = useState(null);

  const addLog = (text, type = 'white') => {
    setLogs(prev => [...prev, { text, type }]);
  };

  const handleScan = async (url) => {
    setIsScanning(true);
    setScore(null);
    setLogs([
      { type: 'white', text: `INITIATING SCAN FOR: ${url}` },
      { type: 'white', text: 'Dispatching TrustLens Orchestrator API...' },
    ]);

    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `Request failed with status ${response.status}`);
      }

      const data = await response.json();

      addLog('SCAN COMPLETE. PROCESSING AGENT BREAKDOWN...', 'white');

      // High-level verdict + score
      addLog(
        `VERDICT: ${String(data.verdict || '').toUpperCase()} | RISK SCORE: ${data.risk_score}`,
        data.risk_score >= 80 ? 'red' : data.risk_score >= 40 ? 'yellow' : 'green'
      );

      if (data.intent) {
        addLog(`PREDICTED INTENT: ${data.intent}`, 'white');
      }

      // Reasoning trace from explainability agent
      if (Array.isArray(data.reasoning_trace)) {
        data.reasoning_trace.forEach((line) => {
          if (typeof line === 'string' && line.trim()) {
            addLog(line, 'white');
          }
        });
      }

      // Per‑agent signals (if present)
      const breakdown = data.agent_breakdown || {};
      const agentEntries = Object.entries(breakdown);
      agentEntries.forEach(([agentName, agentData]) => {
        if (!agentData) return;
        const agentScore = agentData.risk_score ?? 0;
        const label = agentName.toUpperCase();
        const color =
          agentScore >= 80 ? 'red' : agentScore >= 40 ? 'yellow' : 'green';

        addLog(`[${label}] RISK SCORE: ${agentScore}`, color);

        if (Array.isArray(agentData.reasoning)) {
          agentData.reasoning.forEach((reason) => {
            if (typeof reason === 'string' && reason.trim()) {
              addLog(`[${label}] ${reason}`, color);
            }
          });
        }
      });

      setScore(data.risk_score ?? null);
    } catch (err) {
      addLog(`ERROR: ${err.message || 'Unknown error while contacting API'}`, 'red');
      setScore(null);
    } finally {
      setIsScanning(false);
    }
  };

  // Warning pulse background is handled by the .warning-state class in index.css

  return (
    <div className={`app-container ${score >= 80 ? 'warning-state' : ''}`}>
      <div className="star-mist"></div>
      <Navbar />
      <div id="dashboard">
        <Hero onScan={handleScan} />
      </div>
      <div id="agents">
        <AgentConstellation isScanning={isScanning} />
      </div>
      <div id="network">
        <CapabilityGrid />
      </div>
      <div id="verdict">
        <Verdict score={score} />
      </div>
      <div id="logs">
        {logs.length > 0 && <LiveFeedTerminal logs={logs} />}
      </div>
    </div>
  );
};

export default App;
