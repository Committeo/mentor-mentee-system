from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# GET ALL USERS
# =========================
@router.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "dep": u.dep, "role": u.role} for u in users]

# =========================
# DELETE USER
# =========================
@router.delete("/user/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

# =========================
# ASSIGN MENTOR TO MENTEE
# =========================
@router.post("/assign")
def assign_mentor(data: schemas.RequestCreate, db: Session = Depends(get_db)):
    existing = db.query(models.MentorMentee).filter(
        models.MentorMentee.mentee_id == data.mentee_id,
        models.MentorMentee.mentor_id == data.mentor_id
    ).first()
    if existing:
        return {"message": "Already assigned"}

    pair = models.MentorMentee(mentee_id=data.mentee_id, mentor_id=data.mentor_id)
    db.add(pair)
    db.commit()
    return {"message": "Mentor assigned successfully"}

# =========================
# GET ASSIGNMENTS
# =========================
@router.get("/assignments")
def get_assignments(db: Session = Depends(get_db)):
    pairs = db.query(models.MentorMentee).all()
    result = []
    for p in pairs:
        mentor = db.query(models.User).filter(models.User.id == p.mentor_id).first()
        mentee = db.query(models.User).filter(models.User.id == p.mentee_id).first()
        if mentor and mentee:
            result.append({
                "id": p.id,
                "mentor": {"id": mentor.id, "name": mentor.name},
                "mentee": {"id": mentee.id, "name": mentee.name}
            })
    return result

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
    return {"message": "Task added"}

# =========================
# GET ALL TASKS
# =========================
@router.get("/tasks")
def get_all_tasks(db: Session = Depends(get_db)):
    tasks = db.query(models.Task).all()
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

# =========================
# FEEDBACK RELEASE
# =========================
@router.post("/feedback/release")
def release_feedback(db: Session = Depends(get_db)):
    control = db.query(models.FeedbackControl).first()
    if not control:
        control = models.FeedbackControl(is_released=True)
        db.add(control)
    else:
        control.is_released = True
    db.commit()
    return {"message": "Feedback Released"}

# =========================
# ADD QUESTION
# =========================
@router.post("/feedback/add-question")
def add_question(data: dict, db: Session = Depends(get_db)):
    q = models.FeedbackQuestion(
        question=data["question"],
        type=data["type"]
    )
    db.add(q)
    db.commit()
    return {"message": "Question Added"}

# =========================
# GET QUESTIONS
# =========================
@router.get("/feedback/questions")
def get_questions(db: Session = Depends(get_db)):
    return db.query(models.FeedbackQuestion).all()

# =========================
# GET FEEDBACK ANSWERS
# =========================
@router.get("/feedback/answers")
def get_answers(db: Session = Depends(get_db)):
    answers = db.query(models.FeedbackAnswer).all()
    result = []
    for a in answers:
        mentee = db.query(models.User).filter(models.User.id == a.mentee_id).first()
        question = db.query(models.FeedbackQuestion).filter(models.FeedbackQuestion.id == a.question_id).first()
        result.append({
            "mentee": "Anonymous",   # feedback is anonymous — name is intentionally hidden
            "question": question.question if question else "Unknown",
            "answer": a.answer
        })
    return result

# =========================
# DASHBOARD STATS
# =========================
@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    total_mentors = db.query(models.User).filter(models.User.role == "mentor").count()
    total_mentees = db.query(models.User).filter(models.User.role == "mentee").count()
    total_assignments = db.query(models.MentorMentee).count()
    total_tasks = db.query(models.Task).count()
    pending_tasks = db.query(models.Task).filter(models.Task.status == "pending").count()
    total_feedbacks = db.query(models.FeedbackAnswer).count()

    return {
        "total_mentors": total_mentors,
        "total_mentees": total_mentees,
        "total_assignments": total_assignments,
        "total_tasks": total_tasks,
        "pending_tasks": pending_tasks,
        "total_feedbacks": total_feedbacks
    }
