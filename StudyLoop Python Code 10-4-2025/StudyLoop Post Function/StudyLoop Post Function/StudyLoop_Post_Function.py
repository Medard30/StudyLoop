import datetime
import sys
import sqlite3
import json
import os
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QTextEdit, QCheckBox, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QBrush, QPen

#Looks for the database and checks it's there
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "..", "StudyLoop Database", "studyloop_clients.db"))
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

#Creates database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    course TEXT,
    tags TEXT,
    prompt TEXT,
    created_at TEXT,
    author_id INTEGER,
    url TEXT
    )
    """)
    conn.commit()
    conn.close()

#Window creation
class PostWindow(QWidget):
    def __init__(self):
        super().__init__()

        #Window settings
        self.setWindowTitle("StudyLoop Make a Post")
        self.setGeometry(100, 100, 500, 800)
        self.setFixedSize(500, 800)
        self.setStyleSheet("background-color: white;")

        #Feature settings

        #Post Button
        self.postButton = QPushButton("Post", self)
        self.postButton.setGeometry(200, 700, 100, 40)
        self.postButton.clicked.connect(self.handlePost)
        self.postButton.setStyleSheet("""
        QPushButton {
            background-color: green;
            color: white;
        }
        QPushButton:hover {
            background-color: #4cb828;
        }
        QPushButton:pressed {
            background-color: gray;
        }
        """)

        #Title Textbox
        self.postTitle = QLineEdit(self)
        self.postTitle.setGeometry(100, 500, 300, 30)
        self.postTitle.setPlaceholderText("Title: Short and Focused")
        self.postTitle.setStyleSheet("""
        QLineEdit {
            color: black;
        }
        """)

        #Prompt Textbox
        self.postPrompt = QTextEdit(self)
        self.postPrompt.setGeometry(50, 540, 400, 50)
        self.postPrompt.setPlaceholderText("Prompt: What is your problem?")
        self.postPrompt.setStyleSheet("""
        QTextEdit {
            color: black;
        }
        """)

        #Course Textbox
        self.postCourse = QLineEdit(self)
        self.postCourse.setGeometry(50, 600, 120, 30)
        self.postCourse.setPlaceholderText("Course: 'Calc 1'")
        self.postCourse.setStyleSheet("""
        QLineEdit {
            color: black;
        }
        """)

        #Tags Textbox
        self.postTags = QLineEdit(self)
        self.postTags.setGeometry(180, 600, 270, 30)
        self.postTags.setPlaceholderText("Tags: '#Limits' '# Trig'")
        self.postTags.setStyleSheet("""
        QLineEdit {
            color: black;
        }
        """)

        #Honor Checkbox
        self.postHoner = QCheckBox(self)
        self.postHoner.setGeometry(370, 630, 30, 30)
        self.postHoner.setStyleSheet("""
        QCheckBox {
            background-color: transparent;
        }
        QCheckBox::indicator {
            background-color: darkred;
        }
        QCheckBox::indicator:checked {
            background-color: green;
        }
        """)

        #Honor Textbox
        self.honorWarning = QLabel("Make this green to confirm this is your own work/context.", self)
        self.honorWarning.setGeometry(60, 630, 310, 30)
        self.honorWarning.setStyleSheet("""
        QLabel {
            background-color: transparent;
            color: black;
        }
        """)

        #Placeholder Textbox
        self.previewText = QLabel("Placeholder Text for Video Preview", self)
        self.previewText.setGeometry(50, 200, 400, 30)
        self.previewText.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.previewText.setStyleSheet("""
        QLabel {
            background-color: transparent;
            color: black;
            font-size: 20px;
        }
        """)

        #Post URL
        self.postURL = QLineEdit(self)
        self.postURL.setGeometry(50, 660, 400, 30)
        self.postURL.setPlaceholderText("Paste your video here; Youtube URL or Google Drive Link")
        self.postURL.setStyleSheet("""
        QLineEdit {
            background-color: white;
            color: black;
        }
        """)

    #Shape settings
    def paintEvent(self, event):
        shapeMaker = QPainter(self)

        shapeMaker.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
        shapeMaker.setBrush(QBrush(Qt.GlobalColor.lightGray, Qt.BrushStyle.SolidPattern))
        shapeMaker.drawRect(0, 490, 500, 310)

    #Will store post into databse
    def storePost(self, post):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO posts (title, course, tags, prompt, created_at, author_id, url)
            VALUES (?,?,?,?,?,?,?)
        """, (post["title"], post["course"], post["tags"], post["prompt"], post["created_at"], post["author_id"], post["url"]))
        conn.commit()
        conn.close()

    #Code For Handling Contents and Posting
    def handlePost(self):
        if not self.postHoner.isChecked():
            print("You must confirm Honor before posting!")
            return

        post = {
        "title": self.postTitle.text(),
        "prompt": self.postPrompt.toPlainText(),
        "course": self.postCourse.text(),
        "tags": self.postTags.text(),
        "url": self.postURL.text().strip(),
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "author_id": 1 #Placeholder for user accounts
        }

        if "youtube.com" in post["url"] or "youtu.be" in post["url"]:
            print("YouTube Link")
        elif "drive.google.com" in post["url"]:
            print("Google Drive Link")
        else:
            print("Invalid or Unsupported Link")
            return

        #Code for the post being displayed on StudyLoop
        self.storePost(post)

        print("Post Stored")
        print(post)

init_db()
app = QApplication(sys.argv)
window=PostWindow()
window.show()
sys.exit(app.exec())