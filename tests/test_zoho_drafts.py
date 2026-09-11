from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "ops" / "k18" / "create_zoho_drafts.py"
SPEC = spec_from_file_location("create_zoho_drafts", MODULE_PATH)
MODULE = module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_build_message_contains_plain_text_and_html_alternatives():
    record = {
        "candidate_id": "pilot-wit",
        "organization": "WIT Funding & Consulting",
        "url": "https://witfunding.eu/eu-funding/",
        "draft": {
            "subject": "A review-only pilot for WIT",
            "body": "Hello,\n\nCould we compare ten redacted cases?\n\nBest regards,\nHlinor",
            "intro": "Your concept-validation workflow is a strong fit for a small test.",
            "ask": "Would you be open to reviewing ten redacted cases?",
            "repository_url": "https://github.com/HlinorAI/funding-intelligence",
            "repository_sentence": "You can inspect the approach before any data is shared in the",
            "questions": ["Which step takes the most time?", "What would make the test useful?"],
        },
    }

    message = MODULE.build_message(record, "contact@example.org", "k18:pilot-wit:contact@example.org")

    assert message.is_multipart()
    assert message.get_body(preferencelist=("html",)).get_content_type() == "text/html"
    html = message.get_body(preferencelist=("html",)).get_content()
    assert "WIT Funding &amp; Consulting" in html
    assert "Which step takes the most time?" in html
    assert "https://witfunding.eu/eu-funding/" in html
    assert "https://github.com/HlinorAI/funding-intelligence" in html
    assert "inspect the approach before any data is shared" in html
    assert "no applicant contacted" in html


def test_normalized_addresses_deduplicate_case_and_display_names():
    assert MODULE.normalized_addresses('Team <Info@Example.com>, info@example.com') == {"info@example.com"}
