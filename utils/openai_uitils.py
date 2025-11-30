# utils/openai_utils.py
import os
import openai
from typing import List, Dict
import time

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    # openai will error later if missing; we leave this here for clarity
    pass
openai.api_key = OPENAI_API_KEY

def call_chat(messages: List[Dict], model: str = "gpt-3.5-turbo", max_tokens: int = 512, temperature: float = 0.2):
    """
    Single wrapper for ChatCompletion calls.
    messages: list of {"role": "system"/"user"/"assistant", "content": "..."}
    """
    backoff = 1
    for attempt in range(4):
        try:
            resp = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            time.sleep(backoff)
            backoff *= 2
    raise RuntimeError("OpenAI request failed after retries.")

def summarize_text(text: str, max_len: int = 300):
    prompt = [
        {"role":"system", "content": "You are a helpful assistant that creates concise study summaries."},
        {"role":"user", "content": f"Summarize the following notes into a concise, structured study summary. Use bullet points and sections. Keep it under {max_len} words.\n\n{text}"}
    ]
    return call_chat(prompt, max_tokens=500)

def generate_flashcards(text: str, num: int = 10):
    prompt = [
        {"role":"system", "content": "You are an assistant that creates study flashcards (question-answer pairs)."},
        {"role":"user", "content": f"From the text below, generate {num} concise flashcards in JSON array form. Each item should have 'question' and 'answer' fields. Keep answers short (1-3 sentences).\n\n{text}"}
    ]
    return call_chat(prompt, max_tokens=700)

def generate_mcq(text: str, num: int = 5):
    prompt = [
        {"role":"system", "content": "You create multiple-choice questions (MCQs)."},
        {"role":"user", "content": f"From the text below, create {num} MCQs. Return JSON array where each element has: 'question', 'choices' (list of 4 choices), and 'answer' (the correct choice exactly as in choices). Make plausible distractors.\n\n{text}"}
    ]
    return call_chat(prompt, max_tokens=700)

def generate_tf(text: str, num: int = 8):
    prompt = [
        {"role":"system", "content": "You create True/False questions."},
        {"role":"user", "content": f"From the text below, create {num} True/False questions in JSON array form. Each item: 'statement' and 'answer' (True or False). Keep statements short.\n\n{text}"}
    ]
    return call_chat(prompt,max_tokens=700)
