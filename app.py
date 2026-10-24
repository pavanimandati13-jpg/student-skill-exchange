"""Student Skill Exchange - students offer skills they have and request skills they want.

Matches are found automatically: A matches B when A offers something B wants
and B offers something A wants. Matched students can send exchange requests.
"""
import os
import sqlite3

from flask import Flask, g, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get("DB_PATH", os.path.join(BASE_DIR, "skillexchange.db"))
LEVELS = ["Beginner", "Intermediate", "Advanced"]
STATUSES = ["pending", "accepted", "declined", "completed"]

app = Flask(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    department TEXT DEFAULT '',
    year INTEGER DEFAULT 1,
    bio TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL REFERENCES users(id),
    skill TEXT NOT NULL COLLATE NOCASE,
    kind TEXT NOT NULL CHECK (kind IN ('offer','want')),
    level TEXT DEFAULT 'Beginner',
    UNIQUE (user_id, skill, kind)
);
CREATE TABLE IF NOT EXISTS requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_user INTEGER NOT NULL REFERENCES users(id),
    to_user INTEGER NOT NULL REFERENCES users(id),
    offered_skill TEXT NOT NULL,
    wanted_skill TEXT NOT NULL,
    message TEXT DEFAULT '',
    status TEXT NOT NULL DEFAULT 'pending',
    created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript(SCHEMA)
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [("Ravi Kumar", "ravi@college.edu", "CSE", 3, "Loves backend and cloud."),
                 ("Anitha Reddy", "anitha@college.edu", "ECE", 2, "Guitar player and designer."),
                 ("Karthik N", "karthik@college.edu", "CSE", 3, "Competitive programmer."),
                 ("Divya S", "divya@college.edu", "MBA", 1, "Public speaking coach."),
                 ("Sai Teja", "sai@college.edu", "EEE", 4, "Arduino and robotics tinkerer.")]
        db.executemany("INSERT INTO users(name,email,department,year,bio) VALUES (?,?,?,?,?)", users)
        skills = [(1, "Python", "offer", "Advanced"), (1, "Guitar", "want", "Beginner"),
                  (1, "Public Speaking", "want", "Beginner"),
                  (2, "Guitar", "offer", "Intermediate"), (2, "Python", "want", "Beginner"),
                  (2, "UI Design", "offer", "Advanced"),
                  (3, "Data Structures", "offer", "Advanced"), (3, "UI Design", "want", "Beginner"),
                  (4, "Public Speaking", "offer", "Advanced"), (4, "Python", "want", "Beginner"),
                  (5, "Arduino", "offer", "Advanced"), (5, "Data Structures", "want", "Intermediate"),
                  (5, "Public Speaking", "want", "Beginner")]
        db.executemany("INSERT INTO skills(user_id,skill,kind,level) VALUES (?,?,?,?)", skills)
    db.commit()
    db.close()


def err(msg, code=400):
    return jsonify(error=msg), code


# ---------- pages & health ----------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify(status="ok")


# ---------- users ----------
@app.route("/api/users", methods=["GET", "POST"])
def users():
    db = get_db()
    if request.method == "GET":
        rows = db.execute("SELECT * FROM users ORDER BY name").fetchall()
        return jsonify([dict(r) for r in rows])
    d = request.get_json(silent=True) or {}
    name, email = (d.get("name") or "").strip(), (d.get("email") or "").strip().lower()
    if not name or "@" not in email:
        return err("Valid name and email are required")
    existing = db.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if existing:  # simple sign-in: same email returns the same profile
        return jsonify(dict(existing)), 200
    try:
        year = int(d.get("year") or 1)
    except ValueError:
        return err("Year must be a number")
    cur = db.execute("INSERT INTO users(name,email,department,year,bio) VALUES (?,?,?,?,?)",
                     (name, email, d.get("department", ""), year, d.get("bio", "")))
    db.commit()
    return jsonify(dict(db.execute("SELECT * FROM users WHERE id=?", (cur.lastrowid,)).fetchone())), 201


@app.route("/api/users/<int:uid>")
def user_detail(uid):
    db = get_db()
    u = db.execute("SELECT * FROM users WHERE id=?", (uid,)).fetchone()
    if not u:
        return err("User not found", 404)
    sk = db.execute("SELECT id, skill, kind, level FROM skills WHERE user_id=? ORDER BY kind, skill", (uid,)).fetchall()
    return jsonify(**dict(u), skills=[dict(s) for s in sk])


# ---------- skills ----------
@app.route("/api/skills", methods=["POST"])
def add_skill():
    d = request.get_json(silent=True) or {}
    skill, kind = (d.get("skill") or "").strip(), d.get("kind")
    level = d.get("level", "Beginner")
    if not d.get("user_id") or not skill or kind not in ("offer", "want") or level not in LEVELS:
        return err("user_id, skill, kind (offer|want) and valid level are required")
    db = get_db()
    if not db.execute("SELECT 1 FROM users WHERE id=?", (d["user_id"],)).fetchone():
        return err("User not found", 404)
    try:
        cur = db.execute("INSERT INTO skills(user_id,skill,kind,level) VALUES (?,?,?,?)",
                         (d["user_id"], skill.title() if skill.islower() else skill, kind, level))
    except sqlite3.IntegrityError:
        return err("You already listed this skill", 409)
    db.commit()
    return jsonify(id=cur.lastrowid), 201


@app.route("/api/skills/<int:sid>", methods=["DELETE"])
def delete_skill(sid):
    db = get_db()
    cur = db.execute("DELETE FROM skills WHERE id=?", (sid,))
    db.commit()
    return (jsonify(message="Removed"), 200) if cur.rowcount else err("Not found", 404)


@app.route("/api/search")
def search():
    """Find students offering a skill (substring, case-insensitive)."""
    q = (request.args.get("skill") or "").strip()
    rows = get_db().execute(
        """SELECT u.id AS user_id, u.name, u.department, u.year, s.skill, s.level
           FROM skills s JOIN users u ON u.id = s.user_id
           WHERE s.kind='offer' AND s.skill LIKE ? ORDER BY s.skill, u.name""", (f"%{q}%",)).fetchall()
    return jsonify([dict(r) for r in rows])


# ---------- matching ----------
@app.route("/api/matches/<int:uid>")
def matches(uid):
    """Two-way matches: they offer what I want AND I offer what they want."""
    db = get_db()
    if not db.execute("SELECT 1 FROM users WHERE id=?", (uid,)).fetchone():
        return err("User not found", 404)
    rows = db.execute(
        """SELECT u.id AS user_id, u.name, u.department, u.year,
                  theirs.skill AS they_teach, mine.skill AS you_teach
           FROM skills mywant
           JOIN skills theirs ON theirs.skill = mywant.skill AND theirs.kind='offer' AND theirs.user_id != mywant.user_id
           JOIN skills theirwant ON theirwant.user_id = theirs.user_id AND theirwant.kind='want'
           JOIN skills mine ON mine.skill = theirwant.skill AND mine.kind='offer' AND mine.user_id = mywant.user_id
           JOIN users u ON u.id = theirs.user_id
           WHERE mywant.user_id=? AND mywant.kind='want'
           ORDER BY u.name""", (uid,)).fetchall()
    one_way = db.execute(
        """SELECT DISTINCT u.id AS user_id, u.name, theirs.skill AS they_teach
           FROM skills mywant
           JOIN skills theirs ON theirs.skill = mywant.skill AND theirs.kind='offer' AND theirs.user_id != mywant.user_id
           JOIN users u ON u.id = theirs.user_id
           WHERE mywant.user_id=? AND mywant.kind='want' ORDER BY u.name""", (uid,)).fetchall()
    return jsonify(perfect=[dict(r) for r in rows], can_teach_me=[dict(r) for r in one_way])


# ---------- exchange requests ----------
@app.route("/api/requests", methods=["GET", "POST"])
def exchange_requests():
    db = get_db()
    if request.method == "GET":
        uid = request.args.get("user_id", type=int)
        if not uid:
            return err("user_id is required")
        rows = db.execute(
            """SELECT r.*, f.name AS from_name, t.name AS to_name FROM requests r
               JOIN users f ON f.id=r.from_user JOIN users t ON t.id=r.to_user
               WHERE r.from_user=? OR r.to_user=? ORDER BY r.id DESC""", (uid, uid)).fetchall()
        return jsonify([dict(r) for r in rows])
    d = request.get_json(silent=True) or {}
    need = ("from_user", "to_user", "offered_skill", "wanted_skill")
    if not all(d.get(k) for k in need):
        return err("from_user, to_user, offered_skill, wanted_skill are required")
    if d["from_user"] == d["to_user"]:
        return err("You cannot send a request to yourself")
    cur = db.execute("INSERT INTO requests(from_user,to_user,offered_skill,wanted_skill,message) VALUES (?,?,?,?,?)",
                     (d["from_user"], d["to_user"], d["offered_skill"], d["wanted_skill"], d.get("message", "")))
    db.commit()
    return jsonify(id=cur.lastrowid), 201


@app.route("/api/requests/<int:rid>", methods=["PATCH"])
def update_request(rid):
    status = (request.get_json(silent=True) or {}).get("status")
    if status not in STATUSES:
        return err(f"status must be one of {STATUSES}")
    db = get_db()
    cur = db.execute("UPDATE requests SET status=? WHERE id=?", (status, rid))
    db.commit()
    return (jsonify(message="Updated"), 200) if cur.rowcount else err("Not found", 404)


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
