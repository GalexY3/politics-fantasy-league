"""Test and snapshot source code hashes before any real CSV coverage processing."""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
RUN = ROOT / "runs" / "2026-10-31"
FILES = (
    "capture_parcan.py", "capture_pplm_2024.py", "capture_pe_2026.py",
    "coverage_only.py", "test_coverage_only.py", "ingest_offline.py", "freeze.py"
)


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    RUN.mkdir(parents=True, exist_ok=True)
    if (RUN / "frozen_code.json").exists():
        raise ValueError("ALREADY_FROZEN")
    command = [sys.executable, "-m", "unittest", "-v", "test_coverage_only.py"]
    proc = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, timeout=30)
    text = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0 or "Ran 10 tests" not in text or "\nOK" not in text:
        raise ValueError("TESTS_FAILED_DO_NOT_FREEZE")
    log = RUN / "tests_log.txt"
    with log.open("x", encoding="utf-8", newline="\n") as f:
        f.write(text)
    receipt = {
        "freeze_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "tests_command": "python -m unittest -v test_coverage_only.py",
        "tests_returncode": proc.returncode,
        "test_count": 10,
        "tests_passed": True,
        "test_log_sha256": hash_file(log),
        "code_sha256": {name: hash_file(ROOT / name) for name in FILES},
        "capture_took_place_before_code_freeze": True,
        "real_outcome_analysis_performed_before_freeze": False,
        "scope": "offline metadata only; outcomes currently off-limits to confirmatory AB-H",
    }
    with (RUN / "frozen_code.json").open("x", encoding="utf-8", newline="\n") as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")
    print(json.dumps({"tests_passed": True, "test_count": 10,
                      "freeze_utc": receipt["freeze_utc"],
                      "code_sha256": receipt["code_sha256"]}, indent=2))


if __name__ == "__main__":
    if sys.argv[1:] != ["freeze"]:
        print("Usage: python freeze.py freeze", file=sys.stderr)
        sys.exit(2)
    main()
