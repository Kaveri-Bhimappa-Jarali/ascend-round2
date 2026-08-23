import React from 'react';

export default function ProviderCard({ name, stats }) {
  if (!stats) return null;

  const isAws = name.toLowerCase() === 'aws';
  const accentColor = isAws ? '#f97316' : '#3b82f6';
  const progressBg = isAws ? 'rgba(249, 115, 22, 0.1)' : 'rgba(59, 130, 246, 0.1)';

  return (
    <div className="glass-panel" style={{ position: 'relative' }}>
      {/* Dynamic Header color bar */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '3px',
        backgroundColor: accentColor
      }} />

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
        <h4 style={{
          fontSize: '1.25rem',
          fontWeight: 700,
          fontFamily: 'Outfit, sans-serif',
          color: 'var(--text-primary)',
          display: 'flex',
          alignItems: 'center',
          gap: '0.5rem'
        }}>
          <span className={`provider-badge ${isAws ? 'aws' : 'gcp'}`}>
            {name}
          </span>
          Compliance
        </h4>
        <span style={{
          fontSize: '1.25rem',
          fontWeight: 800,
          color: stats.percentage >= 80 ? 'var(--compliant-green)' : (stats.percentage >= 60 ? 'var(--warning-amber)' : 'var(--danger-red)')
        }}>
          {Math.round(stats.percentage)}%
        </span>
      </div>

      {/* Progress Bar */}
      <div style={{
        width: '100%',
        height: '6px',
        backgroundColor: progressBg,
        borderRadius: '3px',
        overflow: 'hidden',
        marginBottom: '1.5rem'
      }}>
        <div style={{
          width: `${stats.percentage}%`,
          height: '100%',
          backgroundColor: accentColor,
          borderRadius: '3px',
          transition: 'width 0.5s ease-out'
        }} />
      </div>

      {/* Statistics breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', textAlign: 'center' }}>
        <div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Scanned</p>
          <p style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--text-primary)' }}>{stats.total}</p>
        </div>
        <div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Compliant</p>
          <p style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--compliant-green)' }}>{stats.compliant}</p>
        </div>
        <div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '0.25rem' }}>Violations</p>
          <p style={{ fontSize: '1.15rem', fontWeight: 700, color: 'var(--danger-red)' }}>{stats.violations}</p>
        </div>
      </div>
    </div>
  );
}
