import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

import moment_fit_diagnostic as diagnostic
import prepare_native


ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/'intake/native_original_35d9747/rust/rei_microphysics/src/axbi_covariant_transport.rs'


class MomentDiagnosticTests(unittest.TestCase):
    @unittest.skipUnless(ORIGINAL.is_file(),'exact native intake not present')
    def test_injection_only_changes_original_failure_branch(self):
        original=ORIGINAL.read_bytes()
        changed=diagnostic.instrument(original)
        self.assertEqual(changed.replace(diagnostic.INJECTION,b'',1),original)
        self.assertEqual(changed.count(diagnostic.ANCHOR),1)
        self.assertIn(diagnostic.INJECTION+diagnostic.ANCHOR,changed)
        with self.assertRaises(ValueError):
            diagnostic.instrument(original+b'\n')

    def test_prepared_mode_mismatch_cannot_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            destination=Path(directory)
            (destination/'PREPARED_IDENTITY.json').write_text(json.dumps(
                dict(native_sha='frozen',outputs={})))
            with mock.patch.object(prepare_native,'load_manifest',return_value=dict(native_sha='frozen')):
                with self.assertRaisesRegex(ValueError,'MODE_CONFLICT'):
                    prepare_native.prepare(ROOT,destination,moment_diagnostics=True)

    @unittest.skipUnless(shutil.which('rustc'),'rustc unavailable')
    def test_compiled_failure_emits_json_and_preserves_error(self):
        # Minimal standalone scope verifies Rust formatting and failure-only
        # placement. It does not replace the exact-algorithm synthetic probe.
        source=r'''
#![allow(dead_code)]
#[derive(Debug,PartialEq)] enum Failure { Original }
fn bad(_: &str)->Failure { Failure::Original }
fn cell(failed:bool)->Result<(),Failure> {
 let (lo,hi,n,u,r,mean,gap,beta,lambda)=(1f64,2f64,1f64,1.5f64,1f64,1.5f64,0.5f64,0f64,0f64);
 let (count_defect,energy_defect,energy_scale,node_lo,node_hi)=(1f64,1f64,1.5f64,1.1f64,1.9f64);
 let base=vec![(1.1f64,0.5f64),(1.9f64,0.5f64)];
 let result=vec![(1.1f64,0.5f64),(1.9f64,0.5f64)];
 let norm=1f64;
 let eval=|_:f64| (vec![0.5f64,0.5f64],0f64,1f64);
 if failed {
        return Err(bad("AXBI_COVARIANT_MOMENT_FIT"));
 }
 Ok(())
}
fn main() {
 assert_eq!(cell(false),Ok(()));
 assert_eq!(cell(true),Err(Failure::Original));
 assert_eq!(cell(true),Err(Failure::Original));
}
'''.encode()
        source=source.replace(diagnostic.ANCHOR,diagnostic.INJECTION+diagnostic.ANCHOR)
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory)
            path=directory/'probe.rs';path.write_bytes(source)
            build=subprocess.run(['rustc','--edition=2021',str(path),'-o',str(directory/'probe')],capture_output=True,text=True)
            self.assertEqual(build.returncode,0,build.stderr)
            run=subprocess.run([str(directory/'probe')],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            lines=run.stderr.splitlines()
            self.assertEqual(len(lines),1)
            self.assertTrue(lines[0].startswith('REI_MOMENT_DIAGNOSTIC '))
            payload=json.loads(lines[0].split(' ',1)[1])
            self.assertEqual(payload['n'],1.)
            self.assertEqual(payload['node_count'],2)


if __name__ == '__main__':
    unittest.main()
