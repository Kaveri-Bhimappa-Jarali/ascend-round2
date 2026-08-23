import React from 'react';

export default function ComplianceRing({ percentage = 0, size = 160 }) {
  const strokeWidth = 14;
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (Math.min(100, Math.max(0, percentage)) / 100) * circumference;

  // Determine dynamic ring color based on compliance performance
  let color = 'var(--danger-red)';
  if (percentage >= 80) {
    color = 'var(--compliant-green)';
  } else if (percentage >= 60) {
    color = 'var(--warning-amber)';
  }

  return (
    <div style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      position: 'relative',
      width: size,
      height: size
    }}>
      <svg width={size} height={size}>
        {/* Background Circle */}
        <circle
          className="ring-bg"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          strokeWidth={strokeWidth}
        />
        {/* Animated Progress Indicator */}
        <circle
          className="ring-indicator"
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="transparent"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      {/* Inner Label */}
      <div style={{
        position: 'absolute',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <span style={{
          fontSize: '2rem',
          fontWeight: 800,
          fontFamily: 'Outfit, sans-serif',
          color: color
        }}>
          {isNaN(percentage) ? '0' : Math.round(percentage)}%
        </span>
        <span style={{
          fontSize: '0.75rem',
          textTransform: 'uppercase',
          fontWeight: 600,
          color: 'var(--text-secondary)',
          marginTop: '2px'
        }}>
          Compliance
        </span>
      </div>
    </div>
  );
}
