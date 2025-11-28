from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import importlib
from api.app.core.config import ConfigManager
from api.app.core.logging import get_logger
from api.app.core.memory import ChatMemory
from api.app.core.prompts import PromptManager

router = APIRouter()
logger = get_logger("rag_endpoint")
config_manager = ConfigManager("config/configs.yaml")
chat_memory = ChatMemory()

class QueryRequest(BaseModel):
    question: str
    mcp_tool: str      # e.g., "tavily", "jina"
    llm_model: str     # e.g., "claude", "gpt4"
    target_url: Optional[str] = None # e.g., "https://bizgenieai.com/"
    session_id: str    # UUID for the conversation

class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    metrics: Dict[str, Any]

@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """Execute query with selected MCP tool + LLM"""
    logger.info(f"Received query: {request.question} [Session: {request.session_id}, Tool: {request.mcp_tool}, Model: {request.llm_model}, Target: {request.target_url}]")

    try:
        # 1. Get Configurations
        mcp_config = config_manager.get_mcp_tool_config(request.mcp_tool)
        llm_config = config_manager.get_llm_model_config(request.llm_model)

        # 2. Load MCP Tool
        logger.info(f"Loading MCP tool: {mcp_config['class']}")
        mcp_module = importlib.import_module(mcp_config["module"])
        mcp_class = getattr(mcp_module, mcp_config["class"])
        mcp_tool = mcp_class(mcp_config)

        # 3. Execute Search (with target_url as context)
        logger.info("Executing search...")
        search_result = mcp_tool.search(request.question, context=request.target_url)
        logger.info(f"Search complete. Found {len(search_result.sources)} sources in {search_result.search_time:.2f}s")

        # 4. Load LLM
        logger.info(f"Loading LLM: {llm_config['class']}")
        llm_module = importlib.import_module(llm_config["module"])
        llm_class = getattr(llm_module, llm_config["class"])
        llm = llm_class(llm_config)

        # 5. Construct System Prompt (Using centralized PromptManager)
        system_prompt = PromptManager.get_system_prompt(request.target_url)

        # 6. Retrieve History & Generate Answer
        logger.info("Retrieving chat history...")
        history = chat_memory.get_history(request.session_id, limit=6) # Get last 6 messages
        
        # Append current user question (content is enriched later by LLM class if needed, or we do it here)
        # For the LLM class to use our standard template, we should actually pass the TEMPLATED question here
        # BUT, our LLM classes currently do their own formatting. 
        # To be truly clean, LLM classes should be dumb pipes and we handle prompting here?
        # OR we update LLM classes to use PromptManager too.
        # Let's update LLM classes to use PromptManager.
        # FOR NOW: We pass the raw question, and let the LLM class use the PromptManager.
        
        history.append({"role": "user", "content": request.question})

        logger.info(f"Generating answer with context of {len(history)-1} previous messages...")
        
        llm_response = llm.generate(
            messages=history,
            context=search_result.content,
            system_prompt=system_prompt
        )
        logger.info(f"Generation complete in {llm_response.generation_time:.2f}s")

        # 7. Save to Memory
        logger.info("Saving turn to memory...")
        chat_memory.add_message(request.session_id, "user", request.question)
        chat_memory.add_message(request.session_id, "assistant", llm_response.answer)

        # 8. Return Response
        return QueryResponse(
            answer=llm_response.answer,
            sources=search_result.sources,
            metrics={
                "mcp_tool": request.mcp_tool,
                "mcp_search_time": search_result.search_time,
                "mcp_cost": search_result.search_cost,
                "llm_model": request.llm_model,
                "llm_time": llm_response.generation_time,
                "llm_cost": llm_response.generation_cost,
                "llm_tokens": llm_response.tokens_used,
                "total_time": search_result.search_time + llm_response.generation_time,
                "total_cost": search_result.search_cost + llm_response.generation_cost
            }
        )

    except Exception as e:
        logger.error(f"Query processing failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/components")
async def get_components():
    """Get available MCP tools and LLMs for UI dropdowns"""
    components = config_manager.list_components()
    
    return {
        "mcp_tools": [
            {"id": key, "name": value["name"]}
            for key, value in components["mcp_tools"].items()
        ],
        "llm_models": [
            {"id": key, "name": value["name"]}
            for key, value in components["llm_models"].items()
        ]
    }