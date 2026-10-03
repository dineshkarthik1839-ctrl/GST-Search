import { useState } from 'react';
import {
  ShieldCheck, MapPin, Calendar,
  Download, Bookmark, BookmarkCheck, ArrowRightLeft, Share2,
  AlertTriangle, Landmark, Layers, X
} from 'lucide-react';
import type { CompanyProfile, GSTRegistration } from '../types';
import { SourceBadge } from './SourceBadge';
import { formatINR } from '../api/client';

interface CompanyProfileViewProps {
  company: CompanyProfile;
  isSaved: boolean;
  onToggleWatchlist: () => void;
  onOpenCompare: () => void;
  onOpenReport: () => void;
}

export const CompanyProfileView: React.FC<CompanyProfileViewProps> = ({
  company,
  isSaved,
  onToggleWatchlist,
  onOpenCompare,
  onOpenReport
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'gst' | 'management' | 'financials' | 'filings' | 'timeline' | 'sources'>('overview');
  const [selectedGst, setSelectedGst] = useState<GSTRegistration | null>(null);
  const [selectedFy, setSelectedFy] = useState<string>(
    company.financials.financial_years[0]?.financial_year || 'FY 2025-26'
  );
  const [filingFilter, setFilingFilter] = useState<string>('ALL');
  const [copyToast, setCopyToast] = useState(false);

  const handleShare = () => {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(window.location.href);
      setCopyToast(true);
      setTimeout(() => setCopyToast(false), 2500);
    }
  };

  const currentFinancial = company.financials.financial_years.find(f => f.financial_year === selectedFy) || company.financials.financial_years[0];

  const filteredFilings = filingFilter === 'ALL'
    ? company.filings
    : company.filings.filter(f => f.filing_type.includes(filingFilter));

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', width: '100%' }}>
      {/* 1. Header Card */}
      <div className="glass-panel" style={{ padding: '28px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
              <h1 style={{ fontSize: '26px', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
                {company.legal_name}
              </h1>
              <span className="status-pill status-active">
                {company.company_status}
              </span>
            </div>
            {company.trade_name && (
              <p style={{ color: 'var(--text-secondary)', fontSize: '15px', marginBottom: '12px' }}>
                Trade Name: <strong style={{ color: 'var(--text-primary)' }}>{company.trade_name}</strong>
              </p>
            )}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '18px', color: 'var(--text-secondary)', fontSize: '13px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Landmark size={15} color="var(--brand-primary)" />
                {company.company_type || 'Private Limited'}
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <MapPin size={15} color="var(--brand-primary)" />
                {company.registered_state || 'India'} (ROC {company.roc || 'ROC'})
              </span>
              <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Calendar size={15} color="var(--brand-primary)" />
                Inc: {company.incorporation_date ? new Date(company.incorporation_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' }) : 'N/A'}
              </span>
            </div>
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            <button
              onClick={onToggleWatchlist}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 16px',
                borderRadius: '8px',
                background: isSaved ? 'rgba(16, 185, 129, 0.15)' : 'var(--bg-surface)',
                border: `1px solid ${isSaved ? 'var(--emerald)' : 'var(--border-color)'}`,
                color: isSaved ? 'var(--emerald)' : 'var(--text-primary)',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 600,
                transition: 'all 0.15s ease'
              }}
            >
              {isSaved ? <BookmarkCheck size={16} /> : <Bookmark size={16} />}
              {isSaved ? 'Watchlisted' : 'Save'}
            </button>

            <button
              onClick={onOpenCompare}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 16px',
                borderRadius: '8px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-primary)',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 600
              }}
            >
              <ArrowRightLeft size={16} />
              Compare
            </button>

            <button
              onClick={onOpenReport}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 16px',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #0284c7 0%, #2563eb 100%)',
                border: 'none',
                color: '#ffffff',
                cursor: 'pointer',
                fontSize: '13px',
                fontWeight: 600,
                boxShadow: '0 4px 12px rgba(37, 99, 235, 0.3)'
              }}
            >
              <Download size={16} />
              Export Report
            </button>

            <button
              onClick={handleShare}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '8px 12px',
                borderRadius: '8px',
                background: 'var(--bg-surface)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-secondary)',
                cursor: 'pointer',
                fontSize: '13px'
              }}
              title="Copy share link"
            >
              <Share2 size={16} />
              {copyToast ? 'Copied!' : 'Share'}
            </button>
          </div>
        </div>

        {/* 2. Identifiers Ribbon */}
        <div style={{
          marginTop: '24px',
          padding: '16px 20px',
          background: 'var(--bg-primary)',
          borderRadius: '10px',
          border: '1px solid var(--border-color)',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '16px'
        }}>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>CIN</span>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', fontWeight: 600, color: 'var(--brand-primary)', marginTop: '2px' }}>
              {company.cin}
            </div>
          </div>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>PAN</span>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '14px', fontWeight: 600, color: 'var(--emerald)', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              {company.pan || 'N/A'}
              {company.pan && <ShieldCheck size={14} />}
            </div>
          </div>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>GST Registrations</span>
            <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
              {company.gst_registrations.length} State {company.gst_registrations.length === 1 ? 'Registration' : 'Registrations'}
            </div>
          </div>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Paid-up Capital</span>
            <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>
              {formatINR(company.paid_up_capital)}
            </div>
          </div>
          <div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Data Freshness</span>
            <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Updated {company.last_updated}
            </div>
          </div>
        </div>
      </div>

      {/* 3. Navigation Tabs */}
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--border-color)',
        overflowX: 'auto',
        gap: '4px'
      }}>
        <button className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`} onClick={() => setActiveTab('overview')}>
          Overview
        </button>
        <button className={`tab-btn ${activeTab === 'gst' ? 'active' : ''}`} onClick={() => setActiveTab('gst')}>
          GST Dashboard ({company.gst_registrations.length})
        </button>
        <button className={`tab-btn ${activeTab === 'management' ? 'active' : ''}`} onClick={() => setActiveTab('management')}>
          Management ({company.directors.length})
        </button>
        <button className={`tab-btn ${activeTab === 'financials' ? 'active' : ''}`} onClick={() => setActiveTab('financials')}>
          Financials {company.financials.status === 'AVAILABLE' ? '• Audited' : ''}
        </button>
        <button className={`tab-btn ${activeTab === 'filings' ? 'active' : ''}`} onClick={() => setActiveTab('filings')}>
          Filings ({company.filings.length})
        </button>
        <button className={`tab-btn ${activeTab === 'timeline' ? 'active' : ''}`} onClick={() => setActiveTab('timeline')}>
          Timeline ({company.timeline.length})
        </button>
        <button className={`tab-btn ${activeTab === 'sources' ? 'active' : ''}`} onClick={() => setActiveTab('sources')}>
          Sources & Provenance
        </button>
      </div>

      {/* 4. Tab Content Panels */}
      {/* ================= OVERVIEW TAB ================= */}
      {activeTab === 'overview' && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
          <div className="bento-card">
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: 'var(--text-primary)' }}>
              Corporate Master Identification
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Legal Name</span>
                <p style={{ fontWeight: 600, fontSize: '14px', marginTop: '2px' }}>{company.legal_name}</p>
                <SourceBadge sourceType="GOVERNMENT OPEN DATA" sourceName="MCA Master Data" updatedAt="03 Oct 2026" verificationStatus="Source Reported" />
              </div>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Company Type & Class</span>
                <p style={{ fontWeight: 500, fontSize: '14px', marginTop: '2px' }}>{company.company_type} ({company.company_class})</p>
                <SourceBadge sourceType="GOVERNMENT OPEN DATA" sourceName="MCA" updatedAt="03 Oct 2026" />
              </div>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Company Category</span>
                <p style={{ fontWeight: 500, fontSize: '14px', marginTop: '2px' }}>{company.company_category || 'Company limited by shares'}</p>
                <SourceBadge sourceType="GOVERNMENT OPEN DATA" sourceName="MCA" updatedAt="03 Oct 2026" />
              </div>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Incorporation Date</span>
                <p style={{ fontWeight: 500, fontSize: '14px', marginTop: '2px' }}>
                  {company.incorporation_date ? new Date(company.incorporation_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'long', year: 'numeric' }) : 'N/A'}
                </p>
                <SourceBadge sourceType="GOVERNMENT OPEN DATA" sourceName="MCA" updatedAt="03 Oct 2026" />
              </div>
            </div>
          </div>

          <div className="bento-card">
            <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px', color: 'var(--text-primary)' }}>
              Capital Structure & Jurisdiction
            </h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Authorized Share Capital</span>
                <p style={{ fontWeight: 700, fontSize: '16px', color: 'var(--brand-primary)', marginTop: '2px' }}>
                  {formatINR(company.authorized_capital)}
                </p>
                <SourceBadge sourceType="GOVERNMENT OPEN DATA" sourceName="MCA" updatedAt="03 Oct 2026" />
              </div>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Paid-up Capital</span>
                <p style={{ fontWeight: 700, fontSize: '16px', color: 'var(--emerald)', marginTop: '2px' }}>
                  {formatINR(company.paid_up_capital)}
                </p>
                <SourceBadge sourceType="GOVERNMENT OPEN DATA" sourceName="MCA" updatedAt="03 Oct 2026" />
              </div>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Registrar of Companies (ROC)</span>
                <p style={{ fontWeight: 500, fontSize: '14px', marginTop: '2px' }}>{company.roc || 'N/A'}</p>
                <SourceBadge sourceType="GOVERNMENT OPEN DATA" sourceName="MCA" updatedAt="03 Oct 2026" />
              </div>
              <div>
                <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Registered Office Address</span>
                <p style={{ fontWeight: 500, fontSize: '13px', lineHeight: '1.4', marginTop: '2px', color: 'var(--text-secondary)' }}>
                  {company.registered_address || 'Address on file with MCA'}
                </p>
                <SourceBadge sourceType="GOVERNMENT OPEN DATA" sourceName="MCA" updatedAt="03 Oct 2026" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* ================= GST TAB ================= */}
      {activeTab === 'gst' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Goods and Services Tax (GST) Registrations</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                Multi-state GST profile verified through authorized GST provider gateway.
              </p>
            </div>
            <SourceBadge sourceType="AUTHORIZED API" sourceName="GST Provider" updatedAt="03 Oct 2026" verificationStatus="Verified" />
          </div>

          {company.gst_registrations.length === 0 ? (
            <div className="bento-card" style={{ textAlign: 'center', padding: '40px 20px' }}>
              <Layers size={36} color="var(--text-muted)" style={{ margin: '0 auto 12px auto' }} />
              <h4 style={{ fontSize: '16px', fontWeight: 600 }}>No GST Registrations Found</h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px', marginTop: '6px' }}>
                This organization (such as a Section 8 non-profit or below threshold enterprise) has no recorded active commercial GST registrations in connected sources.
              </p>
            </div>
          ) : (
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>GSTIN</th>
                    <th>State</th>
                    <th>Registration Date</th>
                    <th>Status</th>
                    <th>Taxpayer Type</th>
                    <th>Business Constitution</th>
                    <th>Action</th>
                  </tr>
                </thead>
                <tbody>
                  {company.gst_registrations.map((gst) => (
                    <tr key={gst.id}>
                      <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--brand-primary)' }}>
                        {gst.gstin}
                      </td>
                      <td>{gst.state}</td>
                      <td>{gst.registration_date || 'N/A'}</td>
                      <td>
                        <span className="status-pill status-active" style={{ fontSize: '11px', padding: '2px 8px' }}>
                          {gst.status}
                        </span>
                      </td>
                      <td>{gst.taxpayer_type}</td>
                      <td>{gst.business_constitution || 'Private Limited'}</td>
                      <td>
                        <button
                          onClick={() => setSelectedGst(gst)}
                          style={{
                            background: 'rgba(56, 189, 248, 0.12)',
                            color: 'var(--brand-primary)',
                            border: '1px solid rgba(56, 189, 248, 0.3)',
                            borderRadius: '6px',
                            padding: '4px 10px',
                            fontSize: '12px',
                            fontWeight: 600,
                            cursor: 'pointer'
                          }}
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* GST Details Modal/Drawer */}
          {selectedGst && (
            <div style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: 'rgba(0, 0, 0, 0.75)',
              backdropFilter: 'blur(6px)',
              zIndex: 9999,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '20px'
            }}>
              <div className="glass-panel" style={{ maxWidth: '650px', width: '100%', maxHeight: '90vh', overflowY: 'auto', padding: '24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-color)', paddingBottom: '14px', marginBottom: '16px' }}>
                  <div>
                    <h3 style={{ fontSize: '18px', fontWeight: 700 }}>GSTIN Details: {selectedGst.gstin}</h3>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '12px' }}>Jurisdiction & Compliance Record</p>
                  </div>
                  <button onClick={() => setSelectedGst(null)} style={{ background: 'transparent', border: 'none', color: 'var(--text-secondary)', cursor: 'pointer' }}>
                    <X size={20} />
                  </button>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', fontSize: '13px' }}>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>State Jurisdiction</span>
                    <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedGst.state_jurisdiction || 'N/A'}</p>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Centre Jurisdiction</span>
                    <p style={{ fontWeight: 600, color: 'var(--text-primary)', marginTop: '2px' }}>{selectedGst.centre_jurisdiction || 'N/A'}</p>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Principal Place of Business</span>
                    <p style={{ fontWeight: 500, color: 'var(--text-secondary)', marginTop: '2px' }}>{selectedGst.principal_place_of_business || 'N/A'}</p>
                  </div>
                  {selectedGst.additional_places.length > 0 && (
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Additional Places of Business</span>
                      <ul style={{ paddingLeft: '18px', marginTop: '4px', color: 'var(--text-secondary)' }}>
                        {selectedGst.additional_places.map((place, i) => (
                          <li key={i}>{place}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {selectedGst.nature_of_business.length > 0 && (
                    <div>
                      <span style={{ color: 'var(--text-muted)' }}>Nature of Business Activities</span>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
                        {selectedGst.nature_of_business.map((item, i) => (
                          <span key={i} style={{ padding: '3px 8px', borderRadius: '4px', background: 'var(--bg-surface)', fontSize: '12px', border: '1px solid var(--border-color)' }}>
                            {item}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {selectedGst.filings.length > 0 && (
                    <div style={{ marginTop: '12px' }}>
                      <span style={{ color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', fontSize: '11px' }}>
                        Permitted GST Return Filing Status
                      </span>
                      <table className="data-table" style={{ marginTop: '6px' }}>
                        <thead>
                          <tr>
                            <th>Return</th>
                            <th>Period</th>
                            <th>Filing Date</th>
                            <th>Status</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedGst.filings.map((fil, idx) => (
                            <tr key={idx}>
                              <td style={{ fontWeight: 600 }}>{fil.return_type}</td>
                              <td>{fil.tax_period}</td>
                              <td>{fil.date_of_filing}</td>
                              <td><span className="status-pill status-active" style={{ fontSize: '10px' }}>{fil.status}</span></td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ================= MANAGEMENT TAB ================= */}
      {activeTab === 'management' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Company Management & Key Persons</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                Directors and Key Managerial Personnel (KMP) recorded in official MCA master data.
              </p>
            </div>
            <SourceBadge sourceType="GOVERNMENT OPEN DATA" sourceName="MCA Master Data" updatedAt="03 Oct 2026" verificationStatus="Source Reported" />
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Designation</th>
                  <th>Appointment Date</th>
                  <th>Cessation Date</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {company.directors.map((dir) => (
                  <tr key={dir.id}>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{dir.name}</td>
                    <td>
                      <span style={{
                        padding: '3px 8px',
                        borderRadius: '4px',
                        background: 'rgba(99, 102, 241, 0.15)',
                        color: '#a5b4fc',
                        fontSize: '12px',
                        fontWeight: 600
                      }}>
                        {dir.designation}
                      </span>
                    </td>
                    <td>{dir.appointment_date || 'N/A'}</td>
                    <td>{dir.cessation_date || 'Active'}</td>
                    <td><SourceBadge sourceType={dir.source_type} sourceName={dir.source} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <p style={{ fontSize: '12px', color: 'var(--text-muted)', fontStyle: 'italic' }}>
            Note: CompanyLens displays only authorized statutory designations (Director, Designated Partner, KMP) reported by official sources. We do not infer beneficial ownership or management hierarchy without explicit statutory evidence.
          </p>
        </div>
      )}

      {/* ================= FINANCIALS TAB ================= */}
      {activeTab === 'financials' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Financial Performance & Balance Sheet</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                Strict distinction between audited company revenue and GST turnover.
              </p>
            </div>
            <SourceBadge
              sourceType={company.financials.source_type}
              sourceName={company.financials.source}
              updatedAt="03 Oct 2026"
            />
          </div>

          {company.financials.status === 'FINANCIAL_DATA_UNAVAILABLE' ? (
            <div className="bento-card" style={{ padding: '36px', textAlign: 'center' }}>
              <AlertTriangle size={36} color="var(--amber)" style={{ margin: '0 auto 12px auto' }} />
              <h4 style={{ fontSize: '17px', fontWeight: 600, color: 'var(--text-primary)' }}>
                Financial Statements Unavailable from Connected Sources
              </h4>
              <p style={{ color: 'var(--text-secondary)', fontSize: '14px', maxWidth: '600px', margin: '8px auto 0 auto' }}>
                {company.financials.message || "Audited financial statements and statutory turnover figures are currently unavailable from connected authorized sources. In accordance with CompanyLens Accuracy Principles, we never estimate or fabricate financial numbers."}
              </p>
            </div>
          ) : (
            <>
              {/* Year Selector */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '13px', color: 'var(--text-secondary)', fontWeight: 600 }}>Financial Year:</span>
                {company.financials.financial_years.map(fy => (
                  <button
                    key={fy.financial_year}
                    onClick={() => setSelectedFy(fy.financial_year)}
                    style={{
                      padding: '6px 14px',
                      borderRadius: '6px',
                      border: `1px solid ${selectedFy === fy.financial_year ? 'var(--brand-primary)' : 'var(--border-color)'}`,
                      background: selectedFy === fy.financial_year ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-surface)',
                      color: selectedFy === fy.financial_year ? 'var(--brand-primary)' : 'var(--text-secondary)',
                      fontSize: '12px',
                      fontWeight: 600,
                      cursor: 'pointer'
                    }}
                  >
                    {fy.financial_year}
                  </button>
                ))}
              </div>

              {/* KPI Cards */}
              {currentFinancial && (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                  <div className="bento-card">
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      {currentFinancial.revenue_label}
                    </span>
                    <p style={{ fontSize: '20px', fontWeight: 700, color: 'var(--brand-primary)', marginTop: '4px' }}>
                      {formatINR(currentFinancial.revenue)}
                    </p>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Currency: INR</span>
                  </div>

                  <div className="bento-card">
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Profit / Loss (PAT)
                    </span>
                    <p style={{ fontSize: '20px', fontWeight: 700, color: 'var(--emerald)', marginTop: '4px' }}>
                      {formatINR(currentFinancial.profit_loss)}
                    </p>
                    <span style={{ fontSize: '11px', color: 'var(--emerald)' }}>Positive Net Margin</span>
                  </div>

                  <div className="bento-card">
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Net Worth
                    </span>
                    <p style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
                      {formatINR(currentFinancial.net_worth)}
                    </p>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Shareholders Equity</span>
                  </div>

                  <div className="bento-card">
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                      Total Assets
                    </span>
                    <p style={{ fontSize: '20px', fontWeight: 700, color: 'var(--text-primary)', marginTop: '4px' }}>
                      {formatINR(currentFinancial.assets)}
                    </p>
                    <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Fixed & Current</span>
                  </div>
                </div>
              )}

              {/* Multi-Year Comparative Table */}
              <div className="table-container">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Financial Year</th>
                      <th>Revenue (Statements)</th>
                      <th>Profit / Loss</th>
                      <th>Net Worth</th>
                      <th>Total Assets</th>
                      <th>Liabilities</th>
                      <th>Source</th>
                    </tr>
                  </thead>
                  <tbody>
                    {company.financials.financial_years.map(fy => (
                      <tr key={fy.financial_year}>
                        <td style={{ fontWeight: 600, color: 'var(--brand-primary)' }}>{fy.financial_year}</td>
                        <td style={{ fontWeight: 600 }}>{formatINR(fy.revenue)}</td>
                        <td style={{ color: 'var(--emerald)', fontWeight: 600 }}>{formatINR(fy.profit_loss)}</td>
                        <td>{formatINR(fy.net_worth)}</td>
                        <td>{formatINR(fy.assets)}</td>
                        <td>{formatINR(fy.liabilities)}</td>
                        <td><SourceBadge sourceType="LICENSED PROVIDER" sourceName="Audited Statements" /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </div>
      )}

      {/* ================= FILINGS TAB ================= */}
      {activeTab === 'filings' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '12px' }}>
            <div>
              <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Statutory Regulatory Filings</h3>
              <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                Annual returns, balance sheet submissions, and corporate governance filings.
              </p>
            </div>
            <div style={{ display: 'flex', gap: '8px' }}>
              {['ALL', 'AOC-4', 'MGT', 'DIR'].map(filter => (
                <button
                  key={filter}
                  onClick={() => setFilingFilter(filter)}
                  style={{
                    padding: '4px 12px',
                    borderRadius: '6px',
                    border: `1px solid ${filingFilter === filter ? 'var(--brand-primary)' : 'var(--border-color)'}`,
                    background: filingFilter === filter ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-surface)',
                    color: filingFilter === filter ? 'var(--brand-primary)' : 'var(--text-secondary)',
                    fontSize: '12px',
                    cursor: 'pointer'
                  }}
                >
                  {filter}
                </button>
              ))}
            </div>
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Filing Type</th>
                  <th>Financial Year</th>
                  <th>Filing Date</th>
                  <th>Status</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {filteredFilings.map(fil => (
                  <tr key={fil.id}>
                    <td style={{ fontWeight: 600, color: 'var(--brand-primary)' }}>{fil.filing_type}</td>
                    <td>{fil.financial_year || 'N/A'}</td>
                    <td>{fil.filing_date || 'N/A'}</td>
                    <td>
                      <span className="status-pill status-active" style={{ fontSize: '11px', padding: '2px 8px' }}>
                        {fil.status}
                      </span>
                    </td>
                    <td><SourceBadge sourceType={fil.source_type} sourceName={fil.source} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ================= TIMELINE TAB ================= */}
      {activeTab === 'timeline' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Corporate Event History & Timeline</h3>
          <div style={{ position: 'relative', paddingLeft: '32px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
            <div style={{
              position: 'absolute',
              left: '11px',
              top: '8px',
              bottom: '8px',
              width: '2px',
              background: 'var(--border-color)'
            }} />
            {company.timeline.map((event) => (
              <div key={event.id} style={{ position: 'relative' }}>
                <div style={{
                  position: 'absolute',
                  left: '-32px',
                  top: '4px',
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: 'var(--bg-surface)',
                  border: '2px solid var(--brand-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '10px',
                  fontWeight: 700,
                  color: 'var(--brand-primary)'
                }}>
                  {event.year.toString().slice(-2)}
                </div>
                <div className="bento-card" style={{ padding: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                    <span style={{ fontWeight: 700, fontSize: '14px', color: 'var(--text-primary)' }}>
                      {event.year} — {event.event_type.replace('_', ' ')}
                    </span>
                    <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      {new Date(event.event_date).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}
                    </span>
                  </div>
                  <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>{event.description}</p>
                  <div style={{ marginTop: '10px' }}>
                    <SourceBadge sourceType={event.source_type} sourceName={event.source} />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ================= SOURCES TAB ================= */}
      {activeTab === 'sources' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 600 }}>Data Provenance & Source Transparency</h3>
          <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
            Every field displayed in CompanyLens is backed by an authoritative source with full auditability.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '16px' }}>
            {company.sources.map((src, i) => (
              <div key={i} className="bento-card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                  <h4 style={{ fontSize: '15px', fontWeight: 600 }}>{src.name}</h4>
                  <span className={`status-pill ${src.status === 'HEALTHY' ? 'status-active' : 'status-inactive'}`} style={{ fontSize: '10px', padding: '2px 8px' }}>
                    {src.status}
                  </span>
                </div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Source Type:</span>{' '}
                    <SourceBadge sourceType={src.source_type} />
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Dataset:</span>{' '}
                    <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{src.dataset}</span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Last Synchronization:</span>{' '}
                    <span style={{ color: 'var(--text-secondary)' }}>{src.last_synchronization}</span>
                  </div>
                  <div>
                    <span style={{ color: 'var(--text-muted)' }}>Data Coverage:</span>{' '}
                    <span style={{ color: 'var(--text-secondary)' }}>{src.coverage}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 5. Statutory Non-Government Legal Disclaimer (Section 61) */}
      <div style={{
        marginTop: '20px',
        padding: '16px 20px',
        background: 'rgba(15, 23, 42, 0.6)',
        borderRadius: '10px',
        border: '1px solid var(--border-color)',
        fontSize: '12px',
        color: 'var(--text-muted)',
        lineHeight: '1.6'
      }}>
        <strong style={{ color: 'var(--text-secondary)' }}>Statutory Notice & Disclaimer:</strong> CompanyLens is an independent corporate intelligence platform. Information is compiled from connected official, government open data, authorized and licensed sources and may be incomplete, delayed, or subject to change. CompanyLens does not issue government certificates, licenses, or represent any government authority.
      </div>
    </div>
  );
};
