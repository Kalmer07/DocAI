"""
Report Generator and Export Formatter
"""
from typing import List, Dict, Any
from datetime import datetime


def format_export(
    findings: List[Dict],
    format: str = "markdown"
) -> tuple:
    """
    Format findings for export.
    
    Args:
        findings: List of finding objects/dicts
        format: Export format (markdown, json, text)
        
    Returns:
        Tuple of (content, filename, content_type)
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "json":
        return _format_json(findings), f"analysis_report_{timestamp}.json", "application/json"
    elif format == "text":
        return _format_text(findings), f"analysis_report_{timestamp}.txt", "text/plain"
    else:  # markdown
        return _format_markdown(findings), f"analysis_report_{timestamp}.md", "text/markdown"


def _format_markdown(findings: List[Dict]) -> str:
    """Format findings as Markdown report"""
    lines = [
        "# 📊 Отчёт анализа документов",
        f"\n*Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')}*\n",
        "---\n"
    ]
    
    # Summary statistics
    total = len(findings)
    by_type = {}
    by_severity = {}
    by_status = {}
    
    for f in findings:
        t = f.get('type', 'unknown')
        s = f.get('severity', 'medium')
        st = f.get('status', 'pending')
        
        by_type[t] = by_type.get(t, 0) + 1
        by_severity[s] = by_severity.get(s, 0) + 1
        by_status[st] = by_status.get(st, 0) + 1
    
    lines.append("## 📈 Сводка")
    lines.append(f"- **Всего находок:** {total}")
    lines.append(f"- **По типу:** {', '.join(f'{k}: {v}' for k, v in by_type.items())}")
    lines.append(f"- **По приоритету:** {', '.join(f'{k}: {v}' for k, v in by_severity.items())}")
    lines.append(f"- **По статусу:** {', '.join(f'{k}: {v}' for k, v in by_status.items())}")
    lines.append("\n---\n")
    
    # Group by severity
    severity_order = ['high', 'medium', 'low']
    severity_titles = {
        'high': '🔴 Высокий приоритет',
        'medium': '🟡 Средний приоритет',
        'low': '🟢 Низкий приоритет'
    }
    
    for severity in severity_order:
        items = [f for f in findings if f.get('severity') == severity]
        if not items:
            continue
        
        lines.append(f"\n## {severity_titles.get(severity, severity)}\n")
        
        for i, item in enumerate(items, 1):
            status_icon = {
                'accepted': '✅',
                'ignored': '❌',
                'edited': '✏️',
                'pending': '⏳'
            }.get(item.get('status', 'pending'), '⏳')
            
            type_icon = {
                'duplicate': '🔄',
                'contradiction': '⚠️',
                'missing': '📭',
                'overlap': '🔀',
                'suggestion': '💡'
            }.get(item.get('type', ''), '📌')
            
            lines.append(f"### {status_icon} {type_icon} #{i} {item.get('title', 'Без названия')}")
            lines.append(f"\n**Файлы:** {', '.join(item.get('files_involved', []))}")
            lines.append(f"\n**Описание:** {item.get('description', '')}")
            
            if item.get('suggestion'):
                lines.append(f"\n**Рекомендация:** {item['suggestion']}")
            
            if item.get('edited_content'):
                lines.append(f"\n**Отредактировано:** {item['edited_content']}")
            
            if item.get('confidence_score'):
                lines.append(f"\n*Уверенность: {item['confidence_score']*100:.0f}%*")
            
            lines.append("\n---\n")
    
    # Footer
    lines.append("\n---")
    lines.append("*Отчёт сгенерирован AI Document Analyzer*")
    
    return "\n".join(lines)


def _format_json(findings: List[Dict]) -> str:
    """Format findings as JSON"""
    import json
    
    report = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_findings": len(findings),
            "generator": "AI Document Analyzer v1.0"
        },
        "findings": [],
        "statistics": {
            "by_type": {},
            "by_severity": {},
            "by_status": {}
        }
    }
    
    for f in findings:
        finding_data = {
            "id": f.get('id'),
            "type": f.get('type'),
            "severity": f.get('severity'),
            "status": f.get('status'),
            "title": f.get('title'),
            "description": f.get('description'),
            "files_involved": f.get('files_involved', []),
            "suggestion": f.get('suggestion'),
            "edited_content": f.get('edited_content'),
            "confidence_score": f.get('confidence_score', 0),
            "created_at": f.get('created_at', datetime.now().isoformat())
        }
        report["findings"].append(finding_data)
        
        # Update statistics
        t = f.get('type', 'unknown')
        s = f.get('severity', 'medium')
        st = f.get('status', 'pending')
        
        report["statistics"]["by_type"][t] = report["statistics"]["by_type"].get(t, 0) + 1
        report["statistics"]["by_severity"][s] = report["statistics"]["by_severity"].get(s, 0) + 1
        report["statistics"]["by_status"][st] = report["statistics"]["by_status"].get(st, 0) + 1
    
    return json.dumps(report, ensure_ascii=False, indent=2)


def _format_text(findings: List[Dict]) -> str:
    """Format findings as plain text"""
    lines = [
        "=" * 60,
        "ОТЧЁТ АНАЛИЗА ДОКУМЕНТОВ",
        f"Сгенерировано: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "=" * 60,
        "",
        f"Всего находок: {len(findings)}",
        ""
    ]
    
    # Group by severity
    for severity in ['high', 'medium', 'low']:
        items = [f for f in findings if f.get('severity') == severity]
        if not items:
            continue
        
        lines.append("-" * 40)
        lines.append(f"ПРИОРИТЕТ: {severity.upper()}")
        lines.append("-" * 40)
        
        for i, item in enumerate(items, 1):
            lines.append(f"\n[{i}] {item.get('title', 'Без названия')}")
            lines.append(f"    Файлы: {', '.join(item.get('files_involved', []))}")
            lines.append(f"    Описание: {item.get('description', '')}")
            lines.append(f"    Рекомендация: {item.get('suggestion', '')}")
            if item.get('status'):
                lines.append(f"    Статус: {item['status']}")
    
    lines.append("\n" + "=" * 60)
    lines.append("Конец отчёта")
    lines.append("=" * 60)
    
    return "\n".join(lines)
