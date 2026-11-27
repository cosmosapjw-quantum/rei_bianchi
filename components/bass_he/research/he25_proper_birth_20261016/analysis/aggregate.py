"""Read actual HE25 results/raw records; no numerical evolution or acceptance relaxation."""
from pathlib import Path
import sys,json,gzip,csv,math
import numpy as np
root=Path('/root/HE25_NCP_BIRTH_20261016')
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from physics import Y_HE,EV_ERG,BIND_EV
from native import _FIELDS,_WIDTHS
records=[]
for p in [root/'pilot/RESULT.json',*sorted((root/'pilot_tight').glob('q*/RESULT.json')),
          *sorted((root/'temporal').glob('q*/RESULT.json')),*sorted((root/'resolution').glob('q*/RESULT.json')),
          root/'controls/BIRTH_QUADRATURE.json',root/'reference_pilot/radau_pilot.json',
          *sorted((root/'references_final').glob('q*.json'))]:
 d=json.loads(p.read_text());r=d['result'];r['case_path']=str(p.relative_to(root));records.append(r)
 assert abs(r['number_defect'])<=3e-15 and abs(r['energy_defect_ev'])<=3e-12
 assert max(abs(x) for x in r['species_defect'])<=3e-12 and r['gas_positive'] and r['min_photon']>=0
 assert r['metadata'].get('newton_max',0)<=3e-12
refs={json.loads(p.read_text())['q']:json.loads(p.read_text())['result'] for p in sorted((root/'references_final').glob('*radau*.json'))}
refs[0.]=json.loads((root/'references_final/q0_radau_tight.json').read_text())['result']
for r in records:
 ref=refs[r['q']];r['dT_K']=r['temperature_K']-ref['temperature_K'];r['max_gas_fraction_error']=max(abs(a-b) for a,b in zip(r['gas_final'][:3],ref['gas_final'][:3]))
fields=['case_path','m','angles','q','temperature_K','dT_K','max_gas_fraction_error','number_defect','energy_defect_ev','min_photon']
with (root/'CASES.csv').open('w',newline='') as f:
 wr=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');wr.writeheader();wr.writerows({k:r[k] for k in fields} for r in records)
max_density=max_event=max_micro=0.;points=0;files=0
for p in sorted(root.rglob('*.jsonl.gz')):
 files+=1
 with gzip.open(p,'rt') as f:
  for line in f:
   r=json.loads(line)
   assert r['source_commit']=='f7830e2f55e7a1938bc3c98f61b60651f8dae474'
   assert r['binary_sha256']=='22d11447300381d5cd02d06e13f312e3e2aa3716eaecf60d3bcdb4d436a434d5'
   if r['kind']!='point':continue
   v=np.array([float(x) for x in r['response'].split('\t')[1:]])
   cols={};off=0
   for key,width in zip(_FIELDS,_WIDTHS):cols[key]=v[off:off+width];off+=width
   a,*values=map(float,r['request'].split('\t'));g=np.array(values[:4]);gamma=np.array(values[4:7]);heat=np.array(values[7:10])
   assert all(np.isfinite(v)) and g[0]>=0 and g[1]>=0 and g[2]>=0 and g[1]+g[2]<=1 and g[3]>0
   nh,nhe=cols['nh'][0],cols['nhe'][0]
   h0=67.4e5/3.0856775814913673e24
   nh0=(1-.2454)*(.0224/.674**2)*(3*h0*h0/(8*np.pi*6.67430e-8))/1.67262192595e-24
   max_density=max(max_density,abs(nhe/nh/Y_HE-1),abs(nh/(nh0/a**3)-1))
   alpha=np.array([1-g[0],Y_HE*(1-g[1]-g[2]),Y_HE*g[1]])
   ev=nh*alpha*gamma;err=max(abs(cols['photo_events']-ev)/np.maximum(ev,1e-29));max_event=max(max_event,float(err))
   expected=nh*np.dot(alpha,gamma*BIND_EV*EV_ERG+heat)
   assert math.isclose(cols['photo_input'][0],expected,rel_tol=2e-10,abs_tol=1e-29)
   micro=cols['thermal_micro'][0]+cols['binding_micro'][0]+cols['escape'][0]-cols['cmb'][0]-cols['photo_input'][0]
   max_micro=max(max_micro,abs(micro)/max(abs(cols['photo_input'][0]),1e-29))
   for key in ['photo_events','ci','rr','dr','escape']:assert (cols[key]>=0).all()
   points+=1
assert max_density<=1e-9 and max_event<=2e-10 and max_micro<=2e-9
summary={'schema':'he25.actual_verification.v1','study_case_records':len(records),'transport_case_records':sum('HE25_positive' in r['metadata']['method'] for r in records),
 'reference_case_records':sum(r['metadata']['method'] in ['Radau','DOP853'] for r in records),
 'native_raw_files':files,'native_point_records_checked':points,'max_number_defect':max(abs(r['number_defect']) for r in records),
 'max_energy_defect_ev_per_H':max(abs(r['energy_defect_ev']) for r in records),'max_species_defect':max(max(abs(x) for x in r['species_defect']) for r in records),
 'max_density_Y_relative_defect':max_density,'max_point_event_relative_defect':max_event,'max_micro_energy_normalized_defect':max_micro}
# Strict temporal acceptance is limited to this exact semi-discrete source/grid.
temporal=[r for r in records if r['case_path'].startswith(('pilot_tight/','temporal/'))]
temporal.sort(key=lambda r:r['metadata']['n']);errs=[abs(r['dT_K']) for r in temporal]
summary['temporal']={'grid':'m4, angular GL4, exact shared discrete source','n':[r['metadata']['n'] for r in temporal],'abs_temperature_errors_K':errs,
 'successive_ratios':[a/b for a,b in zip(errs[:-1],errs[1:])],
 'status':'TEMPORAL_CONVERGENCE_VERIFIED_SCOPED' if all(a>b for a,b in zip(errs[:-1],errs[1:])) and errs[-1]<1e-8 else 'HOLD'}
summary['continuous_spectral_convergence']='HOLD_UNREFINED_MOVING_EDGE_STRIPS'
summary['observational_and_full_EOR']='HOLD'
(root/'VERIFICATION.json').write_text(json.dumps(summary,indent=2));(root/'ALL_RESULTS.json').write_text(json.dumps(records,indent=2))
print(json.dumps(summary,indent=2))
