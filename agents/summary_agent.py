
from google import genai
from config.settings import GEMINI_API_KEY, GEMINI_MODEL_NAME


class SummaryAgent:
    """Summarizes uploaded document content using Gemini."""

    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY not set. Please configure your .env file."
            )

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model_name = GEMINI_MODEL_NAME

    def summarize(self, text: str) -> str:
        """Generate a structured summary of the supplied document text."""

        if not text or not text.strip():
            return "No document content is available to summarize."

        prompt = f"""
You are AGENTRA, an AI document summarization assistant.

Summarize the following document content using ONLY the information provided.

Use this structure:
1. Overview
2. Key Points
3. Important Facts
4. Conclusion

Do not invent information.

DOCUMENT CONTENT:
{text}

SUMMARY:
"""

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )

            if response.text:
                return response.text.strip()

            return "Gemini returned an empty summary."

        except Exception as e:
            return f"Error generating summary: {str(e)}"
