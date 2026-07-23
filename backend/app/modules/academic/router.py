from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.api.deps import get_db, RequireRole
from app.modules.users.models import User
from app.modules.academic.models import Exam, ExamVersion
from app.modules.academic.repository import ExamRepository, ExamVersionRepository
from app.modules.academic.schemas import ExamResponse, ExamListResponse, FullExamVersionResponse

router = APIRouter(prefix="/academic", tags=["Academic"])

@router.get("/exams", response_model=ExamListResponse)
def list_exams(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    repo = ExamRepository(db)
    query = repo.model.__table__.select().where(repo.model.is_deleted == False)
    
    if search:
        query = query.where(repo.model.name.ilike(f"%{search}%"))
        
    items = db.execute(query.offset(skip).limit(limit)).mappings().all()
    
    # We can get total count
    from sqlalchemy import func
    count_query = db.query(func.count(repo.model.id)).filter(repo.model.is_deleted == False)
    if search:
        count_query = count_query.filter(repo.model.name.ilike(f"%{search}%"))
    total = count_query.scalar()
    
    return {
        "items": items,
        "total": total,
        "page": (skip // limit) + 1 if limit > 0 else 1,
        "size": limit
    }

@router.get("/exams/{exam_id}", response_model=ExamResponse)
def get_exam(exam_id: uuid.UUID, db: Session = Depends(get_db)):
    repo = ExamRepository(db)
    exam = repo.get_by_id(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    return exam

@router.get("/exams/{exam_id}/versions", response_model=List[FullExamVersionResponse])
def get_exam_versions(exam_id: uuid.UUID, db: Session = Depends(get_db)):
    repo = ExamVersionRepository(db)
    versions = db.query(repo.model).filter(
        repo.model.exam_id == exam_id,
        repo.model.is_deleted == False
    ).all()
    return versions

@router.delete("/exams/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam(
    exam_id: uuid.UUID, 
    db: Session = Depends(get_db),
    current_user: User = Depends(RequireRole("Admin"))
):
    repo = ExamRepository(db)
    exam = repo.get_by_id(exam_id)
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
        
    repo.delete(exam_id)
    return None
