"""Offline, isolated Git-fixture tests for the exhaustive tracked-byte audit."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("pfl_session_context", ROOT / "scripts/session_context.py")
context = importlib.util.module_from_spec(spec)
assert spec.loader
spec.loader.exec_module(context)


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True)


def test_hashes_every_tracked_byte_but_does_not_claim_semantic_reading(monkeypatch):
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        git(root, "init", "-q")
        (root / "AGENTS.md").write_text("Normas", encoding="utf-8")
        (root / "área").mkdir()
        (root / "área" / "expediente.md").write_text("Criterio falso: not a fact", encoding="utf-8")
        (root / "PROJECT_INDEX.json").write_text(json.dumps({"files": [
            {"path": "AGENTS.md"}, {"path": "área/expediente.md"}]}), encoding="utf-8")
        (root / "data" / "local_field").mkdir(parents=True)
        (root / "data" / "local_field" / "SECRET.txt").write_text("NO TOCAR", encoding="utf-8")
        git(root, "add", "AGENTS.md", "PROJECT_INDEX.json", "área/expediente.md")
        git(root, "-c", "user.email=test@example.invalid", "-c", "user.name=Test",
            "commit", "-q", "-m", "fixture")
        monkeypatch.setattr(context, "MANDATORY_SEMANTIC_ENTRY", ("AGENTS.md",))
        first = context.audit(root, inventory=True)
        assert first["ok"] is True
        assert first["tracked_paths"] == first["files_successfully_hashed"] == 3
        assert first["index_membership_expected"] == 2
        assert first["worktree_clean"] is False  # untracked private file
        assert first["semantic_review_attested"] is False
        assert first["semantic_reading_evidence"] == []
        assert first["private_local_files_inspected"] is False
        assert "SECRET" not in json.dumps(first)
        assert any(x["path"] == "área/expediente.md" for x in first["per_file_manifest"])

        (root / "área" / "expediente.md").write_text("Otra afirmación no verificada", encoding="utf-8")
        second = context.audit(root)
        assert second["per_file_manifest_sha256"] != first["per_file_manifest_sha256"]
        assert second["semantic_review_attested"] is False


def test_missing_index_member_fails_even_when_all_bytes_are_hashed(monkeypatch):
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        git(root, "init", "-q")
        (root / "AGENTS.md").write_text("a", encoding="utf-8")
        (root / "PROJECT_INDEX.json").write_text('{"files": []}', encoding="utf-8")
        git(root, "add", ".")
        git(root, "-c", "user.email=test@example.invalid", "-c", "user.name=Test",
            "commit", "-q", "-m", "fixture")
        monkeypatch.setattr(context, "MANDATORY_SEMANTIC_ENTRY", ("AGENTS.md",))
        report = context.audit(root)
        assert report["files_successfully_hashed"] == 2
        assert report["ok"] is False
        assert report["index_membership_missing"] == ["AGENTS.md"]
        assert "INDEX_MEMBERSHIP_DIFFERENCE" in report["problems"]


def test_missing_semantic_entry_is_explicit_falsator(monkeypatch):
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        git(root, "init", "-q")
        (root / "PROJECT_INDEX.json").write_text('{"files": []}', encoding="utf-8")
        git(root, "add", ".")
        git(root, "-c", "user.email=test@example.invalid", "-c", "user.name=Test",
            "commit", "-q", "-m", "fixture")
        monkeypatch.setattr(context, "MANDATORY_SEMANTIC_ENTRY", ("AGENTS.md",))
        report = context.audit(root)
        assert not report["ok"]
        assert report["anchors_missing"] == ["AGENTS.md"]


def test_guide_link_audit_distinguishes_broken_internal_and_unverified_external(monkeypatch):
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary).resolve()
        (root / "AGENTS.md").write_text(
            "[válido](SISTEMA_ESPA%C3%91OL.md) "
            "[roto](no-existe.md) [fuera](../otra-ruta/informe.md)", encoding="utf-8")
        (root / "SISTEMA_ESPAÑOL.md").write_text("válido", encoding="utf-8")
        monkeypatch.setattr(context, "MANDATORY_SEMANTIC_ENTRY", ("AGENTS.md",))
        errors, outside = context.guide_link_audit(root, {"AGENTS.md"})
        assert len(errors) == 1 and "no-existe.md" in errors[0]
        assert len(outside) == 1 and "otra-ruta" in outside[0]
