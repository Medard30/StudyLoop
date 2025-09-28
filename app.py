from flask import Flask, render_template, request, redirect, url_for, flash, g
import sqlite3, os
from datetime import datetime
from urllib.parse import urlparse, parse_qs  # <-- for YouTube parsing

DB_PATH = os.path.join(os.path.dirname(__file__), "studyloop.db")

# --- DB helpers (per-request connection on g) ---
def get_db():
    if "db" not in g:
        con = sqlite3.connect(DB_PATH)
        con.row_factory = sqlite3.Row
        g.db = con
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# --- App & one-time init ---
app = Flask(__name__)
app.secret_key = "dev-key"
app.teardown_appcontext(close_db)

_initialized = False
@app.before_request
def ensure_initialized():
    """Initialize schema/seed once (Flask 3.x safe)."""
    global _initialized
    if not _initialized:
        init_db()
        _initialized = True

def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS ProblemPost (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, course TEXT, tags TEXT, prompt TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, author_id INTEGER,
        FOREIGN KEY(author_id) REFERENCES User(id)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS VideoReply (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        post_id INTEGER, video_url TEXT, transcript TEXT,
        upvotes INTEGER DEFAULT 0, flags INTEGER DEFAULT 0,
        clear INTEGER DEFAULT 0, correct INTEGER DEFAULT 0, concise INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, author_id INTEGER,
        FOREIGN KEY(post_id) REFERENCES ProblemPost(id),
        FOREIGN KEY(author_id) REFERENCES User(id)
    )""")
    db.commit()
    # Seed minimal data
    cur.execute("SELECT COUNT(*) AS c FROM User"); uc = cur.fetchone()["c"]
    if uc == 0:
        cur.execute("INSERT INTO User(name) VALUES (?)", ("DemoUser",))
        db.commit()
    cur.execute("SELECT COUNT(*) AS c FROM ProblemPost"); pc = cur.fetchone()["c"]
    if pc == 0:
        cur.execute("""INSERT INTO ProblemPost(title,course,tags,prompt,author_id)
                       VALUES (?,?,?,?,1)""",
                    ("Limit sin(x)/x as x→0", "Calc I", "limits,trig",
                     "Why does L'Hôpital give 1 here?"))
        cur.execute("""INSERT INTO ProblemPost(title,course,tags,prompt,author_id)
                       VALUES (?,?,?,?,1)""",
                    ("For loop skipping last item", "CS1", "python,loops",
                     "Why is last item skipped?"))
        db.commit()
        cur.execute("""INSERT INTO VideoReply(post_id,video_url,transcript,upvotes,author_id,clear,correct,concise)
                       VALUES (1, ?, ?, 5, 1, 3,3,3)""",
                    ("https://youtu.be/dQw4w9WgXcQ", "Use series or L'Hôpital: sin x ~ x.",))
        cur.execute("""INSERT INTO VideoReply(post_id,video_url,transcript,upvotes,author_id,clear,correct,concise)
                       VALUES (2, ?, ?, 3, 1, 2,2,2)""",
                    ("https://example.com/clip.mp4", "Range issue: use enumerate or check indices.",))
        db.commit()

def time_to_first_reply(db, post_id):
    cur = db.cursor()
    cur.execute("SELECT MIN(datetime(created_at)) AS first FROM VideoReply WHERE post_id=?", (post_id,))
    row = cur.fetchone()
    if row and row["first"]:
        cur.execute("SELECT datetime(created_at) AS created FROM ProblemPost WHERE id=?", (post_id,))
        p = cur.fetchone()
        if p and p["created"]:
            cur.execute("SELECT CAST((julianday(?) - julianday(?)) * 24 * 60 AS INTEGER)",
                        (row["first"], p["created"]))
            return cur.fetchone()[0]
    return None

# --- Video classifier (YouTube / HTML5 / link) ---
def classify_video(url: str):
    """
    Returns {"player": "youtube"|"html5"|"link", "embed": <url or embed-url>}
    """
    u = (url or "").strip()
    if not u:
        return {"player": "link", "embed": ""}

    lower = u.lower()
    # YouTube
    if "youtube.com" in lower or "youtu.be" in lower:
        try:
            yt_id = None
            if "youtu.be/" in lower:
                yt_id = u.split("youtu.be/")[-1].split("?")[0]
            else:
                q = parse_qs(urlparse(u).query)
                yt_id = (q.get("v") or [None])[0]
            if yt_id:
                return {"player": "youtube", "embed": f"https://www.youtube.com/embed/{yt_id}"}
        except Exception:
            pass
        return {"player": "link", "embed": u}

    # HTML5 sources
    if lower.endswith((".mp4", ".webm", ".ogg", ".ogv")):
        return {"player": "html5", "embed": u}

    return {"player": "link", "embed": u}

# --- Routes ---
@app.route("/")
def index():
    db = get_db(); cur = db.cursor()
    cur.execute("""
      SELECT p.id, p.title, p.course, p.tags, p.created_at,
             (SELECT COUNT(*) FROM VideoReply r WHERE r.post_id=p.id) AS reply_count
      FROM ProblemPost p
      ORDER BY datetime(p.created_at) DESC
    """)
    posts = cur.fetchall()
    data = []
    for p in posts:
        cur.execute("SELECT SUM(clear+correct+concise) AS s, COUNT(*) AS n FROM VideoReply WHERE post_id=?", (p["id"],))
        row = cur.fetchone()
        q_avg = round(row["s"]/row["n"], 1) if row["n"] and row["s"] is not None else None
        data.append({"row": p, "q_avg": q_avg})
    return render_template("index.html", posts=data)

@app.route("/new", methods=["GET","POST"])
def new_post():
    if request.method == "POST":
        title = request.form.get("title","").strip()
        course = request.form.get("course","").strip()
        tags = request.form.get("tags","").strip()
        prompt = request.form.get("prompt","").strip()
        honor = request.form.get("honor")

        form_data = {"title": title, "course": course, "tags": tags, "prompt": prompt}
        honor_checked = bool(honor)

        if not (title and course and tags and prompt and honor):
            flash("Please fill all fields and accept the Honor Code.")
            return render_template("new_post.html", form_data=form_data, honor_checked=honor_checked)

        db = get_db()
        db.execute("""INSERT INTO ProblemPost(title,course,tags,prompt,author_id)
                      VALUES (?,?,?,?,1)""", (title,course,tags,prompt))
        db.commit()
        flash("Post created.")
        return redirect(url_for("index"))

    return render_template("new_post.html", form_data={}, honor_checked=False)

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    db = get_db(); cur = db.cursor()
    cur.execute("SELECT * FROM ProblemPost WHERE id=?", (post_id,))
    post = cur.fetchone()
    if not post:
        return ("Not found", 404)

    cur.execute("""
        SELECT *, (clear+correct+concise) AS qscore
        FROM VideoReply
        WHERE post_id=?
        ORDER BY datetime(created_at) DESC
    """, (post_id,))
    rows = cur.fetchall()

    # Attach player info (youtube/html5/link)
    replies = []
    for r in rows:
        d = dict(r)  # Jinja supports dot access on dict keys
        d.update(classify_video(d.get("video_url", "")))
        replies.append(d)

    ttr = time_to_first_reply(db, post_id)
    return render_template("post_detail.html", post=post, replies=replies, ttr=ttr)

@app.route("/post/<int:post_id>/reply", methods=["POST"])
def add_reply(post_id):
    video_url = request.form.get("video_url","").strip()
    transcript = request.form.get("transcript","").strip()
    if not (video_url and transcript):
        flash("Video URL and Transcript are required.")
        return redirect(url_for("post_detail", post_id=post_id))
    db = get_db()
    db.execute("""INSERT INTO VideoReply(post_id,video_url,transcript,author_id)
                  VALUES (?,?,?,1)""", (post_id, video_url, transcript))
    db.commit()
    flash("Reply added.")
    return redirect(url_for("post_detail", post_id=post_id))

@app.route("/reply/<int:reply_id>/rate", methods=["POST"])
def rate_reply(reply_id):
    dim = request.form.get("dim")
    if dim not in ("clear","correct","concise"):
        return redirect(url_for("index"))
    db = get_db()
    db.execute(f"UPDATE VideoReply SET {dim}={dim}+1, upvotes=upvotes+1 WHERE id=?", (reply_id,))
    db.commit()
    flash(f"Rated {dim}.")
    return redirect(request.referrer or url_for("index"))

@app.route("/reply/<int:reply_id>/report", methods=["POST"])
def report_reply(reply_id):
    db = get_db()
    db.execute("UPDATE VideoReply SET flags=flags+1 WHERE id=?", (reply_id,))
    db.commit()
    flash("Reply reported.")
    return redirect(request.referrer or url_for("index"))

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
