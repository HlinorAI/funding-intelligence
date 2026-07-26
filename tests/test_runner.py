"""Parametric tests for the Funding Intelligence runner.

Each test case in tests/cases/*.yaml has a corresponding expected output
in tests/expected/*.yaml. The runner runs each case and asserts that the
actual report matches the expected decision, gate state, and program
inclusion/exclusion criteria.
"""

from pathlib import Path
import sys
import subprocess
import yaml
import jsonschema
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "runtime"))

from runner import build_report, evaluate, load_yaml as load_card_yaml
from render_report import render
from verify_route import verify_route


def run_runner(case_path: Path, timeout: int = 60) -> dict:
    """Run the Funding Intelligence runner on a test case and return the report."""
    result = subprocess.run(
        [sys.executable, "runtime/runner.py", str(case_path)],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO_ROOT,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Runner failed (exit {result.returncode}):\n{result.stderr}"
        )
    return yaml.safe_load(result.stdout)


def load_yaml(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestRunnerDecisions:
    """Verify that runner decisions match expected outputs."""

    def _check_expected(self, report: dict, expected: dict, case_name: str):
        """Assert that a report matches the expected constraints."""
        # Gate check: gate.passed must match
        if "gate_passed" in expected:
            assert report.get("gate", {}).get("passed") == expected["gate_passed"], (
                f"[{case_name}] Expected gate.passed={expected['gate_passed']}, "
                f"got {report.get('gate', {}).get('passed')}"
            )

        # must_not_be_now: no opportunity should have decision NOW
        if expected.get("must_not_be_now"):
            now_opps = [
                o["program_id"]
                for o in report.get("opportunities", [])
                if o.get("decision") == "NOW"
            ]
            assert len(now_opps) == 0, (
                f"[{case_name}] Expected no NOW opportunities, got: {now_opps}"
            )

        # must_include: a specific program must appear in opportunities or do_not_apply
        must_include = expected.get("must_include")
        if must_include:
            all_programs = set()
            for o in report.get("opportunities", []):
                all_programs.add(o["program_id"])
            for d in report.get("do_not_apply", []):
                all_programs.add(d["program_id"])
            assert must_include in all_programs, (
                f"[{case_name}] Expected '{must_include}' in report, "
                f"found: {sorted(all_programs)}"
            )

        # decision: a specific program should have this decision
        decision_target = expected.get("decision")
        decision_program = expected.get("must_include")
        if decision_target and decision_program:
            found = False
            for o in report.get("opportunities", []):
                if o["program_id"] == decision_program and o.get("decision") == decision_target:
                    found = True
                elif o["program_id"] == decision_program:
                    # Program found but wrong decision — this is a failure
                    assert o.get("decision") == decision_target, (
                        f"[{case_name}] Expected '{decision_program}' to have "
                        f"decision '{decision_target}', got '{o.get('decision')}'"
                    )
            for d in report.get("do_not_apply", []):
                if d["program_id"] == decision_program and d.get("decision") == decision_target:
                    found = True
                elif d["program_id"] == decision_program:
                    assert d.get("decision") == decision_target, (
                        f"[{case_name}] Expected '{decision_program}' (do_not_apply) to have "
                        f"decision '{decision_target}', got '{d.get('decision')}'"
                    )

            if not found:
                # If must_include program is not must_include_target, check first opportunity
                if decision_program and decision_target and not expected.get("must_include"):
                    pass  # handled above
                elif not decision_program:
                    # Check top opportunity
                    opps = report.get("opportunities", [])
                    if opps:
                        assert opps[0].get("decision") == decision_target, (
                            f"[{case_name}] Expected top opportunity decision "
                            f"'{decision_target}', got '{opps[0].get('decision')}'"
                        )

    # --- Individual test cases ---

    def test_ai_startup(self):
        case = Path(__file__).resolve().parent / "cases" / "ai_startup.yaml"
        expected = Path(__file__).resolve().parent / "expected" / "ai_startup.yaml"
        report = run_runner(case)
        exp = load_yaml(expected)
        self._check_expected(report, exp, "ai_startup")

        # Specific assertions
        # Top opportunity should include microsoft-for-startups
        all_ids = [o["program_id"] for o in report.get("opportunities", [])]
        assert "microsoft-for-startups" in all_ids, (
            f"ai_startup: microsoft-for-startups not in opportunities: {all_ids}"
        )
        # No opportunity should be NOW (all cards need verification)
        now_ids = [o["program_id"] for o in report.get("opportunities", []) if o.get("decision") == "NOW"]
        assert len(now_ids) == 0, f"ai_startup: unexpected NOW opportunities: {now_ids}"
        # Gate should be false (status_verified is false for all cards)
        assert report.get("gate", {}).get("passed") is False

    def test_web3(self):
        case = Path(__file__).resolve().parent / "cases" / "web3.yaml"
        expected = Path(__file__).resolve().parent / "expected" / "web3.yaml"
        report = run_runner(case)
        exp = load_yaml(expected)
        self._check_expected(report, exp, "web3")

        # Specific: must include base-funding-ladder
        all_ids = set()
        for o in report.get("opportunities", []):
            all_ids.add(o["program_id"])
        for d in report.get("do_not_apply", []):
            all_ids.add(d["program_id"])
        assert "base-funding-ladder" in all_ids, (
            f"web3: base-funding-ladder not found in report. "
            f"Opportunities: {[o['program_id'] for o in report.get('opportunities', [])]}"
        )

    def test_hardware(self):
        case = Path(__file__).resolve().parent / "cases" / "hardware.yaml"
        expected = Path(__file__).resolve().parent / "expected" / "hardware.yaml"
        report = run_runner(case)
        exp = load_yaml(expected)
        self._check_expected(report, exp, "hardware")

        # Hardware startup should get DO_NOT_APPLY — no AI or Web3 program matches
        opps = report.get("opportunities", [])
        assert len(opps) == 0 or opps[0].get("score", 0) < 50, (
            f"hardware: expected no viable opportunities (score < 50), "
            f"top opp: {opps[0] if opps else 'none'}"
        )

    def test_sme(self):
        case = Path(__file__).resolve().parent / "cases" / "sme.yaml"
        expected = Path(__file__).resolve().parent / "expected" / "sme.yaml"
        report = run_runner(case)
        exp = load_yaml(expected)
        self._check_expected(report, exp, "sme")

        # SME should get DO_NOT_APPLY — payments SME fits no AI or Web3 program
        opps = report.get("opportunities", [])
        assert len(opps) == 0 or opps[0].get("score", 0) < 50, (
            f"sme: expected no viable opportunities (score < 50), "
            f"top opp: {opps[0] if opps else 'none'}"
        )

    def test_affiliated(self):
        case = Path(__file__).resolve().parent / "cases" / "program_affiliated.yaml"
        expected = Path(__file__).resolve().parent / "expected" / "program_affiliated.yaml"
        report = run_runner(case)
        exp = load_yaml(expected)
        self._check_expected(report, exp, "program_affiliated")

        # Y Combinator must be in do_not_apply (current affiliation)
        dna_ids = [d["program_id"] for d in report.get("do_not_apply", [])]
        assert "y-combinator" in dna_ids, (
            f"program_affiliated: y-combinator not in do_not_apply. "
            f"do_not_apply: {dna_ids}"
        )

    def test_previous_successful(self):
        case = Path(__file__).resolve().parent / "cases" / "program_previous.yaml"
        expected = Path(__file__).resolve().parent / "expected" / "program_previous.yaml"
        report = run_runner(case)
        exp = load_yaml(expected)
        self._check_expected(report, exp, "program_previous")

        # Y Combinator must be in do_not_apply (previous successful)
        dna_ids = [d["program_id"] for d in report.get("do_not_apply", [])]
        assert "y-combinator" in dna_ids, (
            f"program_previous: y-combinator not in do_not_apply. "
            f"do_not_apply: {dna_ids}"
        )

    def test_rejected(self):
        case = Path(__file__).resolve().parent / "cases" / "program_rejected.yaml"
        expected = Path(__file__).resolve().parent / "expected" / "program_rejected.yaml"
        report = run_runner(case)
        exp = load_yaml(expected)
        self._check_expected(report, exp, "program_rejected")

        # Y Combinator must be in opportunities with APPLY_AGAIN_AFTER_CHANGE
        opp_ids = {o["program_id"]: o.get("decision") for o in report.get("opportunities", [])}
        assert opp_ids.get("y-combinator") == "APPLY_AGAIN_AFTER_CHANGE", (
            f"program_rejected: expected y-combinator with APPLY_AGAIN_AFTER_CHANGE "
            f"in opportunities, found: {opp_ids}"
        )

        # Top opportunity should still be the best scoring AI program
        assert opp_ids.get("aws-activate") in ("VERIFY_FIRST", "NEXT", "NOW"), (
            f"program_rejected: expected aws-activate as viable opportunity, "
            f"got: {opp_ids}"
        )

    def test_rejected_affiliation_verifier_contract(self):
        """A rejected affiliation may require reapplication work without invalidating eligibility state."""
        result = subprocess.run(
            [
                sys.executable,
                "runtime/verify_route.py",
                "tests/cases/program_rejected.yaml",
                "--route",
                "y-combinator",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0, result.stderr
        document = yaml.safe_load(result.stdout)
        route = document["routes"][0]
        assert route["decision"] == "APPLY_AGAIN_AFTER_CHANGE"
        assert route["project_readiness"] == "REAPPLY_AFTER_CHANGE"
        assert route["eligibility"]["state"] == "INCOMPLETE"
        schema = load_yaml(REPO_ROOT / "schemas" / "route-verification.schema.yaml")
        jsonschema.validate(document, schema)

    def test_structured_evidence_policy_rejects_partial_aws_eligibility(self):
        """Structured policies must not pass a compound requirement when one field is unknown."""
        card = load_card_yaml(REPO_ROOT / "knowledge" / "packs" / "ai" / "programs" / "aws-activate.yaml")
        project = {
            "name": "Partial AWS Evidence",
            "sector": ["artificial_intelligence"],
            "stage": "seed",
            "geography": ["US"],
            "product": {"description": "AI infrastructure", "technology": ["api"]},
            "evidence": {"site": True},
            "needs": {"goals": ["funding"], "requested_mechanisms": ["subsidy"]},
            "constraints": {"native_ecosystems": [], "target_ecosystems": []},
        }
        pack = {
            "company": {"legal_entity": "private_for_profit", "country": "unknown", "current_funding": "seed"},
            "funding-needs": {"aws_account": True},
            "product": {"api_use_case": "managed inference workload"},
        }
        route = verify_route(project, card, pack, False)
        proofs = {item["id"]: item for item in route["required_proof"]}
        assert route["evidence_policy"] == {"mode": "structured", "mechanisms": ["subsidy"]}
        assert proofs["legal_entity"]["status"] == "PASS"
        assert proofs["funding_stage"]["status"] == "PASS"
        assert proofs["headquarters_country"]["status"] == "MISSING"
        assert route["eligibility"]["state"] == "INCOMPLETE"

    def test_official_source_is_not_an_application_endpoint(self):
        """A program page cannot be promoted to an application route without explicit verification."""
        card = load_card_yaml(REPO_ROOT / "knowledge" / "programs" / "base.yaml")
        project = load_yaml(REPO_ROOT / "tests" / "cases" / "web3.yaml")
        runner_result = evaluate(project, card)
        route = verify_route(project, card, {}, False)

        assert runner_result["gate"]["application_endpoint_exists"] is False
        assert route["application_endpoint"] == {
            "url": None,
            "state": "missing",
            "kind": None,
            "verified_at": None,
        }
        assert route["endpoint_status"]["value"] == "MISSING"
        assert route["decision"] == "NO_ACTIONABLE_ENDPOINT"

    def test_renderer_lists_routes_without_application_endpoints(self):
        """The human report must not hide a route blocked by a missing application URL."""
        project = load_yaml(REPO_ROOT / "tests" / "cases" / "web3.yaml")
        card = load_card_yaml(REPO_ROOT / "knowledge" / "programs" / "base.yaml")
        rendered = render(
            build_report(project),
            {"project": project["name"], "routes": [verify_route(project, card, {}, False)]},
        )

        assert "## NO_ACTIONABLE_ENDPOINT" in rendered
        assert "### Base Funding Ladder" in rendered
        assert "Application endpoint: unknown; state `missing`; kind `unknown`" in rendered

    def test_benchmark_smoke(self):
        """Smoke test: run_benchmarks exits cleanly."""
        result = subprocess.run(
            [sys.executable, "runtime/run_benchmarks.py"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=Path(__file__).resolve().parent.parent,
        )
        assert result.returncode == 0, (
            f"Benchmarks failed (exit {result.returncode}):\n{result.stderr}"
        )

    def test_schema_validation(self):
        """Smoke test: validate_schemas exits cleanly."""
        result = subprocess.run(
            [sys.executable, "runtime/validate_schemas.py"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=Path(__file__).resolve().parent.parent,
        )
        assert result.returncode == 0, (
            f"Schema validation failed (exit {result.returncode}):\n{result.stderr}"
        )

    def test_health_check_selftest(self):
        """Smoke test: health_check --self-test exits cleanly."""
        result = subprocess.run(
            [sys.executable, "runtime/health_check.py", "--self-test"],
            capture_output=True,
            text=True,
            timeout=300,
            cwd=Path(__file__).resolve().parent.parent,
        )
        assert result.returncode == 0, (
            f"Health check self-test failed (exit {result.returncode}):\n"
            f"{result.stderr}\n{result.stdout[:500]}"
        )

    def test_report_schema_conformance(self):
        """Verify that runner output conforms to the report schema."""
        case = Path(__file__).resolve().parent / "cases" / "ai_startup.yaml"
        report = run_runner(case)

        # Required top-level keys
        required_keys = {
            "report_version", "project", "classification", "gate",
            "opportunities", "do_not_apply", "coverage_gaps", "missing_proof",
            "execution_plan",
        }
        missing = required_keys - set(report.keys())
        assert not missing, f"Report missing required keys: {missing}"

        # Classification
        cls = report.get("classification", {})
        assert "stage" in cls and "confidence" in cls

        # Gate fields
        gate = report.get("gate", {})
        gate_fields = {
            "project_fit", "stage_compatible", "status_verified", "application_endpoint_exists",
            "mechanism_identified", "evidence_requirements_known",
            "next_action_exists", "passed",
        }
        missing_gate = gate_fields - set(gate.keys())
        assert not missing_gate, f"Gate missing fields: {missing_gate}"

        # Each opportunity must have required fields
        for opp in report.get("opportunities", []):
            opp_fields = {
                "program_id", "program", "status", "score", "decision",
                "mechanism", "gate", "why", "missing", "next_action",
                "stop_condition", "decision_trace", "official_source",
                "last_checked",
            }
            missing_opp = opp_fields - set(opp.keys())
            assert not missing_opp, (
                f"Opportunity '{opp.get('program_id')}' missing: {missing_opp}"
            )
            assert opp.get("score", -1) >= 0, f"Negative score for {opp.get('program_id')}"

        # do_not_apply entries must also have the same fields
        for dna in report.get("do_not_apply", []):
            dna_fields = {
                "program_id", "program", "status", "score", "decision",
                "mechanism", "gate", "why", "missing", "next_action",
                "stop_condition", "decision_trace", "official_source",
                "last_checked",
            }
            missing_dna = dna_fields - set(dna.keys())
            assert not missing_dna, (
                f"do_not_apply '{dna.get('program_id')}' missing: {missing_dna}"
            )

        # Execution plan has required time buckets
        plan = report.get("execution_plan", {})
        for bucket in ("days_7", "days_30", "days_90"):
            assert bucket in plan, f"Execution plan missing {bucket}"

    def test_unknown_stage_requires_verification(self):
        case = Path(__file__).resolve().parent / "cases" / "ai_stage_unknown.yaml"
        report = run_runner(case)
        routes = {item["program_id"]: item for item in report.get("opportunities", [])}
        aws = routes["aws-activate"]
        assert aws["decision"] == "VERIFY_FIRST"
        assert aws["gate"]["project_fit"] is True
        assert aws["gate"]["stage_compatible"] is False
        assert "verified project stage" in aws["missing"]

    def test_known_stage_mismatch_is_rejected(self):
        case = Path(__file__).resolve().parent / "cases" / "ai_stage_mismatch.yaml"
        project = load_yaml(case)
        card = load_card_yaml(REPO_ROOT / "knowledge" / "packs" / "ai" / "programs" / "aws-activate.yaml")
        aws = evaluate(project, card)
        assert aws["decision"] == "DO_NOT_APPLY"
        assert aws["gate"]["project_fit"] is False
        assert aws["gate"]["stage_compatible"] is False
        assert "stage_mismatch (-20)" in aws["decision_trace"]["negative"]
        assert not any(item.startswith("no_native_fit") for item in aws["decision_trace"]["negative"])
