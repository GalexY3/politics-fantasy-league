"""S8 closeout: shipped app.js -> real localhost HTTP -> Python -> actual Node.

Only the DOM/download surface is virtualized in Node; HTTP JSON comes from the
real server and its independent JS warehouse. No external network or originals.
"""
from __future__ import annotations

from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import shutil
import subprocess
from threading import Thread

import pytest

from politics_fantasy.product import seed_demo
from politics_fantasy.server import handler_factory


@pytest.fixture
def s8_live_loopback(tmp_path):
    db=tmp_path/"s8-fictitious-demo.sqlite"
    seed_demo(db)
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(
        db,None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def _node_s8_e2e(base: str, mode: str, *, runner=subprocess.run):
    if shutil.which("node") is None:
        pytest.skip("Node.js is required for this genuine cross-process test")
    script=Path(__file__).resolve().parent/"test_s8_closeout_http_ui.mjs"
    completed=runner(["node",str(script),base,mode],
                     text=True,capture_output=True,timeout=30,check=False)
    assert completed.returncode==0,(
        f"stdout={completed.stdout}\nstderr={completed.stderr}")
    return json.loads(completed.stdout.strip().splitlines()[-1])


def test_s8_real_http_ui_interactions_cross_node_and_verified_export(s8_live_loopback):
    observed=_node_s8_e2e(s8_live_loopback,"baseline")
    assert observed["passed"] is True
    assert observed["evidence"]=="REAL_HTTP_NODE_VM"
    assert observed["cuts"]==["early","late"]
    assert observed["s7"]==20
    assert observed["source_catalog"]=={"early":2,"late":6,"filtered":2}
    assert observed["tamper_rejected"] is True
    assert observed["dry_run"]=="REJECTED_R5"
    assert len(observed["sha256_export"])==64
    assert observed["routes"]>=11
    print("S8_REAL_HTTP_E2E_RECEIPT="+json.dumps(observed,sort_keys=True))


def test_s8_ipc_corruption_real_node_becomes_http_503_and_ui_block(
        s8_live_loopback,monkeypatch):
    from politics_fantasy import scientific_integration_lab as lab
    # The real Node CLI computes successfully; only its IPC stdout is
    # adversarially changed *after* computation. Python must fail closed.
    original_run=lab.subprocess.run
    checked=[]

    def corrupt_node(*args,**kwargs):
        result=original_run(*args,**kwargs)
        if len(args)>0 and len(args[0])>1 and str(args[0][1]).endswith(
                "scientific_integration_warehouse.mjs"):
            assert result.returncode==0,result.stderr
            checked.append(True)
            payload=json.loads(result.stdout)
            late=payload["b0_b3_witness_sets"]["sets_by_knowledge_cut"]["late"]["sets"]
            chosen=next(x for x in late if x["case"]=="S7_NEITHER_APPROVED")
            chosen["status"]="B3_ONLY"
            return subprocess.CompletedProcess(args[0],0,
                stdout=json.dumps(payload),stderr=result.stderr)
        return result

    monkeypatch.setattr(lab.subprocess,"run",corrupt_node)
    observed=_node_s8_e2e(s8_live_loopback,"bridge_503",runner=original_run)
    assert observed=={"mode":"bridge_503","passed":True,
                      "evidence":"REAL_HTTP_503_NODE_VM",
                      "error":"SYNTHETIC_BRIDGE_UNAVAILABLE",
                      "ui_fail_closed":True}
    assert checked, "actual Node CLI never executed"


def test_s8_native_chrome_click_through_from_actual_localhost(s8_live_loopback):
    """Native browser/CDP, not just vm emulation; skip if Chrome not installed."""
    chrome=Path("C:/Program Files/Google/Chrome/Application/chrome.exe")
    if not chrome.is_file():
        pytest.skip("Chrome executable absent: Node VM real-HTTP E2E still covers API")
    if shutil.which("node") is None:
        pytest.skip("Native WebSocket CDP needs the installed Node runtime")
    script=Path(__file__).resolve().parent/"test_s8_closeout_chrome_cdp.mjs"
    proc=subprocess.run(["node",str(script),s8_live_loopback,str(chrome)],
        text=True,capture_output=True,timeout=50,check=False)
    assert proc.returncode==0,f"stdout={proc.stdout}\nstderr={proc.stderr}"
    result=json.loads(proc.stdout.strip().splitlines()[-1])
    assert result["evidence"]=="CHROME_HEADLESS_REAL_CDP"
    assert result["passed"] is True
    assert result["cuts"]==["early","late"]
    assert result["s7_sets"]==20
    assert result["source_catalog"]=={"early":2,"late":6,"filtered":2}
    assert result["dry_run"]=="REJECTED_R5"
    assert result["sha_tamper_rejected"] is True
    assert result["download_verified_from_disk"] is True
    assert result["download_sha256"]==result["sha256_export"]
    assert result["download_file_name"]==(
        f"pfl-s8-late-baseline-{result['sha256_export'][:12]}.json")
    assert result["canonical_bytes"]>0
    assert result["download_bytes"]>result["canonical_bytes"]
    assert result["download_cut"]=="late"
    assert result["download_scenario"]=="baseline"
    assert result["download_first_public"]=="2026-09-19T12:00:00Z"
    assert result["download_R5"]=="STOP_R5"
    assert result["download_gates"]==0
    assert result["downloads_after_tamper"]==1
    assert result["sha_tamper_no_second_download"] is True
    assert len(result["ui_screenshot_sha256"])==64
    print("S8_CHROME_CDP_RECEIPT="+json.dumps(result,sort_keys=True))
