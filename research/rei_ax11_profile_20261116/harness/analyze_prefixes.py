#!/usr/bin/env python3
"""Source-qualified short-prefix comparisons. Empirical discrepancies only."""
from pathlib import Path
import numpy as np
from scipy.interpolate import PchipInterpolator
import csv,json,gzip,hashlib,sys,shutil,statistics
profile=Path(sys.argv[1]);prefix=Path(sys.argv[2]);out=Path(sys.argv[3]);out.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(n,v):(out/n).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
obs=['x_HII','x_HeII','x_HeIII','temperature_K']
def history(d):
 rows=list(csv.DictReader((d/'history.csv').open()))
 h={k:np.asarray([float(x[k]) for x in rows]) for k in ['a','time_s','zbar',*obs]}
 assert np.all(np.diff(h['a'])>0) and np.all(np.diff(h['time_s'])>0)
 return h
dirs={d.name:d for parent in [profile/'results',prefix/'time_preflight_results',prefix/'grid_preflight_results'] for d in parent.iterdir() if d.is_dir()}
valid={name:history(d) for name,d in dirs.items() if json.loads((d/'window_summary.json').read_text())['delta_counts']['accepted']>0}
summaries={name:json.loads((d/'window_summary.json').read_text()) for name,d in dirs.items()}
for name,d in dirs.items():
 if d.parent==profile/'results':continue
 destination=out/'native_receipts'/name;destination.mkdir(parents=True,exist_ok=True)
 for f in ['window_summary.json','checkpoint.start.txt','checkpoint.end.txt','config.cfg','effective_resource_config.cfg']:
  shutil.copyfile(d/f,destination/f)
 e=out/'native_data';e.mkdir(exist_ok=True)
 for f in ['raw/error_components.csv','history.csv']:
  (e/(name+'_'+Path(f).name+'.gz')).write_bytes(gzip.compress((d/f).read_bytes(),mtime=0))

pair_specs=[
 ('dt','PLUS_minus_ZERO',['PLUS_IC_lazy_0','PLUS_T1_ORIGINAL_START','PLUS_T2_FLOOR_START'],['ZERO_IC_lazy_0','ZERO_T1_ORIGINAL_START','ZERO_T2_FLOOR_START'],'matched_original_IC'),
 ('dE','PLUS_minus_ZERO',['PLUS_IC_lazy_0','PLUS_E32','PLUS_E64'],['ZERO_IC_lazy_0','ZERO_E32','ZERO_E64'],'matched_original_IC'),
 ('dmu','PLUS_minus_fixed_ZERO8',['PLUS_IC_lazy_0','PLUS_A16','PLUS_A32'],['ZERO_IC_lazy_0']*3,'fixed_ZERO_mu8_reference; q0angularimplementationroundoffnotmeasuredhere'),
 ('dmu','MINUS_minus_fixed_ZERO8',['MINUS_A8','MINUS_A16','MINUS_A32'],['ZERO_IC_lazy_0']*3,'fixed_ZERO_mu8_reference; q0angularimplementationroundoffnotmeasuredhere')]
paired={};long=[]
for axis,pair,qnames,znames,refscope in pair_specs:
 for coordinate in ['fixed_a','equal_elapsed_proper_time']:
  names=qnames+znames;hh=[valid[x] for x in names]
  if coordinate=='fixed_a':
   low=max(h['a'][0] for h in hh);high=min(h['a'][-1] for h in hh)
   grid=np.linspace(np.log(low),np.log(high),1001); key=lambda h:np.log(h['a']);physical=np.exp(grid)
  else:
   low=max(h['time_s'][0] for h in hh);high=min(h['time_s'][-1] for h in hh)
   # Reuse the original owner consumer: uniform ln(a_0) reference grid,
   # mapped to elapsed proper time on the common time interval.
   h0=valid[znames[0]];l0=np.log(h0['a'])
   lgrid=np.linspace(np.interp(low,h0['time_s'],l0),np.interp(high,h0['time_s'],l0),1001)
   grid=np.interp(lgrid,l0,h0['time_s']);grid[0]=low;grid[-1]=high
   key=lambda h:h['time_s'];physical=grid
  def interp(name,field,method):
   h=valid[name];x=np.log(h['a'])
   if coordinate=='fixed_a':g=grid
   else:
    g=np.interp(grid,h['time_s'],x) if method=='linear' else PchipInterpolator(h['time_s'],x,extrapolate=False)(grid)
    # Exact supplied endpoint identities, not extrapolation or clamping of
    # an outside sample. Polynomial evaluation can otherwise overshoot one ulp.
    g[grid==h['time_s'][0]]=x[0];g[grid==h['time_s'][-1]]=x[-1]
   assert np.isfinite(g).all() and g.min()>=x[0] and g.max()<=x[-1],(coordinate,name,field,method,'outside native domain')
   if field=='a':return np.exp(g)
   if field=='zbar':return 1.0/np.exp(g)-1.0
   if field=='time_s' and coordinate=='equal_elapsed_proper_time':return grid
   value=np.interp(g,x,h[field]) if method=='linear' else PchipInterpolator(x,h[field],extrapolate=False)(g)
   assert np.isfinite(value).all(),(coordinate,name,field,method)
   return value
  item={'axis':axis,'pair':pair,'coordinate':coordinate,'reference_scope':refscope,'q_runs':qnames,'reference_runs':znames,
       'common_coordinate_range':[float(np.exp(grid[0])),float(np.exp(grid[-1]))] if coordinate=='fixed_a' else [low,high],
       'grid_points':1001,'method':'X linear in ln(a); proper-time grid is uniform ln(a_0) mapped through original ZERO clock; t inverted within native ln(a) brackets. PCHIP disagreement is a diagnostic, not an interpolation error bound','observables':{}}
  for field in obs:
   r=np.array([interp(q,field,'linear')-interp(z,field,'linear') for q,z in zip(qnames,znames)])
   rp=np.array([interp(q,field,'pchip')-interp(z,field,'pchip') for q,z in zip(qnames,znames)])
   d01=np.abs(r[0]-r[1]);d12=np.abs(r[1]-r[2]);floor=.01 if field=='temperature_K' else 1e-7
   scale=.1*np.maximum(np.max(np.abs(r),axis=0),floor)
   absolute_d12=max(float(np.max(np.abs(interp(qnames[1],field,'linear')-interp(qnames[2],field,'linear')))),float(np.max(np.abs(interp(znames[1],field,'linear')-interp(znames[2],field,'linear')))))
   item['observables'][field]={'max_abs_response_by_level':np.max(np.abs(r),axis=1).tolist(),'max_D01':float(d01.max()),'max_D12':float(d12.max()),
      'max_D01_over_floor_target':float(np.max(d01/scale)),'max_D12_over_floor_target':float(np.max(d12/scale)),
      'absolute_single_history_D12':absolute_d12,'max_linear_PCHIP_response_difference':float(np.max(np.abs(r-rp))),
      'numerical_discrepancy_below_declared_floor_target':bool(np.all(d01<=scale)&np.all(d12<=scale)),
      'response_resolution_status':'BELOW_DECLARED_RESPONSE_FLOOR' if np.max(np.abs(r))<floor else 'REQUIRES_FULL_HISTORY_AND_COMPONENT_ERROR',
      'empirical_order':'NOT_ASSIGNED: adaptive nonuniform steps and interpolation/cancellation require more than a ratio of maxima'}
   zq=[interp(q,'zbar','linear') for q in qnames];zz=[interp(z,'zbar','linear') for z in znames]
   aq=[interp(q,'a','linear') for q in qnames];az=[interp(z,'a','linear') for z in znames]
   tq=[interp(q,'time_s','linear') for q in qnames];tz=[interp(z,'time_s','linear') for z in znames]
   for i in range(len(grid)):
    long.append([axis,pair,coordinate,i,float(physical[i]),field,*[float(v[i]) for v in aq],*[float(v[i]) for v in az],*[float(v[i]) for v in tq],*[float(v[i]) for v in tz],*[float(v[i]) for v in zq],*[float(v[i]) for v in zz],*[float(v[i]) for v in r],float(d01[i]),float(d12[i]),float(scale[i])])
  paired[axis+'__'+pair+'__'+coordinate]=item
with gzip.open(out/'PAIRED_PREFIX_RESPONSES.csv.gz','wt',newline='') as f:
 w=csv.writer(f);w.writerow(['axis','pair','coordinate','grid_index','coordinate_value','observable','q_a_L0','q_a_L1','q_a_L2','reference_a_L0','reference_a_L1','reference_a_L2','q_t_s_L0','q_t_s_L1','q_t_s_L2','reference_t_s_L0','reference_t_s_L1','reference_t_s_L2','q_z_L0','q_z_L1','q_z_L2','reference_z_L0','reference_z_L1','reference_z_L2','response_L0','response_L1','response_L2','D01','D12','floor_target']);w.writerows(long)

# Actual step density on a common late part of the short dt prefix. This avoids
# inferring sqrt(target) scaling from the zero-photon scalar illustration.
time_names=['PLUS_IC_lazy_0','PLUS_T1_ORIGINAL_START','PLUS_T2_FLOOR_START'];end=min(valid[n]['a'][-1] for n in time_names);start=valid[time_names[0]]['a'][0]
ell=np.log(end/start);lower=start*np.exp(.75*ell);density={}
for name in time_names:
 h=valid[name];mask=(h['a'][:-1]>=lower)&(h['a'][1:]<=end);steps=np.diff(np.log(h['a']))[mask]
 density[name]={'common_a_range':[float(lower),float(end)],'steps_in_range':int(mask.sum()),'median_native_dln_a':float(np.median(steps)),'min_native_dln_a':float(steps.min()),'max_native_dln_a':float(steps.max())}
base=density[time_names[0]]['median_native_dln_a']
for name in time_names:density[name]['baseline_to_level_step_density_ratio']=base/density[name]['median_native_dln_a']

cost={}
for name,d in dirs.items():
 s=summaries[name];n=s['delta_counts']['accepted'];tr=s['delta_counts']['attempts']
 if n==0:
  cost[name]={'status':s['status'],'accepted':0,'trials':tr,'RHS':s['delta_counts']['rhs_evaluations'],'fresh_wall_s':s['fresh_evolution_wall_s']};continue
 physical=sum((d/f).stat().st_size for f in ['history.csv','abundances.csv','spectra.csv','ledgers.csv','feedback.csv'])
 cost[name]={'accepted':n,'trials':tr,'RHS':s['delta_counts']['rhs_evaluations'],'a_end':s['a_end'],'fresh_wall_s':s['fresh_evolution_wall_s'],'wall_per_accepted_s':s['fresh_evolution_wall_s']/n,'wall_per_trial_s':s['fresh_evolution_wall_s']/tr,'five_table_bytes':physical,'five_table_bytes_per_accepted_including_initial_terminal':physical/n}
receipt=json.loads((prefix/'GRID_PREFLIGHT_JOB_RECEIPT.json').read_text())
total={'status':'SHORT_PREFIX_DATA_ACCEPTED_SCOPED','original_DAG':'10/17','expansion_DAG':'28/88','AX11_complete':False,
 'native_windows':len(summaries),'completed_windows':sum(s['status']=='ACCEPTED_WINDOW_COMPLETE' for s in summaries.values()),
 'preserved_expected_T2_start_failures':sum(s['status']=='AXBI_REJECT_CAP' for s in summaries.values()),
 'new_accepted_with_benchmark_repetitions':sum(s['delta_counts']['accepted'] for s in summaries.values()),
 'new_trials_including_failures':sum(s['delta_counts']['attempts'] for s in summaries.values()),
 'new_RHS_including_failures':sum(s['delta_counts']['rhs_evaluations'] for s in summaries.values()),
 'cumulative_native_job_wall_s':receipt['wall_elapsed_s'],'cumulative_child_CPU_s':sum(x['cpu_s'] for x in receipt['records']),
 'native_child_process_starts':len(receipt['records']),'old_cumulative_cost':'UNKNOWN unchanged',
 'all_three_axis_full_histories':'NOT_RUN','short_prefixes_do_not_close_AX11':True,
 'angular_reference_limitation':'q0mu8commonreference; q0higher-mu roundoff not measured; no full angular paired gate issued',
 'milestones':{str(x):'NOT_REACHED_IN_SHORT_PREFIX' for x in [.1,.5,.9]}}
save('PAIRED_PREFIX_ERROR_SUMMARY.json',{'scope':'original-IC prefix only, never zbar20-to4 convergence','results':paired})
save('STEP_DENSITY_AND_COST.json',{'time_step_density':density,'window_costs':cost,'forecast_warning':'Prefix step-density ratios are not global workbounds; lateionization/thermal costs unmeasured atrefinedlevels. Wrapper trace IO contributes to measuredwall, and fullproduction outputdirectory growth may addcost.'})
save('PREFIX_OUTCOME.json',total);save('CUMULATIVE_NATIVE_RECEIPT.json',receipt)
for f in ['TIME_PREFLIGHT_BINDINGS.json','TIME_PREFLIGHT_OUTCOMES.json','TIME_PREFLIGHT_STATUS.json','GRID_PREFLIGHT_BINDINGS.json','GRID_PREFLIGHT_OUTCOMES.json','GRID_PREFLIGHT_STATUS.json']:
 shutil.copyfile(prefix/f,out/f)
print(json.dumps(total,indent=2));print(json.dumps(density,indent=2))
for k,v in paired.items():print(k,{x:{'D01':z['max_D01'],'D12':z['max_D12'],'interp_spread':z['max_linear_PCHIP_response_difference'],'maxR':max(z['max_abs_response_by_level'])} for x,z in v['observables'].items()})
