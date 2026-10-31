"""Adversarial, fully synthetic PE/2025 source-local normalizer checks."""
from __future__ import annotations

import csv
from hashlib import sha256
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_parcan_pe2025_local as pe2025
from build_parcan_local_processes import IngestError


def synthetic_source(rows):
    out = StringIO(newline="")
    writer = csv.writer(out)
    writer.writerow(["ID_INICIATIVA", "LEGISLATURA", "EXTRACTO", "F_CREACION",
                     "SITUACION", "PROCEDIMIENTO", "TIPO_FINALIZACION", "TIPO_DESCRIPCION"])
    for row in rows:
        writer.writerow([row[0], "11", "PRIVATE_PERSON_SENTINEL", row[1],
                         "OUTCOME_SENTINEL", "procedure", "SECRET_FINAL", "type"])
    return out.getvalue().encode("utf-8")


def test_destination_guard_rejects_repo_existing_and_escape():
    for where in (pe2025.REPO, pe2025.REPO / "data" / "raw",
                  pe2025.APPROVED_ROOT.parent / "elsewhere"):
        with pytest.raises(IngestError):
            pe2025.safe_out(where)
    with tempfile.TemporaryDirectory(dir=pe2025.APPROVED_ROOT) as tmp:
        with pytest.raises(IngestError):
            pe2025.safe_out(Path(tmp))
        assert pe2025.safe_out(Path(tmp) / "new") == Path(tmp) / "new"


def test_synthetic_rows_export_only_source_id_creation_and_explicit_unknowns(monkeypatch):
    fake = synthetic_source([(f"test-{i:03d}", "2025-02-11") for i in range(543)])
    monkeypatch.setattr(pe2025, "eligible_input", lambda _: (fake, "2026-10-31T05:00:00+00:00"))
    monkeypatch.setattr(pe2025, "SOURCE_SHA256", sha256(fake).hexdigest())
    monkeypatch.setattr(pe2025, "METADATA_SHA256", "0" * 64)
    monkeypatch.setattr(pe2025, "CAPTURE_SHA256", "1" * 64)
    with tempfile.TemporaryDirectory(dir=pe2025.APPROVED_ROOT) as tmp:
        result = pe2025.build(originals_dir=Path(tmp), output_dir=Path(tmp) / "new")
        assert result["rows"] == 543 and result["ABH_cycles"] == 0
        payload = (Path(tmp) / "new" / "pe2025_source_local_metadata.jsonl").read_text(encoding="utf-8")
        for forbidden in ("PRIVATE_PERSON_SENTINEL", "OUTCOME_SENTINEL", "SECRET_FINAL"):
            assert forbidden not in payload
        one = json.loads(payload.splitlines()[0])
        assert one["first_public_at"] is None
        assert one["terminal_state"] is None and one["transition_events"] is None
        assert one["outcome_fields_analyzed"] is False
        assert one["source_capture_utc"] == "2026-10-31T05:00:00+00:00"
        assert one["recorded_at"] >= one["source_capture_utc"]
        report = json.loads((Path(tmp) / "new" / "receipt.json").read_text(encoding="utf-8"))
        assert report["population_complete"] is False
        assert report["historical_asof_admitted"] is False


def test_duplicate_source_ids_rejected_even_if_outcomes_differ(monkeypatch):
    fake = synthetic_source([("same-id", "2025-02-01"), ("same-id", "2025-02-02")])
    monkeypatch.setattr(pe2025, "eligible_input", lambda _: (fake, "2026-10-31T05:40:00+00:00"))
    monkeypatch.setattr(pe2025, "SOURCE_SHA256", sha256(fake).hexdigest())
    with tempfile.TemporaryDirectory(dir=pe2025.APPROVED_ROOT) as tmp:
        with pytest.raises(IngestError, match="DUPLICATED_SOURCE_PROCESS_ID"):
            pe2025.build(originals_dir=Path(tmp), output_dir=Path(tmp) / "new")


def test_future_creation_is_not_backdated(monkeypatch):
    fake = synthetic_source([("future-id", "2027-01-01")])
    monkeypatch.setattr(pe2025, "eligible_input", lambda _: (fake, "2026-10-31T05:40:00+00:00"))
    monkeypatch.setattr(pe2025, "SOURCE_SHA256", sha256(fake).hexdigest())
    with tempfile.TemporaryDirectory(dir=pe2025.APPROVED_ROOT) as tmp:
        with pytest.raises(IngestError, match="CREATED_AFTER_SOURCE_CAPTURE"):
            pe2025.build(originals_dir=Path(tmp), output_dir=Path(tmp) / "new")
