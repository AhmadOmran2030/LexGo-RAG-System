from importlib import import_module
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load context builder from your module
build_context = import_module("06_retrieve_context").build_context

# 2. Fetch API Key from .env (Local) or st.secrets (Streamlit Cloud)
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
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
    # Standard OpenAI client initialization
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    return response.choices[0].message.content


def answer_question(question):
    if not OPENAI_API_KEY:
        return (
            "Error: Missing `OPENAI_API_KEY`. Please set it in your `.env` or `.streamlit/secrets.toml` file.",
            [],
        )

    context, sources = build_context(question)
    prompt = build_prompt(question, context)

    return ask_openai(prompt), sources


# --- Streamlit Interface ---

st.set_page_config(page_title="Legal Policy Assistant", page_icon="⚖️", layout="centered")

st.title("⚖️ Legal Policy Assistant")
st.caption("Ask questions grounded strictly in internal policy context.")

# Initialize chat session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display message history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "sources" in msg and msg["sources"]:
            with st.expander("Retrieved Sources"):
                for src in msg["sources"]:
                    st.write(f"- {src}")

# Handle new user input
if question := st.chat_input("Ask a policy question..."):
    # Display user input
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    # Process and display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Searching policies and generating response..."):
            answer, sources = answer_question(question)
            st.markdown(answer)
            
            if sources:
                with st.expander("Retrieved Sources"):
                    for src in sources:
                        st.write(f"- {src}")

    # Store assistant response in session state
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources
    })
