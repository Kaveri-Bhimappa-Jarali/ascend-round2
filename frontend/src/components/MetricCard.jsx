import React from 'react';

export default function MetricCard({ title, value, subtitle, color, icon: Icon }) {
  return (
    <div className="glass-panel" style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* Dynamic Colored Bar */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: '4px',
        height: '100%',
        backgroundColor: color || 'var(--sky-blue)'
      }} />

      <div style={{ paddingLeft: '8px' }}>
        <p style={{
          fontSize: '0.85rem',
          fontWeight: 600,
          color: 'var(--text-secondary)',
          textTransform: 'uppercase',
          marginBottom: '0.5rem',
          letterSpacing: '0.05em'
        }}>
          {title}
        </p>
        <h3 style={{
          fontSize: '2.25rem',
          fontWeight: 800,
          fontFamily: 'Outfit, sans-serif',
          color: 'var(--text-primary)',
          lineHeight: 1
        }}>
          {value}
        </h3>
        {subtitle && (
          <p style={{
            fontSize: '0.75rem',
            color: 'var(--text-secondary)',
            marginTop: '0.5rem'
          }}>
            {subtitle}
          </p>
        )}
      </div>

      {Icon && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          width: '48px',
          height: '48px',
          borderRadius: '50%',
          backgroundColor: 'rgba(30, 41, 59, 0.4)',
          color: color || 'var(--sky-blue)',
          marginRight: '8px'
        }}>
          <Icon size={24} />
        </div>
      )}
    </div>
  );
}
