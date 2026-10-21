"""Isolate compile/restore boundaries to exercise actual main flag routing."""
import contextlib,hashlib,importlib.util,io,json,os
from pathlib import Path
import sys,tempfile,unittest
from unittest.mock import patch

MODIFIED=Path(__file__).resolve().parents[1]/'prepare_and_run.py'

class PrepareFlagTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.r=Path(self.temp.name);self.calls=[]
        (self.r/'VIGILODE_PIN.json').write_text('{}');(self.r/'VIGILODE_SOURCE_MANIFEST.json').write_text('{}')
        (self.r/'BASE_NATIVE_MANIFEST.json').write_text(json.dumps({'src/axbi_covariant_transport.rs':hashlib.sha256(b'BASE').hexdigest()}))
        for name,data in [('native_additions/transport_hook.txt','HOOK'),('native_additions/axbi_native_rhs.rs','CODE'),('src/main.rs','SRC'),('tests/focused.rs','TEST'),('Cargo.lock','LOCK'),('Cargo.toml','MANIFEST')]:
            p=self.r/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(data)
        copy=self.r/'prepare_and_run.py';copy.write_bytes(MODIFIED.read_bytes())
        spec=importlib.util.spec_from_file_location('flag_prepare',copy);self.mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.mod)
        self.restore=self.r/'restore.py';self.restore.write_text('# process test stub')
        def capture(folder,argv,env=None,timeout=60,sources=()):
            folder.mkdir(parents=True,exist_ok=False);self.calls.append((folder.name,argv,env))
            if folder.name.endswith('.prepare_evidence'):
                out=Path(argv[-1]);p=out/'native_owner/rust/rei_microphysics/src/axbi_covariant_transport.rs';p.parent.mkdir(parents=True);p.write_bytes(b'BASE')
            if folder.name=='release_build':
                p=self.r/'out/adapter/target/release/rei-vigilode-radau-research';p.parent.mkdir(parents=True);p.write_bytes(b'PROCESS_TEST_STUB_NOT_NATIVE')
            return {'exit_code':0}
        self.mod.capture=capture
        def vigilode(args,out):p=out/'vigilode';p.mkdir();return p
        self.mod.restore_vigilode=vigilode;self.mod.record_toolchain=lambda *a:None
        self.runs=[]
        def cases(*args,**kwargs):self.runs.append((args,kwargs));return 0
        self.mod.run_cases=cases
    def tearDown(self):self.temp.cleanup()
    def invoke(self,*flags):
        argv=['prepare','--ssprk-restore',str(self.restore),'--output-root',str(self.r/'out'),*flags]
        with patch.object(sys,'argv',argv),patch.dict(os.environ,{'CARGO_TARGET_DIR':'/unwanted/external/target'}),contextlib.redirect_stdout(io.StringIO()):return self.mod.main()
    def test_build_only_has_no_science_and_explicit_build_jobs(self):
        self.invoke('--build-only','--build-jobs','3')
        self.assertEqual(self.runs,[])
        build=next(x for x in self.calls if x[0]=='release_build')
        self.assertEqual(build[2]['CARGO_BUILD_JOBS'],'3');self.assertNotIn('CARGO_TARGET_DIR',build[2])
        receipt=json.loads((self.r/'out/evidence/BUILD_ONLY_RECEIPT.json').read_text());self.assertEqual(receipt['scientific_cases'],'NOT_RUN')
        self.assertFalse(any(x[0]=='focused_tests'for x in self.calls))
    def test_optional_focused_tests_are_explicit(self):
        self.invoke('--build-only','--run-focused-tests')
        self.assertTrue(any(x[0]=='focused_tests'for x in self.calls));self.assertEqual(self.runs,[])
    def test_original_all_default_is_legacy_and_nineteen_cases(self):
        self.invoke('--all')
        args,kw=self.runs[0];self.assertEqual(len(args[2]),19);self.assertEqual(kw['case_args'],['--native-eval','legacy'])
        build=next(x for x in self.calls if x[0]=='release_build');self.assertEqual(build[2]['CARGO_BUILD_JOBS'],'1')
    def test_case_profile_forwarding_remains_explicit(self):
        self.invoke('--case','fixed','radau','2','--native-eval','cell-cache','--profile')
        args,kw=self.runs[0];self.assertEqual(args[2],[('fixed','radau','2')]);self.assertEqual(kw['case_args'],['--native-eval','cell-cache','--profile'])
    def test_nonpositive_build_jobs_rejected_before_restore(self):
        with self.assertRaises(SystemExit),contextlib.redirect_stderr(io.StringIO()):self.invoke('--build-only','--build-jobs','0')
        self.assertEqual(self.calls,[])

if __name__=='__main__':unittest.main()
