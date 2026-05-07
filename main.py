from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import engine, Base, SessionLocal
import models

import auth
import mentee
import mentor
import admin
import messenger
import meeting

app = FastAPI(title="Mentor-Mentee System")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Templates & Static
templates = Jinja2Templates(directory="Frontend")
app.mount("/static", StaticFiles(directory="Frontend"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================
# PAGE ROUTES
# ==========================
@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register-page", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# ==========================
# USER APIs
# ==========================
@app.get("/api")
def home():
    return {"message": "Mentor-Mentee API Running"}

@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "dep": u.dep, "role": u.role} for u in users]

@app.get("/mentors")
def get_mentors(db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.role == "mentor").all()
    return [{"id": u.id, "name": u.name, "email": u.email, "dep": u.dep} for u in users]

@app.get("/mentees")
def get_mentees(db: Session = Depends(get_db)):
    users = db.query(models.User).filter(models.User.role == "mentee").all()
    return [{"id": u.id, "name": u.name, "email": u.email, "dep": u.dep} for u in users]

# ==========================
# ROUTERS
# ==========================
app.include_router(auth.router)
app.include_router(mentee.router)
app.include_router(mentor.router)
app.include_router(admin.router)
app.include_router(messenger.router)
app.include_router(meeting.router)

# ==========================
# CREATE TABLES
# ==========================
Base.metadata.create_all(bind=engine)
