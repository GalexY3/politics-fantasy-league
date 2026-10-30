"""Independent supplemental T028 checks; run from archived checkout root.

Requires Node.js, npx, Playwright CLI and its authorized installed browser.
Tests only fictional local UI; does not assert general accessibility or release.
"""
import hashlib
import json
import pathlib
import socket
import subprocess
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent
SERVER = ROOT / 'proyectos/politics-fantasy-league/pilot_local/server.mjs'
SESSION = 'pfl-t028-supplement-qa'
CLI = ['npx.cmd', '--yes', '--package', '@playwright/cli', 'playwright-cli', '-s=' + SESSION]
transcript = []
results = {}

def cli(*args, raw=False):
    argv = CLI + (['--raw'] if raw else []) + list(args)
    result = subprocess.run(argv, cwd=ROOT, text=True, encoding='utf-8', errors='replace', capture_output=True, timeout=90)
    transcript.append({'command': argv[4:], 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
    if result.returncode:
        raise RuntimeError('Playwright command failed: ' + repr(args))
    return result.stdout

def evaluate(expr):
    return json.loads(cli('eval', expr, raw=True))

def http(method):
    request = urllib.request.Request('http://127.0.0.1:8787/', method=method)
    try:
        response = urllib.request.urlopen(request, timeout=5)
    except urllib.error.HTTPError as exc:
        response = exc
    with response:
        return {'status': response.status, 'allow': response.headers.get('Allow'),
                'referrer_policy': response.headers.get('Referrer-Policy')}

server = None
try:
    server = subprocess.Popen(['node', str(SERVER)], cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    for _ in range(50):
        if server.poll() is not None:
            raise RuntimeError('server exited early')
        try:
            with socket.create_connection(('127.0.0.1', 8787), timeout=.2):
                break
        except OSError:
            time.sleep(.1)
    else:
        raise RuntimeError('server did not listen')
    cli('open', 'http://127.0.0.1:8787/')
    cli('press', 'Tab')
    focus1 = evaluate('() => ({tag:document.activeElement.tagName,id:document.activeElement.id})')
    cli('press', 'Tab')
    focus2 = evaluate('() => ({tag:document.activeElement.tagName,id:document.activeElement.id,type:document.activeElement.type})')
    cli('press', 'Space')
    answer = evaluate('() => ({checked:document.activeElement.checked,progress:document.querySelector("#progress").innerText})')
    results['keyboard_select_focus'] = focus1 == {'tag':'SELECT','id':'arm'}
    results['keyboard_radio_focus'] = focus2 == {'tag':'INPUT','id':'X1-0','type':'radio'}
    results['keyboard_space_selects_radio'] = answer['checked'] and '1 de 4' in answer['progress']
    for _ in range(4):
        cli('press', 'Tab')
    focus_reset = evaluate('() => ({tag:document.activeElement.tagName,id:document.activeElement.id})')
    results['keyboard_reset_focus'] = focus_reset == {'tag':'BUTTON','id':'reset'}
    cli('press', 'Enter')
    reset = evaluate('() => ({progress:document.querySelector("#progress").innerText,selected:document.querySelectorAll("#questions input:checked").length})')
    results['keyboard_enter_resets'] = reset['selected'] == 0 and '0 de 4' in reset['progress']
    css = evaluate('() => ({sheets:Array.from(document.styleSheets).map(s=>({href:s.href,rules:s.cssRules.length})),ua:navigator.userAgent})')
    results['css_loaded_and_applied'] = any(s['href'] == 'http://127.0.0.1:8787/style.css' and s['rules'] > 0 for s in css['sheets'])
    cli('resize', '1280', '800')
    cli('screenshot', '--full-page', '--filename', 'desktop.png')
    cli('resize', '375', '812')
    cli('screenshot', '--full-page', '--filename', 'mobile.png')
    dimensions = evaluate('() => ({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
    results['mobile_no_horizontal_overflow'] = dimensions['width'] == 375 and dimensions['scrollWidth'] <= dimensions['width']
    responses = {method: http(method) for method in ('GET','PUT','DELETE')}
    results['no_referrer_header'] = responses['GET']['referrer_policy'] == 'no-referrer'
    results['put_denied'] = responses['PUT']['status'] == 405
    results['delete_denied'] = responses['DELETE']['status'] == 405
    results['two_png_screenshots'] = all((ROOT / name).read_bytes()[:8] == b'\x89PNG\r\n\x1a\n' for name in ('desktop.png','mobile.png'))
    report = {'head': '7a6876f71b6cbc286f86ff4bf1393889e4f22851',
              'scope': 'supplemental fictional pilot controls, not full accessibility or launch',
              'results': results, 'passed': sum(results.values()), 'total': len(results),
              'keyboard': {'select':focus1,'radio':focus2,'answer':answer,'reset_focus':focus_reset,'reset':reset},
              'css_and_browser':css, 'mobile':dimensions, 'http':responses,
              'screenshots': {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ('desktop.png','mobile.png')}}
    (ROOT/'supplement_result.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if not all(results.values()):
        raise SystemExit(1)
finally:
    try:
        cli('close')
    except Exception as exc:
        transcript.append({'close_error':str(exc)})
    if server is not None:
        server.terminate()
        try:
            server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server.kill()
            server.wait(timeout=5)
    (ROOT/'supplement_transcript.json').write_text(json.dumps(transcript,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
