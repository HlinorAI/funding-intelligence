# 🗺️ Project Roadmap & Status

**Last updated:** July 24, 2026  
**Current Phase:** V1 Stabilization & Core Feature Expansion

##  Architectural Philosophy
This project deliberately moves away from typical "RAG-chats" that suffer from hallucinations. 
**Core Principles:**
- **Deterministic & Evidence-Gated:** The core engine (`runtime`) does not use LLMs for decision-making. Matching works strictly via YAML cards and JSON Schema.
- **Zero Hallucination Policy:** Every claim must have a `decision_trace` and a link to a primary source (`official_source`).
- **Immutable Knowledge:** Automation (scripts, CI) **never** overwrites knowledge YAML cards. It only signals issues.
- **Local-First Core:** Minimizing external LLM API calls. The core runs locally on Python; heavy models are used only on the periphery (drafting).

## ✅ Recent Achievements (v0.1.3)

### Localization & Audit
- Migrated all documentation to English; removed legacy Russian localization.
- Full audit of both repositories for Cyrillic characters. Result: **0 matches**.

### Automated Health-Check Layer
- Created `runtime/health_check.py`: deterministic URL status checking (`HEALTHY`, `NOT_FOUND`, `SERVER_ERROR`, `HTTP_ERROR`, `UNREACHABLE`).
- Created `.github/workflows/health-check.yml`: weekly runs, aggregating issues into a single `stale-data` GitHub Issue, saving reports as artifacts.
- Created `runtime/health_report.py`: CLI utility for beautiful, color-coded terminal output (requires `rich`).

### CI/CD Stabilization
- Fixed `validate_schemas.py` private path tracking errors.
- Moved public templates to `docs/` to respect the privacy of the `reports/` directory.
- All checks passing: health-check self-test, benchmarks, regression cases, program cards, project fixtures, Python compilation, YAML parsing.

##  Next Steps (V1 Priorities)

### Priority 1: Ingestion Layer (Reducing User Friction)
- **Task:** Create `runtime/ingest.py`.
- **Logic:** Accepts raw JSON (from external LLM/parsers) → strictly validates against `schemas/project_schema.json` → outputs a safe `project_draft.yaml`.
- **Value:** Founders don't need to write YAML manually. They paste pitch text and get a valid draft for manual review.

### Priority 2: Human-Readable Reporting & Export
- **Task:** Enhance matching result output.
- **Logic:** Implement `runtime/health_report.py` (CLI with `rich`) and add generation of clean Markdown/PDF match reports (Match Score + Decision Trace).
- **Value:** Analysts get a ready-made artifact to attach to investment memos or send to clients.

### Priority 3: Integration Layer (MCP / API)
- **Task:** Wrap the engine in a Model Context Protocol (MCP) server or simple REST API.
- **Logic:** Allow users to invoke matching and validation functions directly from Cursor, Claude Desktop, or their internal CRM.
- **Value:** Seamless integration into existing workflows without learning a new UI.

## 📌 Technical Notes for Contributors
- **Dependencies:** Ensure `rich`, `jsonschema`, and `pyyaml` are added to `requirements.txt` / `pyproject.toml`.
- **Git Workflow:** Always use `git pull --rebase origin main` to avoid messy merge commits.
- **Private Paths:** The `reports/` folder is blocked in `runtime/validate_schemas.py`. All public templates must live in `docs/`.