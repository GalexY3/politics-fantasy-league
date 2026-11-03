"""NTFS alternate streams are not independently auditable v2 source files.

Only disposable synthetic temp material, real Windows NTFS ADS, one OS token.
An ADS has a separate byte stream despite sharing its base file's inode.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from test_beta_operator_instrument_versioning import _prepared_v2, run_cli


WINDOWS_ADS = pytest.mark.skipif(
    os.name != "nt", reason="Real Windows NTFS alternate data stream")


def _make_ads(path: Path, suffix: str) -> Path:
    stream = Path(str(path) + ":" + suffix)
    with stream.open("wb") as out:
        out.write(path.read_bytes())
    assert stream.is_file()
    assert os.stat(stream).st_ino == os.stat(path).st_ino
    assert os.stat(stream).st_nlink == 1
    assert hashlib.sha256(stream.read_bytes()).hexdigest() == hashlib.sha256(
        path.read_bytes()).hexdigest()
    return stream


@WINDOWS_ADS
def test_prepatch_red_record_form_rejects_private_coded_ntfs_ads_source(tmp_path):
    _, _, _, source, _, _ = _prepared_v2(tmp_path, "ads source Ω")
    stream = _make_ads(source, "alternate_coded")
    output = source.parent / "safe private successor from ADS.json"
    unchanged = source.read_bytes()
    code, report, raw = run_cli(
        "--record-form", stream, output,
        "OP01", "TECH_COMPLETED", "A", "UX_CLEAR")
    if code == 0:
        assert output.is_file()
        assert report["source_sha256"] == hashlib.sha256(stream.read_bytes()).hexdigest()
        assert str(stream) not in raw
    assert code != 0, "NTFS alternate data stream was accepted as coded source"
    assert report["status"] == "OPERATOR_REJECTED"
    assert report["error_code"] == "OPERATOR_PRIVATE_FILE_ALIAS_FORBIDDEN"
    assert not output.exists()
    assert source.read_bytes() == unchanged


@WINDOWS_ADS
def test_prepatch_red_evaluate_form_rejects_private_rubric_ntfs_ads_source(tmp_path):
    _, rubric, _, source, _, rubric_file = _prepared_v2(
        tmp_path, "ads rubric Ω")
    stream = _make_ads(rubric_file, "alternate_rubric")
    successor = source.parent / "pre-existing synthetic revision.json"
    code, _, _ = run_cli(
        "--record-form", source, successor,
        "OP01", "TECH_COMPLETED",
        rubric["tasks"][0]["correct_answer_code"], "UX_CLEAR")
    assert code == 0 and successor.is_file()
    original_revision = successor.read_bytes()
    output = source.parent / "scored with rubric ADS.json"
    code, report, raw = run_cli("--evaluate-form", successor, stream, output)
    if code == 0:
        assert output.is_file()
        assert report["status"] == "OPERATOR_FORM_EVALUATION_EXPORTED"
        assert str(stream) not in raw
    assert code != 0, "NTFS alternate data stream was accepted as secret rubric"
    assert report["status"] == "OPERATOR_REJECTED"
    assert report["error_code"] == "OPERATOR_PRIVATE_FILE_ALIAS_FORBIDDEN"
    assert not output.exists()
    assert successor.read_bytes() == original_revision


def test_normal_named_v2_source_and_rubric_still_evaluate(tmp_path):
    _, rubric, _, source, _, rubric_file = _prepared_v2(
        tmp_path, "normal source Ω")
    successor = source.parent / "normal coded revision.json"
    code, _, _ = run_cli(
        "--record-form", source, successor, "OP01", "TECH_COMPLETED",
        rubric["tasks"][0]["correct_answer_code"], "UX_CLEAR")
    assert code == 0
    score = source.parent / "normal scored result.json"
    rc, receipt, _ = run_cli("--evaluate-form", successor, rubric_file, score)
    assert rc == 0 and receipt["status"] == "OPERATOR_FORM_EVALUATION_EXPORTED"
    assert receipt["sha256"] == hashlib.sha256(score.read_bytes()).hexdigest()
