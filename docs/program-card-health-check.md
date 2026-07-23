# Program-card health check

`runtime/health_check.py` is a read-only transport check for the official source recorded in each program card.

It checks:

- HTTP `2xx` and followed redirects as `HEALTHY`;
- `404` as `NOT_FOUND`;
- `5xx` as `SERVER_ERROR`;
- other `4xx` responses as `HTTP_ERROR`;
- DNS, timeout, TLS, and other transport failures as `UNREACHABLE`.

`UNREACHABLE` is never interpreted as `CLOSED`. The script does not edit YAML cards, change `status.state`, or rewrite `last_checked`.

Some official sites deliberately rate-limit or block GitHub-hosted traffic. After a human verifies that an official route is still valid, a card may record `status.health_check.known_access_http_statuses` with only `403` or `429`. The report preserves the raw HTTP result and records the known access constraint, but does not reopen the `stale-data` issue for that already-reviewed condition. A `404`, `5xx`, missing source, or unreviewed `4xx` remains actionable.

Run locally without changing repository files:

```bash
python3 runtime/health_check.py \
  --output /tmp/health-check-report.json \
  --summary /tmp/health-check-summary.md
```

Run the deterministic self-test:

```bash
python3 runtime/health_check.py --self-test
```

The scheduled GitHub Action runs weekly and manually. It uploads the report as an artifact and creates or updates one `stale-data` issue for actionable HTTP/source findings. Human review is required before changing a knowledge card.
