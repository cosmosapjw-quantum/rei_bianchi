"""Bound short-history loader; unchanged C9 analytic PL reconstruction engine."""
import array,csv,hashlib,importlib.util,json,math,statistics,argparse
from pathlib import Path
FIELDS={'x_HI':'x_HI','x_HII':'x_HII','x_HeI':'x_HeI','x_HeII':'x_HeII','x_HeIII':'x_HeIII','ne_cm3':'ne_proper_cm3','Tgas_K':'temperature_K','U0_eV_per_H':'J0_photon_u_eV_per_H','U2_eV_per_H':'J2_photon_u_eV_per_H','photonN_per_H':'photon_n_per_H','Gamma_HI_per_s':'Gamma_HI_per_s','Gamma_HeI_per_s':'Gamma_HeI_per_s','Gamma_HeII_per_s':'Gamma_HeII_per_s','elapsed_time_s':'time_s'}
SPECIES=['H_I','H_II','He_I','He_II','He_III','electron']
def require(ok,msg):
 if not ok:raise ValueError(msg)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(desc):
 digest=hashlib.sha256()
 with Path(desc['path']).open('rb') as f:
  def lines():
   for l in f:digest.update(l);yield l.decode()
  yield from csv.DictReader(lines())
 require(digest.hexdigest()==desc['sha256'],'INPUT_SHA_MISMATCH')
def load(spec):
 s={k:array.array('d') for k in ['L','xe',*FIELDS,*['Y_'+sp for sp in SPECIES]]};temps=[]
 for row in rows(spec['history']):
  require(row['case_id']==spec['case'],'CASE_MISMATCH');a=float(row['a']);nh=float(row['nH_proper_cm3']);require(a>0 and nh>0,'LOG_DIVISION_DOMAIN');L=math.log(a);t=float(row['time_s']);require(not s['L'] or (L>s['L'][-1] and t>s['elapsed_time_s'][-1]),'ROW_CHRONOLOGY');s['L'].append(L);s['xe'].append(float(row['ne_proper_cm3'])/nh);temps.append(float(row['temperature_K']))
  for field,col in FIELDS.items():s[field].append(float(row[col]))
 require(len(s['L'])==spec['expected_history_rows'] and s['elapsed_time_s'][0]==0,'ROWCOUNT_CLOCK_ORIGIN');group=[];index=0
 for row in rows(spec['abundances']):
  group.append(row)
  if len(group)!=6:continue
  require(index<len(s['L']) and [x['species_id'] for x in group]==SPECIES,'SIX_SPECIES');require(all(x['run_id']==spec['case'] and float(x['time_s'])==s['elapsed_time_s'][index] and float(x['Tgas_K'])==temps[index] and x['normalization_registry']=='BASELINE_H_HE_CHARGE_AND_BARYON_V1' for x in group),'ABUNDANCE_ALIGNMENT')
  for row in group:s['Y_'+row['species_id']].append(float(row['Ybaryon']))
  index+=1;group=[]
 require(not group and index==len(s['L']),'ABUNDANCE_COUNT');require(all(len(v)==len(s['L']) and all(math.isfinite(x) for x in v) for v in s.values()),'FINITE_SHAPE')
 ds=[b-a for a,b in zip(s['L'],s['L'][1:])];sort=sorted(ds);dist={'count':len(ds),'min':min(ds),'max':max(ds),'mean':statistics.mean(ds),'median':statistics.median(ds),'q10':sort[int(.1*(len(sort)-1))],'q90':sort[int(.9*(len(sort)-1))],'definition':'differences of actual stored binary64 ln(a) at accepted states'}
 return {'id':spec['id'],'series':s},dist
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--contract',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args();c=json.loads(args.contract.read_text());require(not args.output.exists(),'FRESH_OUTPUT');require(sha(__file__)==c['loader_sha256'],'LOADER_SHA');require(sha(c['engine']['path'])==c['engine']['sha256'],'ENGINE_SHA')
 for x in c['bound_summaries']:require(sha(x['path'])==x['sha256'],'SUMMARY_SHA')
 module=importlib.util.spec_from_file_location('c9_pair',c['engine']['path']);engine=importlib.util.module_from_spec(module);module.loader.exec_module(engine);args.output.mkdir();results={};flat=[]
 for pair in c['pairs']:
  ref,rd=load(pair['reference']);cand,cd=load(pair['candidate']);fields=[x for x in ref['series'] if x!='L'];require(len(fields)==21,'21_OBSERVABLES');d=engine.diagnose_pair(ref,cand,fields);matching=ref['series']['L'][0]==cand['series']['L'][0] and ref['series']['L'][-1]==cand['series']['L'][-1];complete=pair['reference']['complete'] and pair['candidate']['complete'] and matching;d['coverage_label']='FULL_REQUESTED_SHORT_INTERVAL_MATCHING_STORED_ENDPOINTS' if complete else 'PARTIAL_OVERLAP_ONLY_NO_FULL_REQUESTED_COMPARISON';d['requested_z_interval']=[20,19.8];d['accepted_interval_distributions']={'source009':rd,'source010':cd};d['controller_target_ratio']=.5;d['order_or_accuracy_claim']='NOT_ESTABLISHED';d['unit_annotation_source']='new short loader; shared C9 engine unchanged'
  for row in d['summary']:
   f=row['observable'];row['units']='s' if f=='elapsed_time_s' else 's^-1' if f.startswith('Gamma_') else 'cm^-3' if f=='ne_cm3' else 'K' if f=='Tgas_K' else 'eV/H' if f in ['U0_eV_per_H','U2_eV_per_H'] else '1';flat.append({'case':pair['case'],**row})
  results[pair['case']]=d
 status='DIAGNOSTIC_COMPARISON_COMPLETE_REVIEW_PENDING';receipt={'status':status,'engine':c['engine'],'loader_sha256':sha(__file__),'results':results,'scientific_admission':'NOT_ISSUED','agreement_tolerance':None,'environment_caveat':'source009 baseline LOCAL vs source010 NCP; exact ELF/source but CPU/libm/runtime floating environment not proved bitidentical; controller-target plus environment sensitivity, no exclusive causal/time-error attribution','solver_ledger_checkpoint_replays':0,'full_time_angular_energygrid_threshold_isotope_admission':'HOLD','baseline_native_checks':'reused independent source009 resultPASS','candidate_native_checks':'reused once-only source010 native summary'}
 (args.output/'COMPARISON.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
 with (args.output/'comparison_summary.csv').open('x',newline='') as f:w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
 (args.output/'REPORT.md').write_text('# Source010 controller-target sensitivity diagnostic\n\nSource009 baselines ran LOCAL; source010 runs NCP. Exact ELF and source match, while CPU/libm/runtime floating environment is not proved bitidentical. These results describe controller-target plus environment sensitivity, without exclusive causal or time-error attribution. No baseline rerun or extra parity gate was introduced.\n\nThe unchanged C9 engine compares 21 saved piecewise-linear reconstructions at common stored ln(a). Units for Gamma, photonN/H and elapsed proper time are assigned by this new loader. No time_s observable was sent to the engine. Full requested comparison requires matching complete stored endpoints; otherwise only overlap is labeled. No extrapolation, endpoint projection, agreement tolerance, solver-error bound or convergence order is asserted. Half local target does not establish a fixed step ratio. All native validation is reused from bound summaries.\n');print(json.dumps({'status':status,'pairs':2,'observables_each':21,'coverage':{k:v['coverage_label'] for k,v in results.items()}}))
if __name__=='__main__':main()
