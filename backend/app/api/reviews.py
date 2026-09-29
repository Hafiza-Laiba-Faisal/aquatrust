from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.review import Review, ReviewerDecision
from app.schemas.review import ReviewCreate, ReviewResponse

router = APIRouter()


@router.post("/reviews", response_model=ReviewResponse, status_code=201)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """Submit a human review for an assessment."""
    try:
        decision = ReviewerDecision(review.reviewer_decision)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid decision. Must be one of: {[d.value for d in ReviewerDecision]}"
        )

    db_review = Review(
        assessment_id=review.assessment_id,
        reviewer_decision=decision,
        reviewer_comment=review.reviewer_comment,
    )
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
def get_review(review_id: UUID, db: Session = Depends(get_db)):
    """Get a specific review."""
    review = db.query(Review).filter(Review.id == review_id).first()
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review
