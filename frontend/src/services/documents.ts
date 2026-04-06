/**
 * Document Service - File upload and management
 */
import api from './api';

export interface UploadedFile {
  file_id: string;
  filename: string;
  size_bytes: number;
  content_preview: string;
  parsed_successfully: boolean;
  error_message?: string;
}

export interface OllamaConfig {
  model: string;
  temperature: number;
  context_size: number;
  top_p: number;
  seed?: number;
}

export interface AnalysisRequest {
  file_ids: string[];
  ollama_config?: OllamaConfig;
  analysis_types?: string[];
  custom_prompt?: string;
}

export interface Finding {
  id: string;
  type: 'duplicate' | 'contradiction' | 'missing' | 'overlap' | 'suggestion';
  severity: 'high' | 'medium' | 'low';
  title: string;
  description: string;
  files_involved: string[];
  suggestion: string;
  status: 'pending' | 'accepted' | 'ignored' | 'edited';
  edited_content?: string;
  confidence_score: number;
  created_at: string;
}

export interface AnalysisSummary {
  total_findings: number;
  by_type: Record<string, number>;
  by_severity: Record<string, number>;
  by_status: Record<string, number>;
  files_analyzed: number;
}

export interface AnalysisResponse {
  session_id: string;
  findings: Finding[];
  summary: AnalysisSummary;
  raw_ai_response?: string;
  processing_time_ms: number;
}

export interface ModelInfo {
  name: string;
  size: string;
  family: string;
  modified_at: string;
}

export interface ModelsResponse {
  models: ModelInfo[];
  default_model: string;
}

/**
 * Upload multiple files for analysis
 */
export const uploadFiles = async (files: File[]): Promise<UploadedFile[]> => {
  const formData = new FormData();
  files.forEach((file) => formData.append('files', file));

  const response = await api.post<UploadedFile[]>('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};

/**
 * Get available Ollama models
 */
export const getModels = async (): Promise<ModelsResponse> => {
  const response = await api.get<ModelsResponse>('/models');
  return response.data;
};

/**
 * Run document analysis
 */
export const analyzeDocuments = async (
  request: AnalysisRequest
): Promise<AnalysisResponse> => {
  const response = await api.post<AnalysisResponse>('/analyze', request);
  return response.data;
};

/**
 * Update finding status
 */
export const updateFindingStatus = async (
  sessionId: string,
  findingId: string,
  status: Finding['status'],
  editedContent?: string
): Promise<{ success: boolean; finding: Finding }> => {
  const response = await api.post(
    `/analysis/${sessionId}/update-status`,
    null,
    {
      params: { finding_id: findingId, status, edited_content: editedContent },
    }
  );
  return response.data;
};

/**
 * Export analysis report
 */
export interface ExportRequest {
  format: 'markdown' | 'json' | 'text';
  include_pending?: boolean;
  finding_ids?: string[];
}

export const exportReport = async (
  sessionId: string,
  request: ExportRequest
): Promise<{ content: string; filename: string; content_type: string }> => {
  const response = await api.post('/export', request, {
    params: { session_id: sessionId },
  });
  return response.data;
};

/**
 * Download exported report as file
 */
export const downloadReport = async (
  sessionId: string,
  format: string
): Promise<void> => {
  const response = await api.post(
    '/export',
    { format },
    {
      params: { session_id: sessionId },
      responseType: 'blob',
    }
  );

  const blob = new Blob([response.data], {
    type: response.headers['content-type'],
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `analysis_report.${format === 'markdown' ? 'md' : format}`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
