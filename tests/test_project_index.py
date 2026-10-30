"""Navigation must not expose private files or mistake archived copies for runtime."""
import importlib.util
from pathlib import Path
import unittest

PROJECT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('project_index', PROJECT/'scripts/project_index.py')
index = importlib.util.module_from_spec(spec)
spec.loader.exec_module(index)


class IndexTests(unittest.TestCase):
    def test_raw_and_private_paths_are_not_published(self):
        data = index.make_catalogue(['data/raw/person.xml','data/private/a.json','data/local_field/a.json','data/fixtures/synthetic.json'])
        self.assertEqual([x['path'] for x in data['files']], ['data/fixtures/synthetic.json'])

    def test_archived_source_is_not_active_code(self):
        path = 'tareas_codex/T025_EVIDENCIA/baseline/src/politics_fantasy/server.py'
        self.assertEqual(index.classify(path), 'evidence')
        self.assertEqual(index.classify('src/politics_fantasy/server.py'), 'runtime')

    def test_experimental_receipt_signing_is_not_user_authentication(self):
        data = index.make_catalogue(['research/old/linux/receipt.out','src/politics_fantasy/fictional_receipt_auth.mjs'])
        match = index.search(data, 'recibos')[0]
        self.assertEqual(match['category'], 'experimental_code')
        self.assertIn('no autenticación de usuarios', match['purpose'])

    def test_src_tests_and_workflows_do_not_look_like_runtime(self):
        self.assertEqual(index.classify('src/politics_fantasy/test_fictional_room_exposure.mjs'), 'verification')

    def test_self_and_escaped_paths_do_not_enter_catalogue(self):
        data = index.make_catalogue(['PROJECT_INDEX.json','PROJECT_MAP.md','research/INDEX.md','../secret','/absolute','START_HERE.md'])
        self.assertEqual([x['path'] for x in data['files']], ['START_HERE.md'])

    def test_catalogue_does_not_infer_executed_results(self):
        data = index.make_catalogue(['research/test/FINAL_REPORT.md','research/test/FINAL_REPORT.md'])
        self.assertFalse(data['certifies_results'])
        self.assertEqual(len(data['files']), 1)
        self.assertNotIn('status', data['files'][0])

    def test_repository_root_and_vendored_engine_are_indexed(self):
        self.assertEqual(index.ROOT, PROJECT)
        self.assertEqual(index.classify('tools/ab_atlas/atlas_delta.py'), 'atlas_engine')


if __name__ == '__main__':
    unittest.main()
