"""Published EXFOR Barnett2008 He4(pi0) near-threshold coupled EM nuclear Green response.

Source regime: 137.4207 < E_gamma < 158.0047 MeV, below first nuclear breakup + pi0.
The exclusive coherent interpretation is supported by exact kinematics of the final state,
NOT by casually changing EXFOR's inclusive (G,X)PI0 reaction code.
Incident alpha is at rest; pion angular law sin^2(theta) is a MODEL CHOICE, not direct
Barnett angular-data readback. Source cross sections remain direct EXFOR observations.
All outputs per primary gamma / per produced pi0 at one fixed FLRW redshift,
NOT cosmological injection histories, thermal heat, or complete nuclear evolution.
"""
from __future__ import annotations
import csv,math,sys
from pathlib import Path
import numpy as np
from scipy.constants import physical_constants, c, k, e

# PDG rest energies in MeV, c and hbar retained in the unit conversion bridge.
M_ALPHA=3727.3794118
M_PI0=134.9768
M_D=1875.61294257
B_2G=0.98823

def pion_lab(E,mu):
    """Exact recoil kinematics in the alpha rest frame for gamma+alpha -> pi0+alpha."""
    if not (-1-1e-12<=mu<=1+1e-12):raise ValueError('Invalid pion CM cos theta')
    sth=M_PI0+M_PI0**2/(2*M_ALPHA)
    if E<sth:raise ValueError('Below coherent pi0 threshold')
    ss=math.sqrt(M_ALPHA*M_ALPHA+2*M_ALPHA*E)
    epi=(ss*ss+M_PI0*M_PI0-M_ALPHA*M_ALPHA)/(2*ss)
    pp=math.sqrt(max(0,epi**2-M_PI0**2))
    be=E/(M_ALPHA+E);ga=(M_ALPHA+E)/ss
    lab=ga*(epi+be*pp*mu)
    p_lab=math.sqrt(max(0,lab*lab-M_PI0*M_PI0))
    return {'E_pi_MeV':lab,'E_gamma_min_MeV':(lab-p_lab)/2,
            'E_gamma_max_MeV':(lab+p_lab)/2,'recoil_alpha_K_MeV':E-lab}

M_P=938.27208816
M_N=939.56542052
M_T=2808.92113298
M_HE3=2808.39160743
THRESHOLD_COH=M_PI0+M_PI0*M_PI0/(2*M_ALPHA)
Q_DD=2*M_D-M_ALPHA
Q_NPD=M_P+M_N+M_D-M_ALPHA
CONVERSION=2.56819e-6 # mb -> MeV^-2 as in pinned ACROPOLIS v1.3.1
N_TARGET={1:2,2:3,3:3,4:4,5:4,6:5,7:5,8:5,9:5,10:6,11:6,12:7,13:7,14:7,15:8,16:8,17:8}
SOURCEREF='EXFOR_L0138002_Barnett2008_PRC77_064601'


def threshold_mev(masses):
    total=M_PI0+sum(masses)
    return (total*total-M_ALPHA*M_ALPHA)/(2*M_ALPHA)

THRESHOLDS={
    'coherent_alpha':threshold_mev((M_ALPHA,)),
    'pT':threshold_mev((M_P,M_T)),
    'nHe3':threshold_mev((M_N,M_HE3)),
    'dd':threshold_mev((M_D,M_D)),
    'npD':threshold_mev((M_N,M_P,M_D)),
    '2p2n':threshold_mev((M_P,M_P,M_N,M_N)),
}


def read_barnett_exfor(path):
    """Parser for source-backed fixed-column EXFOR rather than retype points."""
    txt=Path(path).read_text(errors='replace')
    tag='SUBENT        L0138002'
    a=txt.index(tag); b=txt.index('ENDSUBENT',a)
    s=txt[a:b]
    assert '(2-HE-4(G,X)0-P0-0,,SIG)' in s
    assert 'ERR-SYS' in s and '2.0' in s
    start=s.index('DATA                 3        216')
    end=s.index('ENDDATA',start)
    rows=[]
    for ln in s[start:end].splitlines():
        if 'L0138002' not in ln:continue
        toks=ln[:66].split()
        if len(toks)!=3:continue
        try:E,cs,err=map(float,toks)
        except ValueError:continue
        if not (120<E<180):continue
        rows.append({'energy_MeV':E,'sigma_micro_b':cs,'stat_micro_b':err,'shared_sys_percent':2.,
            'EXFOR_subentry':'L0138002','reaction_as_compiled':'(G,X)PI0,SIG',
            'source_2008':'Barnett et al. PRC77 064601','row_order':len(rows)+1})
    if len(rows)!=216:raise AssertionError(f'Expected 216 EXFOR rows; found {len(rows)}')
    return rows


def select_source_points(rows):
    targets=[139.80,144.02,148.04,152.03,156.13]
    out=[]
    for t in targets:
        candidates=[x for x in rows if abs(x['energy_MeV']-t)<0.00001]
        if not candidates: raise ValueError('Source point missing: '+str(t))
        # Deterministic source-line choice, no correlated pooling.
        row=min(candidates,key=lambda v:(v['stat_micro_b'],v['row_order']))
        if not THRESHOLD_COH<row['energy_MeV']<THRESHOLDS['pT']:
            raise AssertionError('Chosen source lies outside provably coherent interval')
        if row['sigma_micro_b']<=0:raise ValueError('Nonpositive measured sigma in admitted sample')
        out.append(dict(row))
    return out


def max_daughter(E):
    return pion_lab(E,1.)['E_gamma_max_MeV']


def daughter_reproduction_threshold():
    """Above this parent E, one daughter gamma can in principle produce another pion."""
    from scipy.optimize import brentq
    return brentq(lambda energy:max_daughter(energy)-THRESHOLD_COH,165.,190.,xtol=1e-12)


def angular_ensemble(E,angular_model='pwave',n_mu=32):
    """Coherent 2-body pion, unmeasured angular shape is an explicit hypothesis."""
    mu,w=np.polynomial.legendre.leggauss(n_mu)
    if angular_model=='pwave':w=w*(3/4)*(1-mu*mu)
    elif angular_model=='isotropic':w=w/2.
    else:raise ValueError('Unknown angular law')
    w=w/w.sum()
    points=[pion_lab(E,float(m)) for m in mu]
    lows=np.array([x['E_gamma_min_MeV'] for x in points]);highs=np.array([x['E_gamma_max_MeV'] for x in points]);
    ep=np.array([x['E_pi_MeV'] for x in points]);
    assert np.max(highs)<THRESHOLD_COH, 'Born photon can reopen pion channel; no-regeneration claim invalid'
    return {'mu':mu,'weights':w,'lows':lows,'highs':highs,'Epi':ep,
            'N_exact':2*B_2G,'E_exact':B_2G*float(np.dot(w,ep)),
            'mean_pion_MeV':float(np.dot(w,ep)),
            'max_daughter_MeV':float(np.max(highs))}


def project_pi_daughter_source(grid,kin):
    # Conserve count using bin-overlap integrals rather than raw dN/dE point samples.
    borders=np.r_[grid[0],np.sqrt(grid[:-1]*grid[1:]),grid[-1]]
    counts=np.zeros(len(grid))
    for i in range(len(grid)):
        overlap=np.maximum(0,np.minimum(borders[i+1],kin['highs'])-np.maximum(borders[i],kin['lows']))
        counts[i]=2*B_2G*np.dot(kin['weights'],overlap/(kin['highs']-kin['lows']))
    lg=math.log(grid[-1]/grid[0])/(len(grid)-1)
    wg=lg*np.asarray(grid).copy();wg[0]*=0.5;wg[-1]*=0.5
    spec=counts/wg
    assert abs(np.dot(wg,spec)-2*B_2G)<1e-12
    return spec,wg


def _imports():
    import acropolis
    import acropolis.cascade as ac
    from acropolis.input import InputInterface,locate_sm_file
    from acropolis.nucl import NuclearReactor,_rsig
    from acropolis.params import zeta3,pi2
    from acropolis.info import version
    if version!='1.3.1':raise RuntimeError('ACROPOLIS 1.3.1 source pin violated: '+version)
    return ac,InputInterface,locate_sm_file,NuclearReactor,_rsig,zeta3,pi2


def solve_epoch(sample,z,NE=96,angular_model='pwave',nuclear_sink=True,return_spectrum=False):
    ac,InputInterface,locate_sm_file,NuclearReactor,rsig,zeta3,pi2=_imports()
    energy=sample['energy_MeV']
    kin=angular_ensemble(energy,angular_model)
    Emax=max(kin['highs'])*1.000001
    T=2.7255*k/e/1e6*(1+z)
    ac.NE_pd=NE
    N=max(int(math.log10(Emax/ac.Emin)*NE),ac.NE_min)
    grid=np.logspace(math.log(ac.Emin),math.log(Emax),N,base=np.e)
    source,weights=project_pi_daughter_source(grid,kin)
    ii=InputInterface(locate_sm_file())
    gen=ac.SpectrumGenerator(ii)
    reactor=NuclearReactor([lambda t:0.]*3,[lambda energy,t:0.]*3,(T,T),Emax,ii)
    Y=np.array(ii.bbn_abundances_0());nb=ii.parameter('eta')*2*zeta3/pi2*T**3
    sigmas=np.array([[reactor.get_cross_section(rid,float(E)) for E in grid] for rid in range(1,18)])
    G=np.array([[gen._rate_x(x,float(E),T) for E in grid] for x in range(3)])
    K=np.array([[[[gen._kernel_x_xp(x,xp,float(E),float(Ep),T) if Ep>=E else 0. for Ep in grid] for E in grid] for xp in range(3)] for x in range(3)])
    nuc_loss=nb*sum(Y[N_TARGET[rid]]*sigmas[rid-1] for rid in range(1,18))
    if nuclear_sink:G[0]+=nuc_loss
    F=np.zeros((3,len(grid)));F[0]=source
    sol=ac._JIT_solve_cascade_equation(grid,G,K,np.zeros(3),F,T)
    if not np.isfinite(sol).all() or np.min(sol[1:])<-1e-22: raise ArithmeticError('Invalid coupled cascade density')
    if abs(float(np.dot(weights,source))-2*B_2G)>1e-12:raise AssertionError('Bad daughter count')
    rate=np.array([float(np.trapezoid(sol[1]*nb*Y[N_TARGET[rid]]*sigmas[rid-1],grid)) for rid in range(1,18)])
    born=rate[1]+rate[3]+2*rate[7]+rate[8]  # d from nucl reactions IDs: 2,4,8,9
    destroyed=rate[0]
    Dnet=born-destroyed
    # For two-body alpha -> DD, total laboratory D kinetic energy equals E_gamma - Q_dd.
    # 3-body alpha -> npD: only an energy upper bound for D; no invented differential distribution.
    sigdd=sigmas[7];signpd=sigmas[8]
    flux_alpha=sol[1]*nb*Y[5]
    gross_dd=float(np.trapezoid(flux_alpha*sigdd*np.maximum(0,grid-Q_DD),grid))
    upper_npd=float(np.trapezoid(flux_alpha*signpd*np.maximum(0,grid-Q_NPD),grid))
    pion_sigma=sample['sigma_micro_b']/1000*CONVERSION # measured µb -> mb -> MeV^-2
    Gpi=nb*Y[5]*pion_sigma
    Gqed=gen._rate_x(0,float(energy),T)
    Gnuc=nb*sum(Y[N_TARGET[rid]]*reactor.get_cross_section(rid,float(energy)) for rid in range(1,18))
    Ppi=Gpi/(Gpi+Gqed+Gnuc)
    # Linearize the measured cross section only. These are SOURCE-STAT and
    # common-mode 2% SOURCE-SYS, NOT full transport/nuclear theory errors.
    dP_dsig=Ppi*(1-Ppi)/sample['sigma_micro_b']
    Ppi_stat=abs(dP_dsig)*sample['stat_micro_b']
    Ppi_sys=abs(dP_dsig)*sample['sigma_micro_b']*0.02
    A={0:1,1:1,2:2,3:3,4:3,5:4,6:6,7:7,8:7}
    Z={0:0,1:1,2:1,3:1,4:2,5:2,6:3,7:3,8:4}
    deltas={i:0. for i in range(9)}
    for rid,(target,daughters) in rsig.items():
        if rid==11:continue # original Li6(gamma,X) unspecified final-state species
        f=rate[rid-1]
        deltas[target]-=f
        for j,mult in daughters.items():deltas[j]+=f*mult
        if sum(m*A[j] for j,m in daughters.items())!=A[target] or sum(m*Z[j] for j,m in daughters.items())!=Z[target]:
            raise AssertionError('Nonconserving reaction stoichiometry: '+str(rid))
    br=sum(deltas[i]*A[i] for i in range(9)); cr=sum(deltas[i]*Z[i] for i in range(9))
    if abs(Dnet-deltas[2])>1e-10*max(1,abs(Dnet)) or abs(br)>1e-10 or abs(cr)>1e-10:raise AssertionError('Baryon/charge/D ledger')
    result={
      'source':'Barnett2008_EXFOR_L0138002', 'Eprimary_MeV':energy,'sigma_pi0_micro_b':sample['sigma_micro_b'],
      'sigma_pi0_stat_micro_b':sample['stat_micro_b'],'sigma_pi0_shared_sys_percent':2.,
      'source_line_index':sample['row_order'], 'z':z,'T_MeV':T,'NE_per_decade':NE,'num_grid':N,
      'angular_law':angular_model, 'nuclear_sink':nuclear_sink,'B_pi0_2gamma':B_2G,
      'pion_first_hit_P':Ppi,'pion_first_hit_stat_source_1sigma':Ppi_stat,
      'pion_first_hit_sys_shared_1sigma':Ppi_sys,
      'D_net_first_hit_stat_source_1sigma':abs(Dnet)*Ppi_stat,
      'D_net_first_hit_sys_shared_1sigma':abs(Dnet)*Ppi_sys,
      'Gamma_pi0_MeV':Gpi,'Gamma_EM_MeV':Gqed,'Gamma_nuclear17_MeV':Gnuc,
      'daughter_exact_count':kin['N_exact'],'daughter_exact_total_energy_MeV':kin['E_exact'],
      'daughter_grid_energy_MeV':float(np.dot(weights,source*grid)),
      'daughter_grid_energy_relerr':float(np.dot(weights,source*grid)/kin['E_exact']-1),
      'daughter_Emax_MeV':kin['max_daughter_MeV'], 'daughter_pion_reproduction_kinematically_forbidden':True,
      'D_born_per_pi0':born,'D_destroyed_per_pi0':destroyed,'D_net_per_pi0':Dnet,
      'D_net_per_primary_first_hit':Dnet*Ppi,
      'DD_pair_gross_kinetic_MeV_per_pi0':gross_dd,
      'npD_D_kinetic_upper_MeV_per_pi0':upper_npd,
      'fastD_from_dd_gross_lower_MeV_per_pi0':gross_dd,
      'fastD_from_dd_plus_npD_gross_upper_MeV_per_pi0':gross_dd+upper_npd,
      'D_birth_from_non_alpha_channels_not_in_fastD_bracket':True,
      'fastD_kinetic_scope':'ONLY_alpha(gamma,DD)and_alpha(gamma,npD);NOT_ALL_D_SOURCES',
      'total_photonuclear_events_per_pi0':float(rate.sum()),
      'pi0_produced_per_parent_at_first_hit':Ppi,
      'known_stoichiometry_baryon_residual':br,'known_stoichiometry_charge_residual':cr,
      'unknown_Li6_gamma_X_events':rate[10],
      'no_BASS_native_gamma_source':True,'no_heat_rate':True,
      'no_pion_regeneration_exact_on_source_domain':True,
      'no_nuclear_fragments_pi0_above_first_breakup':True,
      'ACROPOLIS_version':'1.3.1',
    }
    out={'case':result,'rates':rate,'nuclei':deltas}
    if return_spectrum:out['spectra']={'grid':grid,'gamma':sol[1],'electron':sol[2],'positron':sol[3],'injected':source,'nuclear_loss':nuc_loss}
    return out


def read_barnett_csv(path):
    with Path(path).open(newline='',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))
    for row in rows:
        for x in ('energy_MeV','sigma_micro_b','stat_micro_b','shared_sys_percent'):
            row[x]=float(row[x])
        row['row_order']=int(row['row_order'])
    if len(rows)!=216 or any(r['EXFOR_subentry']!='L0138002' for r in rows):
        raise ValueError('Source csv lost Barnett EXFOR identity')
    return rows
