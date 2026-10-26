# Sourcely

Sourcely is a retrieval-augmented generation (RAG) application for asking questions about PDF documents. It retrieves relevant passages, generates answers grounded in those passages, and returns page-level source references.

## Capabilities

- **Page-level citations:** Answers can cite retrieved passages using numbered references. The API returns references with document titles, page numbers, and PDF links that open at the cited page.
- **Relational and vector storage:** PostgreSQL stores document and chunk records; ChromaDB stores embeddings and retrieval metadata. A shared chunk UUID links vector search results to their source records.
- **Separate ingestion stages:** PDF loading and chunk persistence are handled by `chunking.py`; embedding generation and vector upserts are handled by `vectorize.py`.
- **Grounded generation:** The prompt instructs the language model to answer from retrieved source text and to say when the sources do not contain the answer.
- **Database migrations:** Alembic manages PostgreSQL schema changes.
- **Provider integrations:** Jina generates embeddings, while Groq provides the chat completion used to generate answers.

## Sample document

The default ingestion configuration targets the [Claude Opus 5.5 System Card](https://www-cdn.anthropic.com/fc1b44717c85dc068bc6ba5024219938094694bd/Claude%20Opus%205.5%20System%20Card.pdf), which is also included in the repository.

## Architecture

### Ingestion and query flows

```mermaid
flowchart LR
    subgraph Ingestion
        A[PDF] --> B[Loader] --> C[Chunker]
        C -->|text + page_no| D[(Postgres)]
        D -->|ready_to_vectorize| E[Embed: Jina v5] --> F[(ChromaDB)]
    end
    subgraph Query
        Q[Question] --> G[Embed query] --> H[Top-k search in Chroma]
        H -->|chunk IDs| I[Fetch text from Postgres]
        I --> J[Grounded prompt] --> K[LLM] --> L[Answer + cited pages]
    end
```

### Technology stack

- **API:** FastAPI and Uvicorn
- **Relational database and ORM:** PostgreSQL and SQLAlchemy
- **Schema migrations:** Alembic
- **Vector database:** ChromaDB with cosine-distance search
- **PDF processing:** PyMuPDF through LangChain's PDF loader; LangChain text splitters
- **Embeddings:** Jina `jina-embeddings-v5-text-nano`
- **Answer generation:** Groq using `openai/gpt-oss-20b`
- **Web interface:** HTML and JavaScript served by the FastAPI application

## Retrieval defaults

- The text splitter uses a 1,000-character chunk size with 200 characters of overlap.
- Each query retrieves up to five nearest chunks from ChromaDB.
- ChromaDB uses cosine distance to rank vector results.

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/)
- A running PostgreSQL server and a database for the application
- Jina and Groq API keys

## Local setup

Run these commands from the repository root:

```bash
uv sync
cp src/model_rag/.env.example .env
```

Edit `.env` and provide your database URL and API keys:

```dotenv
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@localhost:5432/model_rag
JINA_API_KEY=your_jina_key
GROQ_API_KEY=your_groq_key
```

Create the PostgreSQL database if it does not already exist, then apply the migrations:

```bash
uv run alembic upgrade head
```

## Ingest a PDF

The current ingestion script uses `PDF_PATH`, `TITLE`, and `SOURCE_URL` constants in `src/model_rag/scripts/chunking.py`. Set these values for the PDF you want to ingest. The PDF path is resolved relative to the directory from which the script is run.

Run the ingestion stages from the repository root:

```bash
uv run python -m model_rag.scripts.chunking
uv run python -m model_rag.scripts.vectorize
```

The chunking stage stores the document and its page-aware text chunks in PostgreSQL with a `ready_to_vectorize` status. The vectorization stage processes eligible chunks in batches, upserts their embeddings into the persistent local ChromaDB collection, and marks successfully processed chunks as `vectorized`.

## Run the application

```bash
uv run uvicorn model_rag.main:app --reload
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) to use the web interface. Interactive API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

## API

### `POST /ask`

Request:

```json
{
  "query": "When was the system card published?"
}
```

Response:

```json
{
  "answer": "The system card was published on September 22, 2026 [1].",
  "references": [
    {
      "number": 1,
      "title": "Claude Opus 5.5 System Card",
      "page_no": 1,
      "url": "https://example.com/document.pdf#page=1"
    }
  ]
}
```

The `references` array contains the sources cited in the generated answer. Each reference includes its citation number, document title, page number, and page-specific URL.

## Project structure

```text
src/model_rag/
├── api/                 # FastAPI endpoints
├── db/                  # PostgreSQL models, sessions, and ChromaDB client
├── scripts/             # PDF chunking and vectorization workflows
├── services/            # Retrieval, embeddings, and LLM integrations
└── templates/           # Web interface
migrations/              # Alembic migration revisions
```

## Current implementation notes

- ChromaDB persists locally in the repository's `chroma_db/` directory.
- Chunking creates a new document record and new chunk IDs each time it runs. Vector upserts are idempotent for an existing chunk ID, but rerunning the chunking stage is not a deduplication mechanism.
- The embedding service currently sends `retrieval.query` as the Jina task for both query and passage embedding requests.
- The ingestion script is configured for one PDF at a time through constants in `chunking.py`.
- The application does not currently include authentication, document-level authorization, or a retrieval/answer evaluation suite. Deployments beyond local development should add and validate the operational and security controls appropriate to their environment.

## Roadmap

1. Add authentication and document-level access control.
2. Establish an evaluation set for retrieval relevance and answer quality.
3. Add request logging for queries, retrieved chunk IDs, and latency.
4. Provide a containerized local deployment for PostgreSQL, ChromaDB, and the API.
5. Evaluate hybrid search and reranking.
6. Support multi-document ingestion.
