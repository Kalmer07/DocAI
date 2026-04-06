# Архитектурная схема AI Document Analyzer

## Общая архитектура

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND (React + TS)                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐ │
│  │ FileUploader │  │ModelSelector │  │ChatInterface │  │ExportPanel  │ │
│  │   Component  │  │   Component  │  │   Component  │  │  Component  │ │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬──────┘ │
│         │                 │                 │                 │        │
│  ┌──────▼─────────────────▼─────────────────▼─────────────────▼──────┐ │
│  │                     React Hooks Layer                              │ │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────────┐                │ │
│  │  │ useFiles   │  │ useOllama   │  │ useAnalysis  │                │ │
│  │  └────────────┘  └─────────────┘  └──────────────┘                │ │
│  └───────────────────────────────────────────────────────────────────┘ │
│         │                 │                 │                          │
│  ┌──────▼─────────────────▼─────────────────▼──────────────────────┐   │
│  │                      API Services                                │   │
│  │  ┌────────────┐  ┌─────────────┐  ┌──────────────┐              │   │
│  │  │documents.ts│  │ ollama.ts   │  │ api.ts       │              │   │
│  │  └────────────┘  └─────────────┘  └──────────────┘              │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ HTTP/REST
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (FastAPI)                               │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      API Routes                                    │  │
│  │  /upload    → POST   → Загрузка файлов                            │  │
│  │  /analyze   → POST   → Запуск анализа                             │  │
│  │  /models    → GET    → Список моделей Ollama                      │  │
│  │  /export    → POST   → Экспорт отчёта                             │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│         │                 │                 │                           │
│  ┌──────▼───────┐ ┌───────▼──────┐ ┌───────▼────────┐                  │
│  │   Parsers    │ │  Analyzers   │ │   Ollama       │                  │
│  │   Module     │ │   Module     │ │   Client       │                  │
│  │              │ │              │ │                │                  │
│  │ ┌──────────┐ │ │ ┌──────────┐ │ │ ┌────────────┐ │                  │
│  │ │PDFParser │ │ │ │Comparator│ │ │ │OllamaAPI   │ │                  │
│  │ │DOCXParser│ │ │ │Reporter  │ │ │ │PromptMgr   │ │                  │
│  │ │CSVParser │ │ │ └──────────┘ │ │ └────────────┘ │                  │
│  │ │TXTParser │ │ │              │ │                │                  │
│  │ └──────────┘ │ │              │ │                │                  │
│  └──────────────┘ └──────────────┘ └────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │ HTTP/REST (localhost:11434)
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         OLLAMA (Local AI)                               │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                    Available Models                                │  │
│  │  - llama3.2      - mistral      - qwen2.5                         │  │
│  │  - codellama     - gemma2       - custom models                   │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                   Generation Engine                                │  │
│  │  Context Window Management | Temperature Control | Streaming      │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Поток данных

### 1. Загрузка файлов
```
User → [FileUploader] → FormData → POST /api/upload → [Parser Factory]
                                               ↓
                                    [Text Normalization]
                                               ↓
                                    [Store in Memory/DB]
                                               ↓
                                    Response: {fileId, preview, stats}
```

### 2. Настройка Ollama
```
User → [ModelSelector] → Config: {model, temp, context_size}
                                     ↓
                              GET /api/models (refresh)
                                     ↓
                              Store in Frontend State
```

### 3. Анализ документов
```
User → [Click Analyze] → POST /api/analyze
                                   ↓
                    [Retrieve Files + Config]
                                   ↓
                    [Build Comparison Prompt]
                                   ↓
                    [Call Ollama API] ←── Streaming Response
                                   ↓
                    [Parse AI Response to JSON]
                                   ↓
                    [Generate Findings with IDs]
                                   ↓
                    Response: {findings[], summary}
```

### 4. Интерактивная работа с результатами
```
[AnalysisResults] → Render Findings with Checkboxes
        ↓
User toggles: [✓] Accept  [ ] Ignore  [✎] Edit
        ↓
[Local State Update] → Real-time UI refresh
        ↓
[Export Panel] → Filter by status → Generate Report
```

### 5. Экспорт отчёта
```
User → [Select Format: MD/JSON/TXT] → POST /api/export
                                                ↓
                                  [Filter Findings by Status]
                                                ↓
                                  [Format Template Engine]
                                                ↓
                                  Response: File Download
```

## Компонентные взаимодействия

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend State Flow                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  files[] ──► useFiles ──► upload() ──► API ──► updateState  │
│                                                              │
│  ollamaConfig ──► useOllama ──► fetchModels() ──► setState  │
│                      │                                       │
│                      └─► setParams(model, temp, ctx)        │
│                                                              │
│  analysisState ──► useAnalysis ──► runAnalysis()            │
│                      │                                       │
│                      ├─► findings[]                          │
│                      ├─► selectedIds[]                       │
│                      ├─► editedItems{}                       │
│                      └─► export(format)                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Модульная структура бэкенда

```
backend/
│
├── main.py (FastAPI app)
│   └── Mounts:
│       ├── /api/docs → API routes
│       ├── /static → Uploaded files
│       └── CORS → Frontend origin
│
├── api/
│   ├── routes.py
│   │   ├── @router.post("/upload")
│   │   ├── @router.post("/analyze")
│   │   ├── @router.get("/models")
│   │   └── @router.post("/export")
│   │
│   └── models.py (Pydantic)
│       ├── FileUploadResponse
│       ├── AnalysisRequest
│       ├── AnalysisResponse
│       ├── Finding
│       └── ExportRequest
│
├── parsers/
│   ├── base.py (ABC Parser)
│   │   └── parse(file) → str
│   │
│   ├── factory.py
│   │   └── get_parser(extension) → Parser
│   │
│   └── {pdf,docx,csv,txt}_parser.py
│
├── ollama/
│   ├── client.py
│   │   ├── OllamaClient class
│   │   │   ├── __init__(base_url)
│   │   │   ├── list_models() → List[str]
│   │   │   └── generate(prompt, config) → StreamingResponse
│   │   │
│   │   └── handle_streaming()
│   │
│   └── prompts.py
│       ├── build_comparison_prompt(files, config)
│       ├── FIND_DUPLICATES_PROMPT
│       ├── FIND_CONTRADICTIONS_PROMPT
│       └── GENERATE_REPORT_PROMPT
│
└── analyzers/
    ├── comparator.py
    │   ├── compare_files(files) → raw_findings
    │   └── chunk_for_context(files, max_tokens)
    │
    └── reporter.py
        ├── format_markdown(findings)
        ├── format_json(findings)
        └── apply_filters(findings, status_filter)
```

## Состояние чекбоксов и сохранение

```
Frontend State Structure:
{
  findings: [
    {
      id: "f_001",
      type: "duplicate" | "contradiction" | "missing",
      severity: "high" | "medium" | "low",
      description: string,
      filesInvolved: ["file1.txt", "file2.txt"],
      suggestion: string,
      status: "pending" | "accepted" | "ignored" | "edited",
      editedContent?: string
    }
  ],
  
  // Persisted in localStorage or backend session
  userActions: {
    acceptedIds: ["f_001", "f_003"],
    ignoredIds: ["f_002"],
    edits: {
      "f_004": "Custom edit text..."
    }
  }
}
```

## Генерация финального отчёта

```
Exporter Pipeline:

1. Filter Findings
   └─► Exclude status="ignored"
   └─► Include status="accepted" + status="edited"

2. Apply Template
   │
   ├─► Markdown Template:
   │   # Analysis Report
   │   ## Summary
   │   ## High Priority Items
   │   ## Medium Priority Items
   │   ## Low Priority Items
   │
   ├─► JSON Template:
   │   {
   │     "metadata": {...},
   │     "findings": [...],
   │     "statistics": {...}
   │   }
   │
   └─► Text Template:
       Plain text with indentation

3. Post-process
   └─► Add timestamps
   └─► Add file references
   └─► Calculate statistics

4. Return as downloadable file
```
