# Phase 2 Plan: Product Features & Bootstrap SaaS Preparation

**Target Version:** 0.2.0  
**Focus:** Transform stable deterministic engine into a low-friction, user-facing product.  
**Guiding Principle:** Maintain "Zero Hallucination" and "Evidence-Gated" policies while reducing user friction.

## 🎯 Priority 1: Ingestion Layer (Снижение трения ввода)
*Цель: Пользователь вставляет сырой текст питча или грязный JSON, а система возвращает валидный `project_draft.yaml`.*
- [ ] **Schema Design:** Создать `schemas/project_draft.schema.yaml`. Разрешить значения `unknown` и явный статус `needs_user_input` для отсутствующих критических полей (stage, geography, amount).
- [ ] **Core Logic:** Реализовать `runtime/ingest.py`.
  - Поддержка режимов: `raw_text` (с LLM-экстракцией + confidence score), `structured_json` (прямой маппинг), `mixed`.
  - Строгая пост-валидация результата через `jsonschema` перед сохранением.
- [ ] **Testing:** Добавить 5 regression fixtures в `tests/cases/ingestion/` (чистый JSON, сырой текст, смесь, мусорный ввод, пустой ввод).
- [ ] **Docs:** Обновить `README.md` секцией "Analyze from raw text".

## 🎯 Priority 2: Human-Readable Reporting & Export (UX отчетов)
*Цель: Аналитик получает готовый артефакт, который можно прикрепить к инвест-меморандуму.*
- [ ] **CLI Enhancement:** Модернизировать `runtime/render_report.py` с использованием библиотеки `rich` для цветного, структурированного вывода в терминал (Match Score, Decision Trace, Stop Conditions).
- [ ] **Export Formats:** Добавить флаг `--format pdf` (через легковесный рендеринг Markdown в PDF, например, `markdown2` + `pdfkit` или аналог, либо строгий Markdown с шаблоном для экспорта).
- [ ] **Trace Visibility:** Гарантировать, что `decision_trace` и ссылки на `official_source` визуально выделены в отчете как первичные артефакты доверия.

## 🎯 Priority 3: Integration Layer (MCP / API)
*Цель: Бесшовный вызов движка из Cursor, Claude Desktop или внутренней CRM.*
- [ ] **API Skeleton:** Создать `runtime/api_server.py` (FastAPI) или `runtime/mcp_server.py` (Model Context Protocol).
- [ ] **Endpoints/Tools:** 
  - `ingest_and_analyze(raw_input: str) -> dict`
  - `verify_route(project: dict, route_id: str, live: bool) -> dict`
- [ ] **Security Stub:** Добавить базовую проверку API-ключа (через ENV variable) для подготовки к B2B SaaS монетизации.
- [ ] **Testing:** Интеграционные тесты для API endpoints.

## 🎯 Priority 4: Automated Live-Verification (Опционально, но желательно)
*Цель: Снижение ручного вмешательства при проверке статусов.*
- [ ] **Runner Integration:** Добавить флаг `--auto-verify` в `runtime/runner.py`.
- [ ] **Logic:** Если у карты `needs_verification: true`, раннер автоматически вызывает `health_check` для `application_endpoint`. Если статус `HEALTHY`, флаг снимается, и решение может быть повышено до `NOW` или `NEXT`.
- [ ] **Safety:** Гарантировать, что `UNREACHABLE` или `403/429` (известные ограничения) не ломают процесс, а корректно логируются как `VERIFY_ACCESS_PATH`.

## 📋 Definition of Done for Phase 2
1. Все 4 приоритета реализованы и покрыты тестами (pytest).
2. CI/CD (GitHub Actions) полностью зеленый для новых модулей.
3. Проведен пилотный прогон на 3 реальных внешних проектах (external-local), собран human feedback.
4. Версия обновлена до `0.2.0`.