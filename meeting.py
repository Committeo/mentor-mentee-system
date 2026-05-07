from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal
from datetime import datetime
import models

router = APIRouter(prefix="/meetings", tags=["Meetings"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# SCHEDULE A MEETING
# =========================
@router.post("/schedule")
def schedule_meeting(data: dict, db: Session = Depends(get_db)):
    mentor_id  = data.get("mentor_id")
    mentee_id  = data.get("mentee_id")
    title      = data.get("title", "Mentor-Mentee Session")
    meet_link  = data.get("meet_link", "").strip()
    scheduled  = data.get("scheduled_at")
    duration   = data.get("duration_minutes", 60)
    notes      = data.get("notes", "")

    if not mentor_id or not mentee_id or not meet_link or not scheduled:
        raise HTTPException(status_code=400, detail="mentor_id, mentee_id, meet_link, and scheduled_at are required")

    # Validate the Google Meet link
    if "meet.google.com" not in meet_link:
        raise HTTPException(status_code=400, detail="Please provide a valid Google Meet link (meet.google.com/...)")

    try:
        scheduled_dt = datetime.fromisoformat(scheduled)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid scheduled_at format. Use ISO format: 2025-05-20T14:00:00")

    meeting = models.Meeting(
        title=title,
        meet_link=meet_link,
        scheduled_at=scheduled_dt,
        duration_minutes=duration,
        mentor_id=mentor_id,
        mentee_id=mentee_id,
        notes=notes,
        status="scheduled"
    )
    db.add(meeting)
    db.commit()
    db.refresh(meeting)

    return {
        "success": True,
        "message": "Meeting scheduled successfully",
        "meeting_id": meeting.id
    }


# =========================
# GET MEETINGS FOR A USER (mentor or mentee)
# =========================
@router.get("/user/{user_id}")
def get_user_meetings(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role == "mentor":
        meetings = db.query(models.Meeting).filter(models.Meeting.mentor_id == user_id).all()
    else:
        meetings = db.query(models.Meeting).filter(models.Meeting.mentee_id == user_id).all()

    result = []
    for m in meetings:
        mentor = db.query(models.User).filter(models.User.id == m.mentor_id).first()
        mentee = db.query(models.User).filter(models.User.id == m.mentee_id).first()
        result.append({
            "id": m.id,
            "title": m.title,
            "meet_link": m.meet_link,
            "scheduled_at": str(m.scheduled_at),
            "duration_minutes": m.duration_minutes,
            "notes": m.notes,
            "status": m.status,
            "mentor_name": mentor.name if mentor else "Unknown",
            "mentee_name": mentee.name if mentee else "Unknown",
            "mentor_id": m.mentor_id,
            "mentee_id": m.mentee_id,
        })

    # Sort by scheduled time (upcoming first)
    result.sort(key=lambda x: x["scheduled_at"])
    return result


# =========================
# UPDATE MEETING STATUS
# =========================
@router.put("/status/{meeting_id}")
def update_meeting_status(meeting_id: int, data: dict, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    new_status = data.get("status")
    if new_status not in ["scheduled", "cancelled", "completed"]:
        raise HTTPException(status_code=400, detail="Status must be: scheduled, cancelled, or completed")

    meeting.status = new_status
    db.commit()
    return {"success": True, "message": f"Meeting marked as {new_status}"}


# =========================
# DELETE A MEETING
# =========================
@router.delete("/{meeting_id}")
def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(models.Meeting).filter(models.Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")

    db.delete(meeting)
    db.commit()
    return {"success": True, "message": "Meeting deleted"}


# =========================
# GET UPCOMING MEETINGS COUNT (for dashboard badge)
# =========================
@router.get("/upcoming/{user_id}")
def get_upcoming_count(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return {"upcoming": 0}

    now = datetime.utcnow()
    if user.role == "mentor":
        count = db.query(models.Meeting).filter(
            models.Meeting.mentor_id == user_id,
            models.Meeting.status == "scheduled",
            models.Meeting.scheduled_at >= now
        ).count()
    else:
        count = db.query(models.Meeting).filter(
            models.Meeting.mentee_id == user_id,
            models.Meeting.status == "scheduled",
            models.Meeting.scheduled_at >= now
        ).count()

    return {"upcoming": count}
