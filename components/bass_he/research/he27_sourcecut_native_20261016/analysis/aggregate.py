"""Recheck HE27 native raw ledgers and finite-resolution comparisons; no ODE replay."""
from pathlib import Path
import sys,json,gzip,csv,math,hashlib
import numpy as np
root=Path('/root/HE27_NCP_SOURCECUT_20261016')
PACKAGE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(PACKAGE.parent/'he25_proper_birth_20261016/src'))
from physics import Y_HE,EV_ERG,BIND_EV
from native import _FIELDS,_WIDTHS
result_paths=sorted(root.glob('*/RESULT.json'));records=[]
for p in result_paths:
 d=json.loads(p.read_text());r=d['result'];r['case']=p.parent.name
 ident=json.loads((p.parent/'IDENTITY.json').read_text());r['args']=ident['args'];r['elapsed_s']=d['elapsed_s']
 assert d['status']=='NATIVE_VERIFIED_SCOPED'
 assert abs(r['number_defect'])<=3e-15 and abs(r['energy_defect_ev'])<=3e-12 and max(abs(x) for x in r['species_defect'])<=3e-12
 assert r['gas_positive'] and r['min_photon']>=0
 assert r['metadata'].get('newton_max',0)<=3e-15
 records.append(r)
max_density=max_event=max_micro=0.;points=0;files=0
for p in sorted([f.parent/'native.jsonl.gz' for f in result_paths]):
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

bycase={r['case']:r for r in records}
summary={'schema':'he27.native_ledgers.v1','case_count':len(records),'native_point_records_checked':points,'native_raw_files':files,
 'max_number_defect_per_H':max(abs(r['number_defect']) for r in records),
 'max_energy_defect_eV_per_H':max(abs(r['energy_defect_ev']) for r in records),
 'max_species_defect':max(max(abs(x) for x in r['species_defect']) for r in records),
 'max_density_Y_relative_defect':max_density,'max_point_event_relative_defect':max_event,'max_micro_energy_normalized_defect':max_micro}
if 'fast_reference_dop853' in bycase and 'fast_reference_radau_long' in bycase:
 ref=bycase['fast_reference_dop853'];old=bycase['baseline_reference_dop853'];rad=bycase['fast_reference_radau_long']
 summary['independent_time_reference']={'DOP853_temperature_K':ref['temperature_K'],'Radau_minus_DOP853_K':rad['temperature_K']-ref['temperature_K'],'max_fraction_difference':max(abs(a-b) for a,b in zip(rad['gas_final'][:3],ref['gas_final'][:3]))}
 summary['dynamic_AB']={'cut_minus_baseline_temperature_K':ref['temperature_K']-old['temperature_K'],'cut_minus_baseline_fractions':(np.array(ref['gas_final'][:3])-np.array(old['gas_final'][:3])).tolist(),'same_m_angles_q':[4,4,0],'source_table_nodes':512,'claim':'finite semi-discrete source A/B, not full continuum cutoff error'}
 temporal=sorted([r for r in records if r['args']['lane']=='sourcecut' and r['args'].get('source_module')=='sourcecut_fast' and r['args'].get('source_table_nodes',512)==512 and r['args']['method']=='transport' and r['m']==4 and r['angles']==4 and r['q']==0],key=lambda r:r['metadata']['n'])
 errors=[abs(r['temperature_K']-ref['temperature_K']) for r in temporal]
 summary['temporal']={'n':[r['metadata']['n'] for r in temporal],'temperature_error_K':errors,'ratios':[a/b for a,b in zip(errors[:-1],errors[1:])],'status':'TEMPORAL_CONVERGENCE_VERIFIED_SCOPED' if len(errors)>=3 and all(a>b for a,b in zip(errors[:-1],errors[1:])) else 'HOLD'}
 for r in records:
  if r['m']==4 and r['angles']==4 and r['q']==0 and r['args']['lane']=='sourcecut':r['temperature_error_K']=r['temperature_K']-ref['temperature_K']
summary['full_EoR_upstream_Grackle_observational_Bianchi_CMB']='HOLD'
(root/'ALL_RESULTS.json').write_text(json.dumps(records,indent=2));(root/'VERIFICATION.json').write_text(json.dumps(summary,indent=2))
fields=['case','m','angles','q','temperature_K','temperature_error_K','number_defect','energy_defect_ev','elapsed_s']
with (root/'CASES.csv').open('w',newline='') as f:
 writer=csv.DictWriter(f,fieldnames=fields,lineterminator='\n');writer.writeheader();writer.writerows({k:r.get(k) for k in fields} for r in records)
print(json.dumps(summary,indent=2))
