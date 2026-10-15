"""Independent physics/numerical tests of source-locked PR154 photo plus
manufactured RR/CI rate bridge. Direct SciPy ODE is not the split implementation.
"""
from __future__ import annotations
import math
import random
import unittest
from dataclasses import replace
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import numpy as np
from scipy.integrate import solve_ivp
import source_aware as src
import thermal_bridge as m

MANUFACTURED = m.FrozenCoefficients(
    (9e-10,7e-10,6e-10), (3e-9,2e-9,1e-9), (.15,.25,.35))
NO_CI = m.FrozenCoefficients((9e-10,7e-10,6e-10),(0.,0.,0.),(.15,.25,.35))
ZERO = m.FrozenCoefficients((0.,0.,0.),(0.,0.,0.),(0.,0.,0.))

def state():
    return src.State((src.Node(20.,-.6,.25),src.Node(44.,.25,.19),
                     src.Node(80.,-.2,.14),src.Node(120.,.95,.17)),
                     src.Gas(.84,.16,.047,.022,.011))

def vector(photons:src.State, u, esc):
    return np.array([p.n_per_h for p in photons.photons]+list(photons.gas.__dict__.values())+[u,esc])

def independent_rhs(prior:src.State, rates:m.FrozenCoefficients,nh):
    """Compute *instantaneous unsplit* mass-action RHS from original Verner σ.

    Rates and geometry frozen, independent of exact pair formulas.
    """
    nodes=prior.photons
    energy=np.array([src.physical_energy(p,prior.a,prior.b) for p in nodes])
    k=np.array([[src.C_CM_S*nh*src.MB_CM2*src.verner_mb(i,ee)
                 for i in range(3)] for ee in energy])
    chi=np.array(src.CHI_EV)
    rr_kin=np.array(rates.rr_electron_kinetic_ev)
    ar=np.array(rates.alpha_rr_cm3_s)*nh
    be=np.array(rates.beta_ci_cm3_s)*nh
    def rhs(t,y):
        ns=y[:len(nodes)]
        hi,hii,hei,heii,heiii=y[len(nodes):len(nodes)+5]
        e=hii+heii+2*heiii
        absstock=np.array([hi,hei,heii])
        ionstock=np.array([hii,heii,heiii])
        photo=ns[:,None]*k*absstock[None,:]
        photo_by_i=photo.sum(axis=0)
        ci=be*e*absstock
        rr=ar*e*ionstock
        net=photo_by_i+ci-rr
        dn=-photo.sum(axis=1)
        gasdot=[-net[0],net[0],-net[1],net[1]-net[2],net[2]]
        du=float(np.sum(photo*(energy[:,None]-chi[None,:]))
                 -np.dot(ci,chi)-np.dot(rr,rr_kin))
        de=float(np.dot(rr,chi+rr_kin))
        return np.array([*dn,*gasdot,du,de])
    return rhs

class SourceIdentity(unittest.TestCase):
    def test_exact_immutable_PR154_git_blob(self):
        import hashlib
        data=Path(src.__file__).read_bytes()
        blob=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        self.assertEqual(blob,'db822a53da3ccdca7cf96628e9ef3bbcec83db5a')
    def test_physical_edge_binding_not_photo_fit(self):
        self.assertEqual(src.VERNER_ROWS[0][0],13.60)
        self.assertNotEqual(src.CHI_EV[0],13.60)
        self.assertEqual(len(src.CHI_EV),3)
    def test_source_provider_cannot_forge_physical_authority(self):
        with self.assertRaises(ValueError):
            m.FrozenCoefficients((0.,0.,0.),(0.,0.,0.),(0.,0.,0.),'REAL_GRACKLE')
    def test_no_injected_source_ownership(self):
        out,_,l=m.evolve_coupled_photo_thermal(state(),m.ThermalReservoir(100.),1e9,1e-3,MANUFACTURED)
        self.assertEqual(len(out.photons),len(state().photons))
        self.assertIn('NO_PHOTON_BIRTH',l.source_ownership)
        self.assertIn('NOT_ISSUED',l.recoil_owner)

class ExactSubflows(unittest.TestCase):
    def test_collisional_pair_ode(self):
        for n,e,k,dt in ((.1,.3,.04,4.),(.35,.000001,.8,2.),(.55,.6,2.,100.)):
            x,ev=m.exact_collisional_ionization(n,e,k,dt)
            v=solve_ivp(lambda t,y:[-k*y[0]*y[1],k*y[0]*y[1]],(0,dt),[n,e],
                         method='DOP853',rtol=2e-12,atol=1e-14)
            self.assertTrue(v.success)
            self.assertAlmostEqual(x,v.y[0,-1],delta=2e-10)
            self.assertAlmostEqual(n-x,ev,delta=2e-14)
            self.assertAlmostEqual(v.y[0,-1]+v.y[1,-1],n+e,delta=3e-10)
    def test_collisional_semigroup(self):
        for v in ((.6,.07,.03,4.),(.6,.9,2.,.8),(.00001,1.,.005,2.)):
            n,e,k,dt=v
            x,ev=m.exact_collisional_ionization(n,e,k,dt)
            h,evh=m.exact_collisional_ionization(n,e,k,dt/2)
            g,evg=m.exact_collisional_ionization(h,e+evh,k,dt/2)
            self.assertAlmostEqual(x,g,delta=3e-14)
            self.assertAlmostEqual(ev,evh+evg,delta=3e-14)
    def test_no_free_electrons_no_ci(self):
        self.assertEqual(m.exact_collisional_ionization(.2,0.,1.,100.),(.2,0.))
    def test_extreme_stiff_ci_and_positive(self):
        x,d=m.exact_collisional_ionization(.1,.1,3.,1e4)
        self.assertGreaterEqual(x,0.)
        self.assertAlmostEqual(d,.1,delta=1e-15)
    def test_invalid_rates_rejected(self):
        with self.assertRaises(ValueError): m.exact_collisional_ionization(.1,.1,-1.,2.)
        with self.assertRaises(ValueError): m.FrozenCoefficients((.1,-.01,0.),(0.,)*3,(0.,)*3)
        with self.assertRaises(ValueError): m.ThermalReservoir(-.1)
    def test_temperature_electron_census(self):
        g=state().gas
        w=1.5*m.KB_EV_K*1000*m.particles_per_h(g)
        self.assertAlmostEqual(m.temperature_k(g,w),1000.)
        self.assertAlmostEqual(m.electrons(g),g.h_ii+g.he_ii+2*g.he_iii)
    def test_recomb_requires_actual_electrons(self):
        gas=src.Gas(1.,0.,.08,0.,0.)
        st=src.State((),gas)
        out,t,l=m.evolve_coupled_photo_thermal(st,m.ThermalReservoir(5.),3e11,1e-3,MANUFACTURED)
        self.assertEqual(l.rr_events,(0.,0.,0.))
        self.assertEqual(l.ci_events,(0.,0.,0.))
        self.assertEqual(out,st)

class CoupledScientificLedger(unittest.TestCase):
    def run_case(self,substeps=16, dt=5e10, coeff=MANUFACTURED, thermal=100., geometry=None):
        params={} if geometry is None else geometry
        return m.evolve_coupled_photo_thermal(state(),m.ThermalReservoir(thermal),dt,1e-3,
                                                coeff,reaction_substeps=substeps,**params)
    def test_positive_H_He_electron_and_ledger(self):
        after,r,l=self.run_case()
        self.assertTrue(all(n.n_per_h>=0 for n in after.photons))
        self.assertTrue(all(v>=0 for v in after.gas.__dict__.values()))
        self.assertGreater(sum(l.rr_events),0.)
        self.assertGreater(sum(l.ci_events),0.)
        self.assertGreater(sum(l.photo_events),0.)
        self.assertLess(abs(l.total_energy_residual_ev_per_h),1e-11)
        self.assertLess(abs(l.photon_number_residual),3e-13)
        self.assertLess(abs(l.h_nuclei_residual),3e-14)
        self.assertLess(abs(l.he_nuclei_residual),3e-14)
        self.assertLess(abs(l.electron_charge_residual),3e-13)
        self.assertGreater(r.escape_ev_per_h,0.)
    def test_exact_photo_only_projection(self):
        st=state(); initial=m.ThermalReservoir(100.)
        a,r,l=m.evolve_coupled_photo_thermal(st,initial,1e10,1e-3,ZERO,
                                              reaction_substeps=12)
        b,p=src.evolve(st,1e10,1e-3,reaction_substeps=12)
        self.assertLess(max(abs(x.n_per_h-y.n_per_h) for x,y in zip(a.photons,b.photons)),1e-14)
        self.assertAlmostEqual(m.binding_energy(a.gas)-m.binding_energy(st.gas),p.binding_energy_ev,delta=1e-12)
        self.assertAlmostEqual(r.thermal_ev_per_h,100.+p.photoheat_ev,delta=1e-12)
        self.assertEqual(l.rr_events,(0.,0.,0.))
    def test_zero_duration_unchanged(self):
        st=state()
        a,r,l=m.evolve_coupled_photo_thermal(st,m.ThermalReservoir(15.),0.,1e-3,MANUFACTURED)
        self.assertEqual(st,a)
        self.assertEqual(l.rr_events,(0.,0.,0.))
        self.assertEqual(r,m.ThermalReservoir(15.))
    def test_thermal_budget_rejected_atomically(self):
        st=src.State((),src.Gas(.5,.5,.03,.04,.01))
        t=m.ThermalReservoir(0.)
        with self.assertRaises(m.InsufficientThermalEnergy):
            m.evolve_coupled_photo_thermal(st,t,1e11,1e-3,MANUFACTURED)
        self.assertEqual(st.gas.h_i,.5)
        self.assertEqual(t.thermal_ev_per_h,0.)
    def test_recomb_escape_is_bolometric_only(self):
        st=src.State((),src.Gas(.4,.6,.02,.04,.02))
        a,r,l=m.evolve_coupled_photo_thermal(st,m.ThermalReservoir(35.),1e11,1e-3,NO_CI)
        self.assertEqual(len(a.photons),0)
        self.assertGreater(r.escape_ev_per_h,0)
        self.assertGreater(sum(l.rr_events),0)
        self.assertLess(abs(l.total_energy_residual_ev_per_h),1e-11)
    def test_collisionless_geometry_work_single_owner(self):
        st=state();t=m.ThermalReservoir(100.)
        b,r,l=m.evolve_coupled_photo_thermal(st,t,0.,1e-3,MANUFACTURED,
                                               a_end=1.09,b_end=.04)
        self.assertAlmostEqual(l.total_energy_residual_ev_per_h,0.,delta=1e-12)
        self.assertEqual(b.nphot,st.nphot)
        self.assertAlmostEqual(l.geometric_work_ev_per_h,st.u_phot_ev-b.u_phot_ev,delta=1e-12)
        self.assertNotEqual(l.geometric_work_ev_per_h,0.)
    def test_second_order_vs_unsplit_ode(self):
        st=state();rate=MANUFACTURED;dt=4e10;nh=1e-3
        initial=m.ThermalReservoir(110.)
        Y0=vector(st,initial.thermal_ev_per_h,initial.escape_ev_per_h)
        ref=solve_ivp(independent_rhs(st,rate,nh),(0.,dt),Y0,
                      method='DOP853',rtol=5e-13,atol=3e-15)
        self.assertTrue(ref.success)
        errs=[]
        for sub in (1,2,4,8,16,32,64,128):
            y,u,l=m.evolve_coupled_photo_thermal(st,initial,dt,nh,rate,reaction_substeps=sub)
            err=float(np.max(np.abs(vector(y,u.thermal_ev_per_h,u.escape_ev_per_h)-ref.y[:,-1])))
            errs.append(err)
            self.assertLess(abs(l.total_energy_residual_ev_per_h),3e-11)
        self.assertGreater(errs[3]/errs[4],3.)
        self.assertGreater(errs[4]/errs[5],3.)
        self.assertGreater(errs[5]/errs[6],3.)
        self.assertGreater(errs[6]/errs[7],3.)
        self.assertLess(errs[-1],errs[0]/1000.)
    def test_random_nuclei_energy(self):
        rng=random.Random(20261016)
        for _ in range(100):
            hii=rng.uniform(.03,.9)
            he1=rng.uniform(0.,.08)
            he2=rng.uniform(0.,.08-he1)
            g=src.Gas(1-hii,hii,he1,he2,.08-he1-he2)
            nodes=tuple(src.Node(rng.uniform(15.,200.),rng.uniform(-1.,1.),rng.uniform(0.,.08))
                        for _ in range(3))
            st=src.State(nodes,g)
            out,t,l=m.evolve_coupled_photo_thermal(st,m.ThermalReservoir(400.),1e9,1e-3,
                                                    MANUFACTURED,reaction_substeps=3)
            self.assertGreaterEqual(t.thermal_ev_per_h,0)
            self.assertLess(abs(l.total_energy_residual_ev_per_h),3e-10)
            self.assertLess(abs(l.photon_number_residual),2e-13)
            self.assertLess(abs(l.electron_charge_residual),2e-13)
            self.assertLess(abs(l.h_nuclei_residual),3e-14)
            self.assertLess(abs(l.he_nuclei_residual),3e-14)
    def test_strong_photo_he_ions(self):
        g=src.Gas(1.,0.,.08,0.,0.)
        st=src.State((src.Node(80.,.1,.2),),g)
        result,thermo,l=m.evolve_coupled_photo_thermal(st,m.ThermalReservoir(50.),2e10,1e-3,
                                                       MANUFACTURED,reaction_substeps=32)
        self.assertGreater(result.gas.he_iii,0.)
        self.assertGreater(l.photo_events[1],0.)
        self.assertGreater(l.photo_events[2],0.)
        self.assertAlmostEqual(result.gas.he_total,.08,delta=2e-14)
    def test_continuum_domain_covers_reference_rates(self):
        for sidx in range(3):
            self.assertGreater(MANUFACTURED.alpha_rr_cm3_s[sidx],0.)
            self.assertGreater(MANUFACTURED.beta_ci_cm3_s[sidx],0.)
            self.assertLess(MANUFACTURED.rr_electron_kinetic_ev[sidx],1.)

if __name__=='__main__':
    unittest.main(verbosity=2)