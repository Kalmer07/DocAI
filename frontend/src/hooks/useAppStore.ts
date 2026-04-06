/**
 * Zustand Store for Application State
 * Manages files, Ollama config, and analysis results
 */
import { create } from 'zustand';
import { UploadedFile, Finding, OllamaConfig, AnalysisSummary } from '../services/documents';

interface AnalysisState {
  // Files
  files: UploadedFile[];
  selectedFileIds: string[];
  
  // Ollama Configuration
  ollamaConfig: OllamaConfig;
  availableModels: string[];
  
  // Analysis Results
  sessionId: string | null;
  findings: Finding[];
  summary: AnalysisSummary | null;
  isAnalyzing: boolean;
  
  // User Actions on Findings
  acceptedIds: Set<string>;
  ignoredIds: Set<string>;
  editedItems: Record<string, string>;
  
  // Actions
  addFiles: (files: UploadedFile[]) => void;
  removeFile: (fileId: string) => void;
  toggleFileSelection: (fileId: string) => void;
  clearFiles: () => void;
  
  setOllamaConfig: (config: Partial<OllamaConfig>) => void;
  setAvailableModels: (models: string[]) => void;
  
  setSessionId: (sessionId: string | null) => void;
  setFindings: (findings: Finding[]) => void;
  setSummary: (summary: AnalysisSummary | null) => void;
  setIsAnalyzing: (isAnalyzing: boolean) => void;
  
  toggleAccepted: (findingId: string) => void;
  toggleIgnored: (findingId: string) => void;
  setEditedContent: (findingId: string, content: string) => void;
  resetAnalysis: () => void;
}

export const useAppStore = create<AnalysisState>((set, get) => ({
  // Initial State
  files: [],
  selectedFileIds: [],
  ollamaConfig: {
    model: 'llama3.2',
    temperature: 0.3,
    context_size: 4096,
    top_p: 0.9,
  },
  availableModels: [],
  sessionId: null,
  findings: [],
  summary: null,
  isAnalyzing: false,
  acceptedIds: new Set(),
  ignoredIds: new Set(),
  editedItems: {},
  
  // File Actions
  addFiles: (files) => {
    set((state) => ({
      files: [...state.files, ...files],
      selectedFileIds: [
        ...state.selectedFileIds,
        ...files.map((f) => f.file_id),
      ],
    }));
  },
  
  removeFile: (fileId) => {
    set((state) => ({
      files: state.files.filter((f) => f.file_id !== fileId),
      selectedFileIds: state.selectedFileIds.filter((id) => id !== fileId),
    }));
  },
  
  toggleFileSelection: (fileId) => {
    set((state) => ({
      selectedFileIds: state.selectedFileIds.includes(fileId)
        ? state.selectedFileIds.filter((id) => id !== fileId)
        : [...state.selectedFileIds, fileId],
    }));
  },
  
  clearFiles: () => {
    set({
      files: [],
      selectedFileIds: [],
    });
  },
  
  // Ollama Config Actions
  setOllamaConfig: (config) => {
    set((state) => ({
      ollamaConfig: { ...state.ollamaConfig, ...config },
    }));
  },
  
  setAvailableModels: (models) => {
    set({ availableModels: models });
  },
  
  // Analysis Actions
  setSessionId: (sessionId) => {
    set({ sessionId });
  },
  
  setFindings: (findings) => {
    set({ findings });
  },
  
  setSummary: (summary) => {
    set({ summary });
  },
  
  setIsAnalyzing: (isAnalyzing) => {
    set({ isAnalyzing });
  },
  
  // Finding Status Actions
  toggleAccepted: (findingId) => {
    set((state) => {
      const newAccepted = new Set(state.acceptedIds);
      const newIgnored = new Set(state.ignoredIds);
      
      if (newAccepted.has(findingId)) {
        newAccepted.delete(findingId);
      } else {
        newAccepted.add(findingId);
        newIgnored.delete(findingId);
      }
      
      return {
        acceptedIds: newAccepted,
        ignoredIds: newIgnored,
      };
    });
  },
  
  toggleIgnored: (findingId) => {
    set((state) => {
      const newIgnored = new Set(state.ignoredIds);
      const newAccepted = new Set(state.acceptedIds);
      
      if (newIgnored.has(findingId)) {
        newIgnored.delete(findingId);
      } else {
        newIgnored.add(findingId);
        newAccepted.delete(findingId);
      }
      
      return {
        ignoredIds: newIgnored,
        acceptedIds: newAccepted,
      };
    });
  },
  
  setEditedContent: (findingId, content) => {
    set((state) => ({
      editedItems: { ...state.editedItems, [findingId]: content },
    }));
  },
  
  resetAnalysis: () => {
    set({
      sessionId: null,
      findings: [],
      summary: null,
      acceptedIds: new Set(),
      ignoredIds: new Set(),
      editedItems: {},
    });
  },
}));

// Helper to get finding status
export const getFindingStatus = (
  findingId: string,
  acceptedIds: Set<string>,
  ignoredIds: Set<string>,
  editedItems: Record<string, string>
): 'pending' | 'accepted' | 'ignored' | 'edited' => {
  if (editedItems[findingId]) return 'edited';
  if (acceptedIds.has(findingId)) return 'accepted';
  if (ignoredIds.has(findingId)) return 'ignored';
  return 'pending';
};
