import React from 'react';
import { motion } from 'framer-motion';
import type { HTMLMotionProps } from 'framer-motion';

export interface ButtonProps extends HTMLMotionProps<'button'> {
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger' | 'ai';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  leftIcon,
  rightIcon,
  children,
  className = '',
  disabled,
  ...props
}) => {
  const sizeStyles = {
    sm: { padding: '6px 12px', fontSize: '13px', borderRadius: '6px', gap: '6px' },
    md: { padding: '10px 18px', fontSize: '14px', borderRadius: '8px', gap: '8px' },
    lg: { padding: '14px 24px', fontSize: '16px', borderRadius: '10px', gap: '10px' },
  }[size];

  const variantStyles: Record<string, React.CSSProperties> = {
    primary: {
      background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
      color: '#ffffff',
      border: 'none',
      boxShadow: '0 4px 14px rgba(99, 102, 241, 0.3)',
      fontWeight: 600,
    },
    secondary: {
      background: 'var(--bg-surface-hover)',
      color: 'var(--text-primary)',
      border: '1px solid var(--border-default)',
      fontWeight: 600,
    },
    outline: {
      background: 'transparent',
      color: 'var(--text-primary)',
      border: '1px solid var(--border-default)',
      fontWeight: 500,
    },
    ghost: {
      background: 'transparent',
      color: 'var(--text-secondary)',
      border: 'none',
      fontWeight: 500,
    },
    danger: {
      background: 'rgba(239, 68, 68, 0.15)',
      color: '#ef4444',
      border: '1px solid rgba(239, 68, 68, 0.3)',
      fontWeight: 600,
    },
    ai: {
      background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #06b6d4 100%)',
      color: '#ffffff',
      border: 'none',
      boxShadow: '0 4px 16px rgba(168, 85, 247, 0.35)',
      fontWeight: 700,
    },
  };

  return (
    <motion.button
      whileHover={{ scale: disabled || isLoading ? 1 : 1.02, y: disabled ? 0 : -1 }}
      whileTap={{ scale: disabled || isLoading ? 1 : 0.98 }}
      disabled={disabled || isLoading}
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: disabled || isLoading ? 'not-allowed' : 'pointer',
        opacity: disabled ? 0.5 : 1,
        transition: 'background 0.2s ease, border-color 0.2s ease',
        ...sizeStyles,
        ...variantStyles[variant],
      }}
      className={className}
      {...props}
    >
      {isLoading ? (
        <span style={{ animation: 'spin 1s linear infinite', display: 'inline-block' }}>🌀</span>
      ) : (
        <>
          {leftIcon && <span style={{ display: 'inline-flex' }}>{leftIcon}</span>}
          <span>{children}</span>
          {rightIcon && <span style={{ display: 'inline-flex' }}>{rightIcon}</span>}
        </>
      )}
    </motion.button>
  );
};
