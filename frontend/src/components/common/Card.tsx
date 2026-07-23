import React from 'react';
import { motion } from 'framer-motion';
import type { HTMLMotionProps } from 'framer-motion';

export interface CardProps extends HTMLMotionProps<'div'> {
  glow?: 'indigo' | 'emerald' | 'amber' | 'cyan' | 'none';
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({
  glow = 'none',
  children,
  style,
  className = '',
  ...props
}) => {
  const glowStyles: Record<string, string> = {
    indigo: '0 8px 32px -4px rgba(99, 102, 241, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    emerald: '0 8px 32px -4px rgba(16, 185, 129, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    amber: '0 8px 32px -4px rgba(245, 158, 11, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    cyan: '0 8px 32px -4px rgba(6, 182, 212, 0.2), inset 0 1px 0 rgba(255, 255, 255, 0.1)',
    none: 'var(--shadow-md)',
  };

  return (
    <motion.div
      whileHover={{ y: -2, transition: { duration: 0.15 } }}
      style={{
        background: 'var(--bg-card)',
        border: '1px solid var(--border-default)',
        borderRadius: '16px',
        padding: '24px',
        boxShadow: glowStyles[glow],
        transition: 'border-color 0.2s ease, background-color 0.2s ease',
        position: 'relative',
        overflow: 'hidden',
        ...style,
      }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
};
