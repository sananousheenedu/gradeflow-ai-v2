# GradeFlow AI V2 — PRD

## Product goal

Build a hackathon-ready AI-assisted examination platform that can process
100+ student answer PDFs, extract identities, use multimodal OCR for difficult
documents, grade against an official key, flag uncertain cases for teacher
review, and provide class-level analytics.

## V2 capabilities

### 1. Bulk ingestion
Input:
- Question paper PDF
- Answer key PDF
- 100+ student PDFs

### 2. Document understanding

Digital PDF:
```text
PDF -> text extraction
```

Scanned/handwritten PDF:
```text
PDF -> rendered images -> Groq Vision OCR -> text
```

### 3. AI grading

Inputs:
- Question paper
- Answer key
- Student answers

Outputs:
- Name
- Roll number
- Question marks
- Partial-credit status
- Total score
- Percentage
- Grade
- Confidence
- Feedback

### 4. Human-in-the-loop

A paper enters review when:
- Confidence < configured threshold
- Student identity is missing
- Roll number is missing
- Processing error occurs

### 5. Analytics

Class:
- Number of papers
- Average
- Highest
- Errors
- Review count

Question:
- Average marks
- Maximum marks
- Difficulty %

### 6. Export

- Excel
- JSON
- Per-student result files

## V2 architecture

```text
                    Streamlit Cloud
                          |
                    app.py frontend
                          |
        +-----------------+----------------+
        |                 |                |
   PDF Service       Groq Service      Analytics
        |                 |                |
     PyPDF/PyMuPDF    Vision OCR       Pandas
                          |
                     Groq API
                    /          \
              Vision OCR      Text grading
                    \          /
                       Result
                          |
              +-----------+-----------+
              |           |           |
           Dashboard   Review      Exports
```

## Non-functional requirements

- Secrets never committed to GitHub.
- Batch errors do not stop other papers.
- API retries.
- Bounded concurrency.
- Clear review flags.
- Downloadable audit information.
- Cloud deployment without local OCR system dependencies.

## Acceptance criteria

- [ ] 1 paper can be graded end-to-end.
- [ ] 10 papers can be graded.
- [ ] 100+ papers can be uploaded.
- [ ] Scanned PDF can use Vision OCR.
- [ ] Name and roll number appear in results when present.
- [ ] Low-confidence paper enters review queue.
- [ ] Question analytics appear.
- [ ] Excel download works.
- [ ] Streamlit Cloud deployment works.
- [ ] API key is stored only in secrets.
