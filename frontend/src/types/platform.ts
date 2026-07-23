export interface QuestionOption {
  id: string;
  question_id: string;
  content: string;
  option_index: number;
  is_correct: boolean;
  explanation?: string;
}

export interface Question {
  id: string;
  content: string;
  question_type: string;
  difficulty: string;
  bloom_taxonomy?: string;
  marks: number;
  negative_marks: number;
  explanation?: string;
  detailed_explanation?: string;
  quick_trick_explanation?: string;
  video_explanation_url?: string;
  options: QuestionOption[];
}

export interface AttemptQuestion {
  id: string;
  question_id: string;
  selected_option_id?: string;
  status: 'UNVISITED' | 'VISITED' | 'ANSWERED' | 'MARKED_FOR_REVIEW' | 'ANSWERED_AND_MARKED';
  is_correct?: boolean;
  marks_obtained: number;
  time_spent_seconds: number;
  question?: Question;
}

export interface Attempt {
  id: string;
  user_id: string;
  mock_test_id?: string;
  mode: string;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'ABANDONED';
  start_time: string;
  end_time?: string;
  time_taken_seconds: number;
  score: number;
  total_marks: number;
  accuracy_pct: number;
  speed_seconds_per_q: number;
  correct_count: number;
  wrong_count: number;
  skipped_count: number;
  attempt_questions: AttemptQuestion[];
}

export interface ExamResult {
  id: string;
  attempt_id: string;
  score: number;
  percentile: number;
  rank: number;
  strengths_json?: string[];
  weaknesses_json?: string[];
  recommendations_json?: string[];
}

export interface StudentDashboardData {
  total_questions_attempted: number;
  overall_accuracy_pct: number;
  current_streak_days: number;
  longest_streak_days: number;
  learning_health_score: number;
  retention_pct: number;
  revision_due_count: number;
  mastered_questions_count: number;
  subject_accuracy: Record<string, number>;
  active_test_attempt_id?: string;
  active_test_title?: string;
  daily_activity_heatmap: { date: string; study_time_seconds: number; questions_solved: number; tests_taken: number }[];
  weak_topics: string[];
  strong_topics: string[];
  upcoming_exam: { name: string; days_remaining: number; target_score: number };
}

export interface LeaderboardItem {
  rank: number;
  username: string;
  score: number;
  percentile: number;
}

export interface BookmarkItem {
  id: string;
  entity_type: string;
  entity_id: string;
  created_at: string;
}

export interface UnifiedSearchResult {
  query: string;
  exams: { id: string; name: string; code: string }[];
  subjects: { id: string; name: string }[];
  topics: { id: string; name: string; chapter_id: string }[];
  content: { id: string; title: string; content_type: string; slug: string }[];
  questions: { id: string; content: string; difficulty: string }[];
}
