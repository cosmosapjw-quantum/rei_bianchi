"""Bounded physics and original-NCP scientific regression tests, no native REI launch."""
import base64,hashlib,json,math,tempfile,unittest
from pathlib import Path
import mpmath
from scipy.integrate import quad
from audit_pr159 import RAW,analyze,fit_q,load_raw
from birth_cohort import phi1,expected_bias,frozen_packet
from manufactured_birth import trial,reference


class SourceArchiveAudits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw,cls.receipt=load_raw()
        cls.report=analyze(cls.raw)
    def test_original_22_and_44_binary_file_hashes(self):
        self.assertEqual(len(self.raw),22)
        self.assertEqual(len(self.receipt['files']),44)
        self.assertEqual(self.receipt['original_archive_sha256'],
                         'bf8aaffdae624a6de25d6f8e58fb8c7b3c166f331954d9b841907ab1bc061e4c')
        self.assertEqual(self.receipt['nested_evidence_tar_sha256'],
                         '4b43737e74acaa8af935617294e1e04ff647e49336d555512fd3ae4707decfbb')
    def test_long_temperature_ratios_both_signed_cases(self):
        for tag,expect in [('cold',.6518532699667154),('signed',.6518567733578488)]:
            d=self.report['cases'][tag]['long']['diagnostics']['temperature_k']
            self.assertAlmostEqual(d['observed_abs_ratio'],expect,places=12)
            self.assertLess(d['effective_p_log2'],0)
    def test_source_number_quadrature_second_order_not_temperature(self):
        for tag in ('cold','signed'):
            d=self.report['cases'][tag]['long']['diagnostics']
            self.assertGreater(d['source_n_per_h']['observed_abs_ratio'],3.99)
            self.assertLess(d['source_n_per_h']['observed_abs_ratio'],4.01)
            self.assertLess(d['temperature_k']['observed_abs_ratio'],1.)
    def test_short_first_order_trend(self):
        for tag in ('cold','signed'):
            d=self.report['cases'][tag]['short']['diagnostics']['temperature_k']
            self.assertGreater(d['observed_abs_ratio'],1.90)
            self.assertLess(d['observed_abs_ratio'],2.0)
    def test_newton_long_last_near_gate(self):
        for tag in ('cold','signed'):
            nn=self.report['cases'][tag]['long']['newton_residual']
            self.assertLess(max(nn[0:2]),1e-14)
            self.assertGreater(nn[2],7e-12)
            self.assertLess(nn[2],1e-11)
    def test_quadratic_interpolant_signed_identity(self):
        y4,y8,y16=(8.699222018473609,8.699217796382154,8.699211319324126)
        q=fit_q(y4,y8,y16)
        self.assertAlmostEqual(q['observed_abs_ratio'],.6518532699667154,places=12)
        self.assertLess(q['B_h_over_A'],0.)
        self.assertAlmostEqual(q['next_32_predicted_conditional'],8.699206989292037,places=12)
    def test_raw_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            t=Path(t)
            import shutil
            if (RAW/'RAW_IDENTITY.json').exists():
                shutil.copytree(RAW,t/'raw')
                d=t/'raw/release_cold_long_g481/result.json'
                d.write_bytes(d.read_bytes()+b' ')
            else:
                d=json.loads((RAW.parent/'RAW_SNAPSHOT.json').read_text())
                key='release_cold_long_g481/result.json'
                d['base64_files'][key]=base64.b64encode(
                    base64.b64decode(d['base64_files'][key])+b' ').decode('ascii')
                (t/'RAW_SNAPSHOT.json').write_text(json.dumps(d))
                (t/'raw').mkdir()
            with self.assertRaises(AssertionError):load_raw(t/'raw')
    def test_single_snapshot_git_checkout_replay(self):
        with tempfile.TemporaryDirectory() as t:
            t=Path(t)
            import shutil
            shutil.copy2(RAW.parent/'RAW_SNAPSHOT.json',t/'RAW_SNAPSHOT.json')
            (t/'raw').mkdir()
            copy,receipt=load_raw(t/'raw')
            self.assertEqual(copy,self.raw)
            self.assertEqual(receipt['case_count'],22)

    def test_snapshot_data_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            t=Path(t)
            d=json.loads((RAW.parent/'RAW_SNAPSHOT.json').read_text())
            src='release_cold_long_g481/result.json'
            raw=bytearray(base64.b64decode(d['base64_files'][src]))
            raw[-1]=ord(' ') if raw[-1]!=ord(' ') else ord('\n')
            d['base64_files'][src]=base64.b64encode(raw).decode('ascii')
            (t/'RAW_SNAPSHOT.json').write_text(json.dumps(d))
            (t/'raw').mkdir()
            with self.assertRaises(AssertionError):load_raw(t/'raw')

    def test_checkpoint_restart_and_adaptive_provenance(self):
        for r in self.raw.values():
            self.assertEqual(r['restart_max_abs'],0.)
            self.assertEqual(r['adaptive_status'],'ACCEPTED')
            self.assertEqual(r['adaptive_accepted'],1)


class FrozenPhotonSlab(unittest.TestCase):
    def test_phi1_high_precision(self):
        mpmath.mp.dps=70
        for tau in [0.,1e-14,1e-8,1e-5,1e-3,.1,1,30,1e4]:
            ref=1. if tau==0 else float(-mpmath.expm1(-mpmath.mpf(tau))/mpmath.mpf(tau))
            self.assertLessEqual(abs(phi1(tau)-ref),6e-16*ref+1e-17)
    def test_uniform_source_direct_integral(self):
        for tau in [1e-3,.2,1,3,15]:
            value=quad(lambda u: math.exp(-tau*(1-u)),0,1,epsabs=1e-13)[0]
            self.assertAlmostEqual(phi1(tau),value,places=12)
    def test_old_underabsorption_newborn_overabsorption(self):
        for tau in [.01,.1,1,10,100]:
            old_legacy=1/(1+tau)
            old_exact=math.exp(-tau)
            born_legacy=1/(1+tau)
            born_exact=phi1(tau)
            self.assertGreater(old_legacy,old_exact)
            self.assertLess(born_legacy,born_exact)
    def test_exact_equilibrium_cancellation(self):
        for tau in [.1,1.,10.]:
            S=.04*tau;old=.04
            b=frozen_packet(old=old,source_rate=S,dt=1.,lambdas=(tau,),
                            energy_ev=60.,binding_ev=(13.6,),method='legacy_be')
            e=frozen_packet(old=old,source_rate=S,dt=1.,lambdas=(tau,),
                            energy_ev=60.,binding_ev=(13.6,),method='uniform_exact')
            self.assertAlmostEqual(b.survivor,e.survivor,places=14)
            self.assertAlmostEqual(expected_bias(old,S,tau),0,places=14)
    def test_exact_bias_sign_and_amplitude(self):
        for old,S,tau in [(1.,.1,.1),(.001,.4,.7),(.4,.4,1),(.8,2,5),(.0,.002,100)]:
            a=frozen_packet(old=old,source_rate=S,dt=1.,lambdas=(tau,),energy_ev=60.,binding_ev=(13.6,))
            b=frozen_packet(old=old,source_rate=S,dt=1.,lambdas=(tau,),energy_ev=60.,binding_ev=(13.6,),method='uniform_exact')
            self.assertAlmostEqual(a.survivor-b.survivor,expected_bias(old,S,tau),delta=2e-15)
    def test_photon_species_heat_and_binding_ledger(self):
        rates=(.2,1.,.07)
        for method in ('legacy_be','uniform_exact','be_old_uniform_birth'):
            o=frozen_packet(old=.9,source_rate=.3,dt=3.,lambdas=rates,energy_ev=65.,method=method)
            self.assertGreaterEqual(o.survivor,0)
            self.assertTrue(all(v>=0 for v in o.absorbed_by_species))
            self.assertLess(abs(o.number_residual),1e-14)
            self.assertLess(abs(o.energy_residual),1e-13)
            self.assertGreaterEqual(o.gas_photoheat_ev_per_h,0)
    def test_zero_rates_and_positive_cutoff(self):
        x=frozen_packet(old=.2,source_rate=.3,dt=1.,lambdas=(0.,0.,0.),energy_ev=8.)
        self.assertEqual(x.absorbed,0.)
        with self.assertRaises(ValueError):
            frozen_packet(old=.2,source_rate=0.,dt=1.,lambdas=(0.,0.,.2),energy_ev=25.)
    def test_bad_physical_input_rejected(self):
        for v in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):
                frozen_packet(old=v,source_rate=0.,dt=1.,lambdas=(.2,),energy_ev=60.,binding_ev=(13.6,))


class ManufacturedNonautonomous(unittest.TestCase):
    def test_positive_conservative_nonlinear_time_hazard(self):
        for n in (4,16,64,256):
            for m in ('legacy_be','uniform_exact','be_old_uniform_birth'):
                N,A,S=trial(.265,n,m,3.)
                self.assertGreater(N,0)
                self.assertGreater(A,0)
                self.assertLess(abs(N+A-.265-S),2e-13)
    def test_preasymptotic_ratio_below_one_with_first_order_be(self):
        n0=.265
        y=[trial(n0,n,'legacy_be',3.)[0] for n in (4,8,16,32,64,128,256)]
        r=abs((y[0]-y[1])/(y[1]-y[2]))
        self.assertLess(r,0.70)
        self.assertGreater(r,0.60)
        last=abs((y[-3]-y[-2])/(y[-2]-y[-1]))
        self.assertGreater(last,1.88)
        self.assertLess(last,2.02)
    def test_exact_uniform_second_order_vs_DOP853(self):
        n0=.265;r=reference(n0,3.)[0]
        old=[abs(trial(n0,n,'legacy_be',3.)[0]-r) for n in (128,256)]
        exact=[abs(trial(n0,n,'uniform_exact',3.)[0]-r) for n in (128,256)]
        self.assertGreater(old[0]/old[1],1.8)
        self.assertGreater(exact[0]/exact[1],3.8)
        self.assertLess(exact[1],old[1])
    def test_uniform_birth_only_not_entire_solver_second_order(self):
        r=reference(.265,3.)[0]
        errs=[abs(trial(.265,n,'be_old_uniform_birth',3.)[0]-r) for n in (128,256)]
        self.assertGreater(errs[0]/errs[1],1.8)
        self.assertLess(errs[0]/errs[1],2.2)

if __name__=='__main__':unittest.main(verbosity=2)
