from flask import Flask, render_template, request, redirect, url_for, flash, g, send_from_directory, session
import sqlite3, os, uuid
from datetime import datetime
from werkzeug.utils import secure_filename

# --- File + DB Configuration ---
BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "studyloop.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"mp4", "webm", "ogg", "ogv", "m4v", "mov"}

# --- Flask Setup ---
app = Flask(__name__)
app.secret_key = "dev-key"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024  # 200 MB cap

# --- DB Helpers ---
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

app.teardown_appcontext(close_db)

# --- Tag normalizer ---
def normalize_tags(raw: str) -> str:
    seen, out = set(), []
    for chunk in (raw or "").split(","):
        t = chunk.strip().lstrip("#").lower()
        if t and t not in seen:
            seen.add(t)
            out.append(t)
    return ",".join(out)

# --- DB Initialization ---
_initialized = False
@app.before_request
def ensure_initialized():
    global _initialized
    if not _initialized:
        init_db()
        _initialized = True
    # Each visitor gets a unique session id
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())

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
        post_id INTEGER, video_path TEXT, transcript TEXT,
        upvotes INTEGER DEFAULT 0, flags INTEGER DEFAULT 0,
        clear INTEGER DEFAULT 0, correct INTEGER DEFAULT 0, concise INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP, author_id INTEGER,
        FOREIGN KEY(post_id) REFERENCES ProblemPost(id),
        FOREIGN KEY(author_id) REFERENCES User(id)
    )""")

    # Vote and report tracking
    cur.execute("""
    CREATE TABLE IF NOT EXISTS VoteRecord (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reply_id INTEGER,
        session_id TEXT,
        dimension TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(reply_id, session_id, dimension)
    )""")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS ReportRecord (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        reply_id INTEGER,
        session_id TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(reply_id, session_id)
    )""")

    db.commit()

    # Seed demo user
    cur.execute("SELECT COUNT(*) AS c FROM User")
    if cur.fetchone()["c"] == 0:
        cur.execute("INSERT INTO User(name) VALUES (?)", ("DemoUser",))
        db.commit()

    # Seed example posts
    cur.execute("SELECT COUNT(*) AS c FROM ProblemPost")
    if cur.fetchone()["c"] == 0:
        cur.executemany(
            "INSERT INTO ProblemPost(title, course, tags, prompt, author_id) VALUES (?,?,?,?,1)",
            [
                ("Projectile angle for max range",
                 "Physics I",
                 "kinematics,projectile,angles",
                 "For v0 on level ground, which launch angle gives max range, and why?"),
                ("Python for-loop skips last item",
                 "CS1",
                 "python,loops",
                 "My for-loop misses the last element; what should I check?"),
            ],
        )
        db.commit()

# --- Utility ---
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

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

# --- Routes ---
@app.route("/")
def index():
    q       = (request.args.get("q") or "").strip()
    course  = (request.args.get("course") or "").strip()
    tag_raw = (request.args.get("tag") or "").strip()
    tag = ",".join([t.strip().lstrip("#").lower() for t in tag_raw.split(",") if t.strip()]) if tag_raw else ""
    sort    = (request.args.get("sort") or "newest").lower()

    db = get_db()
    cur = db.cursor()

    sql = """
      SELECT
        p.id, p.title, p.course, p.tags, p.prompt, p.created_at,
        (SELECT COUNT(*) FROM VideoReply r WHERE r.post_id = p.id) AS reply_count,
        (SELECT COALESCE(ROUND(SUM(clear+correct+concise)*1.0/NULLIF(COUNT(*),0),1), NULL)
           FROM VideoReply r2 WHERE r2.post_id = p.id) AS q_avg
      FROM ProblemPost p
      WHERE 1=1
    """
    params = []

    if q:
        like = f"%{q.lower()}%"
        sql += " AND (LOWER(p.title) LIKE ? OR LOWER(p.prompt) LIKE ?) "
        params += [like, like]

    if course:
        sql += " AND LOWER(p.course) = ? "
        params += [course.lower()]

    if tag:
        sql += " AND (',' || LOWER(p.tags) || ',') LIKE ? "
        params += [f"%,{tag},%"]

    if sort == "replies":
        sql += " ORDER BY reply_count DESC, datetime(p.created_at) DESC "
    elif sort == "qscore":
        sql += " ORDER BY (q_avg IS NULL), q_avg DESC, datetime(p.created_at) DESC "
    else:
        sql += " ORDER BY datetime(p.created_at) DESC "

    cur.execute(sql, params)
    posts = cur.fetchall()

    data = [{"row": p, "q_avg": p["q_avg"]} for p in posts]
    state = {"q": q, "course": course, "tag": tag_raw, "sort": sort}
    return render_template("index.html", posts=data, state=state)

@app.route("/new", methods=["GET","POST"])
def new_post():
    if request.method == "POST":
        title   = (request.form.get("title") or "").strip()
        course  = (request.form.get("course") or "").strip()
        tags    = normalize_tags(request.form.get("tags") or "")
        prompt  = (request.form.get("prompt") or "").strip()
        honor   = request.form.get("honor")

        form_data = {"title": title, "course": course, "tags": tags, "prompt": prompt}
        honor_checked = bool(honor)

        if not (title and course and tags and prompt and honor):
            flash("Please fill all fields and accept the Honor Code.")
            return render_template("new_post.html", form_data=form_data, honor_checked=honor_checked)

        db = get_db()
        db.execute(
            "INSERT INTO ProblemPost(title,course,tags,prompt,author_id) VALUES (?,?,?,?,1)",
            (title, course, tags, prompt),
        )
        db.commit()
        flash("Post created.")
        return redirect(url_for("index"))

    return render_template("new_post.html", form_data={}, honor_checked=False)

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT * FROM ProblemPost WHERE id=?", (post_id,))
    post = cur.fetchone()
    if not post:
        return ("Not found", 404)

    # All replies
    cur.execute("""
        SELECT *, (clear+correct+concise) AS qscore
        FROM VideoReply
        WHERE post_id=?
        ORDER BY datetime(created_at) DESC
    """, (post_id,))
    replies = [dict(r) for r in cur.fetchall()]

    # User votes + reports
    sid = session.get("session_id")
    user_votes = {f"{row['reply_id']}_{row['dimension']}" for row in db.execute(
        "SELECT reply_id, dimension FROM VoteRecord WHERE session_id=?", (sid,)
    )}
    user_reports = {row["reply_id"] for row in db.execute(
        "SELECT reply_id FROM ReportRecord WHERE session_id=?", (sid,)
    )}

    ttr = time_to_first_reply(db, post_id)
    return render_template(
        "post_detail.html",
        post=post,
        replies=replies,
        ttr=ttr,
        user_votes=user_votes,
        user_reports=user_reports
    )

# --- Upload and Reply ---
@app.route("/post/<int:post_id>/reply", methods=["POST"])
def add_reply(post_id):
    file = request.files.get("video_file")
    transcript = (request.form.get("transcript") or "").strip()

    if not file or file.filename == "":
        flash("You must select a video file.")
        return redirect(url_for("post_detail", post_id=post_id))

    if not allowed_file(file.filename):
        flash("Unsupported video format. Allowed: mp4, webm, ogg, ogv, m4v, mov.")
        return redirect(url_for("post_detail", post_id=post_id))

    if not transcript:
        flash("Transcript is required.")
        return redirect(url_for("post_detail", post_id=post_id))

    filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{secure_filename(file.filename)}"
    save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(save_path)

    db = get_db()
    db.execute(
        "INSERT INTO VideoReply (post_id, video_path, transcript, author_id) VALUES (?,?,?,1)",
        (post_id, filename, transcript),
    )
    db.commit()

    flash("Reply added successfully.")
    return redirect(url_for("post_detail", post_id=post_id))

@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)

# --- Voting ---
@app.route("/reply/<int:reply_id>/rate", methods=["POST"])
def rate_reply(reply_id):
    dim = request.form.get("dim")
    if dim not in ("clear", "correct", "concise"):
        return redirect(url_for("index"))

    sid = session.get("session_id")
    db = get_db()
    cur = db.cursor()

    # Check if vote exists
    cur.execute("SELECT id FROM VoteRecord WHERE reply_id=? AND session_id=? AND dimension=?", (reply_id, sid, dim))
    row = cur.fetchone()

    if row:
        # Unvote
        cur.execute("DELETE FROM VoteRecord WHERE id=?", (row["id"],))
        cur.execute(f"UPDATE VideoReply SET {dim}={dim}-1, upvotes=upvotes-1 WHERE id=?", (reply_id,))
        flash(f"Removed your {dim} vote.")
    else:
        # New vote
        cur.execute("INSERT INTO VoteRecord (reply_id, session_id, dimension) VALUES (?,?,?)", (reply_id, sid, dim))
        cur.execute(f"UPDATE VideoReply SET {dim}={dim}+1, upvotes=upvotes+1 WHERE id=?", (reply_id,))
        flash(f"Marked {dim}.")

    db.commit()
    return redirect(request.referrer or url_for("index"))


# --- Report ---
@app.route("/reply/<int:reply_id>/report", methods=["POST"])
def report_reply(reply_id):
    sid = session.get("session_id")
    db = get_db()
    cur = db.cursor()

    cur.execute("SELECT id FROM ReportRecord WHERE reply_id=? AND session_id=?", (reply_id, sid))
    row = cur.fetchone()

    if row:
        cur.execute("DELETE FROM ReportRecord WHERE id=?", (row["id"],))
        cur.execute("UPDATE VideoReply SET flags=flags-1 WHERE id=?", (reply_id,))
        flash("Report removed.")
    else:
        cur.execute("INSERT INTO ReportRecord (reply_id, session_id) VALUES (?, ?)", (reply_id, sid))
        cur.execute("UPDATE VideoReply SET flags=flags+1 WHERE id=?", (reply_id,))
        flash("Reply reported.")

    db.commit()
    return redirect(request.referrer or url_for("index"))

# --- Run ---
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
