#!/usr/bin/env python3
"""Scan official pages for application-endpoint candidates without mutating cards.

Most knowledge cards are intentionally source-only: a route stays
non-actionable until a route-specific intake is verified. This scanner
fetches the official source recorded on each such card, extracts anchors,
and surfaces candidate application/intake endpoints as a human-review queue.

Candidates are leads only. A card's `verification.application_url` may be
recorded exclusively by a human who opened and confirmed the route, per the
status-verification rules. A page with no candidate link is not evidence that
no endpoint exists, and a transport failure is not evidence of anything
except transport.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit
from urllib.request import Request, urlopen

import yaml

ROOT = Path(__file__).resolve().parents[1]
PROGRAM_DIR = ROOT / "knowledge" / "programs"
PACK_DIR = ROOT / "knowledge" / "packs"
DEFAULT_OUTPUT = ROOT / "reports" / "endpoint-candidates.yaml"

STRONG_TOKENS = {
    "apply",
    "application",
    "applications",
    "nominate",
    "nomination",
    "submit",
    "intake",
    "onboard",
    "onboarding",
}
FORM_HOSTS = (
    "submittable.com",
    "tally.so",
    "typeform.com",
    "airtable.com",
    "forms.gle",
    "docs.google.com",
)
EXCLUDED_HOSTS = (
    "twitter.com",
    "x.com",
    "linkedin.com",
    "facebook.com",
    "instagram.com",
    "youtube.com",
    "youtu.be",
    "medium.com",
    "reddit.com",
    "discord.com",
    "discord.gg",
    "t.me",
    "telegram.me",
)
KIND_RANK = {"apply_page": 0, "portal": 0, "hosted_form": 1}


class AnchorCollector(HTMLParser):
    """Collect anchor href/text pairs from an HTML document."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[tuple[str, str]] = []
        self._href: str | None = None
        self._text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a" or self._href is not None:
            return
        for name, value in attrs:
            if name == "href" and value:
                self._href = value
                self._text = []
                break

    def handle_data(self, data: str) -> None:
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._href is not None:
            self.anchors.append((self._href, " ".join("".join(self._text).split())))
            self._href = None
            self._text = []


def extract_anchors(html_text: str, base_url: str) -> list[tuple[str, str]]:
    collector = AnchorCollector()
    try:
        collector.feed(html_text)
        collector.close()
    except Exception:
        # Malformed HTML still yields whatever anchors were parsed.
        pass
    resolved: list[tuple[str, str]] = []
    for href, text in collector.anchors:
        absolute = urljoin(base_url, href.strip())
        resolved.append((absolute, text))
    return resolved


def host_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower()


def tokenize(value: str) -> set[str]:
    normalized: set[str] = set()
    for chunk in value.lower().replace("-", " ").replace("_", " ").replace("/", " ").replace("?", " ").replace("=", " ").split():
        normalized.update(part for part in chunk.split(".") if part)
    return normalized


def classify_link(url: str, text: str, source_url: str) -> dict[str, Any] | None:
    """Return a candidate record when a link plausibly leads to an intake."""

    split = urlsplit(url)
    if split.scheme not in {"http", "https"}:
        return None
    host = (split.hostname or "").lower()
    if not host:
        return None
    if any(host == excluded or host.endswith("." + excluded) for excluded in EXCLUDED_HOSTS):
        return None
    clean_source = source_url.split("#")[0].rstrip("/")
    if url.split("#")[0].rstrip("/") == clean_source:
        return None
    tokens = tokenize(split.path + " " + (split.query or "") + " " + text)
    hosted_form = any(host == form_host or host.endswith("." + form_host) for form_host in FORM_HOSTS)
    strong = STRONG_TOKENS & tokens
    if hosted_form:
        kind = "hosted_form"
        reason = "link points to a hosted form provider"
    elif strong:
        if "portal" in tokens:
            kind = "portal"
        else:
            kind = "apply_page"
        reason = f"intake keyword in link: {', '.join(sorted(strong))}"
    else:
        return None
    source_host = host_of(source_url)
    same_host = bool(source_host) and (host == source_host or host.endswith("." + source_host))
    return {
        "url": url,
        "kind": kind,
        "anchor_text": text or None,
        "same_host": same_host,
        "reason": reason,
    }


def candidate_links(html_text: str, source_url: str) -> list[dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for url, text in extract_anchors(html_text, source_url):
        record = classify_link(url, text, source_url)
        if record and record["url"] not in candidates:
            candidates[record["url"]] = record
    return sorted(
        candidates.values(),
        key=lambda item: (not item["same_host"], KIND_RANK.get(item["kind"], 2), item["url"]),
    )


def fetch_page(url: str, timeout: int = 15) -> dict[str, Any]:
    request = Request(
        url,
        headers={"User-Agent": "funding-intelligence-endpoint-scan/1.0"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read(2_000_000)
            charset = response.headers.get_content_charset() or "utf-8"
            return {
                "transport_state": "FETCHED",
                "http_status": response.status,
                "html": body.decode(charset, errors="replace"),
                "error": None,
            }
    except HTTPError as error:
        return {"transport_state": "HTTP_ERROR", "http_status": error.code, "html": None, "error": str(error)}
    except (URLError, TimeoutError, OSError) as error:
        return {"transport_state": "UNREACHABLE", "http_status": None, "html": None, "error": str(error)}


def load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as stream:
        value = yaml.safe_load(stream) or {}
    if not isinstance(value, dict):
        raise ValueError(f"Expected a YAML mapping in {path}")
    return value


def card_paths() -> list[Path]:
    paths = sorted(PROGRAM_DIR.glob("*.yaml"))
    paths.extend(sorted(PACK_DIR.glob("*/programs/*.yaml")))
    return paths


def scan_card(card: dict[str, Any], path: Path, timeout: int = 15) -> dict[str, Any]:
    status = card.get("status") or {}
    verification = card.get("verification") or {}
    record: dict[str, Any] = {
        "program_id": card.get("id"),
        "program": card.get("name"),
        "source": status.get("official_source"),
        "card_path": str(path.relative_to(ROOT)),
    }
    if verification.get("application_url"):
        record.update({"transport_state": "SKIPPED_HAS_ENDPOINT", "http_status": None, "candidates": [], "error": None})
        return record
    source = status.get("official_source")
    if not source:
        record.update({"transport_state": "MISSING_SOURCE", "http_status": None, "candidates": [], "error": "status.official_source is missing"})
        return record
    fetch = fetch_page(str(source), timeout)
    record.update({"transport_state": fetch["transport_state"], "http_status": fetch["http_status"], "error": fetch["error"]})
    if fetch["transport_state"] == "FETCHED" and fetch["html"] is not None:
        record["candidates"] = candidate_links(fetch["html"], str(source))
    else:
        record["candidates"] = []
    return record


def report_from_cards(cards: list[dict[str, Any]], scanned_at: str | None = None) -> dict[str, Any]:
    cards.sort(key=lambda item: str(item.get("program_id")))
    scanned = [item for item in cards if item["transport_state"] == "FETCHED"]
    with_candidates = [item for item in scanned if item.get("candidates")]
    return {
        "endpoint_scan_version": 1,
        "scanned_at": scanned_at or dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "card_count": len(cards),
        "summary": {
            "scanned": len(scanned),
            "skipped_has_endpoint": sum(item["transport_state"] == "SKIPPED_HAS_ENDPOINT" for item in cards),
            "transport_failed": sum(item["transport_state"] in {"UNREACHABLE", "HTTP_ERROR"} for item in cards),
            "missing_source": sum(item["transport_state"] == "MISSING_SOURCE" for item in cards),
            "with_candidates": len(with_candidates),
            "candidate_count": sum(len(item.get("candidates") or []) for item in cards),
        },
        "cards": cards,
        "note": (
            "Candidates are unverified leads for human review. A human must open each URL and "
            "confirm a route-specific intake before recording verification.application_url on the "
            "card. No candidate and a transport failure are both not evidence about endpoints."
        ),
    }


def self_test() -> int:
    html = """
    <html><body>
      <a href="/apply">Apply now</a>
      <a href="https://forms.other.org/type/xyz">Submission form</a>
      <a href="/about">About</a>
      <a href="mailto:team@example.org">Mail us</a>
      <a href="https://twitter.com/example">Twitter</a>
      <a href="#apply">Jump</a>
      <a href="https://portal.example.org/login">Grant application portal</a>
    </body></html>
    """
    candidates = candidate_links(html, "https://example.org/program")
    urls = [item["url"] for item in candidates]
    if "https://example.org/apply" not in urls:
        print(f"ERROR: relative apply link was not resolved: {urls}", file=sys.stderr)
        return 1
    if "https://portal.example.org/login" not in urls:
        print(f"ERROR: portal link with anchor text was not classified: {urls}", file=sys.stderr)
        return 1
    if any(host_of(url) == "twitter.com" for url in urls):
        print(f"ERROR: social link was not excluded: {urls}", file=sys.stderr)
        return 1
    if any(url.startswith("mailto:") for url in urls):
        print(f"ERROR: mailto link was not excluded: {urls}", file=sys.stderr)
        return 1
    kinds = {item["url"]: item["kind"] for item in candidates}
    if kinds.get("https://example.org/apply") != "apply_page":
        print(f"ERROR: apply link misclassified: {kinds}", file=sys.stderr)
        return 1
    if classify_link("https://example.org/about", "About", "https://example.org/program") is not None:
        print("ERROR: plain about link produced a candidate", file=sys.stderr)
        return 1
    if classify_link("https://example.org/", "Home", "https://example.org/") is not None:
        print("ERROR: self link produced a candidate", file=sys.stderr)
        return 1
    report = report_from_cards(
        [
            {"program_id": "synthetic-a", "transport_state": "FETCHED", "candidates": [{"url": "https://a.org/apply", "kind": "apply_page"}]},
            {"program_id": "synthetic-b", "transport_state": "UNREACHABLE", "http_status": None, "candidates": []},
            {"program_id": "synthetic-c", "transport_state": "SKIPPED_HAS_ENDPOINT", "candidates": []},
        ],
        scanned_at="2026-09-12T00:00:00+00:00",
    )
    if report["summary"]["with_candidates"] != 1 or report["summary"]["transport_failed"] != 1 or report["summary"]["skipped_has_endpoint"] != 1:
        print(f"ERROR: endpoint-scan summary miscounted: {report['summary']}", file=sys.stderr)
        return 1
    try:
        json.dumps(report)
    except TypeError as error:
        print(f"ERROR: endpoint-scan report is not JSON serializable: {error}", file=sys.stderr)
        return 1
    print("OK: endpoint-scan self-test")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", action="append", help="limit the scan to card ids; repeatable")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="write the review queue (kept outside Git by default)")
    parser.add_argument("--timeout", type=int, default=15)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return self_test()

    cards: list[dict[str, Any]] = []
    for path in card_paths():
        card = load_yaml(path)
        if args.only and str(card.get("id")) not in set(args.only):
            continue
        cards.append(scan_card(card, path, args.timeout))
    report = report_from_cards(cards)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")
    summary = report["summary"]
    print(
        f"OK: scanned {summary['scanned']} source-only pages; "
        f"{summary['candidate_count']} candidates across {summary['with_candidates']} cards; "
        f"{summary['transport_failed']} transport failures; queue written to {args.output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
