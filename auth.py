from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
import models, schemas
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

router = APIRouter()

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
SYSTEM_EMAIL = os.getenv("SYSTEM_EMAIL", SMTP_USER)

ALLOWED_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com",
    "hotmail.com", "icloud.com",
]

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def is_valid_domain(email: str) -> bool:
    try:
        domain = email.strip().lower().split("@")[1]
        return domain in ALLOWED_DOMAINS
    except Exception:
        return False

def send_email(to_email: str, subject: str, body: str) -> bool:
    if not SMTP_USER or not SMTP_PASS:
        print(f"[DEV] Email to {to_email} | {subject} | {body}")
        return True
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SYSTEM_EMAIL
        msg["To"] = to_email
        msg.attach(MIMEText(body, "plain"))
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo(); server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SYSTEM_EMAIL, to_email, msg.as_string())
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False

otp_store: dict = {}
login_otp_store: dict = {}

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if not is_valid_domain(user.email):
        domain = user.email.split("@")[-1] if "@" in user.email else user.email
        return {"success": False, "message": f"Email domain '@{domain}' is not allowed. Please use Gmail, Yahoo, Outlook, Hotmail, or iCloud."}
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        return {"success": False, "message": "User already exists"}
    valid_roles = ["mentor", "mentee", "admin"]
    if user.role.lower() not in valid_roles:
        return {"success": False, "message": "Invalid role"}
    new_user = models.User(name=user.name, email=user.email, password=user.password, dep=user.dep, role=user.role.lower())
    db.add(new_user)
    db.commit()
    return {"success": True, "message": "Registered successfully"}

@router.post("/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        return {"success": False, "message": "User not found"}
    if user.password != data.password:
        return {"success": False, "message": "Invalid password", "can_use_otp": True}
    return {"success": True, "message": "Login successful",
            "user": {"id": user.id, "name": user.name, "email": user.email, "dep": user.dep, "role": user.role.lower()}}

@router.post("/send-login-otp")
def send_login_otp(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "").strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return {"success": False, "message": "No account found with this email"}
    otp = str(random.randint(100000, 999999))
    login_otp_store[email] = otp
    sent = send_email(email, "Your Login OTP - Mentor Mentee System",
        f"Hello {user.name},\n\nYour one-time login OTP is: {otp}\n\nValid for 10 minutes. Do not share it.")
    if sent:
        return {"success": True, "message": "OTP sent to your registered email"}
    return {"success": False, "message": "Failed to send OTP"}

@router.post("/verify-login-otp")
def verify_login_otp(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "").strip().lower()
    otp = data.get("otp", "").strip()
    if login_otp_store.get(email) != otp:
        return {"success": False, "message": "Invalid or expired OTP"}
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return {"success": False, "message": "User not found"}
    login_otp_store.pop(email, None)
    return {"success": True, "message": "Login successful",
            "user": {"id": user.id, "name": user.name, "email": user.email, "dep": user.dep, "role": user.role.lower()}}

@router.post("/send-otp")
def send_otp(data: dict, db: Session = Depends(get_db)):
    email = data.get("email", "").strip().lower()
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return {"success": False, "message": "No account with this email"}
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    send_email(email, "Password Reset OTP", f"Your password reset OTP is: {otp}")
    return {"success": True, "message": "OTP sent to your email"}

@router.post("/reset-password")
def reset_password(data: schemas.ResetPassword, db: Session = Depends(get_db)):
    if otp_store.get(data.email) != data.otp:
        return {"success": False, "message": "Invalid OTP"}
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user:
        return {"success": False, "message": "User not found"}
    user.password = data.new_password
    db.commit()
    otp_store.pop(data.email, None)
    return {"success": True, "message": "Password updated"}

@router.get("/profile/{user_id}")
def get_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found"}
    if user.role == "mentee":
        pairs = db.query(models.MentorMentee).filter(models.MentorMentee.mentee_id == user_id).all()
        mentors = db.query(models.User).filter(models.User.id.in_([p.mentor_id for p in pairs])).all()
        extra = {"assigned_mentors": [{"id": m.id, "name": m.name} for m in mentors]}
    elif user.role == "mentor":
        pairs = db.query(models.MentorMentee).filter(models.MentorMentee.mentor_id == user_id).all()
        mentees = db.query(models.User).filter(models.User.id.in_([p.mentee_id for p in pairs])).all()
        extra = {"assigned_mentees": [{"id": m.id, "name": m.name} for m in mentees]}
    else:
        extra = {}
    total_users = db.query(models.User).count()
    extra["total_users"] = total_users
    return {"success": True, "user": {"id": user.id, "name": user.name, "email": user.email, "dep": user.dep, "role": user.role, **extra}}

@router.put("/profile/{user_id}")
def update_profile(user_id: int, data: dict, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found"}
    if data.get("name", "").strip():
        user.name = data["name"].strip()
    if data.get("dep", "").strip():
        user.dep = data["dep"].strip()
    if data.get("password", "").strip():
        user.password = data["password"].strip()
    db.commit()
    return {"success": True, "message": "Profile updated",
            "user": {"id": user.id, "name": user.name, "email": user.email, "dep": user.dep, "role": user.role}}

@router.delete("/profile/{user_id}")
def delete_profile(user_id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return {"success": False, "message": "User not found"}
    db.query(models.MentorMentee).filter(
        (models.MentorMentee.mentor_id == user_id) | (models.MentorMentee.mentee_id == user_id)).delete()
    db.query(models.Task).filter(models.Task.mentee_id == user_id).delete()
    db.query(models.FeedbackAnswer).filter(models.FeedbackAnswer.mentee_id == user_id).delete()
    db.query(models.Message).filter(
        (models.Message.sender_id == user_id) | (models.Message.receiver_id == user_id)).delete()
    db.delete(user)
    db.commit()
    return {"success": True, "message": "Account deleted"}
