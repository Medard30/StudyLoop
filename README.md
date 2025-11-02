STUDYLOOP PROJECT.
=================

QA & Documentation (README + setup instructions).
Group 2 project.

*Project Overview
StudyLoop is an application designed as an academic study platform where students/users can post questions, share video explanations, and rate responses.
Core Features
1.	Home Feed: Browse seeded demonstration posts Create Post: Submit questions with title, course, tags, prompt, and honor code acknowledgment
2.	Post Details: View individual posts with community replies
3.	Reply System: Add video responses with required transcripts
4.	Rating System: Rate replies on three criteria (Clear, Correct, Concise)
5.	Reporting: Flag inappropriate content
6.	Search functionality
7.	Form Validation: Preserves user input on validation errors
8.	Backend: Flask 3.x
9.	Database: SQLite
10.	Database Access: Flask.g context + teardown handlers

Prerequisites:
Python 3.10 or higher
Pip python package installer
Step-by-Step Installation
1.	Download the Project
git clone https://github.com/Medard30/StudyLoop.git cd StudyLoop
2 .  Create Virtual Environment
  a)	Windows:
  •	bashpython -m venv .venv
  •	.\.venv\Scripts\activate
  b)	macOS/Linux:
  •	python3 -m venv .venv
  source .venv/bin/activate
3. Install Dependencies
  a.	bashpip install -r requirements.txt
  Expected dependencies:

  -	Flask>=3.0.0
  -	(Any other dependencies from your requirements.txt)

4. Run the Application
  -	python app.py
5. Access the Application
  -	Open your web browser and navigate to:
  http://127.0.0.1:5000
  -	First Run Behavior
  -	The application automatically creates studyloop.db on first run
  -	Demo content (posts, replies, ratings) is seeded automatically
  -	No manual database setup required

2.	Stopping the Application
  •	Press Ctrl+C in the terminal
  •	Deactivate virtual environment: deactivate

QA Testing Checklist
1. Installation & Setup Testing
  -	 Virtual environment creates successfully
  -	 All dependencies install without errors
  -	 Application starts without errors
  -	 Database file (studyloop.db) is created automatically
  -	 Demo data is seeded on first run
  -	 Application is accessible at http://127.0.0.1:5000
2. Home Feed Testing
  -	 Home page loads successfully
  -	 Seeded posts are displayed
  -	 Post titles are visible and clickable
  -	 Course tags are displayed
  -	 Navigation elements work correctly

3. Create Post Testing
  -	 "New Post" page loads
  -	 All form fields are present:
    -	 Title field
    -	 Course field
    -	 Tags field
    -	 Prompt/Question field
    -	 Honor Code checkbox
  -	 Form validation works:
    -	 Empty fields show appropriate errors
    -	 Honor Code must be checked
    -	 Form preserves input on validation error
    -	 Successful post submission redirects appropriately
    -	 New post appears in feed

4. Post Detail Testing
  -	 Clicking post title navigates to detail page
  -	 Post details display correctly:
  -	 Title
  -	 Course
  -	 Tags
  -	 Question/Prompt
  -	 Existing replies are visible
  -	 Reply count is accurate

5. Reply Functionality Testing
  -	 Reply form is accessible
  -	 Required fields:
    -	 Video upload field accepts input
    -	 Transcript field accepts input
  -	 Form validation:
    -	 Both fields are required
    -	 Empty submission shows errors
    -	 Form preserves input on error
  -	 Successful reply submission:
    -	 Reply appears on post detail page
    -	 Video URL is displayed/linked
    -	 Transcript is visible

6. Rating System Testing
3.	 Rating interface is visible on replies
4.	 Three rating criteria present:
5.	 Clear
6.	 Correct
7.	 Concise
8.	 Rating submission works
9.	 Rating counts update correctly
10.	 Users cannot rate multiple times (if implemented)

7. Report Functionality Testing
  -	 Report button/link is visible
  -	 Report submission works
  -	 Report flags are recorded
  -	 Inappropriate content flagging works

8. Database Integrity Testing
  -	 Data persists across application restarts
  -	 No database locks or corruption
  -	 Foreign key relationships maintained
  -	 Database teardown functions properly (flask.g cleanup)

9. Cross-Browser Testing
Test on multiple browsers:
  -	 Chrome/Chromium
  -	 Firefox
  -	 Safari (macOS)
  -	 Edge

10. Security Testing
  -	 SQL injection attempts are handled safely
  -	 XSS attempts are sanitized
  -	 Honor Code enforcement works
  -	 CSRF protection (if implemented)

MVP Scope
This is a Week 8 MVP with intentionally limited features for demonstration purposes.
