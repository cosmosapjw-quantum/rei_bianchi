"""Exact Fraction oracle versus the compiled production pair-search bytes.

Captured-cell and arithmetic regressions only; no whole native campaign.
"""
from fractions import Fraction
from pathlib import Path
from unittest.mock import patch
import hashlib
import heapq
import json
import math
import os
import shutil
import struct
import subprocess
import tempfile
import unittest

import prepare_native
import subnormal_pair_search as search
from test_subnormal_moment_rounding import rust_nodes

ROOT = Path(__file__).resolve().parents[1]


def ticks(value):
    return 0 if value == 0 else struct.unpack('>Q', struct.pack('>d', value))[0]


def fraction_oracle(cell):
    rows = cell['nodes_q_probability_number']
    q = [Fraction(row[0]) for row in rows]
    old = [ticks(row[2]) for row in rows]
    target, energy_target, tau = [ticks(cell[k]) for k in ('n', 'u', 'energy_tolerance')]
    base = old.copy()
    index = max(range(len(base)), key=base.__getitem__)
    base[index] += target - sum(base)
    terms = [round(a*t) for a, t in zip(q, base)]
    energy = sum(terms)
    assert max(q)*target + Fraction(len(q), 2) < 2**52
    heap = []
    intervals = 0
    for donor, ta in enumerate(base):
        if ta < 2:
            continue
        for receiver, tb in enumerate(base):
            if donor == receiver or tb < 1:
                continue
            constant = Fraction(energy-terms[donor]-terms[receiver]-energy_target) + q[donor]*ta + q[receiver]*tb
            slope = q[receiver]-q[donor]
            upper = min(ta-1, 2**52-1-tb)
            if slope:
                ends = sorted(((-tau-1-constant)/slope, (tau+1-constant)/slope))
                low, high = max(1, math.ceil(ends[0])), min(upper, math.floor(ends[1]))
            elif abs(constant) <= tau+1:
                low, high = 1, upper
            else:
                continue
            if low <= high:
                intervals += 1
                heapq.heappush(heap, (low, donor, receiver, high))
    evaluations = 0
    while heap:
        k, donor, receiver, high = heapq.heappop(heap)
        evaluations += 1
        updated_energy = energy-terms[donor]-terms[receiver] + round(q[donor]*(base[donor]-k)) + round(q[receiver]*(base[receiver]+k))
        if abs(updated_energy-energy_target) <= tau:
            corrected = base.copy()
            corrected[donor] -= k
            corrected[receiver] += k
            return dict(k=k, donor=donor, receiver=receiver, evaluations=evaluations,
                        intervals=intervals, count_distance=abs(target-sum(old)),
                        actual_l1=sum(abs(a-b) for a, b in zip(old, corrected)),
                        energy_defect=abs(updated_energy-energy_target))
        if k < high:
            heapq.heappush(heap, (k+1, donor, receiver, high))
    raise AssertionError('Captured constructive fixture unexpectedly lacks a candidate')


class SubnormalPairSearchTests(unittest.TestCase):
    def test_source_identity_and_preparation_mode(self):
        original = b'// Mock identity structure.\n' + search.ANCHOR
        blob = hashlib.sha1(b'blob '+str(len(original)).encode()+b'\0'+original).hexdigest()
        with patch.object(search, 'ORIGINAL_BLOB', blob):
            self.assertEqual(search.instrument_pair_search(original).replace(search.INJECTION, b'', 1), original)
            with self.assertRaisesRegex(ValueError, 'ORIGINAL_IDENTITY'):
                search.instrument_pair_search(original+b'\n')
        self.assertEqual(search.search_rounding_identity(), hashlib.sha256(search.INJECTION).hexdigest())
        self.assertIn(b'REI_PAIR_SEARCH_MAX_EVALUATIONS: usize = 65536', search.INJECTION)
        with tempfile.TemporaryDirectory() as directory:
            dest = Path(directory)
            (dest/'PREPARED_IDENTITY.json').write_text(json.dumps(dict(native_sha='mock', outputs={},
                moment_rounding='subnormal-pair-search', moment_rounding_injection_sha256='wrong')))
            with patch.object(prepare_native, 'load_manifest', return_value=dict(native_sha='mock')):
                with self.assertRaisesRegex(ValueError, 'ROUNDING_VERSION_CONFLICT'):
                    prepare_native.prepare(ROOT, dest, moment_rounding='subnormal-pair-search')

    def test_fraction_oracle_actual_n2_n3(self):
        n2 = json.loads((ROOT/'tests/fixtures/subnormal_pair_captured_cell.json').read_text())['cell']
        n3 = json.loads((ROOT/'tests/fixtures/subnormal_pair_search_captured_cell.json').read_text())['cell']
        a, b = fraction_oracle(n2), fraction_oracle(n3)
        self.assertEqual((a['k'], a['donor'], a['receiver'], a['evaluations']), (1, 24, 0, 625))
        self.assertEqual((b['k'], b['donor'], b['receiver'], b['evaluations'], b['intervals']), (3, 0, 14, 164, 2348))
        self.assertEqual((b['count_distance'], b['actual_l1'], b['energy_defect']), (1, 7, 0))

    def test_compiled_rust_matches_fraction_and_boundary_controls(self):
        cells = [json.loads((ROOT/'tests/fixtures'/name).read_text())['cell'] for name in
                 ('subnormal_pair_captured_cell.json', 'subnormal_pair_search_captured_cell.json')]
        expected = [fraction_oracle(cell) for cell in cells]
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
fn main() {
 let eta=f64::from_bits(1);
'''
        cases = []
        for index, (cell, oracle) in enumerate(zip(cells, expected)):
            n, u = ticks(cell['n']), ticks(cell['u'])
            cases.append(f'''
 let nodes{index}=vec![{rust_nodes(cell)}];
 let n=f64::from_bits({n});let u=f64::from_bits({u});
 let width={cell['hi']-cell['lo']:.17e}f64;
 assert!(trial(n,u,width,nodes{index}.clone(),false,0.0).is_err());
 let fixed=trial(n,u,width,nodes{index}.clone(),true,{cell['normalized_mean_residual']:.17e}f64).unwrap();
 let found=match rei_subnormal_pair_search(n,u,u,&nodes{index},65536).unwrap() {{
  ReiSubnormalSearchOutcome::Found(value)=>value,_=>panic!("captured candidate missing") }};
 assert_eq!(found.k,{oracle['k']});assert_eq!(found.repair.pair,Some(({oracle['donor']},{oracle['receiver']})));
 assert_eq!(found.evaluations,{oracle['evaluations']});assert_eq!(found.intervals,{oracle['intervals']});
 assert_eq!(found.repair.count_distance,{oracle['count_distance']});assert_eq!(found.repair.l1_ticks,{oracle['actual_l1']});
 assert_eq!((sum(fixed.iter().map(|x|x.1))-n).abs().to_bits(),0);
 assert_eq!((sum(fixed.iter().map(|x|x.0*x.1))-u).abs().to_bits(),{oracle['energy_defect']});
 for (a,b) in nodes{index}.iter().zip(&fixed) {{assert_eq!(a.0.to_bits(),b.0.to_bits());assert_eq!(a.1>0.0,b.1>0.0);}}
 println!("fixture={index} k={{}} donor={oracle['donor']} receiver={oracle['receiver']} evaluations={{}} intervals={{}} L1={{}}",found.k,found.evaluations,found.intervals,found.repair.l1_ticks);
''')
        intervals = []
        for b0 in range(-4, 5):
            for b1 in range(-3, 4):
                for radius in range(3):
                    candidates = [k for k in range(1, 6) if abs(b0+k*b1) <= radius]
                    answer = f'Some(({min(candidates)},{max(candidates)}))' if candidates else 'None'
                    intervals.append(f'assert_eq!(rei_signed_interval({b0},{b1},{radius},5).unwrap(),{answer});')
        suffix = r'''
 // Budget exhaustion is a distinct outcome, never NoSolution.
 let n=f64::from_bits(313989944336);let u=f64::from_bits(5352011796590);
 match rei_subnormal_pair_search(n,u,u,&nodes1,1).unwrap() {
  ReiSubnormalSearchOutcome::Budget{next_k,evaluations,intervals}=>{assert!(next_k>=1);assert_eq!(evaluations,1);assert_eq!(intervals,2348);},
  _=>panic!("budget must not imply infeasibility")
 }
 assert_eq!(rei_checked_positive_shift(1,126).unwrap(),1_i128<<126);
 assert!(rei_checked_positive_shift(3,126).is_err());
 assert!(rei_checked_positive_shift(1,127).is_err());
 assert!(rei_signed_interval(i128::MIN,1,1,5).is_err());
 assert!(rei_round_dyadic_product(i128::MAX,2,1).is_err());
 assert_eq!(rei_round_dyadic_product(1,1,2).unwrap(),0);
 assert_eq!(rei_round_dyadic_product(1,3,2).unwrap(),2);
 assert_eq!(rei_round_dyadic_product(1,5,2).unwrap(),2);
 // Normal U, subnormal q, and an unrepresentable common denominator are unsupported.
 assert!(rei_subnormal_pair_search(2.0*eta,f64::MIN_POSITIVE,f64::MIN_POSITIVE,&[(1.0,2.0*eta)],10).is_err());
 assert!(rei_subnormal_pair_search(2.0*eta,eta,eta,&[(eta,2.0*eta)],10).is_err());
 assert!(rei_subnormal_pair_search(2.0*eta,eta,eta,&[(1e-200,2.0*eta)],10).is_err());
 assert!(rei_subnormal_pair_search(2.0*eta,eta,eta,&[(f64::MAX,2.0*eta)],10).is_err());
 // Equal-q intervals retain their full positivity range; no sign pruning.
 assert_eq!(rei_signed_interval(0,0,1,12).unwrap(),Some((1,12)));
 assert_eq!(rei_signed_interval(2,0,1,12).unwrap(),None);
 assert_eq!(rei_signed_interval(7,-2,1,10).unwrap(),Some((3,4)));
 for (n,u,v) in [(1.0,1.0,vec![(1.0,1.0)]),(10.0*eta,10.0*eta,vec![(1.0,10.0*eta)])] {
  let got=trial(n,u,1.0,v.clone(),true,0.0).unwrap();
  assert!(v.iter().zip(&got).all(|(a,b)|a.0.to_bits()==b.0.to_bits()&&a.1.to_bits()==b.1.to_bits()));
 }
 assert!(trial(1.0,1.0,1.0,vec![(1.0,1.1)],true,0.0).is_err());
 assert!(trial(n,u,3.4612670487769624,nodes1,true,1e-8).is_err());
 match rei_subnormal_pair_search(2.0*eta,5.0*eta,5.0*eta,&[(1.0,eta),(2.0,eta)],65536).unwrap() {
  ReiSubnormalSearchOutcome::NoSolution{evaluations,intervals}=>{assert_eq!(evaluations,0);assert_eq!(intervals,0);},
  _=>panic!("no eligible donor")
 }
 println!("signed_intervals=189 controls=PASS");
}
'''
        source = prefix+search.INJECTION.decode()+middle+search.CANDIDATE_HELPER.decode()+search.PAIR_HELPER.decode()+search.SEARCH_HELPER.decode()+''.join(cases)+''.join(intervals)+suffix
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(os.environ.get('REI_PAIR_SEARCH_TEST_ARTIFACT_DIR', temporary))
            directory.mkdir(parents=True, exist_ok=True)
            path = directory/'probe.rs'
            path.write_text(source)
            (directory/'fraction_expected.json').write_text(json.dumps(expected, indent=2)+'\n')
            rustc = shutil.which('rustc')
            self.assertIsNotNone(rustc, 'Rust required for exact search regression')
            build = subprocess.run([rustc, '--edition=2021', '-O', str(path), '-o', str(directory/'probe')], capture_output=True, text=True)
            (directory/'build.stdout').write_text(build.stdout)
            (directory/'build.stderr').write_text(build.stderr)
            self.assertEqual(build.returncode, 0, build.stderr)
            run = subprocess.run([str(directory/'probe')], capture_output=True, text=True)
            (directory/'run.stdout').write_text(run.stdout)
            (directory/'run.stderr').write_text(run.stderr)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertIn('controls=PASS', run.stdout)


if __name__ == '__main__':
    unittest.main()
