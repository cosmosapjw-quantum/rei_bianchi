"""Produce science tables and standalone summary: no external/private input or source normalization."""
import csv, json, pathlib, sys, hashlib, math
from transport import *
from physics_pr131 import state,bb_pair_rate_s
ROOT=pathlib.Path(__file__).resolve().parents[1]
D=ROOT/'data'
D.mkdir(exist_ok=True)
def put_csv(name,rows):
    with (D/name).open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
    print(name,len(rows),'rows')
Egrid=[170.,220.,249.]
zgrid=[1e4,3e4,1e5,2e5,5e5,1e6]
xs=[]
for E in [150.,170.,190.,220.,249.]:
    xs.append(dict(E_gamma_MeV=E,sigma_KN_e_cm2=sigma_kn(E),
       sigma_BH_H_cm2=sigma_bh_born_unscreened(E,1),
       sigma_BH_He_cm2=sigma_bh_born_unscreened(E,2),
       sigma_dd_Rice_binmodel_cm2=(8.29 if E<190 else 4.34)*1e-33,
       BH_model='highE_unscreened_bare_nucleus_Born',KN_model='electron_at_rest_exact_QED',
       dd_model='Rice2000_binned_fit_applied_pointwise'))
put_csv('CROSS_SECTIONS_MODEL_5.csv',xs)
rs=[]
for zi in zgrid:
    for E in Egrid:
        d=four_channel_rates(E,zi); H=state(zi)['H_s_inv']
        rs.append(dict(z=zi,E_gamma_MeV=E,Gamma_BW_s_inv=d['bw'],Gamma_KN_s_inv=d['kn'],
           Gamma_BH_s_inv=d['bh'],Gamma_dd_s_inv=d['dd'],H_s_inv=H,
           total_four_channel_to_H=sum(d.values())/H,
           conditional_dd_fraction_at_local_first_hit=d['dd']/sum(d.values()),
           includes_other_He_photonuclear=False))
put_csv('LOCAL_FOUR_CHANNEL_HAZARDS_18.csv',rs)
ps=[]
for zi in zgrid:
    for E in Egrid:
        p=flight(E,zi)
        ps.append(p)
        print('flight',E,zi,'dd=',format(p['P_dd_first'],'.7e'),'survive=',format(p['P_no_collision_until_terminal'],'.3e'),'tau=',format(p['tau_end'],'.3f'))
put_csv('COSMIC_FIRST_COLLISION_18.csv',ps)
sumr={
 'status':'MODELED_SOURCE_CONDITIONAL_FIRST_COLLISION_ONLY',
 'input_published_primary':['PR131 conserved background and BW exact QED from Gould Schréder 1967',
 'Klein-Nishina exact unpolarized stationary electron total cross section',
 'Racah/Bethe-Heitler high-energy unscreened Born bare nuclear pair production',
 'Rice2000 source bin-fit surrogate 8.29/4.34 nb; one 1998/2000 SAL experiment'],
 'new_physical_rows':len(xs)+len(rs)+len(ps),
 'counts':{'cross_sections':len(xs),'local_four_channel_hazards':len(rs),'cosmic_first_collision_kernel':len(ps)},
 'exact_model_contract':{'source':'ONE gamma injected at z_i with fixed E_i in local comoving alpha rest',
 'cosmology':'PR131 flat fully-ionized Planck/PDG FLRW; no BASS native anisotropy',
 'transport':'FLRW redshift + exact Planck BW thermal absorption + KN first e scattering + high-energy unscreened Born BH nuclear pair production + Rice2000 binned-fit-model He-dd',
 'photon_boundary':'stop at E_gamma=150 MeV or tau=65, whichever earlier',
 'daughter':'2 deuterons per first dd collision; total born kinetic E_gamma-Q; no D plasma deposition',
 'not_included':'gamma e triplet pair, other nuclear channels, Compton redistribution, BH secondary cascade, BASS source normalization, real cosmic ionization history, anisotropy'},
 'DAG':{'Central':'28/88','HE_physical':'14/18','physical_delta':0,'new_auxiliary':'2/2_source_conditional'},
 'hold':{'R_event':None,'heat_rate':None,'kappa':None,'L4':False,'production':'HOLD'},
 'table_mini_slices':[p for p in ps if p['E_inj_MeV']==220 and p['z_inj'] in (1e4,1e5,1e6)]
 }
(D/'SCIENCE_SUMMARY.json').write_text(json.dumps(sumr,indent=2,ensure_ascii=False,allow_nan=False)+'\n')
