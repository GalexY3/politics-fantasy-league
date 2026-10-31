"""Fail-closed normalization of licensed process metadata, no outcome inspection."""
from __future__ import annotations

from datetime import datetime
from hashlib import sha256
from pathlib import Path

import pytest
from scripts.build_parcan_local_processes import (
    IngestError, EXPECTED_HEADERS, build, parse_metadata,
)


CAPTURE = "2026-10-31T05:19:18+00:00"


def csv_fixture(*rows: list[str]) -> bytes:
    import csv
    from io import StringIO
    stream = StringIO(newline="")
    writer = csv.writer(stream)
    writer.writerow(EXPECTED_HEADERS)
    writer.writerows(rows)
    return stream.getvalue().encode("utf-8")


def row(ident="000001", leg="11", created="2024-01-12"):
    return [ident, leg, "Texto PRIVADO que no debe salir", created,
            "ESTADO_TARDIO_NO_PERMITIDO", "TRAMITE", "APROBADA_NO_PERMITIDO", "DESC"]


def test_records_have_only_source_ids_not_statuses_or_future_information():
    raw = csv_fixture(row())
    records, counts = parse_metadata(raw, legislature=11, kind="PE", year=2024,
                                    source_sha=sha256(raw).hexdigest(), captured_utc=CAPTURE)
    assert counts == {"rows":1,"year_mismatch_rows":0,"duplicate_keys_within_distribution":0}
    assert records[0]["source_process_id"] == "000001"
    assert records[0]["created_on"] == "2024-01-12"
    assert records[0]["first_public_at"] is None
    assert records[0]["terminal_state"] is None
    assert records[0]["transition_events"] is None
    assert records[0]["scope_population_certified"] is False
    assert "APROBADA_NO_PERMITIDO" not in str(records)
    assert "Texto PRIVADO" not in str(records)


def test_duplicate_process_identity_within_source_is_rejected():
    raw = csv_fixture(row(),row())
    with pytest.raises(IngestError, match="DUPLICATED_SOURCE_PROCESS_ID"):
        parse_metadata(raw, legislature=11, kind="PE", year=2024,
                       source_sha=sha256(raw).hexdigest(), captured_utc=CAPTURE)


@pytest.mark.parametrize("change,message",[
    ([row(leg="10")], "WRONG_LEGISLATURE"),
    ([row(created="2026-12-31")], "CREATED_AFTER_SOURCE_CAPTURE"),
    ([row(created="2024-13-40")], "BAD_CREATION_DATE"),
    ([row(ident="")], "BAD_INITIATIVE_ID"),
])
def test_corrupt_identity_scope_future_and_date_fail_closed(change,message):
    raw = csv_fixture(*change)
    with pytest.raises(IngestError, match=message):
        parse_metadata(raw, legislature=11, kind="PE", year=2024,
                       source_sha=sha256(raw).hexdigest(), captured_utc=CAPTURE)


def test_source_hash_and_schema_drift_fail_closed():
    raw = csv_fixture(row())
    with pytest.raises(IngestError, match="SOURCE_SHA256_MISMATCH"):
        parse_metadata(raw, legislature=11, kind="PE", year=2024,
                       source_sha="0"*64, captured_utc=CAPTURE)
    bad = raw.replace(b"ID_INICIATIVA", b"PERSON_NAME")
    with pytest.raises(IngestError, match="UNKNOWN_SCHEMA"):
        parse_metadata(bad, legislature=11, kind="PE", year=2024,
                       source_sha=sha256(bad).hexdigest(), captured_utc=CAPTURE)


def test_reject_output_folder_inside_git_and_existing_folder(tmp_path:Path):
    with pytest.raises(IngestError, match="DO_NOT_STORE_SOURCE_ROWS_IN_GIT"):
        build(originals=tmp_path, output=Path(__file__).resolve().parents[1]/"data/local_raw")
    with pytest.raises(IngestError, match="REFUSE_OVERWRITE"):
        build(originals=tmp_path, output=tmp_path)
