#!/usr/bin/env bash
set -eu

REPORT_DIR=/root/hlinor/k18/reports
mkdir -p "$REPORT_DIR"
chmod 700 "$REPORT_DIR"

# This legacy K-18 runner remains useful for public-source discovery and
# qualification. Its Zoho writer is intentionally not part of the active
# outreach path; the current controlled workflow owns draft creation.
/usr/bin/python3 /root/hlinor/k18/k18_workflow.py search \
  --provider official_pages \
  --lane program_operator \
  --output "$REPORT_DIR/search.operator.latest.json"
/usr/bin/python3 /root/hlinor/k18/k18_workflow.py contact-enrich \
  --input "$REPORT_DIR/search.operator.latest.json" \
  --output "$REPORT_DIR/enriched.operator.latest.json"
/usr/bin/python3 /root/hlinor/k18/k18_free_email_finder.py \
  --input "$REPORT_DIR/enriched.operator.latest.json" \
  --output "$REPORT_DIR/enriched.operator.free-finder.latest.json" \
  --limit 10
/usr/bin/python3 /root/hlinor/k18/k18_workflow.py qualify \
  --input "$REPORT_DIR/enriched.operator.free-finder.latest.json" \
  --output "$REPORT_DIR/qualification.operator.free-finder.latest.json"

/usr/bin/python3 /root/hlinor/k18/k18_workflow.py search \
  --provider google_news_rss \
  --lane program_operator \
  --output "$REPORT_DIR/search.news.latest.json"
/usr/bin/python3 /root/hlinor/k18/k18_workflow.py contact-enrich \
  --input "$REPORT_DIR/search.news.latest.json" \
  --output "$REPORT_DIR/enriched.news.latest.json"
/usr/bin/python3 /root/hlinor/k18/k18_workflow.py qualify \
  --input "$REPORT_DIR/enriched.news.latest.json" \
  --output "$REPORT_DIR/qualification.news.latest.json"

/usr/bin/python3 /root/hlinor/k18/k18_workflow.py search \
  --provider github_issues \
  --lane project \
  --output "$REPORT_DIR/search.github.latest.json"
/usr/bin/python3 /root/hlinor/k18/k18_workflow.py contact-enrich \
  --input "$REPORT_DIR/search.github.latest.json" \
  --output "$REPORT_DIR/enriched.github.latest.json"
/usr/bin/python3 /root/hlinor/k18/k18_workflow.py qualify \
  --input "$REPORT_DIR/enriched.github.latest.json" \
  --output "$REPORT_DIR/qualification.github.latest.json"

echo "K-18 legacy Zoho draft writer disabled; use the current controlled outreach workflow."
