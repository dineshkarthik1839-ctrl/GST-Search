import React from 'react';
import { CheckCircle2, Loader2, Sparkles, Database, Search, FileText } from 'lucide-react';

interface SearchStepperProps {
  currentStep: number;
  detectedType: string;
}

export const SearchStepper: React.FC<SearchStepperProps> = ({ currentStep, detectedType }) => {
  const steps = [
    { label: `${detectedType || 'Identifier'} Detected`, icon: Sparkles },
    { label: `Validating ${detectedType || 'format'}...`, icon: CheckCircle2 },
    { label: 'Searching available company records...', icon: Search },
    { label: 'Resolving company identity graph...', icon: Database },
    { label: 'Loading authoritative information...', icon: FileText },
  ];

  return (
    <div style={{
      margin: '24px 0',
      padding: '20px',
      background: 'rgba(19, 23, 34, 0.7)',
      border: '1px solid var(--border-color)',
      borderRadius: '12px',
      backdropFilter: 'blur(8px)'
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px'
      }}>
        {steps.map((step, idx) => {
          const isDone = currentStep > idx;
          const isCurrent = currentStep === idx;

          return (
            <div
              key={idx}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: isDone ? 'var(--emerald)' : isCurrent ? 'var(--brand-primary)' : 'var(--text-muted)',
                fontSize: '13px',
                fontWeight: isCurrent ? 600 : 500,
                transition: 'all 0.2s ease'
              }}
            >
              {isDone ? (
                <CheckCircle2 size={16} />
              ) : isCurrent ? (
                <Loader2 size={16} className="animate-spin" style={{ animation: 'spin 1s linear infinite' }} />
              ) : (
                <div style={{
                  width: '16px',
                  height: '16px',
                  borderRadius: '50%',
                  border: '1px solid var(--border-color)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '10px'
                }}>
                  {idx + 1}
                </div>
              )}
              <span>{step.label}</span>
            </div>
          );
        })}
      </div>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
