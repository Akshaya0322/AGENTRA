"""Reusable prompt templates for AGENTRA.

The prompts are deliberately concise and enforce *ground‑only* answering.
"""

# Prompt used by AnswerGenerationAgent – the context placeholder will be filled with
# retrieved chunk texts (including source citations). The agent must not hallucinate.
ANSWER_PROMPT = (
    "Answer the following question using ONLY the provided context. "
    "If the answer cannot be found in the context, respond with the exact sentence: "
    "'I could not find the answer in the uploaded documents.' "
    "Include citations in the form '[DocumentName (page X)]' after each relevant statement.\n\n"
    "Context:\n{context}\n\n"
    "Question: {question}\n"
)

# Prompt for summarization – the full concatenated text of all chunks is supplied.
SUMMARY_PROMPT = (
    "Create a concise, structured markdown summary of the supplied text. "
    "Use headings and bullet points. Highlight the most important topics, key points, "
    "and conclusions. Do NOT add information that is not present in the text.\n\n"
    "Text:\n{full_text}\n"
)
