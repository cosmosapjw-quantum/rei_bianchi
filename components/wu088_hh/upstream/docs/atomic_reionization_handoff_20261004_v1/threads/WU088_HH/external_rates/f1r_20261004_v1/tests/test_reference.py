import sys, unittest, hashlib, subprocess, tempfile
from pathlib import Path
from decimal import Decimal as D,localcontext,ROUND_DOWN
import mpmath as mp
import sympy as sp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hh_external import SPECS,ProviderError
from hh_source_jet import log_jet,source_jet,taylor_step
mp.mp.dps=130

def contains(pair,x):return mp.mpf(pair[0])<=x<=mp.mpf(pair[1])
def fit(provider,T):
    a,p,b=map(mp.mpf,SPECS[provider]);return a*T**p*mp.exp(-b/T)*mp.mpf('1e-6')

class Reference(unittest.TestCase):
    def test_exact_symbolic_log_polynomials(self):
        p,x=sp.symbols('p x');P=sp.Integer(1);got=[]
        for _ in range(3):P=sp.expand((p+x)*P-x*sp.diff(P,x));got.append(P)
        want=[p+x,p*p+(2*p-1)*x+x*x,p**3+(3*p*p-3*p+1)*x+(3*p-3)*x*x+x**3]
        self.assertTrue(all(sp.expand(a-b)==0 for a,b in zip(got,want)))
    def test_log_derivatives_independent_values(self):
        for provider in SPECS:
            for T in ['4000','10000','100000','1000000']:
                jet=log_jet(provider,T)
                for order in range(4):
                    exact=mp.diff(lambda y:fit(provider,mp.mpf(T)*mp.exp(y)),mp.mpf('0'),order)
                    self.assertTrue(contains(jet['global_dlogT_m3_s'][order],exact),(provider,T,order))
        for T in ['100','2999']:
            jet=log_jet('LCS91',T)
            self.assertEqual(jet['global_dlogT_m3_s'][1:],[['0.000000','0.000000']]*3)
    def test_interval_derivative_ranges(self):
        for provider in SPECS:
            jet=log_jet(provider,'4000','12000')
            for T in ['4000','6500','12000']:
                for order in range(4):
                    val=mp.diff(lambda y:fit(provider,mp.mpf(T)*mp.exp(y)),mp.mpf('0'),order)
                    self.assertTrue(contains(jet['global_dlogT_m3_s'][order],val))
    def test_mixed_partials_and_units(self):
        for provider in SPECS:
            T=mp.mpf('10000');n=mp.mpf('2')
            jet=source_jet(provider,'10000','2','3e-18')
            f=lambda a,b:a*a*fit(provider,T*mp.exp(b))
            for key,orders in [('n',(1,0)),('y',(0,1))]:
                self.assertTrue(contains(jet['gradient'][key],mp.diff(f,(n,mp.mpf(0)),orders)))
            for key,orders in [('nn',(2,0)),('ny',(1,1)),('yy',(0,2))]:
                self.assertTrue(contains(jet['hessian'][key],mp.diff(f,(n,mp.mpf(0)),orders)))
            for key,orders in [('nny',(2,1)),('nyy',(1,2)),('yyy',(0,3))]:
                self.assertTrue(contains(jet['third'][key],mp.diff(f,(n,mp.mpf(0)),orders)))
            # This derivative is algebraically zero; numerical differencing is not a zero oracle.
            ns=sp.symbols('ns');self.assertEqual(sp.diff(ns**2,ns,3),0)
            self.assertTrue(all(D(v)==0 for v in jet['third']['nnn']))
    def test_finite_segment_remainders(self):
        for provider in SPECS:
            for dy in ['-0.1','-0.01','0.001','0.1']:
                for dn in ['-0.2','0','0.2']:
                    got=taylor_step(provider,'10000','2',dy,dn,'3e-18')
                    Y,N=mp.mpf(dy),mp.mpf(dn)
                    f=lambda s:(2+s*N)**2*fit(provider,mp.mpf('10000')*mp.exp(s*Y))
                    poly=sum(mp.diff(f,mp.mpf(0),j)/mp.factorial(j) for j in range(3))
                    err=abs(f(1)-poly)
                    self.assertLessEqual(err,mp.mpf(got['event_remainder_abs_upper_m3_s']))
                    self.assertTrue(contains(got['endpoint_enclosure_m3_s'],f(1)))
                    self.assertTrue(contains(got['direct_endpoint_image_m3_s'],f(1)))
    def test_zero_density_source_jet_is_regular(self):
        jet=source_jet('LCS91','10000','0','3e-18')
        self.assertTrue(all(D(x)==0 for x in jet['value']))
        self.assertTrue(all(D(x)==0 for x in jet['gradient']['n']))
        self.assertGreater(D(jet['hessian']['nn'][0]),0)
        self.assertGreater(D(jet['third']['nny'][0]),0)
    def test_zero_start_can_create_density_path_not_time_update(self):
        got=taylor_step('LCS91','10000','0','0.01','0.2','3e-18')
        value=mp.mpf('0.2')**2*fit('GRACKLE_3_4_1_K57',mp.mpf('10000')*mp.exp(mp.mpf('0.01')))
        self.assertTrue(contains(got['endpoint_enclosure_m3_s'],value))
        self.assertFalse(got['state_segment']['time_step'])
    def test_pure_density_is_quadratic(self):
        got=taylor_step('LCS91','10000','2','0','-2','3e-18')
        self.assertEqual(D(got['event_remainder_abs_upper_m3_s']),0)
        self.assertTrue(contains(got['endpoint_enclosure_m3_s'],0))
        self.assertTrue(all(D(x)==0 for x in got['direct_endpoint_image_m3_s']))
    def test_floor_interior_has_zero_temperature_remainder(self):
        got=taylor_step('LCS91','1000','2','0.1','0.2','3e-18')
        self.assertEqual(D(got['event_remainder_abs_upper_m3_s']),0)
        self.assertTrue(contains(got['endpoint_enclosure_m3_s'],mp.mpf('4.84e-26')))
    def test_touching_cutoff_is_nonsmooth(self):
        for lo,hi in [('2999','3000'),('3000','3000'),('3000','3001')]:
            self.assertIsNone(log_jet('LCS91',lo,hi)['global_dlogT_m3_s'])
        with self.assertRaisesRegex(ProviderError,'NONSMOOTH'):
            source_jet('LCS91','3000','1','3e-18')
    def test_boundary_pieces_are_not_missing(self):
        j=log_jet('LCS91','2999','3001')
        self.assertEqual([p['branch'] for p in j['pieces']],['ARTIFICIAL_FLOOR','ANALYTIC'])
        self.assertFalse(j['pieces'][1]['left_closed'])
        self.assertGreater(D(j['pieces'][0]['dlogT_m3_s'][0][0]),D(j['pieces'][1]['dlogT_m3_s'][0][1]))
    def test_correctedKS_does_not_inherit_cutoff(self):
        j=log_jet('GLOVER2015_KS91_EQ14','2999','3001')
        self.assertEqual(j['boundary_status'],'SMOOTH_ANALYTIC')
        self.assertIsNotNone(j['global_dlogT_m3_s'])
    def test_floor_boundary_step_decrease_is_also_rejected(self):
        with self.assertRaisesRegex(ProviderError,'NONSMOOTH'):
            taylor_step('LCS91','3001','2','-0.01','0','3e-18')
    def test_units_and_energy_are_same_event(self):
        j=taylor_step('LCS91','10000','2','0.01','0.2','3e-18')
        self.assertEqual(j['species_endpoint_enclosures'][1],j['species_endpoint_enclosures'][3])
        self.assertEqual(D(j['thermal_endpoint_J_m3_s'][0]),D(j['binding_endpoint_J_m3_s'][1]).copy_negate())
        self.assertEqual(j['conservation_residuals']['thermal_plus_binding'],['0','0'])
    def test_no_physical_or_consumer_admission(self):
        j=taylor_step('LCS91','10000','2','0.01','0.2','3e-18')
        self.assertFalse(j['admission']);self.assertIsNone(j['physical_domain'])
        self.assertIn('NOT_FULL_REI_RESIDUAL',j['claim_ceiling'])
    def test_bad_representation_and_parameters(self):
        for T in [10000.0,True,'nan','Infinity','0','-1']:
            with self.assertRaises(ProviderError):log_jet('LCS91',T)
        with self.assertRaises(ProviderError):source_jet('LCS91','10000','1','0')
        with self.assertRaises(ProviderError):source_jet('wrong','10000','1','3e-18')
    def test_oversize_path_not_silent_underflow(self):
        with self.assertRaisesRegex(ProviderError,'NUMERIC'):
            taylor_step('LCS91','10000','1','-100001','0','3e-18')
    def test_hostile_decimal_context_cannot_change_output(self):
        a=taylor_step('LCS91','10000','2','0.01','0.2','3e-18')
        with localcontext() as c:
            c.prec=3;c.rounding=ROUND_DOWN
            b=taylor_step('LCS91','10000','2','0.01','0.2','3e-18')
        self.assertEqual(a,b)
    def test_cli_exclusive_output_and_failure_has_no_file(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'x.json'
            cmd=[sys.executable,'-B',str(ROOT/'src/hh_source_jet.py'),'--provider','LCS91','--T','10000','--n','2','--chi','3e-18','--dy','0.01','--dn','0.2','--out',str(path)]
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
            before=path.read_bytes()
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,2)
            self.assertEqual(path.read_bytes(),before)
            out=Path(d)/'bad.json';cmd[-1]=str(out);cmd[cmd.index('--T')+1]='2999'
            self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,2)
            self.assertFalse(out.exists())
    def test_inherited_F1_byte_identity(self):
        self.assertEqual(hashlib.sha256((ROOT/'src/hh_external.py').read_bytes()).hexdigest(),'8c02df302adc895be1327cb2e55bae03ebed8ec06ee7496ff4eeda20fdcdc197')

if __name__=='__main__':unittest.main()
