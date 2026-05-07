from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from database import SessionLocal
import models, schemas
from datetime import datetime

router = APIRouter(prefix="/messages", tags=["Messenger"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# SEND MESSAGE
# =========================
@router.post("/send")
def send_message(data: schemas.MessageCreate, db: Session = Depends(get_db)):
    sender = db.query(models.User).filter(models.User.id == data.sender_id).first()
    receiver = db.query(models.User).filter(models.User.id == data.receiver_id).first()

    if not sender or not receiver:
        raise HTTPException(status_code=404, detail="User not found")

    msg = models.Message(
        sender_id=data.sender_id,
        receiver_id=data.receiver_id,
        message=data.message
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    return {
        "id": msg.id,
        "sender_id": msg.sender_id,
        "receiver_id": msg.receiver_id,
        "message": msg.message,
        "created_at": str(msg.created_at),
        "is_read": msg.is_read
    }

# =========================
# GET CONVERSATION
# =========================
@router.get("/conversation/{user1_id}/{user2_id}")
def get_conversation(user1_id: int, user2_id: int, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(
        or_(
            and_(models.Message.sender_id == user1_id, models.Message.receiver_id == user2_id),
            and_(models.Message.sender_id == user2_id, models.Message.receiver_id == user1_id)
        )
    ).order_by(models.Message.created_at).all()

    # Mark as read
    for msg in messages:
        if msg.receiver_id == user1_id and not msg.is_read:
            msg.is_read = True
    db.commit()

    return [
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "message": m.message,
            "created_at": str(m.created_at),
            "is_read": m.is_read
        }
        for m in messages
    ]

# =========================
# GET CONTACTS (who user can message)
# =========================
@router.get("/contacts/{user_id}")
def get_contacts(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    contacts = []

    if user.role == "mentee":
        # Get their mentor
        pairs = db.query(models.MentorMentee).filter(models.MentorMentee.mentee_id == user_id).all()
        mentor_ids = [p.mentor_id for p in pairs]
        contacts = db.query(models.User).filter(models.User.id.in_(mentor_ids)).all()

    elif user.role == "mentor":
        # Get their mentees
        pairs = db.query(models.MentorMentee).filter(models.MentorMentee.mentor_id == user_id).all()
        mentee_ids = [p.mentee_id for p in pairs]
        contacts = db.query(models.User).filter(models.User.id.in_(mentee_ids)).all()

    elif user.role == "admin":
        # Admin can message everyone
        contacts = db.query(models.User).filter(models.User.id != user_id).all()

    # Count unread messages per contact
    result = []
    for c in contacts:
        unread = db.query(models.Message).filter(
            models.Message.sender_id == c.id,
            models.Message.receiver_id == user_id,
            models.Message.is_read == False
        ).count()
        result.append({
            "id": c.id,
            "name": c.name,
            "role": c.role,
            "dep": c.dep,
            "unread": unread
        })

    return result

# =========================
# UNREAD COUNT
# =========================
@router.get("/unread/{user_id}")
def get_unread_count(user_id: int, db: Session = Depends(get_db)):
    count = db.query(models.Message).filter(
        models.Message.receiver_id == user_id,
        models.Message.is_read == False
    ).count()
    return {"unread": count}
