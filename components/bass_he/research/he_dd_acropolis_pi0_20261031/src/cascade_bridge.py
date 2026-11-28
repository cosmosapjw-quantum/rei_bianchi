"""Source-conditioned pi0->2 gamma from PR135 through unmodified ACROPOLIS v1.3.1.

No upstream library modifications, no BASS-native gamma emissivity and no net energy deposition.
Returns per-conditional-produced-pion photon-induced nuclear event response, not cosmic yields.
"""
from __future__ import annotations
import math, os, sys
from dataclasses import dataclass
from pathlib import Path
import numpy as np

# The previous PR135 Git diff contains a ZIP, not the unpacked pi0 module.
# The byte-exact source from that immutable ZIP is vendored only as an OWNED
# parent snapshot in this new add-only subtree. See provenance SHA256.
PARENT_SOURCE=Path(__file__).resolve().parent
sys.path.insert(0,str(PARENT_SOURCE))
from pi0_physics import selected_angular_rows, pion_lab, B_2G, interpolated_absorption, pion_source_kinematics, prompt_first_hits


def _acrop():
    """Lazy import from an independently provided and version-pinned installation."""
    import acropolis
    import acropolis.cascade as cascade
    from acropolis.input import InputInterface, locate_sm_file
    from acropolis.nucl import NuclearReactor
    from acropolis.params import zeta3, pi2
    from acropolis.info import version
    if version!='1.3.1':raise RuntimeError(f'Expected ACROPOLIS v1.3.1 source; got {version}')
    return cascade,InputInterface,locate_sm_file,NuclearReactor,zeta3,pi2


@dataclass
class SourceShape:
    Einc:float
    mu:np.ndarray
    weights:np.ndarray
    lows:np.ndarray
    highs:np.ndarray
    epi:np.ndarray

    @classmethod
    def from_exfor(cls, Einc:float):
        refs=(206.,216.,229.,241.)
        idx=next((i for i,e in enumerate(refs) if abs(Einc-e)<1e-8),None)
        if idx is None:raise ValueError('Source-matched energy required; do not interpolate angular measurements')
        rows=selected_angular_rows(idx)
        mu=np.cos(np.deg2rad([r['angle_cm_deg'] for r in rows]))
        sig=np.array([r['sigma_micro_b_per_sr'] for r in rows])
        k=np.argsort(mu);mu=mu[k];sig=sig[k]
        q=np.zeros(len(mu));q[0]=sig[0]*(mu[1]-mu[0])/2;q[-1]=sig[-1]*(mu[-1]-mu[-2])/2
        q[1:-1]=sig[1:-1]*(mu[2:]-mu[:-2])/2
        q/=q.sum()
        if len(rows)<20 or q.min()<0 or abs(q.sum()-1)>1e-13:raise AssertionError('Invalid measured angular support')
        point=[pion_lab(Einc,float(m)) for m in mu]
        return cls(Einc,mu,q,np.array([d['E_gamma_min_MeV'] for d in point]),np.array([d['E_gamma_max_MeV'] for d in point]),np.array([d['E_pi_MeV'] for d in point]))

    def spectrum(self,E):
        """dN_gamma/dE per produced pi0; empirical support-angle conditional, two-gamma only."""
        return float(2*B_2G*np.sum(self.weights*((self.lows<=E)&(E<=self.highs))/(self.highs-self.lows)))

    def exact_moments(self):
        return dict(N=2*B_2G,energy=float(B_2G*np.dot(self.weights,self.epi)), mean_pion_energy=float(np.dot(self.weights,self.epi)))

    def project_source(self,grid):
        """Conservative finite-volume source, exact photon COUNT on ACROPOLIS log-energy quadrature.
        End-cell masses are integrated over physical [Emin,Emax] with logarithmic midpoint edges.
        This changes only source discretization, not ACROPOLIS reaction kernels.
        """
        if any(np.diff(grid)<=0):raise ValueError('Grid must increase')
        borders=np.r_[grid[0],np.sqrt(grid[:-1]*grid[1:]),grid[-1]]
        N=np.zeros(len(grid))
        for i in range(len(grid)):
            overlap=np.maximum(0,np.minimum(borders[i+1],self.highs)-np.maximum(borders[i],self.lows))
            N[i]=2*B_2G*float(np.dot(self.weights,overlap/(self.highs-self.lows)))
        dy=math.log(grid[-1]/grid[0])/(len(grid)-1)
        integral_weights=dy*grid.copy();integral_weights[0]*=.5;integral_weights[-1]*=.5
        f=N/integral_weights
        assert abs(float(np.dot(integral_weights,f))-2*B_2G)<1e-12
        return f, integral_weights


def run_fixed_epoch(Einc:float,z:float,NE_pd:int,photon_only_check=False):
    cascade,InputInterface,locate_sm_file,NuclearReactor,zeta3,pi2=_acrop()
    source=SourceShape.from_exfor(Einc)
    # maximize only over measured source-angle range; no all-sky extrapolation
    Emax=float(max(source.highs))*(1.+1e-9)
    if Emax>260:raise RuntimeError('Pion daughter source escaped study domain')
    T=2.7255*8.617333262145e-11*(1.+z)
    cascade.NE_pd=NE_pd
    ne=max(int(math.log10(Emax/cascade.Emin)*NE_pd),cascade.NE_min)
    grid=np.logspace(math.log(cascade.Emin),math.log(Emax),ne,base=np.e)
    injected, weights=source.project_source(grid)
    # Need a pointwise callback; ACROPOLIS obtains this exact same ascending logarithmic grid.
    def SC_gamma(E,T):
        j=int(np.argmin(np.abs(grid-E)))
        if abs(grid[j]-E)>1e-7*max(1,E):raise RuntimeError('ACROPOLIS numerical grid changed')
        return float(injected[j])
    s0=[lambda t:0.,lambda t:0.,lambda t:0.]
    sc=[SC_gamma,lambda e,t:0.,lambda e,t:0.]
    ii=InputInterface(locate_sm_file());generator=cascade.SpectrumGenerator(ii)
    sol=generator.get_spectrum(Emax,s0,sc,T,allX=True)
    if len(sol[0])!=len(grid) or np.max(np.abs(sol[0]-grid))>1e-9:raise AssertionError('Grid mismatch')
    if not np.isfinite(sol).all() or not (sol[1:]>=0).all():raise ArithmeticError('Cascade spectrum nonfinite or negative')
    gamma=sol[1]
    n_b=ii.parameter('eta')*2*zeta3/pi2*T**3
    Y0=ii.bbn_abundances_0()
    n_alpha=Y0[5]*n_b
    reactor=NuclearReactor(s0,sc,(T,T),Emax,ii)
    nuclei=[1,6,7,8,9,15]
    sigma={rid:np.array([reactor.get_cross_section(rid,float(e)) for e in grid]) for rid in nuclei}
    # Reaction target identity: d is index 2, alpha index 5 and Be7 index 8.
    # Critically, using n_alpha for d or Be7 would be scientifically WRONG.
    target_by_rid={1:2,6:5,7:5,8:5,9:5,15:8}
    integrands={rid:gamma*Y0[target_by_rid[rid]]*n_b*sigma[rid] for rid in nuclei}
    yields={str(rid):float(np.trapezoid(integrands[rid],grid)) for rid in nuclei}
    def split_integral(v,cut=150.0):
        if not (grid[0]<cut<grid[-1]): return (float(np.trapezoid(v,grid)),0.) if cut>=grid[-1] else (0.,float(np.trapezoid(v,grid)))
        i=np.searchsorted(grid,cut)
        val=np.interp(cut,grid,v)
        below=np.trapezoid(np.r_[v[:i],val],np.r_[grid[:i],cut])
        above=np.trapezoid(np.r_[val,v[i:]],np.r_[cut,grid[i:]])
        if abs((below+above)-np.trapezoid(v,grid))>1e-10*max(1.,abs(np.trapezoid(v,grid))):raise ArithmeticError('split conservation')
        return float(below),float(above)
    d_integrand=integrands[9]+2*integrands[8]
    D_below,D_above=split_integral(d_integrand)
    # per incoming photon via the *parent* first-hit approximation; no backreaction on parent cascade
    parent=next(r for r in prompt_first_hits(*pion_source_kinematics(),zs=(float(z),)) if abs(r['E_MeV']-Einc)<1e-7)
    D_per_pi=yields['9']+2*yields['8']
    Ndisintegrations=yields['6']+yields['7']+yields['8']+yields['9']
    if Ndisintegrations>1:raise ArithmeticError('Photonuclear linear approximation outside perturbative regime')
    out={
      'E_primary_MeV':Einc,'z':z,'T_MeV':T,'ACROPOLIS_VERSION':'1.3.1',
      'NE_per_decade':NE_pd,'grid_count':len(grid),'source_index':'EXFOR_Rambo1999_M0752002_to_2005',
      'pi0_parent_P_first':parent['P_first_pi0'],
      'pion_count_injected':source.exact_moments()['N'],'pion_energy_injected_MeV':source.exact_moments()['energy'],
      'pion_grid_energy_MeV':float(np.dot(weights,grid*injected)),
      'source_grid_energy_relerr':float(np.dot(weights,grid*injected)/source.exact_moments()['energy']-1),
      'coherent_pi0_two_gamma_branch':B_2G,
      'He4_fraction_per_baryon':float(ii.bbn_abundances_0()[5]),
      'eta':float(ii.parameter('eta')),
      'D_born_per_pi0_conditional':D_per_pi,
      'D_born_below150_per_pi0':D_below,'D_born_above150_per_pi0':D_above,
      'fraction_D_born_below150':D_below/D_per_pi if D_per_pi>0 else None,
      'D_born_per_primary_gamma_first_pi0_then_cascade':D_per_pi*parent['P_first_pi0'],
      'pT_per_pi0':yields['6'],'nHe3_per_pi0':yields['7'],'npD_per_pi0':yields['9'],'dd_per_pi0':yields['8'],
      'D_destroy_per_pi0':yields['1'], 'Be7_destroy_per_pi0':yields['15'],
      'gamma_spectrum_max':float(np.max(sol[1])),
      'electron_spectrum_max':float(np.max(sol[2])),
      'positron_spectrum_max':float(np.max(sol[3])),
      'missing_BASS_native_emissivity':True,
      'linear_nuclear_response_no_full_network_feedback':True,
      'high_E_He4_Cyburt_extrapolation_not_measured':True,
      'pi0_angular_support_conditional_not_full_sky':True,
      'acropolis_spectral_floor_Emin_MeV':float(cascade.Emin),
      'ACROPOLIS_He4_nHe3_cross_section_prefactor_mb':20.7,
      'no_cosmic_heat_rate':True
    }
    if photon_only_check:
        G=np.array([[generator._rate_x(0,float(e),T) for e in grid]])
        K=np.zeros((1,1,len(grid),len(grid)))
        for i,e in enumerate(grid):
            for j,ep in enumerate(grid):
                if ep>=e:K[0,0,i,j]=generator._kernel_x_xp(0,0,float(e),float(ep),T)
        F0=cascade._JIT_solve_cascade_equation(grid,G,K,np.array([0.]),np.array([injected]),T)[1]
        yd0=float(np.trapezoid(F0*n_alpha*(sigma[9]+2*sigma[8]),grid))
        out['D_born_per_pi0_photon_only']=yd0
        out['D_born_coupled_minus_photon_only']=D_per_pi-yd0
        out['D_born_coupled_over_photon_only']=D_per_pi/yd0 if yd0>0 else None
    return out,sol,injected,source
