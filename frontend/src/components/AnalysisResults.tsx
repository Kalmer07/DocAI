import React, { useState } from 'react';
import { Finding } from '../services/documents';
import { useAppStore, getFindingStatus } from '../hooks/useAppStore';

interface AnalysisResultsProps {
  sessionId: string;
}

export const AnalysisResults: React.FC<AnalysisResultsProps> = ({ sessionId }) => {
  const {
    findings,
    summary,
    acceptedIds,
    ignoredIds,
    editedItems,
    toggleAccepted,
    toggleIgnored,
    setEditedContent,
  } = useAppStore();

  const [expandedFinding, setExpandedFinding] = useState<string | null>(null);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');

  const getTypeIcon = (type: Finding['type']) => {
    const icons = {
      duplicate: '🔄',
      contradiction: '⚠️',
      missing: '📭',
      overlap: '🔀',
      suggestion: '💡',
    };
    return icons[type] || '📌';
  };

  const getSeverityClass = (severity: Finding['severity']) => {
    return `finding-${severity}`;
  };

  const getStatusBadge = (finding: Finding) => {
    const status = getFindingStatus(
      finding.id,
      acceptedIds,
      ignoredIds,
      editedItems
    );

    const badges = {
      pending: { text: 'Ожидает', class: 'bg-slate-600' },
      accepted: { text: 'Принято', class: 'bg-green-600' },
      ignored: { text: 'Игнор.', class: 'bg-red-600' },
      edited: { text: 'Изменено', class: 'bg-yellow-600' },
    };

    const badge = badges[status];
    return (
      <span className={`px-2 py-0.5 rounded text-xs ${badge.class}`}>
        {badge.text}
      </span>
    );
  };

  const handleEdit = (finding: Finding) => {
    setEditingId(finding.id);
    setEditText(editedItems[finding.id] || finding.suggestion);
  };

  const handleSaveEdit = (findingId: string) => {
    setEditedContent(findingId, editText);
    setEditingId(null);
  };

  const handleCancelEdit = () => {
    setEditingId(null);
    setEditText('');
  };

  if (findings.length === 0) {
    return (
      <div className="p-8 text-center text-slate-400">
        <p>Результаты анализа появятся здесь</p>
      </div>
    );
  }

  return (
    <div className="analysis-results p-4 space-y-4">
      {/* Summary */}
      {summary && (
        <div className="bg-slate-800/50 rounded-xl p-4 mb-6">
          <h3 className="text-lg font-semibold text-slate-200 mb-3">
            📊 Сводка анализа
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-indigo-400">
                {summary.total_findings}
              </div>
              <div className="text-xs text-slate-400">Всего находок</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-red-400">
                {summary.by_severity.high || 0}
              </div>
              <div className="text-xs text-slate-400">Высокий приоритет</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-400">
                {acceptedIds.size}
              </div>
              <div className="text-xs text-slate-400">Принято</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-slate-400">
                {summary.files_analyzed}
              </div>
              <div className="text-xs text-slate-400">Файлов</div>
            </div>
          </div>
        </div>
      )}

      {/* Findings List */}
      <div className="space-y-3">
        {findings.map((finding) => {
          const status = getFindingStatus(
            finding.id,
            acceptedIds,
            ignoredIds,
            editedItems
          );
          const isExpanded = expandedFinding === finding.id;
          const isEditing = editingId === finding.id;

          return (
            <div
              key={finding.id}
              className={`
                finding-card bg-slate-800/50 rounded-xl p-4 cursor-pointer
                ${getSeverityClass(finding.severity)}
                ${status === 'ignored' ? 'opacity-50' : ''}
              `}
              onClick={() => setExpandedFinding(isExpanded ? null : finding.id)}
            >
              {/* Header */}
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-lg">{getTypeIcon(finding.type)}</span>
                    <h4 className="font-medium text-slate-200 truncate">
                      {finding.title}
                    </h4>
                    {getStatusBadge(finding)}
                  </div>
                  <p className="text-xs text-slate-400">
                    Файлы: {finding.files_involved.join(', ')}
                  </p>
                </div>

                {/* Quick Actions */}
                <div className="flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                  <button
                    onClick={() => toggleAccepted(finding.id)}
                    className={`
                      p-2 rounded-lg transition-colors
                      ${acceptedIds.has(finding.id)
                        ? 'bg-green-600 text-white'
                        : 'bg-slate-700 text-slate-400 hover:text-green-400'}
                    `}
                    title="Принять"
                  >
                    ✓
                  </button>
                  <button
                    onClick={() => toggleIgnored(finding.id)}
                    className={`
                      p-2 rounded-lg transition-colors
                      ${ignoredIds.has(finding.id)
                        ? 'bg-red-600 text-white'
                        : 'bg-slate-700 text-slate-400 hover:text-red-400'}
                    `}
                    title="Игнорировать"
                  >
                    ✕
                  </button>
                  <button
                    onClick={() => handleEdit(finding)}
                    className="p-2 rounded-lg bg-slate-700 text-slate-400 hover:text-yellow-400 transition-colors"
                    title="Редактировать"
                  >
                    ✎
                  </button>
                </div>
              </div>

              {/* Expanded Content */}
              {isExpanded && (
                <div className="mt-4 pt-4 border-t border-slate-700 animate-fade-in">
                  <div className="text-sm text-slate-300 mb-3">
                    <strong className="text-slate-200">Описание:</strong>{' '}
                    {finding.description}
                  </div>

                  {isEditing ? (
                    <div className="space-y-2">
                      <textarea
                        value={editText}
                        onChange={(e) => setEditText(e.target.value)}
                        className="w-full bg-slate-900 border border-slate-600 rounded-lg p-3 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
                        rows={3}
                      />
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleSaveEdit(finding.id)}
                          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 rounded-lg text-sm text-white"
                        >
                          Сохранить
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          className="px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm text-slate-300"
                        >
                          Отмена
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="text-sm">
                      <strong className="text-slate-200">Рекомендация:</strong>{' '}
                      <span className="text-slate-300">
                        {editedItems[finding.id] || finding.suggestion}
                      </span>
                    </div>
                  )}

                  {finding.confidence_score > 0 && (
                    <div className="mt-3 text-xs text-slate-500">
                      Уверенность ИИ: {(finding.confidence_score * 100).toFixed(0)}%
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default AnalysisResults;
