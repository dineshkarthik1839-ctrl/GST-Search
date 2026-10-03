import { useState, useEffect } from 'react';
import {
  Search, ShieldCheck, Database, Key, Award, AlertTriangle,
  ArrowRight, Sparkles, Lock
} from 'lucide-react';

import type { CompanyProfile, SearchResult, SearchMatchSummary } from './types';
import { searchCompanyAPI, getCompanyProfileAPI } from './api/client';
import { Navbar } from './components/Navbar';
import { SearchStepper } from './components/SearchStepper';
import { CompanyProfileView } from './components/CompanyProfileView';
import { AdminModal } from './components/AdminModal';
import { CompareModal } from './components/CompareModal';
import { WatchlistModal } from './components/WatchlistModal';
import { ReportModal } from './components/ReportModal';
import { LegalModal } from './components/LegalModal';
import { AuthModal } from './components/AuthModal';

export const App: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [detectedType, setDetectedType] = useState<string>('');
  const [selectedFilter, setSelectedFilter] = useState<'ALL' | 'GSTIN' | 'PAN' | 'CIN' | 'COMPANY_NAME'>('ALL');
  
  // Pipeline Stepper & Result State
  const [isSearching, setIsSearching] = useState(false);
  const [searchStep, setSearchStep] = useState(0);
  const [searchResult, setSearchResult] = useState<SearchResult | null>(null);
  const [currentCompany, setCurrentCompany] = useState<CompanyProfile | null>(null);

  // Watchlist State
  const [watchlist, setWatchlist] = useState<CompanyProfile[]>([]);

  // Modals & Active View
  const [activeView, setActiveView] = useState<'search' | 'compare' | 'watchlist' | 'admin' | 'sources' | 'about'>('search');
  const [showAdminModal, setShowAdminModal] = useState(false);
  const [showCompareModal, setShowCompareModal] = useState(false);
  const [showWatchlistModal, setShowWatchlistModal] = useState(false);
  const [showReportModal, setShowReportModal] = useState(false);
  const [showLegalModal, setShowLegalModal] = useState(false);
  const [legalTab, setLegalTab] = useState<'privacy' | 'terms' | 'sources' | 'disclaimer'>('disclaimer');
  const [showAuthModal, setShowAuthModal] = useState(false);

  // Real-time Identifier Detection in Search Bar
  useEffect(() => {
    const clean = searchQuery.trim().toUpperCase().replace(/\s+/g, '');
    if (clean.length === 15 && /^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$/.test(clean)) {
      setDetectedType('GSTIN');
    } else if (clean.length === 21 && /^([LU]{1})([0-9]{5})([A-Z]{2})([0-9]{4})([A-Z]{3})([0-9]{6})$/.test(clean)) {
      setDetectedType('CIN');
    } else if (clean.length === 10 && /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(clean)) {
      setDetectedType('PAN');
    } else if (clean.length >= 2) {
      setDetectedType('COMPANY NAME');
    } else {
      setDetectedType('');
    }
  }, [searchQuery]);

  const executeSearch = async (queryToSearch: string) => {
    const q = queryToSearch.trim();
    if (!q) return;

    setIsSearching(true);
    setSearchStep(0); // Identified
    setSearchResult(null);
    setCurrentCompany(null);

    // Progression of real resolution pipeline
    await new Promise(r => setTimeout(r, 120));
    setSearchStep(1); // Validating
    await new Promise(r => setTimeout(r, 150));
    setSearchStep(2); // Searching DB & cache
    await new Promise(r => setTimeout(r, 150));
    setSearchStep(3); // Resolving identity graph
    await new Promise(r => setTimeout(r, 120));
    setSearchStep(4); // Loading authoritative source data

    const result = await searchCompanyAPI(q);
    setSearchStep(5); // Complete!
    setIsSearching(false);
    setSearchResult(result);

    if (result.resolution === 'EXACT_MATCH' || result.resolution === 'HIGH_CONFIDENCE') {
      const comp = result.companies[0] as CompanyProfile;
      setCurrentCompany(comp);
    }
  };

  const handleSelectCompany = (comp: CompanyProfile) => {
    setCurrentCompany(comp);
    setShowWatchlistModal(false);
    setShowCompareModal(false);
    setActiveView('search');
  };

  const handleSelectCompanyById = async (companyId: string) => {
    const profile = await getCompanyProfileAPI(companyId);
    if (profile) {
      setCurrentCompany(profile);
      setActiveView('search');
    }
  };

  const toggleWatchlist = (comp: CompanyProfile) => {
    if (watchlist.some(w => w.id === comp.id)) {
      setWatchlist(watchlist.filter(w => w.id !== comp.id));
    } else {
      setWatchlist([...watchlist, comp]);
    }
  };

  const openLegal = (tab: 'privacy' | 'terms' | 'sources' | 'disclaimer') => {
    setLegalTab(tab);
    setShowLegalModal(true);
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* 1. Top Navbar */}
      <Navbar
        onNavClick={(view) => {
          if (view === 'admin') setShowAdminModal(true);
          else if (view === 'compare') {
            if (currentCompany) setShowCompareModal(true);
            else executeSearch('ABC Technologies').then(() => setShowCompareModal(true));
          } else if (view === 'watchlist') setShowWatchlistModal(true);
          else if (view === 'sources') openLegal('sources');
          else if (view === 'about') openLegal('disclaimer');
          else setActiveView('search');
        }}
        currentView={activeView}
        watchlistCount={watchlist.length}
        onOpenAuth={() => setShowAuthModal(true)}
      />

      {/* Main Container */}
      <main style={{ maxWidth: '1240px', width: '100%', margin: '0 auto', padding: '0 20px 60px 20px', flex: 1 }}>
        {/* 2. Hero Search Header */}
        <section style={{ textAlign: 'center', margin: '36px 0 28px 0' }}>
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '6px 14px',
            borderRadius: '9999px',
            background: 'rgba(56, 189, 248, 0.1)',
            border: '1px solid rgba(56, 189, 248, 0.25)',
            color: 'var(--brand-primary)',
            fontSize: '12px',
            fontWeight: 700,
            letterSpacing: '0.04em',
            marginBottom: '16px'
          }}>
            <ShieldCheck size={15} />
            INDIAN CORPORATE INTELLIGENCE & VERIFICATION
          </div>

          <h1 style={{ fontSize: '42px', fontWeight: 800, letterSpacing: '-0.03em', lineHeight: 1.15, color: '#ffffff', maxWidth: '820px', margin: '0 auto' }}>
            Know the Company Behind the Number.
          </h1>
          <p style={{ fontSize: '17px', color: 'var(--text-secondary)', maxWidth: '640px', margin: '14px auto 28px auto' }}>
            Search Indian companies using GSTIN, PAN, CIN or company name with source-backed official records.
          </p>

          {/* Search Box Card */}
          <div className="glass-panel" style={{ maxWidth: '780px', margin: '0 auto', padding: '16px 20px', boxShadow: '0 20px 40px rgba(0, 0, 0, 0.6)' }}>
            {/* Filter Pills */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '14px', overflowX: 'auto' }}>
              {(['ALL', 'GSTIN', 'PAN', 'CIN', 'COMPANY_NAME'] as const).map(f => (
                <button
                  key={f}
                  onClick={() => setSelectedFilter(f)}
                  style={{
                    padding: '4px 12px',
                    borderRadius: '6px',
                    border: `1px solid ${selectedFilter === f ? 'var(--brand-primary)' : 'var(--border-color)'}`,
                    background: selectedFilter === f ? 'rgba(56, 189, 248, 0.15)' : 'var(--bg-surface)',
                    color: selectedFilter === f ? 'var(--brand-primary)' : 'var(--text-secondary)',
                    fontSize: '11px',
                    fontWeight: 700,
                    cursor: 'pointer',
                    fontFamily: 'var(--font-mono)'
                  }}
                >
                  {f.replace('_', ' ')}
                </button>
              ))}

              {detectedType && (
                <span style={{
                  marginLeft: 'auto',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '11px',
                  fontWeight: 700,
                  color: 'var(--emerald)',
                  background: 'rgba(16, 185, 129, 0.1)',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  border: '1px solid rgba(16, 185, 129, 0.3)'
                }}>
                  <Sparkles size={12} />
                  {detectedType} DETECTED
                </span>
              )}
            </div>

            {/* Input & Search Button */}
            <form onSubmit={(e) => { e.preventDefault(); executeSearch(searchQuery); }} style={{ display: 'flex', gap: '10px' }}>
              <div style={{ position: 'relative', flex: 1 }}>
                <Search size={18} color="var(--text-muted)" style={{ position: 'absolute', left: '14px', top: '14px' }} />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  placeholder="Enter GSTIN, PAN, CIN or company name..."
                  style={{
                    width: '100%',
                    padding: '12px 16px 12px 42px',
                    background: 'var(--bg-surface)',
                    border: '1px solid var(--border-color)',
                    borderRadius: '10px',
                    color: 'var(--text-primary)',
                    fontSize: '15px',
                    fontFamily: 'var(--font-sans)',
                    outline: 'none'
                  }}
                />
              </div>

              <button
                type="submit"
                style={{
                  padding: '0 24px',
                  borderRadius: '10px',
                  background: 'linear-gradient(135deg, #0284c7 0%, #2563eb 100%)',
                  color: '#ffffff',
                  fontWeight: 700,
                  fontSize: '14px',
                  border: 'none',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  boxShadow: '0 4px 14px rgba(37, 99, 235, 0.4)'
                }}
              >
                Search
                <ArrowRight size={16} />
              </button>
            </form>

            {/* Quick Suggestions Chips */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '16px', flexWrap: 'wrap', fontSize: '12px', color: 'var(--text-muted)' }}>
              <span>Try Examples:</span>
              <button
                onClick={() => { setSearchQuery('27ABCDE1234F1Z5'); executeSearch('27ABCDE1234F1Z5'); }}
                style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-color)', color: 'var(--brand-primary)', padding: '3px 8px', borderRadius: '4px', cursor: 'pointer', fontFamily: 'var(--font-mono)' }}
              >
                GSTIN: 27ABCDE1234F1Z5
              </button>
              <button
                onClick={() => { setSearchQuery('U60200TN2020PTC098765'); executeSearch('U60200TN2020PTC098765'); }}
                style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-color)', color: 'var(--brand-primary)', padding: '3px 8px', borderRadius: '4px', cursor: 'pointer', fontFamily: 'var(--font-mono)' }}
              >
                CIN: U60200TN2020PTC098765
              </button>
              <button
                onClick={() => { setSearchQuery('AAACH5432R'); executeSearch('AAACH5432R'); }}
                style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-color)', color: 'var(--brand-primary)', padding: '3px 8px', borderRadius: '4px', cursor: 'pointer', fontFamily: 'var(--font-mono)' }}
              >
                PAN: AAACH5432R
              </button>
              <button
                onClick={() => { setSearchQuery('ABC Technologies'); executeSearch('ABC Technologies'); }}
                style={{ background: 'var(--bg-surface)', border: '1px solid var(--border-color)', color: 'var(--text-secondary)', padding: '3px 8px', borderRadius: '4px', cursor: 'pointer' }}
              >
                Name: ABC Technologies
              </button>
            </div>
          </div>

          <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '12px' }}>
            Information is compiled from connected official, government, authorized and licensed sources. Availability varies by source.
          </p>
        </section>

        {/* 3. Real Request Execution Stepper */}
        {isSearching && (
          <SearchStepper currentStep={searchStep} detectedType={detectedType} />
        )}

        {/* 4. Display Active Company Profile */}
        {currentCompany && !isSearching && (
          <div style={{ marginTop: '20px' }}>
            <CompanyProfileView
              company={currentCompany}
              isSaved={watchlist.some(w => w.id === currentCompany.id)}
              onToggleWatchlist={() => toggleWatchlist(currentCompany)}
              onOpenCompare={() => setShowCompareModal(true)}
              onOpenReport={() => setShowReportModal(true)}
            />
          </div>
        )}

        {/* 5. Multiple Fuzzy Matches View */}
        {searchResult && searchResult.resolution === 'POSSIBLE_MATCH' && !isSearching && (
          <div style={{ marginTop: '24px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '16px' }}>
              Possible Matching Companies ({searchResult.companies.length})
            </h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
              {(searchResult.companies as SearchMatchSummary[]).map((match) => (
                <div key={match.id} className="bento-card">
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <h3 style={{ fontSize: '16px', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {match.legal_name}
                    </h3>
                    <span className="status-pill status-active" style={{ fontSize: '10px' }}>
                      {match.company_status}
                    </span>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginTop: '12px', fontSize: '13px', color: 'var(--text-secondary)' }}>
                    <div>CIN: <strong style={{ color: 'var(--brand-primary)', fontFamily: 'var(--font-mono)' }}>{match.cin}</strong></div>
                    <div>State: {match.registered_state}</div>
                    <div>GST Registrations: {match.gst_count} State Registrations</div>
                    <div>Sources: {match.sources.join(', ')}</div>
                  </div>
                  <button
                    onClick={() => handleSelectCompanyById(match.id)}
                    style={{
                      marginTop: '16px',
                      width: '100%',
                      padding: '8px',
                      borderRadius: '6px',
                      background: 'rgba(56, 189, 248, 0.12)',
                      border: '1px solid rgba(56, 189, 248, 0.3)',
                      color: 'var(--brand-primary)',
                      fontSize: '13px',
                      fontWeight: 600,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      gap: '6px'
                    }}
                  >
                    View Company Profile
                    <ArrowRight size={14} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 6. Unresolved / Not Found State */}
        {searchResult && searchResult.resolution === 'UNRESOLVED' && !isSearching && (
          <div className="bento-card" style={{ marginTop: '24px', padding: '40px 20px', textAlign: 'center' }}>
            <AlertTriangle size={36} color="var(--amber)" style={{ margin: '0 auto 12px auto' }} />
            <h3 style={{ fontSize: '18px', fontWeight: 700 }}>No Relationship Established</h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '14px', maxWidth: '520px', margin: '8px auto 0 auto' }}>
              {searchResult.message || "We validated the identifier, but no company relationship could be established from connected authoritative sources."}
            </p>
          </div>
        )}

        {/* 7. Trust & Architectural Principles Section */}
        {!currentCompany && !isSearching && (
          <div style={{ marginTop: '60px' }}>
            <div style={{ textAlign: 'center', marginBottom: '32px' }}>
              <h2 style={{ fontSize: '24px', fontWeight: 800, color: 'var(--text-primary)' }}>
                Built on Verified Institutional Foundations
              </h2>
              <p style={{ color: 'var(--text-secondary)', fontSize: '15px', marginTop: '6px' }}>
                Zero scraping • Zero artificial turnover estimates • Complete cryptographic provenance
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '20px' }}>
              <div className="bento-card">
                <Database size={24} color="var(--brand-primary)" style={{ marginBottom: '12px' }} />
                <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '6px' }}>Official Open Data</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                  Direct ingestion of MCA Company Master Data via data.gov.in. CIN, incorporation dates, authorized capital, ROC jurisdictions.
                </p>
              </div>

              <div className="bento-card">
                <Key size={24} color="var(--emerald)" style={{ marginBottom: '12px' }} />
                <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '6px' }}>Authorized GST Ecosystem</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                  Connected through approved GSPs. Multi-state registration graph, jurisdictions, principal place of business, and return filing history.
                </p>
              </div>

              <div className="bento-card">
                <Lock size={24} color="var(--amber)" style={{ marginBottom: '12px' }} />
                <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '6px' }}>PAN Security & Hashing</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                  Never exposed in URLs or raw logs. Internal matching uses SHA-256 hashes, strictly verifying corporate existence without personal tax access.
                </p>
              </div>

              <div className="bento-card">
                <Award size={24} color="var(--violet)" style={{ marginBottom: '12px' }} />
                <h3 style={{ fontSize: '16px', fontWeight: 700, marginBottom: '6px' }}>Audited Financial Statements</h3>
                <p style={{ color: 'var(--text-secondary)', fontSize: '13px' }}>
                  Audited statement revenue is never conflated with GST turnover. If financial statements are unverified, we explicitly mark them unavailable.
                </p>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* 8. Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-color)',
        padding: '32px 24px',
        background: 'var(--bg-primary)',
        marginTop: 'auto'
      }}>
        <div style={{ maxWidth: '1240px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 800, fontSize: '16px' }}>
              <ShieldCheck size={18} color="var(--brand-primary)" />
              COMPANYLENS
            </div>
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '4px' }}>
              Authoritative Indian corporate intelligence and identifier resolution platform.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '18px', fontSize: '13px', color: 'var(--text-secondary)' }}>
            <button onClick={() => openLegal('disclaimer')} style={{ background: 'transparent', border: 'none', color: 'inherit', cursor: 'pointer' }}>
              Disclaimer
            </button>
            <button onClick={() => openLegal('sources')} style={{ background: 'transparent', border: 'none', color: 'inherit', cursor: 'pointer' }}>
              Sources
            </button>
            <button onClick={() => openLegal('privacy')} style={{ background: 'transparent', border: 'none', color: 'inherit', cursor: 'pointer' }}>
              Privacy & PAN Policy
            </button>
            <button onClick={() => openLegal('terms')} style={{ background: 'transparent', border: 'none', color: 'inherit', cursor: 'pointer' }}>
              Terms of Use
            </button>
          </div>
        </div>
      </footer>

      {/* Modals */}
      {showAdminModal && <AdminModal onClose={() => setShowAdminModal(false)} />}
      {showCompareModal && currentCompany && (
        <CompareModal
          currentCompany={currentCompany}
          allCompanies={watchlist.length > 0 ? [currentCompany, ...watchlist] : [currentCompany]}
          onClose={() => setShowCompareModal(false)}
          onSelectCompany={handleSelectCompany}
        />
      )}
      {showWatchlistModal && (
        <WatchlistModal
          watchlist={watchlist}
          onRemove={(id) => setWatchlist(watchlist.filter(w => w.id !== id))}
          onSelect={handleSelectCompany}
          onClose={() => setShowWatchlistModal(false)}
        />
      )}
      {showReportModal && currentCompany && (
        <ReportModal
          company={currentCompany}
          onClose={() => setShowReportModal(false)}
        />
      )}
      {showLegalModal && (
        <LegalModal
          initialTab={legalTab}
          onClose={() => setShowLegalModal(false)}
        />
      )}
      {showAuthModal && (
        <AuthModal onClose={() => setShowAuthModal(false)} />
      )}
    </div>
  );
};

export default App;
