import os
import streamlit as st
import pandas as pd

from services.config import get_config
from services.pdf_service import extract_pdf_text
from services.groq_service import grade_student_paper, vision_ocr_pdf
from services.analytics import (
    results_to_dataframe,
    build_question_analytics,
    detect_review_flags,
)
from services.exports import make_excel, make_json_zip

st.set_page_config(
    page_title="GradeFlow AI V2",
    page_icon="📝",
    layout="wide",
)

cfg = get_config()

if "results" not in st.session_state:
    st.session_state.results = []

st.title("📝 GradeFlow AI V2")
st.caption("Bulk AI exam checking • Groq • Vision OCR • Teacher review • Analytics")

with st.sidebar:
    st.header("⚙️ Settings")

    grading_model = st.text_input(
        "Grading model",
        value=cfg.grading_model,
        help="Recommended: openai/gpt-oss-20b"
    )

    vision_model = st.text_input(
        "Vision/OCR model",
        value=cfg.vision_model,
        help="Recommended: qwen/qwen3.6-27b"
    )

    workers = st.slider(
        "Parallel workers",
        min_value=1,
        max_value=8,
        value=cfg.max_workers,
    )

    max_marks = st.number_input(
        "Exam maximum marks",
        min_value=1,
        max_value=10000,
        value=100,
    )

    review_threshold = st.slider(
        "Manual review threshold",
        0.0, 1.0, cfg.review_threshold, 0.05
    )

    use_vision = st.checkbox(
        "Use Groq Vision OCR for scanned/handwritten PDFs",
        value=True,
    )

    st.divider()
    st.markdown("### API status")
    if cfg.api_key:
        st.success("Groq API key loaded")
    else:
        st.error("GROQ_API_KEY missing")

    st.caption(
        "For a first demo, use 5–10 papers. For 100+ papers, keep workers "
        "low enough to respect your Groq limits."
    )

st.markdown("## 1. Exam setup")

c1, c2 = st.columns(2)

with c1:
    question_file = st.file_uploader(
        "Question paper PDF",
        type=["pdf"],
        key="question_file",
    )

with c2:
    answer_key_file = st.file_uploader(
        "Official answer key PDF",
        type=["pdf"],
        key="answer_key_file",
    )

question_text = ""
answer_key_text = ""

if question_file and answer_key_file:
    with st.spinner("Reading exam documents..."):
        question_text = extract_pdf_text(question_file.getvalue())
        answer_key_text = extract_pdf_text(answer_key_file.getvalue())

    q1, q2 = st.columns(2)
    q1.metric("Question paper characters", f"{len(question_text):,}")
    q2.metric("Answer key characters", f"{len(answer_key_text):,}")

    with st.expander("Preview exam text"):
        st.text_area("Question paper", question_text[:10000], height=220)
        st.text_area("Answer key", answer_key_text[:10000], height=220)

st.markdown("## 2. Student papers")

student_files = st.file_uploader(
    "Upload student answer-sheet PDFs",
    type=["pdf"],
    accept_multiple_files=True,
    key="student_files",
)

if student_files:
    st.info(f"{len(student_files)} student paper(s) selected.")

if st.button("🚀 Start bulk grading", type="primary", use_container_width=True):
    if not cfg.api_key:
        st.error("No Groq API key. Add GROQ_API_KEY to Streamlit Secrets or .env.")
        st.stop()

    if not question_file or not answer_key_file:
        st.error("Upload the question paper and answer key first.")
        st.stop()

    if not student_files:
        st.error("Upload at least one student paper.")
        st.stop()

    progress = st.progress(0)
    status = st.empty()
    results = []

    from concurrent.futures import ThreadPoolExecutor, as_completed

    def process(uploaded):
        pdf_bytes = uploaded.getvalue()

        try:
            text = extract_pdf_text(pdf_bytes)

            # If text extraction is poor, use Groq Vision to transcribe pages.
            if use_vision and len(text.strip()) < cfg.min_text_chars_for_ocr:
                text = vision_ocr_pdf(
                    api_key=cfg.api_key,
                    pdf_bytes=pdf_bytes,
                    model=vision_model,
                    max_pages=cfg.max_vision_pages,
                )

            if not text.strip():
                raise ValueError("No readable text could be extracted.")

            result = grade_student_paper(
                api_key=cfg.api_key,
                grading_model=grading_model,
                question_paper=question_text,
                answer_key=answer_key_text,
                student_text=text,
                max_marks=int(max_marks),
            )

            result["filename"] = uploaded.name
            result["review_required"] = (
                float(result.get("confidence", 0)) < review_threshold
                or result.get("student_name", "Unknown") in ["Unknown", ""]
                or result.get("roll_no", "Unknown") in ["Unknown", ""]
            )
            result["review_reasons"] = detect_review_flags(
                result, review_threshold
            )
            return result

        except Exception as exc:
            return {
                "filename": uploaded.name,
                "student_name": "ERROR",
                "roll_no": "ERROR",
                "score": 0,
                "total_marks": int(max_marks),
                "percentage": 0,
                "grade": "ERROR",
                "confidence": 0,
                "feedback": str(exc),
                "question_results": [],
                "review_required": True,
                "review_reasons": [str(exc)],
                "error": str(exc),
            }

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(process, f) for f in student_files]

        for i, future in enumerate(as_completed(futures), start=1):
            results.append(future.result())
            progress.progress(i / len(futures))
            status.write(f"Processed {i}/{len(futures)} papers...")

    st.session_state.results = results
    st.success(f"Completed {len(results)} paper(s).")

if st.session_state.results:
    df = results_to_dataframe(st.session_state.results)

    st.markdown("---")
    st.markdown("## 📊 Results dashboard")

    valid = pd.to_numeric(df["Score"], errors="coerce")
    review_count = int(df["Review Required"].fillna(False).sum())

    a, b, c, d, e = st.columns(5)
    a.metric("Papers", len(df))
    b.metric("Average", f"{valid.mean():.1f}")
    c.metric("Highest", f"{valid.max():.1f}")
    d.metric("Review", review_count)
    e.metric("Errors", int((df["Status"] == "ERROR").sum()))

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("## 📈 Class analytics")

    qdf = build_question_analytics(st.session_state.results)

    if not qdf.empty:
        st.bar_chart(
            qdf.set_index("Question")["Average Marks"]
        )

        st.dataframe(
            qdf,
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("## ⚠️ Teacher review queue")

    review_items = [
        r for r in st.session_state.results
        if r.get("review_required")
    ]

    if not review_items:
        st.success("No papers currently require manual review.")
    else:
        st.warning(f"{len(review_items)} paper(s) require review.")

        for r in review_items:
            with st.expander(
                f"{r.get('student_name')} • {r.get('roll_no')} • "
                f"{r.get('score')}/{r.get('total_marks')}"
            ):
                st.write("**Why review is required:**")
                for reason in r.get("review_reasons", []):
                    st.write(f"- {reason}")

                st.write("**AI feedback:**")
                st.write(r.get("feedback", ""))

                if r.get("question_results"):
                    st.dataframe(
                        pd.DataFrame(r["question_results"]),
                        use_container_width=True,
                        hide_index=True,
                    )

    st.markdown("## 👩‍🏫 Individual student reports")

    for r in st.session_state.results:
        title = (
            f"{r.get('student_name')} • {r.get('roll_no')} • "
            f"{r.get('score')}/{r.get('total_marks')}"
        )

        with st.expander(title):
            x, y, z = st.columns(3)
            x.metric("Score", f"{r.get('score')}/{r.get('total_marks')}")
            y.metric("Grade", r.get("grade"))
            z.metric("AI confidence", f"{float(r.get('confidence', 0))*100:.0f}%")

            st.write(r.get("feedback", ""))

            if r.get("question_results"):
                st.dataframe(
                    pd.DataFrame(r["question_results"]),
                    use_container_width=True,
                    hide_index=True,
                )

    st.markdown("## ⬇️ Export")

    excel_bytes = make_excel(st.session_state.results)
    zip_bytes = make_json_zip(st.session_state.results)

    d1, d2 = st.columns(2)

    with d1:
        st.download_button(
            "Download Excel report",
            data=excel_bytes,
            file_name="gradeflow_v2_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

    with d2:
        st.download_button(
            "Download feedback ZIP",
            data=zip_bytes,
            file_name="gradeflow_v2_feedback.zip",
            mime="application/zip",
            use_container_width=True,
        )

st.markdown("---")
st.caption(
    "GradeFlow AI is an AI-assisted marking tool. For high-stakes examinations, "
    "a teacher should review low-confidence or flagged results."
)
