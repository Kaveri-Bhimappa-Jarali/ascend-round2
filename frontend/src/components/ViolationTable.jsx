import React, { useState } from 'react';
import { Search, Filter, Eye } from 'lucide-react';

export default function ViolationTable({ violations = [], onSelect }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [providerFilter, setProviderFilter] = useState('ALL');
  const [severityFilter, setSeverityFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');

  // Local filtering logic
  const filteredViolations = Array.isArray(violations) ? violations.filter(item => {
    const matchesSearch = 
      (item.resource_name || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.rule_id || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (item.message || '').toLowerCase().includes(searchTerm.toLowerCase());
      
    const matchesProvider = providerFilter === 'ALL' || (item.provider || '').toUpperCase() === providerFilter;
    const matchesSeverity = severityFilter === 'ALL' || (item.severity || '').toUpperCase() === severityFilter;
    const matchesType = typeFilter === 'ALL' || (item.resource_type || '').toLowerCase() === typeFilter.toLowerCase();

    return matchesSearch && matchesProvider && matchesSeverity && matchesType;
  }) : [];

  return (
    <div className="glass-panel" style={{ padding: '1.25rem' }}>
      <h3 style={{
        fontSize: '1.25rem',
        fontWeight: 700,
        fontFamily: 'Outfit, sans-serif',
        color: 'var(--text-primary)',
        marginBottom: '1rem'
      }}>
        Compliance Violations Listing
      </h3>

      {/* Filters Toolbar */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        gap: '1rem',
        marginBottom: '1.5rem',
        alignItems: 'center'
      }}>
        {/* Search Input */}
        <div style={{
          position: 'relative',
          flex: '1 1 240px'
        }}>
          <Search size={16} style={{
            position: 'absolute',
            left: '12px',
            top: '50%',
            transform: 'translateY(-50%)',
            color: 'var(--text-secondary)'
          }} />
          <input
            type="text"
            placeholder="Search by resource, rule, or error..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            style={{
              width: '100%',
              backgroundColor: '#020617',
              border: '1px solid #334155',
              borderRadius: '6px',
              padding: '0.5rem 1rem 0.5rem 2.25rem',
              color: 'var(--text-primary)',
              fontSize: '0.875rem',
              outline: 'none'
            }}
          />
        </div>

        {/* Provider Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Provider:</label>
          <select
            value={providerFilter}
            onChange={(e) => setProviderFilter(e.target.value)}
            style={{
              backgroundColor: '#020617',
              border: '1px solid #334155',
              color: 'var(--text-primary)',
              borderRadius: '6px',
              padding: '0.4rem 0.8rem',
              fontSize: '0.8rem',
              outline: 'none'
            }}
          >
            <option value="ALL">All Cloud</option>
            <option value="AWS">AWS</option>
            <option value="GCP">GCP</option>
          </select>
        </div>

        {/* Severity Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Severity:</label>
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            style={{
              backgroundColor: '#020617',
              border: '1px solid #334155',
              color: 'var(--text-primary)',
              borderRadius: '6px',
              padding: '0.4rem 0.8rem',
              fontSize: '0.8rem',
              outline: 'none'
            }}
          >
            <option value="ALL">All Severities</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>

        {/* Type Filter */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <label style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase', fontWeight: 600 }}>Resource:</label>
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            style={{
              backgroundColor: '#020617',
              border: '1px solid #334155',
              color: 'var(--text-primary)',
              borderRadius: '6px',
              padding: '0.4rem 0.8rem',
              fontSize: '0.8rem',
              outline: 'none'
            }}
          >
            <option value="ALL">All Types</option>
            <option value="storage">Storage</option>
            <option value="database">Database</option>
            <option value="vpc">VPC</option>
          </select>
        </div>
      </div>

      {/* Results Table */}
      <div className="table-container">
        {filteredViolations.length === 0 ? (
          <div style={{
            textAlign: 'center',
            padding: '3rem 1.5rem',
            color: 'var(--text-secondary)'
          }}>
            <p style={{ fontSize: '1rem', fontWeight: 500, marginBottom: '0.25rem' }}>No violations found</p>
            <p style={{ fontSize: '0.75rem' }}>Try adjusting your filters or search term.</p>
          </div>
        ) : (
          <table className="custom-table">
            <thead>
              <tr>
                <th>Provider</th>
                <th>Resource Name</th>
                <th>Type</th>
                <th>Rule / Issue</th>
                <th>Severity</th>
                <th>Status</th>
                <th style={{ textAlign: 'right' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredViolations.map((item, idx) => (
                <tr key={`${item.resource_id}-${idx}`} style={{ cursor: 'pointer' }} onClick={() => onSelect(item)}>
                  <td>
                    <span className={`provider-badge ${item.provider.toLowerCase()}`}>
                      {item.provider}
                    </span>
                  </td>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                    {item.resource_name}
                  </td>
                  <td style={{ textTransform: 'capitalize', color: 'var(--text-secondary)' }}>
                    {item.resource_type}
                  </td>
                  <td style={{ color: 'var(--text-primary)' }}>
                    {item.rule_id.replace(/_/g, ' ')}
                  </td>
                  <td>
                    <span className={`severity-badge ${item.severity.toLowerCase()}`}>
                      {item.severity}
                    </span>
                  </td>
                  <td>
                    <span style={{
                      color: 'var(--danger-red)',
                      fontWeight: 600,
                      fontSize: '0.75rem',
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '0.25rem'
                    }}>
                      Non-Compliant
                    </span>
                  </td>
                  <td style={{ textAlign: 'right' }}>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        onSelect(item);
                      }}
                      style={{
                        backgroundColor: 'transparent',
                        border: 'none',
                        color: 'var(--sky-blue)',
                        cursor: 'pointer',
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '0.25rem',
                        fontSize: '0.8rem',
                        fontWeight: 600
                      }}
                    >
                      <Eye size={14} />
                      Inspect
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
