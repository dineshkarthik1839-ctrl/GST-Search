import React, { useState } from 'react';
import { ShieldCheck, Lock, AlertTriangle, X } from 'lucide-react';

interface LegalModalProps {
  initialTab?: 'privacy' | 'terms' | 'sources' | 'disclaimer';
  onClose: () => void;
}

export const LegalModal: React.FC<LegalModalProps> = ({ initialTab = 'disclaimer', onClose }) => {
  const [tab, setTab] = useState<'privacy' | 'terms' | 'sources' | 'disclaimer'>(initialTab);

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
        maxWidth: '800px',
        width: '100%',
        maxHeight: '90vh',
        overflowY: 'auto',
        padding: '28px'
      }}>
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '16px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={22} color="var(--brand-primary)" />
            <h2 style={{ fontSize: '20px', fontWeight: 700 }}>Legal & Transparency Disclosures</h2>
          </div>
          <button onClick={onClose} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
            <X size={22} />
          </button>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', gap: '8px', marginBottom: '20px' }}>
          <button className={`tab-btn ${tab === 'disclaimer' ? 'active' : ''}`} onClick={() => setTab('disclaimer')}>
            Disclaimer
          </button>
          <button className={`tab-btn ${tab === 'sources' ? 'active' : ''}`} onClick={() => setTab('sources')}>
            Data Sources
          </button>
          <button className={`tab-btn ${tab === 'privacy' ? 'active' : ''}`} onClick={() => setTab('privacy')}>
            Privacy & PAN Security
          </button>
          <button className={`tab-btn ${tab === 'terms' ? 'active' : ''}`} onClick={() => setTab('terms')}>
            Terms of Use
          </button>
        </div>

        {/* Content */}
        <div style={{ fontSize: '13px', lineHeight: 1.7, color: 'var(--text-secondary)' }}>
          {tab === 'disclaimer' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--amber)', fontWeight: 600, fontSize: '15px' }}>
                <AlertTriangle size={18} />
                Statutory Non-Government Entity Disclaimer
              </div>
              <p>
                <strong>CompanyLens</strong> is an independent commercial B2B corporate intelligence platform operated for corporate due diligence, vendor verification, and KYC analysis.
              </p>
              <p>
                CompanyLens is NOT affiliated with, authorized by, sponsored by, or an agent of the Ministry of Corporate Affairs (MCA), the Goods and Services Tax Network (GSTN), the Central Board of Direct Taxes (CBDT), or any department of the Government of India or State Governments.
              </p>
              <p>
                Information displayed on CompanyLens is retrieved algorithmically from public Open Government Data (data.gov.in), authorized GST service providers (GSPs), and licensed financial data vendors. CompanyLens does not issue government certificates, registrations, or legally binding statutory certificates.
              </p>
            </div>
          )}

          {tab === 'sources' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)' }}>Authoritative Data Ecosystem</h3>
              <p>
                CompanyLens complies strictly with Section 3 data collection standards. <strong>We do not scrape government web portals</strong>, bypass CAPTCHAs, or circumvent rate limits.
              </p>
              <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <li>
                  <strong style={{ color: 'var(--text-primary)' }}>MCA Master Data:</strong> Ingested through India's Open Government Data (OGD) platform and official gazette releases. Covers CIN, legal entity status, authorized/paid-up capital, ROC, and director appointments.
                </li>
                <li>
                  <strong style={{ color: 'var(--text-primary)' }}>GST Ecosystem:</strong> Connected via authorized GST Suvidha Providers (GSPs) and authorized APIs. Verifies multi-state GSTINs, legal/trade names, taxpayer constitution, and permitted return filing statuses.
                </li>
                <li>
                  <strong style={{ color: 'var(--text-primary)' }}>PAN Verification:</strong> Handled through approved verification agency gateways. Used solely to confirm organizational corporate identity without accessing private personal tax records.
                </li>
                <li>
                  <strong style={{ color: 'var(--text-primary)' }}>Financial Statements:</strong> Integrated via licensed financial data providers. Sourced strictly from audited filings. We never fabricate turnover or present unofficial estimates.
                </li>
              </ul>
            </div>
          )}

          {tab === 'privacy' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--emerald)', fontWeight: 600, fontSize: '15px' }}>
                <Lock size={18} />
                PAN Security & Data Minimization Policy
              </div>
              <p>
                In strict adherence to Section 13, 22, and 39 of the CompanyLens Security Architecture:
              </p>
              <ul style={{ paddingLeft: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <li>Raw PANs are never placed into application URLs, analytics telemetry, client-side browser console logs, or unencrypted error messages.</li>
                <li>All internal entity matching operates using salted one-way SHA-256 cryptographic hashes.</li>
                <li>PAN display in the user interface is strictly masked (e.g. <code>ABCDE****F</code>) to prevent unauthorized visual capture.</li>
                <li>Entering a PAN will never retrieve personal Income Tax Returns (ITR). CompanyLens only validates organization-level statutory existence.</li>
              </ul>
            </div>
          )}

          {tab === 'terms' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text-primary)' }}>Terms of Service</h3>
              <p>
                By using CompanyLens, you agree to utilize corporate intelligence data solely for lawful business-to-business due diligence, compliance verification, and vendor evaluation.
              </p>
              <p>
                Automated querying outside of authorized API rate limits (10 searches/min anonymous, 30 searches/min authenticated) is strictly monitored and automatically throttled.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
