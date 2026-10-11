"""Changed native-only coordinate gate; exact failed PILOT01 cell only."""
from pathlib import Path
import json,sys,unittest
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE));sys.path.insert(0,str(HERE.parent.parent))
from native_coordinate_absorption import prepare_incident,absorb
from opacity_native import NativeOpacity
from reconstruction import QuadratureNotConverged,TraceRequired

class CoordinateGateTests(unittest.TestCase):
    def test_saved_failed_born_cell_new_gate_and_stiff_absorption(self):
        d=json.loads((HERE.parent/'precision/evidence/PILOT01_FAILED_MEAN/RESULT.json').read_text())
        with NativeOpacity() as op:
            pre=prepare_incident(d['N'],d['U_eV'],d['R'],*d['support_q_eV'],op,support_cap_ev=50000.)
            c=pre.diagnostics['native_coordinate_certificate']
            self.assertGreater(c['old_generic_indicator'],1e-7)
            self.assertLess(c['combined_coordinate_bound'],1e-7/16)
            self.assertEqual(c['support_cap_provenance'],'DECLARED_50000_EV_CAP_QUOTIENT_METADATA')
            self.assertLessEqual(c['exact_node_energy_max_eV'],50000.)
            for lower,h in [(np.array([1e-3,8e-5,0.]),977363400.0610615),
                            (np.array([1e3,80.,80.]),1e20)]:
                out=absorb(pre,lower,h)
                self.assertGreater(out['N'],0.)
                self.assertLessEqual(out['diagnostics']['order_pair_max_error']+c['combined_coordinate_bound'],1e-7)
                self.assertTrue(np.all(out['photoheat_direct']>=0.))
            payload={'new_scope':'saved failed cell changed native-only coordinate gate',
                     'certificate':c,'incident':pre.diagnostics,
                     'native_calls':op.native_calls,'native_energy_evaluations':op.energy_evaluations,
                     'gas_rhs_calls':0,'old_completed_replays':0}
            target=HERE/'evidence/COORDINATE_CHANGED_CELL.json'
            target.write_text(json.dumps(payload,indent=2)+'\n')

    def test_cap_equality_without_caller_provenance_is_rejected(self):
        d=json.loads((HERE.parent/'precision/evidence/PILOT01_FAILED_MEAN/RESULT.json').read_text())
        with NativeOpacity() as op:
            with self.assertRaisesRegex(TraceRequired,'EXPLICIT_CALLER_SOURCE_CAP_PROVENANCE_REQUIRED'):
                prepare_incident(d['N'],d['U_eV'],d['R'],*d['support_q_eV'],op)
            self.assertEqual(op.native_calls,0)

    def test_arbitrary_kernel_retains_original_guard(self):
        d=json.loads((HERE.parent/'precision/evidence/PILOT01_FAILED_MEAN/RESULT.json').read_text())
        with self.assertRaisesRegex(QuadratureNotConverged,'FLOAT_Q_COORDINATE_UNRESOLVED'):
            prepare_incident(d['N'],d['U_eV'],d['R'],*d['support_q_eV'],lambda e:np.ones((len(e),3)))

    def test_thin_threshold_crossing_stays_closed(self):
        a=13.60-1e-9;b=13.60+1e-9
        with NativeOpacity() as op:
            with self.assertRaisesRegex(TraceRequired,'SAME_BRANCH_SUPPORT_REQUIRED'):
                prepare_incident(1.,13.60,1.,a,b,op)
            self.assertEqual(op.native_calls,0)

if __name__=='__main__':unittest.main(verbosity=2)
