"""Boundary tests are analytical fixtures, not native or HH execution evidence."""
import copy
from fractions import Fraction as Q
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('native_driver_tested',Path(__file__).with_name('driver.py'))
d=importlib.util.module_from_spec(spec); spec.loader.exec_module(d)

class NativeBoundaryTests(unittest.TestCase):
    def test_exact_rectangle_serialization_interpretation(self):
        self.assertEqual(d.dyadic_interval({'lower_mantissa':'-7','upper_mantissa':'9','exponent2':'-3'}),(Q(-7,8),Q(9,8)))
    def test_bad_integer_and_resource_endpoints_refused(self):
        for value in [True,0,'-0','01','1.0','1/2','NaN','1'*2501]:
            with self.subTest(value=str(value)[:20]),self.assertRaises(d.DriverError):
                d.dyadic_interval({'lower_mantissa':value,'upper_mantissa':'2','exponent2':'0'})
        for value in [{'lower_mantissa':'3','upper_mantissa':'2','exponent2':'0'},
                      {'lower_mantissa':'0','upper_mantissa':'2','exponent2':'8193'}]:
            with self.assertRaises(d.DriverError): d.dyadic_interval(value)
    def test_json_ambiguous_or_inexact_values_refused(self):
        for raw in [b'{"a":1,"a":2}',b'{"x":NaN}',b'{"x":0.5}']:
            with self.assertRaises(d.DriverError): d.parse_json(raw)
    def test_invalid_limits_and_bool_refused(self):
        self.assertEqual(d.limits_checked(d.DEFAULT_LIMITS),d.DEFAULT_LIMITS)
        for key,value in [('precision_bits',32),('max_evaluations',1000001),('wall_seconds',True),('relative_goal',1024)]:
            with self.subTest(key=key),self.assertRaises(d.DriverError):
                d.limits_checked(dict(d.DEFAULT_LIMITS,**{key:value}))
    def fixture(self):
        plan={'plan_sha256':'a'*64}; task={'index':42,'task_sha256':'b'*64}
        manifest={'archive_sha256':'c'*64,'input_record_sha256':'d'*64,'source':{'sha256':'e'*64}}
        result={'schema':'WU088_LOG2_NATIVE_INTERIOR_RESULT_V1','index':42,'task_sha256':'b'*64,'plan_sha256':'a'*64,
                'archive_sha256':'c'*64,'input_record_sha256':'d'*64,'build_source_sha256':'e'*64,
                'precision_bits':128,'accepted_component_radius_exp':-48,'coordinate_map':'LOG2_EXACT_POWER_ENDPOINTS_V1','status':'RADIUS_MET','accepted':True,
                'endpoint_included':False,'normalization_applied':False,'full_domain_integral':False,
                'scientific_admission':False,'production_admission':False,'flint_status':0,
                'dispatched_evaluations':10,'integration_calls':4,'callback_calls':10,'callback_refusals':1,'analytic_box_refusals':2,
                'rectangle':{'real':{'lower_mantissa':'0','upper_mantissa':'1','exponent2':'-48'},
                             'imag':{'lower_mantissa':'-1','upper_mantissa':'0','exponent2':'-48'}}}
        return result,dict(plan=plan,task=task,manifest=manifest,limits=d.DEFAULT_LIMITS)
    def test_accepted_fixture_stays_conditional(self):
        result,params=self.fixture()
        self.assertIs(d.validate_result(result,**params),result)
        self.assertFalse(result['full_domain_integral']); self.assertFalse(result['scientific_admission'])
    def test_radius_identity_and_promotion_rejected(self):
        result,params=self.fixture()
        for key,value in [('index',43),('task_sha256','f'*64),('production_admission',True),('accepted',1),
                          ('flint_status',1),('dispatched_evaluations',20001),('unspecified_claim',True)]:
            bad=copy.deepcopy(result); bad[key]=value
            with self.subTest(key=key),self.assertRaises(d.DriverError): d.validate_result(bad,**params)
        result['rectangle']['real']['upper_mantissa']='3'
        with self.assertRaises(d.DriverError): d.validate_result(result,**params)
    def test_missing_backend_preflight_refuses_execution(self):
        with tempfile.TemporaryDirectory() as td:
            result=d.preflight(Path(td)/'prefix',Path(td)/'BUILD.json')
            self.assertFalse(result['ready']); self.assertFalse(result['native_executed'])
            self.assertGreaterEqual(len(result['failures']),5)
    def test_immutable_dependencies_available(self):
        pins=d.verify_sources()
        self.assertGreaterEqual(len(pins),10)
    def test_create_only_output_preserves_existing(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'record.json'; d.write_new(out,{'a':1})
            with self.assertRaises(FileExistsError): d.write_new(out,{'a':2})
            self.assertEqual(d.parse_json(out.read_bytes()),{'a':1})
    def test_existing_output_refuses_before_native_or_input_work(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'completed.json'; out.write_text('{}')
            with patch.object(d,'dependencies') as deps,patch.object(d.subprocess,'Popen') as popen:
                with self.assertRaisesRegex(d.DriverError,'not rerun'):
                    d.run_task('unused','unused','a'*64,0,'unused','b'*64,d.DEFAULT_LIMITS,out)
                deps.assert_not_called(); popen.assert_not_called()
    def test_existing_task_claim_refuses_duplicate_execution(self):
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'new.json'; Path(str(out)+'.claim').write_text('another worker')
            with patch.object(d,'dependencies') as deps,patch.object(d.subprocess,'Popen') as popen:
                with self.assertRaises(FileExistsError):
                    d.run_task('unused','unused','a'*64,0,'unused','b'*64,d.DEFAULT_LIMITS,out)
                deps.assert_not_called(); popen.assert_not_called()

    def test_sigma_guard_includes_upper_endpoints(self):
        a,b=Q(1,500),Q(1,200)
        for T in (Q(2),Q(1<<64),Q(1<<192)):
            window={'l_t':'1/256','T_t':str(T),'l_u':'1/256','T_u':str(T)}
            margin=d.real_domain_margin(a,b,window)
            self.assertGreater(margin,0)
            sigma_min=(1/(a+T)+1/(b+T))/2
            self.assertLess(margin,sigma_min)
            self.assertLess(margin,Q(1,256))
            for t in (Q(1,256),Q(1),T):
                for u in (Q(1,256),Q(1),T):
                    self.assertLess(margin,(1/(a+t)+1/(b+u))/2)
            if T>=1<<64:self.assertGreater(Q(1,1<<28),sigma_min)

    def test_domain_guard_refuses_invalid_geometry(self):
        window={'l_t':'1','T_t':'2','l_u':'1','T_u':'2'}
        for a,b in ((Q(0),Q(1)),(Q(1),Q(-1)),(1.0,Q(1)),(True,Q(1))):
            with self.assertRaises(d.DriverError):d.real_domain_margin(a,b,window)
        with self.assertRaises(d.DriverError):d.real_domain_margin(Q(1),Q(1),{**window,'T_t':'1'})

    def test_overlay_source_identity_cannot_reuse_old_build(self):
        identity=d.source_identity()
        self.assertIn('wide_domain_20261001_v1/log_native_driver/driver.py',identity['files'])
        self.assertIn('wide_domain_20261001_v1/log_native_driver/primitive_worker.cpp',identity['files'])
        self.assertEqual(d.PLAN_MODULE,d.LADDER/'production_solver_20261001_v1/endpoint_tasks/planner.py')

    def test_cached_build_is_explicit_and_does_not_double_link_baseline(self):
        baseline=d.build_configuration('baseline');cached=d.build_configuration('cached')
        self.assertEqual(baseline['mode_flags'],['-DWU088_USE_CACHED=0'])
        self.assertEqual(cached['mode_flags'],['-DWU088_USE_CACHED=1'])
        self.assertIn(str(d.OLD/'validated_callback/callback.cpp'),baseline['sources'])
        self.assertNotIn(str(d.OLD/'validated_callback/callback.cpp'),cached['sources'])
        self.assertIn(str(d.LADDER/'ncp64_acceleration_20261001_v1/native_cache/cached_callback.cpp'),cached['sources'])
        with self.assertRaises(d.DriverError):d.build_configuration('automatic')

    def test_cached_dependency_sources_are_pinned(self):
        pins=d.verify_sources()
        for name in ('cached_callback.cpp','cached_callback.hpp'):
            self.assertIn('ncp64_acceleration_20261001_v1/native_cache/'+name,pins)

    def test_refining_host_is_additive_and_bound(self):
        identity=d.source_identity()
        self.assertIn('native_execution_20261001_v1/refining_petras.cpp',identity['files'])
        for mode in ('baseline','cached'):
            config=d.build_configuration(mode)
            self.assertIn(str(d.LADDER/'native_execution_20261001_v1/refining_petras.cpp'),config['sources'])
            self.assertNotIn(str(d.OLD/'interior_pilot/petras_host.cpp'),config['sources'])

    def test_log2_exact_windows(self):
        for lo,hi,e0,e1 in [('1','2',0,1),('1/16','256',-4,8),('1/256',str(1<<192),-8,192)]:
            self.assertEqual(d.log2_window({'l_t':lo,'T_t':hi,'l_u':lo,'T_u':hi}),
                             {'l_t':e0,'T_t':e1,'l_u':e0,'T_u':e1})
    def test_nonpower_noncanonical_negative_log_windows_rejected(self):
        for token in ['3','3/4','2/2','0','-1','1.0',True,str(1<<512)]:
            with self.subTest(token=token),self.assertRaises(d.DriverError):
                d.log2_window({'l_t':'1/16','T_t':token,'l_u':'1','T_u':'2'})
    def test_map_header_bound_and_default_cached(self):
        self.assertEqual(d.build_configuration()['callback_mode'],'cached')
        self.assertIn('wide_domain_20261001_v1/log_native_driver/log_map.hpp',d.source_identity()['files'])
    def test_native_failure_receipt_retains_binding_and_elapsed(self):
        import os,sys
        for code,reason in [(2,'NONZERO_NATIVE_EXIT'),(0,'INVALID_NATIVE_OUTPUT')]:
            with tempfile.TemporaryDirectory() as td:
                out=Path(td)/'failure.json';result,params=self.fixture()
                binding={'build_manifest_sha256':'1'*64,'binary_sha256':'2'*64,'build_source':{'sha256':'3'*64},
                         'native_execution_observed':False,'command':[sys.executable,'-c',f'print("invalid");raise SystemExit({code})']}
                with self.assertRaises(d.DriverError):
                    d.execute_bound_native(binding['command'],dict(os.environ),d.DEFAULT_LIMITS,binding,out,
                                           params['plan'],params['task'],params['manifest'])
                receipt=d.parse_json(out.read_bytes())
                self.assertEqual(receipt['reason'],reason)
                self.assertEqual(receipt['wrapper']['binary_sha256'],'2'*64)
                self.assertTrue(receipt['wrapper']['native_execution_observed'])
                self.assertGreater(receipt['wrapper']['elapsed_wall_ns'],0)
                body={k:v for k,v in receipt.items() if k!='result_sha256'}
                self.assertEqual(receipt['result_sha256'],d.digest(d.canonical(body)))
    def test_launch_failure_retains_binding(self):
        import os
        with tempfile.TemporaryDirectory() as td:
            out=Path(td)/'failure.json';result,params=self.fixture()
            binding={'binary_sha256':'2'*64,'native_execution_observed':False}
            with self.assertRaises(d.DriverError):
                d.execute_bound_native(['/no/such/program'],dict(os.environ),d.DEFAULT_LIMITS,binding,out,
                                       params['plan'],params['task'],params['manifest'])
            receipt=d.parse_json(out.read_bytes())
            self.assertEqual(receipt['reason'],'PROCESS_LAUNCH_FAILED')
            self.assertFalse(receipt['wrapper']['native_execution_observed'])
            self.assertGreater(receipt['wrapper']['elapsed_wall_ns'],0)

if __name__=='__main__': unittest.main(verbosity=2)
