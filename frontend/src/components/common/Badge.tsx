import React from 'react';

export interface BadgeProps {
  variant?: 'primary' | 'secondary' | 'success' | 'warning' | 'danger' | 'ai';
  children: React.ReactNode;
  icon?: React.ReactNode;
  style?: React.CSSProperties;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'primary',
  children,
  icon,
  style,
}) => {
  const badgeStyles: Record<string, React.CSSProperties> = {
    primary: {
      background: 'rgba(99, 102, 241, 0.12)',
      color: '#818cf8',
      border: '1px solid rgba(99, 102, 241, 0.3)',
    },
    secondary: {
      background: 'rgba(6, 182, 212, 0.12)',
      color: '#22d3ee',
      border: '1px solid rgba(6, 182, 212, 0.3)',
    },
    success: {
      background: 'rgba(34, 197, 94, 0.12)',
      color: '#4ade80',
      border: '1px solid rgba(34, 197, 94, 0.3)',
    },
    warning: {
      background: 'rgba(245, 158, 11, 0.12)',
      color: '#fbbf24',
      border: '1px solid rgba(245, 158, 11, 0.3)',
    },
    danger: {
      background: 'rgba(239, 68, 68, 0.12)',
      color: '#f87171',
      border: '1px solid rgba(239, 68, 68, 0.3)',
    },
    ai: {
      background: 'linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(168,85,247,0.2) 100%)',
      color: '#c084fc',
      border: '1px solid rgba(192, 132, 252, 0.4)',
    },
  };

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '3px 10px',
        borderRadius: '9999px',
        fontSize: '11px',
        fontWeight: 700,
        letterSpacing: '0.04em',
        textTransform: 'uppercase',
        ...badgeStyles[variant],
        ...style,
      }}
    >
      {icon && <span style={{ display: 'inline-flex' }}>{icon}</span>}
      <span>{children}</span>
    </span>
  );
};
