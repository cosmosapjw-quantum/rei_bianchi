"""Create F08 artifacts only from complete independently checked actual histories."""
import pathlib,json,csv,gzip,hashlib,math,shutil,io
import numpy as np
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=pathlib.Path.cwd();P=ROOT/'.cuh/fastest-track/REI-F08-PAIRED';OUT=ROOT/'runs/rei_fastest_v1/paired'
labels=['T0_FLRW','T0_BI','T0_EPS_HALF','T1_FLRW','T1_BI','T2_FLRW','T2_BI','S0_FLRW','S0_BI','S2_FLRW','S2_BI','A0_FLRW','A0_BI','A2_FLRW','A2_BI']
fields=['time_s','x_HII','x_HeII','x_HeIII','temperature_K','gamma_HI_per_s','gamma_HeI_per_s','gamma_HeII_per_s','photon_n','photon_u_ev_per_h','lower_guard_n','lower_guard_u','w_ev_per_h','escape_ev_per_h','redshift_work_ev_per_h','thermal_work_ev_per_h','source_n','source_u','absorbed_n','local_bound','public_width','ledger']
data={};sources=[];receipts={};rawpaths={};failed_candidates=[];electron_data={}
initial=json.loads((ROOT/'configs/rei_fastest_v1/science_scenario_v1.json').read_text())['initial_state'];nh0=initial['nH0_cm3'];nhe0=nh0*initial['fHe'];x0=[initial['fractions'][k] for k in ['HII','HeII','HeIII']];assert nh0==1e-4 and initial['fHe']==.083 and x0==[.9,.3,.6]
def electron_row(t,nh,nhe,x,bounds):
 down=lambda v:math.nextafter(v,-math.inf);up=lambda v:math.nextafter(v,math.inf)
 ne=nh*x[0]+nhe*(x[1]+2*x[2])
 lo=down(down(nh*bounds[0][0])+down(nhe*down(bounds[1][0]+down(2*bounds[2][0]))))
 hi=up(up(nh*bounds[0][1])+up(nhe*up(bounds[1][1]+up(2*bounds[2][1]))))
 assert 0<=lo<=ne<=hi
 return [t,nh,nhe,ne,lo,hi,1.]
for label in labels:
 directory=P/'whole/T0_FLRW' if label=='T0_FLRW' else P/'whole-matched'/label/label
 old_directory=directory
 repair=P/'conservative-candidate'/('whole-'+label)/label
 if repair.exists() and (repair/'independent_history_receipt.json').exists():
  execution=json.loads((P/'conservative-candidate'/(label+'-repair-execution.json')).read_text())
  assert execution['producer_exit_code']==0 and execution['independent_exit_code']==0
  old_summary=json.loads((old_directory/'summary.json').read_text());assert old_summary['cumulative_u_residual']>1e-12 or old_summary['cumulative_n_residual']>1e-12
  failed_candidates.append({'run':label,'original_raw_local_path':str((old_directory/'trials.jsonl').relative_to(ROOT)),'original_raw_sha256':hashlib.sha256((old_directory/'trials.jsonl').read_bytes()).hexdigest(),'original_summary':old_summary,'repair_execution':execution,'original_failure_rewritten':False})
  directory=repair
 receipt=json.loads((directory/'independent_history_receipt.json').read_text());assert receipt['status']=='WHOLE_HISTORY_COMPONENT_INDEPENDENT_PASS' and len(receipt['runs'])==1
 summary=json.loads((directory/'summary.json').read_text());assert summary['time_s']==1e13 and summary['status']=='COMPLETE_HISTORY_CANDIDATE';rows=[];electrons=[electron_row(0.,nh0,nhe0,x0,[[x,x] for x in x0])]
 for line in (directory/'trials.jsonl').open():
  r=json.loads(line)
  if not r['accepted']:continue
  rows.append([r['time_s'],*r['fractions'],r['temperature_K'],*r['gamma_per_s'],*[r[k] for k in fields[8:]]])
  nh=r['audits'][2]['n_h_cm3'];nhe=nh*.083;x=r['fractions'];bounds=r['gas_parent'];ne=nh*x[0]+nhe*(x[1]+2*x[2])
  electrons.append(electron_row(r['time_s'],nh,nhe,x,bounds))
 a=np.array(rows);assert len(a)==summary['accepted'];data[label]=a;electron_data[label]=np.array(electrons);receipts[label]=receipt;rawpaths[label]=directory
 # Compiled source identities are actual per-run evidence, including original baseline.
 identity=(directory.parent/'source_identity.bin').read_bytes();offset=0;parts={}
 while offset<len(identity):
  n=int.from_bytes(identity[offset:offset+8],'little');offset+=8;name=identity[offset:offset+n].decode();offset+=n;n=int.from_bytes(identity[offset:offset+8],'little');offset+=8;body=identity[offset:offset+n];offset+=n;parts[name]=hashlib.sha256(body).hexdigest()
 assert parts['scenario']=='c83d2d43adda663707f99af2b45576eb4478cd94d3440a21fd21eaed32b5f2c1'
 sources.append({'run':label,'source_identity_sha256':hashlib.sha256(identity).hexdigest(),'source_parts':parts,'raw_sha256':hashlib.sha256((directory/'trials.jsonl').read_bytes()).hexdigest(),'accepted':summary['accepted'],'rejected':summary['rejected'],'raw_bytes':(directory/'trials.jsonl').stat().st_size,'raw_preserved_local_path':str((directory/'trials.jsonl').relative_to(ROOT)),'raw_publication':'LOCAL_COMPLETE_RAW_PUBLIC_COMPACT_CURVES_AND_PROOF_RECEIPTS'})
# All fixed model/geometry/atomic inputs are byte-identical. Repaired point
# implementations are separately recorded; they retain the original certified
# nonlinear root map and use the same frozen external MPFI proof.
for name in sources[0]['source_parts']:
 if name not in ['paired_history','paired_runtime','coupled_primary']:
  assert len({s['source_parts'][name] for s in sources})==1,('FIXED_MODEL_INPUT_CHANGED',name)
if failed_candidates:
 candidate=(P/'conservative-candidate/coupled_primary.rs').read_bytes()
 original=(P/'whole-original-source/coupled_primary.txt').read_bytes()
 assert candidate.startswith(original),'ORIGINAL_COUPLED_MAP_NOT_EXACT_PREFIX'
 assert hashlib.sha256(original).hexdigest()==sources[0]['source_parts']['coupled_primary']
 assert all(item['repair_execution']['scientific_gate']==1e-12 for item in failed_candidates)
OUT.mkdir(exist_ok=False);(OUT/'curves').mkdir();(OUT/'consumer_inputs').mkdir();(OUT/'receipts').mkdir();(OUT/'source_identities').mkdir();shutil.copyfile(P/'plot_paired_history.py',OUT/'plot_paired_history.py')
for label,a in data.items():
 directory=rawpaths[label]
 with (OUT/'curves'/(label+'.csv.gz')).open('wb') as raw:
  with gzip.GzipFile(fileobj=raw,mode='wb',mtime=0) as compressed:
   text=io.TextIOWrapper(compressed,encoding='utf-8',newline='');writer=csv.writer(text);writer.writerow(fields);writer.writerows(a);text.flush();text.detach()
 with gzip.open(OUT/'consumer_inputs'/(label+'-electron_density.csv.gz'),'wt',newline='') as file:
  writer=csv.writer(file);writer.writerow(['normal_time_s','nH_proper_cm3','nHe_proper_cm3','ne_proper_cm3','ne_conditional_lo','ne_conditional_hi','D_gas_normal_observer']);writer.writerows(electron_data[label])
 for filename in ['summary.json','header.jsonl','checkpoint.dat','independent_history_receipt.json']:shutil.copyfile(directory/filename,OUT/'receipts'/(label+'-'+filename))
 shutil.copyfile(directory.parent/'source_identity.bin',OUT/'source_identities'/(label+'.bin'))
with (OUT/'paired_history.csv').open('w',newline='') as file:
 writer=csv.writer(file);writer.writerow(['run',*fields]);writer.writerows([label,*a[-1]] for label,a in data.items())
# Common physical endpoints only. Report discretization differences, not a continuum bound.
def compare(label,reference):
 a=data[label];b=data[reference]
 if len(a)==len(b):assert np.array_equal(a[:,0],b[:,0]),('UNMATCHED_TIME_AXIS',label,reference)
 elif len(a)%len(b)==0:
  a=a[len(a)//len(b)-1::len(a)//len(b)];assert np.array_equal(a[:,0],b[:,0]),('UNMATCHED_TIME_REFINEMENT',label,reference)
 else:raise AssertionError(('UNMATCHED_TIME_GRID',label,reference))
 delta=a[:,1:]-b[:,1:];return {'candidate':label,'reference':reference,'matched_endpoint_count':len(b),'max_abs_by_observable':dict(zip(fields[1:],np.max(np.abs(delta),axis=0).tolist())),'final_difference_by_observable':dict(zip(fields[1:],delta[-1].tolist()))}
errors={'temporal':[],'spectral':[],'angular':[],'kind':'Measured discrete differences at matched physical endpoints; no rigorous continuum/model/fit/observational uncertainty claim','physical_fit_error':'NOT_MEASURED','model_error':'NOT_MEASURED','QV':'NOT_EVALUABLE','scientific_admission':'HOLD'}
for geo in ['FLRW','BI']:
 errors['temporal'] += [compare('T1_'+geo,'T0_'+geo),compare('T2_'+geo,'T1_'+geo)]
 errors['spectral'] += [compare('S0_'+geo,'T1_'+geo),compare('S2_'+geo,'T1_'+geo)]
 errors['angular'] += [compare('A0_'+geo,'T1_'+geo),compare('A2_'+geo,'T1_'+geo)]
# Resolve the geometry residual itself as well as individual histories.
def paired_compare(candidate,reference):
 ca=data[candidate+'_BI'];cf=data[candidate+'_FLRW'];ra=data[reference+'_BI'];rf=data[reference+'_FLRW']
 assert np.array_equal(ca[:,0],cf[:,0]) and np.array_equal(ra[:,0],rf[:,0])
 if len(ca)!=len(ra):
  assert len(ca)%len(ra)==0;stride=len(ca)//len(ra);ca=ca[stride-1::stride];cf=cf[stride-1::stride]
 assert np.array_equal(ca[:,0],ra[:,0])
 delta=(ca[:,1:]-cf[:,1:])-(ra[:,1:]-rf[:,1:])
 return {'candidate_pair':candidate,'reference_pair':reference,'matched_endpoint_count':len(ra),'max_abs_residual_change_by_observable':dict(zip(fields[1:],np.max(np.abs(delta),axis=0).tolist())),'final_residual_change_by_observable':dict(zip(fields[1:],delta[-1].tolist()))}
errors['paired_residual_resolution']={axis:[paired_compare(a,b) for a,b in pairs] for axis,pairs in {'temporal':[('T1','T0'),('T2','T1')],'spectral':[('S0','T1'),('S2','T1')],'angular':[('A0','T1'),('A2','T1')]}.items()}
errors['lower_guard_scope']='Passive discretization export, not a physical source-tail measurement; included in N/U ledgers and resolution comparisons'
errors['geometry_difference']=compare('T0_BI','T0_FLRW');errors['weak_shear_half']=compare('T0_EPS_HALF','T0_FLRW');errors['epsilon_zero']={'status':'EXACT_SAME_PRESCRIBED_DISCRETE_INPUT','reused':'T0_FLRW','duplicate_history_launched':False,'native_zero_shear_finite_regression':'PASS'}
(OUT/'difference_error_ledger.json').write_text(json.dumps(errors,indent=2)+'\n');(OUT/'source_manifest.json').write_text(json.dumps(sources,indent=2)+'\n')
fig,axes=plt.subplots(3,2,figsize=(11,10),sharex=True)
for geo,color in [('FLRW','#174A7E'),('BI','#B64624')]:
 a=data['T0_'+geo];t=a[:,0]/1e13
 for ax,column,title in [(axes[0,0],1,'H ionized fraction'),(axes[0,1],4,'Temperature (K)'),(axes[1,0],5,'Gamma HI (s^-1)'),(axes[1,1],8,'Photons per H')]:ax.plot(t,a[:,column],color=color,label=geo,lw=1.3);ax.set_title(title)
f=data['T0_FLRW'];b=data['T0_BI'];e=data['T0_EPS_HALF'];assert np.array_equal(f[:,0],b[:,0]) and np.array_equal(f[:,0],e[:,0]);t=f[:,0]/1e13
axes[2,0].plot(t,b[:,1]-f[:,1],label='epsilon=.01',color='#B64624');axes[2,0].plot(t,e[:,1]-f[:,1],label='epsilon=.005',color='#548C2F');axes[2,0].set_title('Bianchi - FLRW xHII (discrete)')
for label,color in [('T0_FLRW','#174A7E'),('T0_BI','#B64624')]:
 a=data[label];axes[2,1].plot(a[:,0]/1e13,a[:,21],label=label,color=color)
axes[2,1].axhline(1e-12,color='grey',ls='--',lw=.8);axes[2,1].set_yscale('log');axes[2,1].set_title('Per-step ledger residual (gate 1e-12)')
for ax in axes.flat:ax.grid(alpha=.2);ax.legend(fontsize=8);ax.ticklabel_format(axis='x',style='plain')
for ax in axes[-1]:ax.set_xlabel('Elapsed time / 1e13 s')
fig.suptitle('Prescribed homogeneous S0 - matched atomic realization\nCase A HG + DR + primary line source; HH/RCT/CR OFF; physical admission HOLD',fontsize=12);fig.tight_layout(rect=[0,0,1,.94]);fig.savefig(OUT/'paired_history.png',dpi=180);fig.savefig(OUT/'paired_history.pdf');plt.close(fig)
result={'status':'PRESCRIBED_DISCRETE_PAIRED_HISTORY_INDEPENDENT_PASS','runs':15,'accepted_trials':sum(len(a) for a in data.values()),'completed_interval_s':[0,1e13],'source_registry':'source_manifest.json','proper_electron_density_inputs':'consumer_inputs/*-electron_density.csv.gz; conditional on actual binary stage density; normal-time seconds; no observer tail assumed','raw_availability':'Complete original JSONL preserved at local source_manifest paths; compact curves and proof receipts published; raw bytes not in Git','separate_resolution_effects':'difference_error_ledger.json','figure':'paired_history.png','full_proofs':{k:v['runs'][0] for k,v in receipts.items()},'observational_reionization_claim':False,'physical_fit_error':'NOT_MEASURED','continuum_error_bound':'NOT_ESTABLISHED','QV':'NOT_EVALUABLE','scientific_admission':'HOLD','failed_candidate_repairs':failed_candidates,'point_implementation_variants':'Original Picard output and qualified conservative compensated variant; same externally verified nonlinear stage map, fixed model and unchanged scientific gates'};(OUT/'campaign_summary.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
