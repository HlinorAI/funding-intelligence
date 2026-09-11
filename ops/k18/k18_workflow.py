#!/usr/bin/env python3
"""Isolated K-18 public research and fail-closed qualification workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import ssl
import sys
import time
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus, urljoin
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

import yaml

try:  # Optional on the local workstation; installed on Hermes.
    from playwright.sync_api import sync_playwright
except Exception:  # pragma: no cover - exercised on the live host
    sync_playwright = None  # type: ignore[assignment]

try:
    import certifi

    HTTPS_CONTEXT = ssl.create_default_context(cafile=certifi.where())
except Exception:  # pragma: no cover - platform fallback
    HTTPS_CONTEXT = ssl.create_default_context()


ROOT = Path(__file__).resolve().parent
QUERIES_PATH = ROOT / "queries.yaml"
SOURCES_PATH = ROOT / "sources.yaml"
URL_RE = re.compile(r"^https?://[^\s]+$", re.IGNORECASE)
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
NEED_TERMS = ("grant", "funding", "funded", "credits", "accelerator", "pilot", "investment", "support")
TECH_TERMS = ("ai", "software", "developer", "api", "open source", "infrastructure", "data", "protocol", "platform")
ROLE_TERMS = ("founder", "ceo", "cto", "co-founder", "fundraising", "grants", "program")
EXCLUDED_TERMS = ("agency", "directory", "marketplace", "consultant", "course", "newsletter", "job board", "press release")
OPERATOR_TERMS = ("accelerator", "grant program", "cohort", "applications open", "application deadline", "pilot funding", "startup program", "pre-accelerator", "residency")
GITHUB_EXCLUDED_REPOS = {"sourcey/startup-credits", "sourcey/startup-perks", "jnd0/startup-perks"}
GITHUB_NOISE_TERMS = ("speaker needed", "authentication", "authantication", "profile management", "valuation challenges", "investors skepticism", "submission", "wallet empty", "base chain", "model-flagged", "download counts", "independent delegate", "secondary", "readme.md", "market oppurtunity")
CONTACT_LINK_TERMS = ("contact", "team", "leadership", "program", "partnership", "alliance", "grants", "accelerator")
GENERIC_EMAIL_PREFIXES = {"info", "hello", "contact", "support", "privacy", "legal", "press", "admin", "office", "communications", "program", "programs", "partnership", "partnerships", "alliance", "alliances", "grants", "general", "enquiries", "inquiry", "connect", "media", "team", "central", "east", "north", "south", "west", "tcentral", "teast", "tnorth", "tsouth", "twest"}
NON_OUTREACH_EMAIL_PREFIXES = {"privacy", "legal", "press", "support", "admin", "security", "abuse", "webmaster", "dpo", "postmaster"}


class SearchProviderBlocked(RuntimeError):
    """The public search endpoint requires an interactive human challenge."""


def clean(value: Any) -> str:
    return " ".join(str(value or "").split()).strip()


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected mapping")
    return value


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_url(value: str) -> str:
    return clean(value).rstrip("/")


def domain(value: str) -> str:
    text = normalize_url(value).lower()
    text = re.sub(r"^https?://", "", text)
    return text.split("/", 1)[0].removeprefix("www.")


def fetch_search(query: str, limit: int = 5, timeout: int = 15) -> list[dict[str, str]]:
    """Use the public DuckDuckGo HTML endpoint; never harvest contact details."""
    request = Request(
        f"https://html.duckduckgo.com/html/?q={quote_plus(query)}",
        headers={"User-Agent": "K18-Funding-Match-Research/1.0"},
    )
    with urlopen(request, timeout=timeout, context=HTTPS_CONTEXT) as response:
        status = getattr(response, "status", None)
        html = response.read().decode("utf-8", errors="replace")
    if status == 202 or "challenge-form" in html or "anomaly-modal" in html:
        raise SearchProviderBlocked("search provider returned an interactive human-verification challenge")
    results: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in re.findall(r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.I | re.S):
        url, title_html = raw
        url = unescape(url)
        title = clean(re.sub(r"<[^>]+>", " ", unescape(title_html)))
        if not URL_RE.fullmatch(url) or domain(url) in seen:
            continue
        seen.add(domain(url))
        results.append({"title": title, "url": url, "query": query})
        if len(results) >= limit:
            break
    return results


def _playwright_result_links(page: Any, selector: str, limit: int) -> list[dict[str, str]]:
    hits: list[dict[str, str]] = []
    seen: set[str] = set()
    for node in page.locator(selector).all():
        anchor = node.locator("xpath=ancestor::a[1]") if selector == "h3" else node
        title = clean(node.inner_text())
        url = clean(anchor.get_attribute("href"))
        normalized_domain = domain(url)
        if not title or not URL_RE.fullmatch(url) or not normalized_domain:
            continue
        if normalized_domain in seen or normalized_domain in {"google.com", "bing.com", "linkedin.com", "facebook.com"}:
            continue
        seen.add(normalized_domain)
        hits.append({"title": title, "url": url})
        if len(hits) >= limit:
            break
    return hits


def fetch_playwright_google(query: str, limit: int = 5, timeout: int = 30) -> list[dict[str, str]]:
    """Read Google result links through installed host-native Playwright Chromium."""
    if sync_playwright is None:
        raise RuntimeError("playwright is not installed")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=playwright.chromium.executable_path)
        try:
            page = browser.new_page(
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
            )
            response = page.goto(
                f"https://www.google.com/search?q={quote_plus(query)}&num={limit}&hl=en",
                wait_until="domcontentloaded",
                timeout=timeout * 1000,
            )
            page.wait_for_timeout(1500)
            body = page.locator("body").inner_text(timeout=10000).lower()
            if response is not None and response.status in {429, 403}:
                raise SearchProviderBlocked(f"Google returned HTTP {response.status}")
            if any(term in body for term in ("unusual traffic", "captcha", "sorry/index", "confirm you are not a robot")):
                raise SearchProviderBlocked("Google returned an interactive human-verification challenge")
            return [dict(hit, query=query) for hit in _playwright_result_links(page, "h3", limit)]
        finally:
            browser.close()


def fetch_playwright_bing(query: str, limit: int = 5, timeout: int = 30) -> list[dict[str, str]]:
    """Read Bing result links through installed host-native Playwright Chromium."""
    if sync_playwright is None:
        raise RuntimeError("playwright is not installed")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, executable_path=playwright.chromium.executable_path)
        try:
            page = browser.new_page(
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/131 Safari/537.36",
            )
            response = page.goto(
                f"https://www.bing.com/search?q={quote_plus(query)}&count={limit}",
                wait_until="domcontentloaded",
                timeout=timeout * 1000,
            )
            page.wait_for_timeout(1200)
            body = page.locator("body").inner_text(timeout=10000).lower()
            if response is not None and response.status in {429, 403}:
                raise SearchProviderBlocked(f"Bing returned HTTP {response.status}")
            if any(term in body for term in ("unusual traffic", "captcha", "confirm you are not a robot")):
                raise SearchProviderBlocked("Bing returned an interactive human-verification challenge")
            return [dict(hit, query=query) for hit in _playwright_result_links(page, "li.b_algo h2 a", limit)]
        finally:
            browser.close()


def visible_text(html: str) -> str:
    text = re.sub(r"<script\b[^>]*>.*?</script>|<style\b[^>]*>.*?</style>|<noscript\b[^>]*>.*?</noscript>", " ", html, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return clean(unescape(text))


def extract_contact_data(url: str, html: str) -> tuple[list[dict[str, str]], list[str]]:
    emails: list[dict[str, str]] = []
    seen_emails: set[str] = set()
    for value in sorted(set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", html, flags=re.I))):
        normalized = value.lower()
        if normalized in seen_emails:
            continue
        seen_emails.add(normalized)
        prefix = normalized.split("@", 1)[0].split("+", 1)[0]
        kind = "non_outreach_email" if prefix in NON_OUTREACH_EMAIL_PREFIXES else "public_general_email" if prefix in GENERIC_EMAIL_PREFIXES else "public_role_email"
        emails.append({"kind": kind, "value": normalized, "source_url": url})
    links: list[str] = []
    for href, label in re.findall(r'<a\b[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', html, flags=re.I | re.S):
        label_text = clean(re.sub(r"<[^>]+>", " ", unescape(label))).lower()
        href_text = unescape(href).lower()
        if any(term in f"{label_text} {href_text}" for term in CONTACT_LINK_TERMS):
            links.append(href)
    return emails, links


def contact_seed_urls(record: dict[str, Any]) -> list[str]:
    seeds: list[str] = []
    for key in ("contact_url", "source_url", "url"):
        value = normalize_url(clean(record.get(key)))
        if URL_RE.fullmatch(value) and domain(value) != "news.google.com":
            seeds.append(value)
    for value in record.get("sources", []) if isinstance(record.get("sources"), list) else []:
        value = normalize_url(clean(value))
        if URL_RE.fullmatch(value) and domain(value) != "news.google.com":
            seeds.append(value)
    unique: list[str] = []
    for value in seeds:
        if value not in unique:
            unique.append(value)
    return unique[:6]


def enrich_contact_record(record: dict[str, Any], timeout: int = 15) -> dict[str, Any]:
    existing_emails = record.get("public_emails", []) if isinstance(record.get("public_emails"), list) else []
    contact_candidates: list[dict[str, str]] = []
    for item in existing_emails:
        if isinstance(item, dict) and clean(item.get("value")):
            contact_candidates.append({"kind": clean(item.get("kind")) or "public_general_email", "value": clean(item.get("value")).lower(), "source_url": clean(item.get("source_url"))})
        elif isinstance(item, str) and EMAIL_RE.fullmatch(clean(item)):
            value = clean(item).lower()
            prefix = value.split("@", 1)[0].split("+", 1)[0]
            kind = "non_outreach_email" if prefix in NON_OUTREACH_EMAIL_PREFIXES else "public_general_email" if prefix in GENERIC_EMAIL_PREFIXES else "public_role_email"
            contact_candidates.append({"kind": kind, "value": value, "source_url": normalize_url(clean(record.get("url")))})
    checked_urls: list[str] = []
    queue = contact_seed_urls(record)
    base_domain = domain(queue[0]) if queue else ""
    while queue and len(checked_urls) < 6:
        url = queue.pop(0)
        if url in checked_urls or (base_domain and domain(url) != base_domain):
            continue
        checked_urls.append(url)
        try:
            request = Request(url, headers={"User-Agent": "K18-Funding-Intelligence/1.0"})
            with urlopen(request, timeout=timeout, context=HTTPS_CONTEXT) as response:
                html = response.read().decode("utf-8", errors="replace")
        except Exception:  # noqa: BLE001
            continue
        emails, links = extract_contact_data(url, html)
        for item in emails:
            if not any(existing.get("value") == item["value"] for existing in contact_candidates):
                contact_candidates.append(item)
        for href in links:
            absolute = normalize_url(urljoin(url, href))
            if URL_RE.fullmatch(absolute) and absolute not in checked_urls and absolute not in queue and domain(absolute) == base_domain:
                queue.append(absolute)
    contact_route = clean(record.get("contact_route")) or "unknown"
    contact_url = normalize_url(clean(record.get("contact_url")))
    outreach_candidates = [item for item in contact_candidates if item.get("kind") in {"public_role_email", "public_general_email"}]
    if outreach_candidates:
        contact_route = outreach_candidates[0].get("kind", "public_general_email")
    elif contact_url and URL_RE.fullmatch(contact_url):
        contact_route = "public_contact_form" if contact_route == "unknown" else contact_route
    elif any(domain(url) == "github.com" for url in checked_urls):
        contact_route = "public_project_page"
    return {
        **record,
        "contact_route": contact_route,
        "contact_url": contact_url or (checked_urls[0] if checked_urls else ""),
        "public_emails": contact_candidates,
        "contact_candidates": contact_candidates,
        "contact_checked_urls": checked_urls,
        "contact_status": "found" if outreach_candidates or contact_url or contact_route == "public_project_page" else "unknown",
    }


def contact_enrich(args: argparse.Namespace) -> int:
    raw = load_json(args.input)
    if isinstance(raw, dict):
        records = raw.get("records", raw.get("results", []))
    elif isinstance(raw, list):
        records = raw
    else:
        records = []
    if not isinstance(records, list):
        raise ValueError("input must contain records/results list")
    enriched: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for record in records:
        if not isinstance(record, dict):
            continue
        try:
            enriched.append(enrich_contact_record(record))
        except Exception as exc:  # noqa: BLE001
            key = clean(record.get("candidate_id") or record.get("url"))
            errors.append({"candidate_id": key, "error": f"{type(exc).__name__}: {exc}"})
            enriched.append({**record, "contact_status": "unknown", "contact_route": "unknown", "public_emails": [], "contact_candidates": []})
    payload = {
        "schema_version": "k18-contact-enrichment.v1",
        "department": "K-18 Funding Match Research",
        "run_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": "public_contact_research_only",
        "send_allowed": False,
        "messages_sent": 0,
        "counts": {"candidates": len(enriched), "contact_found": sum(item.get("contact_status") == "found" for item in enriched), "contact_unknown": sum(item.get("contact_status") != "found" for item in enriched)},
        "errors": errors,
        "records": enriched,
        "next_gate": "relevance_qualification_then_zoho_review_draft" if enriched else "new_signal_required",
    }
    args.output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"K-18 contact enrichment prepared: candidates={len(enriched)} contact_found={payload['counts']['contact_found']} errors={len(errors)} send_allowed=false")
    return 0


def fetch_official_pages(timeout: int = 20) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """Read a small allowlisted set of official program pages, bypassing search engines."""
    config = load_yaml(SOURCES_PATH)
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for source in config.get("official_pages", []):
        url = normalize_url(clean(source.get("url")))
        if not URL_RE.fullmatch(url):
            continue
        try:
            request = Request(url, headers={"User-Agent": "K18-Funding-Intelligence/1.0"})
            with urlopen(request, timeout=timeout, context=HTTPS_CONTEXT) as response:
                html = response.read().decode("utf-8", errors="replace")
        except Exception as exc:  # noqa: BLE001
            errors.append({"query_id": url, "error": f"{type(exc).__name__}: {exc}"})
            continue
        text = visible_text(html)
        title_match = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
        title = clean(unescape(title_match.group(1))) if title_match else domain(url)
        emails = sorted(set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", html, flags=re.I)))
        record = {
            "candidate_id": hashlib.sha256(url.encode()).hexdigest()[:16],
            "organization": clean(source.get("organization")) or title,
            "url": url,
            "public_signal": text[:4000],
            "program_operator_signal": any(term in text.lower() for term in OPERATOR_TERMS),
            "program_status": clean(source.get("program_status")),
            "role": clean(source.get("role")),
            "contact_route": clean(source.get("contact_route")) or "unknown",
            "contact_url": normalize_url(clean(source.get("contact_url"))),
            "public_emails": emails,
            "signal_date": clean(source.get("signal_date")),
            "route_fit": source.get("route_fit") is True,
            "manual_review": False,
            "audience_lane": "program_operator",
            "sources": [url],
        }
        records.append(record)
    return records, errors


def fetch_google_news_rss(query: str, limit: int = 5, timeout: int = 20) -> list[dict[str, Any]]:
    """Read fresh public announcements from Google's RSS surface, not web search."""
    request = Request(
        f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en",
        headers={"User-Agent": "K18-Funding-Intelligence/1.0"},
    )
    last_error: Exception | None = None
    for attempt in range(3):
        try:
            with urlopen(request, timeout=timeout, context=HTTPS_CONTEXT) as response:
                root = ET.fromstring(response.read())
            break
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt == 2:
                raise
            time.sleep(attempt + 1)
    hits: list[dict[str, Any]] = []
    for item in root.findall("./channel/item")[:limit]:
        title = clean(item.findtext("title"))
        news_url = normalize_url(clean(item.findtext("link")))
        source_node = item.find("source")
        source_name = clean(source_node.text if source_node is not None else "")
        source_url = normalize_url(clean(source_node.get("url") if source_node is not None else ""))
        published = clean(item.findtext("pubDate"))
        try:
            signal_date = parsedate_to_datetime(published).date().isoformat()
        except (TypeError, ValueError, OverflowError):
            signal_date = ""
        if not title or not URL_RE.fullmatch(news_url):
            continue
        hits.append(
            {
                "title": title,
                "url": news_url,
                "news_url": news_url,
                "source_name": source_name,
                "source_url": source_url,
                "public_signal": title,
                "signal_date": signal_date,
                "research_status": "news_discovery_unenriched",
            }
        )
    return hits


def fetch_github_issues(query: str, limit: int = 5, timeout: int = 20) -> list[dict[str, Any]]:
    """Find public issue-level funding signals without collecting private contact data."""
    request = Request(
        f"https://api.github.com/search/issues?q={quote_plus(query)}&per_page={limit}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": "K18-Funding-Intelligence/1.0"},
    )
    with urlopen(request, timeout=timeout, context=HTTPS_CONTEXT) as response:
        payload = json.loads(response.read().decode("utf-8"))
    hits: list[dict[str, Any]] = []
    for item in payload.get("items", []):
        if "pull_request" in item:
            continue
        repository_api_url = clean(item.get("repository_url"))
        repository = repository_api_url.removeprefix("https://api.github.com/repos/").lower()
        if repository in GITHUB_EXCLUDED_REPOS or not repository:
            continue
        title = clean(item.get("title"))
        body = clean(item.get("body"))
        if not title or not URL_RE.fullmatch(clean(item.get("html_url"))):
            continue
        signal_text = f"{title} {body}".lower()
        if any(term in signal_text for term in GITHUB_NOISE_TERMS):
            continue
        if not any(term in signal_text for term in ("funding needed", "seeking funding", "looking for funding", "cloud credits", "grant funding", "raising capital", "fundraise")):
            continue
        hits.append(
            {
                "title": title,
                "url": clean(item.get("html_url")),
                "organization": repository,
                "public_signal": clean(f"{title}. {body[:3000]}"),
                "funding_need_signal": True,
                "technical_project": bool(repository_api_url),
                "signal_date": clean(item.get("created_at", ""))[:10],
                "sources": [clean(item.get("html_url")), f"https://github.com/{repository}"],
                "research_status": "public_issue_unreviewed",
            }
        )
        if len(hits) >= limit:
            break
    return hits


def query_lane(item: dict[str, Any]) -> str:
    """Resolve an unlabelled query to the project lane, never both lanes."""

    return clean(item.get("lane")) or "project"


def build_search_record(query_id: str, hit: dict[str, Any], lane: str) -> dict[str, Any]:
    """Attach an authoritative audience lane to every search result."""

    record = dict(hit)
    record.update(
        {
            "candidate_id": hashlib.sha256(clean(hit.get("url")).encode()).hexdigest()[:16],
            "query_id": query_id,
            "audience_lane": lane,
        }
    )
    return record


def search(args: argparse.Namespace) -> int:
    config = load_yaml(QUERIES_PATH)
    queries = config.get("queries") or []
    if args.provider not in {"duckduckgo", "playwright_google", "playwright_bing", "official_pages", "google_news_rss", "github_issues"}:
        raise ValueError("K-18 supports --provider duckduckgo, --provider playwright_google, --provider playwright_bing, --provider official_pages, --provider google_news_rss, or --provider github_issues")
    provider_lanes = {"official_pages": "program_operator", "google_news_rss": "program_operator", "github_issues": "project"}
    expected_lane = provider_lanes.get(args.provider)
    if expected_lane and args.lane != expected_lane:
        raise ValueError(f"provider {args.provider} is restricted to the {expected_lane} lane")
    records: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    query_items = [item for item in queries if query_lane(item) == args.lane]
    if args.provider == "github_issues":
        query_items = [item for item in query_items if clean(item.get("id")).startswith("project_github_")]
    elif args.provider == "google_news_rss":
        query_items = [item for item in query_items if clean(item.get("id")).startswith("program_operator_")]
    if args.provider == "official_pages":
        try:
            page_records, page_errors = fetch_official_pages()
            records.extend(page_records)
            errors.extend(page_errors)
        except Exception as exc:  # noqa: BLE001
            errors.append({"query_id": "official_pages", "error": f"{type(exc).__name__}: {exc}"})
    if args.provider in {"google_news_rss", "github_issues"}:
        for item in query_items[: int(config["limits"]["max_queries_per_run"])]:
            query_id = clean(item.get("id"))
            query = clean(item.get("query"))
            try:
                fetcher = fetch_google_news_rss if args.provider == "google_news_rss" else fetch_github_issues
                for hit in fetcher(query, int(config["limits"]["max_results_per_query"])):
                    record = build_search_record(query_id, hit, args.lane)
                    if args.provider == "google_news_rss":
                        record.update({"organization": hit.get("source_name", ""), "program_operator_signal": args.lane == "program_operator", "program_status": "applications_open" if "open" in hit.get("public_signal", "").lower() else "", "route_fit": False, "contact_route": "unknown", "manual_review": False})
                    records.append(record)
            except Exception as exc:  # noqa: BLE001
                errors.append({"query_id": query_id, "error": f"{type(exc).__name__}: {exc}"})
    for item in query_items[: int(config["limits"]["max_queries_per_run"])] if args.provider in {"duckduckgo", "playwright_google", "playwright_bing"} else []:
        query_id = clean(item.get("id"))
        query = clean(item.get("query"))
        try:
            fetcher = fetch_playwright_google if args.provider == "playwright_google" else fetch_playwright_bing if args.provider == "playwright_bing" else fetch_search
            for hit in fetcher(query, int(config["limits"]["max_results_per_query"])):
                record = build_search_record(query_id, hit, args.lane)
                record["research_status"] = "unreviewed"
                records.append(record)
        except Exception as exc:  # noqa: BLE001
            errors.append({"query_id": query_id, "error": f"{type(exc).__name__}: {exc}"})
    deduped = {record["candidate_id"]: record for record in records}
    payload = {
        "schema_version": "k18-search.v1",
        "department": "K-18 Funding Match Research",
        "run_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": "public_research_only",
        "provider": args.provider,
        "send_allowed": False,
        "messages_sent": 0,
        "discovery_status": "success" if records and not errors else "partial" if records else "blocked" if errors else "empty",
        "results": list(deduped.values()),
        "errors": errors,
        "next_gate": "manual_public_evidence_enrichment" if records else "configure_approved_search_provider",
    }
    args.output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"K-18 search prepared: candidates={len(deduped)} errors={len(errors)} send_allowed=false")
    return 0


def age_days(value: str) -> int | None:
    try:
        return (date.today() - date.fromisoformat(value)).days
    except (TypeError, ValueError):
        return None


def qualify_record(record: dict[str, Any], suppressed: set[str]) -> dict[str, Any]:
    lane = clean(record.get("audience_lane"))
    if lane == "program_operator":
        return qualify_operator_record(record, suppressed)
    if lane != "project":
        key = clean(record.get("candidate_id") or record.get("url")).lower()
        return {
            "candidate_id": key,
            "audience_lane": lane or None,
            "organization": clean(record.get("organization")),
            "url": normalize_url(clean(record.get("url"))),
            "score": 0,
            "status": "research_hold",
            "holds": ["audience_lane_unknown"],
            "reasons": [],
            "contact_route": record.get("contact_route"),
            "recipient_role": clean(record.get("role")),
            "draft": None,
            "send_ready": False,
        }
    text = " ".join(clean(record.get(key)) for key in ("organization", "description", "public_signal", "role"))
    low = text.lower()
    key = clean(record.get("candidate_id") or record.get("url")).lower()
    reasons: list[str] = []
    holds: list[str] = []
    if not key or key in suppressed:
        holds.append("suppressed_or_missing_id")
    if not URL_RE.fullmatch(clean(record.get("url"))):
        holds.append("missing_public_project_url")
    if not any(term in low for term in NEED_TERMS) and record.get("funding_need_signal") is not True:
        holds.append("no_explicit_current_funding_signal")
    if not any(term in low for term in TECH_TERMS) and record.get("technical_project") is not True:
        holds.append("technical_project_not_proven")
    if not any(term in low for term in ROLE_TERMS) and not clean(record.get("role")):
        holds.append("role_route_unknown")
    if any(term in low for term in EXCLUDED_TERMS):
        holds.append("excluded_entity_type")
    freshness = age_days(record.get("signal_date"))
    if freshness is None or freshness < 0 or freshness > 90:
        holds.append("signal_stale_or_unverified")
    if record.get("route_fit") is not True:
        holds.append("route_fit_not_reviewed")
    if record.get("contact_route") not in {"public_role_email", "public_contact_form", "consented_reply"}:
        holds.append("no_approved_contact_route")
    if record.get("manual_review") is not True:
        holds.append("manual_review_required")
    score = 0
    score += 25 if record.get("funding_need_signal") is True or any(term in low for term in NEED_TERMS) else 0
    score += 20 if record.get("technical_project") is True or any(term in low for term in TECH_TERMS) else 0
    score += 15 if freshness is not None and 0 <= freshness <= 30 else 10 if freshness is not None and freshness <= 90 else 0
    score += 15 if record.get("route_fit") is True else 0
    score += 10 if clean(record.get("role")) else 0
    score += 10 if record.get("contact_route") in {"public_role_email", "public_contact_form", "consented_reply"} else 0
    score += 5 if isinstance(record.get("sources"), list) and len(record["sources"]) >= 2 else 0
    relevance_holds = [hold for hold in holds if hold != "manual_review_required"]
    relevance_status = "confirmed" if not relevance_holds else "research_hold"
    status = "manual_review" if relevance_status == "confirmed" else "research_hold"
    draft = None
    if status == "manual_review":
        organization = clean(record.get("organization")) or "your project"
        draft = {
            "subject": f"A checked funding-route map for {organization}",
            "body": (
                f"Hi there,\n\nWe noticed this public signal about {organization}: "
                f"{clean(record.get('public_signal'))}.\n\n"
                "We prepare short, source-backed maps of relevant grants, credits, accelerators, and partner routes, "
                "including what still needs verification. We do not promise funding or submit applications.\n\n"
                "Would a concise review based on your public project information be useful? If not, please ignore this message.\n\n"
                "Best,\nHlinor"
            ),
        }
    return {
        "candidate_id": key,
        "organization": clean(record.get("organization")),
        "url": normalize_url(clean(record.get("url"))),
        "score": min(score, 100),
        "status": status,
        "relevance_status": relevance_status,
        "holds": holds,
        "reasons": reasons,
        "contact_route": record.get("contact_route"),
        "recipient_role": clean(record.get("role")),
        "draft": draft,
        "send_ready": False,
    }


def qualify_operator_record(record: dict[str, Any], suppressed: set[str]) -> dict[str, Any]:
    """Qualify a program operator as a buyer of applicant/pipeline intelligence."""
    text = " ".join(clean(record.get(key)) for key in ("organization", "description", "public_signal", "program_status"))
    low = text.lower()
    key = clean(record.get("candidate_id") or record.get("url")).lower()
    holds: list[str] = []
    if not key or key in suppressed:
        holds.append("suppressed_or_missing_id")
    url = normalize_url(clean(record.get("url")))
    if not URL_RE.fullmatch(url):
        holds.append("missing_official_program_url")
    if not record.get("program_operator_signal") and not any(term in low for term in OPERATOR_TERMS):
        holds.append("program_operator_signal_not_proven")
    if clean(record.get("program_status")) not in {"applications_open", "applications_upcoming", "active_program"}:
        holds.append("program_status_not_verified")
    if record.get("route_fit") is not True:
        holds.append("route_fit_not_reviewed")
    if record.get("contact_route") not in {"public_role_email", "public_general_email", "public_contact_form"}:
        holds.append("no_approved_contact_route")
    if domain(url) == "news.google.com" or clean(record.get("research_status")) == "news_discovery_unenriched":
        holds.append("news_signal_needs_official_page_enrichment")
    if record.get("manual_review") is not True:
        holds.append("manual_review_required")
    if any(term in low for term in ("directory", "job board", "generic startup list")):
        holds.append("excluded_entity_type")
    freshness = age_days(record.get("signal_date"))
    if freshness is None or freshness < 0 or freshness > 120:
        holds.append("signal_stale_or_unverified")
    score = 0
    score += 30 if record.get("program_operator_signal") or any(term in low for term in OPERATOR_TERMS) else 0
    score += 20 if clean(record.get("program_status")) == "applications_open" else 15 if clean(record.get("program_status")) == "applications_upcoming" else 10 if clean(record.get("program_status")) == "active_program" else 0
    score += 15 if record.get("route_fit") is True else 0
    score += 15 if record.get("contact_route") in {"public_role_email", "public_general_email", "public_contact_form"} else 0
    score += 10 if freshness is not None and 0 <= freshness <= 30 else 5 if freshness is not None and freshness <= 120 else 0
    score += 5 if clean(record.get("role")) else 0
    relevance_holds = [hold for hold in holds if hold != "manual_review_required"]
    relevance_status = "confirmed" if not relevance_holds else "research_hold"
    status = "manual_review" if relevance_status == "confirmed" else "research_hold"
    draft = None
    if status == "manual_review":
        organization = clean(record.get("organization")) or "your program"
        draft = {
            "subject": f"Evidence-gated applicant triage for {organization}",
            "body": (
                f"Hi {clean(record.get('role')) or 'team'},\n\n"
                f"I saw the public program update for {organization}: {clean(record.get('program_status'))}.\n\n"
                "Funding Intelligence can pre-triage accelerator and grant applicants against current eligibility, "
                "funding, credits, pilot, and partner routes while preserving source links and explicit unknowns. "
                "The goal is less manual sorting and fewer false-positive referrals; it does not submit applications or promise outcomes.\n\n"
                "Would a small, source-backed pilot for one intake cohort be useful? If not, please ignore this message.\n\n"
                "Best,\nHlinor"
            ),
        }
    return {
        "candidate_id": key,
        "audience_lane": "program_operator",
        "organization": clean(record.get("organization")),
        "url": url,
        "score": min(score, 100),
        "status": status,
        "relevance_status": relevance_status,
        "holds": holds,
        "contact_route": record.get("contact_route"),
        "contact_url": normalize_url(clean(record.get("contact_url"))),
        "public_emails": record.get("public_emails", []),
        "recipient_role": clean(record.get("role")),
        "draft": draft,
        "send_ready": False,
    }


def qualify(args: argparse.Namespace) -> int:
    raw = load_json(args.input)
    if isinstance(raw, dict):
        records = raw.get("records", raw.get("results", []))
    elif isinstance(raw, list):
        records = raw
    else:
        records = []
    if not isinstance(records, list):
        raise ValueError("input must contain records/results list")
    suppressed: set[str] = set()
    if args.suppression and args.suppression.exists():
        data = load_json(args.suppression)
        values = data.get("candidate_ids", []) if isinstance(data, dict) else data
        suppressed = {clean(value).lower() for value in values if clean(value)}
    qualified = [qualify_record(item, suppressed) for item in records if isinstance(item, dict)]
    qualified.sort(key=lambda item: (-item["score"], item["organization"].lower()))
    payload = {
        "schema_version": "k18-qualification.v1",
        "department": "K-18 Funding Match Research",
        "run_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "mode": "draft_only_manual_review",
        "send_allowed": False,
        "messages_sent": 0,
        "counts": {"candidates": len(qualified), "manual_review": sum(item["status"] == "manual_review" for item in qualified), "research_hold": sum(item["status"] == "research_hold" for item in qualified)},
        "records": qualified,
        "next_gate": "owner_review_then_separate_send_approval",
    }
    args.output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"K-18 qualification prepared: candidates={len(qualified)} manual_review={payload['counts']['manual_review']} holds={payload['counts']['research_hold']} send_allowed=false")
    return 0


def self_test() -> int:
    good = {"candidate_id": "good", "audience_lane": "project", "organization": "Orbit AI", "url": "https://orbit.example", "public_signal": "seeking grant funding for an open source AI infrastructure launch", "funding_need_signal": True, "technical_project": True, "role": "founder", "signal_date": date.today().isoformat(), "route_fit": True, "contact_route": "public_contact_form", "manual_review": True, "sources": ["https://orbit.example", "https://orbit.example/blog/grant"]}
    bad = {"candidate_id": "bad", "organization": "Generic Marketing Agency", "url": "https://agency.example", "public_signal": "newsletter and jobs", "signal_date": date.today().isoformat(), "contact_route": "unknown"}
    a = qualify_record(good, set())
    b = qualify_record(bad, set())
    if a["status"] != "manual_review" or a["send_ready"] or b["status"] != "research_hold":
        print("K-18 self-test failed", file=sys.stderr)
        return 1
    print("K-18 self-test passed: explicit signal and manual gates enforced")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    search_parser = sub.add_parser("search")
    search_parser.add_argument("--provider", default="duckduckgo")
    search_parser.add_argument("--lane", default="project", choices=("project", "program_operator"))
    search_parser.add_argument("--output", type=Path, required=True)
    search_parser.set_defaults(func=search)
    qualify_parser = sub.add_parser("qualify")
    qualify_parser.add_argument("--input", type=Path, required=True)
    qualify_parser.add_argument("--output", type=Path, required=True)
    qualify_parser.add_argument("--suppression", type=Path)
    qualify_parser.set_defaults(func=qualify)
    contact_parser = sub.add_parser("contact-enrich")
    contact_parser.add_argument("--input", type=Path, required=True)
    contact_parser.add_argument("--output", type=Path, required=True)
    contact_parser.set_defaults(func=contact_enrich)
    self_parser = sub.add_parser("self-test")
    self_parser.set_defaults(func=lambda _args: self_test())
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
