import React, { useState } from 'react';
import { ArrowRightLeft, X } from 'lucide-react';
import type { CompanyProfile } from '../types';
import { formatINR } from '../api/client';

interface CompareModalProps {
  currentCompany: CompanyProfile;
  allCompanies: CompanyProfile[];
  onClose: () => void;
  onSelectCompany: (company: CompanyProfile) => void;
}

export const CompareModal: React.FC<CompareModalProps> = ({
  currentCompany,
  allCompanies,
  onClose,
}) => {
  const otherCompanies = allCompanies.filter(c => c.id !== currentCompany.id);
  const [selectedOtherId, setSelectedOtherId] = useState<string>(
    otherCompanies[0]?.id || ''
  );

  const targetCompany = allCompanies.find(c => c.id === selectedOtherId) || otherCompanies[0];

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
        maxWidth: '900px',
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '28px'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', marginBottom: '20px' }}>
          <div>
            <h2 style={{ fontSize: '20px', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '8px' }}>
              <ArrowRightLeft size={20} color="var(--brand-primary)" />
              Factual Company Comparison
            </h2>
            <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '2px' }}>
              Side-by-side corporate metric analysis without subjective ranking.
            </p>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
            <X size={22} />
          </button>
        </div>

        {/* Company Selector for Company B */}
        <div style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>Compare with:</span>
          <select
            value={selectedOtherId}
            onChange={(e) => setSelectedOtherId(e.target.value)}
            style={{
              padding: '8px 14px',
              borderRadius: '8px',
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              fontSize: '13px',
              fontWeight: 500
            }}
          >
            {otherCompanies.map(c => (
              <option key={c.id} value={c.id}>
                {c.legal_name} ({c.registered_state})
              </option>
            ))}
          </select>
        </div>

        {targetCompany && (
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th style={{ width: '28%' }}>Metric / Attribute</th>
                  <th style={{ width: '36%', color: 'var(--brand-primary)' }}>{currentCompany.legal_name}</th>
                  <th style={{ width: '36%', color: 'var(--emerald)' }}>{targetCompany.legal_name}</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td style={{ fontWeight: 600 }}>Status</td>
                  <td><span className="status-pill status-active">{currentCompany.company_status}</span></td>
                  <td><span className="status-pill status-active">{targetCompany.company_status}</span></td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600 }}>CIN</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{currentCompany.cin}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{targetCompany.cin}</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600 }}>Registered State</td>
                  <td>{currentCompany.registered_state}</td>
                  <td>{targetCompany.registered_state}</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600 }}>Incorporation Date</td>
                  <td>{currentCompany.incorporation_date || 'N/A'}</td>
                  <td>{targetCompany.incorporation_date || 'N/A'}</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600 }}>Company Class & Type</td>
                  <td>{currentCompany.company_type} ({currentCompany.company_class})</td>
                  <td>{targetCompany.company_type} ({targetCompany.company_class})</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600 }}>Authorized Capital</td>
                  <td style={{ fontWeight: 600 }}>{formatINR(currentCompany.authorized_capital)}</td>
                  <td style={{ fontWeight: 600 }}>{formatINR(targetCompany.authorized_capital)}</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600 }}>Paid-up Capital</td>
                  <td style={{ fontWeight: 600 }}>{formatINR(currentCompany.paid_up_capital)}</td>
                  <td style={{ fontWeight: 600 }}>{formatINR(targetCompany.paid_up_capital)}</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600 }}>GST Registrations</td>
                  <td>{currentCompany.gst_registrations.length} State Registrations</td>
                  <td>{targetCompany.gst_registrations.length} State Registrations</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600 }}>Directors on File</td>
                  <td>{currentCompany.directors.length} Directors</td>
                  <td>{targetCompany.directors.length} Directors</td>
                </tr>
                <tr>
                  <td style={{ fontWeight: 600 }}>Audited Statements Revenue</td>
                  <td>
                    {currentCompany.financials.status === 'AVAILABLE' && currentCompany.financials.financial_years[0]?.revenue
                      ? formatINR(currentCompany.financials.financial_years[0].revenue)
                      : <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Unavailable from connected sources</span>}
                  </td>
                  <td>
                    {targetCompany.financials.status === 'AVAILABLE' && targetCompany.financials.financial_years[0]?.revenue
                      ? formatINR(targetCompany.financials.financial_years[0].revenue)
                      : <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>Unavailable from connected sources</span>}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
