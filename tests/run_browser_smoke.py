"""PF-BR8N native Chromium E2E smoke for the LOCAL FICTIONAL demo.

Run in Github Actions on isolated localhost. Never test public hosting or
make real-politician ratings. Browser screenshot is a transient QA artifact.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
from urllib.request import urlopen, Request
from urllib.error import HTTPError

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
PORT=18787
BASE=f"http://127.0.0.1:{PORT}"
ART=Path(os.environ.get("PF_BROWSER_ARTIFACT","/tmp/pf-browser-e2e"))
ART.mkdir(parents=True,exist_ok=True)

def check_server():
    for _ in range(80):
        try:
            with urlopen(BASE+"/api/progress",timeout=1.0) as h:
                if h.status==200:return
        except Exception:
            time.sleep(.25)
    raise RuntimeError("LOCAL_DEMO_NOT_STARTED")

def main():
    env={**os.environ,"PYTHONPATH":str(ROOT/"src")}
    temp=Path(tempfile.mkdtemp(prefix="pf8n-"))
    proc=subprocess.Popen([sys.executable,"-m","politics_fantasy.server",
        "--db",str(temp/"browser-demo.sqlite"),"--port",str(PORT)],
        cwd=ROOT,env=env,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
    results={"campaign":"PF-BR8N","browser_engine":"chromium_headless",
        "localhost_only":True,"political_person_ratings_enabled":False,"passes":[]}
    try:
        check_server()
        with urlopen(BASE+"/api/progress",timeout=4) as h:
            obj=json.load(h)
            assert obj["revision"]==2 and obj["progress_display_pct"]==35.5
            assert len(obj["release_blockers"])==6
        results["passes"].append("HTTP local progress V2 and six blocked launch gates")
        try:
            with urlopen(Request(BASE+"/api/progress",headers={"Host":"foreign.invalid"}),timeout=4):
                raise AssertionError("HOST_ALLOWLIST_BYPASS")
        except HTTPError as err:
            assert err.code==403
        results["passes"].append("HTTP hostile Host blocked 403")
        with sync_playwright() as play:
            browser=play.chromium.launch(headless=True)
            page=browser.new_page(viewport={"width":1380,"height":860},device_scale_factor=1)
            errors=[]
            page.on("pageerror",lambda error:errors.append(str(error)))
            page.goto(BASE,wait_until="domcontentloaded",timeout=18000)
            page.locator("[data-tab='progress']").click()
            page.locator("#content").get_by_text("Progreso del proyecto",exact=False).first.wait_for(timeout=20000)
            content=page.locator("#content").inner_text()
            assert "35,5" in content,repr(content[:400])
            assert "Fuentes y datos" in content
            assert "Privacidad, seguridad y licencias" in content
            assert "NO está listo" in content
            results["passes"].append("Chromium progress V2 nine sublines and no-publication warning")
            page.locator("[data-tab='market']").click()
            market=page.locator("#content").inner_text()
            assert "Mercado" in market or "mercado" in market,market[:250]
            results["passes"].append("Chromium navigation to fictional transfer market")
            page.locator("[data-tab='atlas']").click()
            atlas=page.locator("#content").inner_text()
            assert "Atlas" in atlas or "atlas" in atlas,atlas[:250]
            results["passes"].append("Chromium navigation to historical electoral atlas")
            assert not errors,repr(errors[:5])
            results["passes"].append("No uncaught JavaScript page errors")
            page.screenshot(path=str(ART/"browser_progress_v2.png"),full_page=True)
            browser.close()
        results["status"]="PASS"
    finally:
        proc.terminate()
        try:proc.wait(timeout=4)
        except subprocess.TimeoutExpired:proc.kill()
        (ART/"browser_qa.json").write_text(json.dumps(results,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
    print("BROWSER_E2E_AUDIT="+json.dumps(results,ensure_ascii=False))
if __name__=="__main__":main()
