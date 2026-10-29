#!/usr/bin/env python3
"""Read-only preflight of T028 in a lawful private checkout or verified partial pilot mirror.

Run: python T028_NATIVE_PREFLIGHT.py --repo . --out /tmp/pfl_t028_receipt.json
Never updates CURRENT, deploys, merges, recruits, or claims ethical approval.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

BASE_URL = 'http://127.0.0.1:8787'

def command(cmd: list[str], cwd: Path, timeout: int = 45) -> dict:
    try:
        r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)
        return {'command': cmd, 'exit': r.returncode, 'stdout_tail': r.stdout[-5000:], 'stderr_tail': r.stderr[-3000:]}
    except (OSError, subprocess.TimeoutExpired) as e:
        return {'command': cmd, 'status': 'BLOCKED_BY_ENVIRONMENT', 'error': str(e)[:600]}

def is_port_in_use() -> bool:
    with socket.socket() as s:
        s.settimeout(.4)
        return s.connect_ex(('127.0.0.1', 8787)) == 0

def direct_http(method: str, route: str) -> dict:
    req = urllib.request.Request(BASE_URL + route, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=5)
    except urllib.error.HTTPError as e:
        resp = e
    try:
        body = resp.read() if method != 'HEAD' else b''
        return {'method': method, 'route': route, 'status': resp.status, 'response_bytes': len(body),
                'CSP': resp.headers.get('Content-Security-Policy', ''),
                'no_store': 'no-store' in resp.headers.get('Cache-Control', ''),
                'nosniff': resp.headers.get('X-Content-Type-Options', '') == 'nosniff',
                'set_cookie': resp.headers.get('Set-Cookie') is not None}
    finally:
        resp.close()

def run_atlas(repo: Path, project: Path) -> dict:
    script = repo / 'ab_atlas' / 'atlas_delta.py'
    abmap = repo / 'ab_atlas' / 'abmap.py'
    seed = project / 'ab_atlas' / 'seed.json'
    updates = project / 'ab_atlas' / 'updates'
    missing = [str(x.relative_to(repo)) for x in [script, abmap, seed, updates] if not x.exists()]
    if missing:
        return {'status': 'NOT_RUN_MISSING_SOURCE', 'missing': missing,
                'canonical_sha256': 'UNKNOWN', 'CURRENT_md_updated': False}
    check = command([sys.executable, str(script), 'check', '--base', str(seed), '--updates', str(updates)], repo)
    if check.get('exit') != 0:
        return {'status': 'FAIL_OR_BLOCKED_CANONICAL_CHECK', 'check': check,
                'canonical_sha256': 'UNKNOWN', 'CURRENT_md_updated': False}
    m = re.search(r'OK\s+(\d+)\s+lotes\s+(\d+)\s+nodos\s+SHA256\s+([0-9a-f]{64})', check.get('stdout_tail', ''))
    if not m:
        return {'status': 'FAIL_UNEXPECTED_CHECK_OUTPUT', 'check': check, 'canonical_sha256': 'UNKNOWN'}
    brief = command([sys.executable, str(script), 'brief', '--base', str(seed),
                     '--updates', str(updates), '--limit', '8'], repo)
    if brief.get('exit') != 0:
        return {'status': 'FAIL_OR_BLOCKED_BRIEF', 'check': check, 'brief': brief,
                'canonical_sha256': m.group(3)}
    try:
        data = json.loads(brief['stdout_tail'])
    except (KeyError, ValueError):
        return {'status': 'FAIL_UNPARSEABLE_BRIEF', 'check': check, 'brief': brief,
                'canonical_sha256': m.group(3)}
    consistent = data.get('state_sha256') == m.group(3)
    count = int(m.group(1))
    return {'status': 'PASS_CANONICAL_CHECK' if consistent and count >= 80 else 'FAIL_CANONICAL_MISMATCH',
            'check': check, 'brief': data, 'lot_count': count, 'node_count': int(m.group(2)),
            'canonical_sha256': m.group(3), 'hash_consistent': consistent,
            'CURRENT_md_updated': False,
            'note': 'The original atlas_delta.py calls abmap.require_valid(strict=True) after each batch.'}

def run_browser() -> dict:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        return {'status': 'NOT_RUN_PLAYWRIGHT_MISSING', 'error': str(e)[:200]}
    result = {'status': 'NOT_RUN', 'browser': 'chromium'}
    try:
        with sync_playwright() as p:
            api = p.request.new_context()
            try:
                r = api.get(BASE_URL + '/', timeout=10000)
                result['api_request'] = {'status': r.status,
                                          'csp': r.headers.get('content-security-policy', '')}
            except Exception as e:
                result['api_request'] = {'status': 'ERROR', 'error': str(e)[:450]}
            finally:
                api.dispose()
            browser = None
            failures = []
            for opts in ({'headless': True},
                         {'headless': True, 'executable_path': shutil.which('chromium') or '/usr/bin/chromium',
                          'args': ['--no-sandbox', '--disable-gpu']}):
                try:
                    browser = p.chromium.launch(**opts)
                    break
                except Exception as e:
                    failures.append(str(e)[-500:])
            if browser is None:
                return {**result, 'status': 'BLOCKED_BROWSER_LAUNCH', 'launch_errors': failures}
            try:
                page = browser.new_page(viewport={'width': 1280, 'height': 768})
                js_errors, requests = [], []
                page.on('pageerror', lambda err: js_errors.append(str(err)[:500]))
                page.on('request', lambda req: requests.append({'method': req.method, 'url': req.url}))
                try:
                    response = page.goto(BASE_URL + '/', wait_until='load', timeout=10000)
                    page.wait_for_timeout(500)
                except Exception as e:
                    text = str(e)
                    status = ('BLOCKED_BY_ADMINISTRATOR' if 'ERR_BLOCKED_BY_ADMINISTRATOR' in text
                              else 'FAIL_BROWSER_NAVIGATION')
                    return {**result, 'status': status, 'error': text[-1100:],
                            'launch_errors': failures, 'requests_seen': requests,
                            'javascript_errors': js_errors}
                radios = page.locator('#questions input[type="radio"]').count()
                groups = page.locator('#questions fieldset').count()
                arms = {}
                for choice in ['control', 'transparency', 'leaderboard', 'both']:
                    page.locator('#arm').select_option(choice)
                    arms[choice] = {'selected': page.locator('#arm').input_value(),
                                    'tutorial': page.locator('#tutorial h3').inner_text(),
                                    'competition': page.locator('#competition h3').inner_text()}
                page.locator('#questions input[type="radio"]').first.check()
                progress = page.locator('#progress').inner_text()
                page.locator('#reset').click()
                reset = page.locator('#progress').inner_text()
                checks = {'document_http_200': response is not None and response.status == 200,
                          'four_groups': groups == 4, 'twelve_radios': radios == 12,
                          'all_arms_selectable': all(v['selected'] == k for k, v in arms.items()),
                          'radio_changes_progress': '1 de 4' in progress,
                          'reset_clears_progress': '0 de 4' in reset,
                          'js_error_free': not js_errors,
                          'no_external_requests': all(x['url'].startswith(BASE_URL + '/') for x in requests),
                          'no_post_or_other_methods': all(x['method'] == 'GET' for x in requests),
                          'materials_requested': any(x['url'] == BASE_URL + '/materials.mjs' for x in requests)}
                return {**result, 'status': 'PASS_BROWSER_HTTP_E2E' if all(checks.values()) else 'FAIL_BROWSER_CHECKS',
                        'checks': checks, 'arms': arms,
                        'javascript_errors': js_errors, 'requests_seen': requests,
                        'launch_errors': failures}
            finally:
                browser.close()
    except Exception as e:
        return {**result, 'status': 'BLOCKED_OR_FAILED_BROWSER_SETUP', 'error': str(e)[-1300:]}

def run_pilot(project: Path) -> dict:
    server = project / 'pilot_local' / 'server.mjs'
    if not server.exists():
        return {'status': 'NOT_RUN_NO_SERVER_SOURCE', 'missing': str(server)}
    if not shutil.which('node'):
        return {'status': 'NOT_RUN_NODE_MISSING'}
    if is_port_in_use():
        return {'status': 'BLOCKED_PORT_ALREADY_IN_USE',
                'note': 'Do not test a service whose origin is unknown.'}
    smoke = project / 'pilot_local' / 'smoke_http.mjs'
    smoke_result = command(['node', str(smoke)], project, 20) if smoke.exists() else {'status': 'NOT_RUN_NO_SMOKE'}
    with tempfile.TemporaryFile(mode='w+t') as out, tempfile.TemporaryFile(mode='w+t') as err:
        proc = subprocess.Popen(['node', str(server)], cwd=project, stdout=out, stderr=err, text=True)
        try:
            for _ in range(50):
                if proc.poll() is not None or is_port_in_use():
                    break
                time.sleep(.1)
            if not is_port_in_use():
                err.seek(0)
                return {'status': 'FAIL_SERVER_START', 'smoke': smoke_result, 'error': err.read()[-1500:]}
            cases = [('GET', '/', 200), ('GET', '/index.html', 200), ('GET', '/app.mjs', 200),
                     ('GET', '/style.css', 200), ('GET', '/materials.mjs', 200),
                     ('HEAD', '/', 200), ('GET', '/fictional_transfer_key.mjs', 404),
                     ('POST', '/', 405), ('GET', '/nonexistent', 404)]
            traces = []
            for method, route, expected in cases:
                try:
                    x = direct_http(method, route)
                    x['pass'] = (x['status'] == expected and "connect-src 'none'" in x['CSP']
                                 and x['no_store'] and x['nosniff'] and not x['set_cookie'])
                except Exception as e:
                    x = {'method': method, 'route': route, 'pass': False, 'error': str(e)[:400]}
                traces.append(x)
            browser = run_browser() if all(x['pass'] for x in traces) else {'status': 'NOT_RUN_HTTP_API_FAILED'}
            return {'status': 'PASS_NATIVE_HTTP_API' if all(x['pass'] for x in traces)
                    else 'FAIL_NATIVE_HTTP_API',
                    'smoke': smoke_result, 'smoke_pass': smoke_result.get('exit') == 0 if smoke.exists() else None,
                    'direct_http': traces, 'browser': browser}
        finally:
            proc.terminate()
            try:
                proc.wait(timeout=4)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=4)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', required=True, type=Path,
                    help='Authenticated repository root or verified partial mirror')
    ap.add_argument('--out', required=True, type=Path,
                    help='JSON receipt outside canonical source files')
    args = ap.parse_args()
    repo = args.repo.resolve()
    project = repo / 'proyectos' / 'politics-fantasy-league'
    mirror = False
    if not project.exists() and (repo / 'pilot_local' / 'server.mjs').exists():
        project, mirror = repo, True
    if not project.exists():
        ap.error('Neither full PFL project nor documented pilot mirror exists at --repo')
    result = {'schema': 'pfl.t028.native.preflight.v1',
              'utc_time': dt.datetime.now(dt.timezone.utc).isoformat(),
              'repo_root': str(repo),
              'scope': 'VERIFIED_PARTIAL_MIRROR' if mirror else 'FULL_CHECKOUT_PATH_PRESENT_NOT_AUTHENTICATED_BY_SCRIPT',
              'python': sys.version.split()[0], 'node': shutil.which('node'),
              'atlas': run_atlas(repo, project), 'pilot': run_pilot(project),
              'prohibitions_respected': {'no_merge': True, 'no_CI': True,
                                         'no_real_scoring': True, 'no_human_data': True,
                                         'no_atlas_CURRENT_auto_update': True}}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    summary = {'scope': result['scope'], 'atlas': result['atlas']['status'],
               'http_api': result['pilot']['status'],
               'browser_e2e': result['pilot'].get('browser', {}).get('status', 'NOT_RUN'),
               'receipt': str(args.out)}
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
