from importlib import import_module
import os

from dotenv import load_dotenv
from openai import OpenAI

build_context = import_module("06_retrieve_context").build_context

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def build_prompt(question, context):
    return f"""You are a careful, grounded legal policy assistant.
Use only the provided context. Do not use outside knowledge.
If the context is not enough, say you do not know rather than guessing.
Prefer CURRENT sources over OUTDATED sources, and note when a source is outdated.
Cite sources like [Source 1].
This is general information about internal policy, not legal advice.

Question:
{question}

Context:
{context}
"""


def ask_openai(prompt):
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content


def answer_question(question):
    context, sources = build_context(question)
    prompt = build_prompt(question, context)

    if not OPENAI_API_KEY:
        return "Missing OPENAI_API_KEY.", sources

    return ask_openai(prompt), sources
