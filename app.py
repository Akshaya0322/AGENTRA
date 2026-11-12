import os
import shutil
from pathlib import Path
import streamlit as st

from utils.helpers import generate_session_id, validate_pdf
from agents.orchestrator import get_orchestrator

# ---------------------------------------------------------------------------
# Session & state initialization
# ---------------------------------------------------------------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = generate_session_id()

if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = get_orchestrator(st.session_state.session_id)

# Persistent workflow state dict – mirrors the LangGraph state schema
if "wf_state" not in st.session_state:
    st.session_state.wf_state = {
        "session_id": st.session_state.session_id,
        "uploaded_files": [],   # list of dicts {path, name, pages, error?}
        "new_files": [],        # pending file paths for processing
        "action": "none",
        "last_query": "",
        "chat_history": [],
        "summary": "",
    }

# Directory to store uploaded PDFs (inside the project data folder)
UPLOAD_DIR = Path(__file__).parents[0] / "data" / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# UI layout – dark navy / purple theme via CSS
# ---------------------------------------------------------------------------
st.set_page_config(page_title="AGENTRA – Multi‑Agent AI Document Assistant", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background: #0a0e27;  /* dark navy */
        color: #e0e0ff;
    }
    .stSidebar {
        background: #1a0e4d;  /* deep purple */
        color: #ffffff;
    }
    .stButton>button {
        background-color: #6c4a9c;  /* accent purple */
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar navigation
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("AGENTRA")
    nav = st.radio(
        "Navigation",
        ["New Chat", "Upload Documents", "Document Library", "Chat History", "Generate Summary", "About"],
        index=0,
    )
    st.markdown("---")
    if st.button("Clear Session"):
        # Reset everything – useful for fresh start
        for key in ["wf_state", "orchestrator", "session_id"]:
            if key in st.session_state:
                del st.session_state[key]
        st.experimental_rerun()

# ---------------------------------------------------------------------------
# Helper to run the orchestrator and update session state
# ---------------------------------------------------------------------------
def run_workflow():
    try:
        new_state = st.session_state.orchestrator.run(st.session_state.wf_state)
        st.session_state.wf_state.update(new_state)
    except Exception as exc:
        st.error(f"Workflow error: {exc}")

# ---------------------------------------------------------------------------
# Main content based on navigation selection
# ---------------------------------------------------------------------------
if nav == "New Chat":
    st.header("Start a new conversation")
    # Reset chat‑specific fields but keep uploaded docs
    st.session_state.wf_state["chat_history"] = []
    st.session_state.wf_state["summary"] = ""
    st.session_state.wf_state["action"] = "none"
    st.success("Chat cleared. You can now ask new questions.")

elif nav == "Upload Documents":
    st.header("Upload PDF Documents")
    uploaded = st.file_uploader("Choose PDF files", type=["pdf"], accept_multiple_files=True)
    if uploaded:
        for file in uploaded:
            # Save to the uploads folder
            save_path = UPLOAD_DIR / file.name
            with open(save_path, "wb") as f:
                f.write(file.getbuffer())
            # Validate quickly
            if not validate_pdf(str(save_path)):
                st.warning(f"{file.name} appears invalid and will be ignored.")
                continue
            # Queue for processing if not already present
            if not any(u["path"] == str(save_path) for u in st.session_state.wf_state["uploaded_files"]):
                st.session_state.wf_state["new_files"].append(str(save_path))
        # Trigger processing step
        st.session_state.wf_state["action"] = "process"
        with st.spinner("Processing uploaded PDFs …"):
            run_workflow()
        st.success("Documents processed.")
    # Show list of already processed documents
    if st.session_state.wf_state["uploaded_files"]:
        st.subheader("Uploaded Documents")
        for doc in st.session_state.wf_state["uploaded_files"]:
            name = doc.get("name", "unknown")
            pages = doc.get("pages", "?")
            err = doc.get("error", None)
            if err:
                st.write(f"- **{name}** – error: {err}")
            else:
                st.write(f"- **{name}** – {pages} page(s)")

elif nav == "Document Library":
    st.header("Document Library")
    if not st.session_state.wf_state["uploaded_files"]:
        st.info("No documents have been uploaded yet.")
    else:
        for doc in st.session_state.wf_state["uploaded_files"]:
            st.write(f"- **{doc.get('name', '')}** – {doc.get('pages', '?')} page(s)")

elif nav == "Chat History":
    st.header("Chat History")
    if not st.session_state.wf_state["chat_history"]:
        st.info("No conversation yet. Ask a question in the 'Ask AGENTRA' section.")
    else:
        for entry in st.session_state.wf_state["chat_history"]:
            role = entry.get("role")
            content = entry.get("content", "")
            if role == "user":
                st.markdown(f"**You:** {content}")
            else:
                st.markdown(f"**AGENTRA:** {content}")
                sources = entry.get("sources", [])
                if sources:
                    with st.expander("Sources"):
                        for src in sources:
                            doc_name = src.get("document_name", "unknown")
                            page = src.get("page_number", "?")
                            st.write(f"- {doc_name} (page {page})")

elif nav == "Generate Summary":
    st.header("Generate Document Summary")
    if not st.session_state.wf_state["uploaded_files"]:
        st.warning("Upload documents before generating a summary.")
    else:
        if st.button("Summarize All Documents"):
            st.session_state.wf_state["action"] = "summarize"
            with st.spinner("Generating summary …"):
                run_workflow()
            st.subheader("Summary")
            st.markdown(st.session_state.wf_state.get("summary", ""), unsafe_allow_html=True)

elif nav == "About":
    st.header("About AGENTRA")
    st.markdown(
        """
        **AGENTRA** is a demonstration of a multi‑agent Retrieval‑Augmented Generation (RAG) system built with:
        - **Google Gemini** for LLM responses
        - **LangGraph** for agent orchestration
        - **Sentence‑Transformers** embeddings stored in **ChromaDB**
        - **Streamlit** UI with a dark navy / purple theme
        
        Upload PDFs, ask questions, and get answers that cite exact document pages.
        """
    )

# ---------------------------------------------------------------------------
# Chat interface (always shown at the bottom of the main page regardless of nav)
# ---------------------------------------------------------------------------
st.markdown("---")
st.subheader("Ask AGENTRA")
question = st.chat_input("Type your question about the uploaded documents…")
if question:
    st.session_state.wf_state["last_query"] = question
    st.session_state.wf_state["action"] = "ask"
    with st.spinner("Generating answer …"):
        run_workflow()
    # Display the latest assistant message immediately
    if st.session_state.wf_state["chat_history"]:
        last = st.session_state.wf_state["chat_history"][-1]
        if last.get("role") == "assistant":
            st.markdown(f"**AGENTRA:** {last.get('content', '')}")
            srcs = last.get("sources", [])
            if srcs:
                with st.expander("Sources"):
                    for src in srcs:
                        doc_name = src.get("document_name", "unknown")
                        page = src.get("page_number", "?")
                        st.write(f"- {doc_name} (page {page})")
        # Also show user query (optional)
        st.markdown(f"**You:** {question}")

# Reset action after handling to avoid repeat execution on rerun
if st.session_state.wf_state.get("action") != "none":
    st.session_state.wf_state["action"] = "none"
