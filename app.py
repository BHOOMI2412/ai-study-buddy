# app.py
import streamlit as st
import json
import pandas as pd
from utils.pdf_parser import extract_text_from_pdf
from utils.openai_uitils import summarize_text, generate_flashcards, generate_mcq, generate_tf
from io import BytesIO
import base64

st.set_page_config(page_title="AI Study Buddy", layout="wide", page_icon="📚")

st.title("📚 AI Study Buddy — Notes → Summary → Flashcards → Quiz")
st.markdown("Upload lecture notes (PDF) or paste text. The app will generate a summary, flashcards, MCQs and True/False questions.")

with st.sidebar:
    st.header("Settings")
    num_flash = st.number_input("Flashcards to generate", min_value=3, max_value=50, value=10)
    num_mcq = st.number_input("MCQs to generate", min_value=1, max_value=20, value=5)
    num_tf = st.number_input("True/False to generate", min_value=1, max_value=30, value=8)
    st.markdown("---")
    st.markdown("⚠ Requires an environment variable OPENAI_API_KEY set before running.")

uploaded = st.file_uploader("Upload PDF (or leave empty to paste text)", type=["pdf"], accept_multiple_files=False)

text_input = st.text_area("Or paste your notes here (plain text)", height=200)

col1, col2 = st.columns([2,1])

with col1:
    if uploaded:
        st.info("Extracting text from uploaded PDF...")
        raw_text = extract_text_from_pdf(uploaded)
    else:
        raw_text = text_input

    if not raw_text or raw_text.strip()=="":
        st.warning("Please upload a PDF or paste some notes to proceed.")
    else:
        st.success("Text ready for processing.")
        if st.button("Generate Study Pack"):
            with st.spinner("Generating summary and study materials... this may take 20-60s depending on your API speed"):
                try:
                    summary = summarize_text(raw_text)
                    flash_raw = generate_flashcards(raw_text, num=int(num_flash))
                    mcq_raw = generate_mcq(raw_text, num=int(num_mcq))
                    tf_raw = generate_tf(raw_text, num=int(num_tf))
                except Exception as e:
                    st.error(f"Error calling API: {e}")
                    st.stop()

            # Try parsing JSON outputs safely
            def safe_parse_json(s):
                try:
                    return json.loads(s)
                except Exception:
                    # Try to extract first JSON-looking substring
                    import re
                    m = re.search(r'(\[.*\])', s, re.S)
                    if m:
                        try:
                            return json.loads(m.group(1))
                        except:
                            return None
                    return None

            flashcards = safe_parse_json(flash_raw)
            mcqs = safe_parse_json(mcq_raw)
            tfs = safe_parse_json(tf_raw)

            st.subheader("📌 Summary")
            st.write(summary)

            st.subheader("🃏 Flashcards")
            if flashcards:
                for i, f in enumerate(flashcards, 1):
                    q = f.get("question") if isinstance(f, dict) else None
                    a = f.get("answer") if isinstance(f, dict) else None
                    with st.expander(f"Card {i}: {q[:120] if q else 'Untitled'}"):
                        st.markdown(f"*Q:* {q}")
                        st.markdown(f"*A:* {a}")
                df_flash = pd.DataFrame([{"question":f.get("question"), "answer":f.get("answer")} for f in flashcards])
                csv = df_flash.to_csv(index=False).encode()
                st.download_button("Download Flashcards CSV", csv, file_name="flashcards.csv", mime="text/csv")
            else:
                st.warning("Could not parse flashcards JSON. Raw output below.")
                st.code(flash_raw)

            st.subheader("❓ Multiple Choice Questions")
            if mcqs:
                answers = []
                for i, m in enumerate(mcqs, 1):
                    question = m.get("question")
                    choices = m.get("choices")
                    correct = m.get("answer")
                    st.write(f"*Q{i}. {question}*")
                    if choices and isinstance(choices, list):
                        sel = st.radio(f"Select answer for Q{i}", choices, key=f"mcq_{i}")
                        if st.button(f"Reveal answer Q{i}", key=f"reveal_mcq_{i}"):
                            st.success(f"Correct answer: *{correct}*")
                df_mcq = pd.DataFrame(mcqs)
                st.download_button("Download MCQs JSON", json.dumps(mcqs, indent=2), file_name="mcqs.json")
            else:
                st.warning("Could not parse MCQs JSON. Raw output below.")
                st.code(mcq_raw)

            st.subheader("✅ True / False")
            if tfs:
                for i, t in enumerate(tfs, 1):
                    st.write(f"{i}. {t.get('statement')}")
                    picked = st.radio(f"Answer {i}", ["True","False"], key=f"tf_{i}")
                    if st.button(f"Reveal TF answer {i}", key=f"reveal_tf_{i}"):
                        st.success(f"Correct: *{t.get('answer')}*")
                st.download_button("Download TrueFalse JSON", json.dumps(tfs, indent=2), file_name="tf.json")
            else:
                st.warning("Could not parse True/False JSON. Raw output below.")
                st.code(tf_raw)

        st.balloons()
