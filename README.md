# Student Skill Exchange

A Flask web app where students list skills they can teach and skills they want to learn.
It finds two-way "perfect swaps" (you teach what they want, they teach what you want) and
manages exchange requests (pending, accepted, declined, completed).

## Features
- Sign up / sign in with a college email (no password, demo level)
- Add or remove skills with levels (Beginner, Intermediate, Advanced)
- Search who can teach a skill (partial, case-insensitive)
- Automatic two-way matching, plus a list of one-way helpers
- Send, accept, decline and complete exchange requests
- REST API, responsive UI with light/dark mode, `/health` endpoint
- Seeded demo data: 5 students (try signing in as `ravi@college.edu`)

## Run locally
```
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py            # http://localhost:5000
python -m unittest discover tests
```

## API
| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/users` | Register or sign in by email |
| GET | `/api/users`, `/api/users/<id>` | List students / profile with skills |
| POST | `/api/skills` | Add skill `{user_id, skill, kind: offer\|want, level}` |
| DELETE | `/api/skills/<id>` | Remove skill |
| GET | `/api/search?skill=python` | Who offers a skill |
| GET | `/api/matches/<user_id>` | Perfect swaps and one-way helpers |
| GET/POST | `/api/requests` | List (`?user_id=`) / send request |
| PATCH | `/api/requests/<id>` | Set status |
| GET | `/health` | Health check |

## Docker / deploy
```
docker build -t skill-exchange .
docker run -d -p 80:8080 -v skill-data:/data skill-exchange
```
Works on any VM (e.g. AWS EC2), Elastic Beanstalk (`Procfile`), Google Cloud Run or Render.
SQLite is fine for a demo; use a managed database (RDS / Cloud SQL) for multiple instances.

## Possible extensions
Password or Google login, ratings and reviews after a completed swap, in-app chat, email notifications.
