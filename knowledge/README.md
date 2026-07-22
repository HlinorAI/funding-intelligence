# Funding Intelligence knowledge base

Источник первой версии: `Global_Funding_Ecosystem_BD_Handbook_2026_Expanded_v3_Collider_RU.md`, статусная проверка источника — 20.07.2026.

Эта папка содержит только операционные данные, которые нужны агенту для routing:

- `programs/*.yaml` — одна карточка на программу, механизм или BD-маршрут;
- `packs/<vertical>/programs/*.yaml` — вертикальные opportunity packs, которые подключаются только при совпадении structured facts;
- `packs/<vertical>/rules/` — вертикальные fit и stage rules;
- `rules/` — общие правила классификации, scoring и остановки;
- `templates/` — заготовки рабочих документов.

## Схема карточки

Обязательные поля:

- `id`, `name`, `ecosystem`;
- `mechanism` — один или несколько типов: `proposal_grant`, `retro`, `incentive`, `accelerator`, `investment`, `subsidy`, `bd`;
- `status.state` — `OPEN`, `ROLLING`, `ACTIVE`, `CLOSED`, `UPCOMING`, `VERIFY`, `WATCH`, `HOLD`, `BD-ONLY`;
- `status.last_checked`, `status.needs_verification`, `status.official_source`;
- `best_fit`, `bad_fit`, `required_evidence`;
- `failure_modes`, `next_action`, `stop_condition`.

Даты и статусы в этой базе не считаются вечными. Перед реальным apply агент обязан открыть официальный источник и actual intake endpoint.
