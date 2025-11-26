# Website RAG Chatbot

A modular RAG (Retrieval-Augmented Generation) system that allows you to index any website and ask questions about its content. Built with FastAPI, ChromaDB, Jina AI, and Claude 3 Opus.

## Features

- **URL Indexing:** Uses [Jina AI Reader](https://jina.ai/reader) to fetch and clean website content.
- **Vector Search:** Uses [ChromaDB](https://www.trychroma.com/) and OpenAI embeddings for semantic search.
- **Smart Answers:** Uses **Claude 3 Opus** (via Anthropic API) to generate accurate answers based on the retrieved context.
- **Simple UI:** Clean web interface to interact with the system.
- **Dockerized:** Fully containerized setup for easy deployment.

## Demo

[Watch the Introduction Video](https://drive.google.com/file/d/176K1GBaAhXD4zUE_W--ww8dX3Zkzz8lQ/view?usp=sharing)

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

## 📚 Additional Resources

- **[PLAN.md](PLAN.md)** - Comprehensive exploration of architecture options
- **[IMPLEMENTATION.md](IMPLEMENTATION.md)** - Detailed implementation strategy
- **[TODO.md](TODO.md)** - Developer guide with step-by-step instructions

### External Documentation
- [Jina AI Reader](https://github.com/jina-ai/reader) - Web to markdown converter
- [Claude API Docs](https://docs.anthropic.com/) - Anthropic's LLM API
- [ChromaDB Docs](https://docs.trychroma.com/) - Vector database
- [FastAPI Docs](https://fastapi.tiangolo.com/) - Web framework

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

---

## Troubleshooting

### Issue: "Error: No module named 'chromadb'" or similar during `pip install`

**Cause**: Python's "externally-managed-environment" policy prevents global package installation.

**Fix**:
The project is Dockerized. Dependencies are installed within the Docker container during build. Ensure `api/requirements.txt` is correct and rebuild the Docker image:
```bash
docker-compose build api
```

### Issue: `docker-compose up` fails due to port conflict

**Cause**: Another process is already using port 8000 or 8001.

**Fix:**
Identify and stop the conflicting process/container. For Docker containers:
```bash
docker ps # Find container using port 8000 or 8001
docker stop <CONTAINER_ID>
```
Then retry:
```bash
docker-compose up -d
```

### Issue: API returns "Error code: 404 - model not found" for LLM (e.g., Claude)

**Cause**: The specified LLM model name in `config/configs.yaml` is incorrect, not supported by your API key, or not available in your region.

**Fix:**
Update `config/configs.yaml` to use a model compatible with your Anthropic (or OpenAI) API key. Valid Claude models include `claude-3-opus-20240229` or `claude-3-haiku-20240307`.

```yaml
# Example for Claude Haiku
llm:
  plugin: "claude"
  api_key: ${ANTHROPIC_API_KEY}
  options:
    model: "claude-3-haiku-20240307"
    temperature: 0.7
```
After modifying `configs.yaml`, trigger an API reload:
```bash
touch api/app/main.py
```

### Issue: UI dropdown is empty, or "Nothing happens" on button click

**Cause**: Browser caching of old JavaScript, or incorrect script path.

**Fix:**
1.  **Hard Refresh:** Press `Ctrl + F5` (Windows/Linux) or `Cmd + Shift + R` (Mac) to force the browser to reload all assets.
2.  **Verify Script Path:** Ensure `ui/index.html` references `script.js` correctly:
    ```html
    <script src="/ui/script.js?v=2"></script>
    ```
    (Note the `/ui/` prefix).

### Issue: Frontend errors like `net::ERR_ABORTED 404 (Not Found)` for `script.js`

**Cause**: Incorrect path for `script.js` in `ui/index.html`. The FastAPI static files are served from `/ui/`.

**Fix:**
Ensure the script tag in `ui/index.html` specifies the full path:
```html
<script src="/ui/script.js?v=2"></script>
```

---

## 🗺️ Roadmap

### ✅ Completed (v1.0)

- [x] Plugin architecture with swappable components
- [x] Jina AI integration for web scraping
- [x] Claude 3 Opus for Q&A
- [x] ChromaDB for vector storage
- [x] REST API with FastAPI
- [x] Docker containerization
- [x] Configuration management
- [x] Simple web UI for indexing and querying

### 🚧 In Progress

- [ ] Additional data retrieval plugins (Tavily, Firecrawl)
- [ ] GPT-4 plugin for comparison
- [ ] Testing framework with metrics

---

## 💡 Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Claude 3](https://www.anthropic.com/claude) - LLM by Anthropic
- [Jina AI](https://jina.ai/) - Web content extraction
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [OpenAI](https://openai.com/) - Embeddings API

---

**Made with ❤️ for BizGenie AI**
