"""ABH25-C02: independent fictional P1->P2 HTTP flow; no real politicians."""
import http.cookiejar
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from politics_fantasy import accounts
from politics_fantasy.server import handler_factory

def request(op, base, endpoint, data=None, csrf=None):
    headers = {'X-PFL-Request': '1'}
    if data is not None:
        headers['Content-Type'] = 'application/json'
    if csrf:
        headers['X-PFL-CSRF'] = csrf
    q = urllib.request.Request(base + endpoint,
        data=json.dumps(data).encode('utf-8') if data is not None else None,
        headers=headers, method='POST' if data is not None else 'GET')
    try:
        with op.open(q, timeout=8) as resp:
            return resp.status, json.load(resp)
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())

def new_client():
    return urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

class Journey(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.auth = root / 'auth.sqlite3'
        self.game = root / 'legacy.sqlite3'
        accounts.init_accounts(self.auth)
        self._start()

    def _start(self):
        self.http = ThreadingHTTPServer(('127.0.0.1', 0),
            handler_factory(self.game, None, None, self.auth))
        self.thread = threading.Thread(target=self.http.serve_forever, daemon=True)
        self.thread.start()
        self.base = f'http://127.0.0.1:{self.http.server_port}'

    def _stop(self):
        self.http.shutdown()
        self.http.server_close()
        self.thread.join(timeout=5)

    def tearDown(self):
        if self.http:
            self._stop()
        self.tmp.cleanup()

    def _login(self, name):
        op = new_client()
        password = 'fictional-only-password-2026'
        self.assertEqual(request(op,self.base,'/api/register',
            {'username':name,'password':password})[0], 201)
        status, body = request(op,self.base,'/api/login',
            {'username':name,'password':password})
        self.assertEqual(status,200)
        return op, body['result']['csrf']

    def _team(self, op, csrf, name):
        status, body = request(op,self.base,'/api/clubs',{'name':name},csrf)
        self.assertEqual(status,200)
        club = body['result']['id']
        for figure in ('F04','F05','F06'):
            self.assertEqual(request(op,self.base,'/api/buy',
                {'club_id':club,'figure_id':figure},csrf)[0],200)
        self.assertEqual(request(op,self.base,'/api/lineup',
            {'club_id':club,'round_id':'next',
             'figures':['F04','F05','F06']},csrf)[0],200)
        return club

    def test_two_accounts_full_round_restart_and_negative_controls(self):
        alice, a = self._login('alice_abh25')
        bob, b = self._login('bob_abh25')
        aid = self._team(alice,a,'Equipo ficticio A')
        bid = self._team(bob,b,'Equipo ficticio B')
        self.assertNotEqual(aid,bid)
        foreign = request(bob,self.base,'/api/lineup',
            {'club_id':aid,'round_id':'next','figures':['F04','F05','F06']},b)
        self.assertEqual(foreign[0],404)
        self.assertEqual(request(alice,self.base,'/api/simulate-round',
            {'round_id':'next'},b)[0],403)
        status, result = request(alice,self.base,'/api/simulate-round',
            {'round_id':'next'},a)
        self.assertEqual(status,200)
        self.assertFalse(result['result']['already_settled'])
        successor = result['result']['next_round_id']
        state_a = request(alice,self.base,'/api/state')[1]
        state_b = request(bob,self.base,'/api/state')[1]
        settled = next(x for x in state_a['rounds'] if x['id']=='next')
        self.assertIsNotNone(settled['scores'][aid])
        self.assertEqual(next(x for x in state_b['rounds'] if x['id']=='next')['coverage_state'],
                         'NOT_AVAILABLE')
        self.assertTrue(any(x['id']==successor for x in state_a['rounds']))
        self.assertTrue(request(alice,self.base,'/api/simulate-round',
            {'round_id':'next'},a)[1]['result']['already_settled'])
        self._stop()
        self.http = None
        self._start()
        after = new_client()
        status, result = request(after,self.base,'/api/login',
            {'username':'alice_abh25','password':'fictional-only-password-2026'})
        self.assertEqual(status,200)
        restarted = request(after,self.base,'/api/state')[1]
        self.assertEqual(next(x for x in restarted['rounds'] if x['id']=='next')
                         ['scores'][aid], settled['scores'][aid])
        self.assertTrue(any(x['id']==successor for x in restarted['rounds']))

    def test_unauthenticated_simulation_and_state_denied(self):
        op = new_client()
        self.assertEqual(request(op,self.base,'/api/state')[0],401)
        self.assertEqual(request(op,self.base,'/api/simulate-round',
            {'round_id':'next'})[0],401)
        self.assertFalse(self.game.exists())

if __name__ == '__main__':
    unittest.main()
