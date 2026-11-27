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
        result={'schema':'WU088_NATIVE_INTERIOR_RESULT_V1','index':42,'task_sha256':'b'*64,'plan_sha256':'a'*64,
                'archive_sha256':'c'*64,'input_record_sha256':'d'*64,'build_source_sha256':'e'*64,
                'precision_bits':128,'accepted_component_radius_exp':-48,'status':'RADIUS_MET','accepted':True,
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

if __name__=='__main__': unittest.main(verbosity=2)
