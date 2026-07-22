# Funding Intelligence

**v0.1 — deterministic opportunity routing and verification**

Внутренняя capability для выбора наиболее вероятного маршрута получения ресурса. Это не SaaS, не интерфейс и не автоматическая система подачи заявок.

## Вход

- описание проекта и продукта;
- сектор, стадия и география;
- сайт, GitHub, demo и deployment, если они подтверждены;
- пользователи, пилоты, выручка и метрики;
- цель: деньги, кредиты, партнёрства или акселератор;
- `evidence/<project>/` с дополнительными фактами.

Неизвестные данные передаются как `unknown`. Агент не заполняет их предположениями.

## Выход

Система разделяет независимые состояния:

- статус программы;
- доступность endpoint;
- fit проекта;
- готовность проекта;
- требуемые доказательства;
- следующий шаг и stop condition.

Основные решения v0.1:

- `NOW` — можно выполнять действие сейчас;
- `VERIFY_FIRST` — сначала подтвердить маршрут;
- `COMPLETE_ELIGIBILITY_DATA` — сначала заполнить eligibility-данные;
- `VERIFY_ACCESS_PATH` — сначала найти фактический путь входа;
- `BUILD_FIRST` — сначала усилить продукт или доказательства;
- `BUILD_NVIDIA_USE_CASE` — сначала доказать нативный NVIDIA/GPU use case;
- `DO_NOT_APPLY` / `NO_ACTIONABLE_ENDPOINT` — не тратить время.

## Что система не обещает

- принятие заявки или получение финансирования;
- актуальный статус без проверенного официального источника;
- превращение cloud credits, BD или акселератора в cash grant;
- автоматическую подачу, юридическую или инвестиционную рекомендацию;
- достоверность фактов, которых нет во входных данных.

## Команды

Проверка всей базовой тестовой матрицы:

```bash
python3 runtime/runner.py --check-all
```

Проверка пяти AI-маршрутов для Hlinor по source snapshot:

```bash
python3 runtime/verify_route.py \
  tests/live/hlinor.yaml \
  --all-ai \
  --evidence-dir evidence/hlinor \
  --verified-at 2026-07-22
```

Для HTTP transport probe добавляется `--live`. Сетевая недоступность при наличии проверенного официального источника не переименовывается в `CLOSED`.

## Hlinor: v0.1 snapshot

Для Hlinor текущая система маршрутизирует:

- AWS Activate — `COMPLETE_ELIGIBILITY_DATA`;
- Microsoft for Startups — `COMPLETE_ELIGIBILITY_DATA`;
- NVIDIA Inception — `BUILD_NVIDIA_USE_CASE`;
- OpenAI for Startups — `VERIFY_ACCESS_PATH`;
- Y Combinator — `BUILD_FIRST`.

Это не пять обещаний подачи. AWS Activate и Microsoft for Startups в данном наборе описываются прежде всего как startup/cloud-credit и support-маршруты, NVIDIA — как startup support с требованием релевантного GPU/NVIDIA use case, OpenAI — как маршрут с отдельно проверяемым access path, YC — как accelerator/investment route. Официальные точки проверки карточек: [AWS Activate](https://aws.amazon.com/startups/credits/), [Microsoft for Startups](https://learn.microsoft.com/en-us/startups/microsoft-for-startups/overview), [NVIDIA Inception](https://www.nvidia.com/en-us/startups/), [OpenAI for Startups](https://openai.com/business/why-openai/startups/), [Y Combinator Apply](https://www.ycombinator.com/apply).

Читаемый результат сохранён в [reports/hlinor.md](/Users/andrejananev/Documents/funding-intelligence/reports/hlinor.md), а исходные подтверждения и пробелы — в [evidence/hlinor/](/Users/andrejananev/Documents/funding-intelligence/evidence/hlinor/).

## Граница следующего теста

`tests/cases/web3.yaml` используется только как вертикальный regression fixture. Это не внешний клиентский проект. Для production-like внешнего теста нужны три реальных входных профиля и человеческая оценка отчётов; до их появления база и verifier не расширяются.
