"""Boundary fixtures mock only native execution; no native/MPI success evidence."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import worker as w
import prepare as p


class NativeTaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d = w.load_driver(w.sha(w.read(w.DRIVER)))
        cls.ladder = w.HERE.parents[1]
        cls.plan_path = w.HERE.parent/'runtime/pilot_plans/TINY_CENTRAL_PLAN.json'
        cls.plan = w.parse(w.read(cls.plan_path))
        cls.npz = cls.ladder/'production_solver_20261001_v1/inputs/FROZEN_INPUTS.npz'

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name); self.build_dir = self.root/'build'; self.build_dir.mkdir()
        (self.build_dir/'primitive_worker').write_text('NOT_EXECUTABLE_TEST_FIXTURE')
        self.provenance = self.root/'backend.json'; self.provenance.write_text('{}')
        self.limits_path = self.root/'limits.json'; self.limits = dict(self.d.DEFAULT_LIMITS)
        self.limits_path.write_bytes(w.canonical(self.limits))
        config = self.d.build_configuration('baseline')
        self.build = {'schema':'WU088_NATIVE_DRIVER_BUILD_V1', 'source':self.d.source_identity(),
            'archive_sha256':self.plan['archive_sha256'], 'input_record_sha256':self.plan['input_record_sha256'],
            'binary_sha256':w.sha(w.read(self.build_dir/'primitive_worker')),
            'backend_provenance':str(self.provenance), 'backend_provenance_sha256':w.sha(w.read(self.provenance)),
            'callback_mode':'baseline', 'callback_mode_flags':config['mode_flags'], 'callback_sources':config['sources'],
            'flags':self.d.FLAGS}
        self.build['manifest_sha256'] = w.sha(w.canonical(self.build))
        (self.build_dir/'BUILD.json').write_bytes(w.canonical(self.build))

    def prepare(self, indices=None):
        indices = [17,3] if indices is None else indices
        r = p.prepare(self.npz,self.plan_path,self.plan['plan_sha256'],self.build_dir,
            self.build['manifest_sha256'],self.limits_path,indices,self.root/'bundle')
        self.manifest_path = Path(r['manifest']['path']); self.manifest_sha = r['manifest']['sha256']
        self.manifest = w.parse(w.read(self.manifest_path)); return r

    def execute(self, ordinal=0):
        with patch.object(w.os,'getuid',return_value=1000), patch.object(w,'load_driver',return_value=self.d):
            return w.run(self.manifest_path,ordinal,self.manifest_sha)

    def envelope(self, index):
        task = self.plan['tasks'][index]
        result = {'schema':'WU088_NATIVE_INTERIOR_RESULT_V1','index':index,'task_sha256':task['task_sha256'],
            'plan_sha256':self.plan['plan_sha256'],'archive_sha256':self.plan['archive_sha256'],
            'input_record_sha256':self.plan['input_record_sha256'],'build_source_sha256':self.build['source']['sha256'],
            'precision_bits':128,'accepted_component_radius_exp':-48,'status':'RADIUS_MET','accepted':True,
            'endpoint_included':False,'normalization_applied':False,'full_domain_integral':False,
            'scientific_admission':False,'production_admission':False,'flint_status':0,
            'dispatched_evaluations':1,'integration_calls':1,'callback_calls':1,'callback_refusals':0,'analytic_box_refusals':0,
            'rectangle':{part:{'lower_mantissa':'0','upper_mantissa':'1','exponent2':'-48'} for part in ('real','imag')}}
        command = [str(self.build_dir/'primitive_worker'),str(index),*[self.plan['window'][k] for k in ('l_t','T_t','l_u','T_u')],
            *[str(self.limits[k]) for k in ('precision_bits','radius_exp','relative_goal','max_evaluations',
                'max_integration_calls','wall_seconds','queued_panels','degree_limit')],task['task_sha256'],self.plan['plan_sha256']]
        result['wrapper'] = {'schema':'WU088_NATIVE_INTERIOR_WRAPPER_V1','build_manifest_sha256':self.build['manifest_sha256'],
            'native_limits':self.limits,'command':command,'native_stdout_sha256':'a'*64,'native_execution_observed':True,
            'scope':'CONDITIONAL_COMPACT_INTERIOR_ONLY','evidence_contract':'SOURCE_BOUND_NATIVE_OUTPUT_ASSUMED_NOT_INDEPENDENTLY_REPLAYED',
            'validation_level':'BYTE_IDENTITY_AND_REPORTED_RADIUS_ONLY','endpoint_plan_module_sha256':w.sha(w.read(self.d.PLAN_MODULE)),
            'historical_abi_admission':False,'independent_scientific_review':False}
        result['result_sha256'] = w.sha(w.canonical(result)); return result

    def fake_api(self, npz, plan, plan_sha, index, build_dir, build_sha, limits, out):
        self.assertEqual((npz,plan,plan_sha,build_dir,build_sha,limits),
            (str(self.npz),str(self.plan_path),self.plan['plan_sha256'],str(self.build_dir),self.build['manifest_sha256'],self.limits))
        result = self.envelope(index)
        with Path(out).open('xb') as f: f.write(w.canonical(result))
        return result

    def test_sequential_selected_ordinals_use_real_api_signature(self):
        receipt = self.prepare()
        self.assertEqual((self.root/'bundle/WORKLIST.txt').read_text(),'2\n0 40\n1 40\n')
        with patch.object(self.d,'run_task',side_effect=self.fake_api) as native:
            a,b = self.execute(0),self.execute(1)
        self.assertEqual([a['native_index'],b['native_index']],[17,3]); self.assertEqual(native.call_count,2)
        self.assertFalse(a['MPI_runtime_admitted']); self.assertFalse(a['production_admission'])
        bound = (self.root/'bundle/bound_worker.py').read_text()
        self.assertIn(repr(self.manifest_sha),bound); self.assertIn(repr(self.manifest['core_worker_sha256']),bound)
        self.assertFalse(receipt['old_synthetic_launcher_compatible'])

    def test_existing_output_or_claim_never_reexecutes(self):
        self.prepare(); out = Path(self.manifest['output_root'])/'primitive_0017.json'
        for path in (out,Path(str(out)+'.claim')):
            path.write_text('preserve')
            with patch.object(self.d,'run_task') as native, self.assertRaisesRegex(w.Refusal,'existing output/claim'):
                self.execute()
            native.assert_not_called(); self.assertEqual(path.read_text(),'preserve'); path.unlink()

    def test_external_manifest_hash_and_source_mutation_refuse_before_api(self):
        self.prepare()
        with patch.object(self.d,'run_task') as native:
            self.manifest_path.write_bytes(w.read(self.manifest_path)+b' ')
            with self.assertRaisesRegex(w.Refusal,'external manifest'): self.execute()
            native.assert_not_called()

    def test_dependency_change_and_binary_change_refused(self):
        self.prepare()
        with patch.object(self.d,'source_identity',return_value={}),patch.object(self.d,'run_task') as native:
            with self.assertRaisesRegex(w.Refusal,'dependency source changed'):self.execute()
            native.assert_not_called()
        (self.build_dir/'primitive_worker').write_text('changed')
        with patch.object(self.d,'run_task') as native,self.assertRaisesRegex(w.Refusal,'file identity changed'):
            self.execute()
        native.assert_not_called()

    def test_failed_driver_not_converted_to_success(self):
        self.prepare()
        with patch.object(self.d,'run_task',side_effect=self.d.DriverError('NATIVE_REJECTED')):
            with self.assertRaisesRegex(ValueError,'NATIVE_REJECTED'):self.execute()
        self.assertEqual(list(Path(self.manifest['output_root']).iterdir()),[])

    def test_return_value_without_durable_output_is_refused(self):
        self.prepare()
        with patch.object(self.d,'run_task',return_value=self.envelope(17)):
            with self.assertRaises(OSError):self.execute()

    def test_wrong_task_or_promoted_envelope_refused(self):
        self.prepare(); context = w.authority(self.manifest)
        for change in ('index','production_admission','command'):
            r = self.envelope(17)
            if change=='index':r['index']=3
            elif change=='command':r['wrapper']['command'][0]='/bin/sh'
            else:r['production_admission']=True
            r['result_sha256']=w.sha(w.canonical({k:v for k,v in r.items() if k!='result_sha256'}))
            with self.assertRaises(ValueError):w.validate_envelope(r,self.manifest,0,context)

    def test_bool_cannot_impersonate_unit_resource_cap_in_wrapper(self):
        self.limits['max_evaluations']=1
        self.limits_path.write_bytes(w.canonical(self.limits))
        self.prepare(); context=w.authority(self.manifest)
        result=self.envelope(17)
        result['wrapper']['native_limits']=dict(self.limits,max_evaluations=True)
        result['result_sha256']=w.sha(w.canonical({k:v for k,v in result.items() if k!='result_sha256'}))
        with self.assertRaises(ValueError):w.validate_envelope(result,self.manifest,0,context)

    def test_index_domain_and_duplicate_selection_refused(self):
        for indices in ([],[0,0],[-1],[2592],[True],[1.0]):
            with self.subTest(indices=indices),self.assertRaisesRegex(w.Refusal,'unique strict'):
                self.prepare(indices)
        self.assertFalse((self.root/'bundle').exists())

    def test_root_execution_refused_before_manifest_read(self):
        with patch.object(w.os,'getuid',return_value=0),patch.object(w,'load_manifest') as load:
            with self.assertRaisesRegex(w.Refusal,'nonroot'):w.run('/missing',0,'a'*64)
            load.assert_not_called()

    def test_bad_ordinal_never_calls_native(self):
        self.prepare()
        with patch.object(self.d,'run_task') as native:
            for ordinal in (-1,2,True):
                with self.assertRaisesRegex(w.Refusal,'ordinal'):self.execute(ordinal)
            native.assert_not_called()

    def test_exact_json_and_symlink_refused(self):
        for data in (b'{"x":1,"x":2}',b'{"x":0.5}',b'{"x":NaN}'):
            with self.assertRaises(w.Refusal):w.parse(data)
        target = self.root/'link'; target.symlink_to(self.provenance)
        with self.assertRaises(w.Refusal):w.read(target)


if __name__=='__main__':unittest.main(verbosity=2)
