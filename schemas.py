from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    dep: str
    role: str

class LoginRequest(BaseModel):
    email: str
    password: str

class RequestCreate(BaseModel):
    mentee_id: int
    mentor_id: int

class MessageCreate(BaseModel):
    sender_id: int
    receiver_id: int
    message: str

class FeedbackCreate(BaseModel):
    mentee_id: int
    message: str

class ResetPassword(BaseModel):
    email: str
    otp: str
    new_password: str

class QuestionCreate(BaseModel):
    question: str
    type: str

class AnswerItem(BaseModel):
    question_id: int
    answer: str

class FeedbackSubmit(BaseModel):
    mentee_id: int
    answers: list[AnswerItem]
