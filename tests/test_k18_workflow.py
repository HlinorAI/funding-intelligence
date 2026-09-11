from datetime import date

from ops.k18.k18_workflow import build_search_record, qualify_record, query_lane


def test_k18_requires_explicit_signal_and_manual_review():
    record = {
        "candidate_id": "orbit",
        "audience_lane": "project",
        "organization": "Orbit AI",
        "url": "https://orbit.example",
        "public_signal": "seeking grant funding for open source AI infrastructure",
        "funding_need_signal": True,
        "technical_project": True,
        "role": "founder",
        "signal_date": date.today().isoformat(),
        "route_fit": True,
        "contact_route": "public_contact_form",
        "manual_review": True,
        "sources": ["https://orbit.example", "https://orbit.example/blog/grant"],
    }
    result = qualify_record(record, set())
    assert result["status"] == "manual_review"
    assert result["send_ready"] is False
    assert result["draft"] is not None


def test_k18_holds_generic_or_unproven_candidate():
    result = qualify_record(
        {
            "candidate_id": "agency",
            "audience_lane": "project",
            "organization": "Generic Marketing Agency",
            "url": "https://agency.example",
            "public_signal": "newsletter and jobs",
            "signal_date": date.today().isoformat(),
            "contact_route": "unknown",
        },
        set(),
    )
    assert result["status"] == "research_hold"
    assert "no_explicit_current_funding_signal" in result["holds"]
    assert "excluded_entity_type" in result["holds"]


def test_k18_operator_lane_prepares_triage_offer():
    result = qualify_record(
        {
            "candidate_id": "operator",
            "audience_lane": "program_operator",
            "organization": "Example Accelerator",
            "url": "https://accelerator.example/program",
            "public_signal": "applications open for accelerator cohort",
            "program_operator_signal": True,
            "program_status": "applications_open",
            "role": "program lead",
            "signal_date": date.today().isoformat(),
            "route_fit": True,
            "contact_route": "public_contact_form",
            "manual_review": True,
        },
        set(),
    )
    assert result["audience_lane"] == "program_operator"
    assert result["status"] == "manual_review"
    assert result["draft"]["subject"].startswith("Evidence-gated applicant triage")


def test_k18_operator_news_signal_cannot_skip_official_enrichment():
    result = qualify_record(
        {
            "candidate_id": "news",
            "audience_lane": "program_operator",
            "organization": "News source",
            "url": "https://news.google.com/rss/articles/example",
            "source_url": "https://example.org",
            "public_signal": "applications open accelerator cohort",
            "program_operator_signal": True,
            "program_status": "applications_open",
            "signal_date": date.today().isoformat(),
            "route_fit": True,
            "contact_route": "public_contact_form",
            "manual_review": True,
        },
        set(),
    )
    assert "news_signal_needs_official_page_enrichment" in result["holds"]
    assert result["status"] == "research_hold"


def test_k18_unknown_lane_fails_closed_without_draft():
    result = qualify_record(
        {
            "candidate_id": "unlabelled",
            "organization": "Unlabelled Candidate",
            "url": "https://example.org",
            "public_signal": "seeking funding",
        },
        set(),
    )
    assert result["status"] == "research_hold"
    assert result["holds"] == ["audience_lane_unknown"]
    assert result["draft"] is None
    assert result["send_ready"] is False


def test_k18_search_records_and_queries_keep_lanes_separate():
    assert query_lane({"id": "untagged"}) == "project"
    assert query_lane({"id": "operator", "lane": "program_operator"}) == "program_operator"
    record = build_search_record("operator_query", {"url": "https://example.org", "title": "Applications open"}, "program_operator")
    assert record["audience_lane"] == "program_operator"
    project = qualify_record(
        {
            "candidate_id": "project",
            "audience_lane": "project",
            "organization": "Orbit AI",
            "url": "https://orbit.example",
            "public_signal": "seeking grant funding for open source AI infrastructure",
            "funding_need_signal": True,
            "technical_project": True,
            "role": "founder",
            "signal_date": date.today().isoformat(),
            "route_fit": True,
            "contact_route": "public_contact_form",
            "manual_review": True,
            "sources": ["https://orbit.example", "https://orbit.example/grant"],
        },
        set(),
    )
    assert project["draft"]["subject"].startswith("A checked funding-route map")
    assert project["draft"]["subject"] != qualify_record(
        {
            "candidate_id": "operator",
            "audience_lane": "program_operator",
            "organization": "Example Accelerator",
            "url": "https://accelerator.example/program",
            "public_signal": "applications open for accelerator cohort",
            "program_operator_signal": True,
            "program_status": "applications_open",
            "role": "program lead",
            "signal_date": date.today().isoformat(),
            "route_fit": True,
            "contact_route": "public_contact_form",
            "manual_review": True,
        },
        set(),
    )["draft"]["subject"]
