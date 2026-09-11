# GradeFlow AI V3 PRD

## Core requirement
Teachers can upload 100+ separate student answer-sheet PDFs in one Streamlit session and receive one consolidated grade sheet.

## Required inputs
- Question paper PDF
- Official answer key PDF
- Multiple student answer-sheet PDFs

## Required output columns
- Roll No
- Student Name
- Score
- Max Marks
- Percentage
- Grade
- Confidence
- Review Required
- Status
- File

## OCR requirement
Scanned/handwritten PDFs must use Groq Vision OCR. Multi-page papers are processed in batches of up to five page images per vision request.

## Reliability
Each student is processed independently. Exceptions are captured as ERROR rows so the batch continues.
