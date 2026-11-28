import copy,json,math,subprocess,sys,tempfile,unittest
from decimal import Decimal as D,localcontext
from fractions import Fraction
from pathlib import Path
import mpmath as mp
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from hh_external import (evaluate_reference as ev,rate_source,application_gate,
                         ProviderError,I,number,analytic)

def contained(bounds,x):return mp.mpf(bounds[0])<=x<=mp.mpf(bounds[1])
class Regression(unittest.TestCase):
    def test_analytic_values_and_derivatives(self):
        with mp.workdps(130):
            for prov,A,p in [('LCS91','1.2e-17','1.2'),('KS92_corrected_Glover15','4.65e-21','1.5')]:
                for val in ['3001','4000','7000','10000','100000','1000000']:
                    with self.subTest(prov=prov,T=val):
                        t=mp.mpf(val);a=mp.mpf(A);pp=mp.mpf(p);b=mp.mpf('157800')
                        f=lambda x:a*x**pp*mp.exp(-b/x)
                        q=ev(prov,val)['pieces'][0]
                        for key,order in [('rate_cm3_s',0),('d1_cm3_s_K',1),('d2_cm3_s_K2',2)]:
                            self.assertTrue(contained(q[key],mp.diff(f,t,order)))
    def test_interval_interior_points_are_enclosed(self):
        with mp.workdps(120):
            for prov,A,p in [('LCS91','1.2e-17','1.2'),('KS92_corrected_Glover15','4.65e-21','1.5')]:
                q=ev(prov,'4000','100000')['pieces'][0]
                for j in range(17):
                    t=mp.mpf(4000)+mp.mpf(j)*6000
                    f=lambda x:mp.mpf(A)*x**mp.mpf(p)*mp.exp(-157800/x)
                    for key,order in [('rate_cm3_s',0),('d1_cm3_s_K',1),('d2_cm3_s_K2',2)]:
                        self.assertTrue(contained(q[key],mp.diff(f,t,order)))
    def test_boundary_ownership(self):
        for lo,hi in [('2999','3000'),('3000','3000'),('3000','3001')]:
            r=ev('LCS91',lo,hi);self.assertIsNone(r['derivatives_global'])
        p=ev('LCS91','3000','3001')['pieces']
        self.assertTrue(p[0]['right_closed']);self.assertFalse(p[1]['left_closed'])
    def test_no_spurious_exact_zero_from_underflow(self):
        with self.assertRaises(ProviderError):ev('KS92_corrected_Glover15','0.01')
        # Not a physical cutoff: LCS's actual low branch remains available.
        self.assertEqual(ev('LCS91','0.01')['rate_cm3_s'],['1E-20','1E-20'])
    def test_invalid_types_and_ranges(self):
        for v in [True,False,float('nan'),3000.0,'NaN','Infinity','1e1001','1'*257,'0','-1']:
            with self.subTest(value=str(v)),self.assertRaises(ProviderError):ev('LCS91',v)
        with self.assertRaises(ProviderError):ev('LCS91','4000','3000')
        with self.assertRaises(ProviderError):ev('UNREGISTERED','4000')
    def test_narrow_decimal_not_rounded_before_branch_selection(self):
        r=ev('LCS91','3000.'+'0'*85+'1')
        self.assertEqual(r['pieces'][0]['branch'],'ANALYTIC')
    def test_ambient_context_independence(self):
        expected=ev('LCS91','7000')
        with localcontext() as c:
            c.prec=4
            self.assertEqual(ev('LCS91','7000'),expected)
    def test_cgs_si_conversion_outward(self):
        r=ev('LCS91','7000','9000')
        lo,hi=(Fraction(D(v)) for v in r['rate_cm3_s'])
        sl,sh=(Fraction(D(v)) for v in r['rate_m3_s'])
        self.assertLessEqual(sl,lo/10**6);self.assertGreaterEqual(sh,hi/10**6)
    def test_source_conservation_and_no_extra_half(self):
        r=ev('LCS91','2000');s=rate_source(r,'5','7')
        q=list(map(lambda a:Fraction(D(a[0])),s['species_sources_m3_s']))
        self.assertEqual(q[0]+q[1]+q[2],0)
        self.assertEqual(q[1]-q[2]-q[3],0)
        self.assertEqual(Fraction(D(s['event_rate_m3_s'][0])),Fraction(25,10**26))
        self.assertEqual(D(s['thermal_J_m3_s'][0])+D(s['binding_J_m3_s'][1]),0)
    def test_zero_density_preserves_known_source(self):
        s=rate_source(ev('LCS91','2000'),'0','3')
        self.assertTrue(all(D(v)==0 for p in s['species_sources_m3_s'] for v in p))
    def test_missing_chi_and_negative_density(self):
        for n,chi in [('-1','3'),('1','0'),('1',None)]:
            with self.assertRaises(ProviderError):rate_source(ev('LCS91','2000'),n,chi)
    def test_response_mutation_rejected(self):
        q=ev('LCS91','2000');q['rate_m3_s']=['0','0']
        with self.assertRaises(ProviderError):rate_source(q,'1','3')
    def test_empty_domain_never_admits_physics(self):
        x=application_gate({});self.assertFalse(x['physical_admission'])
        self.assertEqual(x['canonical_dependency'],'REI-F07')
    def test_presence_is_not_authority_verification(self):
        from hh_external import CONSUMER_FIELDS
        x=application_gate(dict.fromkeys(CONSUMER_FIELDS,'placeholder'))
        self.assertEqual(x['status'],'FIELDS_PRESENT_NOT_AUTHORITY_VERIFIED')
        self.assertFalse(x['physical_admission']);self.assertFalse(x['authority_verification_performed'])
    def test_alias_formula_and_canonical_id(self):
        a=ev('KS92_corrected_Glover15','10000');b=ev('GLOVER2015_KS91_EQ14','10000')
        self.assertEqual(a['rate_cm3_s'],b['rate_cm3_s'])
        self.assertEqual(a['canonical_provider'],'GLOVER2015_KS91_EQ14')
    def test_point_enclosure_is_narrow_not_physical_uncertainty(self):
        q=ev('LCS91','10000');lo,hi=map(D,q['rate_cm3_s'])
        self.assertLess((hi-lo)/lo,D('1e-75'))
        self.assertFalse(q['admission'])
        self.assertEqual(q['physical_uncertainty_kind'],'UNQUANTIFIED_EMPIRICAL_MODEL_ERROR')
    def test_cli_exclusive_creation(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'out.json'; cmd=[sys.executable,'-B',str(ROOT/'src/hh_external.py'),'--provider','LCS91','--lower','3000','--out',str(f)]
            p=subprocess.run(cmd,capture_output=True);self.assertEqual(p.returncode,0,p.stderr)
            old=f.read_bytes();p=subprocess.run(cmd,capture_output=True)
            self.assertEqual(p.returncode,2);self.assertEqual(f.read_bytes(),old)
    def test_cli_does_not_create_output_on_invalid_input(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'out.json'
            p=subprocess.run([sys.executable,'-B',str(ROOT/'src/hh_external.py'),'--provider','LCS91','--lower','0','--out',str(f)],capture_output=True)
            self.assertEqual(p.returncode,2);self.assertFalse(f.exists())

if __name__=='__main__':unittest.main()
