# GradeFlow AI V2 — Beginner Workflow

## A. Build

```text
Create project folder
       |
Install Python
       |
Create virtual environment
       |
pip install -r requirements.txt
       |
Add Groq key to .env
       |
streamlit run app.py
```

## B. Test

```text
Question PDF
Answer Key PDF
3 student PDFs
       |
       v
Start grading
       |
       v
Check dashboard
       |
       v
Check one student's marks
       |
       v
Check review queue
       |
       v
Download Excel
```

## C. Publish to GitHub

```text
GitHub
  |
New repository
  |
gradeflow-ai-v2
  |
git add .
git commit
git push
```

## D. Deploy

```text
Streamlit Community Cloud
        |
Connect GitHub
        |
Create app
        |
Repository = gradeflow-ai-v2
Branch = main
File = app.py
        |
Advanced settings
        |
Secrets = Groq key
        |
Deploy
```

## E. Final hackathon demonstration

### 1. Problem
"Checking 100 papers manually takes hours."

### 2. Input
"Here is the question paper, answer key and student batch."

### 3. AI
"The app extracts digital text or uses Groq Vision when the PDF is scanned."

### 4. Grading
"Groq evaluates each answer and returns structured marks."

### 5. Safety
"Low-confidence results are not silently accepted; they go to the teacher
review queue."

### 6. Intelligence
"The system also identifies difficult questions."

### 7. Output
"One Excel file contains the class result."

## V2.1 ideas

- Side-by-side original PDF and AI score
- Teacher edit score button
- Regrade selected question
- Login
- Database
- Class management
- Student report PDF
- Email reports
- Subject/topic analytics
- Plagiarism/similarity detection
