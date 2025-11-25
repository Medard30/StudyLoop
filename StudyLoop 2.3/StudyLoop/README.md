# StudyLoop — Week 12 Integration & QA Sprint (v2.2)

An academic Q&A platform where students post problems, upload short video replies, and rate clarity/correctness/conciseness.  
This build (v2.2) adds **toggle voting** (you can undo a rating in a category).

## Core Flow
New Post → View Post → Upload Reply (video + transcript) → Rate/Report → Data persists in SQLite.

## Setup
- Requirements
==> Python 3.11+ recommended
- Installation Steps
1. Create virtual environment (recommended):
==> python -m venv .venv
2. Activate virtual environment:
- Windows (CMD):
==> .\.venv\Scripts\activate
- Windows (PowerShell):
==> Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
     .\.venv\Scripts\Activate
- macOS/Linux:
==> source .venv/bin/activate
3. Install dependencies:
==> pip install -r requirements.txt

## Run
==> python app.py
4. Deactivate Virtual Environment
==> deactivate

## Run
python app.py
→ http://127.0.0.1:5000

## Feature slice
- Create Post (title, course, tags normalized, prompt)
- Filter feed by text/course/tag; sort by newest/replies/Q-score
- View Post, upload video reply (MP4/WebM/OGG/OGV), transcript required
- Rate replies (Clear/Correct/Concise) and report

## Files
- Database: studyloop.db (auto-created)
- Uploads:  /uploads (auto-created)
