"""Actual saved receipt validation and synthetic orchestration; no HH execution."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import types
import unittest
from unittest.mock import Mock,patch

spec=importlib.util.spec_from_file_location('tested_w1_runner',Path(__file__).with_name('runner.py'))
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
FAKE_HOST=types.SimpleNamespace(identity=lambda:{'TEST_ONLY':'NO_NATIVE_EXECUTION'})

class RunnerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx=r.context();cls.g=cls.ctx['d'].parse_json(r.read(r.GLOBAL));cls.ctx['global_plan']=cls.g
        cls.grid=r.bound_grid(cls.ctx,cls.g,0);cls.local=cls.ctx['d'].parse_json(r.read(r.PRIOR/'plans/00.json'))
        cls.raw=r.read(r.IMPORTED)
    def normalize_old(self,payload=None,**kwargs):
        return r.normalize(self.ctx,self.grid,self.local,0,payload or self.raw,origin='imported',receipt_path=r.IMPORTED,**kwargs)
    def test_import_saved_tile_zero_without_execution(self):
        with patch.object(self.ctx['d'],'run_task') as run:
            record=self.normalize_old();run.assert_not_called()
        self.assertEqual(record['native_receipt_sha256'],r.IMPORTED_SHA)
        self.assertEqual(record['requested_radius_exp'],-52)
        self.assertEqual(self.grid['tile_count'],16)
    def test_old_import_strict_immutable_even_resealed(self):
        for key,value in [('status','RESOURCE_LIMIT'),('accepted',False),('index',1)]:
            with self.subTest(key=key):
                value_record=json.loads(self.raw);value_record[key]=value;value_record.pop('result_sha256')
                with self.assertRaises(ValueError):self.normalize_old(r.canonical(r.sealed(value_record,'result_sha256')))
    def test_old_receipt_not_new_or_other_tile(self):
        with self.assertRaises(ValueError):r.normalize(self.ctx,self.grid,self.local,0,self.raw)
        with self.assertRaises(ValueError):r.normalize(self.ctx,self.grid,self.local,1,self.raw,origin='imported',receipt_path=r.IMPORTED)
    def test_fixed_explicit_accuracy_and_cap(self):
        limits=r.limits_for(self.ctx,self.grid)
        self.assertEqual(limits,{'degree_limit':64,'max_evaluations':200000,'max_integration_calls':1024,'memory_mib':1024,
            'precision_bits':128,'queued_panels':64,'radius_exp':-52,'relative_goal':128,'wall_seconds':120})
    def test_resealed_global_binding_refused(self):
        grid=copy.deepcopy(self.grid);grid['bindings']['global_endpoint_plan_sha256']='0'*64
        grid.pop('plan_sha256');grid=r.sealed(grid,'plan_sha256')
        with self.assertRaises(ValueError):r.normalize(self.ctx,grid,self.local,0,self.raw,origin='imported',receipt_path=r.IMPORTED)
    def test_prepare_and_resume_revalidates_without_native(self):
        with tempfile.TemporaryDirectory() as td,patch.object(r,'context',return_value=dict(self.ctx)),patch.object(r,'host_module',return_value=FAKE_HOST),patch.object(self.ctx['d'],'run_task') as run:
            root=Path(td)/'case';m=r.prepare(root,3);ctx,m2,plans=r.load_prepared(root,m['manifest_sha256'])
            records,failures,attempted=r.load_state(root,ctx,m2,plans)
            self.assertEqual(sorted(records),[0]);self.assertEqual(failures,[]);self.assertEqual(attempted,[]);run.assert_not_called()
            self.assertEqual(m['max_dispatched_evaluations'],3000000)
            with self.assertRaises(FileExistsError):r.prepare(root,3)
    def test_resealed_limits_cannot_resume(self):
        with tempfile.TemporaryDirectory() as td,patch.object(r,'context',return_value=dict(self.ctx)),patch.object(r,'host_module',return_value=FAKE_HOST):
            root=Path(td)/'case';m=r.prepare(root,3);m['limits']['relative_goal']=64;m.pop('manifest_sha256');m=r.sealed(m,'manifest_sha256')
            (root/'PREPARED.json').write_text(json.dumps(m))
            with self.assertRaises(ValueError):r.load_prepared(root,m['manifest_sha256'])
    def test_unresolved_dispatch_never_rerun(self):
        with tempfile.TemporaryDirectory() as td,patch.object(r,'context',return_value=dict(self.ctx)),patch.object(r,'host_module',return_value=FAKE_HOST):
            root=Path(td)/'case';m=r.prepare(root,3);ctx,m,plans=r.load_prepared(root,m['manifest_sha256'])
            ad=root/'attempts/01';ad.mkdir();r.write_new(ad/'DISPATCH.json',r.sealed({'schema':'WU088_W1_TILE_DISPATCH_V1',
                'tile_id':1,'prepared_sha256':m['manifest_sha256'],'validator_source_sha256':r.source_sha(),
                'plan_sha256':plans[1]['plan_sha256'],'native_cap_charged':200000,'native_execution_requested':True},'dispatch_sha256'))
            with self.assertRaisesRegex(ValueError,'unresolved dispatched'):r.load_state(root,ctx,m,plans)
    def test_stale_claim_refuses_before_context(self):
        with tempfile.TemporaryDirectory() as td,patch.object(r,'load_prepared') as load:
            (Path(td)/'RUN.claim').write_text('old-owner')
            with self.assertRaises(FileExistsError):r.run_prepared(td,'a'*64)
            load.assert_not_called()
    def test_synthetic_exact_collection_gaps_and_duplicates(self):
        c=self.ctx['c'];records=[]
        from fractions import Fraction
        radius=Fraction(2)**-52
        for tile in self.grid['tiles']:
            i=tile['tile_id'];record={**self.normalize_old(),'tile_id':i,'window':tile['window'],
                'native_plan_sha256':('%064x'%(i+1)),'native_receipt_sha256':('%064x'%(100+i)),
                'rectangle':{p:{'lower':str(i-radius),'upper':str(i+radius)} for p in ('real','imag')},
                'reported_radius':{p:str(radius) for p in ('real','imag')}}
            record.pop('record_sha256');records.append(c.seal_normalized_record(record))
        result=c.collect(self.grid,records);self.assertEqual(result['component_radius']['real'],str(Fraction(2)**-48))
        self.assertEqual(result['rectangle']['real']['lower'],str(120-16*radius))
        with self.assertRaises(ValueError):c.collect(self.grid,records[:-1])
        with self.assertRaises(ValueError):c.collect(self.grid,[records[0]]+records[:-1])
    def test_synthetic_parallel_stops_dispatch_and_drains_inflight(self):
        calls=[]
        class Process:
            def __init__(self,i):self.i=i;self.pid=900000+i
            def poll(self):return 1 if self.i==2 else 0
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for folder in ('raw','normalized','attempts','sessions'):(root/folder).mkdir()
            def spawn(command,**kwargs):
                i=int(command[-1]);calls.append(i);(root/'raw'/('%02d.json'%i)).write_text('{}')
                self.assertEqual(kwargs['env']['OPENBLAS_NUM_THREADS'],'1')
                return Process(i)
            host=types.SimpleNamespace(identity=FAKE_HOST.identity,spawn_guarded=spawn)
            with patch.object(r,'host_module',return_value=host):m=r.contract(dict(self.ctx),3)
            plans={i:{'plan_sha256':'%064x'%i} for i in range(16)}
            ctx={'global_plan':self.g,'c':types.SimpleNamespace(collect=Mock(side_effect=AssertionError('incomplete')))}
            norm=lambda ctx,grid,plan,i,raw,**kwargs:{'record_sha256':'%064x'%(i+100),'tile_id':i}
            with patch.object(r,'load_prepared',return_value=(ctx,m,plans)),patch.object(r,'load_state',return_value=({0:{}},[],[])),patch.object(r,'resource_admission',return_value={}),patch.object(r,'host_module',return_value=host),patch.object(r,'context',return_value=ctx),patch.object(r,'normalize',side_effect=norm):
                result=r.run_prepared(root,m['manifest_sha256'])
            self.assertEqual(calls,[1,2,3]);self.assertEqual(result['accepted_tile_ids'],[0,1,3])
            self.assertEqual(result['status'],'STOPPED_FIRST_REJECTION');self.assertEqual(result['new_dispatch_count'],3)
            self.assertEqual([item['status'] for item in result['tile_returns']],['ACCEPTED','REJECTED','ACCEPTED'])
            self.assertFalse((root/'RUN.claim').exists());ctx['c'].collect.assert_not_called()

    def test_synthetic_new_stdout_tamper_and_timeout_refused(self):
        local=self.ctx['d'].parse_json(r.read(r.PRIOR/'plans/01.json'))
        original=json.loads(self.raw);native={k:v for k,v in original.items() if k not in ('wrapper','result_sha256')}
        native['plan_sha256']=local['plan_sha256'];native['task_sha256']=local['tasks'][0]['task_sha256']
        wrapper=copy.deepcopy(original['wrapper']);wrapper['physical_window']=local['window'];wrapper['log2_window']=self.ctx['d'].log2_window(local['window'])
        wrapper['command'][2:6]=[local['window'][k] for k in ('l_t','T_t','l_u','T_u')]
        wrapper['command'][-2:]=[native['task_sha256'],native['plan_sha256']]
        wrapper['process_host']={'timed_out':False,'native_execution_evidence':'SOURCE_BOUND_NATIVE_STDOUT'}
        stdout=r.canonical(native);stderr=b'';wrapper['native_stdout_sha256']=r.digest(stdout);wrapper['native_stderr_sha256']=r.digest(stderr)
        host=types.SimpleNamespace(validate_receipt=Mock())
        with tempfile.TemporaryDirectory() as td,patch.object(r,'host_module',return_value=host):
            rp=Path(td)/'01.json';Path(str(rp)+'.stdout').write_bytes(stdout);Path(str(rp)+'.stderr').write_bytes(stderr)
            record=r.sealed({**native,'wrapper':wrapper},'result_sha256')
            accepted=r.normalize(self.ctx,self.grid,local,1,r.canonical(record),receipt_path=rp)
            self.assertEqual(accepted['tile_id'],1)
            bad=copy.deepcopy(record);bad['wrapper']['process_host']['timed_out']=True;bad.pop('result_sha256')
            with self.assertRaisesRegex(ValueError,'no timeout'):r.normalize(self.ctx,self.grid,local,1,r.canonical(r.sealed(bad,'result_sha256')),receipt_path=rp)
            bad=copy.deepcopy(record);bad['rectangle']['real']['lower_mantissa']='0';bad['rectangle']['real']['upper_mantissa']='0';bad.pop('result_sha256')
            with self.assertRaisesRegex(ValueError,'retained stdout'):r.normalize(self.ctx,self.grid,local,1,r.canonical(r.sealed(bad,'result_sha256')),receipt_path=rp)
            Path(str(rp)+'.stderr').write_bytes(b'tamper')
            with self.assertRaisesRegex(ValueError,'stream hash'):r.normalize(self.ctx,self.grid,local,1,r.canonical(record),receipt_path=rp)

    def test_current_resources_admit_three_not_four(self):
        with patch.object(r,'host_module',return_value=FAKE_HOST):
            m=r.contract(dict(self.ctx),3);resources=r.resource_admission(m)
            self.assertEqual(resources['reservation_bytes'],8*1024**3)
            m['concurrency']=4
            with self.assertRaisesRegex(ValueError,'memory'):r.resource_admission(m)

if __name__=='__main__':unittest.main(verbosity=2)
