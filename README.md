# AGENTRA – Multi-Agent AI Document Assistant

An AI-powered document assistant that allows users to upload PDF documents, generate summaries, and ask questions using Retrieval-Augmented Generation (RAG).

AGENTRA uses semantic search, vector databases, Google Gemini and a LangGraph-based agent workflow to provide document-grounded responses with source references.

## Project Overview

Reading and searching large documents manually can be time-consuming. AGENTRA simplifies this process by allowing users to interact with their PDF documents through a conversational AI interface.

Users can upload documents, retrieve relevant information, generate summaries and ask questions based on the uploaded content.

## Features

- **PDF Upload:** Upload PDF documents through an interactive Streamlit interface.
- **Text Extraction:** Extract text from PDF documents.
- **Text Chunking:** Split extracted content into smaller chunks for efficient retrieval.
- **Semantic Search:** Find relevant document content using sentence embeddings.
- **Vector Storage:** Store document embeddings in ChromaDB.
- **AI-Powered Q&A:** Generate contextual answers using Google Gemini.
- **Document Summarization:** Generate summaries of document content.
- **Source References:** Display document filenames and page numbers associated with retrieved content.
- **Multi-Document Support:** Upload and query multiple PDF documents within a session.
- **Agent Workflow:** Organize document processing, retrieval, answer generation and summarization into separate agent components.

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python |
| Frontend | Streamlit |
| LLM | Google Gemini API |
| Agent Orchestration | LangGraph |
| RAG Framework | Retrieval-Augmented Generation |
| Embedding Model | Sentence Transformers |
| Embedding Model Name | all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| PDF Processing | PyPDF2 |
| Text Chunking | LangChain Text Splitters |
| Environment Management | Python Virtual Environment, python-dotenv |

## System Architecture

```text
             USER
               |
               v
       STREAMLIT INTERFACE
               |
               v
        PDF DOCUMENT UPLOAD
               |
               v
     DOCUMENT PROCESSING AGENT
               |
        PDF TEXT EXTRACTION
               |
          TEXT CHUNKING
               |
               v
       EMBEDDING GENERATION
               |
               v
           CHROMADB
               |
               v
        RETRIEVAL AGENT
               |
       SEMANTIC SIMILARITY
               |
               v
      RELEVANT DOCUMENT CONTEXT
               |
               v
       ANSWER GENERATION AGENT
               |
          GEMINI API
               |
               v
       CONTEXTUAL AI RESPONSE
               |
               v
       SOURCE REFERENCES
```

The LangGraph orchestrator coordinates the agent workflow.

## Project Structure

```text
AGENTRA/
│
├── agents/
│   ├── document_agent.py
│   ├── retrieval_agent.py
│   ├── answer_agent.py
│   ├── summary_agent.py
│   └── orchestrator.py
│
├── config/
│   └── settings.py
│
├── rag/
│   ├── pdf_processor.py
│   ├── text_chunker.py
│   ├── embeddings.py
│   └── vector_store.py
│
├── utils/
│   ├── helpers.py
│   └── prompts.py
│
├── tests/
│   ├── test_chunking.py
│   ├── test_pdf_processor.py
│   └── test_retrieval.py
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone https://github.com/Akshaya0322/AGENTRA.git
cd AGENTRA
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

**Windows PowerShell:**

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure the Gemini API key

Create a `.env` file in the project root directory.

Copy the configuration from `.env.example`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL_NAME=gemini-2.5-flash
```

Get your API key from [Google AI Studio](https://aistudio.google.com/apikey).

**Important:** Never upload your actual `.env` file or API key to GitHub.

### 6. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

## How AGENTRA Works

1. The user uploads one or more PDF documents.
2. The Document Processing Agent extracts text from the PDFs.
3. Extracted text is divided into smaller chunks.
4. Sentence Transformers converts the chunks into numerical embeddings.
5. ChromaDB stores the document chunks and their embeddings.
6. When a user asks a question, the Retrieval Agent searches for relevant content.
7. The Answer Generation Agent sends the retrieved context and question to Google Gemini.
8. Gemini generates a response grounded in the retrieved document content.
9. AGENTRA displays the response along with document and page references.

## Future Enhancements

- Improve complete document-wide retrieval for long PDFs.
- Add advanced multi-agent collaboration and task routing.
- Implement conversation memory across sessions.
- Add support for Word documents and additional file formats.
- Improve source citation accuracy.
- Add automated evaluation of retrieval and answer quality.
- Deploy the application using Streamlit Community Cloud or another hosting platform.

## Learning Outcomes

Through this project, I am developing practical experience in:

- Retrieval-Augmented Generation (RAG).
- Large Language Model (LLM) integration.
- Multi-agent workflow orchestration.
- Vector databases and semantic search.
- Embedding generation and document processing.
- API integration and Python application development.

## Author

**Akshaya G**

B.Tech – Information Technology  
Nandha Engineering College | 2027

GitHub: [Akshaya0322](https://github.com/Akshaya0322)

---

⭐ If you find this project interesting, feel free to explore the repository!
