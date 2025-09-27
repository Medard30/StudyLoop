# StudyLoop — MVP (Week 5)
Minimal Flask + SQLite demo that supports:
- Create a **Problem Post**
- Add a **Reply (video URL + transcript)**
- List posts on a **Feed**
- View a **Thread** with replies
- **Rate** replies and **Report**

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
# open http://localhost:5000
```
The app auto-creates `studyloop.db` and seeds demo content on first run.
