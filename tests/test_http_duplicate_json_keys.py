"""C16: local HTTP mutation requests reject ambiguous duplicate JSON names."""
import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from politics_fantasy.server import handler_factory
from politics_fantasy.product import seed_demo

def test_ambiguous_duplicate_club_creation_rejected(tmp_path):
    path=tmp_path/'demo.sqlite'
    seed_demo(path)
    srv=ThreadingHTTPServer(('127.0.0.1',0),handler_factory(path,None,None))
    thread=threading.Thread(target=srv.serve_forever,daemon=True)
    thread.start()
    try:
        def send(payload):
            conn=http.client.HTTPConnection('127.0.0.1',srv.server_port,timeout=4)
            conn.request('POST','/api/clubs',body=payload,
                         headers={'Host':f'127.0.0.1:{srv.server_port}',
                                  'Content-Type':'application/json'})
            res=conn.getresponse()
            code=res.status
            body=json.loads(res.read())
            conn.close()
            return code,body
        status,bad=send('{"name":"Club Primero","name":"Club Segundo"}')
        assert status==400 and bad['error']=='BAD_REQUEST'
        status,bad=send('{"name":"Club A","nested":{"x":1,"x":2}}')
        assert status==400
        status,ok=send('{"name":"Club Único"}')
        assert status==200 and ok['ok'] is True
    finally:
        srv.shutdown()
        srv.server_close()
        thread.join(timeout=4)
