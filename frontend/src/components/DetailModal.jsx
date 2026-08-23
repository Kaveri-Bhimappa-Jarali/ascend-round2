import React from 'react';
import { X, AlertTriangle, ShieldCheck } from 'lucide-react';

export default function DetailModal({ item, onClose }) {
  if (!item) return null;

  const isAws = item.provider.toLowerCase() === 'aws';

  return (
    <>
      {/* Backdrop overlay */}
      <div className="drawer-backdrop" onClick={onClose} />
      
      {/* Slide-out Drawer */}
      <div className="drawer">
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          borderBottom: '1px solid var(--border-color)',
          paddingBottom: '1rem'
        }}>
          <h3 style={{
            fontSize: '1.25rem',
            fontWeight: 700,
            fontFamily: 'Outfit, sans-serif',
            color: 'var(--text-primary)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem'
          }}>
            Resource Inspection
          </h3>
          <button
            onClick={onClose}
            style={{
              backgroundColor: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              cursor: 'pointer',
              display: 'flex',
              padding: '0.25rem',
              borderRadius: '50%'
            }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Resource Meta Section */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Provider</p>
            <span className={`provider-badge ${isAws ? 'aws' : 'gcp'}`} style={{ marginTop: '0.25rem', fontSize: '0.8rem' }}>
              {item.provider}
            </span>
          </div>

          <div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Resource Name</p>
            <p style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '0.25rem' }}>
              {item.resource_name}
            </p>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
            <div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Resource Type</p>
              <p style={{ fontSize: '0.9rem', fontWeight: 500, color: 'var(--text-primary)', marginTop: '0.25rem', textTransform: 'capitalize' }}>
                {item.resource_type}
              </p>
            </div>
            <div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Severity</p>
              <span className={`severity-badge ${item.severity.toLowerCase()}`} style={{ marginTop: '0.25rem' }}>
                {item.severity}
              </span>
            </div>
          </div>
        </div>

        {/* Violation Message Section */}
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.08)',
          border: '1px solid rgba(239, 68, 68, 0.2)',
          borderRadius: '8px',
          padding: '1rem',
          marginBottom: '1.5rem'
        }}>
          <p style={{
            fontSize: '0.8rem',
            color: 'var(--danger-red)',
            fontWeight: 700,
            textTransform: 'uppercase',
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem',
            marginBottom: '0.5rem'
          }}>
            <AlertTriangle size={14} />
            Violation Detected
          </p>
          <p style={{
            fontSize: '0.875rem',
            lineHeight: 1.5,
            color: 'var(--text-primary)'
          }}>
            {item.message}
          </p>
        </div>

        {/* Timestamps */}
        <div style={{ marginBottom: '1.5rem' }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Detected At</p>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-primary)', marginTop: '0.25rem' }}>
            {new Date(item.detected_at).toLocaleString()}
          </p>
        </div>

        {/* Raw Configuration Payload */}
        <div>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '0.5rem' }}>
            Resource Configuration Metadata
          </p>
          <div style={{
            backgroundColor: '#020617',
            border: '1px solid var(--border-color)',
            borderRadius: '6px',
            padding: '1rem',
            overflowX: 'auto'
          }}>
            <pre style={{
              fontSize: '0.8rem',
              color: '#38bdf8',
              fontFamily: 'Consolas, Monaco, monospace',
              lineHeight: 1.5
            }}>
              {JSON.stringify(item.configuration, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </>
  );
}
