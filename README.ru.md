# Funding Intelligence

[English](README.md)

Детерминированный evidence-gated engine для маршрутизации стартапов и технических проектов к funding, акселераторам, cloud credits, investment, incentives и business-development возможностям.

## Зачем это нужно

Обычные LLM-workflows часто выдают длинные списки правдоподобных программ. Funding Intelligence предназначен для меньшего числа, но более защищённых решений:

- нерелевантные маршруты отбрасываются до рекомендации;
- `unknown` не считается доказательством;
- transport failure не считается `CLOSED`;
- failed hard gate нельзя поднять в `NOW` красивым текстом или высоким raw score;
- каждая рекомендация содержит причину, следующий шаг и stop condition.

Это внутренняя capability и open-source engine prototype, а не marketplace финансирования и не сервис подачи заявок.

## Что делает система

- классифицирует стадию проекта, сектор, цели и mechanism fit;
- сопоставляет проекты с локальными opportunity cards и vertical packs;
- считает детерминированный score и penalties;
- пропускает рекомендации только при наличии structured evidence;
- независимо хранит program status, endpoint status, endpoint transport, project fit и project readiness;
- выдаёт route-specific decisions;
- сохраняет объяснимый `decision_trace` в machine report.

## Чего система не делает

- не гарантирует funding, acceptance или investment;
- не подаёт заявки автоматически;
- не считает credits, incentives, accelerator access или BD value cash grants;
- не придумывает отсутствующие факты и не превращает claims в evidence;
- не считает датированный snapshot вечной истиной;
- не заменяет юридическую, финансовую, compliance или investment консультацию.

## Типы ресурсов

- `proposal_grant` — финансирование по заявке с review, milestones и reporting;
- `retro` — сначала shipping, затем reward за доказанный impact;
- `incentive` — rewards за activity, liquidity или network outcomes;
- `accelerator` / `investment` — отбор, капитал, mentorship или investor access;
- `bd` — стратегические partnerships, pilots, integrations и distribution;
- `cloud_credits` / `startup_support` — инфраструктурные кредиты, technical support и founder resources.

## Примеры решений

- `COMPLETE_ELIGIBILITY_DATA` — маршрут может подходить, но не хватает данных о компании или аккаунте;
- `VERIFY_ACCESS_PATH` — категория возможности существует, но фактический путь к benefit не установлен;
- `BUILD_FIRST` — до подачи нужно создать product, traction или application proof;
- `BUILD_NVIDIA_USE_CASE` — у проекта нет достоверного native NVIDIA/GPU use case;
- `DO_NOT_APPLY` — не совпадают mechanism, stage, ecosystem или project fit;
- `NO_ACTIONABLE_ENDPOINT` — не найден рабочий intake endpoint.

## Структура репозитория

```text
agent/       operator policy для Funding Intelligence Agent
knowledge/   program cards, vertical packs, rules и templates
runtime/     deterministic runner, route verifier и schema validator
schemas/     formal schemas для project, program card, route и report
tests/       публичные synthetic cases и expected decisions
examples/    публичные sample report artifacts
history/     документация для human-maintained application history
```

Private evidence, live project fixtures, operational history и generated reports исключены через `.gitignore`.

## Установка

Требуются Python 3 и PyYAML:

```bash
python3 -m pip install -r requirements.txt
```

Для локального runner не нужны web service или database.

## Использование

Запуск deterministic evaluator на публичном synthetic AI fixture:

```bash
python3 runtime/runner.py tests/cases/ai_startup.yaml --output /tmp/example-ai-report.yaml
```

Запуск route verification на публичном synthetic Web3 fixture. Этот пример намеренно использует card без verified source snapshot и демонстрирует путь `VERIFY_FIRST`:

```bash
python3 runtime/verify_route.py \
  tests/cases/web3.yaml \
  --route base-funding-ladder \
  --output /tmp/base-route-verification.yaml
```

Добавляй `--live` только если нужен HTTP transport probe. Ошибка probe сама по себе не означает, что программа закрыта.

## Пример результата

Публичный fixture `tests/cases/ai_startup.yaml` описывает `Example AI Infrastructure Startup`. Его текущий expected contract:

```yaml
project: Example AI Infrastructure Startup
decision: VERIFY_FIRST
gate_passed: false
must_include: microsoft-for-startups
```

Компактный sample artifact находится в [examples/sample_report.yaml](examples/sample_report.yaml).

## Покрытие knowledge base

В репозитории сейчас есть:

- AI opportunity pack со startup programs, cloud/API credits, technical support, enterprise access и accelerator/investment routes;
- Web3 и ecosystem cards для выбранных chains, infrastructure, incentives, retro routes и BD paths;
- общие правила mechanism, scoring, rejection, status verification и stop conditions.

Это намеренно ограниченный knowledge snapshot. Это не comprehensive global database; отсутствие card для какого-либо маршрута не доказывает отсутствие других возможностей.

## Модель проверки статуса

Route verification разделяет состояния:

- `program_status` — записанный статус программы с source и датой проверки;
- `endpoint_status` — известен ли actionable endpoint;
- endpoint transport — смог ли runtime достучаться до URL во время live probe;
- `project_fit` — насколько structured project facts совпадают с route;
- `project_readiness` — закрыты ли evidence и eligibility gates;
- итоговый `decision` — route-specific действие, выданное policy.

Если official source уже проверен, но последующий HTTP probe не может достичь endpoint, verifier сохраняет source-backed status и записывает transport как `UNREACHABLE`. Network problem не превращается молча в `CLOSED`.

## Тесты

Запуск публичной regression suite:

```bash
python3 runtime/runner.py --check-all
python3 -m py_compile runtime/runner.py runtime/verify_route.py
```

Полный public contract validator:

```bash
python3 runtime/validate_schemas.py
```

Валидатор проверяет публичные YAML, project fixtures, структуру program cards, generated runner reports, public route-verification record, issue forms, private-path exclusions и credential-like patterns. GitHub Actions запускает эти проверки на каждом push и pull request.

Проверка публичных YAML:

```bash
python3 - <<'PY'
from pathlib import Path
import yaml

files = sorted(Path(".").rglob("*.yaml"))
for path in files:
    if any(part in {".git", ".venv"} for part in path.parts):
        continue
    with path.open("r", encoding="utf-8") as f:
        yaml.safe_load(f)
print(f"yaml_ok {len(files)}")
PY
```

## Contributing

При добавлении program card:

1. укажи mechanism и resource type;
2. добавь official source и snapshot date;
3. опиши fit, bad fit, required evidence, next action и stop condition;
4. не используй aggregator как единственный источник проверки;
5. добавь или обнови публичный synthetic fixture и expected decision;
6. запусти regression и YAML checks.

Не добавляй реальные project evidence, credentials, contacts, внутренние метрики или generated private reports.

Правила contribution и состояние проекта описаны в [CONTRIBUTING.md](CONTRIBUTING.md), [CHANGELOG.md](CHANGELOG.md) и [WORKBOARD.md](WORKBOARD.md).

## Ограничения

- program cards являются snapshots и требуют повторной проверки перед реальной заявкой;
- scoring детерминирован, но зависит от качества structured facts и cards;
- текущее knowledge coverage выборочное;
- для claims, eligibility и execution decisions всё ещё нужен human review;
- репозиторий распространяется по [Apache License 2.0](LICENSE).

## Примеры официальных источников

AI pack сейчас ссылается на официальные страницы [AWS Activate](https://aws.amazon.com/startups/credits/), [Microsoft for Startups](https://learn.microsoft.com/en-us/startups/microsoft-for-startups/overview), [NVIDIA Inception](https://www.nvidia.com/en-us/startups/), [OpenAI for Startups](https://openai.com/business/why-openai/startups/) и [Y Combinator Apply](https://www.ycombinator.com/apply). Эти ссылки показывают расположение источников, но не гарантируют eligibility или acceptance.
