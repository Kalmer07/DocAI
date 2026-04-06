"""
REST API Routes for Document Analysis
"""
import uuid
import time
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse

from api.models import (
    FileUploadResponse, AnalysisRequest, AnalysisResponse,
    ModelsResponse, ExportRequest, ExportResponse, FindingStatus
)
from parsers.factory import get_parser, parse_file_content
from ollama.prompts import build_comparison_prompt, ANALYSIS_SYSTEM_PROMPT
from analyzers.reporter import format_export


router = APIRouter()


def get_app_state():
    """Dependency to get application state"""
    from main import state
    return state


# ============== File Upload ==============

@router.post("/upload", response_model=List[FileUploadResponse])
async def upload_files(
    files: List[UploadFile] = File(...),
    state=Depends(get_app_state)
):
    """
    Upload multiple documents for analysis.
    Supports: PDF, DOCX, CSV, TXT, MD
    """
    results = []
    
    for file in files:
        file_id = str(uuid.uuid4())[:8]
        
        try:
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Parse based on extension
            extension = file.filename.split(".")[-1].lower() if file.filename else "txt"
            parsed_text = parse_file_content(content, extension)
            
            # Store in state
            state.uploaded_files[file_id] = {
                "filename": file.filename,
                "content": parsed_text,
                "size": file_size,
                "extension": extension
            }
            
            # Create preview (first 200 chars)
            preview = parsed_text[:200] + "..." if len(parsed_text) > 200 else parsed_text
            
            results.append(FileUploadResponse(
                file_id=file_id,
                filename=file.filename or "unknown",
                size_bytes=file_size,
                content_preview=preview,
                parsed_successfully=True
            ))
            
        except Exception as e:
            results.append(FileUploadResponse(
                file_id=file_id,
                filename=file.filename or "unknown",
                size_bytes=0,
                content_preview="",
                parsed_successfully=False,
                error_message=str(e)
            ))
    
    return results


# ============== Ollama Models ==============

@router.get("/models", response_model=ModelsResponse)
async def list_models(state=Depends(get_app_state)):
    """Get list of available Ollama models"""
    try:
        models = await state.ollama_client.list_models()
        return ModelsResponse(
            models=models,
            default_model="llama3.2"
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama not available: {str(e)}")


# ============== Analysis ==============

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_documents(
    request: AnalysisRequest,
    state=Depends(get_app_state)
):
    """
    Analyze uploaded documents using Ollama AI.
    Compares files, finds duplicates, contradictions, and gaps.
    """
    start_time = time.time()
    
    # Validate files exist
    for file_id in request.file_ids:
        if file_id not in state.uploaded_files:
            raise HTTPException(status_code=400, detail=f"File {file_id} not found")
    
    # Get file contents
    files_data = [
        {"id": fid, **state.uploaded_files[fid]}
        for fid in request.file_ids
    ]
    
    # Build prompt
    config = request.ollama_config or {}
    prompt = build_comparison_prompt(
        files=files_data,
        analysis_types=request.analysis_types,
        custom_instruction=request.custom_prompt
    )
    
    # Call Ollama
    try:
        ai_response = await state.ollama_client.generate(
            system_prompt=ANALYSIS_SYSTEM_PROMPT,
            user_prompt=prompt,
            config=config
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama error: {str(e)}")
    
    # Parse AI response to findings
    # (In production, use structured output/JSON mode)
    findings = parse_ai_response_to_findings(ai_response, files_data)
    
    # Calculate summary
    summary = calculate_summary(findings, len(files_data))
    
    processing_time = int((time.time() - start_time) * 1000)
    
    # Store results
    session_id = str(uuid.uuid4())
    state.analysis_results[session_id] = {
        "findings": findings,
        "raw_response": ai_response
    }
    
    return AnalysisResponse(
        session_id=session_id,
        findings=findings,
        summary=summary,
        raw_ai_response=ai_response,
        processing_time_ms=processing_time
    )


@router.post("/analysis/{session_id}/update-status")
async def update_finding_status(
    session_id: str,
    finding_id: str,
    status: FindingStatus,
    edited_content: str = None,
    state=Depends(get_app_state)
):
    """Update the status of a specific finding"""
    if session_id not in state.analysis_results:
        raise HTTPException(status_code=404, detail="Session not found")
    
    findings = state.analysis_results[session_id]["findings"]
    
    for finding in findings:
        if finding.id == finding_id:
            finding.status = status
            if edited_content:
                finding.edited_content = edited_content
            return {"success": True, "finding": finding}
    
    raise HTTPException(status_code=404, detail="Finding not found")


# ============== Export ==============

@router.post("/export", response_model=ExportResponse)
async def export_report(
    request: ExportRequest,
    session_id: str = None,
    findings: List = None,
    state=Depends(get_app_state)
):
    """
    Export analysis report in specified format.
    Can use session_id or provide findings directly.
    """
    # Get findings
    if session_id:
        if session_id not in state.analysis_results:
            raise HTTPException(status_code=404, detail="Session not found")
        all_findings = state.analysis_results[session_id]["findings"]
    elif findings:
        all_findings = findings
    else:
        raise HTTPException(status_code=400, detail="Provide session_id or findings")
    
    # Filter by status
    filtered_findings = []
    for f in all_findings:
        if f.status == FindingStatus.IGNORED:
            continue
        if not request.include_pending and f.status == FindingStatus.PENDING:
            continue
        if request.finding_ids and f.id not in request.finding_ids:
            continue
        filtered_findings.append(f)
    
    # Format export
    content, filename, content_type = format_export(
        findings=filtered_findings,
        format=request.format
    )
    
    return ExportResponse(
        content=content,
        filename=filename,
        content_type=content_type,
        byte_count=len(content.encode('utf-8'))
    )


# ============== Helper Functions ==============

def parse_ai_response_to_findings(ai_response: str, files_data: list) -> List:
    """
    Parse AI text response into structured findings.
    In production, use Ollama's JSON mode or function calling.
    """
    from api.models import Finding, FindingType, Severity
    import re
    
    findings = []
    
    # Simple parsing logic (improve with proper JSON extraction)
    # Expected AI output format:
    # ## Duplicates
    # - ID: dup_001 | Files: file1.txt, file2.txt | Text: "..."
    #
    # ## Contradictions
    # - ID: con_001 | Files: file1.txt, file3.txt | Issue: "..."
    
    lines = ai_response.split('\n')
    current_section = None
    
    for i, line in enumerate(lines):
        if '## Duplicates' in line or '## Дубликаты' in line:
            current_section = FindingType.DUPLICATE
        elif '## Contradictions' in line or '## Противоречия' in line:
            current_section = FindingType.CONTRADICTION
        elif '## Missing' in line or '## Пропущено' in line:
            current_section = FindingType.MISSING
        
        if current_section and line.strip().startswith('-'):
            # Extract finding data
            finding_id = f"f_{uuid.uuid4().hex[:6]}"
            
            findings.append(Finding(
                id=finding_id,
                type=current_section,
                severity=Severity.MEDIUM,  # AI should specify this
                title=line.strip()[:100],
                description=line.strip(),
                files_involved=[f["filename"] for f in files_data[:2]],
                suggestion="Review and consolidate",
                confidence_score=0.8
            ))
    
    return findings


def calculate_summary(findings: List, files_count: int) -> "AnalysisSummary":
    """Calculate summary statistics"""
    from api.models import AnalysisSummary
    
    by_type = {}
    by_severity = {}
    by_status = {}
    
    for f in findings:
        by_type[f.type.value] = by_type.get(f.type.value, 0) + 1
        by_severity[f.severity.value] = by_severity.get(f.severity.value, 0) + 1
        by_status[f.status.value] = by_status.get(f.status.value, 0) + 1
    
    return AnalysisSummary(
        total_findings=len(findings),
        by_type=by_type,
        by_severity=by_severity,
        by_status=by_status,
        files_analyzed=files_count
    )
