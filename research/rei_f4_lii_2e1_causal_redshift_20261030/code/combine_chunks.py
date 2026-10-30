#!/usr/bin/env python3
"""Join source-ordered immutable chunk outputs, preserving one common spectral family."""
import json,pathlib,sys,numpy as np
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from causal_firstflight import ROOT,CAT,write_csv

def combine(order=16,substeps=4):
 files=sorted((ROOT/'chunks').glob(f'CHUNK_*_o{order}s{substeps}.json'))
 if not files:raise ValueError('MISSING_CHUNKS')
 arr=[json.loads(p.read_text()) for p in files]
 spans=[q['range'] for q in arr]
 if spans[0][0]!=0 or spans[-1][1]!=193 or any(b[1]!=a[0] for b,a in zip(spans[:-1],spans[1:])):raise ValueError(f'MISSING_RANGE:{spans}')
 emissions=[];flights=[];joint=[]
 arrival=np.zeros((192,6))
 integrated={};total=0
 positive={'mean_abs':np.zeros(20),'P2':np.zeros(20)}
 monotone={'mean_abs':np.zeros(20),'P2':np.zeros(20)}
 for q in arr:
  emissions+=q['emissions'];flights+=q['flights'];joint+=q['joint']
  for i,r in enumerate(q['arrival']):
   arrival[i]+=np.array([r['incoming_integrated_H_I_per_baryon'],r['incoming_integrated_He_I_per_baryon'],
     r['incoming_integrated_He_II_per_baryon'],r['incoming_integrated_Li_I_per_baryon'],
     r['primary_electron_eV_per_baryon'],r['binding_eV_per_baryon']])
  R=q['result'];total+=R['integrated_conditional_source_pairs_per_baryon']
  for k,v in R['integrated_conditional_per_baryon'].items():integrated[k]=integrated.get(k,0)+v
  for typ,d in [('positive',positive),('monotone',monotone)]:
   for k in d:d[k]+=np.array(R['global_linear_generator_integrals_for_chunk_combine'][typ][k])
 arrivals=[]
 for i,v in enumerate(arrival):
  arrivals.append(dict(first_absorption_interval=i,arrival_z_high=emissions[0]['z_emission'] if i==0 else float(21*np.exp(-(i)*np.log(7)/192)-1),
    arrival_z_low=float(21*np.exp(-(i+1)*np.log(7)/192)-1),
    incoming_integrated_H_I_per_baryon=float(v[0]),incoming_integrated_He_I_per_baryon=float(v[1]),
    incoming_integrated_He_II_per_baryon=float(v[2]),incoming_integrated_Li_I_per_baryon=float(v[3]),
    primary_electron_eV_per_baryon=float(v[4]),binding_eV_per_baryon=float(v[5])))
 assert len(emissions)==193 and len(flights)==18528 and len(joint)==4825
 # Ensure exactly one source grid, not a different spectrum independently at every epoch.
 bounds={}
 for typ,d in [('positive',positive),('monotone',monotone)]:
  a=d['mean_abs'];b=d['P2']
  bounds[typ]={'global_ionization_count_per_baryon':[float(a.min()),float(a.max())],
   'global_P_two_absorption_events_per_baryon':[float(b.min()),float(b.max())],
   'generator_argmax':int(np.argmax(a))+1,'generator_argmin':int(np.argmin(a))+1}
 base=arr[0]['result'];base['counts']['computed_emission_epochs']=len(emissions);base['counts']['emission_arrival_pairs']=len(flights);base['counts']['pair_channel_rows']=len(joint)
 base['integrated_conditional_source_pairs_per_baryon']=float(total)
 base['integrated_conditional_per_baryon']={k:float(v) for k,v in integrated.items()}
 input_eV=total*60.922559447552
 accounted=sum(integrated[k] for k in ['absorbed_primary_electron_eV','absorbed_binding_eV','cosmological_redshift_work_eV','survivor_eV_at_z2'])
 if abs(input_eV-accounted)>2e-13*input_eV:raise AssertionError('JOIN_ENERGY')
 if abs(arrival[:,:4].sum()-integrated['mean_absorptions_per_pair'])>2e-13*integrated['mean_absorptions_per_pair']:raise AssertionError('JOIN_PHOTON_COUNTS')
 base['energy_conservation']={'input_eV_per_baryon':float(input_eV),'accounted_eV_per_baryon':float(accounted),
 'residual_eV_per_baryon':float(input_eV-accounted),'redshift_work_is_not_heat':True}
 base['global_shape_cone_bounds']=bounds
 base['global_linear_generator_integrals_for_chunk_combine']={t:{k:v.tolist() for k,v in d.items()} for t,d in [('positive',positive),('monotone',monotone)]}
 base['execution']={'method':'six serial 193-epoch source-owned chunks (not 6 independent investigations)',
  'chunks':spans,'spectral_gauss_order':order,'cell_substeps':substeps}
 o=ROOT/'results';o.mkdir(exist_ok=True)
 for name,rows in [('EMISSIONS_193.csv',emissions),('FIRST_FLIGHT_KERNEL.csv',flights),('JOINT_OUTCOMES_4825.csv',joint),('ABSORPTION_ARRIVALS_192.csv',arrivals)]:write_csv(o/name,rows)
 (o/'RESULT.json').write_text(json.dumps(base,indent=2,sort_keys=True,ensure_ascii=False)+'\n')
 print(json.dumps({'counts':base['counts'],'integrated':base['integrated_conditional_per_baryon'],
 'energy':base['energy_conservation'],'bounds':bounds},indent=2),flush=True)
 return base
if __name__=='__main__':combine()
