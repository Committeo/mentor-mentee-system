from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models

router = APIRouter(prefix="/mentor", tags=["Mentor"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# GET MENTOR DASHBOARD
# =========================
@router.get("/dashboard/{mentor_id}")
def get_dashboard(mentor_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == mentor_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Mentor not found")

    pairs = db.query(models.MentorMentee).filter(models.MentorMentee.mentor_id == mentor_id).all()
    mentee_ids = [p.mentee_id for p in pairs]
    mentees = db.query(models.User).filter(models.User.id.in_(mentee_ids)).all()

    mentee_data = []
    for m in mentees:
        tasks = db.query(models.Task).filter(models.Task.mentee_id == m.id).all()
        completed = sum(1 for t in tasks if t.status == "completed")
        mentee_data.append({
            "id": m.id,
            "name": m.name,
            "email": m.email,
            "dep": m.dep,
            "total_tasks": len(tasks),
            "completed_tasks": completed,
            "performance": int((completed / len(tasks)) * 100) if tasks else 0
        })

    return {
        "name": user.name,
        "email": user.email,
        "dep": user.dep,
        "total_mentees": len(mentees),
        "mentees": mentee_data
    }

# =========================
# GET MENTEES OF MENTOR
# =========================
@router.get("/mentees/{mentor_id}")
def get_mentees(mentor_id: int, db: Session = Depends(get_db)):
    pairs = db.query(models.MentorMentee).filter(models.MentorMentee.mentor_id == mentor_id).all()
    mentee_ids = [p.mentee_id for p in pairs]
    mentees = db.query(models.User).filter(models.User.id.in_(mentee_ids)).all()
    return [{"id": m.id, "name": m.name, "email": m.email, "dep": m.dep} for m in mentees]

# =========================
# ADD TASK FOR MENTEE
# =========================
@router.post("/task/add")
def add_task(data: dict, db: Session = Depends(get_db)):
    from datetime import datetime
    deadline = None
    if data.get("deadline"):
        try:
            deadline = datetime.fromisoformat(data["deadline"])
        except:
            pass

    task = models.Task(
        title=data["title"],
        mentee_id=data["mentee_id"],
        deadline=deadline
    )
    db.add(task)
    db.commit()
    return {"message": "Task added successfully"}

# =========================
# GET TASKS FOR MENTEES
# =========================
@router.get("/tasks/{mentor_id}")
def get_tasks(mentor_id: int, db: Session = Depends(get_db)):
    pairs = db.query(models.MentorMentee).filter(models.MentorMentee.mentor_id == mentor_id).all()
    mentee_ids = [p.mentee_id for p in pairs]
    tasks = db.query(models.Task).filter(models.Task.mentee_id.in_(mentee_ids)).all()
    return [
        {
            "id": t.id,
            "title": t.title,
            "status": t.status,
            "mentee_id": t.mentee_id,
            "deadline": str(t.deadline) if t.deadline else None
        }
        for t in tasks
    ]
