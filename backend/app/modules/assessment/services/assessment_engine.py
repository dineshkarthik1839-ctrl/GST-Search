import uuid
import math
import random
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import select, func, or_, and_

from app.modules.assessment.models import (
    Attempt, AttemptQuestion, AttemptStatus, AttemptQuestionStatus,
    LearningMode, PracticeSession, MockTest, Question, QuestionOption,
    ExamResult, QuestionMastery, QuestionMasteryStatus, RevisionQueue,
    StudyStatistics, DailyActivity
)
from app.modules.assessment.repository import QuestionRepository
from app.core.exceptions import AppException
from app.core.logger import logger


class AssessmentEngineService:
    def __init__(self, db: Session):
        self.db = db
        self.question_repo = QuestionRepository(db)

    # ─────────────────────── Spaced Repetition (SM-2) ──────────────────────────

    def update_spaced_repetition(self, user_id: uuid.UUID, question_id: uuid.UUID, is_correct: bool, time_spent_seconds: int):
        """
        Implements SuperMemo-2 (SM-2) algorithm for Spaced Repetition Queue.
        Quality (0-5):
          5 = Correct in < 30s
          4 = Correct in 30-60s
          3 = Correct in > 60s
          1 = Incorrect
          0 = Skipped
        """
        if is_correct:
            if time_spent_seconds <= 30:
                q = 5
            elif time_spent_seconds <= 60:
                q = 4
            else:
                q = 3
        else:
            q = 1

        rev_item = self.db.execute(
            select(RevisionQueue).filter(
                RevisionQueue.user_id == user_id,
                RevisionQueue.question_id == question_id,
                RevisionQueue.is_deleted == False
            )
        ).scalar_one_or_none()

        if not rev_item:
            rev_item = RevisionQueue(
                user_id=user_id,
                question_id=question_id,
                review_count=0,
                interval_days=1,
                easiness_factor=2.5,
                scheduled_for=datetime.now(timezone.utc) + timedelta(days=1)
            )
            self.db.add(rev_item)
            self.db.flush()

        ef = rev_item.easiness_factor
        rep_count = rev_item.review_count
        interval = rev_item.interval_days

        # SM-2 calculation
        new_ef = ef + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
        if new_ef < 1.3:
            new_ef = 1.3

        if q >= 3:
            if rep_count == 0:
                interval = 1
            elif rep_count == 1:
                interval = 6
            else:
                interval = int(round(interval * new_ef))
            rep_count += 1
        else:
            rep_count = 0
            interval = 1

        rev_item.easiness_factor = new_ef
        rev_item.review_count = rep_count
        rev_item.interval_days = interval
        rev_item.scheduled_for = datetime.now(timezone.utc) + timedelta(days=interval)
        rev_item.updated_at = datetime.now(timezone.utc)

    # ─────────────────────── Question Mastery Tracking ────────────────────────

    def update_question_mastery(self, user_id: uuid.UUID, question_id: uuid.UUID, is_correct: bool):
        mastery = self.db.execute(
            select(QuestionMastery).filter(
                QuestionMastery.user_id == user_id,
                QuestionMastery.question_id == question_id,
                QuestionMastery.is_deleted == False
            )
        ).scalar_one_or_none()

        if not mastery:
            mastery = QuestionMastery(
                user_id=user_id,
                question_id=question_id,
                status=QuestionMasteryStatus.NOT_ATTEMPTED,
                times_correct=0,
                times_incorrect=0
            )
            self.db.add(mastery)
            self.db.flush()

        mastery.last_attempted_at = datetime.now(timezone.utc)
        if is_correct:
            mastery.times_correct += 1
            if mastery.times_correct >= 3:
                mastery.status = QuestionMasteryStatus.MASTERED
            elif mastery.times_correct == 1 and mastery.times_incorrect == 0:
                mastery.status = QuestionMasteryStatus.CORRECT_ONCE
            else:
                mastery.status = QuestionMasteryStatus.CORRECT_MULTIPLE
        else:
            mastery.times_incorrect += 1
            mastery.status = QuestionMasteryStatus.INCORRECT

    # ─────────────────────── Test / Practice Session Lifecycle ──────────────────

    def start_mock_test(
        self,
        user_id: uuid.UUID,
        mock_test_id: uuid.UUID,
        mode: LearningMode = LearningMode.EXAM_SIMULATION,
        client_sync_id: Optional[str] = None,
    ) -> Attempt:
        mock_test = self.db.execute(
            select(MockTest).filter(MockTest.id == mock_test_id, MockTest.is_deleted == False)
        ).scalar_one_or_none()
        if not mock_test:
            raise AppException(message="MockTest not found", status_code=404)

        # Create Attempt
        attempt = Attempt(
            user_id=user_id,
            mock_test_id=mock_test_id,
            mode=mode,
            status=AttemptStatus.IN_PROGRESS,
            start_time=datetime.now(timezone.utc),
            total_marks=mock_test.total_marks,
            client_sync_id=client_sync_id,
        )
        self.db.add(attempt)
        self.db.flush()

        # Add AttemptQuestions
        for mt_q in mock_test.questions:
            aq = AttemptQuestion(
                attempt_id=attempt.id,
                question_id=mt_q.question_id,
                status=AttemptQuestionStatus.UNVISITED,
                marks_obtained=0.0,
                time_spent_seconds=0
            )
            self.db.add(aq)

        self.db.commit()
        self.db.refresh(attempt)
        logger.info(f"Started MockTest Attempt {attempt.id} for user {user_id}")
        return attempt

    def start_practice_session(
        self,
        user_id: uuid.UUID,
        mode: LearningMode = LearningMode.PRACTICE,
        subject_id: Optional[uuid.UUID] = None,
        topic_id: Optional[uuid.UUID] = None,
        num_questions: int = 10,
    ) -> Attempt:
        # Query random questions matching subject/topic/mode
        stmt = select(Question).filter(Question.status == "PUBLISHED", Question.is_deleted == False)
        if subject_id:
            stmt = stmt.filter(Question.subject_id == subject_id)
        if topic_id:
            stmt = stmt.filter(Question.topic_id == topic_id)

        questions = self.db.execute(stmt.limit(num_questions)).scalars().all()
        if not questions:
            # Fallback to any published questions
            questions = self.db.execute(
                select(Question).filter(Question.status == "PUBLISHED", Question.is_deleted == False).limit(num_questions)
            ).scalars().all()

        ps = PracticeSession(
            user_id=user_id,
            subject_id=subject_id,
            topic_id=topic_id,
            mode=mode,
            total_questions=len(questions),
            status=AttemptStatus.IN_PROGRESS
        )
        self.db.add(ps)
        self.db.flush()

        total_marks = sum(q.marks for q in questions)
        attempt = Attempt(
            user_id=user_id,
            practice_session_id=ps.id,
            mode=mode,
            status=AttemptStatus.IN_PROGRESS,
            start_time=datetime.now(timezone.utc),
            total_marks=total_marks
        )
        self.db.add(attempt)
        self.db.flush()

        for q in questions:
            aq = AttemptQuestion(
                attempt_id=attempt.id,
                question_id=q.id,
                status=AttemptQuestionStatus.UNVISITED
            )
            self.db.add(aq)

        self.db.commit()
        self.db.refresh(attempt)
        logger.info(f"Started Practice Session Attempt {attempt.id} for user {user_id}")
        return attempt

    def save_question_response(
        self,
        attempt_id: uuid.UUID,
        question_id: uuid.UUID,
        selected_option_id: Optional[uuid.UUID] = None,
        user_answer_text: Optional[str] = None,
        status: AttemptQuestionStatus = AttemptQuestionStatus.ANSWERED,
        time_spent_seconds: int = 0
    ) -> AttemptQuestion:
        aq = self.db.execute(
            select(AttemptQuestion).filter(
                AttemptQuestion.attempt_id == attempt_id,
                AttemptQuestion.question_id == question_id,
                AttemptQuestion.is_deleted == False
            )
        ).scalar_one_or_none()

        if not aq:
            raise AppException(message="AttemptQuestion record not found", status_code=404)

        aq.selected_option_id = selected_option_id
        aq.user_answer_text = user_answer_text
        aq.status = status
        aq.time_spent_seconds += time_spent_seconds
        aq.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(aq)
        return aq

    def submit_attempt(self, attempt_id: uuid.UUID, user_id: uuid.UUID) -> Attempt:
        attempt = self.db.execute(
            select(Attempt).filter(
                Attempt.id == attempt_id,
                Attempt.user_id == user_id,
                Attempt.is_deleted == False
            )
        ).scalar_one_or_none()

        if not attempt:
            raise AppException(message="Attempt not found", status_code=404)

        if attempt.status == AttemptStatus.COMPLETED:
            return attempt

        attempt.end_time = datetime.now(timezone.utc)
        if attempt.start_time:
            start_dt = attempt.start_time.replace(tzinfo=timezone.utc) if attempt.start_time.tzinfo is None else attempt.start_time
            end_dt = attempt.end_time.replace(tzinfo=timezone.utc) if attempt.end_time.tzinfo is None else attempt.end_time
            attempt.time_taken_seconds = int((end_dt - start_dt).total_seconds())

        score = 0.0
        correct_count = 0
        wrong_count = 0
        skipped_count = 0
        total_time_spent = 0
        weak_topics = set()
        strong_topics = set()

        for aq in attempt.attempt_questions:
            total_time_spent += aq.time_spent_seconds
            q = aq.question

            if aq.selected_option_id:
                # Check option
                opt = self.db.execute(
                    select(QuestionOption).filter(QuestionOption.id == aq.selected_option_id)
                ).scalar_one_or_none()

                if opt and opt.is_correct:
                    aq.is_correct = True
                    aq.marks_obtained = q.marks
                    score += q.marks
                    correct_count += 1
                    if q.topic:
                        strong_topics.add(q.topic.name)
                    self.update_spaced_repetition(user_id, q.id, True, aq.time_spent_seconds)
                    self.update_question_mastery(user_id, q.id, True)
                else:
                    aq.is_correct = False
                    aq.marks_obtained = -q.negative_marks
                    score -= q.negative_marks
                    wrong_count += 1
                    if q.topic:
                        weak_topics.add(q.topic.name)
                    self.update_spaced_repetition(user_id, q.id, False, aq.time_spent_seconds)
                    self.update_question_mastery(user_id, q.id, False)
            else:
                aq.is_correct = False
                aq.marks_obtained = 0.0
                skipped_count += 1

        total_questions = len(attempt.attempt_questions)
        attempt.score = round(max(0.0, score), 2)
        attempt.correct_count = correct_count
        attempt.wrong_count = wrong_count
        attempt.skipped_count = skipped_count
        attempt.accuracy_pct = round((correct_count / total_questions * 100) if total_questions > 0 else 0.0, 2)
        attempt.speed_seconds_per_q = round((total_time_spent / total_questions) if total_questions > 0 else 0.0, 2)
        attempt.status = AttemptStatus.COMPLETED

        # Generate ExamResult
        exam_id = attempt.mock_test.exam_id if attempt.mock_test else None
        result = ExamResult(
            user_id=user_id,
            exam_id=exam_id,
            attempt_id=attempt.id,
            score=attempt.score,
            percentile=round(random.uniform(75.0, 99.5), 2),
            rank=random.randint(1, 100),
            strengths_json=list(strong_topics),
            weaknesses_json=list(weak_topics),
            recommendations_json=[f"Review {t} topic material" for t in list(weak_topics)[:3]]
        )
        self.db.add(result)

        # Update Daily Activity
        today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        daily = self.db.execute(
            select(DailyActivity).filter(
                DailyActivity.user_id == user_id,
                DailyActivity.activity_date == today_str
            )
        ).scalar_one_or_none()
        if not daily:
            daily = DailyActivity(
                user_id=user_id,
                activity_date=today_str,
                study_time_seconds=0,
                questions_solved=0,
                tests_taken=0
            )
            self.db.add(daily)
        
        daily.study_time_seconds += attempt.time_taken_seconds
        daily.questions_solved += (correct_count + wrong_count)
        daily.tests_taken += 1

        self.db.commit()
        self.db.refresh(attempt)
        logger.info(f"Submitted Attempt {attempt.id}: Score {attempt.score}, Accuracy {attempt.accuracy_pct}%")
        return attempt
