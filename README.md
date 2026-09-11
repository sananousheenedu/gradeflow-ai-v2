# GradeFlow AI V2

AI-assisted bulk exam checking for 100+ student papers.

## V2 features

- Question paper PDF
- Answer key PDF
- 100+ student PDFs
- Digital PDF text extraction
- Groq Vision OCR fallback for scanned/handwritten pages
- Student name extraction
- Roll number extraction
- Question-level marking
- Partial credit
- AI confidence
- Automatic teacher review queue
- Class average/highest/error metrics
- Question difficulty analytics
- Excel export
- JSON feedback ZIP
- Streamlit Community Cloud deployment
- GitHub-ready project

## Architecture

```text
Streamlit
   |
   +-- Question PDF
   +-- Answer Key PDF
   +-- Student PDFs
          |
          v
   PDF text extraction
          |
          +---- enough text ----> Grading model
          |
          +---- little text ----> Groq Vision OCR
                                  |
                                  v
                              Grading model
                                  |
                                  v
                         Structured JSON result
                                  |
                  +---------------+----------------+
                  |               |                |
                  v               v                v
              Dashboard      Review Queue     Analytics
                                  |
                                  v
                              Excel/JSON
```

## Recommended models

Current Groq documentation lists:
- `openai/gpt-oss-20b` as a production model for text reasoning.
- `qwen/qwen3.6-27b` as a vision-capable preview model supporting image input,
  OCR, and JSON mode.

Model availability can change, so if Groq changes model IDs, replace the
values in Streamlit Secrets or `.env`.

## Local setup

### Step 1 — Install Python

Use Python 3.12.

Check:

```bash
python --version
```

### Step 2 — Create a folder

```bash
mkdir gradeflow-ai-v2
cd gradeflow-ai-v2
```

### Step 3 — Create virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 4 — Install packages

```bash
pip install -r requirements.txt
```

### Step 5 — Add API key

Copy `.env.example` to `.env`.

Windows:

```bash
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Edit `.env`:

```text
GROQ_API_KEY=your_real_key
```

Do NOT put the key in GitHub.

### Step 6 — Run

```bash
streamlit run app.py
```

## GitHub

Create a new GitHub repository named:

```text
gradeflow-ai-v2
```

Then:

```bash
git init
git add .
git commit -m "GradeFlow AI V2"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/gradeflow-ai-v2.git
git push -u origin main
```

## Streamlit Community Cloud

1. Open Streamlit Community Cloud.
2. Sign in with GitHub.
3. Connect your GitHub account.
4. Click Create app.
5. Select your `gradeflow-ai-v2` repository.
6. Branch: `main`
7. Main file: `app.py`
8. Open Advanced settings.
9. In Secrets, paste:

```toml
GROQ_API_KEY = "your_real_key"
GRADING_MODEL = "openai/gpt-oss-20b"
VISION_MODEL = "qwen/qwen3.6-27b"
MAX_WORKERS = "3"
REVIEW_THRESHOLD = "0.75"
MIN_TEXT_CHARS_FOR_OCR = "300"
MAX_VISION_PAGES = "20"
```

10. Click Deploy.

## First test

Do not begin with 100 papers.

Test:

```text
1 question paper
1 answer key
3 student papers
```

Then test:

```text
10 papers
```

Then:

```text
100+ papers
```

This lets you catch PDF/OCR/model problems before a large run.

## How V2 improves the original

### Original

```text
PDF -> OCR -> Groq grading -> results
```

### V2

```text
PDF
 |
 +--> text extraction
 |
 +--> if poor -> Groq Vision OCR
 |
 v
identity + answers
 |
 v
Groq grading
 |
 v
confidence
 |
 +--> high confidence -> results
 |
 +--> low confidence -> teacher review
 |
 v
analytics + Excel + JSON
```

## Handwriting note

Vision OCR can help with handwritten or scanned scripts, but handwriting
recognition is not guaranteed to be perfect. Always review low-confidence
papers.

## Scaling note

100+ papers does not mean 100+ simultaneous API calls. The app uses a bounded
worker pool. Start with 3 workers and increase carefully based on your Groq
limits.

## Hackathon demo

Show this sequence:

1. Upload exam.
2. Upload answer key.
3. Upload 10–100 student PDFs.
4. Click Start bulk grading.
5. Show progress.
6. Show class dashboard.
7. Open review queue.
8. Open a student's question-level marks.
9. Show question difficulty analytics.
10. Download Excel.

## Product pitch

"GradeFlow AI turns hours of manual paper checking into a teacher-in-the-loop
AI workflow: upload the exam, answer key and student papers, and get
identity-aware grading, explanations, confidence flags and class analytics."
