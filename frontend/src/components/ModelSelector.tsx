import React, { useEffect, useState } from 'react';
import { useAppStore } from '../hooks/useAppStore';
import { getModels } from '../services/documents';

interface ModelSelectorProps {
  onModelChange?: (model: string) => void;
}

export const ModelSelector: React.FC<ModelSelectorProps> = ({ onModelChange }) => {
  const { ollamaConfig, setOllamaConfig, availableModels, setAvailableModels } = useAppStore();
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const fetchModels = async () => {
    setIsLoading(true);
    try {
      const response = await getModels();
      const modelNames = response.models.map((m) => m.name);
      setAvailableModels(modelNames);
      
      // Auto-select first model if current not in list
      if (modelNames.length > 0 && !modelNames.includes(ollamaConfig.model)) {
        const newModel = modelNames[0];
        setOllamaConfig({ model: newModel });
        onModelChange?.(newModel);
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const handleModelChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const newModel = e.target.value;
    setOllamaConfig({ model: newModel });
    onModelChange?.(newModel);
  };

  return (
    <div className="model-selector p-4 border-b border-slate-700">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold text-slate-300 uppercase tracking-wider">
          Настройки Ollama
        </h3>
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="text-xs text-indigo-400 hover:text-indigo-300"
        >
          {isExpanded ? 'Свернуть' : 'Развернуть'}
        </button>
      </div>

      {/* Main Model Selector */}
      <div className="mb-3">
        <label className="block text-xs text-slate-400 mb-1">Модель</label>
        <div className="flex gap-2">
          <select
            value={ollamaConfig.model}
            onChange={handleModelChange}
            className="flex-1 bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
          >
            {availableModels.length === 0 ? (
              <option value="llama3.2">llama3.2 (default)</option>
            ) : (
              availableModels.map((model) => (
                <option key={model} value={model}>
                  {model}
                </option>
              ))
            )}
          </select>
          <button
            onClick={fetchModels}
            disabled={isLoading}
            className="px-3 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg text-xs text-slate-300 disabled:opacity-50"
          >
            {isLoading ? '↻' : '⟳'}
          </button>
        </div>
      </div>

      {/* Advanced Settings */}
      {isExpanded && (
        <div className="space-y-3 animate-fade-in">
          {/* Temperature */}
          <div>
            <div className="flex justify-between mb-1">
              <label className="text-xs text-slate-400">Температура</label>
              <span className="text-xs text-slate-300">{ollamaConfig.temperature}</span>
            </div>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={ollamaConfig.temperature}
              onChange={(e) =>
                setOllamaConfig({ temperature: parseFloat(e.target.value) })
              }
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
            <p className="text-xs text-slate-500 mt-1">
              Ниже = более детерминировано, Выше = более креативно
            </p>
          </div>

          {/* Context Size */}
          <div>
            <label className="block text-xs text-slate-400 mb-1">
              Контекстное окно: {ollamaConfig.context_size} токенов
            </label>
            <select
              value={ollamaConfig.context_size}
              onChange={(e) =>
                setOllamaConfig({ context_size: parseInt(e.target.value) })
              }
              className="w-full bg-slate-800 border border-slate-600 rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value={2048}>2048 (быстро)</option>
              <option value={4096}>4096 (стандарт)</option>
              <option value={8192}>8192 (большой)</option>
              <option value={16384}>16384 (очень большой)</option>
            </select>
          </div>

          {/* Top P */}
          <div>
            <div className="flex justify-between mb-1">
              <label className="text-xs text-slate-400">Top P</label>
              <span className="text-xs text-slate-300">{ollamaConfig.top_p}</span>
            </div>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={ollamaConfig.top_p}
              onChange={(e) =>
                setOllamaConfig({ top_p: parseFloat(e.target.value) })
              }
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-indigo-500"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ModelSelector;
