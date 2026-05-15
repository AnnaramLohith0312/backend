'use client';
import React from 'react';

export default function Hero() {
  return (
    <div className="section-large" style={{ position: 'relative', textAlign: 'center' }}>
      {/* Background glow */}
      <div 
        className="glow-accent" 
        style={{ top: '10%', left: '50%', transform: 'translate(-50%, 0)', width: '600px', height: '600px', opacity: 0.1 }}
      ></div>

      <div className="container" style={{ position: 'relative', zIndex: 1 }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          
          <div className="ui-label" style={{ marginBottom: 'var(--space-24)', padding: 'var(--space-8) var(--space-16)', backgroundColor: 'var(--surface-1)', border: '1px solid var(--border-muted)', borderRadius: '100px' }}>
            Introducing SentinelOps AI
          </div>

          <h1 className="hero-title">
            The autonomous<br />night shift.
          </h1>
          
          <p className="hero-subtitle">
            An AI-native SRE copilot that autonomously investigates production incidents, reconstructs causal chains, and generates remediation workflows in real time.
          </p>

          <div style={{ display: 'flex', gap: 'var(--space-16)', marginBottom: 'var(--space-96)' }}>
            <button className="btn btn-neon">
              Start Investigation
            </button>
            <button className="btn btn-secondary">
              View Documentation
            </button>
          </div>

        </div>
      </div>
    </div>
  );
}
