from sqlalchemy.orm import Session
from app.db.repository import BaseRepository
from app.modules.assessment.models import Question, QuestionOption, MockTest, MockTestQuestion, PreviousYearPaper

class QuestionRepository(BaseRepository[Question]):
    def __init__(self, db: Session):
        super().__init__(Question, db)

class QuestionOptionRepository(BaseRepository[QuestionOption]):
    def __init__(self, db: Session):
        super().__init__(QuestionOption, db)

class MockTestRepository(BaseRepository[MockTest]):
    def __init__(self, db: Session):
        super().__init__(MockTest, db)

class MockTestQuestionRepository(BaseRepository[MockTestQuestion]):
    def __init__(self, db: Session):
        super().__init__(MockTestQuestion, db)

class PreviousYearPaperRepository(BaseRepository[PreviousYearPaper]):
    def __init__(self, db: Session):
        super().__init__(PreviousYearPaper, db)
