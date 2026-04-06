import React, { useState } from 'react';
import { useAppStore } from '../hooks/useAppStore';
import { downloadReport } from '../services/documents';

interface ExportPanelProps {
  sessionId: string;
}

export const ExportPanel: React.FC<ExportPanelProps> = ({ sessionId }) => {
  const [isExporting, setIsExporting] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState<'markdown' | 'json' | 'text'>('markdown');
  
  const { acceptedIds, ignoredIds, findings } = useAppStore();

  const handleExport = async () => {
    setIsExporting(true);
    try {
      await downloadReport(sessionId, selectedFormat);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Ошибка экспорта');
    } finally {
      setIsExporting(false);
    }
  };

  // Calculate what will be exported
  const exportableCount = findings.filter((f) => {
    if (ignoredIds.has(f.id)) return false;
    return true;
  }).length;

  return (
    <div className="export-panel p-4 border-t border-slate-700">
      <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider mb-3">
        Экспорт отчёта
      </h3>

      {/* Format Selection */}
      <div className="flex gap-2 mb-4">
        {(['markdown', 'json', 'text'] as const).map((format) => (
          <button
            key={format}
            onClick={() => setSelectedFormat(format)}
            className={`
              flex-1 px-3 py-2 rounded-lg text-sm font-medium transition-colors
              ${selectedFormat === format
                ? 'bg-indigo-600 text-white'
                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}
            `}
          >
            {format === 'markdown' && '📝 MD'}
            {format === 'json' && '📄 JSON'}
            {format === 'text' && '📃 TXT'}
          </button>
        ))}
      </div>

      {/* Export Info */}
      <div className="mb-4 p-3 bg-slate-800/50 rounded-lg">
        <p className="text-xs text-slate-400">
          Будет экспортировано:{' '}
          <span className="text-slate-200 font-medium">{exportableCount}</span> находок
        </p>
        <p className="text-xs text-slate-500 mt-1">
          (игнорируемые пункты не включаются)
        </p>
      </div>

      {/* Export Button */}
      <button
        onClick={handleExport}
        disabled={isExporting || exportableCount === 0}
        className={`
          w-full py-3 rounded-xl font-medium transition-all
          ${isExporting || exportableCount === 0
            ? 'bg-slate-700 text-slate-500 cursor-not-allowed'
            : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 text-white shadow-lg hover:shadow-xl'}
        `}
      >
        {isExporting ? (
          <span className="flex items-center justify-center gap-2">
            <div className="spinner w-5 h-5"></div>
            Экспорт...
          </span>
        ) : (
          <span className="flex items-center justify-center gap-2">
            ⬇️ Скачать отчёт
          </span>
        )}
      </button>
    </div>
  );
};

export default ExportPanel;
