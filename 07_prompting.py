import os
from importlib import import_module
from typing import Tuple, List, Dict, Any

from dotenv import load_dotenv
from openai import OpenAI

build_context = import_module("06_retrieve_context").build_context

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.3-70b-instruct:free")


def build_prompt(question: str, context: str) -> str:
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


def ask_openrouter(prompt: str) -> str:
    if not OPENROUTER_API_KEY:
        return "Error: Missing OPENROUTER_API_KEY environment variable."

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
        default_headers={
            "HTTP-Referer": "https://localhost",
            "X-Title": "Legal Policy RAG Assistant",
        },
    )

    try:
        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        if response and response.choices and len(response.choices) > 0:
            return response.choices[0].message.content or "Model returned an empty response."
        return "OpenRouter API returned an empty choice set."
    except Exception as error:
        status_code = getattr(error, "status_code", "unknown")
        message = getattr(error, "message", str(error))
        return f"OpenRouter error ({status_code}): {message}"


def answer_question(question: str) -> Tuple[str, List[Dict[str, Any]]]:
    context, sources = build_context(question)

    if not context:
        return "I could not find any relevant policy documents to answer your question.", []

    prompt = build_prompt(question, context)
    answer = ask_openrouter(prompt)
    
    return answer, sources
