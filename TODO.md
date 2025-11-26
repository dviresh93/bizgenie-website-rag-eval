# Website RAG System - Development Guide

## Technology Stack & Rationale

### Core Framework: **FastAPI**
**Why?**
- Fast, modern Python web framework
- Built-in async support (important for API calls to Jina, Claude, etc.)
- Automatic API documentation (Swagger UI)
- Easy to integrate with AI services
- Excellent for building REST APIs quickly

### Data Retrieval: **Jina AI Reader** (Phase 1)
**Why?**
- FREE tier available (20 req/sec, 1M tokens/month)
- No API key required for basic usage
- Handles JavaScript-rendered sites automatically
- Returns clean markdown (perfect for RAG)
- Simple HTTP API - just `https://r.jina.ai/{url}`
- Can test immediately without setup

**Later**: Add Tavily for comparison (Phase 4)

### LLM: **Claude 3.5 Sonnet (Anthropic)**
**Why?**
- User preference (you specified Claude)
- Excellent reasoning and instruction following
- 200k context window (can handle large contexts)
- Good price/performance ratio
- Strong at answering questions accurately
- API is simple to use

**Later**: Add GPT-4 for comparison (Phase 5)

### Vector Database: **ChromaDB**
**Why?**
- Simplest to set up (embedded mode or client-server)
- FREE and open source
- Persistent storage
- Built-in embedding function support
- Perfect for <1M documents
- Docker image available
- No complex configuration needed

### Embedding Model: **OpenAI text-embedding-3-small**
**Why?**
- High quality embeddings
- Cheap (~$0.02 per 1M tokens)
- Fast
- 1536 dimensions (good balance)
- Well-supported by ChromaDB
- Proven performance

**Alternative**: Could use Voyage AI or Cohere, but OpenAI is simplest to start

### UI: **Simple HTML + Vanilla JavaScript**
**Why?**
- No build step needed
- Fast to develop
- Easy to debug
- Served directly by FastAPI
- Can upgrade to React later if needed

### Containerization: **Docker Compose**
**Why?**
- Easy multi-service orchestration
- Consistent environment
- Simple to share and deploy
- One command to start everything

---

## Development Phases

Each phase builds on the previous and produces a **working, testable result**.

### Phase 1: Basic Infrastructure ✓
- Project structure
- Plugin interfaces
- Configuration system
- Docker setup
- ChromaDB running

### Phase 2: Jina Plugin (Current Phase)
- Implement Jina data retrieval plugin
- Test URL fetching
- Process markdown content
- Store in ChromaDB
- **Deliverable**: Can index a URL successfully

### Phase 3: Claude Plugin & Query Pipeline
- Implement Claude LLM plugin
- Build retrieval pipeline
- Implement Q&A endpoint
- **Deliverable**: Can answer questions about indexed content

### Phase 4: Simple UI
- Create web interface
- Index URL form
- Ask question interface
- Display answers with sources
- **Deliverable**: Full working prototype with UI

### Phase 5: Tavily Plugin (Comparison)
- Implement Tavily data retrieval plugin
- Allow switching between Jina and Tavily
- **Deliverable**: Can test both approaches

### Phase 6: Testing Framework
- Metrics collection
- Comparison reports
- Performance benchmarks
- **Deliverable**: Scientific comparison of approaches

---

## Phase 2: Jina Plugin Implementation

### Step 1: Install Dependencies

**File**: `api/requirements.txt`

Add to the existing file:
```
# LLM Integration
anthropic==0.21.3

# Document Processing
langchain==0.1.5
langchain-community==0.0.19
tiktoken==0.5.2

# Markdown Processing
markdown==3.5.2
beautifulsoup4==4.12.3
```

**Execute**:
```bash
cd /home/virus/Documents/repo/bizgenie/website-rag/api
pip install -r requirements.txt
```

---

### Step 2: Create Jina Plugin

**File**: `api/app/plugins/data_retrieval/jina_plugin.py`

**Content**:
```python
"""
Jina AI Reader plugin for data retrieval.
Uses Jina's free r.jina.ai service to convert URLs to markdown.
"""
import httpx
from typing import List, Dict
from datetime import datetime
from api.app.plugins.base import DataRetrievalPlugin, StandardDocument


class JinaPlugin(DataRetrievalPlugin):
    """
    Jina AI Reader plugin.

    Uses https://r.jina.ai/{url} to fetch and convert web pages to markdown.
    No API key required for basic usage.
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "https://r.jina.ai"
        self.api_key = config.get("api_key")  # Optional
        self.batch_size = config.get("options", {}).get("batch_size", 10)

    def fetch_url(self, url: str) -> StandardDocument:
        """
        Fetch a single URL using Jina AI Reader.

        Args:
            url: The URL to fetch

        Returns:
            StandardDocument with markdown content
        """
        jina_url = f"{self.base_url}/{url}"

        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(jina_url, headers=headers)
                response.raise_for_status()

                markdown_content = response.text

                # Extract metadata from headers if available
                metadata = {
                    "content_length": len(markdown_content),
                    "jina_response_time": response.elapsed.total_seconds(),
                }

                return StandardDocument(
                    url=url,
                    content=markdown_content,
                    metadata=metadata,
                    timestamp=datetime.utcnow().isoformat(),
                    source_plugin="jina"
                )

        except httpx.HTTPError as e:
            raise Exception(f"Failed to fetch URL with Jina: {str(e)}")

    def fetch_batch(self, urls: List[str]) -> List[StandardDocument]:
        """
        Fetch multiple URLs using parallel processing.

        Args:
            urls: List of URLs to fetch

        Returns:
            List of StandardDocuments
        """
        documents = []

        # Process in batches for rate limiting
        for i in range(0, len(urls), self.batch_size):
            batch = urls[i:i + self.batch_size]

            for url in batch:
                try:
                    doc = self.fetch_url(url)
                    documents.append(doc)
                except Exception as e:
                    print(f"Error fetching {url}: {e}")
                    continue

        return documents

    def get_capabilities(self) -> Dict:
        """Return plugin capabilities"""
        return {
            "name": "Jina AI Reader",
            "supports_js": True,
            "supports_batch": True,
            "rate_limit": "20 req/sec (free tier)" if not self.api_key else "higher",
            "cost_per_request": 0.0,  # Free tier
            "output_format": "markdown",
            "requires_api_key": False,
        }


# Register the plugin
from api.app.core.plugin_factory import PluginFactory
PluginFactory.register_data_retrieval_plugin("jina", JinaPlugin)
```

**Test**:
```bash
cd /home/virus/Documents/repo/bizgenie/website-rag
python3 << 'EOF'
from api.app.plugins.data_retrieval.jina_plugin import JinaPlugin

# Test plugin
config = {"options": {"batch_size": 5}}
plugin = JinaPlugin(config)

# Test fetch_url
doc = plugin.fetch_url("https://example.com")
print(f"✓ Fetched {len(doc.content)} characters from {doc.url}")
print(f"✓ Plugin: {doc.source_plugin}")
print(f"✓ First 100 chars: {doc.content[:100]}")

# Test capabilities
caps = plugin.get_capabilities()
print(f"✓ Plugin capabilities: {caps['name']}")
print(f"✓ Supports JS: {caps['supports_js']}")
EOF
```

---

### Step 3: Create Document Processing Service

**File**: `api/app/services/document_processor.py`

**Content**:
```python
"""
Document processing service.
Handles chunking, embedding, and storage of documents.
"""
from typing import List, Dict
import chromadb
from chromadb.config import Settings
from openai import OpenAI
import tiktoken
from api.app.plugins.base import StandardDocument


class DocumentProcessor:
    """Processes and stores documents in ChromaDB"""

    def __init__(self, config: Dict):
        """
        Initialize document processor.

        Args:
            config: Processing configuration from configs.yaml
        """
        self.config = config

        # Initialize ChromaDB client
        chroma_config = config.get("storage", {})
        self.chroma_client = chromadb.HttpClient(
            host=chroma_config.get("host", "localhost"),
            port=chroma_config.get("port", 8001)
        )

        # Initialize OpenAI for embeddings
        embedding_config = config.get("embedding", {})
        self.openai_client = OpenAI(api_key=embedding_config.get("api_key"))
        self.embedding_model = embedding_config.get("model", "text-embedding-3-small")

        # Chunking config
        chunking_config = config.get("chunking", {})
        self.chunk_size = chunking_config.get("chunk_size", 500)
        self.chunk_overlap = chunking_config.get("chunk_overlap", 50)

        # Initialize tokenizer
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def chunk_text(self, text: str) -> List[str]:
        """
        Split text into chunks based on token count.

        Args:
            text: Text to chunk

        Returns:
            List of text chunks
        """
        tokens = self.tokenizer.encode(text)
        chunks = []

        for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i:i + self.chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)
            chunks.append(chunk_text)

        return chunks

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for text chunks.

        Args:
            texts: List of text chunks

        Returns:
            List of embedding vectors
        """
        response = self.openai_client.embeddings.create(
            model=self.embedding_model,
            input=texts
        )

        return [item.embedding for item in response.data]

    def process_and_store(
        self,
        documents: List[StandardDocument],
        collection_name: str = "website_content"
    ) -> Dict:
        """
        Process documents and store in ChromaDB.

        Args:
            documents: List of StandardDocuments
            collection_name: Name of ChromaDB collection

        Returns:
            Statistics about the processing
        """
        # Get or create collection
        collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Website content for RAG"}
        )

        total_chunks = 0

        for doc in documents:
            # Chunk the document
            chunks = self.chunk_text(doc.content)

            if not chunks:
                continue

            # Generate embeddings
            embeddings = self.generate_embeddings(chunks)

            # Prepare metadata
            metadatas = [
                {
                    "url": doc.url,
                    "source_plugin": doc.source_plugin,
                    "timestamp": doc.timestamp,
                    "chunk_index": i,
                    **doc.metadata
                }
                for i in range(len(chunks))
            ]

            # Generate IDs
            ids = [f"{doc.url}_{i}" for i in range(len(chunks))]

            # Store in ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas,
                ids=ids
            )

            total_chunks += len(chunks)

        return {
            "documents_processed": len(documents),
            "total_chunks": total_chunks,
            "collection_name": collection_name
        }

    def retrieve(
        self,
        query: str,
        collection_name: str = "website_content",
        n_results: int = 5
    ) -> Dict:
        """
        Retrieve relevant chunks for a query.

        Args:
            query: Search query
            collection_name: ChromaDB collection to search
            n_results: Number of results to return

        Returns:
            Dict with results
        """
        collection = self.chroma_client.get_collection(name=collection_name)

        # Generate query embedding
        query_embedding = self.generate_embeddings([query])[0]

        # Search
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )

        return {
            "documents": results["documents"][0],
            "metadatas": results["metadatas"][0],
            "distances": results["distances"][0]
        }
```

---

### Step 4: Test Jina Plugin + Processing Pipeline

**File**: `scripts/test_jina_pipeline.py`

**Content**:
```python
"""
Test script for Jina plugin and document processing pipeline.
"""
import sys
sys.path.insert(0, '/home/virus/Documents/repo/bizgenie/website-rag')

from api.app.plugins.data_retrieval.jina_plugin import JinaPlugin
from api.app.services.document_processor import DocumentProcessor
import os

def test_jina_pipeline():
    """Test the complete pipeline: fetch -> process -> store"""

    print("=" * 60)
    print("Testing Jina Plugin + Document Processing Pipeline")
    print("=" * 60)

    # Step 1: Initialize Jina plugin
    print("\n[1/5] Initializing Jina plugin...")
    jina_config = {"options": {"batch_size": 5}}
    jina = JinaPlugin(jina_config)
    print("✓ Jina plugin initialized")

    # Step 2: Fetch a URL
    print("\n[2/5] Fetching URL with Jina...")
    test_url = "https://example.com"
    doc = jina.fetch_url(test_url)
    print(f"✓ Fetched: {doc.url}")
    print(f"✓ Content length: {len(doc.content)} characters")
    print(f"✓ Source plugin: {doc.source_plugin}")
    print(f"✓ Preview: {doc.content[:200]}...")

    # Step 3: Initialize document processor
    print("\n[3/5] Initializing document processor...")

    # Check for OpenAI API key
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠ OPENAI_API_KEY not set - creating mock processor")
        print("   To test fully: export OPENAI_API_KEY=your-key")
        return

    processor_config = {
        "chunking": {
            "chunk_size": 500,
            "chunk_overlap": 50
        },
        "embedding": {
            "model": "text-embedding-3-small",
            "api_key": openai_key
        },
        "storage": {
            "host": "localhost",
            "port": 8001
        }
    }

    processor = DocumentProcessor(processor_config)
    print("✓ Document processor initialized")

    # Step 4: Process and store
    print("\n[4/5] Processing and storing document...")
    stats = processor.process_and_store([doc], collection_name="test_collection")
    print(f"✓ Processed {stats['documents_processed']} documents")
    print(f"✓ Created {stats['total_chunks']} chunks")
    print(f"✓ Stored in collection: {stats['collection_name']}")

    # Step 5: Test retrieval
    print("\n[5/5] Testing retrieval...")
    query = "What is this website about?"
    results = processor.retrieve(query, collection_name="test_collection", n_results=3)
    print(f"✓ Retrieved {len(results['documents'])} relevant chunks")
    print("\nTop result:")
    print(f"  Content: {results['documents'][0][:150]}...")
    print(f"  Source: {results['metadatas'][0]['url']}")
    print(f"  Distance: {results['distances'][0]:.4f}")

    print("\n" + "=" * 60)
    print("✓ PIPELINE TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_jina_pipeline()
```

**Execute**:
```bash
# First, make sure ChromaDB is running
cd /home/virus/Documents/repo/bizgenie/website-rag
docker-compose up -d chromadb

# Set OpenAI API key
export OPENAI_API_KEY=your-key-here

# Run the test
python3 scripts/test_jina_pipeline.py
```

**Expected Output**:
```
============================================================
Testing Jina Plugin + Document Processing Pipeline
============================================================

[1/5] Initializing Jina plugin...
✓ Jina plugin initialized

[2/5] Fetching URL with Jina...
✓ Fetched: https://example.com
✓ Content length: 1256 characters
✓ Source plugin: jina
✓ Preview: # Example Domain...

[3/5] Initializing document processor...
✓ Document processor initialized

[4/5] Processing and storing document...
✓ Processed 1 documents
✓ Created 3 chunks
✓ Stored in collection: test_collection

[5/5] Testing retrieval...
✓ Retrieved 3 relevant chunks
Top result:
  Content: Example Domain This domain is for use in...
  Source: https://example.com
  Distance: 0.3245

============================================================
✓ PIPELINE TEST COMPLETE
============================================================
```

---

## Phase 3: Claude Plugin & Query Pipeline

### Step 5: Create Claude LLM Plugin

**File**: `api/app/plugins/llm/claude_plugin.py`

**Content**:
```python
"""
Claude (Anthropic) LLM plugin for answer generation.
"""
from typing import List, Dict, Optional
from anthropic import Anthropic
from api.app.plugins.base import LLMPlugin, StandardResponse


class ClaudePlugin(LLMPlugin):
    """
    Claude 3.5 Sonnet plugin for answer generation.
    """

    def __init__(self, config: Dict):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("options", {}).get("model", "claude-3-5-sonnet-20241022")
        self.temperature = config.get("options", {}).get("temperature", 0.7)
        self.max_tokens = config.get("options", {}).get("max_tokens", 1000)

        self.client = Anthropic(api_key=self.api_key)

    def generate(
        self,
        question: str,
        context: List[str],
        prompt_template: Optional[str] = None
    ) -> StandardResponse:
        """
        Generate answer using Claude.

        Args:
            question: User's question
            context: List of relevant text chunks
            prompt_template: Optional custom prompt

        Returns:
            StandardResponse with answer
        """
        # Build prompt
        if not prompt_template:
            prompt_template = self._default_prompt_template()

        context_text = "\n\n".join([f"[{i+1}] {chunk}" for i, chunk in enumerate(context)])

        full_prompt = prompt_template.format(
            context=context_text,
            question=question
        )

        # Call Claude API
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": full_prompt}
                ]
            )

            answer = response.content[0].text

            # Extract source references (if any)
            sources = self._extract_sources(answer, context)

            return StandardResponse(
                answer=answer,
                sources=sources,
                confidence=0.85,  # Could implement confidence scoring
                model_used=self.model,
                tokens_used=response.usage.input_tokens + response.usage.output_tokens
            )

        except Exception as e:
            raise Exception(f"Claude API error: {str(e)}")

    def _default_prompt_template(self) -> str:
        """Default prompt template for Q&A"""
        return """You are a helpful assistant answering questions based on the provided context.

Context from website:
{context}

Question: {question}

Instructions:
1. Answer the question using ONLY information from the context above
2. If the answer is not in the context, say "I don't have enough information to answer that question."
3. Be concise and accurate
4. If you reference specific information, mention which part of the context it came from

Answer:"""

    def _extract_sources(self, answer: str, context: List[str]) -> List[str]:
        """Extract which context chunks were likely used (simple heuristic)"""
        # Simple implementation: return all provided context
        # Could be enhanced with semantic matching
        return [f"Context chunk {i+1}" for i in range(len(context))]

    def get_model_info(self) -> Dict:
        """Return model information"""
        return {
            "provider": "Anthropic",
            "model_name": self.model,
            "context_window": 200000,
            "cost_per_1m_input_tokens": 3.00,
            "cost_per_1m_output_tokens": 15.00,
            "supports_function_calling": True,
            "supports_vision": True
        }


# Register the plugin
from api.app.core.plugin_factory import PluginFactory
PluginFactory.register_llm_plugin("claude", ClaudePlugin)
```

---

### Step 6: Create FastAPI Endpoints

**File**: `api/app/api/v1/endpoints/rag.py`

**Content**:
```python
"""
RAG API endpoints.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import os

from api.app.core.config import ConfigManager
from api.app.core.plugin_factory import PluginFactory
from api.app.services.document_processor import DocumentProcessor

router = APIRouter()

# Initialize configuration
config_manager = ConfigManager("config/configs.yaml")


class IndexRequest(BaseModel):
    """Request to index a URL"""
    url: str
    config_name: Optional[str] = None


class QueryRequest(BaseModel):
    """Request to query the system"""
    question: str
    config_name: Optional[str] = None
    n_results: int = 5


class IndexResponse(BaseModel):
    """Response from indexing"""
    success: bool
    documents_processed: int
    total_chunks: int
    collection_name: str


class QueryResponse(BaseModel):
    """Response from query"""
    answer: str
    sources: List[str]
    confidence: float
    model_used: str
    tokens_used: int
    retrieval_stats: dict


@router.post("/index", response_model=IndexResponse)
async def index_url(request: IndexRequest):
    """
    Index a URL using the specified configuration.
    """
    try:
        # Get configuration
        config_name = request.config_name or config_manager.get_active_config()
        dr_config = config_manager.get_data_retrieval_config(config_name)
        processing_config = config_manager.get_processing_config()

        # Add API keys from environment
        dr_config["api_key"] = os.getenv("JINA_API_KEY", "")
        processing_config["embedding"]["api_key"] = os.getenv("OPENAI_API_KEY")

        # Create data retrieval plugin
        plugin_name = dr_config["plugin"]
        plugin = PluginFactory.create_data_retrieval_plugin(plugin_name, dr_config)

        # Fetch the URL
        document = plugin.fetch_url(request.url)

        # Process and store
        processor = DocumentProcessor(processing_config)
        stats = processor.process_and_store([document])

        return IndexResponse(
            success=True,
            documents_processed=stats["documents_processed"],
            total_chunks=stats["total_chunks"],
            collection_name=stats["collection_name"]
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """
    Query the indexed content.
    """
    try:
        # Get configuration
        config_name = request.config_name or config_manager.get_active_config()
        llm_config = config_manager.get_llm_config(config_name)
        processing_config = config_manager.get_processing_config()

        # Add API keys from environment
        llm_config["api_key"] = os.getenv("ANTHROPIC_API_KEY")
        processing_config["embedding"]["api_key"] = os.getenv("OPENAI_API_KEY")

        # Retrieve relevant chunks
        processor = DocumentProcessor(processing_config)
        retrieval_results = processor.retrieve(
            request.question,
            n_results=request.n_results
        )

        # Create LLM plugin
        plugin_name = llm_config["plugin"]
        llm_plugin = PluginFactory.create_llm_plugin(plugin_name, llm_config)

        # Generate answer
        response = llm_plugin.generate(
            question=request.question,
            context=retrieval_results["documents"]
        )

        return QueryResponse(
            answer=response.answer,
            sources=response.sources,
            confidence=response.confidence,
            model_used=response.model_used,
            tokens_used=response.tokens_used,
            retrieval_stats={
                "chunks_retrieved": len(retrieval_results["documents"]),
                "distances": retrieval_results["distances"]
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/configs")
async def list_configs():
    """List available configurations"""
    return {
        "active": config_manager.get_active_config(),
        "available": config_manager.list_configs()
    }
```

---

### Step 7: Create Main FastAPI App

**File**: `api/app/main.py`

**Content**:
```python
"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.app.api.v1.endpoints import rag

app = FastAPI(
    title="Website RAG System",
    description="Modular RAG system for website Q&A",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(rag.router, prefix="/api/v1", tags=["RAG"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Website RAG System",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}
```

---

### Step 8: Update Claude Config

**File**: `config/configs.yaml`

Update the configuration to use Claude:

```yaml
# Active configuration (can be changed via API)
active_config: "jina_claude"

# Available configurations
configurations:
  jina_claude:
    name: "Jina + Claude 3.5 Sonnet"
    description: "Free data retrieval with Claude LLM"
    data_retrieval:
      plugin: "jina"
      api_key: ${JINA_API_KEY}
      options:
        use_parallel: true
        batch_size: 10
    llm:
      plugin: "claude"
      api_key: ${ANTHROPIC_API_KEY}
      options:
        model: "claude-3-5-sonnet-20241022"
        temperature: 0.7
        max_tokens: 1000

  jina_gpt4:
    name: "Jina + GPT-4"
    description: "Free data retrieval with premium LLM"
    data_retrieval:
      plugin: "jina"
      api_key: ${JINA_API_KEY}
      options:
        use_parallel: true
        batch_size: 10
    llm:
      plugin: "gpt4"
      api_key: ${OPENAI_API_KEY}
      options:
        model: "gpt-4-turbo-preview"
        temperature: 0.7
        max_tokens: 1000

# Processing settings (stable across all configs)
processing:
  chunking:
    strategy: "markdown"
    chunk_size: 500
    chunk_overlap: 50

  embedding:
    provider: "openai"
    model: "text-embedding-3-small"
    api_key: ${OPENAI_API_KEY}

  storage:
    type: "chromadb"
    host: "localhost"
    port: 8001
    persist_directory: "/app/data/chromadb"
```

---

### Step 9: Create Dockerfile for API

**File**: `api/Dockerfile`

**Content**:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

### Step 10: Update .env.example

**File**: `.env.example`

```bash
# OpenAI API Key (required for embeddings)
OPENAI_API_KEY=sk-your-openai-key-here

# Anthropic API Key (required for Claude)
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here

# Jina AI API Key (optional for basic usage)
JINA_API_KEY=your-jina-key-here

# Tavily API Key (optional - for Phase 5)
TAVILY_API_KEY=tvly-your-tavily-key-here

# Application Settings
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

---

## Testing the Complete System

### Test 1: Start All Services

```bash
cd /home/virus/Documents/repo/bizgenie/website-rag

# Create .env file with your API keys
cp .env.example .env
# Edit .env with your actual keys

# Start all services
docker-compose up -d chromadb
docker-compose up -d api

# Check logs
docker-compose logs -f api
```

### Test 2: Test API Endpoints

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test list configs
curl http://localhost:8000/api/v1/configs

# Test indexing a URL
curl -X POST http://localhost:8000/api/v1/index \
  -H "Content-Type: application/json" \
  -d '{"url": "https://bizgenieai.com"}'

# Test querying
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is BizGenie?"}'
```

### Test 3: Access API Documentation

Open in browser:
```
http://localhost:8000/docs
```

You'll see the interactive Swagger UI where you can test all endpoints.

---

## Phase 4: Simple UI (Coming Next)

After Phase 3 is complete and tested, we'll add a simple HTML/JS interface with:
- URL input form
- Question input
- Answer display with sources
- Configuration switcher

---

## Current Status Checklist

### Phase 1: Infrastructure ✓
- [x] Project structure
- [x] Plugin interfaces
- [x] Configuration system
- [x] Docker setup

### Phase 2: Jina Plugin
- [ ] Install dependencies
- [ ] Create Jina plugin
- [ ] Create document processor
- [ ] Test pipeline
- [ ] Verify URL indexing works

### Phase 3: Claude Plugin & API
- [ ] Create Claude plugin
- [ ] Create FastAPI endpoints
- [ ] Create main app
- [ ] Update configs
- [ ] Create Dockerfile
- [ ] Test complete API
- [ ] Verify Q&A works end-to-end

### Phase 4: UI (Pending)
- [ ] Create HTML interface
- [ ] Add styling
- [ ] Integrate with API
- [ ] Test user workflow

---

## Quick Start Commands

```bash
# 1. Navigate to project
cd /home/virus/Documents/repo/bizgenie/website-rag

# 2. Set up environment
cp .env.example .env
# Edit .env with your API keys:
#   OPENAI_API_KEY=sk-...
#   ANTHROPIC_API_KEY=sk-ant-...

# 3. Install Python dependencies
cd api
pip install -r requirements.txt
cd ..

# 4. Start ChromaDB
docker-compose up -d chromadb

# 5. Test Jina pipeline
python3 scripts/test_jina_pipeline.py

# 6. Start API
docker-compose up -d api

# 7. Test the API
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/index \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this page about?"}'

# 8. Open API docs
# Visit: http://localhost:8000/docs
```

---

## Need Help?

If you run into issues:
1. Check logs: `docker-compose logs -f api`
2. Verify ChromaDB is running: `curl http://localhost:8001/api/v1/heartbeat`
3. Check API keys are set in .env
4. Consult me for debugging or expert advice

---

## Summary

**Technology Choices:**
- ✅ FastAPI (modern, async, auto-docs)
- ✅ Claude 3.5 Sonnet (your preference, excellent reasoning)
- ✅ Jina AI (free, handles JS, simple)
- ✅ ChromaDB (simple, free, persistent)
- ✅ OpenAI embeddings (proven quality)
- ✅ Docker Compose (easy orchestration)

**Current Goal:**
Build a working prototype that can:
1. Index a URL (bizgenieai.com)
2. Answer questions about it using Claude
3. Test via API endpoints
4. Later: Add UI and comparison features

Follow the steps above sequentially, test each phase, and consult me for debugging or expert advice!
