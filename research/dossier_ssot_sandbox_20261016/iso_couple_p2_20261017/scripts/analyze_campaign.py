import csv,math,json
from pathlib import Path
base=Path(__file__).resolve().parents[1]/'evidence'
rows=list(csv.DictReader((base/'P2_CAMPAIGN.csv').open()))
assert len(rows)==45
cases={}
for r in rows:
 name=r['case'];d={k:(v if k in ['case','owner'] else float(v)) for k,v in r.items()}
 cases.setdefault(name,[]).append(d)
assert set(cases)=={'baseline_no_helium','helium_mixture','no_source_photons','no_cx','no_cmb'}
record={}
for name,rs in cases.items():
 rs.sort(key=lambda x:x['n_steps'])
 assert [int(x['n_steps']) for x in rs]==[1,2,4,8,16,32,64,128,256]
 tref=rs[-1]['T_K'];hpref=rs[-1]['nhp_m3']
 def fn(k):return next(x['T_K'] for x in rs if x['n_steps']==k)
 a=fn(8);b=fn(16);c=fn(32)
 p=math.log(abs((a-b)/(b-c)),2) if (b-c)!=0 and (a-b)/(b-c)>0 else None
 record[name]={'T_K_N1':rs[0]['T_K'],'T_K_N256':tref,'proton_N1':rs[0]['nhp_m3'],
 'proton_N256':hpref,'photon_final_N256_m3':rs[-1]['photons_m3'],
 'photo_events_N256_m3':rs[-1]['tau_event_m3'],'cx_extent_N256_m3':rs[-1]['cx_m3'],
 'T_abs_diff_N1_N256_K':abs(rs[0]['T_K']-tref),'T_abs_diff_N128_N256_K':abs(fn(128)-tref),
 'observed_order_temperature_grid_8_16_32':p,
 'max_abs_energy_rel_residual':max(abs(r['energy_rel_residual']) for r in rs),
 'max_abs_baryon_rel_residual':max(abs(r['baryon_rel_residual']) for r in rs),
 'max_abs_photon_event_count_relative_residual':max(abs(r['photo_event_over_photon_loss']-1) for r in rs)}
allrow=[r for rr in cases.values() for r in rr]
result={'schema':'rei.iso_couple.p2.numerical.v1','row_count':len(rows),'tested_ns':[1,2,4,8,16,32,64,128,256],
 'fixed_elapsed_s':4e8,'source_scope':'manufactured two finite photon bins at 70/30 eV, no new sources, no Bianchi expansion, no cosmic rates',
 'rate_sources':['PR150 Grackle 3.4.1','PR150 Verner photo fits','PR150 DAtomicProvider HI equality','PR150 Savin2002 original independent fits'],
 'max_abs_energy_relative':max(abs(r['energy_rel_residual']) for r in allrow),
 'max_abs_baryon_relative':max(abs(r['baryon_rel_residual']) for r in allrow),
 'max_abs_photon_count_relative':max(abs(r['photo_event_over_photon_loss']-1) for r in allrow),
 'cases':record,'admission':'PASS_SCOPED_SOURCE_BOUND_SYNTHETIC_FIXED_VOLUME'}
(base/'P2_RESULTS.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
print(json.dumps({'rows':len(rows),'max_energy':result['max_abs_energy_relative'],'max_baryon':result['max_abs_baryon_relative'],'max_photon':result['max_abs_photon_count_relative'],'helium_p':record['helium_mixture']['observed_order_temperature_grid_8_16_32'],'T_abs_diff_1_256':record['helium_mixture']['T_abs_diff_N1_N256_K']}))
try:
 import matplotlib;matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 fig,ax=plt.subplots(figsize=(7,4.2))
 for name in ['helium_mixture','baseline_no_helium','no_source_photons','no_cx']:
  rs=cases[name]
  ax.plot([x['n_steps'] for x in rs],[x['T_K'] for x in rs],marker='o',label=name.replace('_',' '))
 ax.set(xscale='log',xlabel='Equal proper-time subdivisions',ylabel='Final gas temperature [K]',title='Synthetic source-bound H/He/D finite-volume convergence')
 ax.grid(True,alpha=.3);ax.legend(fontsize=8);fig.tight_layout()
 fig.savefig(base/'P2_TEMPERATURE_REFINEMENT.png',dpi=180)
 plt.close(fig)
 fig,ax=plt.subplots(figsize=(7,4.2))
 for name in ['helium_mixture','baseline_no_helium','no_cx']:
  rs=cases[name]
  ax.loglog([x['n_steps'] for x in rs[:-1]], [max(abs(x['T_K']-rs[-1]['T_K']),1e-14) for x in rs[:-1]],marker='o',label=name.replace('_',' '))
 ax.set(xlabel='Equal subdivisions',ylabel='|T(N)-T(256)| [K]',title='First-order joint splitting: finite reference, not certified EoR')
 ax.grid(True,which='both',alpha=.3);ax.legend(fontsize=8);fig.tight_layout()
 fig.savefig(base/'P2_TIME_ERROR.png',dpi=180)
 plt.close(fig)
except ImportError: pass
