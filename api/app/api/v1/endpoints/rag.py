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
