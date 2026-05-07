from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas

# =========================
# ROUTER
# =========================
router = APIRouter(prefix="/mentee", tags=["Mentee"])

# =========================
# DB CONNECTION
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# DASHBOARD API
# =========================
@router.get("/dashboard/{mentee_id}")
def get_dashboard(mentee_id: int, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == mentee_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    tasks = db.query(models.Task).filter(models.Task.mentee_id == mentee_id).all()

    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == "completed")
    pending = total - completed
    performance = int((completed / total) * 100) if total > 0 else 0

    task_list = [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "deadline": str(t.deadline) if t.deadline else None
        }
        for t in tasks
    ]

    return {
        "name": user.name,
        "email": user.email,
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "performance": performance,
        "tasks": task_list
    }

# =========================
# COMPLETE TASK
# =========================
@router.put("/complete-task/{task_id}")
def complete_task(task_id: int, db: Session = Depends(get_db)):

    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "completed"
    db.commit()

    return {
        "message": "Task completed successfully",
        "task_id": task.id,
        "status": task.status
    }

# =========================
# SUBMIT FEEDBACK
# =========================
@router.post("/feedback/submit")
def submit_feedback(data: schemas.FeedbackSubmit, db: Session = Depends(get_db)):

    # Check if feedback is released
    control = db.query(models.FeedbackControl).first()

    if not control or not control.is_released:
        raise HTTPException(status_code=403, detail="Feedback not released yet")

    # Prevent multiple submissions
    existing = db.query(models.FeedbackAnswer).filter(
        models.FeedbackAnswer.mentee_id == data.mentee_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Feedback already submitted")

    # Save answers
    for ans in data.answers:
        new_ans = models.FeedbackAnswer(
            question_id=ans.question_id,
            answer=ans.answer,
            mentee_id=data.mentee_id
        )
        db.add(new_ans)

    db.commit()

    return {"message": "Feedback submitted successfully"}

# =========================
# FEEDBACK STATUS
# =========================
@router.get("/feedback/status")
def feedback_status(db: Session = Depends(get_db)):

    control = db.query(models.FeedbackControl).first()

    return {
        "released": control.is_released if control else False
    }

# =========================
# GET QUESTIONS
# =========================
@router.get("/feedback/questions")
def get_questions(db: Session = Depends(get_db)):

    questions = db.query(models.FeedbackQuestion).all()

    return [
        {
            "id": q.id,
            "question": q.question
        }
        for q in questions
    ]