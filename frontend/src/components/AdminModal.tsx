import React, { useState, useEffect } from 'react';
import { RefreshCw, CheckCircle, X } from 'lucide-react';
import type { ConnectorHealth } from '../types';
import { getSourceHealthAPI, triggerSourceSyncAPI } from '../api/client';

interface AdminModalProps {
  onClose: () => void;
}

export const AdminModal: React.FC<AdminModalProps> = ({ onClose }) => {
  const [sources, setSources] = useState<ConnectorHealth[]>([]);
  const [syncingSource, setSyncingSource] = useState<string | null>(null);
  const [syncMessage, setSyncMessage] = useState<string | null>(null);

  useEffect(() => {
    loadHealth();
  }, []);

  const loadHealth = async () => {
    const data = await getSourceHealthAPI();
    setSources(data);
  };

  const handleSync = async (sourceName: string) => {
    setSyncingSource(sourceName);
    const res = await triggerSourceSyncAPI(sourceName);
    setSyncMessage(res.message);
    await loadHealth();
    setSyncingSource(null);
    setTimeout(() => setSyncMessage(null), 3500);
  };

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.8)',
      backdropFilter: 'blur(8px)',
      zIndex: 9999,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '20px'
    }}>
      <div className="glass-panel" style={{
        maxWidth: '850px',
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '28px'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', marginBottom: '20px' }}>
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)' }}>
              CompanyLens Administration & Data Governance
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '2px' }}>
              Real-time monitoring of connected government gateways, APIs, and data quality pipelines.
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
            <X size={22} />
          </button>
        </div>

        {syncMessage && (
          <div style={{
            padding: '10px 16px',
            borderRadius: '8px',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid var(--emerald)',
            color: 'var(--emerald)',
            fontSize: '13px',
            marginBottom: '16px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <CheckCircle size={16} />
            {syncMessage}
          </div>
        )}

        {/* System Summary KPI Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(170px, 1fr))', gap: '14px', marginBottom: '24px' }}>
          <div className="bento-card" style={{ padding: '16px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Total Companies</span>
            <p style={{ fontSize: '22px', fontWeight: 700, color: 'var(--brand-primary)', marginTop: '4px' }}>3 Active</p>
            <span style={{ fontSize: '11px', color: 'var(--emerald)' }}>100% Verified Identifiers</span>
          </div>

          <div className="bento-card" style={{ padding: '16px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>GST Registrations</span>
            <p style={{ fontSize: '22px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>4 State GSTINs</p>
            <span style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>Across 3 States</span>
          </div>

          <div className="bento-card" style={{ padding: '16px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Data Sources</span>
            <p style={{ fontSize: '22px', fontWeight: 700, color: 'var(--emerald)', marginTop: '4px' }}>4 Connectors</p>
            <span style={{ fontSize: '11px', color: 'var(--emerald)' }}>3 Live • 1 Unconfigured</span>
          </div>

          <div className="bento-card" style={{ padding: '16px' }}>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Failed Jobs</span>
            <p style={{ fontSize: '22px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>0</p>
            <span style={{ fontSize: '11px', color: 'var(--emerald)' }}>Clean Dead-letter Queue</span>
          </div>
        </div>

        {/* Connector Health Monitoring */}
        <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '12px', color: 'var(--text-primary)' }}>
          Authoritative Data Source Health & Synchronization
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
          {sources.map((src, i) => (
            <div key={i} className="bento-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontWeight: 600, fontSize: '14px' }}>{src.name}</span>
                  <span className={`status-pill ${src.status === 'HEALTHY' ? 'status-active' : 'status-inactive'}`} style={{ fontSize: '10px' }}>
                    {src.status}
                  </span>
                </div>
                <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: '3px' }}>
                  {src.message} • Latency: <strong style={{ color: 'var(--text-primary)' }}>{src.latency_ms}ms</strong>
                </p>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <button
                  onClick={() => handleSync(src.name)}
                  disabled={syncingSource === src.name}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 12px',
                    borderRadius: '6px',
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    color: 'var(--text-primary)',
                    fontSize: '12px',
                    fontWeight: 600,
                    cursor: 'pointer'
                  }}
                >
                  <RefreshCw size={13} className={syncingSource === src.name ? "animate-spin" : ""} />
                  {syncingSource === src.name ? "Syncing..." : "Sync Now"}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Data Quality Dashboard (Section 35) */}
        <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '12px', color: 'var(--text-primary)' }}>
          Data Quality & Governance Audit
        </h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '12px',
          background: 'var(--bg-surface)',
          padding: '16px',
          borderRadius: '10px',
          border: '1px solid var(--border-color)',
          fontSize: '13px'
        }}>
          <div>
            <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Missing CINs</span>
            <p style={{ fontWeight: 600, color: 'var(--emerald)' }}>0 (Zero defects)</p>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Duplicate Identifiers</span>
            <p style={{ fontWeight: 600, color: 'var(--emerald)' }}>0</p>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Stale Records</span>
            <p style={{ fontWeight: 600, color: 'var(--emerald)' }}>0 (All fresh)</p>
          </div>
          <div>
            <span style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Conflicting Company Names</span>
            <p style={{ fontWeight: 600, color: 'var(--emerald)' }}>0 (Resolved)</p>
          </div>
        </div>
      </div>
    </div>
  );
};
