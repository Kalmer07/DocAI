# Инструкция по адаптации проекта

## 📍 Где и что менять для интеграции вашего стека

### 1. Переменные окружения

**Файл**: `.env.example` → `.env`

```bash
# Основные настройки
OLLAMA_URL=http://localhost:11434      # URL вашего Ollama
BACKEND_PORT=8000                       # Порт API
FRONTEND_PORT=3000                      # Порт UI
```

---

### 2. Смена модели ИИ

**Файл**: `backend/ollama/prompts.py`

```python
# Измените системный промпт под вашу задачу
ANALYSIS_SYSTEM_PROMPT = """
Ваш кастомный промпт здесь...
"""
```

**Файл**: `frontend/src/components/ModelSelector.tsx`

```typescript
// Измените модель по умолчанию
ollamaConfig: {
  model: 'your-model-name',  // например 'qwen2.5', 'mistral', etc.
  temperature: 0.3,
  context_size: 4096,
}
```

---

### 3. Добавление нового формата файлов

**Файл**: `backend/parsers/parsers.py`

```python
class YourFormatParser(BaseParser):
    def parse(self, content: bytes) -> str:
        # Ваша логика парсинга
        return text
    
    @property
    def supported_extensions(self) -> list:
        return ['your_ext']
```

**Файл**: `backend/parsers/factory.py`

```python
parsers = {
    'txt': TextParser(),
    'your_ext': YourFormatParser(),  # Добавьте сюда
}
```

---

### 4. Изменение структуры ответа API

**Файл**: `backend/api/models.py`

```python
class Finding(BaseModel):
    # Добавьте/измените поля
    id: str
    type: str
    your_custom_field: str  # Новое поле
    ...
```

**Файл**: `frontend/src/services/documents.ts`

```typescript
export interface Finding {
  id: string;
  type: string;
  yourCustomField: string;  // Синхронизируйте с бэкендом
  ...
}
```

---

### 5. Кастомизация UI

**Файл**: `frontend/src/styles/global.css`

```css
:root {
  --primary-color: #your-color;      /* Основной цвет */
  --bg-color: #your-bg;              /* Фон приложения */
  --sidebar-bg: #your-sidebar;       /* Фон сайдбара */
}
```

**Файл**: `frontend/src/components/*.tsx`

Компоненты для изменения:
- `FileUploader.tsx` — загрузка файлов
- `ModelSelector.tsx` — настройки ИИ
- `AnalysisResults.tsx` — отображение результатов
- `ExportPanel.tsx` — экспорт отчёта

---

### 6. Подключение другого ИИ (не Ollama)

**Файл**: `backend/ollama/client.py`

```python
class YourAIClient:
    async def generate(self, prompt: str, config: dict) -> str:
        # Ваш код вызова API
        # OpenAI, Anthropic, Google, etc.
        response = await your_api_call(prompt, config)
        return response.text
```

**Файл**: `backend/main.py`

```python
# Замените OllamaClient на ваш клиент
state.ai_client = YourAIClient(api_key="...")
```

---

### 7. Изменение логики анализа

**Файл**: `backend/analyzers/reporter.py`

```python
def format_export(findings, format):
    # Ваша логика форматирования
    ...
```

**Файл**: `backend/api/routes.py`

```python
def parse_ai_response_to_findings(ai_response, files_data):
    # Ваш парсинг ответа ИИ
    # Можно использовать JSON mode, regex, или LLM parsing
    ...
```

---

### 8. База данных (опционально)

По умолчанию используется in-memory хранилище. Для персистентности:

**Файл**: `backend/main.py`

```python
# Добавьте подключение к БД
from sqlalchemy import create_engine

engine = create_engine("sqlite:///analysis.db")
# Или PostgreSQL, MongoDB, etc.
```

---

### 9. Аутентификация (опционально)

**Файл**: `backend/main.py`

```python
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    # Ваша логика валидации токена
    ...
```

---

### 10. Docker контейнеризация

Создайте `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ ./backend
COPY frontend/ ./frontend

EXPOSE 8000 3000

CMD ["./scripts/run.sh"]
```

---

## 🔑 Ключевые точки расширения

| Компонент | Файл | Что менять |
|-----------|------|------------|
| Промпты ИИ | `backend/ollama/prompts.py` | Системные промпты, шаблоны |
| Парсеры | `backend/parsers/` | Поддержка форматов |
| API Routes | `backend/api/routes.py` | Endpoints, логика |
| UI Компоненты | `frontend/src/components/` | Визуал, взаимодействие |
| Состояние | `frontend/src/hooks/useAppStore.ts` | Структура данных |
| Стили | `frontend/src/styles/global.css` | Темы, цвета |

---

## 💡 Советы по оптимизации

### Для больших документов

1. **Chunking в промптах**:
```python
# backend/ollama/prompts.py
def chunk_text_for_context(text, max_tokens):
    # Разбивка на части
    ...
```

2. **Приоритизация находок**:
```python
# Сортировка по важности
findings.sort(key=lambda f: f.severity_order[f.severity])
findings = findings[:MAX_FINDINGS]
```

3. **Кэширование**:
```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_analysis(file_hash, config_hash):
    ...
```

### Для улучшения качества анализа

1. **Few-shot prompting** в `prompts.py`:
```python
EXAMPLES = """
Пример хорошего вывода:
## ДУБЛИКАТЫ
- [ID] | Файлы: [a.txt, b.txt] | Текст: "..." 
"""
```

2. **Chain-of-thought**:
```python
PROMPT += "\nДавайте рассуждать пошагово..."
```

3. **JSON mode** для структурированного вывода:
```python
# В client.py
payload["format"] = "json"  # Если поддерживается
```
