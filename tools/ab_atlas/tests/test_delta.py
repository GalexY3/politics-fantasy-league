import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import abmap,atlas_delta as delta

class DeltaTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.path=Path(self.tmp.name)
        self.base=self.path/'base.json';self.batches=self.path/'updates';self.batches.mkdir()
        abmap.atomic_write(self.base,abmap.init_doc('Test project','project',scaffold=False))
    def tearDown(self):self.tmp.cleanup()
    def batch(self,n,parent,ops):
        obj={'schema':delta.PATCH_SCHEMA,'batch_id':n,'parent_batch':parent,'at':'2026-10-26T19:00:00+00:00','actor':'chatgpt','reason':'Test controlado','ops':ops}
        (self.batches/(n+'.json')).write_text(json.dumps(obj),encoding='utf8')
        return obj
    def test_delta_atomic_and_brief(self):
        self.batch('0001','',[{'op':'node.add','node':{'id':'deliverable-1','title':'Interfaz','kind':'deliverable','mode':'project'}},
          {'op':'run.add','run':{'id':'R1','activity':'Prueba e2e','status':'failed'}},
          {'op':'complaint.add','complaint':{'id':'E1','run_id':'R1','description':'No abre una vista'}}])
        d,ids=delta.replay(self.base,self.batches)
        self.assertEqual(ids,['0001']);self.assertEqual(len(d['nodes']),2);self.assertEqual(d['runs'][0]['complaint_ids'],['E1'])
        brief=delta.brief(d,ids)
        self.assertEqual(brief['head_batch'],'0001');self.assertEqual(brief['open_complaints'][0]['id'],'E1')
        self.assertEqual(delta.digest(d),delta.digest(delta.replay(self.base,self.batches)[0]))
    def test_reject_stale_parent(self):
        self.batch('0001','',[]);self.batch('0002','',[])
        with self.assertRaisesRegex(ValueError,'conflicto de base'):delta.replay(self.base,self.batches)
    def test_reject_invented_validation(self):
        self.batch('0001','',[{'op':'node.add','node':{'id':'d1','title':'Fase','kind':'deliverable','mode':'project','status':'validated'}}])
        with self.assertRaisesRegex(ValueError,'validación sin aceptación'):delta.replay(self.base,self.batches)
        self.assertEqual(len(abmap.read(self.base)['nodes']),1)
    def test_duplicate_references(self):
        self.batch('0001','',[{'op':'node.add','node':{'id':'d1','title':'Fase','kind':'task','mode':'project'}},
          {'op':'node.add','node':{'id':'d1','title':'Fase','kind':'task','mode':'project'}}])
        with self.assertRaisesRegex(ValueError,'nodo duplicado'):delta.replay(self.base,self.batches)
    def test_gate_no_evidence_and_no_launch(self):
        self.batch('0001','',[{'op':'gate.add','gate':{'id':'deploy','label':'Deploy','critical':True}},
          {'op':'gate.set','id':'deploy','set':{'status':'passed'},'reason':'sin prueba'}])
        with self.assertRaisesRegex(ValueError,'passed sin evidencia'):delta.replay(self.base,self.batches)
        self.assertFalse(abmap.gate_readiness(abmap.read(self.base))['ready'])
    def test_method_rfc_vs_adoption(self):
        self.batch('0001','',[{'op':'method.propose','description':'Reducir coste de audit','reason':'demasiados tokens'}])
        d,ids=delta.replay(self.base,self.batches)
        self.assertEqual(d['method_changes'][0]['status'],'UNVALIDATED')
        self.assertIn('O7',d['method']['version'])
    def test_revision_versioning(self):
        self.batch('0001','',[{'op':'scope.revise','version':'SCOPE-2','reason':'Agregar mantenimiento'}])
        d,_=delta.replay(self.base,self.batches)
        self.assertEqual(d['project_contract']['scope_version'],'SCOPE-2')
        self.assertEqual(d['project_contract']['scope_history'][0]['version'],'SCOPE-1')
    def test_ordered_batches(self):
        self.batch('0001','',[{'op':'node.add','node':{'id':'x','title':'Paso','mode':'project'}}])
        self.batch('0002','0001',[{'op':'node.set','id':'x','set':{'status':'blocked'},'reason':'faltan permisos'}])
        d,ids=delta.replay(self.base,self.batches)
        self.assertEqual(len(ids),2);self.assertEqual(d['nodes'][-1]['status'],'blocked')
        self.assertEqual(d['events'][-1]['payload']['reason'],'faltan permisos')
    def test_do_not_allow_cross_batch_partial(self):
        self.batch('0001','',[{'op':'node.add','node':{'id':'x','title':'Paso','mode':'project'}},
                   {'op':'edge.add','id':'no','from':'root','to':'missing','relation':'depends_on'}])
        with self.assertRaisesRegex(ValueError,'extremo de enlace'):delta.replay(self.base,self.batches)
        self.assertEqual(len(abmap.read(self.base)['nodes']),1)
if __name__=='__main__':unittest.main()

class ExtraInvariants(unittest.TestCase):
    def test_meta_scaffold_keeps_meta_mode(self):
        doc=abmap.init_doc('Inspect AB itself','meta')
        self.assertTrue(all(x['mode']=='meta' for x in doc['nodes']))
        self.assertEqual(doc['nodes'][0]['kind'],'research')
        self.assertIsNone(doc['project_contract'])
    def test_brief_compacts_events(self):
        doc=abmap.init_doc('Compact','project',scaffold=False)
        doc['events'][-1]['payload']['huge']='X'*50000
        b=delta.brief(doc,[],events=5)
        self.assertLess(len(json.dumps(b)),5000)
