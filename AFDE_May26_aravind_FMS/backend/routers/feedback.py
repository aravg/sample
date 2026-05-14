from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from schemas import FeedbackCreate, FeedbackUpdate, FeedbackResponse, FeedbackStats
import crud

router = APIRouter(prefix="/feedback", tags=["Feedback"])


@router.get("/stats", response_model=FeedbackStats)
def get_stats(db: Session = Depends(get_db)):
    return crud.get_stats(db)


@router.get("", response_model=List[FeedbackResponse])
def get_all_feedback(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return crud.get_feedback_list(db, skip=skip, limit=limit)


@router.get("/{feedback_id}", response_model=FeedbackResponse)
def get_feedback(feedback_id: int, db: Session = Depends(get_db)):
    feedback = crud.get_feedback_by_id(db, feedback_id)
    if not feedback:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return feedback


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
def submit_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    return crud.create_feedback(db, feedback)


@router.put("/{feedback_id}", response_model=FeedbackResponse)
def update_feedback(feedback_id: int, feedback: FeedbackUpdate, db: Session = Depends(get_db)):
    updated = crud.update_feedback(db, feedback_id, feedback)
    if not updated:
        raise HTTPException(status_code=404, detail="Feedback not found")
    return updated


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_feedback(feedback_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_feedback(db, feedback_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Feedback not found")
