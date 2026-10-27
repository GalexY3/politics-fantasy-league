"""Local Chromium smoke for the fictional market → lineup → simulated round flow."""
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
import threading

from playwright.sync_api import sync_playwright

from politics_fantasy.product import seed_demo, state
from politics_fantasy.server import handler_factory


def main():
    with TemporaryDirectory() as temp:
        db = Path(temp) / 'game.sqlite'
        seed_demo(db)
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler_factory(db, None))
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with sync_playwright() as play:
                browser = play.chromium.launch(headless=True)
                page = browser.new_page(viewport={'width':1280,'height':900})
                errors = []
                page.on('pageerror', lambda error: errors.append(str(error)))
                page.add_init_script("window.cspViolations=[];document.addEventListener('securitypolicyviolation',e=>window.cspViolations.push(e.effectiveDirective));")
                page.goto(f'http://127.0.0.1:{server.server_port}', wait_until='domcontentloaded')
                page.locator("[data-tab='market']").click()
                page.locator("[data-action='buy'][data-id='F04']").click()
                page.get_by_text('Fichaje registrado.').wait_for()
                page.locator("[data-tab='club']").click()
                for figure in ('F01','F02','F04'):
                    page.locator(f"[data-action='pick'][data-id='{figure}']").click()
                page.locator("[data-action='save-lineup']").click()
                page.get_by_text('Alineación guardada en SQLite.').wait_for()
                for figure in ('F01','F02','F04'):
                    page.locator(f"[data-action='pick'][data-id='{figure}']").click()
                assert page.locator("[data-action='pick'][aria-pressed='true']").count()==0
                page.locator("[data-tab='rounds']").click()
                page.locator("[data-action='simulate-round']").click()
                page.get_by_text('Jornada ficticia simulada y cerrada.').wait_for()
                page.get_by_text('RELOJ DE JUEGO ADELANTADO').wait_for()
                s = state(db)
                assert len(s['rounds'])==3
                closed = next(r for r in s['rounds'] if r['id']=='next')
                assert closed['scores']['demo']==5.5
                assert '5,5 (SINTÉTICOS)' in page.locator('#content').inner_text()
                page.locator("[data-tab='club']").click()
                for figure in ('F01','F02','F04'):
                    page.locator(f"[data-action='pick'][data-id='{figure}']").click()
                page.locator("[data-action='save-lineup']").click()
                page.get_by_text('Alineación guardada en SQLite.').wait_for()
                assert not errors, errors
                assert not page.evaluate('window.cspViolations')
                browser.close()
            print('PLAYABLE_CHROMIUM_SMOKE PASS: buy, lineup, empty draft, simulate, score, next lineup')
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


if __name__ == '__main__':
    main()
