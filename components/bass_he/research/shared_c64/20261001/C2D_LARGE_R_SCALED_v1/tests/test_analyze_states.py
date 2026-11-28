"""Manufactured artifact bindings only; no solver or physical operator call."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('c2d_collector', ROOT/'code/analyze_states.py')
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class ArtifactBindingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.root_patch = patch.object(collector, 'ROOT', self.root)
        self.root_patch.start()
        self.batch = self.root/'evidence/MAIN_MPI'
        self.taskdir = self.batch/'bridge_R18'
        self.taskdir.mkdir(parents=True)
        self.task = {'task_id':'bridge_R18','parameters':{'kind':'bridge','R':18,'configuration':{}}}
        self.data = {'task_id':'bridge_R18','parameters':copy.deepcopy(self.task['parameters']),
                     'value':{'R':18},'new_eigenstates':2}
        self.selected = {'backend':'manufactured'}
        self.write_fixture()

    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()

    @staticmethod
    def write(path, value):
        path.write_bytes(collector.json_bytes(value))

    @staticmethod
    def meta(path):
        return {'bytes':path.stat().st_size,'sha256':collector.digest(path)}

    def write_fixture(self):
        self.write(self.taskdir/'TASK_INPUT.json', self.task)
        self.write(self.taskdir/'DATA.json', self.data)
        (self.taskdir/'STATE.npz').write_bytes(b'manufactured-state-bytes')
        manifest = {'schema':1,'tasks':[self.task],
                    'limits':{'per_worker_memory_gib':1.5,'task_wall_seconds':30}}
        self.write(self.batch/'MANIFEST_INPUT.json',manifest)
        manifest_sha = collector.digest(self.batch/'MANIFEST_INPUT.json')
        code = {'files':{'code/manufactured.py':'0'*64}}
        code['sha256'] = hashlib.sha256(collector.json_bytes(code['files'])).hexdigest()
        self.write(self.batch/'RUN_IDENTITY.json',{'manifest_sha256':manifest_sha,'code':code,
                   'backend':'manufactured','selected_backend':self.selected})
        result = {'status':'PASS','task_id':self.task['task_id'],'parameters':self.task['parameters'],
                  'input_sha256':collector.digest(self.taskdir/'TASK_INPUT.json'),
                  'code_identity_sha256':code['sha256'],'selected_backend':self.selected,
                  'backend':'manufactured','new_eigenstates':2,'evidence_file':'DATA.json',
                  'evidence_bytes':(self.taskdir/'DATA.json').stat().st_size,
                  'evidence_sha256':collector.digest(self.taskdir/'DATA.json'),
                  'state_file':'STATE.npz','state_bytes':(self.taskdir/'STATE.npz').stat().st_size,
                  'state_sha256':collector.digest(self.taskdir/'STATE.npz')}
        self.write(self.taskdir/'RESULT.json',result)
        execution = {'status':'WORKER_RESULT_PASS','task_id':self.task['task_id'],
                     'task_sha256':result['input_sha256'],'code_sha256':code['sha256'],
                     'selected_backend':self.selected,
                     'worker_result_sha256':collector.digest(self.taskdir/'RESULT.json'),
                     'artifacts':{n:self.meta(self.taskdir/n) for n in
                                  ('RESULT.json','TASK_INPUT.json','DATA.json','STATE.npz')}}
        self.write(self.batch/'BATCH_SUMMARY.json',{'tasks':[execution],
                   'code_sha256':code['sha256'],'manifest_sha256':manifest_sha})

    def test_coherent_binding_and_reference(self):
        docs = collector.documents()
        self.assertEqual(len(docs),1)
        ref = collector.state_ref(docs[0])
        self.assertEqual(ref['folder'],'evidence/MAIN_MPI/bridge_R18')
        self.assertEqual(ref['state_sha256'],collector.digest(self.taskdir/'STATE.npz'))

    def test_state_corruption_rejected(self):
        (self.taskdir/'STATE.npz').write_bytes(b'corruption')
        with self.assertRaisesRegex(RuntimeError,'STATE_IDENTITY_MISMATCH'):
            collector.documents()

    def test_coherently_rehashed_data_parameter_drift_rejected(self):
        self.data['parameters']['R'] = 20
        self.write_fixture()
        with self.assertRaisesRegex(RuntimeError,'TASK_DATA_RESULT_BINDING_MISMATCH'):
            collector.documents()

    def test_duplicate_summary_task_rejected(self):
        path = self.batch/'BATCH_SUMMARY.json'
        summary = json.loads(path.read_text())
        summary['tasks'].append(copy.deepcopy(summary['tasks'][0]))
        self.write(path,summary)
        with self.assertRaisesRegex(RuntimeError,'TASK_ORDER_OR_DUPLICATE'):
            collector.documents()

    def test_unsafe_state_folder_rejected(self):
        doc = collector.documents()[0]
        doc['folder'] = '../outside'
        with self.assertRaisesRegex(RuntimeError,'STATE_FOLDER_OUTSIDE_PACKAGE'):
            collector.state_ref(doc)

    def test_replaced_result_after_collection_rejected(self):
        doc = collector.documents()[0]
        result = json.loads((self.taskdir/'RESULT.json').read_text())
        result['new_eigenstates'] = 3
        self.write(self.taskdir/'RESULT.json',result)
        with self.assertRaisesRegex(RuntimeError,'STATE_REFERENCE_RESULT_MISMATCH'):
            collector.state_ref(doc)


if __name__ == '__main__':
    unittest.main()
