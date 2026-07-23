from pydantic import BaseModel
from typing import List, Optional
import uuid

class ExamLanguageBase(BaseModel):
    language: str

class PhysicalRequirementBase(BaseModel):
    gender: str
    category: Optional[str] = None
    height_cm: Optional[float] = None
    chest_normal_cm: Optional[float] = None
    chest_expanded_cm: Optional[float] = None
    running_event: Optional[str] = None
    long_jump: Optional[str] = None
    shot_put: Optional[str] = None

class ExamPatternBase(BaseModel):
    duration_minutes: Optional[int] = None
    total_marks: Optional[float] = None
    total_questions: Optional[int] = None
    negative_marking_ratio: Optional[float] = None

class SelectionStageBase(BaseModel):
    name: str
    stage_order: int = 1
    description: Optional[str] = None

class EligibilityBase(BaseModel):
    age_min: Optional[int] = None
    age_max: Optional[int] = None
    education_req: Optional[str] = None
    additional_reqs: Optional[str] = None

class ExamVersionBase(BaseModel):
    cycle_name: str
    status: str = "UPCOMING"
    notification_url: Optional[str] = None

class ExamBase(BaseModel):
    category_id: uuid.UUID
    code: str
    name: str
    description: Optional[str] = None

class ExamResponse(ExamBase):
    id: uuid.UUID
    class Config:
        from_attributes = True

class ExamVersionResponse(ExamVersionBase):
    id: uuid.UUID
    exam_id: uuid.UUID
    class Config:
        from_attributes = True

class FullExamVersionResponse(ExamVersionResponse):
    eligibility: Optional[EligibilityBase] = None
    languages: List[ExamLanguageBase] = []
    
class ExamListResponse(BaseModel):
    items: List[ExamResponse]
    total: int
    page: int
    size: int
