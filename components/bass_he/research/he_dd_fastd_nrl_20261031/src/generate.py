from __future__ import annotations
import csv,json,math,pathlib,sys
import numpy as np
from fastd import *
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/'data';D.mkdir(exist_ok=True)
def save(name,rows):
    with (D/name).open('w',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');wr.writeheader();wr.writerows(rows)
    print(name,len(rows))

background=[];integrals=[];rates=[];validations=[];profiles=[]
for z in REDSHIFTS:
    p=plasma(z)
    background.append({key:getattr(p,key) for key in p.__dataclass_fields__})
    for K0 in BIRTH_ENERGIES:
        res=integrate(K0,p,order=160)
        fine=integrate(K0,p,order=320)
        fixed=integrate(K0,p,order=160,log_mode='fixed20')
        integrals.append(res)
        validations.append(dict(z=z,K0_MeV=K0,max_160_320_rel=max(abs(fine[k]-res[k])/(abs(fine[k])+1e-100) for k in ('t_stop_s','Q_e_MeV','Q_p_MeV','Q_alpha_MeV','L_path_m')),t_stop_ln_fixed20_s=fixed['t_stop_s'],t_stop_ln_fixed20_over_dynamic=fixed['t_stop_s']/res['t_stop_s'],Q_e_ln_fixed20_MeV=fixed['Q_e_MeV']))
        # equal increment in lnK, upper to lower; no extra stop run
        ks=np.geomspace(K0,terminal(p),81)
        for kk in ks:
            r=energy_probe(p,float(kk))
            r['birth_K_MeV']=K0
            profiles.append(r)
    for k in [0.001,0.01,0.1,1.,10.,50.,100.,150.]:
        rates.append(energy_probe(p,k))
save('FLRW_IONIZED_HHE_5.csv',background)
save('FASTD_INTEGRATED_50.csv',integrals)
save('FASTD_EPOCH_RATES_40.csv',rates)
save('FASTD_PROFILE_4050.csv',profiles)
save('FASTD_VALIDATION_50.csv',validations)
assert len(integrals)==50 and len(profiles)==4050
summary={'unit':'NRL_2023_MAXWELL_TEST_ION_FASTD_CHEMICAL_PLASMA_STOPPING',
        'lineage_parent_pr':138,'lineage_parent_head':'07f2f0beb36cc54c8a4df0b7c0c5728ca8b2de51',
        'new_model_rows':len(background)+len(integrals)+len(rates)+len(profiles)+len(validations),
        'new_observed_rows':0,'DAG':{'central':'28/88','he_physical':'14/18','canonical_delta':0},
        'constants':{'T0_K':T0_K,'n_b0_cm3':NB0_CM3,'Y_He_mass':Y_HE,'lnLambda':'NRL_static_Debye_vs_max(classical,quantum)'},
        'physics_limits':['NRL 2023 test particle energy relaxation of ensemble, applied along characteristic approximation for narrow nonthermal D','all species Maxwellian with common T_CMB(z), fully ionized','single test D and weak perturbation','NRL weak coupling leading-log, static Debye screening approximation','K_terminal=max(1keV,30kBT): untracked terminal energy is not guaranteed heat','K0>30MeV tagged extrapolative nonrel','no nuclear in-flight cross-section folded; target column densities only','no absolute gamma source / R_event / heat_rate'],
        'max_quadrature_rel':max(v['max_160_320_rel'] for v in validations),
        'max_conservation_abs_mev':max(abs(v['q_sum_residual_MeV']) for v in integrals),
        'representative':next(v for v in integrals if v['z']==1e5 and v['K0_MeV']==1.),
        'coulomb_log_sensitivity':next(v for v in validations if v['z']==1e5 and v['K0_MeV']==1.)}
(D/'SCIENTIFIC_SUMMARY.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({k:summary[k] for k in ('new_model_rows','max_quadrature_rel','max_conservation_abs_mev','representative')},indent=2))
