#!/usr/bin/env python3
"""
Human-Readable Reporting Layer: 
Принимает результат runner.py и project_draft.yaml, 
выводит красивый CLI-отчёт через rich, экспортирует в Markdown.
"""
import argparse
import sys
from pathlib import Path
from datetime import datetime, timezone

import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

# Импортируем существующий render_report (если доступен)
try:
    from runtime.render_report import load_yaml, DECISION_GROUPS
except ImportError:
    # Fallback: если render_report не экспортирует функции, загружаем сами
    def load_yaml(path: Path) -> dict:
        with path.open(encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    
    DECISION_GROUPS = {
        "NOW": {"NOW"},
        "BUILD_FIRST": {"BUILD_FIRST", "BUILD_NVIDIA_USE_CASE"},
        "VERIFY_ACCESS_PATH": {"VERIFY_ACCESS_PATH", "COMPLETE_ELIGIBILITY_DATA", "VERIFY_FIRST"},
        "NO_ACTIONABLE_ENDPOINT": {"NO_ACTIONABLE_ENDPOINT"},
        "APPLY_AGAIN_AFTER_CHANGE": {"APPLY_AGAIN_AFTER_CHANGE"},
        "DO_NOT_APPLY": {"DO_NOT_APPLY"},
    }

console = Console()

DECISION_ICONS = {
    "NOW": "✅",
    "NEXT": "🟡",
    "BUILD_FIRST": "🔨",
    "VERIFY_FIRST": "⚠️",
    "VERIFY_ACCESS_PATH": "🔍",
    "DO_NOT_APPLY": "❌",
    "NO_ACTIONABLE_ENDPOINT": "🚫",
}

def get_decision_icon(decision: str) -> str:
    """Возвращает иконку для решения."""
    for group, icon in DECISION_ICONS.items():
        if decision in DECISION_GROUPS.get(group, {group}):
            return icon
    return "❓"

def render_cli_report(project_draft: dict, runner_output: dict) -> None:
    """Выводит красивый CLI-отчёт через rich."""
    project_name = project_draft.get("project_name", "Unknown Project")
    decision = runner_output.get("decision", "UNKNOWN")
    match_score = runner_output.get("match_score", "N/A")
    stage = project_draft.get("stage", "unknown")
    geography = project_draft.get("geography", {}).get("country", "unknown")
    domain = project_draft.get("domain", "unknown")
    missing_fields = project_draft.get("needs_user_input", [])
    routes = runner_output.get("routes", [])
    
    # Заголовок
    console.print()
    console.print(Panel(
        f"[bold cyan]🎯 MATCH REPORT: {project_name}[/bold cyan]",
        expand=False
    ))
    
    # Основная информация
    decision_icon = get_decision_icon(decision)
    console.print(f"  [bold]Decision:[/bold]        {decision_icon} [bold green]{decision}[/bold green]")
    console.print(f"  [bold]Match Score:[/bold]     {match_score}")
    console.print(f"  [bold]Stage:[/bold]           {stage}")
    console.print(f"  [bold]Geography:[/bold]       {geography}")
    console.print(f"  [bold]Domain:[/bold]          {domain}")
    console.print()
    
    # Таблица маршрутов
    if routes:
        console.print(f"  [bold]📋 ROUTES ({len(routes)} matched):[/bold]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Program", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Source", style="blue")
        
        for i, route in enumerate(routes, 1):
            program_name = route.get("program_name", "Unknown")
            status = route.get("decision", "UNKNOWN")
            source = route.get("official_source", "N/A")
            if source and len(source) > 40:
                source = source[:37] + "..."
            table.add_row(str(i), program_name, status, source)
        
        console.print(table)
        console.print()
    
    # Missing fields
    if missing_fields:
        console.print(f"  [bold yellow]⚠️  MISSING FIELDS:[/bold yellow]")
        for field in missing_fields:
            console.print(f"    • {field}")
        console.print()

def render_markdown_report(project_draft: dict, runner_output: dict, output_path: Path) -> None:
    """Генерирует Markdown-отчёт и сохраняет в файл."""
    project_name = project_draft.get("project_name", "Unknown Project")
    decision = runner_output.get("decision", "UNKNOWN")
    match_score = runner_output.get("match_score", "N/A")
    stage = project_draft.get("stage", "unknown")
    geography = project_draft.get("geography", {}).get("country", "unknown")
    domain = project_draft.get("domain", "unknown")
    missing_fields = project_draft.get("needs_user_input", [])
    routes = runner_output.get("routes", [])
    timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    
    lines = [
        f"# Match Report: {project_name}",
        f"**Decision:** {decision}  ",
        f"**Match Score:** {match_score}  ",
        f"**Generated:** {timestamp}",
        "",
        "## Project Details",
        f"- **Stage:** {stage}",
        f"- **Geography:** {geography}",
        f"- **Domain:** {domain}",
        "",
    ]
    
    if routes:
        lines.append("## Matched Routes")
        for i, route in enumerate(routes, 1):
            program_name = route.get("program_name", "Unknown")
            status = route.get("decision", "UNKNOWN")
            source = route.get("official_source", "N/A")
            lines.append(f"{i}. **{program_name}**")
            lines.append(f"   - Status: {status}")
            lines.append(f"   - Source: {source}")
        lines.append("")
    
    if missing_fields:
        lines.append("## Missing Fields")
        for field in missing_fields:
            lines.append(f"- {field}")
        lines.append("")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    console.print(f"✅ Markdown report saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Generate human-readable reports from runner output.")
    parser.add_argument("--project", required=True, help="Path to project_draft.yaml")
    parser.add_argument("--runner-output", required=True, help="Path to runner output YAML")
    parser.add_argument("--export", choices=["markdown"], help="Export format")
    parser.add_argument("--output", default="reports/match_report.md", help="Output path for export")
    
    args = parser.parse_args()
    
    project_path = Path(args.project)
    runner_path = Path(args.runner_output)
    
    if not project_path.exists():
        console.print(f"[red]❌ Project file not found: {project_path}[/red]")
        sys.exit(1)
    
    if not runner_path.exists():
        console.print(f"[red]❌ Runner output not found: {runner_path}[/red]")
        sys.exit(1)
    
    project_draft = load_yaml(project_path)
    runner_output = load_yaml(runner_path)
    
    # CLI вывод (всегда)
    render_cli_report(project_draft, runner_output)
    
    # Экспорт (если запрошен)
    if args.export == "markdown":
        output_path = Path(args.output)
        render_markdown_report(project_draft, runner_output, output_path)

if __name__ == "__main__":
    main()
