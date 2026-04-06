"""
Ollama Models and Configuration
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ModelInfo(BaseModel):
    """Information about an Ollama model"""
    name: str
    size: str
    family: str
    modified_at: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "llama3.2:latest",
                "size": "2.0GB",
                "family": "llama",
                "modified_at": "2024-01-15T10:30:00Z"
            }
        }


class OllamaGenerationConfig(BaseModel):
    """Configuration for text generation"""
    model: str = Field(default="llama3.2", description="Model to use")
    temperature: float = Field(
        default=0.3,
        ge=0.0,
        le=2.0,
        description="Controls randomness. Lower = more deterministic"
    )
    top_p: float = Field(
        default=0.9,
        ge=0.0,
        le=1.0,
        description="Nucleus sampling parameter"
    )
    context_size: int = Field(
        default=4096,
        ge=512,
        le=131072,
        description="Context window size in tokens"
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed for reproducibility"
    )
    num_predict: int = Field(
        default=2048,
        ge=1,
        le=32768,
        description="Maximum tokens to generate"
    )
    
    def to_ollama_options(self) -> dict:
        """Convert to Ollama API options format"""
        return {
            "temperature": self.temperature,
            "top_p": self.top_p,
            "num_ctx": self.context_size,
            "num_predict": self.num_predict,
        }
