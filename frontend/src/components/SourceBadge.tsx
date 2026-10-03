import React from 'react';
import { ShieldCheck, Database, Key, Award, AlertCircle, HelpCircle } from 'lucide-react';

interface SourceBadgeProps {
  sourceType: string;
  sourceName?: string;
  updatedAt?: string;
  verificationStatus?: string;
}

export const SourceBadge: React.FC<SourceBadgeProps> = ({
  sourceType,
  sourceName,
  updatedAt,
  verificationStatus
}) => {
  const normType = sourceType.toUpperCase();

  let badgeClass = 'source-badge-open-data';
  let Icon = Database;

  if (normType.includes('OFFICIAL')) {
    badgeClass = 'source-badge-official';
    Icon = ShieldCheck;
  } else if (normType.includes('OPEN DATA')) {
    badgeClass = 'source-badge-open-data';
    Icon = Database;
  } else if (normType.includes('AUTHORIZED')) {
    badgeClass = 'source-badge-authorized';
    Icon = Key;
  } else if (normType.includes('LICENSED')) {
    badgeClass = 'source-badge-licensed';
    Icon = Award;
  } else if (normType.includes('DERIVED')) {
    badgeClass = 'source-badge-derived';
    Icon = HelpCircle;
  } else if (normType.includes('UNAVAILABLE')) {
    badgeClass = 'source-badge-unavailable';
    Icon = AlertCircle;
  }

  return (
    <div style={{ display: 'inline-flex', flexDirection: 'column', gap: '3px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
        <span className={`source-badge ${badgeClass}`}>
          <Icon size={12} />
          {normType}
        </span>
        {sourceName && (
          <span style={{ fontSize: '12px', color: 'var(--text-secondary)', fontWeight: 500 }}>
            {sourceName}
          </span>
        )}
      </div>
      {(updatedAt || verificationStatus) && (
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
          {verificationStatus ? `${verificationStatus} • ` : ''}
          {updatedAt ? `Updated ${updatedAt}` : ''}
        </span>
      )}
    </div>
  );
};
