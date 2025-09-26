import sys
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QTextEdit, QVBoxLayout, QCheckBox, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QBrush, QPen

#Window creation
class PostWindow(QWidget):
    def __init__(self):
        super().__init__()

        #Window settings
        self.setWindowTitle("StudyLoop Make a Post")
        self.setGeometry(100, 100, 500, 800)
        self.setStyleSheet("background-color: white;")

        #Feature settings

        #Post Button
        self.postButton = QPushButton("Post", self)
        self.postButton.setGeometry(200, 690, 100, 40)
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

        #Title Textbox
        self.postTitle = QLineEdit(self)
        self.postTitle.setGeometry(100, 500, 300, 30)
        self.postTitle.setPlaceholderText("Title: Short and Focused")

        #Title Textbox
        self.postPrompt = QTextEdit(self)
        self.postPrompt.setGeometry(50, 540, 400, 50)
        self.postPrompt.setPlaceholderText("Prompt: What is your problem?")

        #Course Textbox
        self.postCourse = QLineEdit(self)
        self.postCourse.setGeometry(50, 600, 120, 30)
        self.postCourse.setPlaceholderText("Course: 'Calc 1'")

        #Tags Textbox
        self.postTags = QLineEdit(self)
        self.postTags.setGeometry(180, 600, 270, 30)
        self.postTags.setPlaceholderText("Tags: '#Limits' '# Trig'")

        #Honor Checkbox
        self.postHoner = QCheckBox(self)
        self.postHoner.setGeometry(350, 630, 30, 30)
        self.postHoner.setStyleSheet("""
        QCheckBox {
            background-color: transparent;
            color: black;
        }
        """)

        #Honor Textbox
        self.honorWarning = QLabel("Check this to confirm this is your own work/context.", self)
        self.honorWarning.setGeometry(75, 630, 270, 30)
        self.honorWarning.setStyleSheet("""
        QLabel {
            background-color: transparent;
            color: black;
        }
        """)

    #Shape settings
    def paintEvent(self, event):
        shapeMaker = QPainter(self)

        shapeMaker.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.SolidLine))
        shapeMaker.setBrush(QBrush(Qt.GlobalColor.lightGray, Qt.BrushStyle.SolidPattern))
        shapeMaker.drawRect(0, 490, 500, 310)


app = QApplication(sys.argv)
window=PostWindow()
window.show()
sys.exit(app.exec())