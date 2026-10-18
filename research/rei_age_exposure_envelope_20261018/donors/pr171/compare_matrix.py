"""Separate reference sensitivity and native-to-matched-reference comparisons."""
import json,argparse
from pathlib import Path
import numpy as np
p=argparse.ArgumentParser();p.add_argument('root',type=Path);a=p.parse_args();root=a.root
THRESHOLD=.005
spec=['HI','HeI','HeII']
def read(d,name):return json.loads((root/d/name).read_text())
def complete(d):return (root/d/'solver_return.json').exists() and read(d,'solver_return.json')['status']=='SCOPED_NUMERICAL_EXECUTION_COMPLETE'
def rel(x,y):
 x=np.asarray(x,float);y=np.asarray(y,float);delta=abs(x-y)
 return np.where(y!=0,delta/np.where(y!=0,abs(y),1),np.where(delta==0,0,np.inf)).tolist()
def collect(d,native=False):
 e=read(d,'endpoint.json');s=read(d,'setup.json') if not native else None
 if native:return e,s
 return e,s
def compare(da,db,kind):
 ea,sa=collect(da,kind=='native_to_matched_reference');eb,sb=collect(db)
 fa=np.array(ea['flat']);fb=np.array(eb['flat']);la=np.array(ea['ledgers']);lb=np.array(eb['ledgers']);source=np.array(sb['source_inventory']).sum(axis=0)
 r=dict(kind=kind,left=da,right=db,finest_neighbor_target=THRESHOLD,species_fraction_relative=rel(fa[:3],fb[:3]),thermal_w_relative=rel(fa[3],fb[3]),temperature_relative=rel(ea['temperature_K'],eb['temperature_K']),survivor_N_relative=rel(ea['N'],eb['N']),survivor_U_relative=rel(ea['U'],eb['U']),survivor_N_source_normalized=abs(ea['N']-eb['N'])/source[0],survivor_U_source_normalized=abs(ea['U']-eb['U'])/source[1],quadrupole_difference_over_U=abs(ea['quadrupole_U_mu2_minus_third']-eb['quadrupole_U_mu2_minus_third'])/eb['U'],Gamma_relative=rel(ea['Gamma_s'],eb['Gamma_s']),heat_relative=rel(ea['heat_erg_per_absorber_s'],eb['heat_erg_per_absorber_s']),photo_events_relative=rel(la[4:7],lb[4:7]),RR_events_relative=rel(la[7:10],lb[7:10]),CI_events_relative=rel(la[10:13],lb[10:13]),DR_events_relative=rel(la[13],lb[13]),escape_CMB_photonwork_thermalwork_relative=rel(la[:4],lb[:4]))
 births_a=np.asarray(ea['birth_times_s'] if sa is None else sa['birth_times_s']);births_b=np.asarray(sb['birth_times_s']);age_a=ea['proper_time_s']-births_a;age_b=eb['proper_time_s']-births_b
 ca=np.array(ea['cohorts']);cb=np.array(eb['cohorts']);edge=np.linspace(0,max(age_a.max(),age_b.max()),17);hist_a=np.histogram(age_a,bins=edge,weights=ca[:,0])[0];hist_b=np.histogram(age_b,bins=edge,weights=cb[:,0])[0]
 r['age_bins_s']=edge.tolist();r['age_survivor_histogram_left']=hist_a.tolist();r['age_survivor_histogram_right']=hist_b.tolist();r['age_histogram_normalized_L1']=float(np.abs(hist_a/ea['N']-hist_b/eb['N']).sum());r['age_mean_s']=[float((age_a*ca[:,0]).sum()/ea['N']),float((age_b*cb[:,0]).sum()/eb['N'])];r['age_second_moment_s2']=[float((age_a**2*ca[:,0]).sum()/ea['N']),float((age_b**2*cb[:,0]).sum()/eb['N'])];r['age_mean_relative']=rel(*r['age_mean_s']);r['age_second_moment_relative']=rel(*r['age_second_moment_s2'])
 r['emitted_N_U_left']=ea.get('emitted_N_U') if sa is None else np.asarray(sa['source_inventory']).sum(axis=0).tolist();r['emitted_N_U_right']=source.tolist();r['emitted_N_U_relative']=rel(r['emitted_N_U_left'],source)
 metrics=np.r_[r['species_fraction_relative'],r['thermal_w_relative'],r['temperature_relative'],r['survivor_N_relative'],r['survivor_U_relative'],r['quadrupole_difference_over_U'],r['Gamma_relative'],r['heat_relative'],r['photo_events_relative'],r['RR_events_relative'],r['CI_events_relative'],r['DR_events_relative'],r['age_histogram_normalized_L1'],r['age_mean_relative'],r['age_second_moment_relative']]
 r['max_selected_endpoint_difference']=float(metrics.max());r['endpoint_target_observed_met']=bool(np.isfinite(metrics).all() and metrics.max()<=THRESHOLD);r['claim']='finite sensitivity only; no convergence order or full-history admission'
 if kind=='native_to_matched_reference':r['classification']='NATIVE_TO_REFERENCE_DIFFERENCE; native time error retained'
 elif 'angular' in da or 'angular' in db:
  r['classification']='REFERENCE_FLOOR_LIMITED';r['reference_floor_basis']='q0 accuracy/tight species-photo relative difference ~1.22e-9; matched q+ tight NOT_MEASURED'
 elif 'source' in da or 'source' in db:r['classification']='SOURCE_SUBDIVISION_TWO_LEVEL_SENSITIVITY_ONLY'
 elif 'age' in da or 'age' in db:r['classification']='AGE_REFINEMENT_HOLD' if not r['endpoint_target_observed_met'] else 'FINITE_AGE_NEIGHBOR_TARGET_OBSERVED'
 else:r['classification']='FINITE_TRANSPORT_NEIGHBOR_TARGET_OBSERVED' if r['endpoint_target_observed_met'] else 'TRANSPORT_REFINEMENT_HOLD'
 # Pre/post source-jump side labels are matched explicitly. Background x values
 # differ by at most binary64 clock rounding between old saved baselines.
 oa=read(da,'observations.json');ob=read(db,'observations.json');common=[]
 for b in ob:
  candidates=[v for v in oa if v['side']==b['side'] and abs(v['x']-b['x'])<=2e-15]
  if not candidates and kind=='native_to_matched_reference':candidates=[v for v in oa if v['side']=='pre' and abs(v['x']-b['x'])<=2e-15]
  if not candidates:continue
  av=min(candidates,key=lambda v:abs(v['x']-b['x']));ae=av['physical'];be=b['physical'];common.append(dict(x=b['x'],side=b['side'],clock_difference_ln_a=av['x']-b['x'],gas_abs=np.abs(np.array(ae['flat'][:4])-be['flat'][:4]).tolist(),N_relative=rel(ae['N'],be['N']),U_relative=rel(ae['U'],be['U']),Gamma_relative=rel(ae['Gamma_s'],be['Gamma_s']),heat_relative=rel(ae['heat_erg_per_absorber_s'],be['heat_erg_per_absorber_s'])))
 r['common_physical_observations']=common;r['observation_target_count']=len(ob);r['matched_observation_count']=len(common)
 return r
pairs=[('age8','age16'),('age16','age32'),('qplus_base','angular16'),('angular16','angular32'),('qplus_base','transport32'),('transport32','transport64'),('qplus_base','source16')]
result=dict(reference_to_reference=[],native_to_matched_reference=[],not_evaluable=[])
for x,y in pairs:
 if complete(x) and complete(y):result['reference_to_reference'].append(compare(x,y,'reference_to_reference'))
 else:result['not_evaluable'].append([x,y])
for d in ['age8','age16','age32','qplus_base','angular16','angular32','transport32','transport64','source16']:
 if (root/(d+'_native')/'endpoint.json').exists() and complete(d):result['native_to_matched_reference'].append(compare(d+'_native',d,'native_to_matched_reference'))
def finite_json(v):
 if isinstance(v,dict):return {k:finite_json(x) for k,x in v.items()}
 if isinstance(v,list):return [finite_json(x) for x in v]
 if isinstance(v,float) and not np.isfinite(v):return None
 return v
(root/'MATRIX_COMPARISON.json').write_text(json.dumps(finite_json(result),indent=2,allow_nan=False)+'\n')
for r in result['reference_to_reference']:print(r['left'],r['right'],r['max_selected_endpoint_difference'],r['endpoint_target_observed_met'])
