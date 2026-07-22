# Funding route scoring

## Hard gates

1. `CLOSED` не может попасть в `NOW` или получить совет `APPLY`.
2. `VERIFY` и `WATCH` требуют проверки official source и actual intake endpoint.
3. Механизм обязан совпадать с ask: retro не финансирует идею до shipping, incentive не является runway, investment не является grant.
4. Для chain/ecosystem route нужен конкретный native value: deployment, architecture, users, integrations или public-good artifact.
5. Если обязательное evidence отсутствует, итоговая рекомендация — `BUILD FIRST`, а не speculative application.
6. Если проект не указывает target/native ecosystem, chain-specific card получает `DO_NOT_APPLY`, а не «слабый fit».

## Base score — 100

- `strategic_fit`: 25
- `technical_fit`: 20
- `evidence`: 20
- `mechanism_fit`: 15
- `execution_readiness`: 10
- `access`: 10

## Penalties

- `-25`: закрытая программа предложена как apply;
- `-20`: generic multichain port без native thesis;
- `-15`: pre-funding ask в retro/incentive route;
- `-15`: нет shipped product там, где он обязателен;
- `-10`: бюджет — только payroll без ecosystem outcome;
- `-10`: нет измеримых milestones;
- `-10`: обещаны users/TVL без distribution plan.

## Interpretation

- `80–100`: `NOW`;
- `65–79`: `NOW` или `NEXT` после закрытия gaps;
- `50–64`: `LATER` / relationship building;
- `<50`: `DO NOT APPLY`.

## Output contract

Для каждого выбранного маршрута агент указывает:

- fit и score;
- точный mechanism и status;
- почему подходит;
- missing proof;
- следующий шаг;
- stop condition.
