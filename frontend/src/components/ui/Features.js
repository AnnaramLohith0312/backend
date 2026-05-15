'use client';
import React from 'react';

const features = [
  {
    title: "Log Investigation Agent",
    description: "Autonomously retrieves and vector searches operational logs to detect anomalies and extract stack traces.",
    icon: "🔍"
  },
  {
    title: "Deployment Analysis Agent",
    description: "Cross-references incident timing with commit histories to identify probable deployment regressions.",
    icon: "📦"
  },
  {
    title: "Trace Correlation Engine",
    description: "Reconstructs distributed traces to identify precise dependency bottlenecks causing upstream failures.",
    icon: "🕸️"
  },
  {
    title: "Remediation Planner",
    description: "Generates operational playbooks and confidence-scored rollback recommendations.",
    icon: "⚡"
  }
];

export default function Features() {
  return (
    <div className="section" style={{ backgroundColor: 'var(--surface-1)' }}>
      <div className="container">
        
        <div style={{ textAlign: 'center', marginBottom: 'var(--space-64)' }}>
          <h2 className="section-title">Multi-Agent Autonomy</h2>
          <p className="section-subtitle">
            SentinelOps AI orchestrates a swarm of specialized agents to execute complex triage workflows in parallel.
          </p>
        </div>

        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
          gap: 'var(--space-24)' 
        }}>
          {features.map((feature, idx) => (
            <div key={idx} className="card">
              <div style={{ 
                fontSize: '2rem', 
                marginBottom: 'var(--space-16)',
                display: 'inline-block',
                padding: 'var(--space-12)',
                backgroundColor: 'rgba(255,255,255,0.03)',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--border-muted)'
              }}>
                {feature.icon}
              </div>
              <h3 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: 'var(--space-8)' }}>
                {feature.title}
              </h3>
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                {feature.description}
              </p>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
}
