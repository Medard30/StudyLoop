# StudyLoop — MVP (Week 5)
Minimal Flask + SQLite demo (Proposal: StudyLoop).

## Features
- Home feed (seeded posts)
- New Post (Title, Course, Tags, Prompt, Honor Code)
- Post Detail + Reply (video URL + required transcript)
- Rate (Clear/Correct/Concise) + Report (flags)
- Flask 3.x-safe DB handling (flask.g + teardown); preserves form values on validation error

## How to run
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
python app.py
# open http://127.0.0.1:5000
```
The app auto-creates `studyloop.db` and seeds demo content on first run.
