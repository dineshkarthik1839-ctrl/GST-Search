import React from 'react';
import { ShieldCheck, Search, ArrowRightLeft, Bookmark, Settings, Info, LogIn } from 'lucide-react';

interface NavbarProps {
  onNavClick: (view: 'search' | 'compare' | 'watchlist' | 'admin' | 'sources' | 'about') => void;
  currentView: string;
  watchlistCount: number;
  onOpenAuth: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  onNavClick,
  currentView,
  watchlistCount,
  onOpenAuth
}) => {
  return (
    <header className="glass-panel" style={{
      position: 'sticky',
      top: '12px',
      zIndex: 100,
      margin: '12px 16px 20px 16px',
      padding: '12px 24px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      borderRadius: '14px'
    }}>
      {/* Brand */}
      <div
        onClick={() => onNavClick('search')}
        style={{ display: 'flex', alignItems: 'center', gap: '10px', cursor: 'pointer' }}
      >
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #0284c7 0%, #3b82f6 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#ffffff',
          boxShadow: '0 4px 12px rgba(2, 132, 199, 0.4)'
        }}>
          <ShieldCheck size={22} />
        </div>
        <div>
          <div style={{ fontSize: '18px', fontWeight: 800, letterSpacing: '-0.03em', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '6px' }}>
            COMPANYLENS
            <span style={{ fontSize: '10px', padding: '2px 6px', background: 'rgba(56, 189, 248, 0.15)', color: 'var(--brand-primary)', borderRadius: '4px', fontWeight: 700 }}>
              IN
            </span>
          </div>
          <p style={{ fontSize: '10px', color: 'var(--text-muted)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
            Corporate Intelligence
          </p>
        </div>
      </div>

      {/* Nav Links */}
      <nav style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <button
          onClick={() => onNavClick('search')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '7px 12px',
            borderRadius: '8px',
            background: currentView === 'search' ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
            color: currentView === 'search' ? 'var(--brand-primary)' : 'var(--text-secondary)',
            border: 'none',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          <Search size={15} />
          Search
        </button>

        <button
          onClick={() => onNavClick('compare')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '7px 12px',
            borderRadius: '8px',
            background: currentView === 'compare' ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
            color: currentView === 'compare' ? 'var(--brand-primary)' : 'var(--text-secondary)',
            border: 'none',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          <ArrowRightLeft size={15} />
          Compare
        </button>

        <button
          onClick={() => onNavClick('watchlist')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '7px 12px',
            borderRadius: '8px',
            background: currentView === 'watchlist' ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
            color: currentView === 'watchlist' ? 'var(--brand-primary)' : 'var(--text-secondary)',
            border: 'none',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            position: 'relative'
          }}
        >
          <Bookmark size={15} />
          Watchlist
          {watchlistCount > 0 && (
            <span style={{
              background: 'var(--brand-primary)',
              color: '#000000',
              fontSize: '10px',
              fontWeight: 800,
              padding: '1px 5px',
              borderRadius: '9999px',
              marginLeft: '2px'
            }}>
              {watchlistCount}
            </span>
          )}
        </button>

        <button
          onClick={() => onNavClick('admin')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '7px 12px',
            borderRadius: '8px',
            background: currentView === 'admin' ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
            color: currentView === 'admin' ? 'var(--brand-primary)' : 'var(--text-secondary)',
            border: 'none',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          <Settings size={15} />
          Admin
        </button>

        <button
          onClick={() => onNavClick('sources')}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '7px 12px',
            borderRadius: '8px',
            background: currentView === 'sources' ? 'rgba(56, 189, 248, 0.12)' : 'transparent',
            color: currentView === 'sources' ? 'var(--brand-primary)' : 'var(--text-secondary)',
            border: 'none',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          <Info size={15} />
          Sources
        </button>
      </nav>

      {/* Auth Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
        <button
          onClick={onOpenAuth}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            padding: '7px 14px',
            borderRadius: '8px',
            background: 'var(--bg-surface)',
            border: '1px solid var(--border-color)',
            color: 'var(--text-primary)',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer'
          }}
        >
          <LogIn size={15} />
          Sign In
        </button>
      </div>
    </header>
  );
};
