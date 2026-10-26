"""20 documented AB engineering contrast cycles; each test targets a falsifiable invariant.
These are system tests; they are not twenty independent scientific confirmations.
"""
import json
from pathlib import Path
import tempfile
import unittest
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import abmap as m

class TwentyABCycles(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.file=Path(self.tmp.name)/'graph.json'
    def doc(self,mode='project'):
        d=m.init_doc('Research & delivery',mode,'Entregar producto seguro','Usuarios de campo')
        m.atomic_write(self.file,d)
        return d
    def change(self,fn):return m.mutate(self.file,fn)
    def test_C01_proyecto_universal_con_scaffold_y_root(self):
        d=self.doc('project');self.assertIn('root',{n['id'] for n in d['nodes']});self.assertEqual(len(d['nodes']),6)
        self.assertEqual(set(n['phase'] for n in d['nodes'][1:]),{'discover','specify','build','verify','release'})
    def test_C02_separacion_de_ciencia_producto_meta(self):
        a=m.init_doc('Investigación','research');b=m.init_doc('Híbrido','hybrid')
        self.assertIsNone(a['project_contract']);self.assertIsNotNone(b['project_contract'])
        self.assertTrue(any(n['mode']=='research' for n in b['nodes']))
    def test_C03_contrato_resultado_y_destinatarios(self):
        d=self.doc();self.assertEqual(d['project_contract']['outcome'],'Entregar producto seguro');self.assertTrue(d['project_contract']['audience'])
    def test_C04_scope_no_sobrescribe_historia(self):
        d=self.doc()
        def revision(x):
            x['project_contract']['scope_history'].append({'version':'SCOPE-2','previous':'SCOPE-1','reason':'Nuevos usuarios'});x['project_contract']['scope_version']='SCOPE-2'
        self.change(revision);f=m.read(self.file);self.assertEqual(len(f['project_contract']['scope_history']),2)
        self.assertEqual(f['project_contract']['scope_history'][0]['version'],'SCOPE-1')
    def test_C05_release_no_preparado_si_no_hay_gates(self):
        d=self.doc();self.assertFalse(m.gate_readiness(d)['ready']);self.assertEqual(m.gate_readiness(d)['defined'],0)
    def test_C06_gate_no_pasa_sin_evidencia(self):
        d=self.doc();d['project_contract']['release_gates'].append({'id':'security','label':'Revisión de permisos','status':'passed','critical':True,'evidence':[]});self.assertTrue(any('security' in e for e in m.validate(d)))
    def test_C07_waiver_distinto_de_garantia_de_entrega(self):
        d=self.doc();d['project_contract']['release_gates'].append({'id':'security','label':'Revisión','status':'waived','critical':True,'evidence':[],'rationale':'Sólo local'});self.assertFalse(m.gate_readiness(d)['ready'])
    def test_C08_validacion_de_entregable_requiere_aceptacion(self):
        d=self.doc();n=next(n for n in d['nodes'] if n['kind']=='deliverable');n['status']='validated';self.assertTrue(any('validación' in e for e in m.validate(d,strict=True)))
    def test_C09_aceptacion_documenta_criterio_prueba_y_revisor(self):
        d=self.doc();n=next(n for n in d['nodes'] if n['kind']=='deliverable');n['status']='validated';n['acceptance']={'criteria':'Smoke sin fallos','evidence':['tests/smoke_browser.py'],'verified_by':'playwright','verified':True};self.assertFalse(m.validate(d,strict=True))
    def test_C10_hallazgo_no_se_infiere_de_progreso_de_producto(self):
        d=self.doc();self.assertNotIn('scientific_grade',d.get('project_contract',{}))
        self.assertNotIn('CT2',d.get('project_contract',{}))
    def test_C11_dependencias_ciclicas_rechazadas(self):
        d=self.doc();a=d['nodes'][1]['id'];b=d['nodes'][2]['id'];d['edges'].extend([{'id':'e1','from':a,'to':b,'relation':'depends_on'},{'id':'e2','from':b,'to':a,'relation':'depends_on'}]);self.assertTrue(any('Ciclo' in e for e in m.validate(d)))
    def test_C12_priorizacion_de_bloqueo_de_lanzamiento(self):
        d=self.doc();a=d['nodes'][1]['id'];b=d['nodes'][2]['id'];d['nodes'][2]['status']='blocked';d['nodes'][2]['kind']='blocker';d['edges'].append({'id':'e1','from':a,'to':b,'relation':'depends_on'});self.assertEqual(m.select_next(d)[0]['id'],b)
    def test_C13_compatibilidad_de_formato_anterior(self):
        d=self.doc();d['schema_version']='1.0';d['nodes'][1]['status']='validated';self.assertFalse(m.validate(d))
    def test_C14_scan_unreviewed_no_fabrica_hallazgos(self):
        d=self.doc();n=m.add_node(d,'paper.md','artifact','project','unreviewed',parent='root',sources=['paper.md']);self.assertFalse(n['acceptance']['verified']);self.assertNotIn('finding',n['kind'])
    def test_C15_mutacion_invalida_no_cambia_disco(self):
        self.doc();old=self.file.read_bytes()
        with self.assertRaises(ValueError):self.change(lambda d:d['edges'].append({'id':'bad','from':'root','to':'unknown','relation':'depends_on'}))
        self.assertEqual(self.file.read_bytes(),old)
    def test_C16_recibo_por_ejecucion_y_vinculo_de_queja(self):
        d=self.doc();d['runs'].append({'id':'R1','status':'failed','complaint_ids':['C1'],'activity':'Smoke'});d['complaints'].append({'id':'C1','run_id':'R1','severity':'major','status':'open','description':'Error encontrado'});self.assertFalse(m.validate(d))
    def test_C17_complaint_sin_run_rechazada(self):
        d=self.doc();d['complaints'].append({'id':'C1','run_id':'desconocido','severity':'major','status':'open','description':'Error'});self.assertTrue(any('ejecución inexistente' in e for e in m.validate(d)))
    def test_C18_no_duplicar_queja_y_distinguir_causa(self):
        d=self.doc();d['runs'].append({'id':'R1','status':'failed','complaint_ids':['C1'],'activity':'Prueba'});d['complaints'].append({'id':'C1','run_id':'R1','severity':'major','status':'open','description':'Error','suspected_cause':'A','verified_cause':''});self.assertFalse(m.validate(d));self.assertNotEqual(d['complaints'][0]['suspected_cause'],d['complaints'][0]['verified_cause'])
    def test_C19_legacy_provenance_y_roundtrip(self):
        d=self.doc();m.atomic_write(self.file,d);r=m.read(self.file);self.assertEqual(r['nodes'],d['nodes']);self.assertEqual(r['events'],d['events']);self.assertFalse(m.validate(r))
    def test_C20_ab_meta_mutable_pero_no_mejora_automaticamente(self):
        d=self.doc();self.assertTrue(d['method']['mutable']);self.assertNotIn('superiority_claim',d['method']);self.assertNotIn('improved_by',d['method'])

if __name__=='__main__':unittest.main(verbosity=2)
