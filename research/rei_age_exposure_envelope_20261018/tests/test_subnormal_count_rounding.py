import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest import mock

import prepare_native
import subnormal_count_rounding as rounding


ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/'intake/native_original_35d9747/rust/rei_microphysics/src/axbi_covariant_transport.rs'


class SubnormalCountTests(unittest.TestCase):
    @unittest.skipUnless(ORIGINAL.is_file(),'exact source intake unavailable')
    def test_only_failed_branch_is_instrumented(self):
        original=ORIGINAL.read_bytes()
        changed=rounding.instrument_rounding(original)
        self.assertEqual(changed.replace(rounding.INJECTION,b'',1),original)
        with self.assertRaises(ValueError):
            rounding.instrument_rounding(original+b'\n')

    def test_rounding_mode_conflict_rejects_reuse(self):
        with tempfile.TemporaryDirectory() as directory:
            destination=Path(directory)
            (destination/'PREPARED_IDENTITY.json').write_text(json.dumps(dict(native_sha='frozen',outputs={})))
            with mock.patch.object(prepare_native,'load_manifest',return_value=dict(native_sha='frozen')):
                with self.assertRaisesRegex(ValueError,'ROUNDING_MODE_CONFLICT'):
                    prepare_native.prepare(ROOT,destination,moment_rounding='subnormal-count')

    @unittest.skipUnless(shutil.which('rustc'),'rustc unavailable')
    def test_captured_case_and_fail_closed_controls_compiled(self):
        cell=json.loads((ROOT/'tests/fixtures/subnormal_count_captured_cell.json').read_text())
        nodes=','.join(f'({q:.17e}f64,{number:.17e}f64)' for q,probability,number in cell['nodes_q_probability_number'])
        # The same original compensated sum and failure gates are used in this
        # standalone probe; the injected repair bytes are not reimplemented.
        prefix=r'''
#![allow(dead_code)]
#[derive(Debug)] enum ForwardError { InvalidInput(&'static str) }
fn bad(tag:&'static str)->ForwardError { ForwardError::InvalidInput(tag) }
#[derive(Default)] struct Diagnostics { max_count_relative_defect:f64, max_energy_relative_defect:f64 }
fn sum(xs: impl Iterator<Item=f64>)->f64 {
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
        middle=r'''
  }
  return Err(bad("AXBI_COVARIANT_MOMENT_FIT"));
 }
 Ok(result)
}
fn candidate(n:f64,nodes:&[(f64,f64)])->bool {
'''
        suffix='''
 rei_subnormal_count_candidate(n,nodes).is_some()
}
fn main() {
 let eta=f64::from_bits(1);
 let n=f64::from_bits(240243477644326);let u=f64::from_bits(4094958919588752);
 let nodes=vec![NODES];
 assert!(trial(n,u,3.4612670487769624,nodes.clone(),false,0.0).is_err());
 let fixed=trial(n,u,3.4612670487769624,nodes.clone(),true,6.769278295586412e-17).unwrap();
 assert_eq!((sum(fixed.iter().map(|x|x.1))-n).abs(),0.0);
 assert_eq!((sum(fixed.iter().map(|x|x.0*x.1))-u).abs().to_bits(),4);
 assert_eq!(nodes.iter().zip(&fixed).filter(|(a,b)|a.1.to_bits()!=b.1.to_bits()).count(),1);
 assert!(trial(n,u,3.4612670487769624,nodes,true,1e-8).is_err());
 // Originally passing subnormal cell stays bit-for-bit unchanged.
 let passing=vec![(1.0,10.0*eta)];
 assert_eq!(trial(10.0*eta,10.0*eta,1.0,passing.clone(),true,0.0).unwrap(),passing);
 // Normal amplitudes cannot use this subnormal-only correction.
 assert!(trial(1.0,1.0,1.0,vec![(1.0,1.1)],true,0.0).is_err());
 assert!(!candidate(eta,&[(1.0,-eta)]));
 assert!(!candidate(eta,&[(1.0,f64::MAX)]));
 assert!(!candidate(eta,&[(1.0,f64::INFINITY)]));
 assert!(!candidate(eta,&[(1.0,f64::from_bits((1u64<<52)-1)),(1.0,f64::from_bits((1u64<<52)-1))]));
 assert!(!candidate(eta,&[(1.0,3.0*eta),(1.0,3.0*eta)]));
 assert!(!candidate(eta,&[(1.0,0.0)]));
 // A count-feasible candidate with a failed original energy gate is rejected.
 assert!(trial(100.0*eta,6045.0*eta,1.0,vec![(100.0,60.0*eta),(1.0,45.0*eta)],true,0.0).is_err());
 println!("captured_count_ticks=0 captured_energy_ticks=4 controls=PASS");
}
'''.replace('NODES',nodes)
        source=(prefix+rounding.INJECTION.decode()+middle+rounding.CANDIDATE_HELPER.decode()+suffix)
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory);path=directory/'probe.rs';path.write_text(source)
            build=subprocess.run(['rustc','--edition=2021','-O',str(path),'-o',str(directory/'probe')],capture_output=True,text=True)
            self.assertEqual(build.returncode,0,build.stderr)
            run=subprocess.run([str(directory/'probe')],capture_output=True,text=True)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertIn('controls=PASS',run.stdout)
            lines=[line for line in run.stderr.splitlines() if line.startswith('REI_SUBNORMAL_COUNT_CORRECTION ')]
            self.assertEqual(len(lines),1)
            report=json.loads(lines[0].split(' ',1)[1])
            self.assertEqual(report['l1_ticks'],'5')
            self.assertEqual(report['before_total_ticks'],'240243477644331')
            self.assertEqual(report['after_total_ticks'],'240243477644326')


if __name__ == '__main__':
    unittest.main()
