"""Independent source verification of collisionless canonical-cell Vlasov.

Runs original BASS PR160 MassiveMoments and original PR140 source-assisted
hierarchy, plus direct component continuity and Raychaudhuri identities.
"""
import math
import sys
from pathlib import Path
import numpy as np
import pytest

HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(PARENT))
from canonical_fv import CanonicalMomentumFV,CanonicalFVSpecies
from massive_radial import MassiveRadialGrid,MassiveRadialSpecies
from run_hierarchy import source_lock,public_sigma_from_q
from species_hierarchy import SpeciesHierarchy

BASS=Path("/home/cosmosapjw/rec_theory_runs/BASS_PR160_PINNED_20261015/checkout")


def test_cells_strict_positivity_quadrature_normalization_and_no_flux():
    for A in (-1.,-.5,0.,.5,2.):
        cells=CanonicalMomentumFV(30.,A,24,12)
        assert cells.cell_numbers.shape==(24,12)
        assert cells.packet_count==4*24*12
        assert np.all(cells.cell_numbers>=0)
        assert cells.total_cell_number>0
        assert not cells.cell_numbers.flags.writeable
        assert np.max(np.abs(cells.distribution_change_deta()))==0
        begin=cells.moments(0.,0.)
        assert abs(begin.rho-1)<5e-15
        later=cells.moments(.7,.02)
        assert later.ncell_number==pytest.approx(
            cells.total_cell_number*math.exp(-2.1),rel=1e-15)
        assert later.rho>later.pressure_perp+later.pressure_parallel
        assert later.pressure_parallel>=0 and later.pressure_perp>=0
        assert abs(later.delta_p)<=2*later.pbar*(1+1e-13)


@pytest.mark.parametrize("invalid",[-1.0001,2.0001,float("nan")])
def test_negative_source_is_rejected(invalid):
    with pytest.raises(ValueError):
        CanonicalMomentumFV(30.,invalid)


@pytest.mark.parametrize("mass", [3.,30.,300.])
@pytest.mark.parametrize("A",[-.7,0.,.5])
def test_original_BASS160_fd_mass_shell_original_source_convergence(mass,A):
    sys.path.insert(0,str(BASS/"research/rei_axbi_sigma_matter_20261015"))
    sys.path.insert(0,str(BASS))
    from sigma_matter import MassiveMoments
    src=MassiveMoments(mass,angular_n=64)
    for x,b in ((0.,0.),(.25,.004),(.8,-.017)):
        expected=np.array(src.evaluate(x,b,A))
        values={}
        for nr,nmu,order in ((16,8,2),(32,16,2),(32,16,3)):
            m=CanonicalMomentumFV(mass,A,nr,nmu,gauss_order=order).moments(x,b)
            values[(nr,order)]=np.array([m.rho,m.pressure_perp,m.pressure_parallel])
        # Upgrade cell-local quadrature order when relativistic mass needs
        # it; use fewer cells, not a weakened source accuracy gate.
        e=np.max(np.abs(values[(32,3)]-expected))
        assert e<5e-10
        assert e < max(1e-15,np.max(abs(values[(16,2)]-expected))) *1.01
        assert np.all(values[(32,3)]>0)


def test_exact_component_massive_continuity_and_shear_work():
    for mass,A in [(3.,-.5),(30.,.5),(300.,.2)]:
        obj=CanonicalMomentumFV(mass,A,40,20)
        for eta,b in ((.03,.002),(.5,-.01),(1.0,.02)):
            h=3e-6
            first=obj.moments(eta,b)
            dx=(obj.moments(eta+h,b).rho-
                obj.moments(eta-h,b).rho)/(2*h)
            db=(obj.moments(eta,b+h).rho-
                obj.moments(eta,b-h).rho)/(2*h)
            analytic_dx=-3*(first.rho+first.pbar)
            analytic_db=-2*first.delta_p
            assert abs(dx-analytic_dx)/abs(analytic_dx)<2e-10
            assert abs(db-analytic_db)/max(first.rho,1e-150)<2e-10
            # LRS sigma:pi=2*s*DeltaP; the sector work is not dropped.
            v=.005
            conv=dx+v*db
            assert abs(conv+3*(first.rho+first.pbar)+2*v*first.delta_p)<1e-8


def test_zero_massive_fraction_recovers_PR137_source_without_injection():
    s=source_lock()
    sig,eps=public_sigma_from_q(.01)
    kw=dict(Sigma_ref=sig,orientation=eps,kappa_gamma=.2,kappa_nu=.2)
    new=CanonicalFVSpecies(s,2.7255,8,**kw,mass_fraction=0.)
    ref=SpeciesHierarchy(s,2.7255,8,**kw)
    y=new.initial_state()
    np.testing.assert_allclose(new.rhs(0.,y),ref.rhs(0.,y),rtol=1e-13,atol=5e-15)
    # Compare identical solver configurations, not PR137's different
    # stricter default rtol=2e-12 to the FV default rtol=3e-11.
    sol,seq,_=new.integrate(81,rtol=3e-11,atol=3e-13)
    old,ot,_=ref.integrate(81,rtol=3e-11,atol=3e-13)
    np.testing.assert_array_equal(sol.y,old.y)


def test_actual_geometry_and_Killing_population_owners_sign_sources():
    s=source_lock()
    for A,positive in [(.5,True),(-.5,False)]:
        obj=CanonicalFVSpecies(s,2.7255,8,
            Sigma_ref=0.,orientation=0,kappa_gamma=.2,kappa_nu=.2,
            mass_fraction=.1,massive_A=A,radial_cells=32,angular_cells=16)
        ini=obj.fields(0,obj.initial_state())
        assert ini["massive_min_cell_population"]>=0
        assert ini["massive_energy_norm"]==pytest.approx(
            .1*s.omega_m/s.aref**3,rel=1e-14)
        assert (ini["Pi_matter_J_m3"]>0)==positive
        sol,diagnostics,_=obj.integrate(81)
        assert sol.success and sol.nfev>10
        assert diagnostics[-1]["Sigma"]>0
        assert all(abs(u["massive_number_cell_sum"]-ini["massive_number_cell_sum"])
                   <1e-14 for u in diagnostics)
        assert all(u["massive_min_cell_population"]>=0 for u in diagnostics)
        assert abs(diagnostics[-1]["N_gamma"][0]-1)<2e-12
        assert abs(diagnostics[-1]["N_nu"][0]-1)<2e-12


def test_independent_source_assisted_PR140_convergence_actual_Einstein():
    s=source_lock()
    k=dict(Sigma_ref=0.,orientation=0,kappa_gamma=.2,kappa_nu=.2,
           mass_fraction=.1,massive_A=.5,mass_over_Tref=30.)
    model=MassiveRadialSpecies(s,2.7255,8,
        mass_over_T_ref=30.,Sigma_ref=0.,orientation=0,
        kappa_gamma=.2,kappa_nu=.2,
        mass_fraction=.1,massive_A=.5)
    t,prev,_=model.integrate(81,rtol=2e-11,atol=1e-13)
    ref=prev[-1]["Sigma"]
    err=[]
    for n,a in [(16,8),(32,16),(64,32)]:
        fv=CanonicalFVSpecies(s,2.7255,8,**k,radial_cells=n,angular_cells=a)
        so,seq,_=fv.integrate(81,rtol=2e-11,atol=1e-13)
        err.append(abs(seq[-1]["Sigma"]-ref))
    assert err[2]<2e-8
    assert err[2] < err[0]


def test_einstein_constraint_differentiation_independent_raychaudhuri():
    src=source_lock()
    eq=CanonicalFVSpecies(src,2.7255,8,
        Sigma_ref=public_sigma_from_q(.01)[0],orientation=1,
        kappa_gamma=.2,kappa_nu=.2,mass_fraction=.1,
        massive_A=.5,radial_cells=48,angular_cells=24)
    y=eq.initial_state()
    sol,_,_=eq.integrate(121,rtol=2e-11,atol=1e-13)
    for idx in (9,37,81,110):
        x=float(sol.t[idx]);y=np.array(sol.y[:,idx])
        f=eq.fields(x,y)
        dy=eq.rhs(x,y)
        h=1e-5
        fp=eq.fields(x+h,y+h*dy)
        fm=eq.fields(x-h,y-h*dy)
        measured=(fp["Einstein_H2"]-fm["Einstein_H2"])/(2*h)
        predicted=(-src.h0**2*(3*f["dust_energy_norm"]
                     +4*f["rad_energy_norm"]
                     +3*(f["massive_energy_norm"]
                         +f["massive_mean_pressure_norm"]))
                    -6*f["s"]**2)
        assert abs(measured/predicted-1)<6e-8
