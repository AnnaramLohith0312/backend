'use client';
import React from 'react';

export default function IncidentDashboard() {
  return (
    <div className="section" style={{ position: 'relative', zIndex: 2 }}>
      <div className="container">
        
        {/* The Dashboard Frame */}
        <div style={{
          backgroundColor: 'var(--bg-primary)',
          border: '1px solid var(--border-muted)',
          borderRadius: 'var(--radius-xl)',
          padding: 'var(--space-24)',
          boxShadow: 'var(--shadow-glow), 0 20px 40px rgba(0,0,0,0.8)',
          display: 'grid',
          gridTemplateColumns: '1fr 300px',
          gap: 'var(--space-24)',
          minHeight: '600px',
          overflow: 'hidden'
        }}>
          
          {/* Main Area: Causal Graph / Timeline */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-24)' }}>
            
            {/* Header */}
            <div style={{ borderBottom: '1px solid var(--border-muted)', paddingBottom: 'var(--space-16)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: 'var(--space-8)' }}>
                  <span style={{ display: 'inline-block', width: '10px', height: '10px', backgroundColor: 'var(--accent-red)', borderRadius: '50%', boxShadow: '0 0 10px var(--accent-red)' }}></span>
                  Incident: Latency Spike in billing-service
                </h3>
                <p className="ui-label" style={{ marginTop: 'var(--space-4)' }}>ID: INC-8291 • Severity: High • Status: Investigating</p>
              </div>
              <div className="ui-label" style={{ color: 'var(--accent-neon)' }}>
                Autonomy Mode: Active
              </div>
            </div>

            {/* Causal Chain Visualization Mock */}
            <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 'var(--space-16)' }}>
              <div className="ui-label">Probable Causal Chain (Confidence: 82%)</div>
              
              <div style={{ padding: 'var(--space-16)', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--accent-neon)' }}>
                <strong>1. Deploy v2.14.0</strong>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Commit 8f92a1c • 14:02 UTC</p>
              </div>
              
              <div style={{ width: '2px', height: '20px', backgroundColor: 'var(--border-muted)', margin: '0 var(--space-24)' }}></div>
              
              <div style={{ padding: 'var(--space-16)', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--accent-pink)' }}>
                <strong>2. Database Connection Pool Exhaustion</strong>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Detected via log-agent • 14:05 UTC</p>
              </div>
              
              <div style={{ width: '2px', height: '20px', backgroundColor: 'var(--border-muted)', margin: '0 var(--space-24)' }}></div>
              
              <div style={{ padding: 'var(--space-16)', backgroundColor: 'var(--bg-secondary)', borderRadius: 'var(--radius-md)', borderLeft: '3px solid var(--accent-red)' }}>
                <strong>3. Latency increase in billing-service</strong>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>P99 &gt; 2.4s • Triggered Webhook</p>
              </div>
            </div>

          </div>

          {/* Right Sidebar: Agent Activity & Remediation */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-16)', borderLeft: '1px solid var(--border-muted)', paddingLeft: 'var(--space-24)' }}>
            
            <div>
              <div className="ui-label" style={{ marginBottom: 'var(--space-12)' }}>Live Agent Orchestration</div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>
                <div style={{ fontSize: '0.875rem', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Planner Agent</span> <span style={{ color: 'var(--text-secondary)' }}>Done</span>
                </div>
                <div style={{ fontSize: '0.875rem', display: 'flex', justifyContent: 'space-between' }}>
                  <span>Log Agent</span> <span style={{ color: 'var(--text-secondary)' }}>Done</span>
                </div>
                <div style={{ fontSize: '0.875rem', display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--accent-neon)' }}>Deploy Agent</span> <span>Active...</span>
                </div>
                <div style={{ fontSize: '0.875rem', display: 'flex', justifyContent: 'space-between' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Remediation</span> <span>Waiting</span>
                </div>
              </div>
            </div>

            <div style={{ marginTop: 'auto' }}>
              <div className="card" style={{ backgroundColor: 'rgba(59, 130, 246, 0.05)', borderColor: 'var(--accent-neon)' }}>
                <div className="ui-label" style={{ color: 'var(--accent-neon)', marginBottom: 'var(--space-8)' }}>Recommended Action</div>
                <p style={{ fontSize: '0.875rem', marginBottom: 'var(--space-12)' }}>Rollback billing-service to previous stable version (v2.13.9)</p>
                <button className="btn btn-neon" style={{ width: '100%', fontSize: '0.875rem', padding: 'var(--space-8)' }}>
                  Execute Rollback
                </button>
              </div>
            </div>

          </div>

        </div>

      </div>
    </div>
  );
}
