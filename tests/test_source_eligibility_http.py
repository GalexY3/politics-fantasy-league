"""C05 integration contract: GET works locally; other Hosts stay forbidden.

No real data is imported and no release gate is waived.
"""
import http.client
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
from politics_fantasy.server import handler_factory

class EligibilityHTTPTest(unittest.TestCase):
    def test_get_and_host_guard(self):
        with TemporaryDirectory() as td:
            srv=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(Path(td)/"db.sqlite",None,None))
            thread=threading.Thread(target=srv.serve_forever,daemon=True)
            thread.start()
            try:
                def call(host):
                    conn=http.client.HTTPConnection("127.0.0.1",srv.server_port,timeout=5)
                    conn.request("GET","/api/eligibility-policy",headers={"Host":host})
                    r=conn.getresponse()
                    body=r.read()
                    conn.close()
                    return r.status,body
                import json
                code,blob=call(f"127.0.0.1:{srv.server_port}")
                self.assertEqual(code,200)
                answer=json.loads(blob)
                self.assertFalse(answer["real_person_scoring"])
                self.assertFalse(answer["release_ready"])
                self.assertEqual(answer["policy_version"],"PFL-ELIG-1")
                code,_=call("attacker.invalid")
                self.assertEqual(code,403)
            finally:
                srv.shutdown()
                srv.server_close()
                thread.join(timeout=5)
