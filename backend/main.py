"""
FastAPI Backend - Main Entry Point
AI Document Analyzer
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from api.routes import router as api_router
from ollama.client import OllamaClient


# Global state
class AppState:
    def __init__(self):
        self.ollama_client = None
        self.uploaded_files = {}  # file_id -> {name, content, metadata}
        self.analysis_results = {}  # session_id -> findings


state = AppState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    state.ollama_client = OllamaClient(base_url="http://localhost:11434")
    print("✓ Ollama client initialized")
    yield
    # Shutdown
    state.uploaded_files.clear()
    state.analysis_results.clear()
    print("✓ Application shutdown complete")


app = FastAPI(
    title="AI Document Analyzer",
    description="Document comparison and analysis using local Ollama AI",
    version="1.0.0",
    lifespan=lifespan
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure per environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix="/api", tags=["API"])


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    ollama_available = False
    try:
        if state.ollama_client:
            await state.ollama_client.list_models()
            ollama_available = True
    except Exception:
        pass
    
    return {
        "status": "healthy" if ollama_available else "degraded",
        "ollama": "connected" if ollama_available else "disconnected",
        "files_loaded": len(state.uploaded_files)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
