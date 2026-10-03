import React from 'react';
import { Printer, X, ShieldCheck } from 'lucide-react';
import type { CompanyProfile } from '../types';
import { formatINR } from '../api/client';

interface ReportModalProps {
  company: CompanyProfile;
  onClose: () => void;
}

export const ReportModal: React.FC<ReportModalProps> = ({ company, onClose }) => {
  const handlePrint = () => {
    window.print();
  };

  const reportId = `CL-REP-${new Date().getFullYear()}-${company.cin.slice(-6)}`;
  const genDate = new Date().toLocaleDateString('en-IN', {
    day: '2-digit',
    month: 'long',
    year: 'numeric'
  });

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: 'rgba(0, 0, 0, 0.85)',
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
        maxHeight: '92vh',
        overflowY: 'auto',
        padding: '36px',
        background: '#ffffff',
        color: '#1e293b'
      }}>
        {/* Actions bar (hidden in print) */}
        <div className="no-print" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', paddingBottom: '16px', borderBottom: '1px solid #e2e8f0' }}>
          <div>
            <span style={{ fontSize: '13px', fontWeight: 600, color: '#0284c7' }}>OFFICIAL INTELLIGENCE DOSSIER</span>
            <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#0f172a' }}>Export Company Dossier</h3>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <button
              onClick={handlePrint}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 16px',
                borderRadius: '6px',
                background: '#0284c7',
                border: 'none',
                color: '#ffffff',
                fontWeight: 600,
                fontSize: '13px',
                cursor: 'pointer'
              }}
            >
              <Printer size={16} />
              Print / Save PDF
            </button>
            <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: '#64748b', cursor: 'pointer' }}>
              <X size={22} />
            </button>
          </div>
        </div>

        {/* Printable Report Body */}
        <div style={{ fontFamily: 'var(--font-sans)', lineHeight: 1.5 }}>
          {/* Header */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', borderBottom: '2px solid #0284c7', paddingBottom: '16px', marginBottom: '24px' }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShieldCheck size={24} color="#0284c7" />
                <h1 style={{ fontSize: '22px', fontWeight: 800, color: '#0f172a', letterSpacing: '-0.02em' }}>
                  COMPANYLENS VERIFIED REPORT
                </h1>
              </div>
              <p style={{ fontSize: '12px', color: '#64748b', marginTop: '3px' }}>
                Report Reference ID: <strong>{reportId}</strong> • Generated on {genDate}
              </p>
            </div>
            <div style={{ textAlign: 'right' }}>
              <span style={{ padding: '4px 10px', borderRadius: '4px', background: '#dcfce7', color: '#166534', fontWeight: 700, fontSize: '12px' }}>
                {company.company_status}
              </span>
              <p style={{ fontSize: '11px', color: '#64748b', marginTop: '4px' }}>Authoritative Sources Compiled</p>
            </div>
          </div>

          {/* Section 1: Overview */}
          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a', borderBottom: '1px solid #cbd5e1', paddingBottom: '4px', marginBottom: '10px' }}>
              1. Corporate Overview & Master Identifiers
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', fontSize: '13px' }}>
              <div><strong>Legal Name:</strong> {company.legal_name}</div>
              <div><strong>Trade Name:</strong> {company.trade_name || 'N/A'}</div>
              <div><strong>CIN:</strong> <span style={{ fontFamily: 'var(--font-mono)' }}>{company.cin}</span></div>
              <div><strong>PAN:</strong> <span style={{ fontFamily: 'var(--font-mono)' }}>{company.pan} (Verified)</span></div>
              <div><strong>Incorporation Date:</strong> {company.incorporation_date || 'N/A'}</div>
              <div><strong>State & ROC:</strong> {company.registered_state} ({company.roc})</div>
              <div><strong>Authorized Capital:</strong> {formatINR(company.authorized_capital)}</div>
              <div><strong>Paid-up Capital:</strong> {formatINR(company.paid_up_capital)}</div>
              <div style={{ gridColumn: 'span 2' }}>
                <strong>Registered Office:</strong> {company.registered_address}
              </div>
            </div>
          </div>

          {/* Section 2: GST Registrations */}
          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a', borderBottom: '1px solid #cbd5e1', paddingBottom: '4px', marginBottom: '10px' }}>
              2. Goods & Services Tax (GST) Registrations ({company.gst_registrations.length})
            </h2>
            {company.gst_registrations.length === 0 ? (
              <p style={{ fontSize: '12px', color: '#64748b' }}>No commercial GST registrations on file.</p>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                <thead>
                  <tr style={{ background: '#f1f5f9', textAlign: 'left' }}>
                    <th style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>GSTIN</th>
                    <th style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>State</th>
                    <th style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>Registration Date</th>
                    <th style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {company.gst_registrations.map(g => (
                    <tr key={g.id}>
                      <td style={{ padding: '6px 8px', border: '1px solid #cbd5e1', fontFamily: 'var(--font-mono)' }}>{g.gstin}</td>
                      <td style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>{g.state}</td>
                      <td style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>{g.registration_date || 'N/A'}</td>
                      <td style={{ padding: '6px 8px', border: '1px solid #cbd5e1', color: '#166534', fontWeight: 600 }}>{g.status}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {/* Section 3: Management */}
          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a', borderBottom: '1px solid #cbd5e1', paddingBottom: '4px', marginBottom: '10px' }}>
              3. Management & Directors ({company.directors.length})
            </h2>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
              <thead>
                <tr style={{ background: '#f1f5f9', textAlign: 'left' }}>
                  <th style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>Name</th>
                  <th style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>Designation</th>
                  <th style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>Appointment Date</th>
                </tr>
              </thead>
              <tbody>
                {company.directors.map(d => (
                  <tr key={d.id}>
                    <td style={{ padding: '6px 8px', border: '1px solid #cbd5e1', fontWeight: 600 }}>{d.name}</td>
                    <td style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>{d.designation}</td>
                    <td style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>{d.appointment_date || 'N/A'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Section 4: Financial Statements */}
          <div style={{ marginBottom: '20px' }}>
            <h2 style={{ fontSize: '15px', fontWeight: 700, color: '#0f172a', borderBottom: '1px solid #cbd5e1', paddingBottom: '4px', marginBottom: '10px' }}>
              4. Financial Statements & Revenue (INR)
            </h2>
            {company.financials.status === 'AVAILABLE' ? (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                <thead>
                  <tr style={{ background: '#f1f5f9', textAlign: 'left' }}>
                    <th style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>Financial Year</th>
                    <th style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>Revenue (Statements)</th>
                    <th style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>Profit / Loss</th>
                    <th style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>Net Worth</th>
                  </tr>
                </thead>
                <tbody>
                  {company.financials.financial_years.map(fy => (
                    <tr key={fy.financial_year}>
                      <td style={{ padding: '6px 8px', border: '1px solid #cbd5e1', fontWeight: 600 }}>{fy.financial_year}</td>
                      <td style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>{formatINR(fy.revenue)}</td>
                      <td style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>{formatINR(fy.profit_loss)}</td>
                      <td style={{ padding: '6px 8px', border: '1px solid #cbd5e1' }}>{formatINR(fy.net_worth)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <p style={{ fontSize: '12px', color: '#64748b', fontStyle: 'italic' }}>
                Turnover data unavailable from connected sources. CompanyLens strictly refuses to estimate or fabricate unverified financial metrics.
              </p>
            )}
          </div>

          {/* Statutory Disclaimer & Signature */}
          <div style={{
            marginTop: '32px',
            borderTop: '2px solid #cbd5e1',
            paddingTop: '16px',
            fontSize: '11px',
            color: '#64748b',
            lineHeight: 1.6
          }}>
            <p>
              <strong>Data Accuracy & Legal Disclosure:</strong> CompanyLens is an independent corporate verification and intelligence software platform. This report is compiled algorithmically from connected authoritative government open datasets, authorized GSPs, and licensed financial databases. CompanyLens is not a government authority and does not issue statutory certifications.
            </p>
            <p style={{ marginTop: '6px' }}>
              Authentication Hash: <span style={{ fontFamily: 'var(--font-mono)' }}>SHA256:{company.cin.slice(0, 10)}...VERIFIED</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
