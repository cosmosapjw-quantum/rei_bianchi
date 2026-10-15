"""Direct BASS160+original Lewis-Challinor source regressions for PR137."""
from __future__ import annotations
import hashlib
import itertools
import math
import os
from pathlib import Path
import sys

import numpy as np
import pytest

HERE=Path(__file__).resolve().parent
PR137=HERE.parent
sys.path.insert(0,str(PR137))
sys.path.insert(0,str(HERE))
from massive_radial import MassiveRadialGrid,MassiveRadialSpecies,scalar_hierarchy_rhs
from species_hierarchy import SpeciesHierarchy
from run_hierarchy import source_lock,public_sigma_from_q

BASS160_ROOT=Path(os.environ.get("BASS160_ROOT",
  "/home/cosmosapjw/rec_theory_runs/BASS_PR160_PINNED_20261015/checkout"))
EXPECTED_BASS_SHA="1857567475b1c8586298f868e5420aae7a72e8e1ba69cce6a5b21bfca4fdd790"


def source_BASS160():
    fn=BASS160_ROOT/"research/rei_axbi_sigma_matter_20261015/sigma_matter.py"
    if not fn.is_file():pytest.skip("original BASS PR160 pinned source unavailable")
    assert hashlib.sha256(fn.read_bytes()).hexdigest()==EXPECTED_BASS_SHA
    sys.path.insert(0,str(BASS160_ROOT))
    sys.path.insert(0,str(fn.parent))
    import sigma_matter
    return sigma_matter


def source_H():
    sys.path.insert(0,str(BASS160_ROOT))
    from bianchi.matter import hierarchy as H,freestream as FS
    return H,FS


def positive_f0(A,fs):
    def f(q,nh):
        return fs.f_fermi_dirac(q)[:,None]*(1+A*(3*nh[:,2]**2-1)/2)[None,:]
    return f


def STF4_z():
    eye=np.eye(3);z=np.array([0.,0.,1.])
    a=np.empty((3,3,3,3))
    for i,j,k,l in itertools.product(range(3),repeat=4):
        a[i,j,k,l]=(
            z[i]*z[j]*z[k]*z[l]
            -(eye[i,j]*z[k]*z[l]+eye[i,k]*z[j]*z[l]+
              eye[i,l]*z[j]*z[k]+eye[j,k]*z[i]*z[l]+
              eye[j,l]*z[i]*z[k]+eye[k,l]*z[i]*z[j])/7
            +(eye[i,j]*eye[k,l]+eye[i,k]*eye[j,l]+
              eye[i,l]*eye[j,k])/35
        )
    return a


def test_source_BASS160_exact_moments_three_angles():
    upstream=source_BASS160()
    grid=MassiveRadialGrid(30,96,32)
    original=upstream.MassiveMoments(30.,angular_n=32)
    for x,b,A in [(0.,0.,.5),(.15,.002,-.4),(.8,-.009,.8)]:
        J=grid.moments(x,b,A,4)
        E,PP,PA=original.evaluate(x,b,A)
        np.testing.assert_allclose([J.j0[0],J.j0[1]/3,J.j2[0]/3],
             [E,(2*PP+PA)/3,(PA-PP)/3],rtol=5e-12,atol=5e-17)
        assert J.j0[0]>0 and 0<J.j0[1]<J.j0[0]


def test_original_BASS_massive_i0_i2_i4_tensors_nonzero_seed():
    H,FS=source_H()
    grid=MassiveRadialGrid(30,96,32)
    x=.26;b=.005;A=.4
    a=np.exp([x-b,x-b,x+2*b])
    f=positive_f0(A,FS)
    norm=H.J_moment([1,1,1],30.,0,0,f,backend="python")
    J=grid.moments(x,b,A,4)
    for i in range(4):
        J0=H.J_moment(a,30.,0,i,f,backend="python")/norm
        J2=H.J_moment(a,30.,2,i,f,backend="python")[2,2]*1.5/norm
        assert J.j0[i]==pytest.approx(J0,rel=8e-12)
        assert J.j2[i]==pytest.approx(J2,rel=8e-12,abs=3e-15)
    for i in range(3):
        J4=H.J_moment(a,30.,4,i,f,backend="python")[2,2,2,2]*(35/8)/norm
        assert J.j4[i]==pytest.approx(J4,rel=1e-8,abs=3e-15)


def test_exact_LRS_scalar_rhs_vs_original_BASS_Eq12_tensor():
    H,FS=source_H()
    stf2=np.diag([-1/3,-1/3,2/3])
    stf4=STF4_z()
    grid=MassiveRadialGrid(15,96,32)
    for x,b,A,s in [(.03,.003,.2,.02),(.6,-.017,-.4,-.015)]:
        moments=grid.moments(x,b,A,5)
        sigma=np.diag([-s,-s,2*s])
        for i in range(3):
            lhs0,lhs2=scalar_hierarchy_rhs(
              moments.j0,moments.j2,moments.j4,1.3,s,i
            )
            D={}
            for k in range(i+3):
                D[(0,k)]=moments.j0[k]
                D[(2,k)]=moments.j2[k]*stf2
                D[(4,k)]=moments.j4[k]*stf4
            b0=float(H.hierarchy_rhs(D,1.3,sigma,0,i))
            b2=H.hierarchy_rhs(D,1.3,sigma,2,i)[2,2]*1.5
            assert lhs0[i]==pytest.approx(b0,rel=3e-13,abs=3e-14)
            assert lhs2[i]==pytest.approx(b2,rel=3e-13,abs=3e-14)


def test_radial_characteristic_energy_and_full_moment_derivative():
    grid=MassiveRadialGrid(30,96,32)
    for x,b,A,v in [(.03,.002,.5,.009),(.5,-.01,-.7,-.005),
                     (1.1,.02,.2,.004)]:
        d=1e-5
        p=grid.moments(x+d,b+v*d,A,4)
        m=grid.moments(x-d,b-v*d,A,4)
        c=grid.moments(x,b,A,4)
        expect0,expect2=scalar_hierarchy_rhs(
            c.j0,c.j2,c.j4,1.,v,2)
        np.testing.assert_allclose((p.j0[:3]-m.j0[:3])/(2*d),
                                   expect0,rtol=5e-9,atol=5e-12)
        np.testing.assert_allclose((p.j2[:3]-m.j2[:3])/(2*d),
                                   expect2,rtol=1e-7,atol=3e-12)
        # Energy-momentum conservation exact for source massive species.
        assert expect0[0]==pytest.approx(
          -3*(c.j0[0]+c.j0[1]/3)-2*v*c.j2[0],rel=3e-14)


def test_matter_fraction_baryon_protection_and_isotropic_limit():
    s=source_lock()
    kwargs=dict(Sigma_ref=0.,orientation=0,kappa_gamma=.2,kappa_nu=.2)
    with pytest.raises(ValueError,match="baryonic Omega_m"):
        MassiveRadialSpecies(s,2.7255,**kwargs,mass_fraction=.9999)
    with pytest.raises(ValueError,match="positive W"):
        MassiveRadialSpecies(s,2.7255,**kwargs,massive_A=3.)
    for mass in (3.,30.,300.):
        model=MassiveRadialSpecies(s,2.7255,**kwargs,
                        mass_fraction=.1,mass_over_T_ref=mass,massive_A=0.)
        v=model.fields(0,model.initial_state())
        old=SpeciesHierarchy(s,2.7255,8,**kwargs).fields(
             0,SpeciesHierarchy(s,2.7255,8,**kwargs).initial_state())
        assert v["massive_energy_norm"]==pytest.approx(s.omega_m*.1/s.aref**3)
        assert v["Pi_matter_J_m3"]==pytest.approx(0.,abs=5e-23)
        assert v["H"]==pytest.approx(old["H"],rel=2e-15)


@pytest.mark.parametrize("fm,Am",[(0.,.0),(.1,.5),(.1,-.3)])
def test_actual_evolved_radial_index_towers_match_exact_momentum_characteristic(fm,Am):
    s=source_lock()
    model=MassiveRadialSpecies(s,2.7255,Sigma_ref=0.,orientation=0,
           kappa_gamma=.2,kappa_nu=.2,mass_fraction=fm,massive_A=Am,
           imax=2)
    sol,ds,_=model.integrate(81,rtol=2e-11,atol=1e-13)
    assert sol.success
    maxdiff=0.
    for i in range(0,len(sol.t),5):
        state=ds[i]["exact_radial_towers"]
        off=model.main_size;n=3
        err=np.max(abs(sol.y[off:off+n,i]-state.j0[:3]))
        err2=np.max(abs(sol.y[off+n:off+2*n,i]-state.j2[:3]))
        maxdiff=max(maxdiff,err,err2)
    assert maxdiff<8e-10
    assert abs(ds[-1]["N_gamma"][0]-1)<1e-12
    assert abs(ds[-1]["N_nu"][0]-1)<1e-12


def test_actual_source_Thomson_and_massive_backreaction_do_not_overlap():
    from run_hierarchy import actual_electrons
    source=source_lock()
    donor,_=actual_electrons(Path.home()/"Dropbox/bianchi/rei_bianchi")
    configs=dict(Sigma_ref=0.,orientation=0,
                 kappa_gamma=.2,kappa_nu=.2,mass_fraction=.1,
                 massive_A=.5)
    new=MassiveRadialSpecies(source,2.7255,ne_source=donor,**configs)
    pre=MassiveRadialSpecies(source,2.7255,ne_source=None,**configs)
    s1,d1,_=new.integrate(81)
    s0,d0,_=pre.integrate(81)
    assert d1[-1]["E_gamma"][2]<d0[-1]["E_gamma"][2]
    assert abs(d1[-1]["E_nu"][2]-d0[-1]["E_nu"][2])<2e-5
    assert d1[-1]["Pi_matter_J_m3"]>0
    assert d1[-1]["Pi_matter_J_m3"]/d1[-1]["Pi_radiation_J_m3"]>0
    assert d1[-1]["Sigma"]!=d0[-1]["Sigma"]


def test_bounded_radial_batch_same_scalar_reference():
    grid=MassiveRadialGrid(30,96,32)
    x=np.linspace(0,1.35,137)
    b=np.sin(x)*.015
    dense=grid.batch(x,b,.5,imax=2,chunk=31)
    ref=np.array([
        [grid.moments(float(a),float(z),.5,2).j0,
         grid.moments(float(a),float(z),.5,2).j2,
         grid.moments(float(a),float(z),.5,2).j4]
        for a,z in zip(x,b)
    ])
    np.testing.assert_allclose(dense,ref,rtol=5e-13,atol=2e-15)


def test_independent_original_BASS160_full_Einstein_Vlasov_limit():
    """PR137 gamma+nu == one massless radiation source with no Thomson.

    When kappa_gamma==kappa_nu, their split brightness is identical,
    hence this NEW coupled gravity must reproduce ORIGINAL BASS PR160
    exact massless and finite-mass Vlasov with the same Omegas and
    initial amplitudes. This code NEVER feeds original BASS tables
    or metric values as ODE data.
    """
    b=source_BASS160()
    cfg=b.InitialStress(0.,1,1.,.2,.1,.5,30.)
    reference=b.EinsteinVlasovSigmaMatter(cfg)
    target=reference.at_x(reference.xmax)
    m=MassiveRadialSpecies(source_lock(),2.7255,8,
        Sigma_ref=0.,orientation=0,kappa_gamma=.2,kappa_nu=.2,
        mass_fraction=.1,massive_A=.5,mass_over_T_ref=30.,
        ne_source=None)
    sol,values,_=m.integrate(101,rtol=2e-11,atol=1e-13)
    end=values[-1]
    assert abs(sol.y[1,-1]-target["b"])<2e-12
    assert abs(end["Sigma"]-target["Sigma"])<2e-12
    assert abs(end["Pi_matter_J_m3"]-target["Pi_m_J_m3"])/abs(target["Pi_m_J_m3"])<2e-8
    assert abs(end["Pi_radiation_J_m3"]-target["Pi_r_J_m3"])<1e-22


def test_independent_Raychaudhuri_constraint_for_evolving_massive_and_photons():
    s=source_lock()
    model=MassiveRadialSpecies(s,2.7255,8,Sigma_ref=0.,
        orientation=0,kappa_gamma=.2,kappa_nu=.2,mass_fraction=.1,
        massive_A=.5,mass_over_T_ref=30.)
    sol,_,_=model.integrate(101)
    for x in (.05,.32,.84,s.xmax-.05):
        yy=np.array([np.interp(x,sol.t,sol.y[k]) for k in range(len(sol.y))])
        # Use an exactly solved point as finite-difference seed would be
        # ideal. The tiny interpolation error enters only the state, not
        # its exact instantaneous Einstein derivative identity.
        F=model.fields(x,yy)
        dy=model.rhs(x,yy)
        h=1e-5
        p=model.fields(x+h,yy+h*dy)
        n=model.fields(x-h,yy-h*dy)
        observed=(p["H"]**2-n["H"]**2)/(2*h)
        rest=F["dust_energy_norm"]
        rad=F["rad_energy_norm"]
        e=F["massive_energy_norm"]
        pbar=F["massive_mean_pressure_norm"]
        S=F["s"]
        predicted=-(s.h0**2)*(3*rest+4*rad+3*(e+pbar))-6*S*S
        assert abs(observed-predicted)/abs(predicted)<4e-8


def test_hierarchy_state_is_actual_gravity_owner_not_passive_regressor():
    src=source_lock()
    active=MassiveRadialSpecies(src,2.7255,8,Sigma_ref=0.,
         orientation=0,kappa_gamma=.2,kappa_nu=.2,
         mass_fraction=.1,massive_A=.5,gravity_owner="hierarchy")
    passive=MassiveRadialSpecies(src,2.7255,8,Sigma_ref=0.,
         orientation=0,kappa_gamma=.2,kappa_nu=.2,
         mass_fraction=.1,massive_A=.5,gravity_owner="exact_vlasov")
    y=active.initial_state()
    # Deliberate temporary perturbation demonstrates that source ownership
    # is correctly wired. This is a negative numerical control, not a
    # legitimate independently initialized physical distribution.
    yp=y.copy()
    yp[active.main_size]*=1.01
    yp[active.main_size+active.imax+1]*=1.01
    a=active.fields(0.,yp)
    p=passive.fields(0.,yp)
    assert a["H"]>p["H"]
    assert a["Pi_matter_J_m3"]>p["Pi_matter_J_m3"]
    assert a["gravity_owner"]=="hierarchy"
    assert p["gravity_owner"]=="exact_vlasov"
    sol,_,_=active.integrate(91)
    ctrl,_,_=passive.integrate(91)
    assert abs(sol.y[1,-1]-ctrl.y[1,-1])<1e-9
