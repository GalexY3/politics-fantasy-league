"""Fail-closed boundaries; never invokes a real PDF or the public network."""
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_pan_iaen_2024_offline.py"


def run(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                          cwd=ROOT, capture_output=True, text=True, timeout=20)


def test_repo_cannot_be_used_as_raw_or_output_destination(tmp_path):
    response = run("--raw-root", ROOT, "--output-dir", ROOT / "forbidden_output")
    assert response.returncode != 0
    assert "ORIGINALS_OR_DERIVATIVES_INSIDE_GIT_PROHIBITED" in response.stderr
    assert not (ROOT / "forbidden_output").exists()


def test_foreign_pdf_bytes_fail_sha_before_any_parsing(tmp_path):
    (tmp_path / "PAN_2024.pdf").write_bytes(b"%PDF-1.7\nFAKE FIXTURE NOT A GOVERNMENT DOCUMENT\n")
    target = tmp_path / "derived"
    response = run("--raw-root", tmp_path, "--output-dir", target)
    assert response.returncode != 0
    assert "OFFICIAL_EXACT_ASSET_SHA_MISMATCH" in response.stderr
    assert not target.exists()


def test_existing_private_output_is_not_overwritten(tmp_path):
    (tmp_path / "derived").mkdir()
    response = run("--raw-root", tmp_path, "--output-dir", tmp_path / "derived")
    assert response.returncode != 0
    assert "OUTPUT_MUST_BE_NEW_SUBDIRECTORY" in response.stderr
