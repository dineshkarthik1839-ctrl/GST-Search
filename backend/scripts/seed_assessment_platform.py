import sys
import os
import random
import uuid
from datetime import datetime, timezone, timedelta

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import app.db.metadata
from app.db.session import SessionLocal
from app.core.logger import logger
from app.modules.academic.models import Exam
from app.modules.users.models import User
from app.modules.assessment.models import (
    MockTest, MockTestQuestion, Question, Attempt, AttemptQuestion,
    AttemptStatus, AttemptQuestionStatus, LearningMode, ExamResult,
    Leaderboard, DailyActivity, RevisionQueue, QuestionMastery,
    QuestionMasteryStatus, StudyStatistics
)
from app.modules.engagement.models import Bookmark, BookmarkType

def seed_assessment_platform():
    logger.info("Seeding Assessment Platform Attempts, Leaderboards & Analytics...")
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(email="admin@example.com").first()
        if not user:
            user = db.query(User).first()
        if not user:
            logger.error("No user found. Please run seed.py first.")
            return

        exam = db.query(Exam).first()
        if not exam:
            logger.error("No exam found. Please run seed.py first.")
            return

        questions = db.query(Question).filter(Question.status == "PUBLISHED").limit(50).all()
        if not questions:
            logger.error("No questions found. Please run seed_questions.py first.")
            return

        # 1. Create a MockTest
        mock_test = db.query(MockTest).filter_by(exam_id=exam.id).first()
        if not mock_test:
            mock_test = MockTest(
                exam_id=exam.id,
                title="Telangana Police Constable Full Mock Test 1",
                duration_minutes=120,
                total_marks=len(questions) * 1.5
            )
            db.add(mock_test)
            db.flush()

            for idx, q in enumerate(questions):
                mtq = MockTestQuestion(
                    mock_test_id=mock_test.id,
                    question_id=q.id,
                    marks=q.marks,
                    negative_marks=q.negative_marks
                )
                db.add(mtq)
            db.commit()
            db.refresh(mock_test)

        # 2. Create Completed Attempt & ExamResult
        attempt = Attempt(
            user_id=user.id,
            mock_test_id=mock_test.id,
            mode=LearningMode.EXAM_SIMULATION,
            status=AttemptStatus.COMPLETED,
            start_time=datetime.now(timezone.utc) - timedelta(hours=2),
            end_time=datetime.now(timezone.utc),
            time_taken_seconds=5400,
            score=42.5,
            total_marks=mock_test.total_marks,
            accuracy_pct=85.0,
            speed_seconds_per_q=45.0,
            correct_count=35,
            wrong_count=10,
            skipped_count=5
        )
        db.add(attempt)
        db.flush()

        for idx, q in enumerate(questions):
            is_correct = (idx % 4 != 0)
            selected_opt = q.options[0].id if q.options else None
            aq = AttemptQuestion(
                attempt_id=attempt.id,
                question_id=q.id,
                selected_option_id=selected_opt,
                status=AttemptQuestionStatus.ANSWERED if idx < 45 else AttemptQuestionStatus.UNVISITED,
                is_correct=is_correct if idx < 45 else None,
                marks_obtained=q.marks if (idx < 45 and is_correct) else (-q.negative_marks if idx < 45 else 0.0),
                time_spent_seconds=random.randint(20, 90)
            )
            db.add(aq)

        res = ExamResult(
            user_id=user.id,
            exam_id=exam.id,
            attempt_id=attempt.id,
            score=42.5,
            percentile=98.5,
            rank=3,
            strengths_json=["Arithmetic", "Indian Polity", "English"],
            weaknesses_json=["Geography of Telangana", "Physics"],
            recommendations_json=["Review Telangana Rivers", "Practice Ratio & Proportion Quizzes"]
        )
        db.add(res)

        # 3. Create Leaderboard Entries
        lb1 = Leaderboard(user_id=user.id, exam_id=exam.id, mock_test_id=mock_test.id, score=42.5, rank=3, percentile=98.5, period="ALL_TIME")
        db.add(lb1)

        # 4. Create Revision Queue Items
        for q in questions[:10]:
            rq = RevisionQueue(
                user_id=user.id,
                question_id=q.id,
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=1),
                review_count=1,
                interval_days=1,
                easiness_factor=2.5
            )
            db.add(rq)

            qm = QuestionMastery(
                user_id=user.id,
                question_id=q.id,
                status=QuestionMasteryStatus.CORRECT_ONCE,
                times_correct=1,
                times_incorrect=0,
                last_attempted_at=datetime.now(timezone.utc)
            )
            db.add(qm)

        # 5. Bookmarks
        for q in questions[:5]:
            bm = Bookmark(user_id=user.id, entity_type=BookmarkType.QUESTION, entity_id=q.id)
            db.add(bm)

        # 6. Daily Activity (Heatmap data for last 7 days)
        for d in range(7):
            dt_str = (datetime.now(timezone.utc) - timedelta(days=d)).strftime("%Y-%m-%d")
            da = DailyActivity(
                user_id=user.id,
                activity_date=dt_str,
                study_time_seconds=random.randint(1800, 7200),
                questions_solved=random.randint(20, 80),
                tests_taken=1 if d % 2 == 0 else 0
            )
            db.add(da)

        # 7. Study Statistics
        stats = db.query(StudyStatistics).filter_by(user_id=user.id).first()
        if not stats:
            stats = StudyStatistics(
                user_id=user.id,
                total_questions_attempted=150,
                overall_accuracy_pct=82.4,
                current_streak_days=7,
                longest_streak_days=15,
                learning_health_score=92.0,
                retention_pct=88.5,
                subject_accuracy_json={"Arithmetic": 85.0, "General Science": 78.0, "History of India": 90.0, "English": 84.0}
            )
            db.add(stats)

        db.commit()
        logger.info("Successfully seeded Assessment Platform data!")
    except Exception as e:
        logger.error(f"Error seeding assessment platform: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_assessment_platform()
