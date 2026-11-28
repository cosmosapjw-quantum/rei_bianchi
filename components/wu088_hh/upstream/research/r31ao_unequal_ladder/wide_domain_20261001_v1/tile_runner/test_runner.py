"""Read-only existing HH receipt validation plus mocked sequential dispatch; zero HH reruns."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock,patch

spec=importlib.util.spec_from_file_location('tested_tile_runner',Path(__file__).with_name('runner.py'))
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx=r.context()
        path=r.LADDER/'native_execution_20261001_v1/runtime/pilot_plans/CENTRAL_PLAN.json'
        cls.g=cls.ctx['d'].parse_json(r.read(path));r.validate_global(cls.ctx,cls.g,cls.g['plan_sha256'])
        cls.ctx['global_plan']=cls.g
        cls.grid=r.bound_grid(cls.ctx,cls.g,0)
        cls.local=r.native_plan(cls.ctx,cls.g,cls.grid['tiles'][0]['window'])
        cls.raw=r.read(r.NEW/'runtime/LOG2_CENTRAL.json')
    def test_actual_central_readonly_normalize_and_collect(self):
        record=r.normalize(self.ctx,self.grid,self.local,0,self.raw)
        result=self.ctx['c'].collect(self.grid,[record])
        self.assertEqual(result['status'],'COMPLETE_COMPACT_INTERIOR_RADIUS_MET')
        self.assertEqual(record['native_receipt_sha256'],r.digest(self.raw))
        self.assertEqual(record['native_plan_sha256'],self.g['plan_sha256'])
        self.assertEqual(result['bindings']['global_endpoint_plan_sha256'],self.g['plan_sha256'])
        self.assertNotEqual(result['global_plan_sha256'],self.g['plan_sha256'])
    def test_corrupt_wrapper_refused_even_after_resigning(self):
        cases={'binary_sha256':'0'*64,'build_manifest_sha256':'0'*64,'build_source':{},
               'command':['/bin/true'],'physical_window':{'l_t':'2'},'log2_window':{'l_t':2},
               'native_limits':{},'linkage':{},'backend_provenance_sha256':'0'*64,
               'archive_sha256':'0'*64,'native_execution_observed':False,'returncode':1,
               'coordinate_map':'LINEAR','elapsed_wall_ns':True,'extra':1}
        for key,value in cases.items():
            with self.subTest(key=key):
                record=json.loads(self.raw);record['wrapper'][key]=value;record.pop('result_sha256')
                payload=r.canonical(r.sealed(record,'result_sha256'))
                with self.assertRaises(ValueError):r.normalize(self.ctx,self.grid,self.local,0,payload)
    def test_raw_selfhash_and_wrong_tile_refused(self):
        record=json.loads(self.raw);record['index']=1
        with self.assertRaises(ValueError):r.normalize(self.ctx,self.grid,self.local,0,r.canonical(record))
        with self.assertRaises(ValueError):r.normalize(self.ctx,self.grid,self.local,1,self.raw)
    def test_global_scope_change_refused(self):
        ctx=dict(self.ctx);ctx['global_plan']=copy.deepcopy(self.g);ctx['global_plan']['window']['T_t']='4'
        with self.assertRaises(ValueError):r.normalize(ctx,self.grid,self.local,0,self.raw)
    def test_resealed_arbitrary_global_endpoint_sha_refused(self):
        grid=copy.deepcopy(self.grid);grid['bindings']['global_endpoint_plan_sha256']='0'*64
        grid.pop('plan_sha256');grid=r.sealed(grid,'plan_sha256')
        with self.assertRaises(ValueError):r.normalize(self.ctx,grid,self.local,0,self.raw)
    def test_prepare_and_load_single_tile_no_native(self):
        path=r.LADDER/'native_execution_20261001_v1/runtime/pilot_plans/CENTRAL_PLAN.json'
        with tempfile.TemporaryDirectory() as td,patch.object(r,'context',return_value=self.ctx),patch.object(self.ctx['d'],'run_task') as execute:
            out=Path(td)/'prepared';m=r.prepare(path,self.g['plan_sha256'],0,out)
            _,restored,plans=r.load_prepared(out,m['manifest_sha256'])
            self.assertEqual(restored,m);self.assertEqual(plans,[self.local]);execute.assert_not_called()
            with self.assertRaises(FileExistsError):r.prepare(path,self.g['plan_sha256'],0,out)
    def test_w1_exact_caps_and_w3_refusal(self):
        g=copy.deepcopy(self.g);g['window']={'l_t':'1/16','T_t':'256','l_u':'1/16','T_u':'256'}
        grid=r.bound_grid(self.ctx,g,0);self.assertEqual(grid['tile_count'],16);self.assertEqual(grid['tile_radius_exp'],-52)
        limits=r.limits_for(self.ctx,grid);self.assertEqual(limits['max_evaluations']*16,320000)
        self.assertEqual((limits['wall_seconds']+5)*16,560)
        g['window']={'l_t':'1/256','T_t':str(1<<192),'l_u':'1/256','T_u':str(1<<192)}
        with self.assertRaises(ValueError):r.bound_grid(self.ctx,g,0)
    def test_mock_sequential_stops_on_third_failure_and_never_collects(self):
        calls=[]
        def dispatch(*args):
            i=len(calls);calls.append(i);Path(args[-1]).write_text('{}')
            if i==2:raise ValueError('SYNTHETIC_FORCED_REJECTION')
        d=types.SimpleNamespace(run_task=dispatch)
        c=types.SimpleNamespace(collect=Mock(side_effect=AssertionError('must not collect incomplete tiles')))
        ctx={'d':d,'c':c,'global_plan':{}}
        grid={'tiles':[{'tile_id':i} for i in range(16)],'tile_count':16,'primitive_index':0,
              'bindings':{'global_endpoint_plan_sha256':'a'*64},'plan_sha256':'b'*64}
        m={'grid':grid,'limits':{'max_evaluations':20000},'max_dispatched_evaluations':320000,
           'local_plans':[{'path':'plans/%02d.json'%i} for i in range(16)]}
        plans=[{'plan_sha256':str(i)*64} for i in range(16)]
        with tempfile.TemporaryDirectory() as td,patch.object(r,'load_prepared',return_value=(ctx,m,plans)),\
             patch.object(r,'context',return_value=ctx),patch.object(r,'normalize',return_value={'SYNTHETIC':True}):
            result=r.run_prepared(td,'c'*64)
            self.assertEqual(calls,[0,1,2]);self.assertEqual(result['accepted_tiles'],2)
            self.assertEqual(result['attempted_tiles'],3);self.assertEqual(result['native_cap_charged'],60000)
            self.assertEqual(result['status'],'STOPPED_FIRST_REJECTION');c.collect.assert_not_called()
            self.assertTrue((Path(td)/'RUN_RESULT.json').is_file())
            with self.assertRaises(ValueError):r.run_prepared(td,'c'*64)
    def test_existing_claim_refuses_before_context(self):
        with tempfile.TemporaryDirectory() as td,patch.object(r,'load_prepared') as load:
            (Path(td)/'RUN.claim').write_text('existing')
            with self.assertRaises(FileExistsError):r.run_prepared(td,'a'*64)
            load.assert_not_called()

if __name__=='__main__':unittest.main(verbosity=2)
