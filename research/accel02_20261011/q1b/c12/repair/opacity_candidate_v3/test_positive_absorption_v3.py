"""New attempt67 and new log-coordinate policy cases only."""
from pathlib import Path
import json,math,unittest
import numpy as np
import positive_absorption_v3 as candidate
from opacity_native import NativeOpacity,THRESHOLDS_EV
from reconstruction import CellSpectrum,_log_mean_power,QuadratureNotConverged
HERE=Path(__file__).resolve().parent


def cell_for_p(p,a=54.42,b=58.10903285705145,R=.9980826907410681):
    N=1e-12;mean=math.exp(_log_mean_power(p,1.,a,b));U=R*N*mean
    return CellSpectrum(N,U,R,a,b,mean,p,'INTERIOR','INTERIOR')

class LogPanelTests(unittest.TestCase):
    def tearDown(self):candidate.pop_refinement_records()

    def test_exact_attempt67_candidate_and_saved_gas_attenuation(self):
        entry=json.loads((HERE/'evidence/EXTRACT67/RESULT.json').read_text());g=entry['geometry'];gas=entry['gas']
        lower=np.array([g['nH']*(1-gas[0]),g['nHe']*(1-gas[1]-gas[2]),g['nHe']*gas[1]])
        with NativeOpacity() as opacity:
            prepared=candidate.prepare_incident(**entry['parameters'],opacity=opacity,orders=(64,128),rtol=1e-7)
            self.assertEqual(prepared.rtol,1e-7);self.assertEqual(prepared.diagnostics['coordinate'],'LOG_Q_COMPOSITE_POSITIVE')
            self.assertLessEqual(prepared.diagnostics['order_pair_max_error'],1e-7)
            self.assertTrue(np.all(prepared.P>0));self.assertEqual(prepared.N,entry['parameters']['N']);self.assertEqual(prepared.U,entry['parameters']['U'])
            result=candidate.absorb(prepared,lower,entry['h_s'])
            self.assertLessEqual(result['diagnostics']['order_pair_max_error'],1e-7)
            records=candidate.pop_refinement_records();self.assertEqual(len(records),1);self.assertEqual(records[0]['status'],'REFINED_LOGQ_SAME_TOLERANCE')
            report=dict(case=entry['parameters'],incident_diagnostics=prepared.diagnostics,attenuation_diagnostics=result['diagnostics'],refinement_records=records,native_sigma_calls=opacity.native_calls,sigma_energy_evaluations=opacity.energy_evaluations,native_gas_calls=0,whole_maps=0)
        out=HERE/'evidence/CANDIDATE67';out.mkdir(exist_ok=False)
        (out/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
        np.savez_compressed(out/'PREPARED.npz',q=prepared.q,P=prepared.P,sigma=prepared.sigma,coarse_q=prepared.coarse.q,coarse_P=prepared.coarse.P,coarse_sigma=prepared.coarse.sigma)

    def test_panel_tiling_thresholds_signs_and_prospective_cap(self):
        for p in (0.,140.73475623873867,-140.73475623873867,400.,-400.):
            cell=cell_for_p(p);splits=[float(E/cell.R) for E in THRESHOLDS_EV if cell.a<E/cell.R<cell.b]
            panels,diag=candidate.log_panels(cell,splits)
            self.assertEqual(panels[0][0],0.);self.assertEqual(panels[-1][1],math.log1p((cell.b-cell.a)/cell.a))
            self.assertTrue(all(left<right for left,right in panels))
            self.assertTrue(all(panels[j][1]==panels[j+1][0] for j in range(len(panels)-1)))
            self.assertLessEqual(max(abs(p)*(b-a) for a,b in panels),candidate.MAX_EXPONENT_SPAN)
            self.assertEqual(diag['max_panels'],128)
            for q in splits:self.assertIn(math.log1p((q-cell.a)/cell.a),[x for pair in panels for x in pair])
        with self.assertRaisesRegex(QuadratureNotConverged,'LOGQ_PANEL_CAP'):
            candidate.log_panels(cell_for_p(1e5),[])

    def test_positive_measure_original_moment_fit_both_signs(self):
        # No native SIGMA: manufacture zero kernels to isolate new positive measure.
        for p in (-400.,0.,400.):
            cell=cell_for_p(p);splits=[54.42/cell.R]
            measure=candidate.measure_logq(cell,lambda energy:np.zeros((len(energy),3)),64,splits)
            self.assertTrue(np.all(measure.P>0));self.assertTrue(np.all(measure.q>cell.a));self.assertTrue(np.all(measure.q<cell.b))
            self.assertLessEqual(abs(math.fsum(measure.P)/cell.N-1),1e-12)
            self.assertLessEqual(abs(cell.R*math.fsum(measure.q*measure.P)/cell.U-1),1e-12)
            self.assertLessEqual(abs(measure.diagnostics['mean_fit_cell_relative_residual']),1e-12)

if __name__=='__main__':unittest.main(verbosity=2)
