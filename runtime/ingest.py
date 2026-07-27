#!/usr/bin/env python3
"""
Ingestion Layer: Принимает сырой ввод, нормализует и валидирует по схеме.
Поддерживает опциональную LLM-экстракцию (через ENV и флаг --use-llm).
"""
import json
import yaml
import argparse
import sys
import os
from pathlib import Path
from jsonschema import validate, ValidationError
from datetime import datetime, timezone

SCHEMA_PATH = Path(__file__).parent.parent / "schemas" / "project_draft.schema.yaml"
DRAFTS_DIR = Path(__file__).parent.parent / "drafts"

def load_schema() -> dict:
    with open(SCHEMA_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def extract_with_llm(raw_text: str) -> dict:
    """
    LLM-экстракция ключевых полей из сырого текста.
    Опциональная фича: активируется только если:
    1. Установлена переменная окружения OPENAI_API_KEY или ANTHROPIC_API_KEY
    2. Передан флаг --use-llm в CLI
    
    Пока возвращает заглушку (Phase 2.1 - подготовка к интеграции).
    """
    # Проверка наличия API ключей
    openai_key = os.environ.get("OPENAI_API_KEY")
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if not (openai_key or anthropic_key):
        print("⚠️  LLM extraction disabled: No API key found (OPENAI_API_KEY or ANTHROPIC_API_KEY)")
        return ingest_raw_text(raw_text)  # Fallback to stub
    
    # TODO: Phase 2.2 - Реальная LLM интеграция
    # Здесь будет вызов OpenAI/Anthropic API с structured output
    # Пример промпта:
    # """
    # Extract the following fields from the text and return as JSON:
    # - project_name (string)
    # - stage (enum: idea, pre-seed, seed, series_a, series_b, growth, unknown)
    # - geography.country (string, ISO 2 code or full name)
    # - domain (string: AI, Web3, Hardware, SaaS, etc.)
    # - funding_amount_usd (integer or null)
    # 
    # Text: {raw_text}
    # """
    
    print("⚠️  LLM extraction not yet implemented (Phase 2.2)")
    return ingest_raw_text(raw_text)  # Fallback to stub

def ingest_raw_text(raw_text: str) -> dict:
    """
    Заглушка для LLM-экстракции (Phase 2.1). 
    Пока возвращает безопасную структуру с пометкой needs_user_input.
    """
    return {
        "project_name": "Unknown Project",
        "description": raw_text[:200] if raw_text else "No description provided",
        "stage": "unknown",
        "geography": {"country": "unknown"},
        "domain": "unknown",
        "funding_amount_usd": None,
        "team_background": "unknown",
        "official_source": None,
        "needs_user_input": ["project_name", "stage", "geography.country", "domain"],
        "ingestion_metadata": {
            "source_type": "raw_text",
            "confidence_score": 0.5,
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
    }

def ingest_json(json_data: dict) -> dict:
    """Нормализует структурированный JSON под схему."""
    if "needs_user_input" not in json_data:
        json_data["needs_user_input"] = []
    if "ingestion_metadata" not in json_data:
        json_data["ingestion_metadata"] = {
            "source_type": "structured_json",
            "confidence_score": 1.0,
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
        }
    return json_data

def validate_and_save(data: dict, output_filename: str = "project_draft.yaml") -> bool:
    schema = load_schema()
    try:
        validate(instance=data, schema=schema)
        DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
        output_path = DRAFTS_DIR / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
        
        print(f"✅ Success: Validated and saved to {output_path}")
        if data.get("needs_user_input"):
            print(f"⚠️  Warning: Missing or uncertain fields: {', '.join(data['needs_user_input'])}")
        return True
    except ValidationError as e:
        print(f"❌ Validation Error: {e.message}")
        print(f"   Path: {' -> '.join(map(str, e.path))}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Ingest raw text or JSON into a validated project draft.")
    parser.add_argument("input", help="Raw text string or path to a JSON file")
    parser.add_argument("--type", choices=["text", "json", "auto"], default="auto", help="Input type")
    parser.add_argument("--output", default="project_draft.yaml", help="Output filename in drafts/")
    parser.add_argument("--use-llm", action="store_true", help="Enable LLM extraction (requires API key)")
    
    args = parser.parse_args()
    
    input_type = args.type
    if input_type == "auto":
        if args.input.endswith(".json") and Path(args.input).exists():
            input_type = "json"
        else:
            input_type = "text"

    if input_type == "json":
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
            processed_data = ingest_json(data)
        except Exception as e:
            print(f"❌ Failed to read JSON: {e}")
            sys.exit(1)
    else:
        if args.use_llm:
            processed_data = extract_with_llm(args.input)
        else:
            processed_data = ingest_raw_text(args.input)

    success = validate_and_save(processed_data, args.output)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
