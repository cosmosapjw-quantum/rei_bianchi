"""Compiled fixed-cell regressions; no physical campaign or convergence claim."""
from pathlib import Path
from unittest.mock import patch
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest

import prepare_native
import subnormal_count_rounding as count
import subnormal_moment_rounding as pair

ROOT = Path(__file__).resolve().parents[1]


def rust_nodes(cell):
    return ','.join(f'({q:.17e}f64,{number:.17e}f64)'
                    for q, probability, number in cell['nodes_q_probability_number'])


class SubnormalMomentTests(unittest.TestCase):
    def test_instrumentation_is_failed_branch_only_and_modes_are_stable(self):
        original = b'// Mock source for injection structure, not native identity.\n' + pair.ANCHOR
        blob = hashlib.sha1(b'blob ' + str(len(original)).encode() + b'\0' + original).hexdigest()
        with patch.object(pair, 'ORIGINAL_BLOB', blob):
            changed = pair.instrument_pair_rounding(original)
            self.assertEqual(changed.replace(pair.INJECTION, b'', 1), original)
            self.assertEqual(pair.pair_rounding_identity(), hashlib.sha256(pair.INJECTION).hexdigest())
            with self.assertRaisesRegex(ValueError, 'ORIGINAL_IDENTITY'):
                pair.instrument_pair_rounding(original + b'\n')
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            identity = dict(native_sha='mock', outputs={}, moment_rounding='subnormal-pair',
                            moment_rounding_injection_sha256='changed')
            (dest / 'PREPARED_IDENTITY.json').write_text(json.dumps(identity))
            with patch.object(prepare_native, 'load_manifest', return_value=dict(native_sha='mock')):
                with self.assertRaisesRegex(ValueError, 'ROUNDING_VERSION_CONFLICT'):
                    prepare_native.prepare(ROOT, dest, moment_rounding='subnormal-pair')
                with self.assertRaisesRegex(ValueError, 'ROUNDING_MODE_CONFLICT'):
                    prepare_native.prepare(ROOT, dest, moment_rounding='subnormal-count')
        # The historical count implementation is imported unchanged, not copied/revised.
        self.assertTrue(pair.INJECTION.startswith(count.CANDIDATE_HELPER))

    def test_actual_count_pair_and_gate_controls_compiled(self):
        first = json.loads((ROOT / 'tests/fixtures/subnormal_count_captured_cell.json').read_text())
        later = json.loads((ROOT / 'tests/fixtures/subnormal_pair_captured_cell.json').read_text())['cell']
        self.assertEqual(len(later['nodes_q_probability_number']), 128)
        prefix = r'''
#![allow(dead_code)]
#[derive(Debug)] enum ForwardError { InvalidInput(&'static str) }
fn bad(tag:&'static str)->ForwardError { ForwardError::InvalidInput(tag) }
#[derive(Default)] struct Diagnostics { max_count_relative_defect:f64, max_energy_relative_defect:f64 }
fn sum(xs:impl Iterator<Item=f64>)->f64 {
 let (mut total,mut correction)=(0.0,0.0);
 for x in xs { let y=x-correction;let next=total+y;correction=(next-total)-y;total=next; }
 total
}
fn trial(n:f64,u:f64,width:f64,result:Vec<(f64,f64)>,enabled:bool,f:f64)
 ->Result<Vec<(f64,f64)>,ForwardError> {
 let count_defect=(sum(result.iter().map(|x|x.1))-n).abs();
 let energy_defect=(sum(result.iter().map(|x|x.0*x.1))-u).abs();
 let energy_scale=u.abs().max(n*width);
 let lambda=0f64;let eval=|_:f64|(Vec::<f64>::new(),f,0f64);
 let mut diagnostics=Diagnostics::default();
 if count_defect>64.0*f64::EPSILON*n || energy_defect>128.0*f64::EPSILON*energy_scale {
  if enabled {
'''
        middle = r'''
  }
  return Err(bad("AXBI_COVARIANT_MOMENT_FIT"));
 }
 Ok(result)
}
'''
        suffix = r'''
fn main() {
 let eta=f64::from_bits(1);
 let first=vec![FIRST];
 let n=f64::from_bits(240243477644326);let u=f64::from_bits(4094958919588752);
 assert!(trial(n,u,3.4612670487769624,first.clone(),false,0.0).is_err());
 let fixed=trial(n,u,3.4612670487769624,first.clone(),true,6.769278295586412e-17).unwrap();
 assert_eq!((sum(fixed.iter().map(|x|x.1))-n).abs().to_bits(),0);
 assert_eq!((sum(fixed.iter().map(|x|x.0*x.1))-u).abs().to_bits(),4);
 assert_eq!(rei_subnormal_l1(&first,&fixed),5);
 let nodes=vec![LATER];
 let n=f64::from_bits(1244638132025);let u=f64::from_bits(21215026808689);
 assert!(trial(n,u,3.4612670487769624,nodes.clone(),false,0.0).is_err());
 let repaired=trial(n,u,3.4612670487769624,nodes.clone(),true,7.28135986364630949e-17).unwrap();
 let metadata=rei_subnormal_pair_candidate(n,u,u,&nodes).unwrap();
 assert_eq!(metadata.pair,Some((24,0)));
 assert_eq!(metadata.count_distance,0);assert_eq!(metadata.l1_ticks,2);
 assert_eq!((sum(repaired.iter().map(|x|x.1))-n).abs().to_bits(),0);
 assert_eq!((sum(repaired.iter().map(|x|x.0*x.1))-u).abs().to_bits(),1);
 for (old,new) in nodes.iter().zip(&repaired) {
  assert_eq!(old.0.to_bits(),new.0.to_bits());
  assert_eq!(old.1>0.0,new.1>0.0);
 }
 // The exact-count base is restored first, then the same pair is checked.
 let mut combined=nodes.clone();combined[1].1=f64::from_bits(combined[1].1.to_bits()+1);
 let metadata=rei_subnormal_pair_candidate(n,u,u,&combined).unwrap();
 assert_eq!(metadata.count_distance,1);assert_eq!(metadata.l1_ticks,3);
 assert_eq!(metadata.pair,Some((24,0)));
 assert_eq!(metadata.after_ticks,n.to_bits() as u128);
 assert!(trial(n,u,3.4612670487769624,nodes.clone(),true,1e-8).is_err());
 // Originally passing normal and subnormal vectors remain byte-identical.
 for (n,u,passing) in [(1.0,1.0,vec![(1.0,1.0)]),
                       (10.0*eta,10.0*eta,vec![(1.0,10.0*eta)])] {
  let got=trial(n,u,1.0,passing.clone(),true,0.0).unwrap();
  assert!(passing.iter().zip(&got).all(|(a,b)|a.0.to_bits()==b.0.to_bits()&&a.1.to_bits()==b.1.to_bits()));
 }
 assert!(trial(1.0,1.0,1.0,vec![(1.0,1.1)],true,0.0).is_err());
 // No eligible positive-support donor; old error remains.
 assert!(trial(2.0*eta,5.0*eta,1.0,vec![(1.0,eta),(2.0,eta)],true,0.0).is_err());
 // Exact count alone cannot bypass the original energy gate.
 assert!(trial(100.0*eta,6045.0*eta,1.0,vec![(100.0,60.0*eta),(1.0,45.0*eta)],true,0.0).is_err());
 assert!(rei_subnormal_pair_candidate(eta,eta,eta,&[(1.0,-eta)]).is_none());
 assert!(rei_subnormal_pair_candidate(eta,eta,eta,&[(f64::NAN,eta)]).is_none());
 assert!(rei_subnormal_pair_candidate(eta,eta,eta,&[(0.0,eta)]).is_none());
 assert!(rei_subnormal_pair_candidate(eta,eta,eta,&[(1.0,f64::MIN_POSITIVE)]).is_none());
 // Every stored zero remains zero; one-tick donors are never removed.
 let no_pair=vec![(1.0,eta),(2.0,0.0)];
 assert!(rei_subnormal_pair_candidate(eta,2.0*eta,2.0*eta,&no_pair).is_none());
 println!("captured_count_energy_ticks=4 later_pair_energy_ticks=1 donor=24 receiver=0 controls=PASS");
}
'''.replace('FIRST', rust_nodes(first)).replace('LATER', rust_nodes(later))
        source = prefix + pair.INJECTION.decode() + middle + count.CANDIDATE_HELPER.decode() + pair.PAIR_HELPER.decode() + suffix
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(os.environ.get('REI_PAIR_TEST_ARTIFACT_DIR', temporary))
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / 'probe.rs'
            path.write_text(source)  # Preserve actual source before compilation.
            rustc = shutil.which('rustc')
            self.assertIsNotNone(rustc, 'Rust required for the compiled fixed-cell regression')
            build = subprocess.run([rustc, '--edition=2021', '-O', str(path), '-o', str(directory/'probe')], capture_output=True, text=True)
            (directory/'build.stdout').write_text(build.stdout)
            (directory/'build.stderr').write_text(build.stderr)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(directory/'probe')], capture_output=True, text=True)
            (directory/'run.stdout').write_text(run.stdout)
            (directory/'run.stderr').write_text(run.stderr)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn('controls=PASS', run.stdout)
            reports = [json.loads(line.split(' ', 1)[1]) for line in run.stderr.splitlines()
                       if line.startswith('REI_SUBNORMAL_PAIR_CORRECTION ')]
            self.assertEqual([r['mode'] for r in reports], ['count-only', 'pair'])
            self.assertEqual(reports[0]['actual_l1_ticks'], '5')
            self.assertEqual(reports[1]['actual_l1_ticks'], '2')
            self.assertEqual(reports[1]['pair']['donor'], 24)
            self.assertEqual(reports[1]['pair']['receiver'], 0)


if __name__ == '__main__':
    unittest.main()
