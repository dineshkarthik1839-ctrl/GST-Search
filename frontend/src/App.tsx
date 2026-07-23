import { useState, useEffect } from 'react';
import { apiClient } from './api/client';
import type { Attempt, StudentDashboardData, LeaderboardItem, BookmarkItem, UnifiedSearchResult } from './types/platform';

type ViewMode = 'dashboard' | 'browser' | 'test' | 'result' | 'bookmarks' | 'analytics';

export function App() {
  const [currentView, setCurrentView] = useState<ViewMode>('dashboard');
  const [dashboardData, setDashboardData] = useState<StudentDashboardData | null>(null);
  const [activeAttempt, setActiveAttempt] = useState<Attempt | null>(null);
  const [activeQuestionIndex, setActiveQuestionIndex] = useState<number>(0);
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [searchResults, setSearchResults] = useState<UnifiedSearchResult | null>(null);
  const [isSearchOpen, setIsSearchOpen] = useState<boolean>(false);
  const [bookmarks, setBookmarks] = useState<BookmarkItem[]>([]);
  const [leaderboard, setLeaderboard] = useState<LeaderboardItem[]>([]);
  const [timerSeconds, setTimerSeconds] = useState<number>(3600);
  const [isBookmarked, setIsBookmarked] = useState<boolean>(false);

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

  // Keyboard shortcuts (1-4 select option, N next, P prev, M mark, S submit)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (currentView !== 'test' || !activeAttempt) return;
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
      } else if (e.key.toLowerCase() === 'm') {
        handleMarkForReview();
      } else if (e.key.toLowerCase() === 'k' && (e.ctrlKey || e.metaKey)) {
        e.preventDefault();
        setIsSearchOpen(prev => !prev);
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

    const res = await apiClient.toggleBookmark(currentQ.id, 'QUESTION');
    setIsBookmarked(res.bookmarked);
    loadBookmarks();
  };

  const handleSubmitTest = async () => {
    if (!activeAttempt) return;
    try {
      const completed = await apiClient.submitAttempt(activeAttempt.id);
      setActiveAttempt(completed);
      setCurrentView('result');
      loadDashboard();
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
    <div style={{ display: 'flex', width: '100%', minHeight: '100vh', background: '#0a0b0e', color: '#f3f4f6' }}>
      {/* ── Sidebar Navigation ── */}
      <aside style={{ width: '260px', background: '#12141a', borderRight: '1px solid #232736', padding: '24px 16px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
        <div>
          <h2 style={{ fontSize: '18px', fontWeight: '800', color: '#818cf8', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>⚡</span> GOVEXAM PLATFORM
          </h2>
          <span style={{ fontSize: '11px', color: '#6b7280', textTransform: 'uppercase', letterSpacing: '0.1em' }}>Telangana Intelligence Platform</span>
        </div>

        <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <button onClick={() => setCurrentView('dashboard')} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 14px', borderRadius: '8px', background: currentView === 'dashboard' ? 'rgba(99,102,241,0.15)' : 'transparent', color: currentView === 'dashboard' ? '#818cf8' : '#9ca3af', border: 'none', cursor: 'pointer', fontWeight: '600', textAlign: 'left' }}>
            <span>📊</span> Dashboard
          </button>
          <button onClick={() => setCurrentView('browser')} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 14px', borderRadius: '8px', background: currentView === 'browser' ? 'rgba(99,102,241,0.15)' : 'transparent', color: currentView === 'browser' ? '#818cf8' : '#9ca3af', border: 'none', cursor: 'pointer', fontWeight: '600', textAlign: 'left' }}>
            <span>📚</span> Syllabus & Exams
          </button>
          <button onClick={() => handleStartPractice('PRACTICE')} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 14px', borderRadius: '8px', background: currentView === 'test' ? 'rgba(99,102,241,0.15)' : 'transparent', color: currentView === 'test' ? '#818cf8' : '#9ca3af', border: 'none', cursor: 'pointer', fontWeight: '600', textAlign: 'left' }}>
            <span>📝</span> Practice & Test Engine
          </button>
          <button onClick={() => setCurrentView('bookmarks')} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 14px', borderRadius: '8px', background: currentView === 'bookmarks' ? 'rgba(99,102,241,0.15)' : 'transparent', color: currentView === 'bookmarks' ? '#818cf8' : '#9ca3af', border: 'none', cursor: 'pointer', fontWeight: '600', textAlign: 'left' }}>
            <span>🔖</span> Bookmarks ({bookmarks.length})
          </button>
          <button onClick={() => setCurrentView('analytics')} style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 14px', borderRadius: '8px', background: currentView === 'analytics' ? 'rgba(99,102,241,0.15)' : 'transparent', color: currentView === 'analytics' ? '#818cf8' : '#9ca3af', border: 'none', cursor: 'pointer', fontWeight: '600', textAlign: 'left' }}>
            <span>📈</span> Analytics & Retention
          </button>
        </nav>

        <div style={{ marginTop: 'auto', background: '#161822', padding: '14px', borderRadius: '10px', border: '1px solid #232736' }}>
          <div style={{ fontSize: '12px', color: '#9ca3af' }}>Current Streak</div>
          <div style={{ fontSize: '20px', fontWeight: '800', color: '#f59e0b' }}>🔥 7 Days Streak</div>
          <div style={{ fontSize: '11px', color: '#6b7280', marginTop: '4px' }}>Keep solving daily to maintain retention!</div>
        </div>
      </aside>

      {/* ── Main View Container ── */}
      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflowY: 'auto' }}>
        {/* Top Header Bar */}
        <header style={{ height: '64px', background: '#12141a', borderBottom: '1px solid #232736', padding: '0 28px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <button onClick={() => setIsSearchOpen(true)} style={{ background: '#161822', border: '1px solid #232736', padding: '8px 16px', borderRadius: '8px', color: '#6b7280', fontSize: '13px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '12px', width: '320px' }}>
            <span>🔍 Search questions, topics, exams...</span>
            <kbd style={{ background: '#232736', padding: '2px 6px', borderRadius: '4px', fontSize: '11px', color: '#9ca3af' }}>Ctrl+K</kbd>
          </button>

          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <span className="badge badge-success">Telangana Police Constable 2026</span>
            <div style={{ width: '36px', height: '36px', borderRadius: '50%', background: '#6366f1', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: '700', fontSize: '14px' }}>DK</div>
          </div>
        </header>

        <div style={{ padding: '28px', flex: 1 }}>
          {/* ── DASHBOARD VIEW ── */}
          {currentView === 'dashboard' && dashboardData && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h1 style={{ fontSize: '26px', fontWeight: '800' }}>Welcome back, Student 👋</h1>
                  <p style={{ color: '#9ca3af', fontSize: '14px' }}>Target: Telangana Police Recruitment Exam 2026</p>
                </div>
                <button onClick={() => handleStartPractice('EXAM_SIMULATION')} style={{ background: '#6366f1', color: '#fff', padding: '12px 24px', borderRadius: '8px', border: 'none', fontWeight: '700', cursor: 'pointer', boxShadow: '0 4px 12px rgba(99,102,241,0.3)' }}>
                  ▶ Start Full Mock Test
                </button>
              </div>

              {/* Bento Grid Metrics */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
                <div className="bento-card">
                  <div style={{ color: '#6b7280', fontSize: '12px', fontWeight: '600' }}>OVERALL ACCURACY</div>
                  <div style={{ fontSize: '28px', fontWeight: '800', color: '#10b981', marginTop: '6px' }}>{dashboardData.overall_accuracy_pct}%</div>
                  <span className="badge badge-success" style={{ marginTop: '8px' }}>Top 5% Candidate</span>
                </div>
                <div className="bento-card">
                  <div style={{ color: '#6b7280', fontSize: '12px', fontWeight: '600' }}>LEARNING HEALTH SCORE</div>
                  <div style={{ fontSize: '28px', fontWeight: '800', color: '#818cf8', marginTop: '6px' }}>{dashboardData.learning_health_score}/100</div>
                  <span className="badge badge-primary" style={{ marginTop: '8px' }}>Optimal Retention</span>
                </div>
                <div className="bento-card">
                  <div style={{ color: '#6b7280', fontSize: '12px', fontWeight: '600' }}>QUESTIONS ATTEMPTED</div>
                  <div style={{ fontSize: '28px', fontWeight: '800', color: '#f3f4f6', marginTop: '6px' }}>{dashboardData.total_questions_attempted}</div>
                  <span style={{ fontSize: '12px', color: '#9ca3af' }}>From 500 Question Bank</span>
                </div>
                <div className="bento-card">
                  <div style={{ color: '#6b7280', fontSize: '12px', fontWeight: '600' }}>REVISION DUE (SM-2)</div>
                  <div style={{ fontSize: '28px', fontWeight: '800', color: '#f59e0b', marginTop: '6px' }}>{dashboardData.revision_due_count} Items</div>
                  <button onClick={() => handleStartPractice('REVISION')} style={{ background: 'transparent', color: '#fbbf24', border: 'none', cursor: 'pointer', fontSize: '12px', fontWeight: '700', padding: 0, marginTop: '6px' }}>Revise Now →</button>
                </div>
              </div>

              {/* Subject Accuracy & Weak Topics */}
              <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
                <div className="bento-card">
                  <h3 style={{ fontSize: '16px', fontWeight: '700', marginBottom: '16px' }}>Subject Mastery & Accuracy</h3>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                    {Object.entries(dashboardData.subject_accuracy).map(([subj, acc]) => (
                      <div key={subj}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
                          <span>{subj}</span>
                          <span style={{ fontWeight: '700', color: acc >= 80 ? '#10b981' : '#f59e0b' }}>{acc}%</span>
                        </div>
                        <div style={{ height: '8px', background: '#232736', borderRadius: '4px', overflow: 'hidden' }}>
                          <div style={{ width: `${acc}%`, height: '100%', background: acc >= 80 ? '#10b981' : '#f59e0b', borderRadius: '4px' }}></div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bento-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  <h3 style={{ fontSize: '16px', fontWeight: '700' }}>Recommended Practice</h3>
                  <div style={{ background: '#12141a', padding: '14px', borderRadius: '8px', border: '1px solid #232736' }}>
                    <div style={{ fontSize: '12px', color: '#ef4444', fontWeight: '700' }}>⚠️ WEAK TOPICS DETECTED</div>
                    <div style={{ fontSize: '14px', fontWeight: '600', marginTop: '4px' }}>Geography of Telangana & Physical Geography</div>
                    <button onClick={() => handleStartPractice('WEAK_TOPIC_PRACTICE')} style={{ marginTop: '10px', background: '#ef4444', color: '#fff', border: 'none', padding: '8px 14px', borderRadius: '6px', fontSize: '12px', fontWeight: '700', cursor: 'pointer', width: '100%' }}>
                      Practice Weak Topics Now
                    </button>
                  </div>

                  <div style={{ background: '#12141a', padding: '14px', borderRadius: '8px', border: '1px solid #232736' }}>
                    <div style={{ fontSize: '12px', color: '#3b82f6', fontWeight: '700' }}>📅 UPCOMING EXAM COUNTDOWN</div>
                    <div style={{ fontSize: '18px', fontWeight: '800', marginTop: '4px' }}>42 Days Remaining</div>
                    <div style={{ fontSize: '12px', color: '#9ca3af' }}>Telangana Police Constable Prelims 2026</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ── QUESTION TEST SCREEN (Supports 10 Learning Modes) ── */}
          {currentView === 'test' && activeAttempt && currentQ && (
            <div style={{ display: 'grid', gridTemplateColumns: '3fr 1fr', gap: '20px', height: 'calc(100vh - 120px)' }}>
              {/* Main Question Panel */}
              <div className="bento-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid #232736', paddingBottom: '14px', marginBottom: '20px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span className="badge badge-primary">{activeAttempt.mode}</span>
                      <span style={{ fontSize: '14px', color: '#9ca3af' }}>Question {activeQuestionIndex + 1} of {activeAttempt.attempt_questions.length}</span>
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                      <div style={{ fontFamily: 'JetBrains Mono', fontSize: '18px', fontWeight: '800', color: timerSeconds < 300 ? '#ef4444' : '#f59e0b' }}>
                        ⏱ {formatTimer(timerSeconds)}
                      </div>
                      <button onClick={handleToggleBookmark} style={{ background: 'transparent', border: '1px solid #232736', color: isBookmarked ? '#f59e0b' : '#9ca3af', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer' }}>
                        {isBookmarked ? '★ Bookmarked' : '☆ Bookmark'}
                      </button>
                    </div>
                  </div>

                  {/* Question Content */}
                  <div style={{ fontSize: '18px', fontWeight: '600', lineHeight: '1.6', marginBottom: '24px' }}>
                    {currentQ.content}
                  </div>

                  {/* Options */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {currentQ.options.map((opt, idx) => {
                      const isSelected = currentAQ?.selected_option_id === opt.id;
                      return (
                        <div
                          key={opt.id}
                          onClick={() => handleSelectOption(opt.id)}
                          style={{
                            padding: '14px 18px',
                            borderRadius: '10px',
                            border: isSelected ? '2px solid #6366f1' : '1px solid #232736',
                            background: isSelected ? 'rgba(99,102,241,0.15)' : '#12141a',
                            cursor: 'pointer',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '14px',
                            transition: 'all 0.15s ease'
                          }}
                        >
                          <div style={{ width: '26px', height: '26px', borderRadius: '50%', border: isSelected ? '2px solid #6366f1' : '1px solid #4b5563', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: '700', color: isSelected ? '#818cf8' : '#9ca3af' }}>
                            {String.fromCharCode(65 + idx)}
                          </div>
                          <div style={{ fontSize: '15px', color: isSelected ? '#fff' : '#d1d5db' }}>{opt.content}</div>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Footer Controls */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderTop: '1px solid #232736', paddingTop: '16px', marginTop: '20px' }}>
                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      disabled={activeQuestionIndex === 0}
                      onClick={() => setActiveQuestionIndex(prev => prev - 1)}
                      style={{ padding: '10px 18px', borderRadius: '8px', background: '#12141a', border: '1px solid #232736', color: '#9ca3af', cursor: activeQuestionIndex === 0 ? 'not-allowed' : 'pointer', fontWeight: '600' }}
                    >
                      ← Previous (P)
                    </button>
                    <button
                      onClick={handleMarkForReview}
                      style={{ padding: '10px 18px', borderRadius: '8px', background: 'rgba(245,158,11,0.15)', border: '1px solid rgba(245,158,11,0.3)', color: '#fbbf24', cursor: 'pointer', fontWeight: '600' }}
                    >
                      🔖 Mark for Review (M)
                    </button>
                  </div>

                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      disabled={activeQuestionIndex === activeAttempt.attempt_questions.length - 1}
                      onClick={() => setActiveQuestionIndex(prev => prev + 1)}
                      style={{ padding: '10px 18px', borderRadius: '8px', background: '#12141a', border: '1px solid #232736', color: '#fff', cursor: 'pointer', fontWeight: '600' }}
                    >
                      Next → (N)
                    </button>
                    <button
                      onClick={handleSubmitTest}
                      style={{ padding: '10px 24px', borderRadius: '8px', background: '#10b981', border: 'none', color: '#fff', fontWeight: '700', cursor: 'pointer' }}
                    >
                      Submit Test
                    </button>
                  </div>
                </div>
              </div>

              {/* Question Palette Drawer */}
              <div className="bento-card" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                <h3 style={{ fontSize: '15px', fontWeight: '700' }}>Question Palette</h3>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '8px', maxHeight: '350px', overflowY: 'auto' }}>
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

                <div style={{ borderTop: '1px solid #232736', paddingTop: '14px', display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '11px', color: '#9ca3af' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#10b981' }}></div> Answered
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#f59e0b' }}></div> Marked for Review
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#6366f1' }}></div> Answered & Marked
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ── RESULT & PERFORMANCE REPORT SCREEN ── */}
          {currentView === 'result' && activeAttempt && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <div className="bento-card" style={{ background: 'linear-gradient(135deg, rgba(99,102,241,0.2) 0%, rgba(16,185,129,0.1) 100%)', border: '1px solid #33384f', padding: '32px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <span className="badge badge-success">Attempt Finalized</span>
                  <h1 style={{ fontSize: '32px', fontWeight: '800', margin: '8px 0' }}>Score: {activeAttempt.score} / {activeAttempt.total_marks}</h1>
                  <p style={{ color: '#9ca3af' }}>Accuracy: {activeAttempt.accuracy_pct}% • Speed: {activeAttempt.speed_seconds_per_q}s per question</p>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontSize: '36px', fontWeight: '800', color: '#10b981' }}>98.5th Percentile</div>
                  <div style={{ color: '#9ca3af', fontSize: '13px' }}>Rank 3 out of 100 Candidates</div>
                </div>
              </div>

              {/* Question Breakdown */}
              <div className="bento-card">
                <h3 style={{ fontSize: '18px', fontWeight: '700', marginBottom: '16px' }}>Detailed Question-by-Question Review</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                  {activeAttempt.attempt_questions.map((aq, idx) => {
                    const q = aq.question;
                    if (!q) return null;
                    return (
                      <div key={aq.id} style={{ background: '#12141a', padding: '16px', borderRadius: '10px', border: aq.is_correct ? '1px solid rgba(16,185,129,0.3)' : '1px solid rgba(239,68,68,0.3)' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
                          <span style={{ fontWeight: '700' }}>Q{idx + 1}. {q.content}</span>
                          <span style={{ fontWeight: '700', color: aq.is_correct ? '#10b981' : '#ef4444' }}>
                            {aq.is_correct ? `+${q.marks} Marks` : `-${q.negative_marks} Marks`}
                          </span>
                        </div>
                        {q.explanation && (
                          <div style={{ background: '#161822', padding: '10px 14px', borderRadius: '6px', fontSize: '13px', color: '#9ca3af', marginTop: '8px' }}>
                            💡 <strong>Explanation:</strong> {q.explanation}
                          </div>
                        )}
                        {q.quick_trick_explanation && (
                          <div style={{ background: 'rgba(245,158,11,0.1)', padding: '10px 14px', borderRadius: '6px', fontSize: '13px', color: '#fbbf24', marginTop: '6px' }}>
                            ⚡ <strong>Quick Trick:</strong> {q.quick_trick_explanation}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}

          {/* ── BOOKMARKS VIEW ── */}
          {currentView === 'bookmarks' && (
            <div className="bento-card">
              <h2 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '16px' }}>Your Saved Question Bookmarks</h2>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                {bookmarks.map((bm, i) => (
                  <div key={bm.id} style={{ padding: '14px', background: '#12141a', borderRadius: '8px', border: '1px solid #232736', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontWeight: '600' }}>Bookmark #{i + 1} ({bm.entity_type})</div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>Saved on {new Date(bm.created_at).toLocaleDateString()}</div>
                    </div>
                    <button onClick={() => handleStartPractice('BOOKMARKED_QUESTIONS')} style={{ background: '#6366f1', color: '#fff', border: 'none', padding: '6px 14px', borderRadius: '6px', cursor: 'pointer', fontWeight: '600' }}>Practice Now</button>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* ── ANALYTICS VIEW ── */}
          {currentView === 'analytics' && dashboardData && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
              <div className="bento-card">
                <h2 style={{ fontSize: '20px', fontWeight: '700', marginBottom: '14px' }}>Competitive Exam Leaderboard</h2>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                  {leaderboard.map(item => (
                    <div key={item.rank} style={{ display: 'flex', justifyContent: 'space-between', padding: '12px 16px', background: '#12141a', borderRadius: '8px', border: '1px solid #232736' }}>
                      <div style={{ display: 'flex', gap: '14px', alignItems: 'center' }}>
                        <span style={{ fontWeight: '800', color: item.rank <= 3 ? '#f59e0b' : '#9ca3af' }}>#{item.rank}</span>
                        <span style={{ fontWeight: '600' }}>{item.username}</span>
                      </div>
                      <div style={{ fontWeight: '700', color: '#10b981' }}>{item.score} Marks ({item.percentile}%ile)</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* ── Global Unified Search Modal (Ctrl+K) ── */}
      {isSearchOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(8px)', zIndex: 1000, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <div style={{ width: '600px', background: '#161822', border: '1px solid #33384f', borderRadius: '14px', padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <input
                autoFocus
                placeholder="Search questions, subjects, topics, exams..."
                value={searchQuery}
                onChange={e => handleSearch(e.target.value)}
                style={{ width: '100%', background: '#12141a', border: '1px solid #232736', padding: '12px 16px', borderRadius: '8px', color: '#fff', fontSize: '15px', outline: 'none' }}
              />
              <button onClick={() => setIsSearchOpen(false)} style={{ background: 'transparent', border: 'none', color: '#9ca3af', fontSize: '20px', cursor: 'pointer', marginLeft: '12px' }}>✕</button>
            </div>

            {searchResults && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '350px', overflowY: 'auto' }}>
                {searchResults.questions.length > 0 && (
                  <div>
                    <div style={{ fontSize: '12px', color: '#818cf8', fontWeight: '700', marginBottom: '6px' }}>QUESTIONS</div>
                    {searchResults.questions.map(q => (
                      <div key={q.id} style={{ padding: '8px 12px', background: '#12141a', borderRadius: '6px', fontSize: '13px', marginBottom: '4px' }}>
                        {q.content}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
