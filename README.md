# Mentor-Mentee System

Mentor-Mentee Management System built using FastAPI.

## Setup & Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open:

http://127.0.0.1:8000

## Features

### Admin
- Dashboard with stats
- View mentors & mentees
- Assign mentor ↔ mentee pairs
- Add tasks for mentees
- Feedback control (add questions, release)
- Messenger (can message anyone)

### Mentor
- Dashboard with mentee performance overview
- View assigned mentees
- Assign tasks with deadlines
- Messenger (chat with your mentees)

### Mentee
- Dashboard with task progress & performance %
- View and complete tasks
- Submit feedback (when released)
- Messenger (chat with your mentor)

## Messenger API Endpoints

- `POST /messages/send` — Send a message
- `GET /messages/conversation/{user1_id}/{user2_id}` — Get chat history
- `GET /messages/contacts/{user_id}` — Get contacts list with unread count
- `GET /messages/unread/{user_id}` — Get total unread messages

## Roles

- **Admin** — Full access
- **Mentor** — Manage assigned mentees and tasks
- **Mentee** — View tasks, complete tasks, and submit feedback

## Technologies Used

- FastAPI
- SQLAlchemy
- SQLite
- Jinja2 Templates
- HTML, CSS, JavaScript
- Bootstrap 5

## Project Structure

```
mentor-mentee-system/
│── main.py
│── models.py
│── database.py
│── schemas.py
│── routes.py
│── requirements.txt
│── Frontend/
│── static/
│── README.md
```