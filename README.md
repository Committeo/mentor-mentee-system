# Mentor-Mentee System

## Setup & Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open: http://127.0.0.1:8000

## Features

### Admin
- Dashboard with stats
- View mentors & mentees
- Assign mentor ↔ mentee pairs
- Add tasks for mentees
- Feedback control (add questions, release)
- **Messenger** (can message anyone)

### Mentor
- Dashboard with mentee performance overview
- View assigned mentees
- Assign tasks with deadlines
- **Messenger** (chat with your mentees)

### Mentee
- Dashboard with task progress & performance %
- View & complete tasks
- Submit feedback (when released)
- **Messenger** (chat with your mentor)

## Messenger API Endpoints
- POST `/messages/send` — send a message
- GET `/messages/conversation/{user1_id}/{user2_id}` — get chat history
- GET `/messages/contacts/{user_id}` — get contacts list with unread count
- GET `/messages/unread/{user_id}` — total unread messages

## Roles
- **admin** — full access
- **mentor** — manage mentees & tasks
- **mentee** — view tasks, submit feedback
