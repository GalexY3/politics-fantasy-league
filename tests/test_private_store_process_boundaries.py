"""POSIX process-boundary negatives: fictional bytes, no internet or real names."""
import hashlib
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

import pytest

from politics_fantasy.private_audit import audit_private_root

pytestmark = pytest.mark.skipif(os.name != "posix", reason="POSIX subprocess + SIGKILL only")


def _child_env():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(Path(__file__).resolve().parents[1] / "src")
    return env


def _kill_after_ready(root, child_code, tag, expected):
    proc = subprocess.Popen(
        [sys.executable, "-c", child_code, str(root), tag],
        env=_child_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    try:
        marker = proc.stdout.readline().strip()
        assert marker == expected, f"Child did not reach interrupt point: {marker!r}"
        proc.send_signal(signal.SIGKILL)
        proc.wait(timeout=8)
        assert proc.returncode == -signal.SIGKILL
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=8)
        proc.stdout.close()
        proc.stderr.close()


def test_real_multiprocess_jsonl_appends_are_unique(tmp_path):
    """Four independent Python processes; partial syscalls cannot interleave rows."""
    script = """
import os,sys,time
from pathlib import Path
import politics_fantasy.secure_store as store
root=Path(sys.argv[1]);worker=int(sys.argv[2])
write=store._write_all
def split(fd,data):
    n=max(1,len(data)//2)
    write(fd,data[:n]);time.sleep(.002);write(fd,data[n:])
store._write_all=split
for i in range(12):
    store.append_private_jsonl(root,'manifest.jsonl',{'worker':worker,'index':i})
"""
    jobs = [
        subprocess.Popen([sys.executable, "-c", script, str(tmp_path), str(n)],
                         env=_child_env(), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                         text=True)
        for n in range(4)
    ]
    for child in jobs:
        _, err = child.communicate(timeout=15)
        assert child.returncode == 0, err[-500:]
    rows = [json.loads(line) for line in (tmp_path / "manifest.jsonl").read_text().splitlines()]
    assert len(rows) == 48
    assert len({(r["worker"], r["index"]) for r in rows}) == 48


def test_sigkill_within_private_append_is_rejected_by_auditor(tmp_path):
    code = """
import os,signal,sys
from pathlib import Path
import politics_fantasy.secure_store as store
def half(fd,payload):
    os.write(fd,payload[:max(1,len(payload)//2)])
    os.fsync(fd)
    print('MID_LEDGER',flush=True)
    signal.pause()
store._write_all=half
store.append_private_jsonl(Path(sys.argv[1]),'manifest.jsonl',{'fictional':True})
"""
    _kill_after_ready(tmp_path, code, "append", "MID_LEDGER")
    with pytest.raises(ValueError, match="INCOMPLETE_LEDGER_RECORD"):
        audit_private_root(tmp_path)


@pytest.mark.parametrize("phase,orphan", [("prelink", 0), ("postlink", 1)])
def test_sigkill_private_object_install_visible_to_aggregate_audit(tmp_path, phase, orphan):
    code = """
import hashlib,os,signal,sys
from pathlib import Path
import politics_fantasy.secure_store as store
phase=sys.argv[2]
data=b'{"synthetic":"interrupted-object"}'
sha=hashlib.sha256(data).hexdigest()
if phase=='prelink':
    def partial(fd,body):
        os.write(fd,body[:7]);os.fsync(fd)
        print('MID_OBJECT',flush=True);signal.pause()
    store._write_all=partial
else:
    verify=store._verify_object
    calls=[0]
    def pause_after_link(fd,name,body):
        calls[0]+=1
        verify(fd,name,body)
        if calls[0]==2:
            print('MID_OBJECT',flush=True);signal.pause()
    store._verify_object=pause_after_link
store.store_bytes(Path(sys.argv[1]),data,sha)
"""
    _kill_after_ready(tmp_path, code, phase, "MID_OBJECT")
    result = audit_private_root(tmp_path)
    assert result["manifest_rows"] == 0
    assert result["unexpected_object_entries"] == 1
    assert result["orphan_objects"] == orphan
    cli = subprocess.run(
        [sys.executable, "-m", "politics_fantasy.private_audit_cli", "--root", str(tmp_path)],
        capture_output=True, text=True, env=_child_env(), timeout=10
    )
    assert cli.returncode == 2
    assert json.loads(cli.stdout)["release_grade"] is False
    assert "interrupted-object" not in cli.stdout
