import React, { useState, useEffect } from 'react';
import Tilt from 'react-parallax-tilt';
import { ScanSearch } from 'lucide-react';
import '../App.css';

const Hero = ({ onScan }) => {
  const [url, setUrl] = useState('');
  const [typedText, setTypedText] = useState('');
  const [phraseIndex, setPhraseIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);
  
  const phrases = [
    "DECODING THE WEB,\nONE URL AT A TIME.",
    "UNCOVERING THREATS,\nSECURING YOUR FUTURE.",
    "TRUSTLENS-AI,\nYOUR DIGITAL SHIELD."
  ];

  useEffect(() => {
    const currentPhrase = phrases[phraseIndex];
    let typingSpeed = isDeleting ? 30 : 60;

    if (!isDeleting && typedText === currentPhrase) {
      typingSpeed = 2000;
      const timeout = setTimeout(() => setIsDeleting(true), typingSpeed);
      return () => clearTimeout(timeout);
    } else if (isDeleting && typedText === '') {
      setIsDeleting(false);
      setPhraseIndex((prev) => (prev + 1) % phrases.length);
      return;
    }

    const timeout = setTimeout(() => {
      setTypedText(currentPhrase.slice(0, typedText.length + (isDeleting ? -1 : 1)));
    }, typingSpeed);

    return () => clearTimeout(timeout);
  }, [typedText, isDeleting, phraseIndex]);

  const handleScan = (e) => {
    e.preventDefault();
    if (url && onScan) {
      onScan(url);
    }
  };

  return (
    <section className="hero-container">
      <h1 className="hero-title" style={{ whiteSpace: 'pre-line', minHeight: '2.4em' }}>
        {typedText}
        <span className="cursor-blink">|</span>
      </h1>
      
      <div className="search-box-wrapper">
        <Tilt 
          tiltMaxAngleX={10} 
          tiltMaxAngleY={10} 
          perspective={1000} 
          transitionSpeed={1500}
          scale={1.05}
          gyroscope={true}
        >
          <form className="search-box aero-glass" onSubmit={handleScan}>
            <input 
              type="text" 
              className="search-input" 
              placeholder="Enter Target URL / Domain / IP..."
              value={url}
              onChange={(e) => setUrl(e.target.value)}
            />
            <button type="submit" className="search-btn">
              <ScanSearch size={18} />
              Analyze
            </button>
          </form>
        </Tilt>
      </div>
    </section>
  );
};

export default Hero;
