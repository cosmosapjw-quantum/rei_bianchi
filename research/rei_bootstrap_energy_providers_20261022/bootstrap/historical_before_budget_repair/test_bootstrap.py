"""Deterministic orchestration tests; no ODE, point checks or rendering."""
import contextlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('bootstrap', HERE/'bootstrap.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


class FakeExecutor:
    """Tiny deterministic receipts, independent from the frozen numerical code."""
    def __init__(self, fail=None):
        self.cases = [dict(sigma=.01,am=i,ar=0.,ellmax=16) for i in range(79)]
        self.cases[7] = dict(sigma=0.,am=0.,ar=0.,ellmax=16)
        self.cases[70] = dict(sigma=.6,am=1.6,ar=-.8,ellmax=16)
        self.controls = [dict(self.cases[i],ellmax=24,rtol=2e-9,atol=2e-12) for i in (7,70,75)]
        self.reference = dict(sigma=0.,am=0.,ar=0.,reference=True)
        self.saved = set()
        self.records = []
        self.calls = []
        self.fail = fail
        self.cost = 0.001

    def key(self, stage, config):
        return stage, json.dumps(config,sort_keys=True)

    def present(self, stage, config=None):
        return self.key(stage,config) in self.saved

    def receipts(self):
        return self.records

    def complete(self):
        if self.present('summary'):
            return dict(status='COMPLETE_NO_WORK',validated_quotients=82,validated_reference=1,
                        scientific_admission='PENDING_INDEPENDENT_REVIEW')

    def execute(self, stage, config, remaining_cpu, remaining_wall):
        self.calls.append((stage,config))
        if self.fail == stage or self.fail == len(self.calls):
            return dict(status='FAILED',cpu_s=self.cost,wall_s=self.cost)
        if stage == 'case':
            self.records.append(dict(cpu_s=self.cost,wall_s=self.cost))
        self.saved.add(self.key(stage,config))
        return dict(status='PASS',cpu_s=self.cost,wall_s=self.cost)


class OrchestrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.ws = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def test_full_empty_dag_and_no_work(self):
        ex = FakeExecutor()
        result = b.Engine(self.ws,ex).run()
        self.assertEqual(result['attempts_total'],83)
        stages = [stage for stage,_ in ex.calls]
        self.assertEqual(stages[:5],['checks','case','case','pair','reanalysis'])
        self.assertEqual(stages[-1],'summary')
        self.assertEqual(stages.count('case'),83)
        self.assertEqual(ex.calls[1][1],ex.cases[7])
        self.assertEqual(ex.calls[2][1],ex.reference)
        self.assertEqual([c for s,c in ex.calls[5:10]], [ex.cases[70],ex.cases[75],*ex.controls])
        before = (self.ws/'BOOTSTRAP_STATE.json').read_bytes()
        ex.calls.clear()
        repeated = b.Engine(self.ws,ex).run()
        self.assertEqual(repeated['bootstrap_status'],'COMPLETE_NO_WORK')
        self.assertEqual(ex.calls,[])
        self.assertEqual((self.ws/'BOOTSTRAP_STATE.json').read_bytes(),before)

    def test_partial_resume_only_missing_and_inherit_budget(self):
        ex = FakeExecutor()
        for stage, config in [('checks',None),('case',ex.cases[7]),('case',ex.reference),('pair',None),('reanalysis',None)]:
            ex.execute(stage,config,2400,900)
        ex.calls.clear()
        result = b.Engine(self.ws,ex).run()
        self.assertEqual(result['attempts_total'],83)
        self.assertEqual(sum(s=='case' for s,_ in ex.calls),81)
        self.assertFalse(any(s in ('checks','pair','reanalysis') for s,_ in ex.calls))
        self.assertGreaterEqual(result['limits_consumed']['cpu_s'],83*ex.cost)

    def test_failure_is_retained_no_retry(self):
        ex = FakeExecutor(fail=3)
        with self.assertRaisesRegex(RuntimeError,'stage failed'):
            b.Engine(self.ws,ex).run()
        self.assertEqual(b.read(self.ws/'BOOTSTRAP_STATE.json')['attempts'],2)
        before = list(ex.calls)
        with self.assertRaisesRegex(RuntimeError,'prior stop'):
            b.Engine(self.ws,ex).run()
        self.assertEqual(ex.calls,before)

    def test_failed_check_and_summary_stop(self):
        for stage in ('checks','summary'):
            with self.subTest(stage=stage), tempfile.TemporaryDirectory() as tmp:
                ex = FakeExecutor(fail=stage)
                with self.assertRaisesRegex(RuntimeError,'stage failed'):
                    b.Engine(tmp,ex).run()
                self.assertEqual(b.read(Path(tmp)/'BOOTSTRAP_STATE.json')['status'],'FAILED')

    def test_cumulative_limits(self):
        for field, value in [('attempts',90),('cpu_s',2400.),('wall_s',900.)]:
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                ex = FakeExecutor()
                engine = b.Engine(tmp,ex)
                engine.state[field] = value
                engine.save()
                with self.assertRaisesRegex(RuntimeError,'cumulative resource limit'):
                    engine.run_one('case',ex.cases[0])
                self.assertEqual(ex.calls,[])
                again = b.Engine(tmp,ex)
                with self.assertRaisesRegex(RuntimeError,'prior stop'):
                    again.run()
                self.assertGreaterEqual(again.state[field],value)

    def test_poststage_cpu_limit_stops_next_launch(self):
        ex = FakeExecutor()
        engine = b.Engine(self.ws,ex)
        engine.state['cpu_s'] = 2398.
        ex.cost = 3.
        with self.assertRaisesRegex(RuntimeError,'after stage'):
            engine.run_one('checks')
        self.assertEqual(len(ex.calls),1)
        self.assertEqual(engine.state['status'],'RESOURCE_LIMIT')

    def test_interrupted_launch_and_executor_exception(self):
        ex = FakeExecutor()
        engine = b.Engine(self.ws,ex)
        engine.state['active'] = dict(stage='case',config=ex.reference)
        engine.save()
        with self.assertRaisesRegex(RuntimeError,'unfinished launch'):
            b.Engine(self.ws,ex)
        self.assertEqual(ex.calls,[])
        with tempfile.TemporaryDirectory() as tmp:
            ex = FakeExecutor()
            ex.execute = lambda *args: (_ for _ in ()).throw(OSError('fixture failure'))
            engine = b.Engine(tmp,ex)
            with self.assertRaisesRegex(OSError,'fixture failure'):
                engine.run_one('case',ex.reference)
            state = b.read(Path(tmp)/'BOOTSTRAP_STATE.json')
            self.assertEqual(state['attempts'],1)
            self.assertIsNotNone(state['active'])

    def test_worker_bounds(self):
        for workers in (0,5):
            with self.assertRaises(ValueError):
                b.Engine(self.ws,FakeExecutor(),workers)

    def test_source_only_prepare_stdlib_plan_and_clean_import(self):
        target = self.ws/'fresh'
        command = [sys.executable,'-S',str(HERE/'bootstrap.py'),'prepare','--workspace',str(target)]
        result = subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(list((target/'pilot/results').iterdir()),[])
        self.assertFalse((target/'pilot/summary.json').exists())
        planned = subprocess.run([sys.executable,'-S',str(HERE/'bootstrap.py'),'plan','--workspace',str(target)],capture_output=True,text=True)
        self.assertEqual(planned.returncode,0,planned.stderr)
        self.assertEqual(json.loads(planned.stdout)['cases']['total'],83)
        # Import/verify only: no numerical checks and no IVP. Separate process avoids module reuse.
        program = 'import sys;sys.path.insert(0,sys.argv[1]);import bootstrap;b=bootstrap.load_runner(sys.argv[2]);print(b.ROOT)'
        imported = subprocess.run([sys.executable,'-c',program,str(HERE),str(target)],capture_output=True,text=True)
        self.assertEqual(imported.returncode,0,imported.stderr)
        self.assertEqual(list((target/'pilot/results').iterdir()),[])
        with self.assertRaises(FileExistsError):
            b.prepare(b.DEFAULT_SOURCE,target)
        # Accidental change to copied immutable inputs is diagnosed before launch.
        p = target/'pilot/data/verner_photo_Z1_Z2_Z3.dat'
        p.write_bytes(p.read_bytes()+b'\n')
        with self.assertRaisesRegex(RuntimeError,'immutable source changed'):
            b.plan(target)

    def test_completed_original_reuse_zero_compute(self):
        source = b.DEFAULT_SOURCE
        protected = list((source/'pilot/results').glob('*')) + [source/'pilot/summary.json']
        before = {str(p):b.digest(p) for p in protected if p.is_file()}
        program = '''import sys
sys.path.insert(0,sys.argv[1])
import bootstrap
r=bootstrap.load_runner(sys.argv[2])
def fail(*a,**k): raise AssertionError('compute forbidden')
for name in ('run_case','point_checks','profile','reanalyze_existing_profile','execute_config','run_stage','controls_stage','sweep'):
 setattr(r,name,fail)
r.solve_ivp=fail
r.ProcessPoolExecutor=fail
print(r.saved_inventory(require_complete=True)['status'])
'''
        result = subprocess.run([sys.executable,'-c',program,str(HERE),str(source)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertIn('COMPLETE_NO_WORK',result.stdout)
        self.assertEqual(before,{str(p):b.digest(p) for p in protected if p.is_file()})


class SummaryTests(unittest.TestCase):
    def setUp(self):
        import numpy as np
        self.np = np
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.out = self.root/'results'
        self.out.mkdir()
        ex = FakeExecutor()
        def normalized(config):
            return dict({'rtol':2e-8,'atol':2e-11},**config)
        case_configs = [normalized(c) for c in ex.cases+ex.controls+[ex.reference]]
        class Runner:
            ROOT, OUT, RTOL, ATOL = self.root,self.out,2e-8,2e-11
            ISOTOPES = [('n',1,0),('H1',1,1),('D',2,1),('T',3,1),('He3',3,2),('He4',4,2),('Li6',6,3),('Li7',7,3)]
            case_configurations = staticmethod(lambda:(ex.cases,ex.controls))
            Coupled = staticmethod(lambda **c:c)
            case_id = staticmethod(lambda c:'c'+str(case_configs.index(normalized(c))))
            verify_existing_case = staticmethod(lambda c:dict(isotope_sum_errors={'H':0.},massive_number_drift=0.,min_brightness=.25))
            source = staticmethod(lambda:None)
            class AtomicQuotient:
                def __init__(self,source):
                    self.w_element = np.array([1.,1.,0.,0.,0.,0.,0.,0.,0.])
                    self.q = np.array([0,1,0,1,2,0,1,2,3])
        self.r = Runner
        names = ['nB_m3','ne_m3','U_thermal_J_m3','U_binding_J_m3','U_UV_J_m3','background_J_m3','signed_Sigma','P_m','P_r']
        d = np.array([[2.,1.,1.,2.,3.,100.,0.,0.,0.]]*2)
        f = np.array([[.5,.5,1.,0.,0.,1.,0.,0.,0.]]*2)
        census = np.zeros((2,21));census[:,1]=1.
        for c in ex.cases+ex.controls:
            np.savez(self.out/(Runner.case_id(c)+'.npz'),x=[0.,1.],diagnostics=d,diagnostic_names=names,conditional=f,census=census)
        for name,value in [('point_checks_v2.json',dict(passed=True)),('profile_pair.json',dict(status='PASS')),('profile_existing_reanalysis.json',dict(status='PASS'))]:
            b.write(self.out/name,value)

    def tearDown(self):
        self.temp.cleanup()

    def test_case_id_normalizes_only_default_tolerances(self):
        cases, controls = self.r.case_configurations()
        nominal = cases[7]
        self.assertEqual(self.r.case_id(nominal),self.r.case_id(dict(nominal,rtol=self.r.RTOL,atol=self.r.ATOL)))
        self.assertNotEqual(self.r.case_id(nominal),self.r.case_id(controls[0]))
        with self.assertRaises(ValueError):
            self.r.case_id(dict(nominal,rtol=2e-9,atol=2e-12))
        with self.assertRaises(ValueError):
            self.r.case_id(dict(nominal,ellmax=24))

    def test_fresh_summary_values_and_independent_status(self):
        result = b.fresh_summary(self.r)
        self.assertEqual(result['completed'],82)
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['scientific_admission'],'PENDING_INDEPENDENT_REVIEW')
        self.assertAlmostEqual(result['max_testfluid_energy_over_background'],.06)
        self.assertEqual(result['max_baryon_sum_residual'],0.)
        self.assertEqual(result['max_electron_closure_relative'],0.)
        self.assertEqual(len(result['controls']),3)
        with self.assertRaises(FileExistsError):
            b.fresh_summary(self.r)

    def test_missing_and_corrupt_raw_stop_without_summary(self):
        p = self.out/'c0.npz'
        original = p.read_bytes()
        p.unlink()
        with self.assertRaises(FileNotFoundError):
            b.fresh_summary(self.r)
        self.assertFalse((self.root/'summary.json').exists())
        p.write_bytes(b'corrupt fixture')
        with self.assertRaises(ValueError):
            b.fresh_summary(self.r)
        self.assertFalse((self.root/'summary.json').exists())

    def test_failed_control_is_numeric_fail_pending_review(self):
        c = self.r.case_configurations()[1][0]
        p = self.out/(self.r.case_id(c)+'.npz')
        with self.np.load(p) as z:
            arrays = {k:z[k] for k in z.files}
        arrays['conditional'] = arrays['conditional'].copy()
        arrays['conditional'][0,0] += 1e-3
        self.np.savez(p,**arrays)
        result = b.fresh_summary(self.r)
        self.assertEqual(result['status'],'FAILED')
        self.assertFalse(result['all_82_and_3_controls_scoped_numerical_pass'])
        self.assertEqual(result['scientific_admission'],'PENDING_INDEPENDENT_REVIEW')


if __name__ == '__main__':
    unittest.main(verbosity=2)
