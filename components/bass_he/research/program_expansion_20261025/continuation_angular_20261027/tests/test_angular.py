"""New angular contracts only. Parent PHOTON05 is read as saved data."""
import hashlib
import json
import math
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from angular_pushforward import (AngularMap,ContractError,AngularResolutionError,
                                from_masses,normalization_weights,inclusive_from_event_atom)
PARENT=ROOT.parent/'continuation_photon_20261027'
SAVED=PARENT/'evidence/validation/SAVED_PLOT_DATA.json'
DATA=json.loads(SAVED.read_text())

def dec(x):
    return Decimal.from_float(float(x))

def ref_nu(g,a,m):
    """Direction directly from longitudinal/transverse vector components."""
    z=g*m+g*a
    x2=(Decimal(1)-m)*(Decimal(1)+m)
    return z/(x2+z*z).sqrt()

def bracketed_root(g,a,nu,left,right,increasing):
    """Independent bisection, no quadratic formula or implementation calls."""
    with localcontext() as c:
        c.prec=90
        g,a,n=dec(g),dec(a),dec(nu)
        lo,hi=left,right
        for _ in range(150):
            m=(lo+hi)/2
            if (ref_nu(g,a,m)<n)==increasing:lo=m
            else:hi=m
        return float((lo+hi)/2)

class AngularTests(unittest.TestCase):
    def assertNear(self,a,b,rel=5e-13,absolute=2e-14):
        self.assertLessEqual(abs(a-b),absolute+rel*abs(b),(a,b))

    def test01_parent_saved_identity(self):
        self.assertEqual(hashlib.sha256(SAVED.read_bytes()).hexdigest(),
                         '923c9349019d7061a4d6e71343ef6930b9db6b95b82f16085f725f18b618d755')
        self.assertEqual(len(DATA['native']),12)
        self.assertFalse(DATA['physical_rate_admitted'])

    def test02_native_directions_against_stored_vectors(self):
        for row in DATA['native']:
            ev=row['event'];p=from_masses(ev['A'],ev['M'],ev['photon_energy'])
            for label,sign in [('plus',1),('minus',-1)]:
                q=ev[label]['momentum_energy']
                expected=q[2]/math.hypot(*q)
                actual=p['map'].forward(sign*ev['u'][2])['nu']
                self.assertNear(actual,expected,rel=0,absolute=2e-14)

    def test03_native_jacobian_independent_vector_derivative(self):
        with localcontext() as c:
            c.prec=90
            for row in DATA['native']:
                ev=row['event'];p=from_masses(ev['A'],ev['M'],ev['photon_energy'])
                for sign in (1,-1):
                    m=dec(sign*ev['u'][2]);g=dec(p['gamma']);a=dec(p['a'])
                    x=(1-m*m).sqrt();z=g*m+g*a;dx=-m/x;dz=g
                    Q=(x*x+z*z).sqrt();dQ=(x*dx+z*dz)/Q
                    ref=(dz*Q-z*dQ)/(Q*Q)
                    self.assertNear(p['map'].forward(float(m))['jacobian_signed'],float(ref))

    def test04_identity_map(self):
        m=AngularMap(1,0)
        for mu in (-1,-.77,-.1,0,.25,.99,1):
            self.assertEqual(m.forward(mu)['nu'],mu)
            self.assertEqual(m.forward(mu)['jacobian_signed'],1)
            self.assertEqual(m.inverse(mu)['branches'][0]['mu'],mu)

    def test05_zero_drift_symmetry_and_poles(self):
        m=AngularMap(1.25,0)
        for mu in (.1,.5,.9):self.assertEqual(m.forward(mu)['nu'],-m.forward(-mu)['nu'])
        for mu in (-1,1):self.assertNear(m.forward(mu)['jacobian_signed'],1/1.25**2)

    def test06_single_branch_independent_bisection(self):
        for g,a in [(1,.3),(1.25,.7),(3,.2)]:
            m=AngularMap(g,a)
            for nu in (-.9,-.3,0,.2,.8):
                br=m.inverse(nu)['branches'];self.assertEqual(len(br),1)
                r=bracketed_root(g,a,nu,Decimal(-1),Decimal(1),True)
                self.assertNear(br[0]['mu'],r,rel=0,absolute=2e-12)
                self.assertNear(m.forward(br[0]['mu'])['nu'],nu,rel=0,absolute=2e-14)

    def test07_fold_branches_independent_bisection(self):
        for g,a in [(1,2),(1.25,1.5),(2,1.1)]:
            m=AngularMap(g,a)
            with localcontext() as c:
                c.prec=90;fold=-Decimal(1)/dec(a)
                for t in (.2,.5,.8):
                    nu=m.nu_min+(1-m.nu_min)*t;br=m.inverse(nu)['branches']
                    self.assertEqual(len(br),2)
                    refs=[bracketed_root(g,a,nu,Decimal(-1),fold,False),bracketed_root(g,a,nu,fold,Decimal(1),True)]
                    for x,r in zip(br,refs):
                        self.assertNear(x['mu'],r,rel=0,absolute=2e-12)
                        self.assertNear(m.forward(x['mu'])['nu'],nu,rel=0,absolute=2e-14)

    def test08_original_sign_filter_and_support(self):
        for a in (1,2,5):
            m=AngularMap(1.2,a)
            self.assertEqual(m.inverse(-.5)['status'],'OUTSIDE_SUPPORT')
        m=AngularMap(1.25,2)
        self.assertEqual(m.inverse(math.nextafter(m.nu_min,-math.inf))['branches'],[])
        self.assertEqual(m.inverse(0)['status'],'OUTSIDE_SUPPORT')

    def test09_endpoint_multiplicity(self):
        for a in (0,.5,1,2):
            m=AngularMap(1.25,a)
            self.assertEqual([x['mu'] for x in m.inverse(1)['branches']],[-1,1] if a>1 else [1])
        self.assertEqual(AngularMap(1.25,.3).inverse(-1)['branches'][0]['mu'],-1)

    def test10_fold_density_is_explicit(self):
        m=AngularMap(1.25,2)
        f=m.forward(m.fold_mu);r=m.inverse(m.nu_min);d=m.density(m.nu_min,lambda mu:.5)
        self.assertEqual(f['status'],'FOLD');self.assertEqual(r['status'],'FOLD')
        self.assertEqual(len(r['branches']),1);self.assertEqual(r['branches'][0]['jacobian_abs'],0)
        self.assertIsNone(d['density']);self.assertTrue(d['singular'])

    def test11_stopped_direction_and_open_boundary(self):
        m=AngularMap(1.25,1)
        self.assertEqual(m.forward(-1)['status'],'STOPPED');self.assertIsNone(m.forward(-1)['nu'])
        self.assertEqual(m.inverse(0)['status'],'OPEN_BOUNDARY')
        for nu in (.1,.5,.9):
            br=m.inverse(nu)['branches'];self.assertEqual(len(br),1)
            self.assertNear(m.forward(br[0]['mu'])['nu'],nu)

    def test12_exact_threshold_atom(self):
        p=from_masses(2,2,3)
        self.assertEqual(p['status'],'THRESHOLD_ATOM');self.assertIsNone(p['map'])
        self.assertEqual(p['distribution'],{'kind':'ATOM','nu':1})
        with self.assertRaises(ContractError):from_masses(2,2,math.nextafter(3,0))

    def test13_rounded_threshold_is_not_an_atom(self):
        # eth=7/6 is not a binary64 number. Upward rounding has positive excess.
        e=float(Fraction(7,6));self.assertNotEqual(Fraction.from_float(e),Fraction(7,6))
        if Fraction.from_float(e)<Fraction(7,6):
            with self.assertRaises(ContractError):from_masses(3,2,e)
        else:
            # Such tiny excess may exceed the declared a domain; no false atom.
            try:p=from_masses(3,2,e)
            except ContractError:return
            self.assertNotEqual(p['status'],'THRESHOLD_ATOM')

    def test14_transition_separate_from_threshold(self):
        p=from_masses(3,2,1.5)
        self.assertEqual(p['a'],1);self.assertEqual(p['transition_energy'],1.5)
        self.assertNear(p['threshold'],7/6)
        self.assertEqual(from_masses(3,2,1.4)['map'].regime,'TWO_BRANCH_FOLD')
        self.assertEqual(from_masses(3,2,1.6)['map'].regime,'ONE_BRANCH')

    def test15_no_finite_transition_when_A_le_M(self):
        for A,M,e in [(2,2,4),(2,2,100),(1,2,10)]:
            p=from_masses(A,M,e);self.assertIsNone(p['transition_energy'])
            self.assertEqual(p['map'].regime,'TWO_BRANCH_FOLD')

    def test16_invalid_scalar_contract(self):
        for x in (True,None,'1',float('nan'),float('inf')):
            with self.assertRaises(ContractError):AngularMap(x,.3)
            with self.assertRaises(ContractError):AngularMap(1,x)
            with self.assertRaises(ContractError):AngularMap(1,.3).forward(x)
        for mu in (-1.0001,1.0001):
            with self.assertRaises(ContractError):AngularMap(1,.3).forward(mu)

    def test17_parameter_domain(self):
        for g,a in [(.99,0),(1,-.1),(1e6+1,0),(1,1e6+1)]:
            with self.assertRaises(ContractError):AngularMap(g,a)
        for args in [(0,2,4),(4,2,4),(5,2,4),(2,-2,4),(2,2,0)]:
            with self.assertRaises(ContractError):from_masses(*args)

    def test18_density_nonnegativity_and_original_sign(self):
        m=AngularMap(1.25,2);nu=(1+m.nu_min)/2
        p=m.density(nu,lambda mu:.5)
        self.assertGreater(p['density'],0);self.assertEqual(len(p['branches']),2)
        self.assertLess(m.forward(p['branches'][0]['mu'])['jacobian_signed'],0)
        with self.assertRaises(ContractError):m.density(nu,lambda mu:-1)
        with self.assertRaises(ContractError):m.density(nu,None)

    def test19_branch_weighted_energy_preserves_information(self):
        p=from_masses(2,2,4);m=p['map'];nu=(1+m.nu_min)/2
        eta=4/p['cm_energy'];mean=3.;slope=eta*p['kappa']
        E=lambda mu:mean+slope*mu
        r=m.weighted_density(nu,lambda mu:.5,E)
        r2=m.weighted_density(nu,lambda mu:.5,lambda mu:E(mu)**2)
        self.assertEqual(len(r['branches']),2)
        self.assertNotEqual(r['branches'][0]['weight'],r['branches'][1]['weight'])
        variance=r2['density']/r['unweighted_density']-(r['density']/r['unweighted_density'])**2
        self.assertGreater(variance,0)
        self.assertNear(r['density'],sum(x['contribution'] for x in r['branches']))

    def test20_quotient_conventions_exact_discrete(self):
        f=normalization_weights('EVENT_SYMMETRIC_FULL_SPHERE')
        h=normalization_weights('INCLUSIVE_DAUGHTER_FULL_SPHERE')
        H=normalization_weights('EVENT_REPRESENTATIVE_HEMISPHERE')
        # Two equally weighted antipodes; B+=3 and B-=7, event weight=5.
        event_pair=sum(Fraction(5,2)*10*Fraction(f['pair_observable_factor']) for _ in range(2))
        inclusive_pair=sum(Fraction(5)*10*Fraction(h['pair_observable_factor']) for _ in range(2))
        single=sum(Fraction(5)*B*Fraction(h['single_inclusive_factor']) for B in (3,7))
        self.assertEqual(event_pair,50);self.assertEqual(inclusive_pair,50);self.assertEqual(single,50)
        self.assertIsNone(H['single_inclusive_factor']);self.assertTrue(H['must_sum_pair'])
        with self.assertRaises(ContractError):normalization_weights('EXFOR_UNKNOWN')
        self.assertEqual(inclusive_from_event_atom(5)['inclusive_weight'],10)

    def test21_fold_asymptotic_integrable(self):
        m=AngularMap(1.25,2)
        y1=m.density(m.nu_min+1e-5,lambda mu:.5)['density']
        y2=m.density(m.nu_min+2.5e-6,lambda mu:.5)['density']
        self.assertLess(abs(y2/y1-2),.002)

    def test22_finite_fold_bin_mass(self):
        m=AngularMap(1.25,2);hi=m.nu_min+.01
        roots=m.inverse(hi)['branches'];mass=.5*(roots[1]['mu']-roots[0]['mu'])
        with localcontext() as c:
            c.prec=90;fold=-Decimal(1)/2
            lo=bracketed_root(1.25,2,hi,Decimal(-1),fold,False)
            high=bracketed_root(1.25,2,hi,fold,Decimal(1),True)
        self.assertNear(mass,.5*(high-lo),rel=0,absolute=2e-11)
        self.assertGreater(mass,0);self.assertLess(mass,1)

    def test23_unresolvable_direction_is_not_fabricated(self):
        m=AngularMap(1,2)
        with self.assertRaises(AngularResolutionError):m.forward(math.nextafter(m.fold_mu,0))
        with self.assertRaises(AngularResolutionError):AngularMap(1e6,1e6).nu_min
        self.assertEqual(AngularMap(1e6,1e6).forward(1)['nu'],1)
        self.assertEqual(AngularMap(1e6,1e6).forward(-1)['nu'],1)

    def test24_weighted_signed_values_and_overflow(self):
        m=AngularMap(1,0)
        self.assertEqual(m.weighted_density(.3,lambda mu:2,lambda mu:-3)['density'],-6)
        with self.assertRaises(ContractError):m.weighted_density(.3,lambda mu:1,lambda mu:float('nan'))
        with self.assertRaises(AngularResolutionError):m.weighted_density(.3,lambda mu:1e308,lambda mu:10)

    def test25_protected_thermal_ports_and_budget(self):
        d=json.loads((ROOT/'MODEL_CONTRACT.json').read_text())
        for k in ('Gamma_thermal','Cv','species_heating','thermal_deposition','independent_binding_rhs'):
            self.assertIsNone(d['energy_and_population'][k])
        self.assertEqual(d['protected']['HE101']['reserve'],0)
        self.assertEqual(d['protected']['HE101']['outcomes'],['PASS','FAIL','FAIL'])
        self.assertEqual(d['protected']['PHOTON05']['workflow'],'PARTIAL')

    def test99_save_new_angular_data_without_parent_replay(self):
        native=[]
        for row in DATA['native']:
            ev=row['event'];p=from_masses(ev['A'],ev['M'],ev['photon_energy']);m=p['map']
            plus=m.forward(ev['u'][2]);minus=m.forward(-ev['u'][2])
            native.append({'source_row':row['source_row'],'source_values':row['values'],'source_units':row['units'],
                           'gamma':p['gamma'],'a':p['a'],'regime':m.regime,'plus':plus,'minus':minus,
                           'plus_lab_angle_deg':math.degrees(math.acos(plus['nu'])),
                           'minus_lab_angle_deg':math.degrees(math.acos(minus['nu'])),
                           'DCS_scaled':False,'event_flux_inferred':False})
        curves=[]
        for a in (.3,1,2):
            m=AngularMap(1.25,a);values=[m.forward(-1+2*i/160) for i in range(161)]
            curves.append({'gamma':1.25,'a':a,'scope':'SYNTHETIC_MAP_CONTROL','values':values})
        m=AngularMap(1.25,2);caustic=[]
        for i in range(61):
            dx=10**(-6+4*i/60);d=m.density(m.nu_min+dx,lambda mu:.5)
            caustic.append({'delta_nu':dx,'density':d['density']})
        out={'schema':'HE_ANGULAR06_SAVED_DATA_V1','parent_saved_sha256':hashlib.sha256(SAVED.read_bytes()).hexdigest(),
             'native':native,'synthetic_curves':curves,'synthetic_fold_density':caustic,
             'physical_rate_admitted':False,'old_scientific_kernel_calls':0,'source_DCS_normalization':'UNRESOLVED'}
        dst=ROOT/'evidence/validation/SAVED_PLOT_DATA.json';dst.parent.mkdir(parents=True,exist_ok=True)
        dst.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
        self.assertEqual(len(native),12)

if __name__=='__main__':unittest.main()
