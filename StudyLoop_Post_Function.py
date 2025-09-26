import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QTextEdit, QCheckBox, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QBrush, QPen

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

        #Save Draft Button
        self.draftButton = QPushButton("Save Draft", self)
        self.draftButton.setGeometry(200, 740, 100, 40)
        self.draftButton.setStyleSheet("""
        QPushButton {
            background-color: darkblue;
            color: white;
        }
        QPushButton:hover {
            background-color: #0004ff;
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

        
    #Code For Checking Contents and Posting
    def handlePost(self):
        if not self.postHoner.isChecked():
            print("You must confirm Honor before posting!")
            return

        title = self.postTitle.text()
        prompt = self.postPrompt.toPlainText()
        course = self.postCourse.text()
        tags = self.postTags.text()
        URL = self.postURL.text().strip()

        if "youtube.com" in URL or "youtu.be" in URL:
            print("YouTube Link")
        elif "drive.google.com" in URL:
            print("Google Drive Link")
        else:
            print("Invalid or Unsupported Link")
            return

        #Code for the post being displayed on StudyLoop
        print("Post submitted!")
        print("Title:", title)
        print("Prompt:", prompt)
        print("Course:", course)
        print("Tags:", tags)
        print("URL:", URL)


app = QApplication(sys.argv)
window=PostWindow()
window.show()
sys.exit(app.exec())