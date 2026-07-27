"""
Tests for runtime/ingest.py - Ingestion Layer
"""
import pytest
import json
import yaml
from pathlib import Path
from runtime.ingest import (
    ingest_raw_text,
    ingest_json,
    validate_and_save,
    load_schema
)

# Test fixtures
SAMPLE_RAW_TEXT = "We are building an AI-powered drone for pizza delivery in Estonia, seeking $100k seed funding."
SAMPLE_JSON = {
    "project_name": "PizzaDrone AI",
    "description": "AI-powered drone for pizza delivery",
    "stage": "seed",
    "geography": {"country": "Estonia", "region": "Tallinn"},
    "domain": "AI",
    "funding_amount_usd": 100000,
    "team_background": "Ex-Bolt engineers",
    "official_source": "https://pizzadrone.ai"
}
INVALID_JSON_MISSING_FIELDS = {
    "project_name": "Test"
    # Missing required fields: description, stage, geography, domain, needs_user_input
}

class TestIngestRawText:
    def test_basic_text_extraction(self):
        """Test that raw text creates a valid draft with graceful degradation."""
        result = ingest_raw_text(SAMPLE_RAW_TEXT)
        
        assert result["project_name"] == "Unknown Project"
        assert SAMPLE_RAW_TEXT[:200] in result["description"]
        assert result["stage"] == "unknown"
        assert result["geography"]["country"] == "unknown"
        assert result["domain"] == "unknown"
        assert len(result["needs_user_input"]) > 0
        assert result["ingestion_metadata"]["source_type"] == "raw_text"
        assert 0.0 <= result["ingestion_metadata"]["confidence_score"] <= 1.0
    
    def test_empty_text(self):
        """Test that empty text is handled gracefully."""
        result = ingest_raw_text("")
        assert result["description"] == "No description provided"
        assert len(result["needs_user_input"]) > 0
    
    def test_very_long_text(self):
        """Test that very long text is truncated."""
        long_text = "A" * 1000
        result = ingest_raw_text(long_text)
        assert len(result["description"]) <= 200

class TestIngestJSON:
    def test_valid_json(self):
        """Test that valid JSON is normalized correctly."""
        result = ingest_json(SAMPLE_JSON.copy())
        
        assert result["project_name"] == "PizzaDrone AI"
        assert result["stage"] == "seed"
        assert result["geography"]["country"] == "Estonia"
        assert "needs_user_input" in result
        assert result["ingestion_metadata"]["source_type"] == "structured_json"
        assert result["ingestion_metadata"]["confidence_score"] == 1.0
    
    def test_json_with_existing_needs_user_input(self):
        """Test that existing needs_user_input is preserved."""
        json_with_needs = SAMPLE_JSON.copy()
        json_with_needs["needs_user_input"] = ["team_background"]
        result = ingest_json(json_with_needs)
        
        assert result["needs_user_input"] == ["team_background"]

class TestValidateAndSave:
    def test_valid_draft_passes_validation(self, tmp_path):
        """Test that a valid draft passes schema validation."""
        valid_draft = {
            "project_name": "Test Project",
            "description": "A test project description",
            "stage": "seed",
            "geography": {"country": "US"},
            "domain": "SaaS",
            "needs_user_input": []
        }
        
        # Temporarily change DRAFTS_DIR for testing
        from runtime import ingest
        original_drafts_dir = ingest.DRAFTS_DIR
        ingest.DRAFTS_DIR = tmp_path
        
        try:
            success = validate_and_save(valid_draft, "test_draft.yaml")
            assert success is True
            
            output_file = tmp_path / "test_draft.yaml"
            assert output_file.exists()
            
            with open(output_file, 'r') as f:
                saved_data = yaml.safe_load(f)
            assert saved_data["project_name"] == "Test Project"
        finally:
            ingest.DRAFTS_DIR = original_drafts_dir
    
    def test_invalid_draft_fails_validation(self, tmp_path):
        """Test that an invalid draft fails schema validation."""
        invalid_draft = {
            "project_name": "T",  # Too short (minLength: 2)
            "description": "Short",  # Too short (minLength: 10)
            "stage": "invalid_stage",  # Not in enum
            "geography": {"country": "US"},
            "domain": "SaaS",
            "needs_user_input": []
        }
        
        from runtime import ingest
        original_drafts_dir = ingest.DRAFTS_DIR
        ingest.DRAFTS_DIR = tmp_path
        
        try:
            success = validate_and_save(invalid_draft, "invalid_draft.yaml")
            assert success is False
        finally:
            ingest.DRAFTS_DIR = original_drafts_dir

class TestSchemaLoading:
    def test_schema_loads_successfully(self):
        """Test that the schema file loads without errors."""
        schema = load_schema()
        assert schema is not None
        assert "properties" in schema
        assert "project_name" in schema["properties"]
        assert "needs_user_input" in schema["properties"]

class TestEndToEnd:
    def test_full_pipeline_raw_text(self, tmp_path):
        """Test full pipeline: raw text -> ingest -> validate -> save."""
        from runtime import ingest
        original_drafts_dir = ingest.DRAFTS_DIR
        ingest.DRAFTS_DIR = tmp_path
        
        try:
            data = ingest_raw_text(SAMPLE_RAW_TEXT)
            success = validate_and_save(data, "e2e_test.yaml")
            
            assert success is True
            output_file = tmp_path / "e2e_test.yaml"
            assert output_file.exists()
        finally:
            ingest.DRAFTS_DIR = original_drafts_dir
    
    def test_full_pipeline_json(self, tmp_path):
        """Test full pipeline: JSON -> ingest -> validate -> save."""
        from runtime import ingest
        original_drafts_dir = ingest.DRAFTS_DIR
        ingest.DRAFTS_DIR = tmp_path
        
        try:
            data = ingest_json(SAMPLE_JSON.copy())
            success = validate_and_save(data, "e2e_json_test.yaml")
            
            assert success is True
            output_file = tmp_path / "e2e_json_test.yaml"
            assert output_file.exists()
        finally:
            ingest.DRAFTS_DIR = original_drafts_dir
