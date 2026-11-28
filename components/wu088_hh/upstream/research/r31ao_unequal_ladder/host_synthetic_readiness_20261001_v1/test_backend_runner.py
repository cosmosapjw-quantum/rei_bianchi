"""Synthetic extraction/plan/refusal tests; no library or native compilation."""
import hashlib,io,json,os,tarfile,tempfile,unittest
import sys,time
import backend_runner as runner
from pathlib import Path
from backend_runner import RunnerError,safe_extract,build_steps,clean_environment,validate_config,CONFIG


def tar_payload(entries):
    out=io.BytesIO()
    with tarfile.open(fileobj=out,mode='w:gz') as tf:
        for name,data,kind in entries:
            item=tarfile.TarInfo(name);item.type=kind
            if kind==tarfile.REGTYPE:item.size=len(data);tf.addfile(item,io.BytesIO(data))
            else:item.linkname='../outside';tf.addfile(item)
    return out.getvalue()


class RunnerTests(unittest.TestCase):
    def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
    def tearDown(self):self.tmp.cleanup()
    def extract(self,entries,**kwargs):
        data=tar_payload(entries);source=self.root/'source.tgz';source.write_bytes(data)
        return safe_extract(source,self.root/'new',expected_sha256=hashlib.sha256(data).hexdigest(),expected_root='pkg',**kwargs)
    def test_safe_regular_archive(self):
        result=self.extract([('pkg/src/a.c',b'int x;',tarfile.REGTYPE)])
        self.assertEqual((result/'src/a.c').read_bytes(),b'int x;')
    def test_hash_before_extraction(self):
        p=self.root/'src';p.write_bytes(b'bad')
        with self.assertRaises(RunnerError):safe_extract(p,self.root/'new',expected_sha256='0'*64,expected_root='pkg')
        self.assertFalse((self.root/'new').exists())
    def test_path_symlink_duplicate_refusal(self):
        for entries in [[('pkg/../evil',b'',tarfile.REGTYPE)],[('/pkg/x',b'',tarfile.REGTYPE)],[('pkg/link',b'',tarfile.SYMTYPE)],[('pkg/x',b'',tarfile.REGTYPE),('pkg/x',b'',tarfile.REGTYPE)]]:
            with self.subTest(entries=entries),self.assertRaises(RunnerError):self.extract(entries)
            if (self.root/'new').exists():self.fail('validation mutated destination')
    def test_extraction_create_only_and_caps(self):
        self.extract([('pkg/a',b'abc',tarfile.REGTYPE)])
        with self.assertRaises(RunnerError):self.extract([('pkg/a',b'abc',tarfile.REGTYPE)])
    def test_member_budget_refusal(self):
        with self.assertRaises(RunnerError):self.extract([('pkg/a',b'abc',tarfile.REGTYPE)],max_file_bytes=2)
    def test_plan_order_flags_and_no_network_commands(self):
        steps=build_steps(self.root,self.root/'prefix',{'sh':'/bin/sh','make':'/usr/bin/make'},CONFIG)
        ids=[s['id'] for s in steps]
        self.assertLess(ids.index('gmp-install'),ids.index('mpfr-configure'))
        self.assertLess(ids.index('mpfr-install'),ids.index('flint-bootstrap'))
        self.assertLess(ids.index('flint-bootstrap'),ids.index('flint-configure'))
        for s in steps:
            self.assertIsInstance(s['argv'],list)
            self.assertFalse(any(x in s['argv'] for x in ('sudo','apt','pip','curl','wget','git')))
            if 'make' in Path(s['argv'][0]).name:self.assertIn('-j2',s['argv'])
        mpfr=next(s for s in steps if s['id']=='mpfr-configure')
        self.assertIn('--with-gmp='+str(self.root/'prefix'),mpfr['argv'])
    def test_config_refuses_unbounded_jobs_and_caps(self):
        for key,value in [('jobs',3),('global_wall_seconds',0),('memory_mib',999999)]:
            c=dict(CONFIG);c[key]=value
            with self.assertRaises(RunnerError):validate_config(c)
    def test_clean_environment(self):
        previous=dict(os.environ)
        try:
            os.environ.update(LD_PRELOAD='/evil.so',PYTHONPATH='/evil',MAKEFLAGS='-j99',http_proxy='http://bad',CFLAGS='-ffast-math')
            e=clean_environment(self.root,self.root/'prefix',{'cc':'/usr/bin/gcc','cxx':'/usr/bin/g++'},CONFIG)
            self.assertNotIn('LD_PRELOAD',e);self.assertNotIn('PYTHONPATH',e);self.assertNotIn('MAKEFLAGS',e)
            self.assertNotIn('http_proxy',e);self.assertNotIn('-ffast-math',e['CFLAGS'])
            self.assertNotIn('HOME',e)
        finally:os.environ.clear();os.environ.update(previous)
    def test_petras_final_line_marker_with_locked_diagnostics(self):
        text='one_dimensional_polynomial=0.3333333333\nnested_polynomial=0.25\n'+json.dumps({'synthetic_only':True,'native_fixture_checks':10,'actual_HH_evaluations':0})+'\n'
        p=runner.parse_native_marker('petras',text)
        self.assertEqual(p['payload']['actual_HH_evaluations'],0)
        self.assertEqual(len(p['diagnostic_lines']),2)
        with self.assertRaises(runner.RunnerError):runner.parse_native_marker('petras',text+'untrusted trailing output\n')
    def test_callback_marker_refuses_false_extra_and_nonzero_hh(self):
        for p in [{'scope':'SYNTHETIC_ONLY','native_synthetic_passed':False},
                  {'scope':'SYNTHETIC_ONLY','native_synthetic_passed':True,'extra':True}]:
            with self.assertRaises(runner.RunnerError):runner.parse_native_marker('callback',json.dumps(p))
        with self.assertRaises(runner.RunnerError):runner.parse_native_marker('petras',json.dumps({'synthetic_only':True,'native_fixture_checks':10,'actual_HH_evaluations':1}))
    def test_bounded_python_stage_and_timeout(self):
        root=self.root/'stage';root.mkdir();(root/'logs').mkdir()
        config=dict(CONFIG);config['memory_mib']=128
        step={'id':'synthetic-python','stage':'guard-test','cwd':str(root),'argv':[sys.executable,'-I','-c','print("synthetic")'],'wall_seconds':2}
        r=runner.run_stage(step,root,{'PATH':'/usr/bin:/bin'},config,time.monotonic()+3)
        self.assertEqual(r['exit_code'],0);self.assertFalse(r['aggregate_tree_memory_limit'])
        step.update(id='synthetic-timeout',argv=[sys.executable,'-I','-c','import time;time.sleep(2)'],wall_seconds=0.1)
        with self.assertRaises(runner.RunnerError):runner.run_stage(step,root,{'PATH':'/usr/bin:/bin'},config,time.monotonic()+3)
        self.assertEqual(json.loads((root/'logs/synthetic-timeout/STAGE.json').read_text())['reason'],'WALL_LIMIT')
    def test_extraction_expansion_count_and_ancestor_caps(self):
        for entries,kw in [([('pkg/a',b'x'*1024,tarfile.REGTYPE)],{'max_expanded_bytes':128}),
                           ([('pkg/a',b'a',tarfile.REGTYPE),('pkg/b',b'b',tarfile.REGTYPE)],{'max_members':1}),
                           ([('pkg/a',b'a',tarfile.REGTYPE),('pkg/a/b',b'b',tarfile.REGTYPE)],{})]:
            with self.assertRaises(runner.RunnerError):self.extract(entries,**kw)
            self.assertFalse((self.root/'new').exists())


if __name__=='__main__':unittest.main(verbosity=2)
