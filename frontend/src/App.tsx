import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import confetti from 'canvas-confetti';
import {
  LayoutDashboard,
  BookOpen,
  FileCheck2,
  Bookmark,
  TrendingUp,
  Sparkles,
  Search,
  Flame,
  Clock,
  CheckCircle2,
  AlertTriangle,
  BrainCircuit,
  Trophy,
  Zap,
  RotateCcw,
  Target,
  ArrowRight,
} from 'lucide-react';

import { apiClient } from './api/client';
import type { Attempt, StudentDashboardData, LeaderboardItem, BookmarkItem, UnifiedSearchResult } from './types/platform';
import { Button } from './components/common/Button';
import { Card } from './components/common/Card';
import { Badge } from './components/common/Badge';
import { ThemeToggle } from './components/common/ThemeToggle';
import { AIChatDrawer } from './components/ai/AIChatDrawer';
import './styles/theme.css';

type ViewMode = 'dashboard' | 'browser' | 'test' | 'result' | 'bookmarks' | 'analytics';

export function App() {
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  const [currentView, setCurrentView] = useState<ViewMode>('dashboard');
  const [dashboardData, setDashboardData] = useState<StudentDashboardData | null>(null);
  const [activeAttempt, setActiveAttempt] = useState<Attempt | null>(null);
  const [activeQuestionIndex, setActiveQuestionIndex] = useState<number>(0);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<UnifiedSearchResult | null>(null);
  const [isSearchOpen, setIsSearchOpen] = useState<boolean>(false);
  const [isAIDrawerOpen, setIsAIDrawerOpen] = useState<boolean>(false);
  const [bookmarks, setBookmarks] = useState<BookmarkItem[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardItem[]>([]);
  const [timerSeconds, setTimerSeconds] = useState<number>(3600);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  useEffect(() => {
    loadDashboard();
    loadBookmarks();
    loadLeaderboard();
  }, []);

  useEffect(() => {
    let interval: any = null;
    if (currentView === 'test' && timerSeconds > 0) {
      interval = setInterval(() => {
        setTimerSeconds(prev => (prev > 0 ? prev - 1 : 0));
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [currentView, timerSeconds]);

  // Global Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
        e.preventDefault();
        setIsSearchOpen(prev => !prev);
      } else if (currentView === 'test' && activeAttempt) {
        if (['1', '2', '3', '4'].includes(e.key)) {
          const idx = parseInt(e.key) - 1;
          const currentQ = activeAttempt.attempt_questions[activeQuestionIndex]?.question;
          if (currentQ && currentQ.options[idx]) {
            handleSelectOption(currentQ.options[idx].id);
          }
        } else if (e.key.toLowerCase() === 'n') {
          if (activeQuestionIndex < activeAttempt.attempt_questions.length - 1) {
            setActiveQuestionIndex(prev => prev + 1);
          }
        } else if (e.key.toLowerCase() === 'p') {
          if (activeQuestionIndex > 0) {
            setActiveQuestionIndex(prev => prev - 1);
          }
        }
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentView, activeAttempt, activeQuestionIndex]);

  const loadDashboard = async () => {
    try {
      const data = await apiClient.getDashboard();
      setDashboardData(data);
    } catch (e) {
      console.error(e);
    }
  };

  const loadBookmarks = async () => {
    try {
      const bms = await apiClient.getBookmarks();
      setBookmarks(bms);
    } catch (e) {
      console.error(e);
    }
  };

  const loadLeaderboard = async () => {
    try {
      const lb = await apiClient.getLeaderboard();
      setLeaderboard(lb);
    } catch (e) {
      console.error(e);
    }
  };

  const handleStartPractice = async (mode: string = 'PRACTICE') => {
    try {
      const attempt = await apiClient.startPracticeSession(mode, 10);
      setActiveAttempt(attempt);
      setActiveQuestionIndex(0);
      setTimerSeconds(1800);
      setCurrentView('test');
    } catch (e) {
      console.error(e);
    }
  };

  const handleSelectOption = async (optId: string) => {
    if (!activeAttempt) return;
    const currentAQ = activeAttempt.attempt_questions[activeQuestionIndex];
    if (!currentAQ) return;

    const updatedAQs = [...activeAttempt.attempt_questions];
    updatedAQs[activeQuestionIndex] = {
      ...currentAQ,
      selected_option_id: optId,
      status: 'ANSWERED',
    };

    setActiveAttempt({
      ...activeAttempt,
      attempt_questions: updatedAQs,
    });

    await apiClient.saveAnswer(activeAttempt.id, currentAQ.question_id, optId, 'ANSWERED', 15);
  };

  const handleMarkForReview = async () => {
    if (!activeAttempt) return;
    const currentAQ = activeAttempt.attempt_questions[activeQuestionIndex];
    if (!currentAQ) return;

    const newStatus = currentAQ.selected_option_id ? 'ANSWERED_AND_MARKED' : 'MARKED_FOR_REVIEW';
    const updatedAQs = [...activeAttempt.attempt_questions];
    updatedAQs[activeQuestionIndex] = {
      ...currentAQ,
      status: newStatus,
    };

    setActiveAttempt({
      ...activeAttempt,
      attempt_questions: updatedAQs,
    });

    await apiClient.saveAnswer(activeAttempt.id, currentAQ.question_id, currentAQ.selected_option_id, newStatus, 10);
  };

  const handleToggleBookmark = async () => {
    if (!activeAttempt) return;
    const currentQ = activeAttempt.attempt_questions[activeQuestionIndex]?.question;
    if (!currentQ) return;

    await apiClient.toggleBookmark(currentQ.id, 'QUESTION');
    loadBookmarks();
  };

  const handleSubmitTest = async () => {
    if (!activeAttempt) return;
    try {
      const completed = await apiClient.submitAttempt(activeAttempt.id);
      setActiveAttempt(completed);
      setCurrentView('result');
      loadDashboard();
      confetti({
        particleCount: 100,
        spread: 70,
        origin: { y: 0.6 },
      });
    } catch (e) {
      console.error(e);
    }
  };

  const handleSearch = async (q: string) => {
    setSearchQuery(q);
    if (q.trim().length >= 2) {
      const res = await apiClient.searchUnified(q);
      setSearchResults(res);
    }
  };

  const formatTimer = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const currentAQ = activeAttempt?.attempt_questions[activeQuestionIndex];
  const currentQ = currentAQ?.question;

  return (
    <div style={{ display: 'flex', width: '100%', minHeight: '100vh', background: 'var(--bg-app)', color: 'var(--text-primary)' }}>
      {/* ── Silicon Valley Sidebar Navigation ── */}
      <aside style={{ width: '270px', background: 'var(--bg-surface)', borderRight: '1px solid var(--border-default)', padding: '24px 18px', display: 'flex', flexDirection: 'column', gap: '28px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div>
            <div style={{ fontSize: '20px', fontWeight: 800, letterSpacing: '-0.02em', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span className="gradient-text-ai">TopExamX</span>
              <Badge variant="ai">PRO AI</Badge>
            </div>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>Question Intelligence Platform</div>
          </div>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
          <button
            onClick={() => setCurrentView('dashboard')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '11px 14px',
              borderRadius: '10px',
              background: currentView === 'dashboard' ? 'var(--primary-glow)' : 'transparent',
              color: currentView === 'dashboard' ? 'var(--primary)' : 'var(--text-secondary)',
              border: currentView === 'dashboard' ? '1px solid var(--border-highlight)' : '1px solid transparent',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px',
              textAlign: 'left',
              transition: 'all 0.2s ease',
            }}
          >
            <LayoutDashboard size={18} /> Dashboard
          </button>

          <button
            onClick={() => setCurrentView('browser')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '11px 14px',
              borderRadius: '10px',
              background: currentView === 'browser' ? 'var(--primary-glow)' : 'transparent',
              color: currentView === 'browser' ? 'var(--primary)' : 'var(--text-secondary)',
              border: currentView === 'browser' ? '1px solid var(--border-highlight)' : '1px solid transparent',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px',
              textAlign: 'left',
              transition: 'all 0.2s ease',
            }}
          >
            <BookOpen size={18} /> Syllabus & Exams
          </button>

          <button
            onClick={() => handleStartPractice('PRACTICE')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '11px 14px',
              borderRadius: '10px',
              background: currentView === 'test' ? 'var(--primary-glow)' : 'transparent',
              color: currentView === 'test' ? 'var(--primary)' : 'var(--text-secondary)',
              border: currentView === 'test' ? '1px solid var(--border-highlight)' : '1px solid transparent',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px',
              textAlign: 'left',
              transition: 'all 0.2s ease',
            }}
          >
            <FileCheck2 size={18} /> Test Engine
          </button>

          <button
            onClick={() => setCurrentView('bookmarks')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '11px 14px',
              borderRadius: '10px',
              background: currentView === 'bookmarks' ? 'var(--primary-glow)' : 'transparent',
              color: currentView === 'bookmarks' ? 'var(--primary)' : 'var(--text-secondary)',
              border: currentView === 'bookmarks' ? '1px solid var(--border-highlight)' : '1px solid transparent',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px',
              textAlign: 'left',
              transition: 'all 0.2s ease',
            }}
          >
            <Bookmark size={18} /> Saved ({bookmarks.length})
          </button>

          <button
            onClick={() => setCurrentView('analytics')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              padding: '11px 14px',
              borderRadius: '10px',
              background: currentView === 'analytics' ? 'var(--primary-glow)' : 'transparent',
              color: currentView === 'analytics' ? 'var(--primary)' : 'var(--text-secondary)',
              border: currentView === 'analytics' ? '1px solid var(--border-highlight)' : '1px solid transparent',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px',
              textAlign: 'left',
              transition: 'all 0.2s ease',
            }}
          >
            <TrendingUp size={18} /> Analytics & Mastery
          </button>
        </nav>

        {/* AI Tutor Callout Widget */}
        <div style={{ marginTop: 'auto', background: 'linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(168,85,247,0.15) 100%)', border: '1px solid rgba(192, 132, 252, 0.3)', padding: '16px', borderRadius: '14px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px', fontWeight: 700, color: '#c084fc' }}>
            <Sparkles size={16} /> AI Tutor Connected
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-secondary)' }}>Instant answers, quick tricks & concept breakdowns.</div>
          <Button variant="ai" size="sm" onClick={() => setIsAIDrawerOpen(true)} leftIcon={<Zap size={14} />}>
            Ask AI Tutor
          </Button>
        </div>
      </aside>

      {/* ── Main App Content ── */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
        {/* Top Floating App Bar */}
        <header style={{ height: '68px', background: 'var(--bg-glass)', backdropFilter: 'blur(16px)', borderBottom: '1px solid var(--border-default)', padding: '0 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'sticky', top: 0, zIndex: 100 }}>
          <button
            onClick={() => setIsSearchOpen(true)}
            style={{
              background: 'var(--bg-surface)',
              border: '1px solid var(--border-default)',
              padding: '8px 16px',
              borderRadius: '10px',
              color: 'var(--text-muted)',
              fontSize: '13px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              width: '340px',
            }}
          >
            <Search size={16} />
            <span>Search questions, topics, exams...</span>
            <kbd style={{ background: 'var(--bg-card)', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', color: 'var(--text-secondary)', marginLeft: 'auto' }}>Ctrl+K</kbd>
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <Badge variant="success" icon={<CheckCircle2 size={12} />}>Telangana Police 2026</Badge>
            <ThemeToggle theme={theme} onToggle={() => setTheme(prev => (prev === 'dark' ? 'light' : 'dark'))} />
            <div style={{ width: '38px', height: '38px', borderRadius: '50%', background: 'linear-gradient(135deg, #6366f1 0%, #a855f7 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '14px', color: '#fff', boxShadow: 'var(--shadow-glow)' }}>
              DK
            </div>
          </div>
        </header>

        {/* View Content Area */}
        <div style={{ padding: '32px', flex: 1 }}>
          <AnimatePresence mode="wait">
            {/* ── BENTO DASHBOARD VIEW ── */}
            {currentView === 'dashboard' && dashboardData && (
              <motion.div
                key="dashboard"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                transition={{ duration: 0.2 }}
                style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <h1 style={{ fontSize: '28px', fontWeight: 800, letterSpacing: '-0.02em' }}>
                      Welcome back, <span className="gradient-text-ai">Dinesh</span>
                    </h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '14px', marginTop: '4px' }}>
                      Target: Telangana Police Constable & Sub-Inspector Recruitment Prelims 2026
                    </p>
                  </div>
                  <Button variant="primary" size="lg" onClick={() => handleStartPractice('EXAM_SIMULATION')} rightIcon={<ArrowRight size={18} />}>
                    Launch Full Mock Test
                  </Button>
                </div>

                {/* Bento Grid Metrics Cards */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px' }}>
                  <Card glow="emerald">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Overall Accuracy</span>
                      <Target size={18} color="#10b981" />
                    </div>
                    <div style={{ fontSize: '32px', fontWeight: 800, color: '#10b981', marginTop: '10px' }}>{dashboardData.overall_accuracy_pct}%</div>
                    <Badge variant="success" style={{ marginTop: '10px' }}>Top 5% Rank</Badge>
                  </Card>

                  <Card glow="indigo">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Learning Health Score</span>
                      <BrainCircuit size={18} color="#818cf8" />
                    </div>
                    <div style={{ fontSize: '32px', fontWeight: 800, color: '#818cf8', marginTop: '10px' }}>{dashboardData.learning_health_score}/100</div>
                    <Badge variant="primary" style={{ marginTop: '10px' }}>SM-2 Optimized</Badge>
                  </Card>

                  <Card glow="amber">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Revision Queue</span>
                      <RotateCcw size={18} color="#f59e0b" />
                    </div>
                    <div style={{ fontSize: '32px', fontWeight: 800, color: '#f59e0b', marginTop: '10px' }}>{dashboardData.revision_due_count} Items</div>
                    <button onClick={() => handleStartPractice('REVISION')} style={{ background: 'none', border: 'none', color: '#fbbf24', fontSize: '13px', fontWeight: 700, cursor: 'pointer', padding: 0, marginTop: '8px' }}>
                      Start Spaced Revision →
                    </button>
                  </Card>

                  <Card glow="cyan">
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Study Streak</span>
                      <Flame size={18} color="#ef4444" />
                    </div>
                    <div style={{ fontSize: '32px', fontWeight: 800, color: '#f87171', marginTop: '10px' }}>7 Days 🔥</div>
                    <span style={{ fontSize: '12px', color: 'var(--text-secondary)', marginTop: '8px', display: 'block' }}>Streak Goal: 14 Days</span>
                  </Card>
                </div>

                {/* Subject Mastery & Recommendations */}
                <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
                  <Card>
                    <h3 style={{ fontSize: '18px', fontWeight: 700, marginBottom: '20px' }}>Subject Mastery & Accuracy Breakdown</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
                      {Object.entries(dashboardData.subject_accuracy).map(([subject, accuracy]) => (
                        <div key={subject}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '14px', marginBottom: '8px' }}>
                            <span style={{ fontWeight: 600 }}>{subject}</span>
                            <span style={{ fontWeight: 700, color: accuracy >= 80 ? '#10b981' : '#f59e0b' }}>{accuracy}% Accuracy</span>
                          </div>
                          <div style={{ height: '10px', background: 'var(--bg-surface)', borderRadius: '9999px', overflow: 'hidden', border: '1px solid var(--border-subtle)' }}>
                            <motion.div
                              initial={{ width: 0 }}
                              animate={{ width: `${accuracy}%` }}
                              transition={{ duration: 0.8, ease: 'easeOut' }}
                              style={{
                                height: '100%',
                                background: accuracy >= 80 ? 'linear-gradient(90deg, #10b981 0%, #059669 100%)' : 'linear-gradient(90deg, #f59e0b 0%, #d97706 100%)',
                                borderRadius: '9999px',
                              }}
                            />
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <Card glow="amber">
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#ef4444', fontSize: '13px', fontWeight: 700, marginBottom: '8px' }}>
                        <AlertTriangle size={16} /> WEAK TOPICS DETECTED
                      </div>
                      <h4 style={{ fontSize: '15px', fontWeight: 700 }}>Geography of Telangana & Physical Geography</h4>
                      <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: '8px 0 16px 0' }}>Current accuracy is 45%. Solve targeted weak topic questions to boost exam score.</p>
                      <Button variant="danger" size="sm" onClick={() => handleStartPractice('WEAK_TOPIC_PRACTICE')}>
                        Practice Weak Topics
                      </Button>
                    </Card>

                    <Card>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#3b82f6', fontSize: '13px', fontWeight: 700, marginBottom: '8px' }}>
                        <Clock size={16} /> EXAM COUNTDOWN
                      </div>
                      <div style={{ fontSize: '24px', fontWeight: 800 }}>42 Days Left</div>
                      <div style={{ fontSize: '13px', color: 'var(--text-secondary)', marginTop: '4px' }}>Telangana Police Constable Prelims 2026</div>
                    </Card>
                  </div>
                </div>
              </motion.div>
            )}

            {/* ── QUESTION TEST SCREEN ── */}
            {currentView === 'test' && activeAttempt && currentQ && (
              <motion.div
                key="test"
                initial={{ opacity: 0, scale: 0.98 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.98 }}
                transition={{ duration: 0.2 }}
                style={{ display: 'grid', gridTemplateColumns: '3fr 1fr', gap: '24px', height: 'calc(100vh - 140px)' }}
              >
                {/* Question Container */}
                <Card style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                  <div>
                    {/* Header Controls */}
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--border-default)', paddingBottom: '16px', marginBottom: '24px' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <Badge variant="primary">{activeAttempt.mode}</Badge>
                        <span style={{ fontSize: '14px', color: 'var(--text-secondary)', fontWeight: 600 }}>
                          Question {activeQuestionIndex + 1} of {activeAttempt.attempt_questions.length}
                        </span>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '18px', fontWeight: 800, color: timerSeconds < 300 ? '#ef4444' : '#f59e0b', background: 'var(--bg-surface)', padding: '6px 14px', borderRadius: '8px', border: '1px solid var(--border-default)' }}>
                          ⏱ {formatTimer(timerSeconds)}
                        </div>
                        <Button variant="outline" size="sm" onClick={handleToggleBookmark}>
                          <Bookmark size={14} /> Save Question
                        </Button>
                      </div>
                    </div>

                    {/* Question Content */}
                    <h2 style={{ fontSize: '19px', fontWeight: 600, lineHeight: 1.6, marginBottom: '28px' }}>
                      {currentQ.content}
                    </h2>

                    {/* Options Grid */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                      {currentQ.options.map((opt, idx) => {
                        const isSelected = currentAQ?.selected_option_id === opt.id;
                        return (
                          <motion.div
                            key={opt.id}
                            whileHover={{ x: 3 }}
                            onClick={() => handleSelectOption(opt.id)}
                            style={{
                              padding: '16px 20px',
                              borderRadius: '12px',
                              border: isSelected ? '2px solid var(--primary)' : '1px solid var(--border-default)',
                              background: isSelected ? 'var(--primary-glow)' : 'var(--bg-surface)',
                              cursor: 'pointer',
                              display: 'flex',
                              alignItems: 'center',
                              gap: '16px',
                              transition: 'border-color 0.15s ease',
                            }}
                          >
                            <div
                              style={{
                                width: '28px',
                                height: '28px',
                                borderRadius: '50%',
                                border: isSelected ? '2px solid var(--primary)' : '1px solid var(--text-muted)',
                                background: isSelected ? 'var(--primary)' : 'transparent',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                fontSize: '13px',
                                fontWeight: 700,
                                color: isSelected ? '#ffffff' : 'var(--text-secondary)',
                              }}
                            >
                              {String.fromCharCode(65 + idx)}
                            </div>
                            <div style={{ fontSize: '15px', color: isSelected ? 'var(--text-primary)' : 'var(--text-secondary)', fontWeight: isSelected ? 600 : 400 }}>
                              {opt.content}
                            </div>
                          </motion.div>
                        );
                      })}
                    </div>
                  </div>

                  {/* Test Navigation Bar */}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid var(--border-default)', paddingTop: '20px', marginTop: '24px' }}>
                    <div style={{ display: 'flex', gap: '12px' }}>
                      <Button
                        variant="secondary"
                        disabled={activeQuestionIndex === 0}
                        onClick={() => setActiveQuestionIndex(prev => prev - 1)}
                      >
                        ← Previous (P)
                      </Button>
                      <Button variant="outline" onClick={handleMarkForReview}>
                        🔖 Mark Review
                      </Button>
                    </div>

                    <div style={{ display: 'flex', gap: '12px' }}>
                      <Button
                        variant="secondary"
                        disabled={activeQuestionIndex === activeAttempt.attempt_questions.length - 1}
                        onClick={() => setActiveQuestionIndex(prev => prev + 1)}
                      >
                        Next → (N)
                      </Button>
                      <Button variant="primary" onClick={handleSubmitTest}>
                        Submit Test
                      </Button>
                    </div>
                  </div>
                </Card>

                {/* Question Palette Drawer */}
                <Card style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: 700 }}>Question Palette</h3>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '10px', maxHeight: '380px', overflowY: 'auto' }}>
                    {activeAttempt.attempt_questions.map((aq, idx) => {
                      let statusClass = 'unvisited';
                      if (aq.status === 'ANSWERED') statusClass = 'answered';
                      if (aq.status === 'MARKED_FOR_REVIEW') statusClass = 'marked';
                      if (aq.status === 'ANSWERED_AND_MARKED') statusClass = 'answered-marked';

                      return (
                        <button
                          key={aq.id}
                          onClick={() => setActiveQuestionIndex(idx)}
                          className={`palette-btn ${statusClass} ${activeQuestionIndex === idx ? 'active' : ''}`}
                        >
                          {idx + 1}
                        </button>
                      );
                    })}
                  </div>

                  <div style={{ borderTop: '1px solid var(--border-default)', paddingTop: '16px', display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '12px', color: 'var(--text-secondary)' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#10b981' }}></div> Answered
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#f59e0b' }}></div> Marked for Review
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#6366f1' }}></div> Answered & Marked
                    </div>
                  </div>
                </Card>
              </motion.div>
            )}

            {/* ── RESULT & PERFORMANCE REPORT VIEW ── */}
            {currentView === 'result' && activeAttempt && (
              <motion.div
                key="result"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                transition={{ duration: 0.2 }}
                style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}
              >
                <Card glow="emerald" style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(16,185,129,0.15) 100%)', padding: '36px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Badge variant="success" icon={<Trophy size={14} />}>Attempt Submitted & Auto-Graded</Badge>
                      <h1 style={{ fontSize: '36px', fontWeight: 800, margin: '12px 0 6px 0' }}>Score: {activeAttempt.score} / {activeAttempt.total_marks}</h1>
                      <p style={{ color: 'var(--text-secondary)', fontSize: '15px' }}>
                        Accuracy: <strong>{activeAttempt.accuracy_pct}%</strong> • Average Speed: <strong>{activeAttempt.speed_seconds_per_q}s</strong> / question
                      </p>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '42px', fontWeight: 800, color: '#10b981' }}>98.5th</div>
                      <div style={{ fontSize: '14px', color: 'var(--text-secondary)' }}>Candidate Percentile Rank</div>
                    </div>
                  </div>
                </Card>

                {/* Question-by-Question Breakdown */}
                <Card>
                  <h3 style={{ fontSize: '20px', fontWeight: 700, marginBottom: '20px' }}>Question-by-Question Performance Review</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
                    {activeAttempt.attempt_questions.map((aq, idx) => {
                      const q = aq.question;
                      if (!q) return null;
                      return (
                        <div key={aq.id} style={{ background: 'var(--bg-surface)', padding: '20px', borderRadius: '12px', border: aq.is_correct ? '1px solid rgba(34,197,94,0.3)' : '1px solid rgba(239,68,68,0.3)' }}>
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                            <span style={{ fontSize: '16px', fontWeight: 700 }}>Q{idx + 1}. {q.content}</span>
                            <Badge variant={aq.is_correct ? 'success' : 'danger'}>
                              {aq.is_correct ? `+${q.marks} Marks` : `-${q.negative_marks} Marks`}
                            </Badge>
                          </div>

                          {q.explanation && (
                            <div style={{ background: 'var(--bg-card)', padding: '12px 16px', borderRadius: '8px', fontSize: '14px', color: 'var(--text-secondary)', marginTop: '12px', lineHeight: 1.6 }}>
                              💡 <strong>Detailed Explanation:</strong> {q.explanation}
                            </div>
                          )}

                          {q.quick_trick_explanation && (
                            <div style={{ background: 'rgba(245,158,11,0.1)', padding: '12px 16px', borderRadius: '8px', fontSize: '14px', color: '#fbbf24', marginTop: '8px', border: '1px solid rgba(245,158,11,0.3)' }}>
                              ⚡ <strong>Quick Trick Mnemonic:</strong> {q.quick_trick_explanation}
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </Card>
              </motion.div>
            )}

            {/* ── BOOKMARKS VIEW ── */}
            {currentView === 'bookmarks' && (
              <motion.div key="bookmarks" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <Card>
                  <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '20px' }}>Saved Question Bookmarks</h2>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {bookmarks.map((bm, idx) => (
                      <div key={bm.id} style={{ padding: '16px 20px', background: 'var(--bg-surface)', borderRadius: '10px', border: '1px solid var(--border-default)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div>
                          <div style={{ fontWeight: 600, fontSize: '15px' }}>Saved Question #{idx + 1}</div>
                          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>Bookmarked on {new Date(bm.created_at).toLocaleDateString()}</div>
                        </div>
                        <Button variant="primary" size="sm" onClick={() => handleStartPractice('BOOKMARKED_QUESTIONS')}>
                          Practice Now
                        </Button>
                      </div>
                    ))}
                  </div>
                </Card>
              </motion.div>
            )}

            {/* ── ANALYTICS VIEW ── */}
            {currentView === 'analytics' && (
              <motion.div key="analytics" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
                <Card>
                  <h2 style={{ fontSize: '22px', fontWeight: 700, marginBottom: '20px' }}>TopExamX Candidate Leaderboard</h2>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {leaderboard.map(item => (
                      <div key={item.rank} style={{ display: 'flex', justifyContent: 'space-between', padding: '16px 20px', background: 'var(--bg-surface)', borderRadius: '10px', border: '1px solid var(--border-default)' }}>
                        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                          <span style={{ fontWeight: 800, fontSize: '16px', color: item.rank <= 3 ? '#f59e0b' : 'var(--text-muted)' }}>#{item.rank}</span>
                          <span style={{ fontWeight: 600 }}>{item.username}</span>
                        </div>
                        <div style={{ fontWeight: 700, color: '#10b981' }}>{item.score} Marks ({item.percentile}%ile)</div>
                      </div>
                    ))}
                  </div>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </main>

      {/* AI Chat Drawer Component */}
      <AIChatDrawer isOpen={isAIDrawerOpen} onClose={() => setIsAIDrawerOpen(false)} />

      {/* Global Unified Search Modal (Ctrl+K) */}
      {isSearchOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(8px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} style={{ width: '640px', background: 'var(--bg-card)', border: '1px solid var(--border-highlight)', borderRadius: '16px', padding: '24px', boxShadow: 'var(--shadow-lg)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <input
                autoFocus
                placeholder="Search questions, topics, exams, notes..."
                value={searchQuery}
                onChange={e => handleSearch(e.target.value)}
                style={{ width: '100%', background: 'var(--bg-surface)', border: '1px solid var(--border-default)', padding: '14px 18px', borderRadius: '10px', color: 'var(--text-primary)', fontSize: '16px', outline: 'none' }}
              />
              <button onClick={() => setIsSearchOpen(false)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '20px', cursor: 'pointer', marginLeft: '14px' }}>✕</button>
            </div>

            {searchResults && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px', maxHeight: '380px', overflowY: 'auto' }}>
                {searchResults.questions.length > 0 && (
                  <div>
                    <div style={{ fontSize: '12px', color: '#818cf8', fontWeight: 700, marginBottom: '8px' }}>MATCHING QUESTIONS</div>
                    {searchResults.questions.map(q => (
                      <div key={q.id} style={{ padding: '10px 14px', background: 'var(--bg-surface)', borderRadius: '8px', fontSize: '14px', marginBottom: '6px', cursor: 'pointer' }}>
                        {q.content}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </motion.div>
        </div>
      )}
    </div>
  );
}

export default App;
