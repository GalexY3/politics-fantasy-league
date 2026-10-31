"""Loopback-only fictional demo with local accounts (NOT public internet hosting).

Run: PYTHONPATH=src python -m politics_fantasy.server --db data/demo/game.db
Sessions/CSRF and per-account SQLite are local safeguards, NOT a production
identity system, TLS stack, distributed rate limiter or internet deployment.
"""
from __future__ import annotations
import argparse
import json
import mimetypes
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from .product import GameError, add_club, seed_demo, set_lineup, simulate_round, state, transfer
from . import accounts
from .lab import local_lab_report
from .field_api import local_field_status
from .actor_api import local_actor_universe_status
from .electoral_atlas import atlas_status
from .evidence_warehouse_status import status as evidence_status
from .progress_api import progress_status
from .candidacy_api import status as official_candidacies_status
from .nomination_atlas import status as nomination_atlas_status
from .source_eligibility import policy_status
from .source_event_registry import public_stage_catalog
from .official_source_status import published_sources
from .parcan_cohort_status import status as parcan_status
from .procedural_coverage import coverage_status
from .siap_coverage import status as siap_status
from .procedural_population_readiness import report as population_readiness_report
from .retained_integrity_status import status as retained_integrity_status
from .registration_readiness_query import registration_readiness
from .synthetic_institutional_demo import report as institutional_lineage_demo

HERE=Path(__file__).resolve().parent
WEB=HERE/'web'
PROJECT=HERE.parent.parent
PILOT=PROJECT/'data/pilot_official_webview/20260723_vote_totals_MANUAL.csv'
FIELD=PROJECT/'data/local_field/report.json'


def _unique_request_json_pairs(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('DUPLICATE_JSON_FIELD')
        result[key] = value
    return result


def handler_factory(db_path: Path, pilot_path: Path | None, field_path: Path | None=None,
                    accounts_path: Path | None=None):
    # accounts_path=None exists solely for old single-user test harnesses.
    # The real serve() ALWAYS supplies an accounts_path and enforces identity.
    class Handler(BaseHTTPRequestHandler):
        server_version = 'PoliticsFantasyDemo/0.2'
        sys_version = ''
        def respond(self, code: int, body: bytes, content_type: str, cookie: str | None=None):
            self.send_response(code)
            self.send_header('Content-Type',content_type)
            self.send_header('Content-Length',str(len(body)))
            if cookie is not None:
                self.send_header('Set-Cookie',cookie)
            self.send_header('Cache-Control','no-store')
            self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('X-Frame-Options','DENY')
            self.send_header('Content-Security-Policy',"default-src 'self'; img-src 'self' data:; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.end_headers()
            self.wfile.write(body)
        def reply(self, code: int, payload: object, cookie: str | None=None):
            self.respond(code,json.dumps(payload,ensure_ascii=False,default=str).encode('utf-8'),'application/json; charset=utf-8',cookie)
        def _is_local_host(self):
            # Never trust a user-controlled Host header to bless an Origin.
            # Combined with binding only 127.0.0.1 this limits DNS rebinding.
            host=self.headers.get('Host','').strip().lower()
            return host in (f'127.0.0.1:{self.server.server_port}',
                            f'localhost:{self.server.server_port}')
        def _token(self):
            try:
                jar = SimpleCookie()
                raw = self.headers.get('Cookie', '')
                if len(raw) > 4096:
                    return None
                jar.load(raw)
                item = jar.get('pfl_session')
                return item.value if item else None
            except Exception:
                return None
        def _identity(self):
            if accounts_path is None:
                return None
            return accounts.lookup(accounts_path, self._token())
        def _cookie(self, token: str | None):
            value = token or ''
            lifetime = accounts.SESSION_TTL if token else 0
            return (f'pfl_session={value}; Path=/; HttpOnly; SameSite=Strict; '
                    f'Max-Age={lifetime}')
        def _origin_allowed(self):
            origin = self.headers.get('Origin')
            # SameSite Strict and an explicit CSRF request header complement Origin.
            # No permissive CORS is enabled for localhost.
            host = self.headers.get('Host','')
            return not origin or origin in (
                f'http://{host}', f'http://127.0.0.1:{self.server.server_port}',
                f'http://localhost:{self.server.server_port}')
        def do_GET(self):
            if not self._is_local_host():
                return self.reply(403,{'error':'LOCAL_HOST_REQUIRED'})
            route=urlsplit(self.path).path
            if route == '/api/session':
                if accounts_path is None:
                    return self.reply(200,{'authenticated':False,'legacy_test_mode':True})
                session = self._identity()
                if session is None:
                    return self.reply(401,{'authenticated':False,'error':'AUTH_REQUIRED'})
                return self.reply(200,{'authenticated':True,'username':session.handle,
                                       'csrf':session.csrf_secret})
            if route == '/api/state':
                if accounts_path is not None:
                    session = self._identity()
                    if session is None:
                        return self.reply(401,{'error':'AUTH_REQUIRED'})
                    payload = state(accounts.game_path(accounts_path,session.user_id),pilot_csv=pilot_path)
                    payload['authentication'] = 'LOCAL_ACCOUNT_ISOLATED'
                    payload['account'] = {'username':session.handle}
                    return self.reply(200,payload)
                return self.reply(200,state(db_path,pilot_csv=pilot_path))
            if route == '/api/lab':
                return self.reply(200,local_lab_report())
            if route == '/api/field':
                return self.reply(200,local_field_status(field_path))
            if route == '/api/progress':
                return self.reply(200,progress_status())
            if route == '/api/eligibility-policy':
                return self.reply(200,policy_status())
            if route == '/api/source-stages':
                return self.reply(200,public_stage_catalog())
            if route == '/api/evidence-readiness':
                return self.reply(200,evidence_status())
            if route == '/api/scientific-sources':
                return self.reply(200,published_sources())
            if route == '/api/spanish-process-cohorts':
                query = urlsplit(self.path).query
                try:
                    parsed = parse_qs(query, keep_blank_values=True, strict_parsing=True, max_num_fields=1)
                    if not set(parsed).issubset({'as_of'}) or any(len(v) != 1 for v in parsed.values()):
                        raise ValueError('INVALID_QUERY')
                    payload = parcan_status(as_of=parsed.get('as_of', [None])[0])
                    return self.reply(200,payload)
                except ValueError:
                    return self.reply(400,{'error':'INVALID_AS_OF_OR_QUERY'})
            if route == '/api/procedural-coverage':
                query = urlsplit(self.path).query
                try:
                    parsed = parse_qs(query, keep_blank_values=True, strict_parsing=True,
                                      max_num_fields=1)
                    if not set(parsed).issubset({'as_of'}) or any(len(v) != 1 for v in parsed.values()):
                        raise ValueError('INVALID_QUERY')
                    return self.reply(200,coverage_status(as_of=parsed.get('as_of',[None])[0]))
                except ValueError:
                    return self.reply(400,{'error':'INVALID_AS_OF_OR_QUERY'})
            if route == '/api/siap-index-coverage':
                query = urlsplit(self.path).query
                try:
                    parsed = parse_qs(query, keep_blank_values=True, strict_parsing=True,
                                      max_num_fields=1)
                    if not set(parsed).issubset({'as_of'}) or any(len(v) != 1 for v in parsed.values()):
                        raise ValueError('INVALID_QUERY')
                    return self.reply(200,siap_status(as_of=parsed.get('as_of',[None])[0]))
                except ValueError:
                    return self.reply(400,{'error':'INVALID_AS_OF_OR_QUERY'})
            if route == '/api/procedural-population-readiness':
                query = urlsplit(self.path).query
                try:
                    parsed = parse_qs(query, keep_blank_values=True, strict_parsing=True,
                                      max_num_fields=1)
                    if not set(parsed).issubset({'as_of'}) or any(len(v) != 1 for v in parsed.values()):
                        raise ValueError('INVALID_QUERY')
                    return self.reply(200,population_readiness_report(as_of=parsed.get('as_of',[None])[0]))
                except ValueError:
                    return self.reply(400,{'error':'INVALID_AS_OF_OR_QUERY'})
            if route == '/api/retained-source-integrity':
                query = urlsplit(self.path).query
                try:
                    parsed = parse_qs(query, keep_blank_values=True, strict_parsing=True,
                                      max_num_fields=1)
                    if not set(parsed).issubset({'as_of'}) or any(len(v)!=1 for v in parsed.values()):
                        raise ValueError('INVALID_QUERY')
                    return self.reply(200,retained_integrity_status(as_of=parsed.get('as_of',[None])[0]))
                except ValueError:
                    return self.reply(400,{'error':'INVALID_AS_OF_OR_QUERY'})
            if route == '/api/denominator-evidence':
                query = urlsplit(self.path).query
                try:
                    parsed = parse_qs(query,keep_blank_values=True,strict_parsing=True,
                                      max_num_fields=2)
                    if not set(parsed).issubset({'as_of','source_id'}) or any(len(v)!=1 for v in parsed.values()):
                        raise ValueError('INVALID_QUERY')
                    result=population_readiness_report(as_of=parsed.get('as_of',[None])[0])
                    from .source_scope_query import filter_denominator_source
                    return self.reply(200,filter_denominator_source(
                        result['denominator_evidence'],parsed.get('source_id',[None])[0]))
                except ValueError:
                    return self.reply(400,{'error':'INVALID_AS_OF_OR_QUERY'})
            if route == '/api/registration-readiness':
                query=urlsplit(self.path).query
                try:
                    parsed=parse_qs(query,keep_blank_values=True,strict_parsing=True,
                                    max_num_fields=2)
                    if (not set(parsed).issubset({'as_of','source_id'})
                            or any(len(v)!=1 for v in parsed.values())
                            or 'source_id' not in parsed):
                        raise ValueError('SOURCE_REQUIRED')
                    r=population_readiness_report(as_of=parsed.get('as_of',[None])[0])
                    return self.reply(200,registration_readiness(
                        readiness=r,source_id=parsed['source_id'][0]))
                except ValueError:
                    return self.reply(400,{'error':'INVALID_AS_OF_SOURCE_OR_QUERY'})
            if route == '/api/institutional-lineage-lab':
                query=urlsplit(self.path).query
                try:
                    parsed=parse_qs(query,keep_blank_values=True,strict_parsing=True,
                                    max_num_fields=2)
                    if (not set(parsed).issubset({'as_of','cut_on'})
                            or any(len(v)!=1 for v in parsed.values())):
                        raise ValueError('UNSUPPORTED_INSTITUTIONAL_LAB_QUERY')
                    return self.reply(200,institutional_lineage_demo(
                        as_of=parsed.get('as_of',[None])[0],
                        cut_on=parsed.get('cut_on',['2023-12-31'])[0]))
                except ValueError:
                    return self.reply(400,{'error':'INVALID_SYNTHETIC_LINEAGE_CUT'})
            if route == '/api/official-nominations':
                return self.reply(200,nomination_atlas_status())
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
            if urlsplit(self.path).path not in ('/api/register','/api/login','/api/logout',
                                                    '/api/clubs','/api/buy','/api/sell',
                                                    '/api/lineup','/api/simulate-round'):
                return self.reply(404,{'error':'NOT_FOUND'})
            if not self._origin_allowed():
                return self.reply(403,{'error':'CROSS_ORIGIN_REJECTED'})
            if self.headers.get('Content-Type','').split(';')[0].strip().lower()!='application/json':
                return self.reply(415,{'error':'JSON_REQUIRED'})
            try:
                size=int(self.headers.get('Content-Length','0'))
                if not 0 < size <= 16_384:
                    return self.reply(413,{'error':'BAD_CONTENT_LENGTH'})
                body=json.loads(self.rfile.read(size), object_pairs_hook=_unique_request_json_pairs)
                if not isinstance(body,dict):
                    return self.reply(400,{'error':'OBJECT_REQUIRED'})
                route=urlsplit(self.path).path
                if route in ('/api/register','/api/login'):
                    if accounts_path is None:
                        return self.reply(404,{'error':'ACCOUNTS_NOT_CONFIGURED'})
                    if self.headers.get('X-PFL-Request') != '1':
                        return self.reply(403,{'error':'REQUEST_HEADER_REQUIRED'})
                    if route == '/api/register':
                        handle=accounts.register(accounts_path,body.get('username'),body.get('password'))
                        return self.reply(201,{'ok':True,'result':{'username':handle}})
                    token,session=accounts.login(accounts_path,body.get('username'),body.get('password'))
                    return self.reply(200,{'ok':True,'result':{
                        'username':session.handle,'csrf':session.csrf_secret}},
                        self._cookie(token))
                session = self._identity()
                if accounts_path is not None:
                    if session is None:
                        return self.reply(401,{'error':'AUTH_REQUIRED'})
                    if not accounts.csrf_matches(session,self.headers.get('X-PFL-CSRF')):
                        return self.reply(403,{'error':'CSRF_REQUIRED'})
                    if route == '/api/logout':
                        accounts.revoke(accounts_path,self._token())
                        return self.reply(200,{'ok':True,'result':{'logged_out':True}},
                                          self._cookie(None))
                    game_db=accounts.game_path(accounts_path,session.user_id)
                else:
                    if route == '/api/logout':
                        return self.reply(404,{'error':'ACCOUNTS_NOT_CONFIGURED'})
                    game_db=db_path
                if route == '/api/clubs':
                    result=add_club(game_db,body.get('name',''))
                elif route in ('/api/buy','/api/sell'):
                    result=transfer(game_db,club_id=body.get('club_id'),figure_id=body.get('figure_id'),
                                    action=route.removeprefix('/api/'))
                elif route == '/api/simulate-round':
                    result=simulate_round(game_db,round_id=body.get('round_id'))
                else:
                    result=set_lineup(game_db,club_id=body.get('club_id'),round_id=body.get('round_id'),
                                      figures=body.get('figures'))
                self.reply(200,{'ok':True,'result':result})
            except accounts.AccountError as exc:
                self.reply(exc.status,{'ok':False,'error':exc.code})
            except GameError as exc:
                self.reply(exc.status,{'ok':False,'error':exc.code,'message':str(exc)})
            except (ValueError, TypeError, json.JSONDecodeError):
                self.reply(400,{'ok':False,'error':'BAD_REQUEST'})
        def log_message(self, fmt, *args):
            # Do not log requests, cookies, account names or authorization tokens.
            return
    return Handler


def serve(db_path: Path, *, port: int=8787, pilot_path: Path | None=PILOT, field_path: Path | None=FIELD):
    # Existing direct handler_factory() use is maintained for legacy unit tests.
    # serve() uses a mandatory account boundary: it NEVER serves the shared demo
    # game's club data to authenticated users.
    auth_db=db_path.parent/'accounts.sqlite3'
    accounts.init_accounts(auth_db)
    server=ThreadingHTTPServer(('127.0.0.1',port),
                               handler_factory(db_path,pilot_path,field_path,auth_db))
    print(f'Politics Fantasy League · DEMO SINTÉTICA · http://127.0.0.1:{server.server_port}',flush=True)
    print('Cuentas locales con sesiones; NO exponer a internet. No hay puntos políticos reales.',flush=True)
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
