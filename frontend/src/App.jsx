import React, { useState, useEffect } from 'react';
import { Shield, AlertCircle, RefreshCw, Layers, Database, ShieldAlert, Cpu } from 'lucide-react';
import { getComplianceSummary, getViolations, triggerResourceEvaluation } from './services/api';
import ComplianceRing from './components/ComplianceRing';
import MetricCard from './components/MetricCard';
import ProviderCard from './components/ProviderCard';
import ViolationTable from './components/ViolationTable';
import DetailModal from './components/DetailModal';

export default function App() {
  const [summary, setSummary] = useState(null);
  const [violations, setViolations] = useState([]);
  const [selectedItem, setSelectedItem] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [isDemoMode, setIsDemoMode] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Core Data Fetching
  const fetchData = async (showLoadingSpinner = false) => {
    if (showLoadingSpinner) setLoading(true);
    setErrorMsg(null);
    try {
      const summaryResp = await getComplianceSummary();
      const violationsResp = await getViolations();

      // Defensive summary processing
      const defaultSummary = {
        total_resources: 0,
        compliant_resources: 0,
        non_compliant_resources: 0,
        compliance_percentage: 100,
        critical: 0,
        high: 0,
        medium: 0,
        low: 0,
        providers: {
          AWS: { total: 0, compliant: 0, violations: 0, percentage: 100 },
          GCP: { total: 0, compliant: 0, violations: 0, percentage: 100 }
        }
      };

      const summaryData = {
        ...defaultSummary,
        ...summaryResp.data,
        providers: {
          AWS: { ...defaultSummary.providers.AWS, ...(summaryResp.data?.providers?.AWS || {}) },
          GCP: { ...defaultSummary.providers.GCP, ...(summaryResp.data?.providers?.GCP || {}) }
        }
      };

      // Defensive violations processing (handles flat list or wrapped object)
      const violationsList = Array.isArray(violationsResp.data)
        ? violationsResp.data
        : (violationsResp.data?.violations || []);

      setSummary(summaryData);
      setViolations(violationsList);
      
      // If either endpoint resolved from mock data, report simulated state
      setIsDemoMode(summaryResp.isMock || violationsResp.isMock);
    } catch (err) {
      setErrorMsg('Failed to process compliance data.');
    } finally {
      setLoading(false);
    }
  };

  // Initial load and periodic polling setup (every 10 seconds)
  useEffect(() => {
    fetchData(true);
    
    const intervalId = setInterval(() => {
      fetchData(false);
    }, 10000);

    return () => clearInterval(intervalId);
  }, []);

  // Trigger evaluation scan
  const handleTriggerScan = async () => {
    setRefreshing(true);
    try {
      await triggerResourceEvaluation();
      await fetchData(false);
    } catch (err) {
      console.error('Scan trigger failed:', err);
    } finally {
      // Simulate scan duration
      setTimeout(() => {
        setRefreshing(false);
      }, 1000);
    }
  };


  if (loading) {
    return (
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        backgroundColor: 'var(--bg-primary)',
        color: 'var(--text-primary)',
        gap: '1.5rem'
      }}>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid rgba(56, 189, 248, 0.2)',
          borderTopColor: 'var(--sky-blue)',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite'
        }} />
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Loading Compliance Sentinel metrics...</p>
        <style dangerouslySetInnerHTML={{__html: `
          @keyframes spin { to { transform: rotate(360deg); } }
        `}} />
      </div>
    );
  }

  const complianceRate = summary ? summary.compliance_percentage : 0;

  return (
    <div style={{
      maxWidth: '1280px',
      margin: '0 auto',
      padding: '2rem 1.5rem'
    }}>
      {/* Top Banner Alert if using Demo fallback */}
      {isDemoMode && (
        <div style={{
          backgroundColor: 'rgba(245, 158, 11, 0.08)',
          border: '1px solid rgba(245, 158, 11, 0.25)',
          borderRadius: '8px',
          padding: '0.75rem 1rem',
          display: 'flex',
          alignItems: 'center',
          gap: '0.75rem',
          marginBottom: '2rem',
          color: 'var(--warning-amber)'
        }}>
          <AlertCircle size={18} />
          <div style={{ fontSize: '0.85rem' }}>
            <span style={{ fontWeight: 700 }}>DEMO / SIMULATION MODE ACTIVE: </span>
            Could not connect to the backend server API. Showing pre-defined local compliance violation statistics.
          </div>
        </div>
      )}

      {/* Header Toolbar */}
      <header style={{
        display: 'flex',
        flexWrap: 'wrap',
        justifyContent: 'space-between',
        alignItems: 'center',
        gap: '1.5rem',
        marginBottom: '2.5rem',
        borderBottom: '1px solid var(--border-color)',
        paddingBottom: '1.5rem'
      }}>
        <div>
          <h1 style={{
            fontSize: '2.25rem',
            fontWeight: 800,
            fontFamily: 'Outfit, sans-serif',
            color: 'var(--text-primary)',
            display: 'flex',
            alignItems: 'center',
            gap: '0.75rem'
          }}>
            <Shield size={32} style={{ color: 'var(--sky-blue)' }} />
            CloudCompliance Sentinel
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
            GDPR & HIPAA Configuration Drift Auditing System
          </p>
        </div>

        <button
          onClick={handleTriggerScan}
          disabled={refreshing}
          style={{
            backgroundColor: 'var(--sky-blue)',
            color: '#020617',
            border: 'none',
            borderRadius: '8px',
            padding: '0.6rem 1.25rem',
            fontSize: '0.875rem',
            fontWeight: 700,
            cursor: refreshing ? 'not-allowed' : 'pointer',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.5rem',
            opacity: refreshing ? 0.7 : 1,
            transition: 'opacity 0.2s ease'
          }}
        >
          <RefreshCw size={16} className={refreshing ? 'spin-anim' : ''} style={{
            animation: refreshing ? 'spin 1s linear infinite' : 'none'
          }} />
          {refreshing ? 'Re-scanning...' : 'Refresh Scan'}
        </button>
      </header>

      {/* Main Layout Grid */}
      <main>
        {/* Compliance stats widgets */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          {/* Compliance Progress section */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '1.5rem',
            alignItems: 'stretch'
          }}>
            {/* Overall Ring panel */}
            <div className="glass-panel" style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '2rem',
              flexWrap: 'wrap'
            }}>
              <ComplianceRing percentage={complianceRate} />
              <div style={{ flex: 1, minWidth: '180px' }}>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 800, fontFamily: 'Outfit, sans-serif', marginBottom: '0.5rem' }}>
                  Auditing Score
                </h2>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  This score reflects the percentage of cloud assets meeting the GDPR & HIPAA requirements of your active compliance policies.
                </p>
              </div>
            </div>

            {/* Counts metrics */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))',
              gap: '1rem'
            }}>
              <MetricCard
                title="Resources Scanned"
                value={summary ? summary.total_resources : 0}
                icon={Layers}
                color="var(--sky-blue)"
              />
              <MetricCard
                title="Compliant Assets"
                value={summary ? summary.compliant_resources : 0}
                icon={Database}
                color="var(--compliant-green)"
              />
              <MetricCard
                title="Active Violations"
                value={summary ? summary.non_compliant_resources : 0}
                icon={ShieldAlert}
                color="var(--danger-red)"
              />
            </div>
          </div>
        </div>

        {/* Severity Metrics Distribution Panel */}
        <section style={{ marginBottom: '2rem' }}>
          <div className="glass-panel">
            <h4 style={{
              fontSize: '0.85rem',
              fontWeight: 600,
              color: 'var(--text-secondary)',
              textTransform: 'uppercase',
              marginBottom: '1rem',
              letterSpacing: '0.05em'
            }}>
              Violations Severity Distribution
            </h4>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
              gap: '1.5rem'
            }}>
              <div style={{ padding: '0.75rem', borderLeft: '3px solid var(--danger-red)', backgroundColor: 'rgba(239, 68, 68, 0.05)', borderRadius: '0 6px 6px 0' }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>CRITICAL</p>
                <p style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>{summary ? summary.critical : 0}</p>
              </div>
              <div style={{ padding: '0.75rem', borderLeft: '3px solid var(--danger-red)', backgroundColor: 'rgba(239, 68, 68, 0.05)', borderRadius: '0 6px 6px 0' }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>HIGH</p>
                <p style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>{summary ? summary.high : 0}</p>
              </div>
              <div style={{ padding: '0.75rem', borderLeft: '3px solid var(--warning-amber)', backgroundColor: 'rgba(245, 158, 11, 0.05)', borderRadius: '0 6px 6px 0' }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>MEDIUM</p>
                <p style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>{summary ? summary.medium : 0}</p>
              </div>
              <div style={{ padding: '0.75rem', borderLeft: '3px solid var(--sky-blue)', backgroundColor: 'rgba(56, 189, 248, 0.05)', borderRadius: '0 6px 6px 0' }}>
                <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 600 }}>LOW</p>
                <p style={{ fontSize: '1.75rem', fontWeight: 800, color: 'var(--text-primary)' }}>{summary ? summary.low : 0}</p>
              </div>
            </div>
          </div>
        </section>

        {/* Provider summaries grid */}
        <section style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          <ProviderCard name="AWS" stats={summary?.providers?.AWS} />
          <ProviderCard name="GCP" stats={summary?.providers?.GCP} />
        </section>

        {/* Violations grid table */}
        <section style={{ marginBottom: '3rem' }}>
          <ViolationTable
            violations={violations}
            onSelect={(item) => setSelectedItem(item)}
          />
        </section>
      </main>

      {/* Side Slide-out Details Drawer */}
      {selectedItem && (
        <DetailModal
          item={selectedItem}
          onClose={() => setSelectedItem(null)}
        />
      )}
    </div>
  );
}
