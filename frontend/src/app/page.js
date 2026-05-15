import Hero from '@/components/ui/Hero';
import Features from '@/components/ui/Features';
import IncidentDashboard from '@/components/dashboard/IncidentDashboard';

export default function Home() {
  return (
    <main style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* Stage 1: Identity */}
      <Hero />

      {/* Stage 2: Product Visualization */}
      <div style={{ marginTop: 'calc(-1 * var(--space-128))', position: 'relative', zIndex: 10 }}>
        <IncidentDashboard />
      </div>

      {/* Stage 3: Capability Expansion */}
      <Features />

      {/* Stage 6: Conversion Push */}
      <div className="section" style={{ textAlign: 'center', backgroundColor: 'var(--bg-primary)' }}>
        <div className="container">
          <h2 className="section-title">Ready to automate your incident response?</h2>
          <p className="section-subtitle" style={{ maxWidth: '600px', margin: '0 auto var(--space-48) auto' }}>
            Deploy SentinelOps AI today and turn fragmented telemetry into autonomous operational reasoning.
          </p>
          <button className="btn btn-neon" style={{ padding: 'var(--space-16) var(--space-48)', fontSize: '1.125rem' }}>
            Get Early Access
          </button>
        </div>
      </div>

      {/* Simple Footer */}
      <footer style={{ borderTop: '1px solid var(--border-muted)', padding: 'var(--space-48) 0', textAlign: 'center', color: 'var(--text-muted)' }}>
        <div className="container">
          <p>© {new Date().getFullYear()} SentinelOps AI. All rights reserved.</p>
        </div>
      </footer>

    </main>
  );
}
