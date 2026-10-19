import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

import numpy as np

from build_refined_sources import overlay
from reference_diagnostics import COMPUTATIONAL_BASE_SHA, transform_solver
from source_jump_diagnosis import diagnose_jumps


ROOT=Path(__file__).resolve().parents[1]


class ReferenceDiagnosticsTests(unittest.TestCase):
    def test_passive_generated_reference_and_retry_rollback(self):
        _,source=overlay((ROOT/'donors/pr171/positive_native.rs').read_bytes(),
                         (ROOT/'donors/pr171/positive_solver.py').read_bytes())
        self.assertEqual(hashlib.sha256(source.encode()).hexdigest(),COMPUTATIONAL_BASE_SHA)
        with self.assertRaises(ValueError):
            transform_solver(source.encode()+b'\n')
        with tempfile.TemporaryDirectory() as directory:
            directory=Path(directory)
            server=directory/'fixture'
            shutil.copyfile(ROOT/'tests/fixtures/reference_rpc_fixture.py',server)
            server.chmod(0o755)
            results={}
            for mode,data in [('off',source.encode()),('on',transform_solver(source.encode()))]:
                script=directory/(mode+'.py');script.write_bytes(data)
                out=directory/mode;log=directory/(mode+'_rhs.txt')
                result=subprocess.run([sys.executable,str(script),str(server),str(out),
                                       '--birth-panels','2','--transport-cells','1',
                                       '--error-norm','block-max','--max-wall-s','20'],
                                      env=dict(os.environ,REI_FIXTURE_RHS_LOG=str(log),
                                               OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'),
                                      capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stderr)
                results[mode]=(out,log)
            left,right=results['off'][0],results['on'][0]
            self.assertEqual(results['off'][1].read_bytes(),results['on'][1].read_bytes())
            for name in ('endpoint.json','observations.json','ledgers.json','provider_errors.json'):
                self.assertEqual((left/name).read_bytes(),(right/name).read_bytes(),name)
            for path in left.glob('accepted_coordinates_event*.npy'):
                self.assertEqual(path.read_bytes(),(right/path.name).read_bytes())
            a=json.loads((left/'solver_return.json').read_text());b=json.loads((right/'solver_return.json').read_text())
            for key in ('calls','errors','intervals','status'):
                self.assertEqual(a[key],b[key],key)
            trace=json.loads((right/'reference_diagnostics.json').read_text())
            self.assertTrue(any(not estimate['error_accept'] for attempt in trace['attempts'] for estimate in attempt['estimates']))
            discarded=[attempt for attempt in trace['attempts'] if attempt['discarded']]
            self.assertEqual(len(discarded),1)
            self.assertGreater(discarded[0]['local_error_accepted_estimates'],0)
            self.assertEqual(discarded[0]['final_trajectory_accepted_estimates'],0)
            self.assertEqual(sum(attempt['final_trajectory_accepted_estimates'] for attempt in trace['attempts']),
                             sum(record['solver_steps'] for record in b['intervals']))
            for attempt in trace['attempts']:
                for estimate in attempt['estimates']:
                    self.assertEqual(estimate['block_max_diagnostic'],estimate['error_norm_actual'])
            setup=json.loads((right/'setup.json').read_text())
            jumps=json.loads((right/'source_jumps.json').read_text())
            report=diagnose_jumps(setup,jumps)
            self.assertEqual(report['coverage'],'COMPLETE')
            self.assertEqual(report['available_unique_births'],2)
            self.assertTrue(all(record['unchanged_nonbirth_coordinates_bits'] for record in report['records']))
            self.assertTrue(all(record['unchanged_gas_coordinate_bits'] and record['unchanged_ledger_coordinate_bits'] for record in report['records']))

    def test_source_jump_missing_duplicate_and_exact_subnormal(self):
        eta=float.fromhex('0x0.0000000000001p-1022')
        setup=dict(births=[1.,2.],source_inventory=[[eta,0.],[1.,0.]])
        pre=dict(N=0.,U=0.,gas=[0.]*4,ledgers=[0.]*14)
        post=dict(pre,N=eta)
        record=dict(status='AVAILABLE',event=0,x=1.,active_before=0,active_after=1,
                    source_inventory=[eta,0.],pre=pre,post=post)
        report=diagnose_jumps(setup,dict(records=[record]))
        self.assertEqual(report['missing_events'],[1])
        self.assertEqual(report['records'][0]['delta_photon_invariant']['numerator'],'0')
        report=diagnose_jumps(setup,dict(records=[record,record]))
        self.assertEqual(report['duplicate_events'],[dict(event=0,count=2)])
        self.assertEqual(report['available_unique_births'],0)


if __name__ == '__main__':
    unittest.main()
