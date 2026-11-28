import sys,json,math,csv,hashlib
from pathlib import Path
import numpy as np
sys.path.insert(0,'/root/BASS_HE_HE23_DENSITY_20261016/research/he23_density_contract_20261016/src')
from he21_photo import Y_HE,EV_ERG,BIND_EV,SOURCE_N_PER_H,admissible
from he22_native_client import parse_native_point
w=Path('/root/HE23_NCP_DENSITY_20261016')
cases=[]
for directory in ['pilot_energy_gate_v2','matrix_energy_gate_v2','refinement_energy_gate_v2']:
 for p in sorted((w/directory).glob('q*.json')):
  r=json.loads(p.read_text())['result'];cases.append(r)
  assert abs(r['number_defect'])<=3e-15
  assert abs(r['energy_defect'])<=3e-12
  assert max(abs(x) for x in r['chemical_species_defect'])<=3e-12
  assert r['max_newton_error']<3e-12 and r['max_support_crossing']==0
  assert abs(r['source_count']-SOURCE_N_PER_H)<3e-15
  assert abs(r['source_shape_number_defect'])<3e-15 and abs(r['source_shape_energy_defect'])<3e-12
  assert admissible(np.array(r['gas_final'])) and all(x>=0 for x in r['absorbed'])
  # Independent charge/electron ledger from species events, including CI/RR/DR.
  dxe=(r['gas_final'][0]-1e-5)+Y_HE*((r['gas_final'][1]-1e-5)+2*r['gas_final'][2])
  events=sum(r['absorbed'])+sum(r['ci_per_H'])-sum(r['rr_per_H'])-r['dr_per_H']
  r['electron_chemical_defect']=dxe-events
  assert abs(dxe-events)<3e-12
native_count=0;max_density=0.;max_event_rel=0.;max_energy_rel=0.
for directory in ['pilot_energy_gate_v2','matrix_energy_gate_v2','refinement_energy_gate_v2']:
 for p in sorted((w/directory).glob('raw*/*_rhs.json')):
  r=json.loads(p.read_text());assert r['returncode']==0
  argv=[float(v) for v in r['argv'][1:]];a=argv[0];g=np.array(argv[1:5]);gamma=np.array(argv[5:8]);power=np.array(argv[8:11])
  assert admissible(g)
  fields={row.split('\t')[0]:np.array([float(x) for x in row.split('\t')[1:]]) for row in r['stdout'].splitlines()[1:]}
  assert all(np.isfinite(v).all() for v in fields.values())
  nh=float(fields['NH_CM3'][0]);nhe=float(fields['NHE_CM3'][0]);max_density=max(max_density,abs(nh/r['expected_nh']-1),abs(nhe/nh/Y_HE-1))
  assert max_density<=1e-9
  alpha=np.array([1-g[0],Y_HE*(1-g[1]-g[2]),Y_HE*g[1]])
  ev=nh*alpha*gamma
  np.testing.assert_allclose(fields['PHOTO_EVENTS'],ev,rtol=2e-10,atol=1e-29)
  rel=np.max(np.abs(fields['PHOTO_EVENTS']-ev)/np.maximum(abs(ev),1e-29));max_event_rel=max(max_event_rel,float(rel))
  expected_photo=nh*sum(alpha*(gamma*BIND_EV*EV_ERG+power))
  assert math.isclose(fields['PHOTO_INPUT'][0],expected_photo,rel_tol=2e-10,abs_tol=1e-29)
  thermal,bind,escape,cmb,photo=(float(fields[k][0]) for k in ['THERMAL_MICRO','BINDING_MICRO','ESCAPE','CMB_TO_GAS','PHOTO_INPUT'])
  residual=thermal+bind+escape-cmb-photo
  ratio=abs(residual)/max(abs(photo),1e-29);max_energy_rel=max(max_energy_rel,ratio)
  assert ratio<=2e-9
  for k in ['PHOTO_EVENTS','CI_EVENTS','RR_EVENTS','DR_EVENTS','ESCAPE']:
   assert (fields[k]>=0).all(),(p,k)
  native_count+=1
summary=dict(status='PASS_SCOPED_ACTUAL_NATIVE',case_records=len(cases),native_rhs_records_checked=native_count,max_abs_number_defect=max(abs(r['number_defect']) for r in cases),max_abs_energy_defect_ev_per_H=max(abs(r['energy_defect']) for r in cases),max_abs_species_defect=max(max(abs(x) for x in r['chemical_species_defect']) for r in cases),max_abs_electron_defect=max(abs(r['electron_chemical_defect']) for r in cases),max_newton_error=max(r['max_newton_error'] for r in cases),max_density_relative_error=max_density,max_point_event_relative_error=max_event_rel,max_point_micro_energy_relative_error=max_energy_rel,scope='discrete ledgers and original Rust port; not global IVP or EoR certificate')
(w/'VERIFICATION.json').write_text(json.dumps(summary,indent=2))
keys=['m','steps','q','temperature_final_K','heat_ev','binding_delta_ev','escaped_ev','cmb_to_gas_ev','work_gas_ev','work_photon_ev','number_defect','energy_defect','electron_chemical_defect','max_newton_error','elapsed_s']
with (w/'CASES.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=keys);writer.writeheader();writer.writerows({k:r[k] for k in keys} for r in cases)
grid={(r['m'],r['steps']):r for r in cases if r['q']==0}
comparisons=[]
for kind in ['time','energy']:
 for fixed in [4,8,16] if kind=='time' else [2,4,8]:
  for low,high in [(2,4),(4,8)] if kind=='time' else [(4,8),(8,16)]:
   a,b=(grid[fixed,low],grid[fixed,high]) if kind=='time' else (grid[low,fixed],grid[high,fixed])
   comparisons.append({'axis':kind,'fixed_m_or_n':fixed,'low':low,'high':high,'delta_T_K':b['temperature_final_K']-a['temperature_final_K'],'max_abs_gas_fraction_delta':max(abs(x-y) for x,y in zip(a['gas_final'][:3],b['gas_final'][:3])),'absorbed_delta':[y-x for x,y in zip(a['absorbed'],b['absorbed'])],'heat_delta_ev_per_H':b['heat_ev']-a['heat_ev']})
(w/'CONVERGENCE.json').write_text(json.dumps({'q':0,'grid_m':[4,8,16],'grid_n':[2,4,8],'angular_order':8,'comparisons':comparisons,'admission':'finite differences only; angular refinement and independent continuum error bound NOT_VERIFIED'},indent=2))
print(json.dumps(summary,indent=2));print(json.dumps(comparisons,indent=2))
