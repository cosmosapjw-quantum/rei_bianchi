"""Independent proper-cell validation. Set MATERIAL_EXCHANGE and REI_LIVE_NATIVE to exercise compiled entry points."""
import csv
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO

from scipy.integrate import solve_ivp
from rei_bianchi.microphysics import cli, cr, experiment, hh

ROOT = Path(__file__).resolve().parents[3]
FROZEN = ROOT / 'components' / 'bass_rec'


def radau(rhs, initial, duration):
    solution = solve_ivp(rhs, (0., duration), [initial], method='Radau',
                         rtol=2e-12, atol=2e-15)
    assert solution.success, solution.message
    return solution.y[0, -1]


class FiniteExchangeTests(unittest.TestCase):
    def test_riccati_against_implicit_evolution(self):
        # Direct mass-action integrand. Independent from the analytic quadratic solution.
        for temp, x, y, eta, exposure in [
                (2.7, .999, .9, .01, 125.), (413., .17, .68, .007, .03),
                (7133., .68, .19, 2.5e-5, 2.4), (2e5, .0, .8, .01, 170.)]:
            with self.subTest(temp=temp, eta=eta):
                kf, kr = hh.savin_rates(temp)
                nh = .031
                duration = exposure / (nh * max(kf, kr))
                def rhs(_, value):
                    y_now = value[0]
                    x_now = x + eta * (y - y_now)
                    return [nh * (kf*x_now*(1-y_now) - kr*(1-x_now)*y_now)]
                y_numeric = radau(rhs, y, duration)
                extent = experiment.closed_cx_extent(nh,x,eta,y,temp,duration)
                y_native = y + extent/(1e6*nh*eta)
                self.assertAlmostEqual(y_native,y_numeric,delta=1.3e-12)
                self.assertTrue(0 <= y_native <= 1)
                self.assertTrue(0 <= x + eta*(y - y_native) <= 1)

    def test_absent_reactants_remain_exact_and_neighbor_has_reverse_sign(self):
        for x,y in [(0.,0.),(1.,1.)]:
            self.assertEqual(experiment.closed_cx_extent(.031,x,.01,y,2.7,1e12),0.)
        self.assertLess(experiment.closed_cx_extent(.031,math.nextafter(1.,0.),.01,1.,2.7,1e12),0.)

    def test_invalid_input(self):
        for args in [(0.,.5,.01,.5,100,10),(.03,1.001,.01,.5,100,10),
                     (.03,.5,-.01,.5,100,10),(.03,.5,.01,.5,2.5,10),
                     (.03,.5,.01,-1,100,10),(.03,.5,.01,.5,100,math.nan)]:
            with self.subTest(args=args), self.assertRaises(ValueError):
                experiment.closed_cx_extent(*args)
        for kwargs in [dict(case='unknown'),dict(y_d_initial=math.nan),
                       dict(eta_d=-.001),dict(duration_s=0)]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                experiment.late_cell('unneeded',**kwargs)
        with redirect_stderr(StringIO()), self.assertRaises(SystemExit) as cm:
            cli.main(['cell','--case','bad','--native','unneeded'])
        self.assertEqual(cm.exception.code,2)

    def test_invalid_native_history(self):
        with tempfile.TemporaryDirectory() as folder:
            src = FROZEN/'validation'/'uv_exchange.tsv'
            with src.open() as stream:
                rows=list(csv.DictReader(stream,delimiter='\t'))
            rows[-1]['binding_U']='nan'
            altered=Path(folder)/'uv.tsv'
            with altered.open('w') as stream:
                writer=csv.DictWriter(stream,delimiter='\t',fieldnames=rows[0].keys());writer.writeheader();writer.writerows(rows)
            with self.assertRaisesRegex(ValueError,'Nonfinite'):
                experiment.consume_live(FROZEN/'validation'/'rei_history.tsv',altered)

    @unittest.skipUnless(os.getenv('MATERIAL_EXCHANGE'), 'provide built REI material_exchange')
    def test_named_cell_source_on_off_and_small_transfer(self):
        binary=os.environ['MATERIAL_EXCHANGE'];case='SHEAR_HALF_MINUS'
        off=experiment.late_cell(binary,case,enabled=False)
        run=subprocess.run([sys.executable,'-m','rei_bianchi.microphysics.cli','cell',
                            '--case',case,'--native',binary],check=True,capture_output=True,text=True)
        on=json.loads(run.stdout); expected=cr.snapshot_primary_ionization(case)
        self.assertEqual(on['case'],case)
        self.assertEqual(off['native']['electron_fast_m3'],0.)
        self.assertEqual(off['CR_window_projectile_debit_eV_m3'],0.)
        self.assertEqual(off['signed_CX_extent_m3'],on['signed_CX_extent_m3'])
        births=expected['window_primary_ions_m3_by_target']; small=on['CR_window_projectile_debit_eV_m3']
        self.assertGreater(small,0.)
        self.assertLess(small,math.ulp(on['native']['initial_ev_m3']))
        self.assertTrue(math.isclose(on['native']['electron_fast_m3'],math.fsum(births.values()),rel_tol=6e-15))
        # Use binding from counts+thresholds, separately exported native births and calibration stock.
        binding = math.fsum(births[s]*cr.OWNER_THRESHOLD_EV[s] for s in births)
        recovered = math.fsum([binding,on['native']['born_kinetic_ev_m3'],on['native']['threshold_offset_ev_m3']])
        self.assertTrue(math.isclose(recovered,small,rel_tol=3e-15))
        self.assertLess(abs(on['CR_transfer_partition_residual_eV_m3']),4e-15*small)
        # The local projectile stock has enough significant digits to resolve its subtracted debit.
        active=on['active_band_initial_reference_eV_m3']; observed=active-on['native']['projectile_remaining_ev_m3']
        self.assertAlmostEqual(observed,small,delta=2*math.ulp(active))

    @unittest.skipUnless(os.getenv('REI_LIVE_NATIVE'), 'provide built REI live characteristics example')
    def test_rust_trace_against_stiff_ode_on_native_steps(self):
        initial=json.loads((FROZEN/'fixtures'/'REC_HMLA_Z20.json').read_text())['initial']
        with tempfile.TemporaryDirectory() as folder:
            out=Path(folder)/'live'
            subprocess.run([os.environ['REI_LIVE_NATIVE'],str(out),'19.999','4','0.005','4','8',
                            str(initial['x_HII']),str(initial['T_m_K']),'--material-trace'],
                           check=True,text=True,capture_output=True)
            with (out/'material_trace.tsv').open() as stream: rows=list(csv.DictReader(stream,delimiter='\t'))
        self.assertEqual(len(rows),4);y=initial['x_HII']
        for row in rows:
            r={k:float(v) for k,v in row.items()};kf,kr=hh.savin_rates(r['mean_T_K']);x=r['mean_x_HII'];n=r['mean_nH_cm3']
            y=radau(lambda _,v:[n*(kf*x*(1-v[0])-kr*(1-x)*v[0])],y,r['dt_s'])
            self.assertAlmostEqual(y,r['y_DII'],delta=1.0e-13)


if __name__=='__main__': unittest.main()
