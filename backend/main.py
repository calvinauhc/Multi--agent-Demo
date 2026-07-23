import os
import uvicorn
from fastapi import FastAPI, Query, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from typing import Optional

from backend.agents import MultiAgentOrchestrator

app = FastAPI(title="Multi-Agent Estate Research & Writer API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex="https?://.*",  # Supports credentials (cookies) on wildcard subdomain proxies
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {
        "title": "Agentic Property Market Research API",
        "version": "2.1",
        "status": "healthy",
        "endpoints": {
            "root": "/",
            "health": "/health",
            "generate": "/api/generate?query=<topic>&provider=<mock/openai/anthropic/gemini>"
        },
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Multi-agent backend is healthy!"}

@app.get("/api/generate")
async def generate_property_content(
    query: str = Query(..., description="The real estate/property query to research"),
    tone: str = Query("professional", description="The tone of the generated Instagram post"),
    provider: str = Query("mock", description="LLM provider: 'mock', 'openai', 'anthropic', 'gemini'"),
    api_key: Optional[str] = Query(None, description="Optional LLM API Key. If not provided, uses backend .env key")
):
    """
    Server-Sent Events (SSE) endpoint to stream multi-agent execution steps
    and final content outputs.
    """
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # If key is omitted in query params, check custom authorization header or environment variables
    effective_api_key = api_key
    if not effective_api_key and provider != "mock":
        effective_api_key = os.getenv("LLM_API_KEY")

    # If the user selects a real provider but has no key, raise an error early so the UI knows
    if provider != "mock" and not effective_api_key:
        # We can yield a mock error, but raising an HTTP exception is cleaner.
        raise HTTPException(
            status_code=400,
            detail=f"API Key is required for provider '{provider}'. Please enter a key in the settings panel."
        )

    # Initialize the orchestrator
    orchestrator = MultiAgentOrchestrator(
        query=query,
        tone=tone,
        api_key=effective_api_key,
        provider=provider
    )

    # Return the real-time event generator stream
    return EventSourceResponse(orchestrator.run())

if __name__ == "__main__":
    # Run uvicorn server on port 8000
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
