"""Scientific tests for bounded source-age LRS reference, not native EoR."""
import math
import unittest
from dataclasses import replace
import numpy as np
from scipy.integrate import quad
from age_transport import (Model,SPECIES,CHI,BINDING_EV,sigma_mb,ray_geometry,hazards,
    geometric_loss_rate,photon_events,integrate_ray,reference_ray,integrate_source,
    source_free_sharp_pi_bounds,source_free_pressure,age_event_boundaries,
    positive_blackbody_nodes,integrate_spectral_source,adaptive_birth_age_source,
    terminal_angular_panels,integrate_angular_event_source)

class VernerAndGeometry(unittest.TestCase):
    def test_thresholds_and_gating(self):
        self.assertEqual(CHI,(13.6,24.59,54.42))
        for name,chi in zip(SPECIES,CHI):
            self.assertEqual(sigma_mb(name,chi-1e-6),0.)
            self.assertGreater(sigma_mb(name,chi),0.)
    def test_native_binding_not_rounded_fit_threshold(self):
        # The Verner switch-on energy and the actual chemical binding owner
        # are distinct. Treating them as identical gives spurious photoheat.
        self.assertTrue(all(c>e for c,e in zip(CHI,BINDING_EV)))
        for i,(species,threshold) in enumerate(zip(SPECIES,CHI)):
            self.assertGreater(threshold-BINDING_EV[i],0.)
            self.assertGreater(sigma_mb(species,threshold),0.)
    def test_invalid_fit_domain(self):
        with self.assertRaises(ValueError):sigma_mb('HI',60000.)
        with self.assertRaises(ValueError):sigma_mb('HI',-1.)
    def test_exact_geodesic_birth(self):
        for mu in (-1.,-.3,0.,.4,1.):
            for y in (.0,.3,.6):
                E,mu2=ray_geometry(Model(),y,y,mu)
                self.assertAlmostEqual(E,82.)
                self.assertAlmostEqual(mu2,mu*mu)
    def test_flrw_angular_equal_energy(self):
        m=Model(signed_v0=0.)
        for mu in (-1.,0.,1.):
            E,_=ray_geometry(m,0,.4,mu)
            self.assertAlmostEqual(E,m.e_birth_ev*math.exp(-.4),delta=5e-14)
    def test_exact_signed_axis_scaling(self):
        m=Model(signed_v0=.06)
        for y in (0.,.1,.3):
            x=.7;d=m.b(x)-m.b(y)
            self.assertAlmostEqual(ray_geometry(m,y,x,0.)[0],82.*math.exp(y-x+d))
            self.assertAlmostEqual(ray_geometry(m,y,x,1.)[0],82.*math.exp(y-x-2*d))
    def test_energy_derivative_against_finite_difference(self):
        m=Model(signed_v0=-.04,b_osc_amp=.013,b_osc_freq=9.)
        for y in (0.,.1):
            for mu in (0.,.3,1.):
                x=.5;h=1e-5
                fd=(ray_geometry(m,y,x-h,mu)[0]-ray_geometry(m,y,x+h,mu)[0])/(2*h)
                self.assertAlmostEqual(fd,geometric_loss_rate(m,y,x,mu),delta=1e-7)
    def test_signed_rate_can_be_negative(self):
        m=Model(signed_v0=0.,b_osc_amp=.25,b_osc_freq=18.)
        vals=[geometric_loss_rate(m,0,float(x),0.) for x in np.linspace(0,.7,40)]
        self.assertLess(min(vals),0.)
        self.assertGreater(max(vals),0.)
    def test_absorber_hazards_nonnegative(self):
        m=Model()
        for y in (0.,.17,.38):
            for x in np.linspace(y,.7,8):
                self.assertTrue(all(v>=0 for v in hazards(m,y,float(x),.4)))
    def test_threshold_root_alignment(self):
        m=Model()
        edges=photon_events(m,0.,.4)
        self.assertGreater(len(edges),2)
        chi=CHI[2]
        self.assertAlmostEqual(ray_geometry(m,0,edges[1],.4)[0],chi,delta=2e-11)
    def test_multiple_crossings_geometry(self):
        m=Model(signed_v0=0.,b_osc_amp=.22,b_osc_freq=18.)
        cuts=photon_events(m,0.,1.,scan=768)
        self.assertGreaterEqual(len(cuts),6)
        self.assertEqual(cuts[0],0.)
        self.assertEqual(cuts[-1],m.x_end)

class SharpSourceAge(unittest.TestCase):
    def test_source_integral_exact(self):
        m=Model()
        self.assertAlmostEqual(quad(m.source,0,m.x_end,epsabs=1e-13)[0],m.x_end)
    def test_sharp_envelope_attained(self):
        for v in (-.05,0.,.045):
            m=Model(signed_v0=v)
            low,hi=source_free_sharp_pi_bounds(m)
            self.assertAlmostEqual(source_free_pressure(m,0.),low,delta=2e-12)
            self.assertAlmostEqual(source_free_pressure(m,1.),hi,delta=2e-12)
    def test_sharp_envelope_bounds_all_positive_even_skies(self):
        for b0 in (-.12,0.,.15):
            m=Model(signed_v0=b0,b_osc_amp=.01,b_osc_freq=4.)
            low,hi=source_free_sharp_pi_bounds(m)
            for mu in np.linspace(-1.,1.,17):
                val=source_free_pressure(m,float(mu))
                self.assertLessEqual(val,hi+2e-11)
                self.assertGreaterEqual(val,low-2e-11)
    def test_two_independent_age_quadratures(self):
        m=Model(signed_v0=.06,b_osc_amp=.018,b_osc_freq=8.)
        l,h=source_free_sharp_pi_bounds(m)
        l2,h2=source_free_sharp_pi_bounds(m,method='gl',n_age=32)
        self.assertAlmostEqual(l,l2,delta=5e-12)
        self.assertAlmostEqual(h,h2,delta=5e-12)

class SourceAbsorption(unittest.TestCase):
    def test_ray_count_and_energy(self):
        m=Model()
        for y in (0.,.1,.4):
            for mu in (0.,.4,1.):
                q=integrate_ray(m,y,mu,n_time=32)
                self.assertGreaterEqual(q.survivor,0.)
                self.assertTrue(all(v>=0. for v in q.absorbed))
                self.assertGreaterEqual(q.heat_ev,0.)
                self.assertLess(abs(q.photon_residual),3e-14)
                self.assertLess(abs(q.energy_residual),1e-11)
    def test_ray_independent_ode(self):
        m=Model()
        for y,mu in [(0.,0.),(.08,.7),(.21,1.)]:
            actual=integrate_ray(m,y,mu,n_time=128)
            direct=reference_ray(m,y,mu,n_time=32)
            self.assertLess(abs(actual.survivor-direct.survivor),5e-5)
            self.assertLess(abs(actual.heat_ev-direct.heat_ev),2e-3)
    def test_source_integrated_ledgers_signed(self):
        for v in (-.04,0.,.04):
            m=Model(signed_v0=v)
            r=integrate_source(m,8,8,n_time=24)
            self.assertAlmostEqual(r.emitted_photons,.7,delta=1e-12)
            self.assertLess(abs(r.photon_residual),1e-12)
            self.assertLess(abs(r.energy_residual),1e-10)
            self.assertGreaterEqual(r.survivors,0.)
            self.assertTrue(all(a>=0. for a in r.absorbed))
    def test_flrw_no_generated_stress(self):
        m=Model(signed_v0=0.)
        for mu in (4,8,12):
            a=integrate_source(m,6,mu,20)
            self.assertLess(abs(a.final_pi_ev),2e-11)
    def test_reflection_symmetry(self):
        m=Model(signed_v0=.05)
        for y in (0.,.25):
            left=integrate_ray(m,y,.6)
            right=integrate_ray(m,y,-.6)
            self.assertEqual(left,right)
    def test_event_aware_age_splits(self):
        m=Model(signed_v0=.04)
        panels=age_event_boundaries(m,[-1.,0.,1.])
        self.assertGreater(len(panels),2)
        self.assertEqual(panels[0],0.)
        self.assertEqual(panels[-1],m.x_end)
    def test_no_opacity_is_exact_source_free(self):
        m=Model(kappa_th=(0.,0.,0.))
        r=integrate_source(m,6,10,n_time=8)
        self.assertEqual(r.absorbed,(0.,0.,0.))
        self.assertAlmostEqual(r.survivors,r.emitted_photons,delta=5e-14)
        self.assertAlmostEqual(r.final_pi_ev,0.,delta=2e-10) if m.signed_v0==0 else None
    def test_multicrossing_positive_and_reference(self):
        m=Model(signed_v0=0.,b_osc_amp=.22,b_osc_freq=18.)
        a=integrate_ray(m,0.,1.,n_time=128,scan=768)
        b=reference_ray(m,0.,1.,n_time=64,scan=768)
        self.assertGreater(a.event_count,3)
        self.assertLess(abs(a.survivor-b.survivor),2e-4)
        self.assertLess(abs(a.energy_residual),2e-11)
        self.assertLess(abs(b.energy_residual),5e-8)
    def test_spectral_weights_positive(self):
        nodes=positive_blackbody_nodes(8)
        self.assertTrue(all(e>0 and w>0 for e,w in nodes))
        self.assertAlmostEqual(sum(w for _,w in nodes),1.)
    def test_spectral_three_axes(self):
        m=Model()
        a=integrate_spectral_source(m,8,4,6,12)
        self.assertGreater(a.ray_calls,60)
        self.assertLess(abs(a.photon_residual),1e-11)
        self.assertLess(abs(a.energy_residual),5e-10)
        self.assertGreater(a.absorbed[0],0.)
        self.assertGreater(a.absorbed[1],0.)
        self.assertGreater(a.absorbed[2],0.)
    def test_embedded_adaptive_age_positive_and_conservative(self):
        m=Model()
        a=adaptive_birth_age_source(m,8,32,rtol=1e-4,atol=1e-6)
        self.assertTrue(a.result.ray_calls>0)
        self.assertTrue(all(x>=0 for x in a.result.absorbed))
        self.assertLess(abs(a.result.photon_residual),2e-12)
        self.assertLess(abs(a.result.energy_residual),5e-10)

    def test_adaptive_vs_global_age_reference(self):
        m=Model()
        a=adaptive_birth_age_source(m,8,64,rtol=1e-5,atol=1e-7)
        b=integrate_source(m,240,8,64)
        self.assertLess(abs(a.result.absorbed[2]-b.absorbed[2]),1e-7)
        self.assertLess(a.result.ray_calls,b.ray_calls)

    def test_adaptive_stricter_tolerance_never_fewer_calls(self):
        m=Model()
        loose=adaptive_birth_age_source(m,6,20,rtol=1e-3,atol=1e-5)
        tight=adaptive_birth_age_source(m,6,20,rtol=1e-6,atol=1e-8)
        self.assertGreaterEqual(tight.result.ray_calls,loose.result.ray_calls)

    def test_adaptive_bad_budgets_rejected(self):
        with self.assertRaises(ValueError):adaptive_birth_age_source(Model(),4,8,rtol=0)
        with self.assertRaises(ValueError):adaptive_birth_age_source(Model(),4,8,max_depth=0)

    def test_angular_zero_shear_with_adaptive_ages(self):
        a=adaptive_birth_age_source(Model(signed_v0=0.),8,32,rtol=1e-4)
        self.assertLess(abs(a.result.final_pi_ev),1e-11)

    def test_terminal_angular_cut_closed_form(self):
        m=Model(signed_v0=.04)
        cuts=terminal_angular_panels(m,.29)
        self.assertEqual(len(cuts),4)
        mu=cuts[2]
        E,_=ray_geometry(m,.29,m.x_end,mu)
        self.assertAlmostEqual(E,CHI[2],delta=3e-12)

    def test_event_angle_split_keeps_flrw_isotropy(self):
        m=Model(signed_v0=0.)
        q=integrate_angular_event_source(m,5,8,32)
        self.assertLess(abs(q.final_pi_ev),2e-11)
        self.assertEqual(q.age_panels,5)

    def test_event_angle_source_preserves_ledgers(self):
        m=Model(signed_v0=.04)
        q=integrate_angular_event_source(m,10,8,32)
        self.assertLess(abs(q.photon_residual),1e-12)
        self.assertLess(abs(q.energy_residual),2e-10)
        self.assertGreater(q.age_panels,10)

    def test_negative_inputs_rejected(self):
        with self.assertRaises(ValueError):Model(kappa_th=(1.,-.1,0.))
        with self.assertRaises(ValueError):integrate_ray(Model(),.1,.4,n_time=0)
        with self.assertRaises(ValueError):positive_blackbody_nodes(1)

if __name__=='__main__':unittest.main()
