import json, pathlib, subprocess, sys, tempfile, unittest
BASE=pathlib.Path(__file__).resolve().parents[1]
BIN=BASE/'abmap.py'
def cli(*args):return subprocess.run([sys.executable,str(BIN),*map(str,args)],capture_output=True,text=True)
class TestMap(unittest.TestCase):
 def test_lifecycle(self):
  with tempfile.TemporaryDirectory() as td:
   f=pathlib.Path(td)/'state.json';out=pathlib.Path(td)/'map.html'
   self.assertEqual(cli('init','--name','Proyecto piloto','--mode','hybrid','--no-scaffold','--file',f).returncode,0)
   a=cli('add','--file',f,'--title','¿Algo nuevo?','--kind','question','--parent','root')
   self.assertEqual(a.returncode,0,a.stderr);nid=a.stdout.strip()
   self.assertEqual(cli('status','--file',f,'--node',nid,'--status','answered','--reason','Se documentó el resultado').returncode,0)
   self.assertEqual(cli('run','--file',f,'--run-id','R01','--activity','Prueba de datos','--status','failed').returncode,0)
   self.assertEqual(cli('complaint','--file',f,'--run-id','R01','--severity','major','--category','evidence','--description','Faltan filas').returncode,0)
   self.assertEqual(cli('validate','--file',f).returncode,0)
   self.assertEqual(cli('build','--file',f,'--output',out).returncode,0)
   d=json.loads(f.read_text());self.assertEqual(len(d['nodes']),2);self.assertEqual(d['nodes'][1]['status'],'answered')
   self.assertEqual(len(d['complaints']),1);self.assertEqual(d['runs'][0]['complaint_ids'],[d['complaints'][0]['id']]);self.assertIn('Proyecto piloto',out.read_text())
 def test_scan_does_not_infer_facts(self):
  with tempfile.TemporaryDirectory() as td:
   td=pathlib.Path(td);f=td/'state.json';r=td/'data';r.mkdir();(r/'result.md').write_text('Superé el benchmark')
   cli('init','--name','Test','--no-scaffold','--file',f)
   self.assertEqual(cli('scan','--file',f,'--root',r).returncode,0)
   d=json.loads(f.read_text());self.assertEqual(d['nodes'][1]['kind'],'artifact');self.assertEqual(d['nodes'][1]['status'],'unreviewed')
 def test_broken_link_rejected(self):
  with tempfile.TemporaryDirectory() as td:
   f=pathlib.Path(td)/'s.json';cli('init','--name','Test','--no-scaffold','--file',f)
   a=cli('link','--file',f,'--source','root','--target','unknown','--relation','tests')
   self.assertNotEqual(a.returncode,0)
   self.assertEqual(len(json.loads(f.read_text())['edges']),0)
if __name__=='__main__':unittest.main()
