from sqlalchemy.orm import Session
from app.db.repository import BaseRepository
from app.modules.academic.models import ExamCategory, Exam, Subject, ExamSubject, Chapter, Topic

class ExamCategoryRepository(BaseRepository[ExamCategory]):
    def __init__(self, db: Session):
        super().__init__(ExamCategory, db)

class ExamRepository(BaseRepository[Exam]):
    def __init__(self, db: Session):
        super().__init__(Exam, db)

class SubjectRepository(BaseRepository[Subject]):
    def __init__(self, db: Session):
        super().__init__(Subject, db)

class ExamSubjectRepository(BaseRepository[ExamSubject]):
    def __init__(self, db: Session):
        super().__init__(ExamSubject, db)

class ChapterRepository(BaseRepository[Chapter]):
    def __init__(self, db: Session):
        super().__init__(Chapter, db)

class TopicRepository(BaseRepository[Topic]):
    def __init__(self, db: Session):
        super().__init__(Topic, db)

from app.modules.academic.models import ExamVersion, Eligibility, SelectionStage, ExamPattern, PhysicalRequirement, ExamLanguage

class ExamVersionRepository(BaseRepository[ExamVersion]):
    def __init__(self, db: Session):
        super().__init__(ExamVersion, db)

class EligibilityRepository(BaseRepository[Eligibility]):
    def __init__(self, db: Session):
        super().__init__(Eligibility, db)

class SelectionStageRepository(BaseRepository[SelectionStage]):
    def __init__(self, db: Session):
        super().__init__(SelectionStage, db)

class ExamPatternRepository(BaseRepository[ExamPattern]):
    def __init__(self, db: Session):
        super().__init__(ExamPattern, db)

class PhysicalRequirementRepository(BaseRepository[PhysicalRequirement]):
    def __init__(self, db: Session):
        super().__init__(PhysicalRequirement, db)

class ExamLanguageRepository(BaseRepository[ExamLanguage]):
    def __init__(self, db: Session):
        super().__init__(ExamLanguage, db)
