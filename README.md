# AI Document Analyzer

Веб-инструмент для сравнительного анализа документов с использованием локального ИИ (Ollama).

## 🚀 Быстрый старт

### Требования

1. **Python 3.8+** — для бэкенда
2. **Node.js 18+** — для фронтенда (опционально)
3. **Ollama** — локальный ИИ-сервер

### Установка Ollama

```bash
# macOS / Linux
curl -fsSL https://ollama.ai/install.sh | sh

# После установки:
ollama pull llama3.2
ollama serve
```

### Запуск проекта

```bash
# Клонирование репозитория
cd /workspace

# Запуск через универсальный скрипт
./scripts/run.sh
```

Скрипт автоматически:
- Проверит зависимости
- Создаст виртуальное окружение Python
- Установит пакеты
- Запустит бэкенд и фронтенд

### Ручной запуск

```bash
# Бэкенд
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Фронтенд (в отдельном терминале)
cd frontend
npm install
npm run dev
```

## 📁 Структура проекта

```
/workspace
├── backend/              # FastAPI бэкенд
│   ├── api/             # REST endpoints
│   ├── parsers/         # Парсеры документов
│   ├── ollama/          # Ollama клиент и промпты
│   └── analyzers/       # Логика анализа
├── frontend/            # React + TypeScript
│   └── src/
│       ├── components/  # UI компоненты
│       ├── hooks/       # Zustand store
│       └── services/    # API клиенты
└── scripts/             # Скрипты запуска
```

## 🔧 Конфигурация

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Основные переменные:

| Переменная | Описание | По умолчанию |
|------------|----------|--------------|
| `OLLAMA_URL` | URL Ollama сервера | `http://localhost:11434` |
| `BACKEND_PORT` | Порт бэкенда | `8000` |
| `FRONTEND_PORT` | Порт фронтенда | `3000` |
| `DEFAULT_OLLAMA_MODEL` | Модель по умолчанию | `llama3.2` |

## 📖 Использование

1. **Загрузите файлы** (3-15 документов): TXT, MD, CSV, PDF, DOCX
2. **Настройте Ollama**: выберите модель, температуру, размер контекста
3. **Запустите анализ**: ИИ найдёт дубликаты, противоречия, пробелы
4. **Просмотрите результаты**: отмечайте галочками, редактируйте
5. **Экспортируйте отчёт**: Markdown, JSON или TXT

## 🎯 Возможности

- ✅ **Мультиформатность**: PDF, DOCX, CSV, TXT, MD
- ✅ **Гибкие настройки ИИ**: выбор модели, температура, контекст
- ✅ **Интерактивность**: принятие/игнорирование/редактирование находок
- ✅ **Экспорт**: Markdown, JSON, Text
- ✅ **Локальность**: все данные обрабатываются локально через Ollama

## 🛠 Адаптация под свой стек

### Смена фреймворка бэкенда

1. Измените `backend/api/routes.py` под ваш фреймворк (Flask, Django, etc.)
2. Сохраните структуру ответов API
3. Обновите парсеры при необходимости

### Смена фронтенд-фреймворка

1. Перепишите компоненты из `frontend/src/components/` на Vue/Svelte/etc.
2. Используйте те же API вызовы из `frontend/src/services/`
3. Сохраните структуру состояния (files, findings, ollamaConfig)

### Подключение другого ИИ

В `backend/ollama/client.py` замените вызовы Ollama API на:
- OpenAI API
- Anthropic API
- Локальную модель (LM Studio, etc.)

## 📝 API Endpoints

| Endpoint | Method | Описание |
|----------|--------|----------|
| `/api/upload` | POST | Загрузка файлов |
| `/api/models` | GET | Список моделей Ollama |
| `/api/analyze` | POST | Запуск анализа |
| `/api/export` | POST | Экспорт отчёта |
| `/docs` | GET | Swagger документация |

## 💡 Оптимизация промптов

Для работы с большими документами:

1. **Chunking**: Разбивайте текст на части < context_size
2. **Приоритизация**: Сортируйте находки по severity
3. **Температура**: 0.2-0.4 для точности, 0.7+ для креативности
4. **JSON mode**: Используйте `format: json` для структурированного вывода

## 🐛 Troubleshooting

**Ollama не подключается:**
```bash
ollama serve  # Убедитесь, что сервер запущен
curl http://localhost:11434/api/tags  # Проверьте доступность
```

**Ошибка импорта Python:**
```bash
source backend/venv/bin/activate
pip install -r backend/requirements.txt
```

**Фронтенд не собирается:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## 📄 Лицензия

MIT
