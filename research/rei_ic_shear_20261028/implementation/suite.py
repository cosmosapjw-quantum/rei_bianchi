"""Single finite standard-library formula suite and small CSV/JSON products."""
import csv
import hashlib
import json
import math
import unittest
from pathlib import Path
import ic_bianchi as m

CONTRACT=json.loads((m.UNIT/'theory/BIANCHI_BENCHMARK_CONTRACT.json').read_text())
PROFILES=json.loads((m.UNIT/'theory/INITIAL_PROFILES.json').read_text())
RTOL=CONTRACT['numeric_tolerance']['relative']
ATOL=CONTRACT['numeric_tolerance']['absolute']


class FormulaTests(unittest.TestCase):
    def close(self,a,b):self.assertTrue(math.isclose(a,b,rel_tol=RTOL,abs_tol=ATOL),msg=f'{a!r} != {b!r}')

    def test_offdiagonal_contraction_and_stf(self):
        a=m.matrix([.1,-.2,.1,.03,0.,.04]);b=m.matrix([.02,.01,-.03,0.,.01,.02])
        m.stf(a);m.stf(b)
        self.close(m.dot(a,b),.1*.02-.2*.01+.1*(-.03)+2*.04*.02)
        self.assertEqual(m.packed(a),[.1,-.2,.1,.03,0.,.04])
        with self.assertRaises(ValueError):m.stf(m.matrix([1,0,0,0,0,0]))

    def test_phase_distribution_positivity_domain(self):
        for q in (-1.,-.05,0.,.05,2.):
            a=m.lrs_quadrupole(q,(1.,2.,3.))
            check=m.quadrupole_distribution(a)
            self.assertGreaterEqual(check['minimum_angular_factor'],-1e-12)
        with self.assertRaises(ValueError):m.lrs_quadrupole(2.001)
        with self.assertRaises(ValueError):m.quadrupole_distribution(m.matrix([-1.1,.55,.55,0,0,0]))
        generic=m.matrix([.1,-.04,-.06,.03,-.02,.01])
        self.assertGreater(m.quadrupole_distribution(generic)['minimum_angular_factor'],0.)

    def test_independent_angular_moment_quadrature(self):
        # Fixed GL3(mu) x8 uniform azimuth rule is exact for these degree<=4
        # polynomial spherical moments. This is not a dynamical integration.
        a=m.matrix([.1,-.04,-.06,.03,-.02,.01])
        norm=0.;pressure=[[0.]*3 for _ in range(3)]
        for mu,w in ((-math.sqrt(.6),5/9),(0.,8/9),(math.sqrt(.6),5/9)):
            for j in range(8):
                phi=2*math.pi*j/8;n=(math.sqrt(1-mu*mu)*math.cos(phi),math.sqrt(1-mu*mu)*math.sin(phi),mu)
                angular=1+sum(n[i]*a[i][k]*n[k] for i in range(3) for k in range(3));weight=w/16
                norm+=weight*angular
                for i in range(3):
                    for k in range(3):pressure[i][k]+=weight*angular*n[i]*n[k]
        theory=m.component_moments(1.,1/3,a)
        self.close(norm,1.)
        for i in range(3):
            for j in range(3):self.close(pressure[i][j],theory['pressure'][i][j])
        self.close(m.trace(theory['pressure']),1.);self.close(m.trace(theory['pi']),0.)

    def test_matter_stress_suppression_and_dust(self):
        a=m.lrs_quadrupole(.05);w=CONTRACT['benchmarks']['matter_w']
        rad=m.component_moments(1.,1/3,a);matter=m.component_moments(1.,w,a)
        self.close(matter['pi'][2][2]/rad['pi'][2][2],3*w)
        self.assertGreaterEqual(matter['minimum_pressure_eigenvalue'],0.)
        self.assertEqual(m.component_moments(1.,0.,a)['pi'],m.ZERO)
        with self.assertRaises(ValueError):m.component_moments(1.,.5,a)

    def test_hamiltonian_initializer_and_invalid_domain(self):
        S=m.matrix([-.001,-.001,.002,.0002,.0001,-.0003])
        positive=m.initial_geometry(1.,S);negative=m.initial_geometry(1.,m.scale(S,-1))
        self.close(positive['relative_constraint_residual'],0.)
        self.close(positive['H_s-1'],negative['H_s-1'])
        self.assertGreater(positive['H_s-1'],m.initial_geometry(1.,m.ZERO)['H_s-1'])
        with self.assertRaises(ValueError):m.initial_geometry(1.,m.matrix([-1,-1,2,0,0,0]))
        with self.assertRaises(ValueError):m.initial_geometry(0.,m.ZERO)
        with self.assertRaises(ValueError):m.initial_geometry(-1.,m.ZERO)

    def test_constraint_propagation_identity(self):
        sigma=m.matrix([.1,-.2,.1,.03,0.,.04])
        r=m.component_moments(1.,1/3,m.lrs_quadrupole(.05,(1.,2.,3.)))
        matter=m.component_moments(2.,1e-6,m.lrs_quadrupole(-.05,(2.,-1.,1.)))
        # Independently oriented tensors need not commute; no shared eigenframe
        # is introduced by the generic derivative calculation.
        result=m.gravity_derivatives(.9,sigma,[r,matter],Lambda=.1/m.C**2,kappa=1.)
        self.close(result['Cdot_plus_2HC_plus_kappa_sumQ'],0.)
        self.close(result['Cdot'],-2*.9*result['C'])

    def test_signed_relative_axis_work(self):
        s=.001;rho=1.;q=.05;sigma=m.matrix([-s,-s,2*s,0,0,0])
        for cosine in CONTRACT['benchmarks']['angle_cosines']:
            axis=(math.sqrt(max(0.,1-cosine*cosine)),0.,cosine)
            pi=m.component_moments(rho,1/3,m.lrs_quadrupole(q,axis))['pi']
            expected=2/5*s*rho*q*(3*cosine*cosine-1)/2
            self.close(m.dot(sigma,pi),expected)
            self.close(m.dot(sigma,m.scale(pi,-1)),-expected)
        aligned=m.component_moments(1.,1/3,m.lrs_quadrupole(q))['pi']
        transverse=m.component_moments(1.,1/3,m.lrs_quadrupole(q,(1.,0.,0.)))['pi']
        self.assertGreater(m.dot(sigma,aligned),0.);self.assertLess(m.dot(sigma,transverse),0.)

    def test_free_and_forced_analytic_limits(self):
        S=m.matrix([-.001,-.001,.002,0.,0.,0.]);pi=m.matrix([-.01,-.01,.02,.003,0.,0.])
        for x in CONTRACT['benchmarks']['x_values']:
            self.close(m.F(0,x),math.log(x));self.close(m.F(1e-14,x),math.log(x))
            for p in CONTRACT['benchmarks']['background_H_exponents_p']:
                free=m.normalized_response(S,m.ZERO,p,4,x)
                for i in range(3):
                    for j in range(3):self.close(free[i][j]*x**(-p),S[i][j]*x**(-3))
                plus=m.normalized_response(m.ZERO,pi,p,4,x)
                minus=m.normalized_response(m.ZERO,m.scale(pi,-1),p,4,x)
                self.close(m.dot(m.add(plus,minus),m.add(plus,minus)),0.)
                self.assertEqual(m.normalized_response(m.ZERO,m.ZERO,p,4,x),m.ZERO)
        with self.assertRaises(ValueError):m.F(0,0)

    def test_profile_normalization_zeros_and_legacy_identity(self):
        extracted=json.loads((m.UNIT/'implementation/CURRENT_INITIAL_VALUES.json').read_text())
        legacy=m.initial_profile()
        self.assertEqual(legacy['state17_per_Href'],list(extracted['per_Href_visible'].values()))
        self.close(legacy['baryons_per_Href'],1.32808000350006)
        self.assertGreater(legacy['thermal_energy_eV_per_Href'],.03)
        self.assertLess(legacy['thermal_energy_eV_per_Href'],.05)
        for profile in PROFILES['profiles']:
            result=m.initial_profile(profile['id']);y=result['state17_per_Href']
            self.close(result['electron_per_Href'],profile['electron_charge_per_Href'])
            self.assertGreater(result['thermal_energy_eV_per_Href'],0.)
            self.assertEqual([y[j] for j in (0,5,6)],[0,0,0])
            self.assertEqual(result['fast_B_per_Href'],[0,0]);self.assertEqual(result['fast_U_eV_per_Href'],[0,0])
            self.assertFalse(result['abundance_floors_added']);self.assertFalse(result['automatic_bath_substitution'])
            self.assertGreater(result['baryons_per_Href'],1.) # no baryon renormalization to1
            for indices,total in (([1,2],1.),([7,8,9],1e-5),([10,11,12],.082),([13,14,15,16],5e-10)):
                self.close(sum(y[j] for j in indices),total)
            self.close(sum(y[3:5]),2.5e-5 if profile['id']=='legacy_reproduction_300K' else 2.527e-5)
        cold=m.initial_profile('cold_IGM_residual_source_onset_8K')
        self.close(cold['baryons_per_Href'],1.32808054350006)
        self.close(cold['state17_per_Href'][4]/sum(cold['state17_per_Href'][3:5]),.0002)
        self.assertIn('REQUIRES_NEW',cold['compatible_bath'])
        with self.assertRaises(ValueError):m.initial_profile('automatic_cold_default')

    def test_explicit_constant_prehistory_limits(self):
        onset=m.constant_prehistory(2.,14.,1.,0.)
        self.assertEqual(onset['B_per_Href'],0.);self.assertEqual(onset['U_eV_per_Href'],0.)
        finite=m.constant_prehistory(2.,14.,1.,math.log(2.))
        self.close(finite['B_per_Href'],1.);self.close(finite['U_eV_per_Href'],7.)
        relaxed=m.constant_prehistory(2.,14.,1.,relaxed=True)
        self.close(relaxed['B_per_Href'],2.);self.close(relaxed['U_eV_per_Href'],14.)
        no_loss=m.constant_prehistory(2.,14.,0.,3.)
        self.close(no_loss['B_per_Href'],6.);self.close(no_loss['U_eV_per_Href'],42.)
        with self.assertRaises(ValueError):m.constant_prehistory(0.,1.,1.,3.)
        with self.assertRaises(ValueError):m.constant_prehistory(2.,14.,1.)
        with self.assertRaises(ValueError):m.constant_prehistory(2.,14.,0.,relaxed=True)


def write_products(out):
    initialized=[m.initial_profile(profile['id']) for profile in PROFILES['profiles']]
    (out/'INITIALIZED_PROFILES.json').write_text(json.dumps({'profiles':initialized,'auxiliary_IC':PROFILES['auxiliary_IC'],
        'status':'INITIAL_DATA_CONSTRUCTIONS_NOT_EVOLVED','old_bath_or_IC_mutated':False},indent=2,allow_nan=False)+'\n')
    b=CONTRACT['benchmarks'];D=m.matrix([-1.,-1.,2.,0.,0.,0.])
    with (out/'ANALYTIC_RESPONSE.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['row','background_p','x_a_over_a0','initial_LRS_s_over_H','q_rad','q_matter',
            'free_s_over_H','rad_s_over_H_per_kappa_rhorad_over_H0sq','matter_s_over_H_per_kappa_rhom_over_H0sq',
            'F_3pluspminus4','F_3pluspminus5','Omega_sigma0','relative_constraint_residual'])
        for name,(S,qr,qm) in zip(('B0','S+','S-','R+','R-','M+','M-'),b['rows_S_qrad_qmatter']):
            geo=m.initial_geometry(1.,m.scale(D,S))
            for p in b['background_H_exponents_p']:
                for x in b['x_values']:
                    prefactor=x**(p-3)
                    writer.writerow([name,p,x,S,qr,qm,S*prefactor,qr/15*m.F(3+p-4,x)*prefactor,
                        b['matter_w']*qm/5*m.F(3+p-5,x)*prefactor,m.F(3+p-4,x),m.F(3+p-5,x),geo['Omega_sigma'],geo['relative_constraint_residual']])
    with (out/'SIGNED_WORK.csv').open('w',newline='') as f:
        writer=csv.writer(f);writer.writerow(['s_coefficient','q','cos_relative_axis_angle','P2','sigma_pi_rad_per_rho','sigma_pi_matter_per_rho','matter_w'])
        for s in (-b['epsilon_shear'],b['epsilon_shear']):
            for q in (-b['q_amplitude'],b['q_amplitude']):
                for cosine in b['angle_cosines']:
                    P2=(3*cosine*cosine-1)/2;work=2/5*s*q*P2
                    writer.writerow([s,q,cosine,P2,work,3*b['matter_w']*work,b['matter_w']])
    paths=[m.UNIT/'theory/BIANCHI_BENCHMARK_CONTRACT.json',m.UNIT/'theory/BIANCHI_I.md',
           m.UNIT/'theory/INITIAL_PROFILES.json',m.UNIT/'theory/INITIAL_CONDITIONS.md',
           Path(m.__file__),Path(__file__),m.UNIT/'implementation/CURRENT_INITIAL_VALUES.json']
    (out/'SOURCE_IDENTITIES.json').write_text(json.dumps({str(p.relative_to(m.UNIT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},indent=2)+'\n')


def main():
    out=m.UNIT/'outputs';out.mkdir(exist_ok=True)
    tests=unittest.defaultTestLoader.loadTestsFromTestCase(FormulaTests)
    result=unittest.TextTestRunner(verbosity=2).run(tests)
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,
            'failures':len(result.failures),'errors':len(result.errors),'relative_tolerance':RTOL,'absolute_tolerance':ATOL,
            'IVPs':0,'plots':0,'old_science_reruns':0,'arbitrary_abundance_floors':False,
            'claim':'Bounded initial-data and analytic tensor/response checks only; no isotope sensitivity trajectory',
            'response_density_normalization':'Responses report coefficients of kappa*rho/H0²; no cosmological density fractions inferred',
            'constraint_test_density':'rho=1 J/m³,Lambda=0 as arbitrary explicit algebraic fixture only; not selected cosmological model'}
    if result.wasSuccessful():write_products(out)
    (out/'FORMULA_TEST_RESULT.json').write_text(json.dumps(report,indent=2)+'\n')
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__=='__main__':main()
