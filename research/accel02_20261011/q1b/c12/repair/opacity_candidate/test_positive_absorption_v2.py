"""New failure66 scope only. Actual opacity cell; no gas RHS/full maps."""
from pathlib import Path
import json,math,unittest
from unittest.mock import patch
import numpy as np
import positive_absorption_v2 as candidate
from opacity_native import NativeOpacity

HERE=Path(__file__).resolve().parent

class RefinementTests(unittest.TestCase):
    def tearDown(self):candidate.pop_refinement_records()

    def test_exact_failed_cell_and_saved_gas_attenuation(self):
        entry=json.loads((HERE/'evidence/EXTRACT66/RESULT.json').read_text())
        q=entry['parameters'];g=entry['geometry'];gas=entry['gas']
        lower=np.array([g['nH']*(1-gas[0]),g['nHe']*(1-gas[1]-gas[2]),g['nHe']*gas[1]])
        with NativeOpacity() as opacity:
            prepared=candidate.prepare_incident(**q,opacity=opacity,orders=(64,128),rtol=1e-7)
            self.assertEqual(prepared.diagnostics['orders'],[128,256])
            self.assertEqual(prepared.rtol,1e-7)
            self.assertLess(prepared.diagnostics['order_pair_max_error'],1e-7)
            result=candidate.absorb(prepared,lower,entry['h_s'])
            self.assertLess(result['diagnostics']['order_pair_max_error'],1e-7)
            self.assertTrue(np.all(prepared.P>0));self.assertTrue(np.all(result['K0']>=0))
            record=candidate.pop_refinement_records();self.assertEqual(len(record),1)
            self.assertEqual(record[0]['status'],'REFINED_SAME_TOLERANCE')
            self.assertIn('INCIDENT_ORDER_PAIR:',record[0]['original_failure']['message'])
            result_out=dict(parameters=q,requested_orders=[64,128],effective_orders=prepared.diagnostics['orders'],rtol=prepared.rtol,incident_diagnostics=prepared.diagnostics,attenuation_diagnostics=result['diagnostics'],refinement_receipts=record,native_sigma_calls=opacity.native_calls,sigma_energy_evaluations=opacity.energy_evaluations,native_gas_calls=0,whole_maps=0)
        dest=HERE/'evidence/CANDIDATE66';dest.mkdir(exist_ok=False)
        (dest/'RESULT.json').write_text(json.dumps(result_out,indent=2)+'\n')
        np.savez_compressed(dest/'PREPARED.npz',q=prepared.q,P=prepared.P,sigma=prepared.sigma,coarse_q=prepared.coarse.q,coarse_P=prepared.coarse.P,coarse_sigma=prepared.coarse.sigma)

    def test_unrelated_failure_and_non_native_refusal_are_not_retried(self):
        for opacity,message in ((object(),'INCIDENT_ORDER_PAIR: manufactured'),(NativeOpacity.__new__(NativeOpacity),'MOMENT_TARGET_OUTSIDE_STRICT_NODE_CONVEX_HULL')):
            failure=candidate.QuadratureNotConverged(message)
            with patch.object(candidate._base,'prepare_incident',side_effect=failure) as function:
                with self.assertRaises(candidate.QuadratureNotConverged) as caught:
                    candidate.prepare_incident(1.,2.,1.,1.,3.,opacity)
                self.assertIs(caught.exception,failure);self.assertEqual(function.call_count,1)
                self.assertEqual(candidate.pop_refinement_records(),[])

    def test_higher_order_refusal_is_recorded_and_never_retried_again(self):
        first=candidate.QuadratureNotConverged('INCIDENT_ORDER_PAIR: first')
        final=candidate.QuadratureNotConverged('INCIDENT_ORDER_PAIR: refined')
        with patch.object(candidate._base,'prepare_incident',side_effect=[first,final]) as function:
            with self.assertRaises(candidate.QuadratureNotConverged) as caught:
                candidate.prepare_incident(1.,2.,1.,1.,3.,NativeOpacity.__new__(NativeOpacity))
            self.assertIs(caught.exception,final);self.assertEqual(function.call_count,2)
        record=candidate.pop_refinement_records()
        self.assertEqual(len(record),1);self.assertEqual(record[0]['status'],'REFINEMENT_FAILED_CLOSED')
        self.assertEqual(record[0]['effective_orders'],[128,256])
        self.assertFalse(record[0]['tolerance_changed'])

if __name__=='__main__':unittest.main(verbosity=2)
