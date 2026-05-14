from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from models import Feedback
from schemas import FeedbackCreate, FeedbackUpdate
from typing import Optional, List


def get_feedback_list(db: Session, skip: int = 0, limit: int = 100) -> List[Feedback]:
    return db.query(Feedback).order_by(Feedback.submitted_at.desc()).offset(skip).limit(limit).all()


def get_feedback_by_id(db: Session, feedback_id: int) -> Optional[Feedback]:
    return db.query(Feedback).filter(Feedback.feedback_id == feedback_id).first()


def create_feedback(db: Session, feedback: FeedbackCreate) -> Feedback:
    db_feedback = Feedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def update_feedback(db: Session, feedback_id: int, feedback: FeedbackUpdate) -> Optional[Feedback]:
    db_feedback = get_feedback_by_id(db, feedback_id)
    if not db_feedback:
        return None
    update_data = feedback.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_feedback, field, value)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback


def delete_feedback(db: Session, feedback_id: int) -> bool:
    db_feedback = get_feedback_by_id(db, feedback_id)
    if not db_feedback:
        return False
    db.delete(db_feedback)
    db.commit()
    return True


def search_feedback(
    db: Session,
    keyword: Optional[str] = None,
    rating: Optional[int] = None,
    program_name: Optional[str] = None,
) -> List[Feedback]:
    query = db.query(Feedback)

    if keyword:
        keyword_filter = f"%{keyword}%"
        query = query.filter(
            or_(
                Feedback.participant_name.ilike(keyword_filter),
                Feedback.program_name.ilike(keyword_filter),
                Feedback.comments.ilike(keyword_filter),
            )
        )
    if rating is not None:
        query = query.filter(Feedback.rating == rating)
    if program_name:
        query = query.filter(Feedback.program_name.ilike(f"%{program_name}%"))

    return query.order_by(Feedback.submitted_at.desc()).all()


def get_stats(db: Session):
    total = db.query(func.count(Feedback.feedback_id)).scalar() or 0
    avg = db.query(func.avg(Feedback.rating)).scalar() or 0.0
    recent = db.query(Feedback).order_by(Feedback.submitted_at.desc()).limit(5).all()
    return {
        "total_count": total,
        "average_rating": round(float(avg), 2),
        "recent_feedback": recent,
    }
