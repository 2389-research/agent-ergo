"""Deterministic tests of the metadata checker, not evaluations of model behavior."""
from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1]
SCRIPT = SKILL / "scripts" / "validate_traceability.py"
spec = importlib.util.spec_from_file_location("traceability", SCRIPT)
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)
EXAMPLE = json.loads((SKILL / "assets" / "traceability.example.json").read_text())


class ManifestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = deepcopy(EXAMPLE)

    def assert_invalid(self, fragment: str, root: Path | None = None) -> None:
        errors = validator.validate_manifest(self.data, root)
        self.assertTrue(any(fragment in error for error in errors), errors)

    def test_example_valid(self) -> None:
        self.assertEqual(validator.validate_manifest(self.data), [])

    def test_noop_valid(self) -> None:
        self.data["findings"] = []
        self.data["changes"] = []
        self.data["checks"] = [self.data["checks"][0]]
        self.data["checks"][0]["change_ids"] = []
        self.assertEqual(validator.validate_manifest(self.data), [])

    def test_audit_with_proposals_valid(self) -> None:
        self.data["mode"] = "audit"
        self.data["completion"]["status"] = "audit-complete"
        self.data["changes"][0]["status"] = "proposed"
        self.data["findings"][0]["disposition"] = "proposed"
        self.assertEqual(validator.validate_manifest(self.data), [])

    def test_complete_audit_can_report_failures(self) -> None:
        self.data["mode"] = "audit"
        self.data["completion"]["status"] = "audit-complete"
        self.data["changes"][0]["status"] = "proposed"
        self.data["findings"][0]["disposition"] = "unresolved"
        self.data["checks"][0]["status"] = "fail"
        self.assertEqual(validator.validate_manifest(self.data), [])

    def test_audit_cannot_apply(self) -> None:
        self.data["mode"] = "audit"
        self.assert_invalid("audit mode cannot declare applied")

    def test_docs_mode_cannot_change_implementation(self) -> None:
        for surface in ("implementation", "mixed"):
            with self.subTest(surface=surface):
                self.data["changes"][0]["surface"] = surface
                self.assert_invalid("outside improve-docs")

    def test_schema_boolean_rejected(self) -> None:
        self.data["schema_version"] = True
        self.assert_invalid("expected integer 1")

    def test_unknown_field_rejected(self) -> None:
        self.data["changes"][0]["acceptence"] = "typo"
        self.assert_invalid("unknown fields")

    def test_duplicate_identifiers_rejected(self) -> None:
        self.data["findings"][0]["id"] = "S-01"
        self.assert_invalid("duplicate identifier")

    def test_invalid_identifier_rejected(self) -> None:
        self.data["findings"][0]["id"] = "bad id"
        self.assert_invalid("invalid identifier")

    def test_malformed_shapes_do_not_crash(self) -> None:
        for value in (None, [], 4, "bad", {"mode": ["bad"]}):
            with self.subTest(value=value):
                self.assertTrue(validator.validate_manifest(value))
        for field in ("sources", "findings", "changes", "checks"):
            with self.subTest(field=field):
                data = deepcopy(EXAMPLE)
                data[field] = [None, [], {"id": []}]
                self.assertTrue(validator.validate_manifest(data))

    def test_invalid_enum_shapes_do_not_crash(self) -> None:
        self.data["changes"][0]["surface"] = {"bad": True}
        self.data["checks"][0]["status"] = ["pass"]
        self.assert_invalid("expected one of")

    def test_source_is_required(self) -> None:
        self.data["sources"] = []
        self.assert_invalid("at least one attributable source")

    def test_source_reference_must_exist(self) -> None:
        self.data["findings"][0]["evidence"] = ["S-missing"]
        self.assert_invalid("unknown reference S-missing")

    def test_finding_reference_must_exist(self) -> None:
        self.data["changes"][0]["finding_ids"] = ["F-missing"]
        self.assert_invalid("unknown reference F-missing")

    def test_check_reference_must_exist(self) -> None:
        self.data["checks"][0]["change_ids"] = ["C-missing"]
        self.assert_invalid("unknown reference C-missing")

    def test_missing_evidence_rejected(self) -> None:
        self.data["checks"][0]["evidence"] = "   "
        self.assert_invalid("expected non-empty text")

    def test_duplicate_reference_rejected(self) -> None:
        self.data["changes"][0]["finding_ids"] = ["F-01", "F-01"]
        self.assert_invalid("duplicate entries")

    def test_high_open_finding_prevents_complete(self) -> None:
        self.data["findings"][0]["disposition"] = "unresolved"
        self.assert_invalid("unresolved high severity")

    def test_low_deferred_finding_requires_disclosure(self) -> None:
        self.data["findings"][0]["severity"] = "low"
        self.data["findings"][0]["disposition"] = "deferred"
        self.data["checks"] = self.data["checks"][:1]
        self.data["completion"]["limitations"] = []
        self.assert_invalid("disclose findings left open")

    def test_addressed_requires_applied_changes(self) -> None:
        self.data["changes"][0]["status"] = "proposed"
        self.assert_invalid("addressed requires all linked changes")

    def test_addressed_requires_passing_required_checks(self) -> None:
        self.data["checks"][0]["status"] = "fail"
        self.assert_invalid("addressed requires passing completion checks")

    def test_proposed_disposition_requires_proposed_change(self) -> None:
        self.data["findings"][0]["disposition"] = "proposed"
        self.assert_invalid("proposed disposition needs a proposed change")

    def test_change_needs_acceptance_check(self) -> None:
        self.data["checks"] = []
        self.assert_invalid("no acceptance check is linked")

    def test_applied_change_needs_required_check(self) -> None:
        self.data["checks"][0]["required_for_completion"] = False
        self.assert_invalid("applied change needs a required completion check")

    def test_required_flag_is_boolean(self) -> None:
        self.data["checks"][0]["required_for_completion"] = "false"
        self.assert_invalid("expected a boolean")

    def test_failed_or_unrun_checks_require_disclosure(self) -> None:
        self.data["completion"]["limitations"] = []
        self.assert_invalid("disclose failed, blocked, or unrun checks")

    def test_optional_runtime_not_run_does_not_block_document_completion(self) -> None:
        self.assertEqual(validator.validate_manifest(self.data), [])

    def test_implementation_completion_needs_runtime(self) -> None:
        self.data["mode"] = "implement"
        self.data["changes"][0]["surface"] = "implementation"
        self.assert_invalid("implementation completion needs a required passing runtime check")

    def test_implementation_completion_with_runtime_valid(self) -> None:
        self.data["mode"] = "implement"
        self.data["changes"][0]["surface"] = "mixed"
        self.data["checks"][1]["status"] = "pass"
        self.data["checks"][1]["required_for_completion"] = True
        self.assertEqual(validator.validate_manifest(self.data), [])

    def test_partial_requires_limitation(self) -> None:
        self.data["completion"]["status"] = "partial"
        self.data["completion"]["limitations"] = []
        self.assert_invalid("describe why work is partial or blocked")

    def test_audit_complete_requires_audit_mode(self) -> None:
        self.data["completion"]["status"] = "audit-complete"
        self.assert_invalid("audit-complete requires audit mode")

    def test_audit_uses_own_completion_label(self) -> None:
        self.data["mode"] = "audit"
        self.data["changes"][0]["status"] = "proposed"
        self.data["findings"][0]["disposition"] = "proposed"
        self.assert_invalid("use audit-complete")

    def test_self_dependency_cycle_rejected(self) -> None:
        self.data["changes"][0]["depends_on"] = ["C-01"]
        self.assert_invalid("dependency cycle detected")

    def test_two_node_cycle_rejected(self) -> None:
        second = deepcopy(self.data["changes"][0])
        second["id"] = "C-02"
        second["depends_on"] = ["C-01"]
        self.data["changes"][0]["depends_on"] = ["C-02"]
        self.data["changes"].append(second)
        self.data["checks"][0]["change_ids"].append("C-02")
        self.assert_invalid("dependency cycle detected")

    def test_unknown_dependency_rejected(self) -> None:
        self.data["changes"][0]["depends_on"] = ["C-missing"]
        self.assert_invalid("unknown reference C-missing")

    def test_applied_dependency_cannot_be_proposed(self) -> None:
        second = deepcopy(self.data["changes"][0])
        second["id"] = "C-02"
        second["status"] = "proposed"
        self.data["changes"].append(second)
        self.data["changes"][0]["depends_on"] = ["C-02"]
        self.data["checks"][0]["change_ids"].append("C-02")
        self.assert_invalid("applied change depends on a proposed change")

    def test_large_dependency_chain_nonrecursive(self) -> None:
        base = deepcopy(self.data["changes"][0])
        self.data["changes"] = []
        for index in range(1100):
            change = deepcopy(base)
            change["id"] = f"C-{index:04d}"
            change["depends_on"] = [f"C-{index - 1:04d}"] if index else []
            self.data["changes"].append(change)
        self.data["checks"][0]["change_ids"] = [c["id"] for c in self.data["changes"]]
        self.data["checks"][1]["change_ids"] = []
        self.assertEqual(validator.validate_manifest(self.data), [])

    def test_unsafe_local_paths_rejected(self) -> None:
        source = self.data["sources"][0]
        source["kind"] = "local"
        for path in ("/etc/passwd", "../secret", "docs/../../secret", "C:/secret", "docs\\x", "~/.env", ".", "a\x00b"):
            with self.subTest(path=path):
                source["location"] = path
                self.assert_invalid("repository-relative POSIX path")

    def test_existing_local_sources_and_targets(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "design.md").write_text("# Retry policy\n")
            self.data["sources"][0].update(kind="local", location="design.md")
            self.data["changes"][0]["targets"][0].update(kind="local", location="design.md")
            self.assertEqual(validator.validate_manifest(self.data, root), [])
            self.data["sources"][0]["location"] = "missing.md"
            self.assert_invalid("local file does not exist", root)

    def test_missing_applied_target_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.data["changes"][0]["targets"][0].update(kind="local", location="missing.md")
            self.assert_invalid("local file does not exist", Path(directory))

    def test_missing_proposed_target_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.data["mode"] = "audit"
            self.data["completion"]["status"] = "audit-complete"
            self.data["findings"][0]["disposition"] = "proposed"
            self.data["changes"][0]["status"] = "proposed"
            self.data["changes"][0]["targets"][0].update(kind="local", location="new.md")
            self.assertEqual(validator.validate_manifest(self.data, Path(directory)), [])

    def test_symlink_escape_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory, tempfile.TemporaryDirectory() as outside:
            root = Path(directory)
            target = Path(outside) / "secret.md"
            target.write_text("sensitive")
            (root / "linked.md").symlink_to(target)
            self.data["sources"][0].update(kind="local", location="linked.md")
            self.assert_invalid("escapes --root", root)

    def test_invalid_root_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            self.assert_invalid("cannot resolve an existing directory", Path(directory) / "missing")

    def test_noop_complete_still_requires_a_check(self) -> None:
        self.data["findings"] = []
        self.data["changes"] = []
        self.data["checks"] = []
        self.assert_invalid("completion requires at least one recorded check")

    def run_cli(self, content: bytes) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_bytes(content)
            before = manifest.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), str(manifest)],
                                    capture_output=True, text=True, timeout=10, check=False)
            self.assertEqual(manifest.read_bytes(), before)
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ["manifest.json"])
            return result

    def test_cli_success_reports_limited_scope(self) -> None:
        result = self.run_cli(json.dumps(self.data).encode())
        self.assertEqual(result.returncode, 0, result.stderr)
        output = json.loads(result.stdout)
        self.assertTrue(output["valid"])
        self.assertIn("Metadata only", output["validation_scope"])

    def test_cli_invalid_manifest_exit_one(self) -> None:
        result = self.run_cli(b'{"schema_version": 9}')
        self.assertEqual(result.returncode, 1)
        self.assertFalse(json.loads(result.stdout)["valid"])

    def test_cli_rejects_invalid_json_and_encoding(self) -> None:
        for content in (b'{"x":}', b'{"x":1,"x":2}', b'{"x":NaN}', b'{"x":Infinity}', b'\xff'):
            with self.subTest(content=content):
                result = self.run_cli(content)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertFalse(json.loads(result.stdout)["valid"])

    def test_cli_input_limit(self) -> None:
        result = self.run_cli(b" " * (validator.MAX_BYTES + 1))
        self.assertEqual(result.returncode, 2)
        self.assertIn("input limit", result.stdout)

    def test_cli_missing_file_exit_two(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(SCRIPT), str(Path(directory) / "absent.json")],
                                    capture_output=True, text=True, timeout=10, check=False)
            self.assertEqual(result.returncode, 2)
            self.assertFalse(json.loads(result.stdout)["valid"])


if __name__ == "__main__":
    unittest.main()
