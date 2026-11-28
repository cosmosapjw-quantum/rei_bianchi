#!/usr/bin/env python3
"""R44 source-bound HD52 level-resolved chemical injection, cooling and a material energy ledger.

Exploratory only. Original Grackle k52/k53 and EMAA HD52 are read from pinned
references. These are two of Grackle's 12-species network reactions, not an
implementation of the full Grackle code. Nascent HD J distribution is UNSOURCED,
represented by three explicitly declared alternative formation-state policies.
Time horizon 20 laboratory years with fixed (z,CMB,Tgas,nH) as an externally
thermostatted primordial-gas one-zone thought experiment. No physical chemical Q.
"""
from __future__ import annotations
import sys, os, csv, math, json, argparse, hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
import numpy as np
from scipy.constants import k as KB
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

RAW_SHA='b0db1613425e403889c3a74f6cd9e142c562a552f1ebf05e61cbf509cd429c94'
PARSER_SHA='c982bdd3a1dcf61bbd734295a68b2162b536068f4f65eb9e18ff188dd774252b'
GRACKLE_COMMIT='01261db0cefc69d8d5558e76a671b0c1f6e48271'
GRACKLE_RATE_BLOB='dfbab661e7c45981eed750baebff140849917152'
SEC_YEAR=365.25*86400
N_LEVELS=52
N_LINES=368

@dataclass(frozen=True)
class Scenario:
    temperatures_K: tuple=(70.,100.)  # exact original H-collision source nodes
    radiation_z: float=30.
    radiation_T0_K: float=2.7255
    fixed_H_cm3: float=1e4
    initial_H2_cm3: float=10.
    initial_Dplus_cm3: float=0.2
    initial_HD_cm3: float=1e-4
    initial_Hplus_cm3: float=1.
    final_year: float=20.
    n_time_points: int=961
    policies: tuple=('ground_J0','excited_J2','gibbs_Tgas')


def sha256(path: Path):return hashlib.sha256(path.read_bytes()).hexdigest()


def original_source(source_dir):
    path=Path(source_dir)
    if sha256(path/'source_private/HD.Rovibration.805a7aa5.radex')!=RAW_SHA:raise ValueError('Original EMAA source SHA mismatch')
    if sha256(path/'source_private/emaa_primary.py')!=PARSER_SHA:raise ValueError('Original EMAA parser SHA mismatch')
    sys.path.insert(0,str(path.resolve()))
    import generate as r43
    if Path(r43.ROOT).resolve()!=path.resolve():raise RuntimeError('imported generator is not supplied frozen source')
    return r43,r43.load_data()


def grackle_k52(T):
    """Grackle source k52_rate, physical cm^3 s^-1, H2+D+ -> HD+H+."""
    if not (T>0 and math.isfinite(T)): raise ValueError('positive finite T required')
    if T<=1e4:
        l=math.log10(T)
        return 1e-9*(.417+.846*l-.137*l*l)
    return 1.609e-9


def grackle_k53(T):
    """Grackle source k53_rate, physical cm^3 s^-1, HD+H+ -> H2+D+."""
    if not (T>0 and math.isfinite(T)): raise ValueError('positive finite T required')
    return 1.1e-9*math.exp(-488./T)


def chemistry_extent(t, kf, kr, a, b, c, d):
    """Exact scalar Riccati extent at volume=1. Handles forward transient to equilibrium."""
    if t<0:raise ValueError('t>=0')
    A=kf-kr; B=-kf*(a+b)-kr*(c+d);C=kf*a*b-kr*c*d
    if C<=0:raise ValueError('selected source scenario requires initially forward extent')
    disc=B*B-4*A*C
    if disc<0:raise ArithmeticError('unphysical Riccati discriminant')
    if abs(A) < 1e-30:
        return C*t if B==0 else -C*math.expm1(B*t)/B
    q=-.5*(B+math.copysign(math.sqrt(disc),B))
    r1=C/q if q else (-B-math.sqrt(disc))/(2*A)
    r2=q/A if q else (-B+math.sqrt(disc))/(2*A)
    if r1>r2:r1,r2=r2,r1
    y0=r1/r2; y=y0*math.exp(A*(r1-r2)*t)
    x=(r1-y*r2)/(1-y)
    if x < -1e-12 or x>min(a,b)+1e-10: raise ArithmeticError('extent escaped physical simplex')
    return max(0.,x)


def source_distributions(data, T, E):
    lv=data['levels'];g=np.array([lv[i]['g'] for i in range(1,53)])
    states={ (lv[i]['v'],lv[i]['J']):i-1 for i in range(1,53)}
    f0=np.eye(52)[states[(0,0)]];f2=np.eye(52)[states[(0,2)]]
    p=g*np.exp(-(E-E.min())/(KB*T));p/=p.sum()
    return {'ground_J0':f0,'excited_J2':f2,'gibbs_Tgas':p}


def evaluate_case(r43,data, s:Scenario, T:float, policy:str):
    if T not in data['partners'][5]['temps']:raise ValueError('T outside EMAA original H source nodes')
    # Deliberate H-only 52-state excitation; H+ collider at 70/100K unsupported in the original H/H+ grid.
    nH=s.fixed_H_cm3
    R,lines=r43.radio_matrix(data,s.radiation_T0_K*(1+s.radiation_z))
    C=r43.coll_matrix(data,5,T,nH)
    K=C+R
    E=np.array([data['levels'][i]['E']*r43.owner.HCJ for i in range(1,53)])
    inject=source_distributions(data,T,E)[policy]
    kf,kr=grackle_k52(T),grackle_k53(T)
    a,b,c,d=s.initial_H2_cm3,s.initial_Dplus_cm3,s.initial_HD_cm3,s.initial_Hplus_cm3
    def chem(t):
        x=chemistry_extent(t,kf,kr,a,b,c,d)
        form=kf*(a-x)*(b-x)
        destroy=kr*(d+x)
        return x,form,destroy
    def rhs(t,n):
        _,F,D=chem(t)
        return K@n + F*inject-D*n
    def jac(t,n):return K-chem(t)[2]*np.eye(52)
    times=np.r_[0.,np.geomspace(1.,s.final_year*SEC_YEAR,s.n_time_points-1)]
    sol=solve_ivp(rhs,(0.,s.final_year*SEC_YEAR),c*inject,t_eval=times,
                  method='BDF',rtol=2e-11,atol=5e-19,jac=jac,dense_output=True)
    if not sol.success:raise RuntimeError(f'stiff source solve failed: {sol.message}')
    stationary,p_stationary,_=r43.equilibrium(data,T,nH,0.,s.radiation_T0_K*(1+s.radiation_z))
    lam_steady=float(stationary['net_photon_J_s_per_HD'])
    def flux(n):return -float(E@(R@n))*1e6  # W/m^3; n in cm^-3
    rows=[]; pops=[]; powers=[]
    def make_row(i,t,n):
        x,F,D=chem(t); ydot=rhs(t,n)
        phot=flux(n);coll=float(E@(C@n))*1e6
        inject_energy=float(E@inject)*F*1e6
        sink_energy=float(E@n)*D*1e6
        dot_internal=float(E@ydot)*1e6
        internal=float(E@n)*1e6
        residual=coll+inject_energy-sink_energy-phot-dot_internal
        return {'Tgas_K':T,'Trad_K':s.radiation_T0_K*(1+s.radiation_z),
                'formation_policy':policy,'time_s':t,'time_year':t/SEC_YEAR,
                'chemical_extent_cm3':x,'H2_cm3':a-x,'Dplus_cm3':b-x,
                'HD_exact_cm3':c+x,'Hplus_cm3':d+x,'HD_master_cm3':float(n.sum()),
                'HD_nonnegative_min_cm3':float(n.min()),
                'chemical_formation_cm3_s':F,'chemical_destruction_rate_s':D,
                'radiative_power_W_m3':phot,'stationary_power_W_m3':(c+x)*lam_steady*1e6,
                'radiative_minus_stationary_W_m3':phot-(c+x)*lam_steady*1e6,
                'collision_power_to_HD_W_m3':coll,
                'formation_internal_energy_source_W_m3':inject_energy,
                'destruction_internal_energy_sink_W_m3':sink_energy,
                'dU_HD_internal_dt_W_m3':dot_internal,
                'U_HD_internal_J_m3':internal,
                'instant_energy_residual_W_m3':residual,
                'unknown_reaction_Q_J':None,
                'state_resolved_source_authority':'assumed_formation_state_not_published'}
    for i,t in enumerate(sol.t):
        n=sol.y[:,i];row=make_row(i,float(t),n);rows.append(row)
        powers.append(row['radiative_power_W_m3'])
        for j,nj in enumerate(n):
            pops.append({'Tgas_K':T,'formation_policy':policy,'time_year':t/SEC_YEAR,
                         'level_id':j+1,'v':data['levels'][j+1]['v'],'J':data['levels'][j+1]['J'],
                         'n_HD_level_cm3':float(nj)})
    cum=[0.]
    for i in range(1,len(rows)):
        dt=rows[i]['time_s']-rows[i-1]['time_s']
        cum.append(cum[-1]+.5*dt*(powers[i]+powers[i-1]))
    for row,q in zip(rows,cum):row['cumulative_photon_J_m3']=q
    # Exact sign-change in the actual smooth time-dependent 52-state interpolation.
    cross=[]
    for i in range(1,len(rows)):
        if powers[i]*powers[i-1]<0:
            r=brentq(lambda t:flux(sol.sol(t)),rows[i-1]['time_s'],rows[i]['time_s'],xtol=1e-5)
            cross.append(r/SEC_YEAR)
    photons=[]
    for timeyr in (0.,.01,.1,1.,5.,20.):
        t=timeyr*SEC_YEAR;n=sol.sol(t)
        for upper,lower,Eph,down,up,freq in lines:
            row={'Tgas_K':T,'formation_policy':policy,'time_year':timeyr,
                 'upper_id':upper+1,'lower_id':lower+1,'frequency_GHz':freq,
                 'emission_W_m3':1e6*Eph*down*n[upper],
                 'absorption_W_m3':1e6*Eph*up*n[lower],
                 'net_photon_W_m3':1e6*Eph*(down*n[upper]-up*n[lower])}
            photons.append(row)
    check={
        'Tgas_K':T,'formation_policy':policy,'z_fixed':s.radiation_z,
        'initial_power_W_m3':rows[0]['radiative_power_W_m3'],
        'final_power_W_m3':rows[-1]['radiative_power_W_m3'],
        'final_steady_power_W_m3':rows[-1]['stationary_power_W_m3'],
        'initial_nHD_cm3':rows[0]['HD_master_cm3'],
        'final_nHD_cm3':rows[-1]['HD_master_cm3'],
        'final_nHD_chem_exact_cm3':rows[-1]['HD_exact_cm3'],
        'sign_crossing_years':cross,
        'cumulative_energy_J_m3':rows[-1]['cumulative_photon_J_m3'],
        'max_chem_total_mismatch_cm3':max(abs(r['HD_master_cm3']-r['HD_exact_cm3']) for r in rows),
        'max_energy_ledger_residual_W_m3':max(abs(r['instant_energy_residual_W_m3']) for r in rows),
        'solver_success':sol.success,'solver_nfev':sol.nfev,'rows':len(rows),
        'population_rows':len(pops),'photon_line_rows':len(photons)}
    return rows,pops,photons,check


def writecsv(path,rows):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n')
        wr.writeheader()
        for r in rows:
            wr.writerow({k:('' if v is None else format(v,'.17g') if isinstance(v,float) else v) for k,v in r.items()})


def run(out:Path,source_dir:Path,s:Scenario=Scenario()):
    r43,data=original_source(source_dir)
    out.mkdir(parents=True,exist_ok=True)
    rows=[];pops=[];photons=[];checks=[]
    for T in s.temperatures_K:
        for p in s.policies:
            a,b,c,d=evaluate_case(r43,data,s,T,p)
            rows+=a;pops+=b;photons+=c;checks.append(d)
    writecsv(out/'R44_TIME_SERIES.csv',rows)
    writecsv(out/'R44_LEVEL_POPULATIONS.csv',pops)
    writecsv(out/'R44_LINE_PHOTONS.csv',photons)
    summary={'project':'cosmosapjw-quantum/WU088_HH','unit':'R44_EMAA_HD52_CHEMICAL_INJECTION_DYNAMIC_CMB',
             'status':'EXPLORATORY_SOURCE_CONDITIONAL','canonical_DAG':'34/49_UNCHANGED',
             'parent_PR':182,'protected_parent_HEAD':'03a884d4035194703307c243179ca5e74e028b72',
             'immutable_R43_parent_PR':181,'immutable_R43_parent_HEAD':'993e8a607ab1a25d9f8d0ecd170c80ac0603a2b6',
             'raw_EMAA_SHA256':RAW_SHA,'raw_parser_SHA256':PARSER_SHA,
             'Grackle_commit':GRACKLE_COMMIT,'Grackle_rate_functions_git_blob':GRACKLE_RATE_BLOB,
             'specified_physical_conditions':asdict(s),
             'rows':{'dynamic':len(rows),'HD52_populations':len(pops),'368line_photons':len(photons)},
             'cases':checks,'source_input_states':{'ground_J0':'HD(v=0,J=0)','excited_J2':'HD(v=0,J=2)',
                  'gibbs_Tgas':'normalized 52-level Boltzmann with source rotational g and energies'},
             'source_grid_limit':'H-neutral original exact 70K and 100K; Hplus as CHEMICAL collider only',
             'standing_236_88_vs_224_100':'UNRESOLVED_HISTORICAL_GRID_IDENTITY',
             'R6_distinct_author':'NOT_RUN','C9_distinct_author':'NOT_RUN',
             'HH_R10':'OFF','L4':False,'production':'NOT_ISSUED','no_main_merge':True,'auto_next_node':False,
             'not_claimed':['no state-resolved chemistry source distribution','no chemical Q','no self-consistent Tgas',
                 'no cosmological expanding-cell trajectory','not full 12-species Grackle','not an observation',
                 'not first discovery of primordial HD nonLTE dynamical chemical rates']}
    (out/'R44_SUMMARY.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    return summary


def main():
    p=argparse.ArgumentParser();p.add_argument('--source-dir',type=Path,required=True)
    p.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'results')
    a=p.parse_args();s=run(a.out,a.source_dir)
    print(json.dumps({'status':s['status'],'rows':s['rows'],
        'cases':[{k:x[k] for k in ('Tgas_K','formation_policy','sign_crossing_years','cumulative_energy_J_m3')} for x in s['cases']]},indent=2))
if __name__=='__main__':main()
