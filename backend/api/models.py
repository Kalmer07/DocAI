"""
Pydantic Models for API Request/Response
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime
from enum import Enum


class FindingType(str, Enum):
    DUPLICATE = "duplicate"
    CONTRADICTION = "contradiction"
    MISSING = "missing"
    OVERLAP = "overlap"
    SUGGESTION = "suggestion"


class Severity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class FindingStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    IGNORED = "ignored"
    EDITED = "edited"


# ============== Request Models ==============

class OllamaConfig(BaseModel):
    """Configuration for Ollama model"""
    model: str = Field(default="llama3.2", description="Model name")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Temperature for generation")
    context_size: int = Field(default=4096, ge=512, le=32768, description="Context window size")
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    seed: Optional[int] = None


class AnalysisRequest(BaseModel):
    """Request to analyze uploaded documents"""
    file_ids: List[str] = Field(..., min_length=3, description="IDs of files to analyze")
    ollama_config: Optional[OllamaConfig] = None
    analysis_types: List[str] = Field(
        default=["duplicates", "contradictions", "overlaps"],
        description="Types of analysis to perform"
    )
    custom_prompt: Optional[str] = None


class ExportRequest(BaseModel):
    """Request to export analysis results"""
    format: Literal["markdown", "json", "text"] = "markdown"
    include_pending: bool = False
    finding_ids: Optional[List[str]] = None  # If None, export all non-ignored


# ============== Response Models ==============

class FileUploadResponse(BaseModel):
    """Response after file upload"""
    file_id: str
    filename: str
    size_bytes: int
    content_preview: str
    parsed_successfully: bool
    error_message: Optional[str] = None


class Finding(BaseModel):
    """Single analysis finding"""
    id: str = Field(..., description="Unique finding identifier")
    type: FindingType
    severity: Severity
    title: str
    description: str
    files_involved: List[str]
    suggestion: str
    status: FindingStatus = FindingStatus.PENDING
    edited_content: Optional[str] = None
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisSummary(BaseModel):
    """Summary statistics of analysis"""
    total_findings: int
    by_type: Dict[str, int]
    by_severity: Dict[str, int]
    by_status: Dict[str, int]
    files_analyzed: int


class AnalysisResponse(BaseModel):
    """Response with analysis results"""
    session_id: str
    findings: List[Finding]
    summary: AnalysisSummary
    raw_ai_response: Optional[str] = None
    processing_time_ms: int


class ModelInfo(BaseModel):
    """Information about an Ollama model"""
    name: str
    size: str
    family: str
    modified_at: datetime


class ModelsResponse(BaseModel):
    """List of available Ollama models"""
    models: List[ModelInfo]
    default_model: str = "llama3.2"


class ExportResponse(BaseModel):
    """Export result"""
    content: str
    filename: str
    content_type: str
    byte_count: int


# ============== WebSocket Messages ==============

class WSMessage(BaseModel):
    """WebSocket message structure"""
    type: Literal["progress", "finding", "complete", "error"]
    data: Dict
    timestamp: datetime = Field(default_factory=datetime.utcnow)
