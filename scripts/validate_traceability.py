#!/usr/bin/env python3
"""Read-only, standard-library validator for an optional design change manifest.

Validate declared traceability, not the truth of evidence or runtime correctness.
Exit codes: 0 valid, 1 invalid manifest, 2 input or argument error.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path, PurePosixPath
import re
import sys
from typing import Any

MAX_BYTES = 4 * 1024 * 1024
ID_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]{0,127}$")


def validate_manifest(data: Any, root: Path | None = None) -> list[str]:
    """Return all detected metadata errors without changing files or running tools."""
    errors: list[str] = []
    all_ids: set[str] = set()

    def shape(value: Any, label: str, fields: set[str]) -> dict[str, Any]:
        if not isinstance(value, dict):
            errors.append(f"{label}: expected an object")
            return {}
        missing = fields - value.keys()
        extra = value.keys() - fields
        if missing:
            errors.append(f"{label}: missing fields: {', '.join(sorted(missing))}")
        if extra:
            errors.append(f"{label}: unknown fields: {', '.join(sorted(extra))}")
        return value

    def text(value: Any, label: str) -> bool:
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{label}: expected non-empty text")
            return False
        return True

    def choice(value: Any, label: str, options: set[str]) -> None:
        if not isinstance(value, str) or value not in options:
            errors.append(f"{label}: expected one of {', '.join(sorted(options))}")

    def texts(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
        if not isinstance(value, list):
            errors.append(f"{label}: expected an array")
            return []
        if nonempty and not value:
            errors.append(f"{label}: must not be empty")
        result = []
        for index, item in enumerate(value):
            if text(item, f"{label}[{index}]"):
                result.append(item)
        if len(result) != len(set(result)):
            errors.append(f"{label}: duplicate entries")
        return result

    def records(value: Any, label: str, fields: set[str]) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            errors.append(f"{label}: expected an array")
            return []
        result = []
        for index, item in enumerate(value):
            item_label = f"{label}[{index}]"
            record = shape(item, item_label, fields)
            identifier = record.get("id")
            if text(identifier, f"{item_label}.id"):
                if not ID_PATTERN.fullmatch(identifier):
                    errors.append(f"{item_label}.id: invalid identifier format")
                if identifier in all_ids:
                    errors.append(f"{item_label}.id: duplicate identifier")
                all_ids.add(identifier)
            result.append(record)
        return result

    def local_path(value: Any, label: str, *, must_exist: bool) -> None:
        if not isinstance(value, str) or not value.strip():
            return  # The caller reports missing/empty location.
        path = PurePosixPath(value)
        if (path.is_absolute() or ".." in path.parts or not path.parts
                or "\\" in value or "\x00" in value or value.startswith("~")
                or re.match(r"^[A-Za-z]:", value)):
            errors.append(f"{label}: use a confined, repository-relative POSIX path")
            return
        if root is not None:
            try:
                resolved = (root / value).resolve()
                resolved.relative_to(root)
                if must_exist and not resolved.is_file():
                    errors.append(f"{label}: local file does not exist under --root")
            except ValueError:
                errors.append(f"{label}: path escapes --root through a symbolic link")
            except (OSError, RuntimeError):
                errors.append(f"{label}: local path cannot be resolved safely")

    def location(record: dict[str, Any], label: str, *, must_exist: bool) -> None:
        choice(record.get("kind"), f"{label}.kind", {"local", "remote", "inline"})
        text(record.get("location"), f"{label}.location")
        text(record.get("anchor"), f"{label}.anchor")
        if record.get("kind") == "local":
            local_path(record.get("location"), f"{label}.location", must_exist=must_exist)

    if root is not None:
        try:
            root = Path(root).resolve(strict=True)
            if not root.is_dir():
                return ["--root: expected an existing directory"]
        except (OSError, RuntimeError):
            return ["--root: cannot resolve an existing directory"]

    data = shape(data, "$", {"schema_version", "mode", "scope", "sources", "findings",
                              "changes", "checks", "completion"})
    if type(data.get("schema_version")) is not int or data.get("schema_version") != 1:
        errors.append("schema_version: expected integer 1")
    mode = data.get("mode")
    choice(mode, "mode", {"improve-docs", "audit", "implement"})
    scope = shape(data.get("scope"), "scope", {"summary", "baseline"})
    text(scope.get("summary"), "scope.summary")
    text(scope.get("baseline"), "scope.baseline")

    source_fields = {"id", "kind", "location", "anchor", "version"}
    sources = records(data.get("sources"), "sources", source_fields)
    if not sources:
        errors.append("sources: at least one attributable source is required")
    for index, source in enumerate(sources):
        location(source, f"sources[{index}]", must_exist=True)
        text(source.get("version"), f"sources[{index}].version")

    finding_fields = {"id", "severity", "disposition", "claim", "evidence", "rationale"}
    findings = records(data.get("findings"), "findings", finding_fields)
    finding_refs: list[list[str]] = []
    for index, finding in enumerate(findings):
        label = f"findings[{index}]"
        choice(finding.get("severity"), f"{label}.severity", {"blocker", "high", "medium", "low"})
        choice(finding.get("disposition"), f"{label}.disposition",
               {"addressed", "proposed", "deferred", "unresolved", "not-applicable"})
        text(finding.get("claim"), f"{label}.claim")
        text(finding.get("rationale"), f"{label}.rationale")
        finding_refs.append(texts(finding.get("evidence"), f"{label}.evidence", nonempty=True))

    change_fields = {"id", "finding_ids", "summary", "surface", "status", "targets",
                     "depends_on", "acceptance"}
    changes = records(data.get("changes"), "changes", change_fields)
    change_findings: list[list[str]] = []
    dependencies: list[list[str]] = []
    for index, change in enumerate(changes):
        label = f"changes[{index}]"
        change_findings.append(texts(change.get("finding_ids"), f"{label}.finding_ids", nonempty=True))
        dependencies.append(texts(change.get("depends_on"), f"{label}.depends_on"))
        text(change.get("summary"), f"{label}.summary")
        text(change.get("acceptance"), f"{label}.acceptance")
        choice(change.get("surface"), f"{label}.surface", {"documentation", "implementation", "mixed"})
        choice(change.get("status"), f"{label}.status", {"applied", "proposed"})
        if mode == "audit" and change.get("status") == "applied":
            errors.append(f"{label}: audit mode cannot declare applied changes")
        if mode == "improve-docs" and change.get("surface") in ("implementation", "mixed"):
            errors.append(f"{label}: implementation surface is outside improve-docs mode")
        targets = change.get("targets")
        if not isinstance(targets, list) or not targets:
            errors.append(f"{label}.targets: expected a non-empty array")
        else:
            for target_index, target in enumerate(targets):
                target_label = f"{label}.targets[{target_index}]"
                target = shape(target, target_label, {"kind", "location", "anchor"})
                location(target, target_label, must_exist=change.get("status") == "applied")

    check_fields = {"id", "change_ids", "kind", "status", "required_for_completion", "description", "evidence"}
    checks = records(data.get("checks"), "checks", check_fields)
    check_refs: list[list[str]] = []
    for index, check in enumerate(checks):
        label = f"checks[{index}]"
        check_refs.append(texts(check.get("change_ids"), f"{label}.change_ids"))
        choice(check.get("kind"), f"{label}.kind", {"structural", "walkthrough", "runtime"})
        choice(check.get("status"), f"{label}.status", {"pass", "fail", "not-run", "blocked"})
        if type(check.get("required_for_completion")) is not bool:
            errors.append(f"{label}.required_for_completion: expected a boolean")
        text(check.get("description"), f"{label}.description")
        text(check.get("evidence"), f"{label}.evidence")

    completion = shape(data.get("completion"), "completion", {"status", "summary", "limitations"})
    status = completion.get("status")
    choice(status, "completion.status", {"complete", "partial", "blocked", "audit-complete"})
    text(completion.get("summary"), "completion.summary")
    limitations = texts(completion.get("limitations"), "completion.limitations")
    if status == "audit-complete" and mode != "audit":
        errors.append("completion.status: audit-complete requires audit mode")
    if status == "complete" and mode == "audit":
        errors.append("completion.status: use audit-complete for a completed audit")
    if status in ("partial", "blocked") and not limitations:
        errors.append("completion.limitations: describe why work is partial or blocked")
    if any(check.get("status") != "pass" for check in checks) and not limitations:
        errors.append("completion.limitations: disclose failed, blocked, or unrun checks")

    # Stop before relationship checks if malformed fields could cause unsafe access.
    if errors:
        return errors

    source_by_id = {s["id"]: s for s in sources}
    finding_by_id = {f["id"]: f for f in findings}
    change_by_id = {c["id"]: c for c in changes}

    def references(ids: list[str], registry: dict[str, Any], label: str) -> None:
        for identifier in ids:
            if identifier not in registry:
                errors.append(f"{label}: unknown reference {identifier}")

    for index, refs in enumerate(finding_refs):
        references(refs, source_by_id, f"findings[{index}].evidence")
    for index, refs in enumerate(change_findings):
        references(refs, finding_by_id, f"changes[{index}].finding_ids")
    for index, refs in enumerate(dependencies):
        references(refs, change_by_id, f"changes[{index}].depends_on")
    for index, refs in enumerate(check_refs):
        references(refs, change_by_id, f"checks[{index}].change_ids")
    if errors:
        return errors

    # Kahn's algorithm avoids recursion limits for large dependency chains.
    pending = {c["id"]: len(c["depends_on"]) for c in changes}
    children: dict[str, list[str]] = {c["id"]: [] for c in changes}
    for change in changes:
        for dependency in change["depends_on"]:
            children[dependency].append(change["id"])
            if change["status"] == "applied" and change_by_id[dependency]["status"] != "applied":
                errors.append(f"change {change['id']}: applied change depends on a proposed change")
    ready = [identifier for identifier, count in pending.items() if count == 0]
    visited = 0
    while ready:
        identifier = ready.pop()
        visited += 1
        for child in children[identifier]:
            pending[child] -= 1
            if pending[child] == 0:
                ready.append(child)
    if visited != len(changes):
        errors.append("changes.depends_on: dependency cycle detected")

    for change in changes:
        associated = [check for check in checks if change["id"] in check["change_ids"]]
        if not associated:
            errors.append(f"change {change['id']}: no acceptance check is linked")
        if change["status"] == "applied" and not any(c["required_for_completion"] for c in associated):
            errors.append(f"change {change['id']}: applied change needs a required completion check")
        if status == "complete" and change["surface"] in ("implementation", "mixed"):
            if not any(c["kind"] == "runtime" and c["status"] == "pass"
                       and c["required_for_completion"] for c in associated):
                errors.append(f"change {change['id']}: implementation completion needs a required passing runtime check")

    for finding in findings:
        associated = [c for c in changes if finding["id"] in c["finding_ids"]]
        if finding["disposition"] == "addressed":
            if not associated or any(c["status"] != "applied" for c in associated):
                errors.append(f"finding {finding['id']}: addressed requires all linked changes to be applied")
            for change in associated:
                required = [c for c in checks if change["id"] in c["change_ids"] and c["required_for_completion"]]
                if not required or any(c["status"] != "pass" for c in required):
                    errors.append(f"finding {finding['id']}: addressed requires passing completion checks")
        if finding["disposition"] == "proposed" and not any(c["status"] == "proposed" for c in associated):
            errors.append(f"finding {finding['id']}: proposed disposition needs a proposed change")
        if status == "complete" and finding["severity"] in ("blocker", "high"):
            if finding["disposition"] not in ("addressed", "not-applicable"):
                errors.append(f"finding {finding['id']}: unresolved high severity prevents complete remediation")
        if status == "complete" and finding["disposition"] in ("proposed", "deferred", "unresolved") and not limitations:
            errors.append("completion.limitations: disclose findings left open or deferred")

    if status in ("complete", "audit-complete") and not checks:
        errors.append("checks: completion requires at least one recorded check")
    if status == "complete":
        if any(c["status"] != "applied" for c in changes):
            errors.append("completion.status: complete remediation cannot contain proposed changes")
        required = [c for c in checks if c["required_for_completion"]]
        if not required or any(c["status"] != "pass" for c in required):
            errors.append("completion.status: every required completion check must pass")
    return errors


def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Reject ambiguity instead of silently accepting the last duplicate JSON key."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON constant: {value}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, help="Check confined local source and applied-target paths.")
    args = parser.parse_args(argv)
    try:
        with args.manifest.open("rb") as handle:
            raw = handle.read(MAX_BYTES + 1)
        if len(raw) > MAX_BYTES:
            raise ValueError("manifest exceeds the 4 MiB input limit")
        data = json.loads(raw.decode("utf-8"), object_pairs_hook=reject_duplicate_keys,
                          parse_constant=reject_constant)
        errors = validate_manifest(data, args.root)
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        print(json.dumps({"valid": False, "error": f"Cannot read manifest: {exc}"}, indent=2))
        return 2
    counts: dict[str, Any] = {}
    if isinstance(data, dict):
        for key in ("sources", "findings", "changes", "checks"):
            if isinstance(data.get(key), list):
                counts[key] = len(data[key])
        check_items = data.get("checks")
        if isinstance(check_items, list):
            counts["check_statuses"] = dict(Counter(
                c["status"] for c in check_items
                if isinstance(c, dict) and isinstance(c.get("status"), str)))
    print(json.dumps({"valid": not errors, "errors": errors, "counts": counts,
                      "validation_scope": "Metadata only; no source truth, semantic consistency, or runtime behavior verified."}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
