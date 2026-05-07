from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

# =========================
# USER
# =========================
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    dep = Column(String)
    role = Column(String, default="mentee")

    tasks = relationship("Task", back_populates="mentee")
    sent_messages = relationship("Message", foreign_keys="[Message.sender_id]", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="[Message.receiver_id]", back_populates="receiver")


# =========================
# MENTOR-MENTEE
# =========================
class MentorMentee(Base):
    __tablename__ = "mentor_mentee"

    id = Column(Integer, primary_key=True, index=True)
    mentee_id = Column(Integer, ForeignKey("users.id"))
    mentor_id = Column(Integer, ForeignKey("users.id"))


# =========================
# MESSAGE
# =========================
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    receiver_id = Column(Integer, ForeignKey("users.id"))
    message = Column(String, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")


# =========================
# TASK
# =========================
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    status = Column(String, default="pending")
    deadline = Column(DateTime)
    mentee_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    mentee = relationship("User", back_populates="tasks")


# =========================
# FEEDBACK CONTROL
# =========================
class FeedbackControl(Base):
    __tablename__ = "feedback_control"

    id = Column(Integer, primary_key=True)
    is_released = Column(Boolean, default=False)


# =========================
# FEEDBACK QUESTION
# =========================
class FeedbackQuestion(Base):
    __tablename__ = "feedback_questions"

    id = Column(Integer, primary_key=True)
    question = Column(String, nullable=False)
    type = Column(String)

    answers = relationship("FeedbackAnswer", back_populates="question")


# =========================
# FEEDBACK ANSWER
# =========================
class FeedbackAnswer(Base):
    __tablename__ = "feedback_answers"

    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("feedback_questions.id"))
    answer = Column(String, nullable=False)
    mentee_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    question = relationship("FeedbackQuestion", back_populates="answers")


# =========================
# MEETING (Google Meet)
# =========================
class Meeting(Base):
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    meet_link = Column(String, nullable=False)
    scheduled_at = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=60)
    mentor_id = Column(Integer, ForeignKey("users.id"))
    mentee_id = Column(Integer, ForeignKey("users.id"))
    notes = Column(String, default="")
    status = Column(String, default="scheduled")  # scheduled | cancelled | completed
    created_at = Column(DateTime, default=datetime.utcnow)
