import os
from typing import Any, Dict, List, TypedDict

from langgraph.graph import StateGraph, START, END

from agents.document_agent import DocumentProcessingAgent
from agents.answer_agent import AnswerGenerationAgent
from agents.summary_agent import SummaryAgent
class AgentState(TypedDict):
    session_id: str
    uploaded_files: list
    new_files: list
    action: str
    last_query: str
    chat_history: list
    summary: str
class WorkflowOrchestrator:

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.graph = StateGraph(self._state_schema())
        self._build_graph()
        self.compiled = self.graph.compile()

    @staticmethod
    def _state_schema():
        return AgentState

    def _build_graph(self) -> None:
        self.graph.add_node("process_docs", self._process_documents)
        self.graph.add_node("answer", self._answer_question)
        self.graph.add_node("summarize", self._summarize)

        def route(state: Dict[str, Any]):
            return state.get("action", "none")

        self.graph.add_conditional_edges(
            START,
            route,
            {
                "process": "process_docs",
                "ask": "answer",
                "summarize": "summarize",
                "none": END,
            },
        )

        self.graph.add_edge("process_docs", END)
        self.graph.add_edge("answer", END)
        self.graph.add_edge("summarize", END)
    
    # ---------------------------------------------------------------------
    # Node implementations
    # ---------------------------------------------------------------------
    def _process_documents(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process any pending PDFs and store their chunks.
        Updates `uploaded_files` and clears `new_files`.
        """
        pending: List[str] = state.get("new_files", [])
        if not pending:
            return state
        doc_agent = DocumentProcessingAgent(self.session_id)
        processed_meta: List[Dict[str, Any]] = []
        for fpath in pending:
            # Skip if already processed in this session
            if any(u["path"] == fpath for u in state.get("uploaded_files", [])):
                continue
            try:
                chunk_meta = doc_agent.process_pdf(fpath)
                page_numbers = {m["page_number"] for m in chunk_meta}
                processed_meta.append({
                    "path": fpath,
                    "name": os.path.basename(fpath),
                    "pages": len(page_numbers),
                })
            except Exception as exc:
                processed_meta.append({
                    "path": fpath,
                    "name": os.path.basename(fpath),
                    "pages": 0,
                    "error": str(exc),
                })
        # Merge with existing metadata
        state.setdefault("uploaded_files", []).extend(processed_meta)
        state["new_files"] = []
        return state

    def _answer_question(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Run retrieval and Gemini answer generation for the latest query."""
        query = state.get("last_query", "").strip()
        if not query:
            return state
        answer_agent = AnswerGenerationAgent()
        try:
            result = answer_agent.answer(self.session_id, query)
            answer = result.get("answer", "")
            sources = result.get("sources", [])
        except Exception as exc:
            answer = f"Error during answer generation: {exc}"
            sources = []
        # Record in chat history
        state.setdefault("chat_history", []).append({"role": "user", "content": query})
        state["chat_history"].append({"role": "assistant", "content": answer, "sources": sources})
        state["last_query"] = ""
        return state

    def _summarize(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a markdown summary of all uploaded documents for the session."""
        summary_agent = SummaryAgent()
        try:
            summary = summary_agent.summarize(self.session_id)
        except Exception as exc:
            summary = f"Error during summarization: {exc}"
        state["summary"] = summary
        return state

    # ---------------------------------------------------------------------
    # Graph construction helpers
    # ---------------------------------------------------------------------
    

    # ---------------------------------------------------------------------
    # Public run method
    # ---------------------------------------------------------------------
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the graph with the supplied state and return the updated state."""
        # The compiled LangGraph object provides an ``invoke`` method. Using ``invoke``
        # works across LangGraph versions (some expose ``__call__`` while others only
        # implement ``invoke``). This avoids the ``CompiledStateGraph object is not
        # callable`` error.
        if hasattr(self.compiled, "invoke"):
            return self.compiled.invoke(state)
        # Fallback for older versions that support direct call.
        return self.compiled(state)

# ---------------------------------------------------------------------
# Convenience accessor for Streamlit callers
# ---------------------------------------------------------------------
def get_orchestrator(session_id: str) -> WorkflowOrchestrator:
    """Factory that returns a new orchestrator; callers may cache it in
    ``st.session_state`` for reuse across runs.
    """
    return WorkflowOrchestrator(session_id)
