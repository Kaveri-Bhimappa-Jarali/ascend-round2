import React from 'react';

function App() {
  return (
    <div style={{
      fontFamily: 'Inter, sans-serif',
      padding: '2rem',
      backgroundColor: '#0f172a',
      color: '#f8fafc',
      minHeight: '100vh'
    }}>
      <header style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: 700, color: '#38bdf8' }}>
          CloudCompliance Sentinel
        </h1>
        <p style={{ color: '#94a3b8' }}>
          Continuous Multi-Cloud Security Auditing
        </p>
      </header>
      <main>
        <div style={{
          background: 'rgba(30, 41, 59, 0.7)',
          padding: '1.5rem',
          borderRadius: '12px',
          border: '1px solid #334155'
        }}>
          <h2>Welcome</h2>
          <p>This is the dashboard placeholder for CloudCompliance Sentinel.</p>
        </div>
      </main>
    </div>
  );
}

export default App;
