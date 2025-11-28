"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # Added
from fastapi.responses import HTMLResponse # Added
from api.app.api.v1.endpoints import rag
from api.app.core.logging import setup_logging

# Initialize logging
logger = setup_logging()

# Import plugins to register them
from api.app.plugins.data_retrieval import jina_plugin, tavily_plugin
from api.app.plugins.llm import claude_plugin

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

# Serve static files for the UI
app.mount("/ui", StaticFiles(directory="ui"), name="ui") # Added

@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("ui/index.html", "r") as f:
        return f.read()

@app.get("/health")
async def health():
    """Health check endpoint"""
    logger.debug("Health check called")
    return {"status": "healthy"}