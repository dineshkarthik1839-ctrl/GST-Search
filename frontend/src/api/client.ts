import type { Attempt, ExamResult, StudentDashboardData, LeaderboardItem, BookmarkItem, UnifiedSearchResult } from '../types/platform';

const API_BASE = '/api/v1/questions';

export const apiClient = {
  async startPracticeSession(mode: string = 'PRACTICE', numQuestions: number = 10): Promise<Attempt> {
    const res = await fetch(`${API_BASE}/practice/start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ mode, num_questions: numQuestions }),
    });
    if (!res.ok) throw new Error('Failed to start practice session');
    return res.json();
  },

  async startMockTest(mockTestId: string): Promise<Attempt> {
    const res = await fetch(`${API_BASE}/tests/${mockTestId}/start`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to start mock test');
    return res.json();
  },

  async getAttempt(attemptId: string): Promise<Attempt> {
    const res = await fetch(`${API_BASE}/attempts/${attemptId}`);
    if (!res.ok) throw new Error('Failed to fetch attempt');
    return res.json();
  },

  async saveAnswer(attemptId: string, questionId: string, selectedOptionId?: string, status: string = 'ANSWERED', timeSpentSeconds: number = 0) {
    const res = await fetch(`${API_BASE}/attempts/${attemptId}/questions/${questionId}/answer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ selected_option_id: selectedOptionId, status, time_spent_seconds: timeSpentSeconds }),
    });
    return res.json();
  },

  async submitAttempt(attemptId: string): Promise<Attempt> {
    const res = await fetch(`${API_BASE}/attempts/${attemptId}/submit`, {
      method: 'POST',
    });
    if (!res.ok) throw new Error('Failed to submit attempt');
    return res.json();
  },

  async getExamResult(attemptId: string): Promise<ExamResult> {
    const res = await fetch(`${API_BASE}/attempts/${attemptId}/result`);
    if (!res.ok) throw new Error('Failed to fetch exam result');
    return res.json();
  },

  async getDashboard(): Promise<StudentDashboardData> {
    const res = await fetch(`${API_BASE}/analytics/dashboard`);
    if (!res.ok) throw new Error('Failed to fetch dashboard metrics');
    return res.json();
  },

  async getLeaderboard(period: string = 'ALL_TIME'): Promise<LeaderboardItem[]> {
    const res = await fetch(`${API_BASE}/analytics/leaderboard?period=${period}`);
    if (!res.ok) throw new Error('Failed to fetch leaderboard');
    return res.json();
  },

  async toggleBookmark(entityId: string, entityType: string = 'QUESTION'): Promise<{ bookmarked: boolean }> {
    const res = await fetch(`${API_BASE}/bookmarks/toggle`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ entity_id: entityId, entity_type: entityType }),
    });
    return res.json();
  },

  async getBookmarks(): Promise<BookmarkItem[]> {
    const res = await fetch(`${API_BASE}/bookmarks`);
    if (!res.ok) throw new Error('Failed to fetch bookmarks');
    return res.json();
  },

  async searchUnified(q: string): Promise<UnifiedSearchResult> {
    const res = await fetch(`${API_BASE}/search/unified?q=${encodeURIComponent(q)}`);
    if (!res.ok) throw new Error('Failed to search');
    return res.json();
  }
};
