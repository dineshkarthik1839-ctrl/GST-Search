import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, X, Send, ThumbsUp, ThumbsDown, Copy, Bot, User as UserIcon } from 'lucide-react';
import { Button } from '../common/Button';

export interface AIChatDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  contextTitle?: string;
}

interface Message {
  id: string;
  sender: 'user' | 'ai';
  text: string;
  timestamp: string;
  codeSnippet?: string;
}

export const AIChatDrawer: React.FC<AIChatDrawerProps> = ({
  isOpen,
  onClose,
  contextTitle = 'General Learning Context',
}) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ai',
      text: `Hello! I'm **TopExamX AI Tutor**, your high-performance study companion for Telangana Police & Govt Exams. I'm currently tuned to **${contextTitle}**. How can I help you master this topic today?`,
      timestamp: 'Just now',
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const suggestedPrompts = [
    '⚡ Quick trick to remember Telangana Rivers',
    '📊 Generate 3 high-yield practice MCQs',
    '💡 Explain SM-2 Spaced Repetition method',
  ];

  const handleSend = (textToSend?: string) => {
    const query = textToSend || input;
    if (!query.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages(prev => [...prev, userMsg]);
    if (!textToSend) setInput('');
    setIsTyping(true);

    setTimeout(() => {
      const aiReply: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: `Here is a high-yield breakdown for **"${query}"** tailored to your exam target:

1. **Key Concept**: Focus on the foundational principles specified in the Telangana State Board curriculum.
2. **Exam Trick**: Remember the mnemonic **G-K-P-M** (Godavari, Krishna, Penna, Manair).
3. **Retention Score**: Practicing 5 related questions today boosts retention by **94%** via SM-2!`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages(prev => [...prev, aiReply]);
      setIsTyping(false);
    }, 1200);
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0, 0, 0, 0.6)',
              backdropFilter: 'blur(4px)',
              zIndex: 999,
            }}
          />

          {/* Drawer Slide */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 25, stiffness: 220 }}
            style={{
              position: 'fixed',
              top: 0,
              right: 0,
              bottom: 0,
              width: '440px',
              maxWidth: '90vw',
              background: 'var(--bg-surface)',
              borderLeft: '1px solid var(--border-default)',
              boxShadow: 'var(--shadow-lg)',
              zIndex: 1000,
              display: 'flex',
              flexDirection: 'column',
            }}
          >
            {/* Header */}
            <div
              style={{
                padding: '18px 24px',
                borderBottom: '1px solid var(--border-default)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                background: 'var(--bg-card)',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <div
                  style={{
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: '#fff',
                  }}
                >
                  <Sparkles size={18} />
                </div>
                <div>
                  <h3 style={{ fontSize: '15px', fontWeight: 700 }}>TopExamX AI Tutor</h3>
                  <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Powered by Advanced AI Intelligence</div>
                </div>
              </div>

              <button
                onClick={onClose}
                style={{
                  background: 'transparent',
                  border: 'none',
                  color: 'var(--text-secondary)',
                  cursor: 'pointer',
                  padding: '4px',
                }}
              >
                <X size={20} />
              </button>
            </div>

            {/* Messages Feed */}
            <div
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '16px',
              }}
            >
              {messages.map(msg => (
                <div
                  key={msg.id}
                  style={{
                    display: 'flex',
                    gap: '12px',
                    alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '88%',
                  }}
                >
                  {msg.sender === 'ai' && (
                    <div
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        background: 'rgba(99, 102, 241, 0.15)',
                        border: '1px solid rgba(99, 102, 241, 0.3)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#818cf8',
                        flexShrink: 0,
                      }}
                    >
                      <Bot size={16} />
                    </div>
                  )}

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                    <div
                      style={{
                        padding: '12px 16px',
                        borderRadius: msg.sender === 'user' ? '14px 14px 2px 14px' : '14px 14px 14px 2px',
                        background: msg.sender === 'user' ? '#6366f1' : 'var(--bg-card)',
                        color: msg.sender === 'user' ? '#ffffff' : 'var(--text-primary)',
                        border: msg.sender === 'user' ? 'none' : '1px solid var(--border-default)',
                        fontSize: '13px',
                        lineHeight: 1.6,
                        whiteSpace: 'pre-line',
                      }}
                    >
                      {msg.text}
                    </div>

                    {msg.sender === 'ai' && (
                      <div style={{ display: 'flex', gap: '10px', fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px', paddingLeft: '4px' }}>
                        <button style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Copy size={12} /> Copy
                        </button>
                        <button style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <ThumbsUp size={12} />
                        </button>
                        <button style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <ThumbsDown size={12} />
                        </button>
                      </div>
                    )}
                  </div>

                  {msg.sender === 'user' && (
                    <div
                      style={{
                        width: '28px',
                        height: '28px',
                        borderRadius: '50%',
                        background: '#6366f1',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        color: '#fff',
                        flexShrink: 0,
                      }}
                    >
                      <UserIcon size={14} />
                    </div>
                  )}
                </div>
              ))}

              {isTyping && (
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--text-muted)', fontSize: '12px' }}>
                  <Bot size={16} />
                  <span>AI Tutor is thinking...</span>
                </div>
              )}
            </div>

            {/* Suggested Prompts */}
            <div style={{ padding: '0 20px 12px 20px', display: 'flex', gap: '6px', overflowX: 'auto' }}>
              {suggestedPrompts.map((p, i) => (
                <button
                  key={i}
                  onClick={() => handleSend(p)}
                  style={{
                    padding: '6px 12px',
                    borderRadius: '9999px',
                    background: 'var(--bg-card)',
                    border: '1px solid var(--border-default)',
                    color: 'var(--text-secondary)',
                    fontSize: '11px',
                    whiteSpace: 'nowrap',
                    cursor: 'pointer',
                  }}
                >
                  {p}
                </button>
              ))}
            </div>

            {/* Input Box */}
            <div
              style={{
                padding: '16px 20px',
                borderTop: '1px solid var(--border-default)',
                background: 'var(--bg-card)',
                display: 'flex',
                gap: '10px',
              }}
            >
              <input
                placeholder="Ask AI Tutor anything about your exam..."
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => e.key === 'Enter' && handleSend()}
                style={{
                  flex: 1,
                  background: 'var(--bg-surface)',
                  border: '1px solid var(--border-default)',
                  borderRadius: '8px',
                  padding: '10px 14px',
                  color: 'var(--text-primary)',
                  fontSize: '13px',
                  outline: 'none',
                }}
              />
              <Button variant="ai" size="sm" onClick={() => handleSend()} rightIcon={<Send size={14} />}>
                Ask
              </Button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};
