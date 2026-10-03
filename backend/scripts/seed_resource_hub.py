import os
import sys
import uuid
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.modules.content.models import (
    ContentItem, ContentType, ContentStatus,
    PdfDetails, VideoDetails, BookDetails, UserResourceProgress
)
from app.modules.engagement.models import ExamNotification, Notification, UserNotification
from app.modules.academic.models import Exam
from app.modules.users.models import User


def seed_resource_hub():
    db: Session = SessionLocal()
    try:
        print("🌱 Seeding Epic 2 Resource Library & Exam Calendar...")

        exam = db.query(Exam).filter(Exam.code.ilike("%POLICE%")).first()
        user = db.query(User).filter_by(is_active=True).first()

        # 1. Seed Exam Notifications & Calendar
        notif1 = ExamNotification(
            exam_id=exam.id if exam else None,
            title="Telangana State Level Police Recruitment Board (TSLPRB) Official Notification 2026",
            notification_type="OFFICIAL_NOTIFICATION_PDF",
            official_pdf_url="https://tslprb.gov.in/notifications/ts_police_constable_2026.pdf",
            application_start_date=datetime.now(timezone.utc) - timedelta(days=30),
            application_end_date=datetime.now(timezone.utc) + timedelta(days=15),
            exam_date=datetime.now(timezone.utc) + timedelta(days=42),
            is_active=True,
        )
        db.add(notif1)

        notif2 = ExamNotification(
            exam_id=exam.id if exam else None,
            title="TSPSC Group II Services Prelims Exam Schedule & Hall Ticket Download",
            notification_type="HALL_TICKET",
            official_pdf_url="https://tspsc.gov.in/notifications/group2_hallticket_2026.pdf",
            application_start_date=datetime.now(timezone.utc) - timedelta(days=45),
            application_end_date=datetime.now(timezone.utc) - timedelta(days=10),
            exam_date=datetime.now(timezone.utc) + timedelta(days=60),
            is_active=True,
        )
        db.add(notif2)

        # 2. Seed Content Items (Books, Notes, Videos, PDFs, Current Affairs)
        resources_data = [
            {
                "title": "Telangana Armed Police Constable Comprehensive Reference Book (2026 Edition)",
                "slug": "ts-police-constable-comprehensive-book-2026",
                "type": ContentType.BOOK,
                "desc": "Complete subject-wise guide covering General Studies, Arithmetic, Reasoning, and Telangana History.",
                "book": {"author_name": "Dr. V. K. Ramana", "isbn": "978-93-5283-102-1", "page_count": 480, "publisher": "Telangana State Academy Press"}
            },
            {
                "title": "Official TSLPRB Syllabus & Exam Pattern Handbook 2026",
                "slug": "tslprb-official-syllabus-handbook-2026",
                "type": ContentType.PDF,
                "desc": "Official pdf layout detailing physical efficiency test standards, prelims marks distribution, and syllabus breakdown.",
                "pdf": {"pdf_url": "https://cdn.topexamx.com/pdf/tslprb_official_handbook_2026.pdf", "file_size_bytes": 4200000}
            },
            {
                "title": "Telangana Movement (1948 - 2014) Video Lecture Series (Masterclass)",
                "slug": "telangana-movement-masterclass-video-series",
                "type": ContentType.VIDEO,
                "desc": "12-part video lecture series covering Gentlemen's Agreement, 1969 Agitation, KCR Fast, and AP Reorganisation Act.",
                "video": {"video_url": "https://cdn.topexamx.com/video/telangana_movement_masterclass.mp4", "duration_seconds": 4500, "transcript": "Welcome to the Telangana Movement Masterclass..."}
            },
            {
                "title": "Telangana Budget & Economic Survey 2025-2026 Summary Notes",
                "slug": "telangana-budget-economic-survey-notes-2026",
                "type": ContentType.NOTE,
                "desc": "High-yield concise notes covering GSDP growth rate, Rythu Bandhu, Kaleshwaram Project allocation, and welfare schemes."
            },
            {
                "title": "Monthly Current Affairs Digest - January 2026 (Telangana Focus)",
                "slug": "monthly-current-affairs-january-2026-telangana",
                "type": ContentType.CURRENT_AFFAIR,
                "desc": "Top 100 Telangana current affairs news, awards, appointments, and police department welfare initiatives."
            }
        ]

        created_items = []
        for rd in resources_data:
            item = ContentItem(
                title=rd["title"],
                slug=rd["slug"],
                description=rd["desc"],
                content_type=rd["type"],
                status=ContentStatus.PUBLISHED,
                language="en",
                author_id=user.id if user else None,
            )
            db.add(item)
            db.flush()

            if "book" in rd:
                db.add(BookDetails(content_item_id=item.id, **rd["book"]))
            if "pdf" in rd:
                db.add(PdfDetails(content_item_id=item.id, **rd["pdf"]))
            if "video" in rd:
                db.add(VideoDetails(content_item_id=item.id, **rd["video"]))

            created_items.append(item)

        # 3. Seed User Progress (Continue Learning)
        if user and created_items:
            progress1 = UserResourceProgress(
                user_id=user.id,
                content_item_id=created_items[0].id,
                last_page_read=42,
                completion_pct=25.0,
                last_accessed_at=datetime.now(timezone.utc) - timedelta(hours=2),
            )
            db.add(progress1)

            progress2 = UserResourceProgress(
                user_id=user.id,
                content_item_id=created_items[2].id,
                video_timestamp_seconds=1240,
                completion_pct=60.0,
                last_accessed_at=datetime.now(timezone.utc) - timedelta(hours=12),
            )
            db.add(progress2)

        db.commit()
        print("✅ Epic 2 Resource Hub & Exam Calendar seeded successfully!")
    except Exception as e:
        db.rollback()
        print(f"❌ Seeding error: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_resource_hub()
