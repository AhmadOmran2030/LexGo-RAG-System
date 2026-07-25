from importlib import import_module
import os

from dotenv import load_dotenv
from openai import OpenAI

build_context = import_module("06_retrieve_context").build_context

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/free")


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


def ask_openrouter(prompt):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
    except Exception as error:
        status_code = getattr(error, "status_code", "unknown")
        message = getattr(error, "message", str(error))
        return f"OpenRouter error ({status_code}): {message}"
    return response.choices[0].message.content


def answer_question(question):
    context, sources = build_context(question)
    prompt = build_prompt(question, context)

    if not OPENROUTER_API_KEY:
        return "Missing OPENROUTER_API_KEY.", sources

    return ask_openrouter(prompt), sources
