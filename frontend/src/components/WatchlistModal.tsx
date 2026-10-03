import React from 'react';
import { Bookmark, X, ExternalLink, Trash2 } from 'lucide-react';
import type { CompanyProfile } from '../types';

interface WatchlistModalProps {
  watchlist: CompanyProfile[];
  onRemove: (companyId: string) => void;
  onSelect: (company: CompanyProfile) => void;
  onClose: () => void;
}

export const WatchlistModal: React.FC<WatchlistModalProps> = ({
  watchlist,
  onRemove,
  onSelect,
  onClose
}) => {
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
        maxWidth: '750px',
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '28px'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', marginBottom: '20px' }}>
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Bookmark size={20} color="var(--brand-primary)" />
              Saved Corporate Watchlist
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '2px' }}>
              Tracked entities for compliance changes, filing alerts, and GST registration updates.
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
            <X size={22} />
          </button>
        </div>

        {watchlist.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 20px', color: 'var(--text-muted)' }}>
            <Bookmark size={40} style={{ margin: '0 auto 12px auto', opacity: 0.5 }} />
            <p style={{ fontSize: '15px', color: 'var(--text-secondary)' }}>Your Watchlist is empty.</p>
            <p style={{ fontSize: '13px', marginTop: '4px' }}>Click "Save" on any company profile to monitor it here.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {watchlist.map((company) => (
              <div
                key={company.id}
                className="bento-card"
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '16px 20px',
                  flexWrap: 'wrap',
                  gap: '12px'
                }}
              >
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <h3
                      onClick={() => onSelect(company)}
                      style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text-primary)', cursor: 'pointer' }}
                    >
                      {company.legal_name}
                    </h3>
                    <span className="status-pill status-active" style={{ fontSize: '10px', padding: '2px 8px' }}>
                      {company.company_status}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: '14px', marginTop: '4px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                    <span>CIN: <strong style={{ color: 'var(--text-primary)' }}>{company.cin}</strong></span>
                    <span>State: {company.registered_state}</span>
                    <span>GSTINs: {company.gst_registrations.length}</span>
                    <span>Updated: {company.last_updated}</span>
                  </div>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <button
                    onClick={() => onSelect(company)}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '4px',
                      padding: '6px 12px',
                      borderRadius: '6px',
                      background: 'rgba(56, 189, 248, 0.12)',
                      border: '1px solid rgba(56, 189, 248, 0.3)',
                      color: 'var(--brand-primary)',
                      fontSize: '12px',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    <ExternalLink size={13} />
                    View
                  </button>

                  <button
                    onClick={() => onRemove(company.id)}
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--ruby)',
                      cursor: 'pointer',
                      padding: '6px'
                    }}
                    title="Remove from Watchlist"
                  >
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
