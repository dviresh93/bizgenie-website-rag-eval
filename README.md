# Website RAG Chatbot

A modular RAG (Retrieval-Augmented Generation) system that allows you to index any website and ask questions about its content. Built with FastAPI, ChromaDB, Jina AI, and Claude 3 Opus.

## Features

- **URL Indexing:** Uses [Jina AI Reader](https://jina.ai/reader) to fetch and clean website content.
- **Vector Search:** Uses [ChromaDB](https://www.trychroma.com/) and OpenAI embeddings for semantic search.
- **Smart Answers:** Uses **Claude 3 Opus** (via Anthropic API) to generate accurate answers based on the retrieved context.
- **Simple UI:** Clean web interface to interact with the system.
- **Dockerized:** Fully containerized setup for easy deployment.

## Prerequisites

- Docker & Docker Compose
- OpenAI API Key (for embeddings)
- Anthropic API Key (for Claude)
- Jina AI API Key (optional, for higher rate limits)

## Quick Start

1.  **Clone the repository:**
    ```bash
    git clone git@github.com:dviresh93/bizgenie-website-rag-eval.git
    cd bizgenie-website-rag-eval
    ```

2.  **Set up environment variables:**
    Copy the example file and add your API keys:
    ```bash
    cp .env.example .env
    # Edit .env with your keys
    ```

3.  **Run with Docker:**
    ```bash
    docker-compose up -d --build
    ```

4.  **Access the UI:**
    Open [http://localhost:8000](http://localhost:8000) in your browser.

## Architecture

- **Frontend:** Static HTML/JS served by FastAPI.
- **Backend:** FastAPI (Python) at `/api/v1`.
- **Database:** ChromaDB (Vector Store).

## Configuration

Configuration is managed in `config/configs.yaml`. You can change the active model or settings there.

```yaml
llm:
  options:
    model: "claude-3-opus-20240229" # Current active model
```

## Testing

Run the API integration tests:
```bash
docker-compose exec api python3 tests/test_endpoints.py
```