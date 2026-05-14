# Feedback Management System (FMS)

A centralized web-based system to collect, manage, search, and analyze feedback from participants, employees, or customers.

## Tech Stack

| Layer    | Technology           |
|----------|----------------------|
| Frontend | React 18 (CDN/SPA)   |
| Backend  | Python FastAPI       |
| Database | SQLite               |
| API Test | Postman / Swagger UI |

---

## Features

- Submit feedback with participant name, program, rating (1–5), and comments
- View all feedback in a searchable, filterable table
- Dashboard showing total count, average rating, and recent submissions
- Full CRUD: Create, Read, Update, Delete feedback
- Search by keyword, rating, or program/event name
- Responsive UI — works on desktop and mobile

---

## Project Structure

```
FMS_Project/
├── backend/
│   ├── main.py          # FastAPI app entry point
│   ├── database.py      # SQLAlchemy engine & session
│   ├── models.py        # ORM models
│   ├── schemas.py       # Pydantic request/response schemas
│   ├── crud.py          # Database operations
│   ├── routers/
│   │   └── feedback.py  # Feedback API routes
│   └── requirements.txt
├── frontend/
│   ├── index.html       # Single-page app entry
│   ├── style.css        # All styles
│   └── src/
│       └── App.js       # React components (runs via Babel CDN)
├── database/
│   └── schema.sql       # SQL schema + seed data
├── docs/
├── screenshots/
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Setup & Installation

### 1. Backend Setup

**Prerequisites:** Python 3.9+

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API will be available at: `http://127.0.0.1:8000`
Interactive docs: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup

No build step required. Open `frontend/index.html` directly in a browser (Chrome, Edge, Firefox).

> **Note:** For CORS to work, open the file through a local server or just double-click `index.html`. The frontend connects to `http://127.0.0.1:8000`.

Optional — serve with Python's built-in server:
```bash
cd frontend
python -m http.server 3000
# Then open http://localhost:3000
```

---

## API Endpoints

| Method | Endpoint            | Description              |
|--------|---------------------|--------------------------|
| GET    | /feedback           | List all feedback        |
| GET    | /feedback/{id}      | Get feedback by ID       |
| POST   | /feedback           | Submit new feedback      |
| PUT    | /feedback/{id}      | Update existing feedback |
| DELETE | /feedback/{id}      | Delete feedback          |
| GET    | /feedback/stats     | Dashboard stats          |
| GET    | /search             | Search & filter          |

### Example: Submit Feedback

**POST** `/feedback`
```json
{
  "participant_name": "Alice Johnson",
  "program_name": "React Workshop 2025",
  "rating": 5,
  "comments": "Excellent hands-on sessions!"
}
```

**Response 201:**
```json
{
  "feedback_id": 1,
  "participant_name": "Alice Johnson",
  "program_name": "React Workshop 2025",
  "rating": 5,
  "comments": "Excellent hands-on sessions!",
  "submitted_at": "2026-05-14T10:30:00"
}
```

### Search Examples

```
GET /search?keyword=react
GET /search?rating=5
GET /search?program_name=workshop
GET /search?keyword=training&rating=4
```

---

## Rating Scale

| Rating | Label     |
|--------|-----------|
| 1      | Poor      |
| 2      | Fair      |
| 3      | Good      |
| 4      | Very Good |
| 5      | Excellent |

---

## Database

SQLite database file `feedback.db` is auto-created inside `backend/` on first run.

To seed sample data:
```bash
cd backend
python -c "
from database import SessionLocal, engine
import models
models.Base.metadata.create_all(bind=engine)
from crud import create_feedback
from schemas import FeedbackCreate
db = SessionLocal()
samples = [
  FeedbackCreate(participant_name='Alice', program_name='React Workshop', rating=5, comments='Great!'),
  FeedbackCreate(participant_name='Bob', program_name='Python Training', rating=4, comments='Very useful'),
]
for s in samples:
    create_feedback(db, s)
db.close()
print('Seeded!')
"
```

---

## GitHub Repository Naming

Follows the convention:
```
AFDE_May26_Aravind_FMS
```

---
