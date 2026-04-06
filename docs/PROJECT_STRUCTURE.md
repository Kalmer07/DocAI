# AI Document Analyzer - Project Structure

```
/workspace
├── backend/                    # Python FastAPI backend
│   ├── api/                    # REST API endpoints
│   │   ├── __init__.py
│   │   ├── routes.py           # Основные роуты (upload, analyze, export)
│   │   └── models.py           # Pydantic модели для API
│   ├── parsers/                # Парсеры документов
│   │   ├── __init__.py
│   │   ├── base.py             # Базовый класс парсера
│   │   ├── pdf_parser.py       # Парсинг PDF
│   │   ├── docx_parser.py      # Парсинг DOCX
│   │   ├── csv_parser.py       # Парсинг CSV
│   │   └── txt_parser.py       # Парсинг TXT
│   ├── ollama/                 # Ollama клиент и промпты
│   │   ├── __init__.py
│   │   ├── client.py           # Ollama API клиент
│   │   ├── models.py           # Модели для настроек Ollama
│   │   └── prompts.py          # Промпт-инжиниринг
│   ├── analyzers/              # Логика анализа документов
│   │   ├── __init__.py
│   │   ├── comparator.py       # Сравнение документов
│   │   └── reporter.py         # Генерация отчётов
│   ├── main.py                 # Точка входа FastAPI
│   └── requirements.txt        # Python зависимости
│
├── frontend/                   # React + TypeScript frontend
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/         # UI компоненты
│   │   │   ├── ChatInterface.tsx    # Основной чат-интерфейс
│   │   │   ├── FileUploader.tsx     # Загрузка файлов
│   │   │   ├── ModelSelector.tsx    # Селектор моделей Ollama
│   │   │   ├── AnalysisResults.tsx  # Результаты анализа с чекбоксами
│   │   │   └── ExportPanel.tsx      # Экспорт отчёта
│   │   ├── hooks/            # Custom React hooks
│   │   │   ├── useOllama.ts       # Hook для работы с Ollama
│   │   │   ├── useFiles.ts        # Hook для управления файлами
│   │   │   └── useAnalysis.ts     # Hook для анализа
│   │   ├── services/         # API сервисы
│   │   │   ├── api.ts             # Axios инстанс
│   │   │   ├── ollama.ts          # Ollama сервис
│   │   │   └── documents.ts       # Документ сервис
│   │   ├── styles/           # Стили (CSS/Tailwind)
│   │   │   └── global.css
│   │   ├── utils/            # Утилиты
│   │   │   ├── formatters.ts      # Форматирование данных
│   │   │   └── validators.ts      # Валидация
│   │   ├── App.tsx           # Главный компонент
│   │   └── main.tsx          # Точка входа React
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── scripts/                  # Скрипты запуска и утилиты
│   ├── run.sh                # Основной скрипт запуска (fallback-логика)
│   └── check_env.py          # Проверка окружения
│
├── docs/                     # Документация
│   ├── architecture.md       # Архитектурная схема
│   └── adaptation_guide.md   # Инструкция по адаптации
│
├── README.md                 # Общая документация
└── .env.example              # Пример переменных окружения
```

## Назначение ключевых папок:

- **backend/api**: REST API для взаимодействия с фронтендом
- **backend/parsers**: Извлечение текста из различных форматов файлов
- **backend/ollama**: Интеграция с локальным Ollama, управление моделями
- **backend/analyzers**: Бизнес-логика сравнения и анализа документов
- **frontend/src/components**: UI компоненты в стиле чата Qwen
- **frontend/src/hooks**: Управление состоянием и side-effects
- **frontend/src/services**: HTTP запросы к бэкенду и Ollama
- **scripts**: Автономные скрипты запуска с диагностикой
