# AI Study Buddy

A Streamlit app that converts uploaded notes into a study pack: summary, flashcards, MCQs, and True/False questions using the OpenAI API.

## Setup
1. Create virtualenv and activate it:
   python -m venv venv
   source venv/bin/activate   # or venv\Scripts\activate on Windows

2. Install:
   pip install -r requirements.txt

3. Set environment variable:
   export OPENAI_API_KEY="sk-..."
   # on Windows:
   # setx OPENAI_API_KEY "sk-..."

4. Run:
   streamlit run app.py

## Demo script
See demo script below.