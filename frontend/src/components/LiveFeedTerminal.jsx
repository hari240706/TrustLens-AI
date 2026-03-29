import React, { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';
import './LiveFeedTerminal.css';

const LiveFeedTerminal = ({ logs }) => {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  return (
    <div className="terminal-container aero-glass">
      <div className="terminal-header">
        <Terminal size={14} />
        <span>ORCHESTRATOR THREAD_0</span>
      </div>
      <div className="terminal-body" ref={scrollRef}>
        <div className="crt-scanline"></div>
        {logs.map((log, i) => (
          <div key={i} className={`log-line ${log.type}`}>
            <span className="opacity-50 inline-block mr-2">{'>'}</span> 
            {log.text}
          </div>
        ))}
      </div>
    </div>
  );
};

export default LiveFeedTerminal;
