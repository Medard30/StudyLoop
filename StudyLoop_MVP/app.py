
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3, os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "studyloop.db")

def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = get_db()
    cur = con.cursor()
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
    con.commit()
    # Seed minimal data
    cur.execute("SELECT COUNT(*) FROM User"); uc = cur.fetchone()[0]
    if uc == 0:
        cur.execute("INSERT INTO User(name) VALUES (?)", ("DemoUser",)); con.commit()
    cur.execute("SELECT COUNT(*) FROM ProblemPost"); pc = cur.fetchone()[0]
    if pc == 0:
        cur.execute("INSERT INTO ProblemPost(title,course,tags,prompt,author_id) VALUES (?,?,?,?,1)",
                    ("Limit sin(x)/x as x→0", "Calc I", "limits,trig", "Why does L'Hôpital give 1 here?"))
        cur.execute("INSERT INTO ProblemPost(title,course,tags,prompt,author_id) VALUES (?,?,?,?,1)",
                    ("For loop skipping last item", "CS1", "python,loops", "Why is last item skipped?"))
        con.commit()
        cur.execute("INSERT INTO VideoReply(post_id,video_url,transcript,upvotes,author_id,clear,correct,concise) VALUES (1,?,?,5,1,3,3,3)",
                    ("https://example.com/unlisted1", "Use series or L'Hôpital: sin x ~ x."))
        cur.execute("INSERT INTO VideoReply(post_id,video_url,transcript,upvotes,author_id,clear,correct,concise) VALUES (2,?,?,3,1,2,2,2)",
                    ("https://example.com/unlisted2", "Range issue: use enumerate or check indices."))
        con.commit()
    con.close()

def time_to_first_reply(con, post_id):
    cur = con.cursor()
    cur.execute("SELECT MIN(datetime(created_at)) FROM VideoReply WHERE post_id=?", (post_id,))
    first = cur.fetchone()[0]
    if first:
        cur.execute("SELECT datetime(created_at) FROM ProblemPost WHERE id=?", (post_id,))
        ptime = cur.fetchone()[0]
        if ptime:
            cur.execute("SELECT CAST((julianday(?) - julianday(?)) * 24 * 60 AS INTEGER)", (first, ptime))
            return cur.fetchone()[0]
    return None

app = Flask(__name__)
app.secret_key = "dev-key"

@app.before_first_request
def startup(): init_db()

@app.route("/")
def index():
    con = get_db(); cur = con.cursor()
    cur.execute("""
      SELECT p.id, p.title, p.course, p.tags, p.created_at,
             (SELECT COUNT(*) FROM VideoReply r WHERE r.post_id=p.id) AS reply_count
      FROM ProblemPost p
      ORDER BY datetime(p.created_at) DESC""")
    posts = cur.fetchall()
    data = []
    for p in posts:
        cur.execute("SELECT SUM(clear+correct+concise), COUNT(*) FROM VideoReply WHERE post_id=?", (p["id"],))
        s,n = cur.fetchone()
        q_avg = round(s/n,1) if n and s is not None else None
        data.append({"row": p, "q_avg": q_avg})
    con.close()
    return render_template("index.html", posts=data)

@app.route("/new", methods=["GET","POST"])
def new_post():
    if request.method == "POST":
        title = request.form.get("title","").strip()
        course = request.form.get("course","").strip()
        tags = request.form.get("tags","").strip()
        prompt = request.form.get("prompt","").strip()
        honor = request.form.get("honor")
        if not (title and course and tags and prompt and honor):
            flash("Please fill all fields and accept the Honor Code."); return redirect(url_for("new_post"))
        con = get_db()
        con.execute("INSERT INTO ProblemPost(title,course,tags,prompt,author_id) VALUES (?,?,?,?,1)",
                    (title,course,tags,prompt))
        con.commit(); con.close(); flash("Post created."); return redirect(url_for("index"))
    return render_template("new_post.html")

@app.route("/post/<int:post_id>")
def post_detail(post_id):
    con = get_db(); cur = con.cursor()
    cur.execute("SELECT * FROM ProblemPost WHERE id=?", (post_id,)); post = cur.fetchone()
    if not post: con.close(); return ("Not found", 404)
    cur.execute("""SELECT *, (clear+correct+concise) as qscore
                   FROM VideoReply WHERE post_id=? ORDER BY datetime(created_at) DESC""", (post_id,))
    replies = cur.fetchall()
    ttr = time_to_first_reply(con, post_id); con.close()
    return render_template("post_detail.html", post=post, replies=replies, ttr=ttr)

@app.route("/post/<int:post_id>/reply", methods=["POST"])
def add_reply(post_id):
    video_url = request.form.get("video_url","").strip()
    transcript = request.form.get("transcript","").strip()
    if not (video_url and transcript):
        flash("Video URL and Transcript are required."); return redirect(url_for("post_detail", post_id=post_id))
    con = get_db()
    con.execute("INSERT INTO VideoReply(post_id,video_url,transcript,author_id) VALUES (?,?,?,1)",
                (post_id, video_url, transcript))
    con.commit(); con.close(); flash("Reply added."); return redirect(url_for("post_detail", post_id=post_id))

@app.route("/reply/<int:reply_id>/rate", methods=["POST"])
def rate_reply(reply_id):
    dim = request.form.get("dim")
    if dim not in ("clear","correct","concise"): return redirect(url_for("index"))
    con = get_db()
    con.execute(f"UPDATE VideoReply SET {dim}={dim}+1, upvotes=upvotes+1 WHERE id=?", (reply_id,))
    con.commit(); con.close(); flash(f"Rated {dim}."); return redirect(request.referrer or url_for("index"))

@app.route("/reply/<int:reply_id>/report", methods=["POST"])
def report_reply(reply_id):
    con = get_db()
    con.execute("UPDATE VideoReply SET flags=flags+1 WHERE id=?", (reply_id,))
    con.commit(); con.close(); flash("Reply reported."); return redirect(request.referrer or url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
