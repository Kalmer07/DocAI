"""
Prompt Engineering for Document Analysis
Optimized for Ollama with context window management
"""
from typing import List, Dict, Any


# ============== System Prompts ==============

ANALYSIS_SYSTEM_PROMPT = """Ты — экспертный аналитик документов. Твоя задача:
1. Сравнивать предоставленные документы между собой
2. Находить дубликаты, противоречия, пересечения и пропуски
3. Формировать структурированный отчёт с рекомендациями

Формат ответа должен быть СТРОГО структурирован:

## ДУБЛИКАТЫ
- [ID] | Файлы: [file1, file2] | Текст: "..." | Рекомендация: "..."

## ПРОТИВОРЕЧИЯ  
- [ID] | Файлы: [file1, file2] | Проблема: "..." | Решение: "..."

## ПЕРЕСЕЧЕНИЯ
- [ID] | Файлы: [file1, file2, file3] | Общая тема: "..." | Статус: "..."

## ПРОПУЩЕННЫЕ ЭЛЕМЕНТЫ
- [ID] | Файл: [file1] | Чего не хватает: "..." | Приоритет: high/medium/low

## РЕЗЮМЕ
Краткое summary анализа (2-3 предложения)

Важно:
- Будь конкретен, цитируй原文 где возможно
- Указывай приоритет для каждого пункта
- Предлагай конкретные действия по исправлению
"""


# ============== Analysis Prompts ==============

COMPARISON_PROMPT_TEMPLATE = """
Проанализируй следующие {num_files} документов на предмет:
{analysis_types}

{custom_instruction}

=== ДОКУМЕНТЫ ===

{files_content}

=== КОНЕЦ ДОКУМЕНТОВ ===

Инструкции по анализу:
1. Сравни каждый документ со всеми остальными
2. Ищи точные и смысловые дубликаты
3. Выявляй логические противоречия между документами
4. Отмечай пересечения тем и требований
5. Определяй пропущенные элементы в каждом документе

Ответ давай ТОЛЬКО в структурированном формате как указано в системном промпте.
"""


DUPLICATE_DETECTION_PROMPT = """
Найди все дубликаты в предоставленных документах:
- Точные совпадения текста
- Синонимичные формулировки с одинаковым смыслом
- Повторяющиеся пункты списков

Для каждого дубликата укажи:
- Какие файлы задействованы
- Цитату дублируемого текста
- Рекомендацию: объединить/удалить/оставить
"""


CONTRADICTION_DETECTION_PROMPT = """
Найди логические противоречия между документами:
- Разные значения одних и тех же параметров
- Противоречащие друг другу требования
- Несовместимые утверждения

Для каждого противоречия укажи:
- Какие файлы конфликтуют
- Суть противоречия
- Предлагаемое разрешение
"""


GAP_ANALYSIS_PROMPT = """
Проанализируй документы на предмет пропущенных элементов:
- Какие важные разделы отсутствуют
- Какие требования не раскрыты
- Где не хватает конкретики

Для каждого пробела укажи:
- В каком файле обнаружен пробел
- Что именно отсутствует
- Приоритет заполнения (high/medium/low)
"""


# ============== Prompt Builders ==============

def build_comparison_prompt(
    files: List[Dict[str, Any]],
    analysis_types: List[str],
    custom_instruction: str = None,
    max_tokens_per_file: int = 2000
) -> str:
    """
    Build the main comparison prompt with chunking for large files.
    
    Args:
        files: List of file data with 'filename' and 'content'
        analysis_types: Types of analysis to perform
        custom_instruction: Optional custom instruction from user
        max_tokens_per_file: Max tokens to include per file (rough estimate)
    
    Returns:
        Formatted prompt string
    """
    # Format files content
    files_content = []
    for file in files:
        filename = file.get('filename', 'unknown')
        content = file.get('content', '')
        
        # Truncate if too large (simple token estimation: 1 token ≈ 4 chars)
        if len(content) > max_tokens_per_file * 4:
            content = content[:max_tokens_per_file * 4] + "...[truncated]"
        
        files_content.append(f"--- ФАЙЛ: {filename} ---\n{content}\n")
    
    # Format analysis types description
    type_descriptions = {
        "duplicates": "- Точные и смысловые дубликаты",
        "contradictions": "- Логические противоречия и конфликты",
        "overlaps": "- Тематические пересечения",
        "gaps": "- Пропущенные элементы и пробелы"
    }
    
    analysis_desc = "\n".join(
        type_descriptions.get(t.lower(), f"- {t}")
        for t in analysis_types
    )
    
    # Build final prompt
    prompt = COMPARISON_PROMPT_TEMPLATE.format(
        num_files=len(files),
        analysis_types=analysis_desc,
        custom_instruction=custom_instruction or "Следуй стандартному формату анализа.",
        files_content="\n".join(files_content)
    )
    
    return prompt


def build_structured_output_prompt(
    files: List[Dict[str, Any]],
    focus_area: str = "all"
) -> str:
    """
    Build prompt for JSON structured output (when using Ollama JSON mode).
    
    Args:
        files: List of file data
        focus_area: Specific area to focus on
    
    Returns:
        Prompt requesting JSON output
    """
    files_summary = "\n".join([
        f"- {f['filename']}: {len(f['content'])} символов"
        for f in files
    ])
    
    return f"""
Проанализируй документы и верни ответ в JSON формате:

Документы для анализа:
{files_summary}

Область анализа: {focus_area}

JSON схема ответа:
{{
  "findings": [
    {{
      "id": "string",
      "type": "duplicate|contradiction|overlap|gap",
      "severity": "high|medium|low",
      "title": "string",
      "description": "string",
      "files_involved": ["filename1", "filename2"],
      "suggestion": "string",
      "confidence": 0.0-1.0
    }}
  ],
  "summary": "string",
  "statistics": {{
    "total_findings": number,
    "by_type": {{}},
    "by_severity": {{}}
  }}
}}

Верни ТОЛЬКО валидный JSON без дополнительного текста.
"""


# ============== Optimization Utilities ==============

def estimate_tokens(text: str) -> int:
    """
    Rough estimate of token count.
    For English: ~1 token per 4 characters
    For Russian: ~1 token per 3 characters (more variable)
    """
    # Simple heuristic
    cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
    ratio = cyrillic_chars / len(text) if text else 0
    
    # Weighted average
    chars_per_token = ratio * 3 + (1 - ratio) * 4
    return int(len(text) / chars_per_token) if chars_per_token > 0 else 0


def chunk_text_for_context(
    text: str,
    max_tokens: int,
    overlap: int = 100
) -> List[str]:
    """
    Split text into chunks that fit within context window.
    
    Args:
        text: Input text to chunk
        max_tokens: Maximum tokens per chunk
        overlap: Overlap between chunks in characters
    
    Returns:
        List of text chunks
    """
    # Convert tokens to approximate characters
    max_chars = max_tokens * 4  # Conservative estimate
    
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = min(start + max_chars, len(text))
        
        # Try to break at sentence boundary
        if end < len(text):
            for sep in ['. ', '! ', '? ', '\n']:
                last_sep = text[start:end].rfind(sep)
                if last_sep > max_chars // 2:
                    end = start + last_sep + len(sep)
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks


def prioritize_findings(findings: List[Dict], max_count: int = 20) -> List[Dict]:
    """
    Prioritize findings when too many are found.
    Sort by severity and confidence.
    """
    severity_order = {"high": 0, "medium": 1, "low": 2}
    
    sorted_findings = sorted(
        findings,
        key=lambda f: (
            severity_order.get(f.get('severity', 'low'), 2),
            -f.get('confidence', 0.5)
        )
    )
    
    return sorted_findings[:max_count]
