import os
import sys
import sqlite3
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt6.QtCore import QTimer

#Accesses the database
def getNewPosts(existingIDs):
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    DB_PATH = os.path.join(BASE_DIR, "StudyLoop Database", "studyloop_clients.db")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if existingIDs:
        placeholders = ','.join('?' for _ in existingIDs)
        query = f"""
            SELECT id, title, course, tags, prompt, created_at, url, author_id
            FROM posts
            WHERE id NOT IN ({placeholders})
            ORDER BY created_at ASC
        """
        cursor.execute(query, tuple(existingIDs))
    else:
        cursor.execute("""
            SELECT id, title, course, tags, prompt, created_at, url, author_id
            FROM posts
            ORDER BY created_at ASC
        """)
    
    rows = cursor.fetchall()
    conn.close()
    return rows

#Feed window
class StudyLoopFeed(QWidget):
    def __init__(self):
        super().__init__()

        #Window settings
        self.setWindowTitle("StudyLoop Feed")
        self.setGeometry(200, 200, 500, 800)

        #Allows for widgets to be placed in window
        self.feedLayout = QVBoxLayout(self)

        #Adds and formats the scroll bar
        self.feedScroll = QScrollArea(self)
        self.feedScroll.setWidgetResizable(True)
        self.feedLayout.addWidget(self.feedScroll)

        #Creates the individual posts
        #Allows a layout for the posts
        self.feedScrollContent = QWidget()
        self.feedScroll.setWidget(self.feedScrollContent)
        self.contentLayout = QVBoxLayout(self.feedScrollContent)

        #Track displayed post IDs
        self.DisplayedIDs = set()

        #Initial load
        self.loadNewPosts()

        #Timer to refresh every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.loadNewPosts)
        self.timer.start(5000)

        self.setLayout(self.feedLayout)

    def loadNewPosts(self):
        #Fetch new posts not already displayed
        posts = getNewPosts(self.DisplayedIDs)
        if posts:
            for post in posts:
                post_id, title, course, tags, prompt, created_at, url, author_id = post
                postLabel = QLabel(
                    f"<b>{title}</b> ({course})<br>"
                    f"{prompt}<br>"
                    f"Tags: {tags}<br>"
                    f"Posted by User {author_id}<br>"
                    f"<i>{created_at}</i><br>"
                    f"Link: {url}"
                )
                postLabel.setWordWrap(True)
                self.contentLayout.addWidget(postLabel)

                #Track that this post is now displayed
                self.DisplayedIDs.add(post_id)

            #Scroll to newest post
            scrollBar = self.feedScroll.verticalScrollBar()
            scrollBar.setValue(scrollBar.maximum())

        self.feedScrollContent.setLayout(self.contentLayout)

app = QApplication(sys.argv)
window = StudyLoopFeed()
window.show()
sys.exit(app.exec())