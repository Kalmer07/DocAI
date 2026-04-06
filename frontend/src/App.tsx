import React, { useState } from 'react';
import { useAppStore } from './hooks/useAppStore';
import { analyzeDocuments } from './services/documents';
import FileUploader from './components/FileUploader';
import ModelSelector from './components/ModelSelector';
import AnalysisResults from './components/AnalysisResults';
import ExportPanel from './components/ExportPanel';

function App() {
  const {
    files,
    selectedFileIds,
    ollamaConfig,
    sessionId,
    findings,
    isAnalyzing,
    setIsAnalyzing,
    setSessionId,
    setFindings,
    setSummary,
    resetAnalysis,
  } = useAppStore();

  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (selectedFileIds.length < 3) {
      setError('Выберите минимум 3 файла для анализа');
      return;
    }

    setError(null);
    setIsAnalyzing(true);
    resetAnalysis();

    try {
      const response = await analyzeDocuments({
        file_ids: selectedFileIds,
        ollama_config: ollamaConfig,
        analysis_types: ['duplicates', 'contradictions', 'overlaps', 'gaps'],
      });

      setSessionId(response.session_id);
      setFindings(response.findings);
      setSummary(response.summary);
    } catch (err) {
      console.error('Analysis failed:', err);
      setError(
        err instanceof Error ? err.message : 'Ошибка анализа. Проверьте подключение к Ollama.'
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleNewAnalysis = () => {
    resetAnalysis();
    setError(null);
  };

  return (
    <div className="app flex h-screen bg-slate-900">
      {/* Sidebar */}
      <aside className="w-80 bg-slate-800 border-r border-slate-700 flex flex-col">
        <div className="p-4 border-b border-slate-700">
          <h1 className="text-xl font-bold text-white">🤖 AI Document Analyzer</h1>
          <p className="text-xs text-slate-400 mt-1">
            Сравнение и анализ документов
          </p>
        </div>

        {/* Model Settings */}
        <ModelSelector />

        {/* File Upload */}
        <div className="flex-1 overflow-y-auto">
          <FileUploader />

          {/* File List */}
          {files.length > 0 && (
            <div className="p-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-semibold text-slate-300">
                  Файлы ({files.length})
                </h3>
                <button
                  onClick={handleNewAnalysis}
                  className="text-xs text-indigo-400 hover:text-indigo-300"
                >
                  Очистить
                </button>
              </div>

              <div className="space-y-2">
                {files.map((file) => (
                  <div
                    key={file.file_id}
                    className="flex items-center gap-2 p-2 bg-slate-700/50 rounded-lg"
                  >
                    <input
                      type="checkbox"
                      checked={selectedFileIds.includes(file.file_id)}
                      onChange={() => {}}
                      onClick={(e) => e.stopPropagation()}
                      className="checkbox-custom"
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm text-slate-200 truncate">
                        {file.filename}
                      </p>
                      <p className="text-xs text-slate-500">
                        {(file.size_bytes / 1024).toFixed(1)} KB
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-4 p-3 bg-indigo-900/30 border border-indigo-700/50 rounded-lg">
                <p className="text-xs text-indigo-300">
                  ✅ Выбрано:{' '}
                  <span className="font-medium">{selectedFileIds.length}</span> из{' '}
                  {files.length}
                </p>
                {selectedFileIds.length < 3 && (
                  <p className="text-xs text-red-400 mt-1">
                    ⚠️ Нужно минимум 3 файла
                  </p>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Analyze Button */}
        {files.length >= 3 && (
          <div className="p-4 border-t border-slate-700">
            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing || selectedFileIds.length < 3}
              className={`
                w-full py-3 rounded-xl font-medium transition-all
                ${isAnalyzing || selectedFileIds.length < 3
                  ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg hover:shadow-xl'}
              `}
            >
              {isAnalyzing ? (
                <span className="flex items-center justify-center gap-2">
                  <div className="spinner"></div>
                  Анализ...
                </span>
              ) : (
                '🔍 Запустить анализ'
              )}
            </button>
          </div>
        )}
      </aside>

      {/* Main Chat Area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="h-14 border-b border-slate-700 flex items-center px-6 bg-slate-800/50">
          <h2 className="text-lg font-medium text-slate-200">
            {sessionId ? 'Результаты анализа' : 'Загрузите документы для начала'}
          </h2>
        </header>

        {/* Content */}
        <div className="flex-1 overflow-y-auto">
          {error && (
            <div className="m-4 p-4 bg-red-900/30 border border-red-700/50 rounded-xl text-red-300">
              ❌ {error}
            </div>
          )}

          {!sessionId && !isAnalyzing && (
            <div className="h-full flex items-center justify-center text-slate-500">
              <div className="text-center max-w-md">
                <svg
                  className="w-20 h-20 mx-auto mb-4 opacity-50"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <p className="text-lg">
                  Загрузите 3-15 документов для сравнительного анализа
                </p>
                <p className="text-sm mt-2">
                  ИИ найдёт дубликаты, противоречия и пропущенные элементы
                </p>
              </div>
            </div>
          )}

          {sessionId && <AnalysisResults sessionId={sessionId} />}
        </div>

        {/* Export Panel */}
        {sessionId && findings.length > 0 && (
          <ExportPanel sessionId={sessionId} />
        )}
      </main>
    </div>
  );
}

export default App;
