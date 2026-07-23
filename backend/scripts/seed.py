import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.db.session import SessionLocal
from app.core.logger import logger

def seed_db():
    logger.info("Seeding database...")
    db = SessionLocal()
    try:
        from app.db.metadata import Base
        from app.modules.users.models import Role, User
        from app.modules.users.repository import RoleRepository, UserRepository
        from app.core.security import get_password_hash
        
        role_repo = RoleRepository(db)
        user_repo = UserRepository(db)
        
        roles = ["Super Admin", "Admin", "Faculty", "Student"]
        role_entities = {}
        for role_name in roles:
            existing_role = role_repo.get_by_field("name", role_name)
            if not existing_role:
                new_role = role_repo.create(obj_in={"name": role_name, "description": f"{role_name} Role"})
                role_entities[role_name] = new_role
                logger.info(f"Created role: {role_name}")
            else:
                role_entities[role_name] = existing_role
                
        # Create superadmin
        superadmin_email = "admin@example.com"
        admin_user = db.query(User).filter_by(email="admin@example.com").first()
        if not admin_user:
            admin_user = User(
                email=superadmin_email,
                full_name="Super Admin",
                password_hash=get_password_hash("Admin@123"),
                is_active=True
            )
            db.add(admin_user)
            admin_user.roles.append(role_entities["Super Admin"])
            db.commit()
            db.refresh(admin_user)
            logger.info("Created super admin user.")
            
        seed_telangana_police(db)
        seed_content(db, admin_user)
            
        logger.info("Database seeding completed.")
    except Exception as e:
        logger.error(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

def seed_content(db, author):
    from app.modules.content.models import ContentItem, ContentType, ContentStatus, BookDetails, ContentRevision
    import uuid
    import datetime
    
    # 1. Book Content
    book = db.query(ContentItem).filter_by(slug="indian-polity-laxmikanth").first()
    if not book:
        book = ContentItem(
            title="Indian Polity by M. Laxmikanth",
            slug="indian-polity-laxmikanth",
            description="Comprehensive guide to Indian Polity for competitive exams.",
            content_type=ContentType.BOOK,
            status=ContentStatus.PUBLISHED,
            author_id=author.id,
            publish_date=datetime.datetime.now(datetime.timezone.utc)
        )
        db.add(book)
        db.commit()
        db.refresh(book)
        
        book_details = BookDetails(
            content_item_id=book.id,
            author_name="M. Laxmikanth",
            isbn="978-9352603633",
            page_count=800,
            publisher="McGraw Hill"
        )
        db.add(book_details)
        
        # Initial Revision
        rev = ContentRevision(
            content_item_id=book.id,
            version_number=1,
            snapshot={"title": book.title, "description": book.description},
            created_by_id=author.id,
            change_summary="Initial publication"
        )
        db.add(rev)
        db.commit()
        logger.info("Seeded ContentItem (Book: Indian Polity)")

def seed_telangana_police(db):
    from app.modules.academic.models import ExamCategory, Exam, ExamVersion, Eligibility, SelectionStage, ExamPattern, PhysicalRequirement, Subject, Chapter, Topic, ExamSubject
    
    # 1. Category
    category = db.query(ExamCategory).filter_by(name="State Police").first()
    if not category:
        category = ExamCategory(name="State Police", description="State Police Recruitment Exams")
        db.add(category)
        db.commit()
        db.refresh(category)
        
    # 2. Exam
    exam = db.query(Exam).filter_by(code="TSLPRB_CONSTABLE").first()
    if not exam:
        exam = Exam(category_id=category.id, code="TSLPRB_CONSTABLE", name="Telangana Police Constable", description="Recruitment for SCT PC Civil and Equivalent")
        db.add(exam)
        db.commit()
        db.refresh(exam)
        
    # 3. Exam Version
    version = db.query(ExamVersion).filter_by(exam_id=exam.id, cycle_name="2026 Cycle").first()
    if not version:
        version = ExamVersion(exam_id=exam.id, cycle_name="2026 Cycle", status="ACTIVE")
        db.add(version)
        db.commit()
        db.refresh(version)
        
        # 4. Eligibility
        eligibility = Eligibility(exam_version_id=version.id, age_min=18, age_max=25, education_req="Intermediate or equivalent")
        db.add(eligibility)
        
        # 5. Selection Stages
        prelims = SelectionStage(exam_version_id=version.id, name="Preliminary Written Test (PWT)", stage_order=1)
        pmt_pet = SelectionStage(exam_version_id=version.id, name="Physical Measurement & Efficiency Test (PMT/PET)", stage_order=2)
        mains = SelectionStage(exam_version_id=version.id, name="Final Written Examination (FWE)", stage_order=3)
        db.add_all([prelims, pmt_pet, mains])
        db.commit()
        db.refresh(prelims)
        db.refresh(pmt_pet)
        db.refresh(mains)
        
        # 6. Exam Patterns
        db.add(ExamPattern(selection_stage_id=prelims.id, duration_minutes=180, total_marks=200, total_questions=200, negative_marking_ratio=0.2))
        db.add(ExamPattern(selection_stage_id=mains.id, duration_minutes=180, total_marks=200, total_questions=200, negative_marking_ratio=0.2))
        
        # 7. Physical Requirements
        db.add(PhysicalRequirement(selection_stage_id=pmt_pet.id, gender="MALE", category="GENERAL", height_cm=167.6, chest_normal_cm=86.3, chest_expanded_cm=91.3, running_event="1600 meters in 7 minutes 15 seconds", long_jump="4.00 meters", shot_put="6.00 meters"))
        db.add(PhysicalRequirement(selection_stage_id=pmt_pet.id, gender="FEMALE", category="GENERAL", height_cm=152.5, running_event="800 meters in 5 minutes 20 seconds", long_jump="2.50 meters", shot_put="4.00 meters"))
        
        # 8. Subjects
        subjects = [
            ("English", "Test of English Language"),
            ("Arithmetic", "Test of Arithmetic"),
            ("General Science", "Test of General Science"),
            ("History of India", "History of India, Indian culture, Indian National Movement"),
            ("Geography of India", "Geography of India")
        ]
        
        for sub_name, sub_desc in subjects:
            subj = db.query(Subject).filter_by(name=sub_name).first()
            if not subj:
                subj = Subject(name=sub_name, description=sub_desc)
                db.add(subj)
                db.commit()
                db.refresh(subj)
            db.add(ExamSubject(exam_version_id=version.id, subject_id=subj.id, weightage=1))
            
        db.commit()
        logger.info("Seeded Telangana Police Exam structured data.")

if __name__ == "__main__":
    seed_db()
