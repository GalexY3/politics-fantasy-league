"""Loopback-only HTTP application. Demonstration, not hardened multiuser web hosting.

Run: PYTHONPATH=src python -m politics_fantasy.server --db data/demo/game.db
Do NOT reverse-proxy to internet: there is no session authentication or CSRF account protection.
"""
from __future__ import annotations
import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .product import GameError, add_club, seed_demo, set_lineup, state, transfer
from .lab import local_lab_report
from .field_api import local_field_status
from .actor_api import local_actor_universe_status
from .electoral_atlas import atlas_status
from .evidence_warehouse_status import status as evidence_status
from .progress_api import progress_status
from .candidacy_api import status as official_candidacies_status

HERE=Path(__file__).resolve().parent
WEB=HERE/'web'
PROJECT=HERE.parent.parent
PILOT=PROJECT/'data/pilot_official_webview/20260723_vote_totals_MANUAL.csv'
FIELD=PROJECT/'data/local_field/report.json'


def handler_factory(db_path: Path, pilot_path: Path | None, field_path: Path | None=None):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'PoliticsFantasyDemo/0.2'
        sys_version = ''
        def respond(self, code: int, body: bytes, content_type: str):
            self.send_response(code)
            self.send_header('Content-Type',content_type)
            self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('X-Frame-Options','DENY')
            self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)
        def reply(self, code: int, payload: object):
            self.respond(code,json.dumps(payload,ensure_ascii=False,default=str).encode('utf-8'),'application/json; charset=utf-8')
        def _is_local_host(self):
            # Never trust a user-controlled Host header to bless an Origin.
            # Combined with binding only 127.0.0.1 this limits DNS rebinding.
            host=self.headers.get('Host','').strip().lower()
            return host in (f'127.0.0.1:{self.server.server_port}',
                            f'localhost:{self.server.server_port}')
        def do_GET(self):
            if not self._is_local_host():
                return self.reply(403,{'error':'LOCAL_HOST_REQUIRED'})
            route=urlsplit(self.path).path
            if route == '/api/state':
                return self.reply(200,state(db_path,pilot_csv=pilot_path))
            if route == '/api/lab':
                return self.reply(200,local_lab_report())
            if route == '/api/field':
                return self.reply(200,local_field_status(field_path))
            if route == '/api/progress':
                return self.reply(200,progress_status())
            if route == '/api/evidence-readiness':
                return self.reply(200,evidence_status())
            if route == '/api/verified-candidacies':
                return self.reply(200,official_candidacies_status())
            if route == '/api/electoral-atlas':
                return self.reply(200,atlas_status())
            if route == '/api/actors':
                return self.reply(200,local_actor_universe_status())
            if route == '/api/health':
                return self.reply(200,{'ok':True,'mode':'SYNTHETIC_DEMO','real_player_scoring':False})
            assets={'/':'index.html','/index.html':'index.html','/app.js':'app.js','/style.css':'style.css'}
            filename=assets.get(route)
            if not filename:
                return self.reply(404,{'error':'NOT_FOUND'})
            p=WEB/filename
            self.respond(200,p.read_bytes(),mimetypes.guess_type(str(p))[0] or 'application/octet-stream')
        def do_POST(self):
            if not self._is_local_host():
                return self.reply(403,{'error':'LOCAL_HOST_REQUIRED'})
            if urlsplit(self.path).path not in ('/api/clubs','/api/buy','/api/sell','/api/lineup'):
                return self.reply(404,{'error':'NOT_FOUND'})
            origin=self.headers.get('Origin')
            if origin and origin not in (f'http://{self.headers.get("Host", "")}',f'http://127.0.0.1:{self.server.server_port}',f'http://localhost:{self.server.server_port}'):
                return self.reply(403,{'error':'CROSS_ORIGIN_REJECTED'})
            if self.headers.get('Content-Type','').split(';')[0].strip().lower()!='application/json':
                return self.reply(415,{'error':'JSON_REQUIRED'})
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0 < size <= 16_384:
                    return self.reply(413,{'error':'BAD_CONTENT_LENGTH'})
                body=json.loads(self.rfile.read(size))
                if not isinstance(body,dict):
                    return self.reply(400,{'error':'OBJECT_REQUIRED'})
                route=urlsplit(self.path).path
                if route == '/api/clubs':
                    result=add_club(db_path,body.get('name',''))
                elif route in ('/api/buy','/api/sell'):
                    result=transfer(db_path,club_id=body.get('club_id'),figure_id=body.get('figure_id'),
                                    action=route.removeprefix('/api/'))
                else:
                    result=set_lineup(db_path,club_id=body.get('club_id'),round_id=body.get('round_id'),
                                      figures=body.get('figures'))
                self.reply(200,{'ok':True,'result':result})
            except GameError as exc:
                self.reply(exc.status,{'ok':False,'error':exc.code,'message':str(exc)})
            except (ValueError, TypeError, json.JSONDecodeError):
                self.reply(400,{'ok':False,'error':'BAD_REQUEST'})
        def log_message(self, fmt, *args):
            # No personal data/authorization tokens in log; this is a single-user local demo.
            return
    return Handler


def serve(db_path: Path, *, port: int=8787, pilot_path: Path | None=PILOT, field_path: Path | None=FIELD):
    seed_demo(db_path)
    server=ThreadingHTTPServer(('127.0.0.1',port),handler_factory(db_path,pilot_path,field_path))
    print(f'Politics Fantasy League · DEMO SINTÉTICA · http://127.0.0.1:{server.server_port}',flush=True)
    print('Sin autenticación: NO exponer a internet. No hay puntos políticos reales.',flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--db',type=Path,default=Path('data/demo/game.db'))
    p.add_argument('--port',type=int,default=8787)
    a=p.parse_args()
    serve(a.db,port=a.port)

if __name__ == '__main__':
    main()
