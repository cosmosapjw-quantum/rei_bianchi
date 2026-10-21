"""Assemble actual saved-data summary and case provenance; zero IVPs."""
import csv,hashlib,json
from pathlib import Path
import numpy as np
import atomic as at
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'results'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main(base=None):
 global BASE
 if base is not None:BASE=Path(base)
 m=json.loads((BASE/'MANIFEST.json').read_text());records=[];arrays={};receipts={}
 for c in m['cases']:
  p=BASE/'cases'/c['id'];r=json.loads((p/'RESULT.json').read_text());assert r['status']=='COMPLETED' and sha(p/'raw.npz')==r['raw_sha256'];receipts[c['id']]=r
  with np.load(p/'raw.npz',allow_pickle=False) as z:arrays[c['id']]={k:np.array(z[k]) for k in z.files}
  records.append({'case_id':c['id'],'kind':c['config']['kind'],'configuration':c['config'],'source_core_identity':m['source']['core_identity'],'source_files_sha256':m['source']['core_files_sha256'],'executed_runner_sha256':m['source']['runner_sha256'],'executed_source_kind':'SANDBOX_UNPUBLISHED_WITH_SHA256','execution_Git_commit':'NOT_A_GIT_EXECUTION; no publication SHA substituted','donor_repository':'cosmosapjw-quantum/BASS_HE','donor_commit':'e8bb035d31f59e34734947b9082bdbd60128b799','input_sha256':sha(p/'INPUT.json'),'attempt_sha256':sha(p/'ATTEMPT.json'),'result_sha256':sha(p/'RESULT.json'),'raw_sha256':r['raw_sha256'],'raw_bytes':r['raw_bytes'],'relative_raw_path':str((p/'raw.npz').relative_to(ROOT)),'realized_initial_axes':dict(zip(('signed_S_F0','P_m0','P_r0'),r['initial_axes'])),'method':'Radau','nfev':r['nfev'],'njev':r['njev'],'nlu':r['nlu'],'actual_rhs_calls':r['actual_rhs_calls'],'worker_cpu_s':r['worker_cpu_s'],'worker_wall_s':r['worker_wall_s'],'epochs':257,'z_range':[20.,2.],'argv':['python3','-B','code/run_pilot.py','--workers','4','--no-plots'],'versions':{'numpy':m['source']['numpy'],'scipy':m['source']['scipy']},'checks':r['checks'],'rate_policy':'ElementalElectronicEquality; source Verner1996 photo, Verner-Ferland1996 totalRR; HeI a; no CI/DR/CX','photo_parent_rows':['HI','HeI','HeII','LiI','LiII','LiIII'],'RR_product_labels':['H I','HeI a','HeII','LiI','LiII','LiIII']})
 (BASE/'CASE_PROVENANCE_LEDGER.json').write_text(json.dumps({'schema':'rei.hheli.case_provenance.v1','rows':records,'case_count':82,'unique_nominal':79,'combined_controls':3,'new_IVPs':82,'publication_identity':'Subsequent publication is separately recorded; not execution commit identity'},indent=2)+'\n')
 with (BASE/'CASE_PROVENANCE_LEDGER.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows({k:json.dumps(v,sort_keys=True,separators=(',',':')) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in records)
 nominal=[c for c in m['cases'] if c['config']['kind']!='combined_refinement'];raw=[arrays[c['id']] for c in nominal];allraw=list(arrays.values())
 def bounds(v):return [float(np.min(v)),float(np.max(v))]
 initial={k:bounds([r[k][0] for r in raw]) for k in ('signed_Sigma','Sigma_F','P_m','P_r','Pi_m','Pi_r','Pi_total')};final={k:bounds([r[k][-1] for r in raw]) for k in ('signed_Sigma','Sigma_F','P_m','P_r','Pi_m','Pi_r','Pi_total','ne_m3','tau_T')}
 canc=[]
 for c in nominal:
  if c['config']['kind']=='cancellation':
   r=arrays[c['id']];canc.append({'id':c['id'],'A_m':c['config']['A_m'],'A_r':c['config']['A_r'],'initial':{k:float(r[k][0]) for k in ('signed_Sigma','P_m','P_r','Pi_total')},'final':{k:float(r[k][-1]) for k in ('signed_Sigma','P_m','P_r','Pi_total')}})
 baseline=next(c for c in nominal if c['config']['Sigma_F0']==0 and c['config']['A_m']==0 and c['config']['A_r']==0 and c['config']['kind']=='grid');r=arrays[baseline['id']];history=[]
 for target in (20.,10.,8.,6.,4.,2.):
  i=int(np.argmin(abs(r['z']-target)));history.append({'requested_z':target,'stored_sample_index':i,'actual_saved_z':float(r['z'][i]),'selection':'exact endpoint' if target in (20.,2.) else 'nearest saved sample, no interpolation','charge_fractions':{name:r['conditional_f'][at.SLICES[name],i].tolist() for name in at.POPULATED},'ne_m3':float(r['ne_m3'][i]),'tau_T':float(r['tau_T'][i]),'T_K':float(r['T_K'][i]),'UV_f':at.forcing(float(r['z'][i]))[0],'Gamma_HI_over_H':float(5e-14*at.forcing(float(r['z'][i]))[0]/r['H_per_s'][i])})
 coverage=[]
 for i,name in enumerate(at.NAMES):coverage.append({'state':name,'minimum_Y':min(float(v['Y_Aq'][i].min()) for v in allraw),'maximum_Y':max(float(v['Y_Aq'][i].max()) for v in allraw),'identically_zero_all_samples_all_cases':all(np.all(v['Y_Aq'][i]==0) for v in allraw)})
 same={}
 for pair,a,b in [('H1_D','H1','D'),('He3_He4','He3','He4'),('Li6_Li7','Li6','Li7')]:same[pair]=max(float(np.max(abs(v['conditional_f'][at.SLICES[a]]-v['conditional_f'][at.SLICES[b]]))) for v in allraw)
 report={'schema':'rei.hheli.saved_data_science_summary.v1','nominal_cases':79,'computed_total':82,'initial_nominal_ranges':initial,'final_nominal_ranges':final,'cancellation_cases':canc,'baseline_case_id':baseline['id'],'baseline_charge_samples':history,'abundances_per_baryon':at.ABUNDANCES,'census_21':coverage,'Li_high_charge_analytic_zero_roundoff_max_abs_fraction':max(float(np.max(abs(v['conditional_f'][[15,16,19,20]]))) for v in allraw),'same_element_max_fraction_difference':same,'same_element_interpretation':'Identical elemental electronic rates and identical initial conditional charge fractions; separate isotope abundances, not isotope-specific spectroscopy','maximum_test_fluid_energy_ratio':max(float(v['test_fluid_energy_ratio'].max()) for v in allraw),'background_energy_definition':'Inherited massive+dust+radiation energy density, excluding Lambda; atomic rest mass already included in dust','minimum_fraction_all_cases':min(float(v['conditional_f'].min()) for v in allraw),'minimum_sampled_angular_brightness':min(v['diagnostics']['sampled_brightness_minimum'] for v in receipts.values()),'maximum_sampled_angular_minimum':max(v['diagnostics']['sampled_brightness_minimum'] for v in receipts.values()),'global_ne_m3_range':bounds(np.concatenate([v['ne_m3'] for v in allraw])),'global_tau_T_range':bounds(np.concatenate([v['tau_T'] for v in allraw])),'max_isotope_sum_error':max(v['diagnostics']['isotope_sum_max'] for v in receipts.values()),'max_number_drift':max(max(v['diagnostics']['number_relative_drift'].values()) for v in receipts.values()),'max_baryon_error':max(v['diagnostics']['max_baryon_relative_residual'] for v in receipts.values()),'max_algebraic_Friedmann_error':max(v['diagnostics']['max_Friedmann_algebraic_relative_residual'] for v in receipts.values()),'energy_interpretation':'Q_required-P_photo is combined bath-minus-escaped requirement; no actual recombination cooling is asserted','new_IVPs_in_this_summary':0}
 (BASE/'SAVED_DATA_SCIENCE_SUMMARY.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ('baseline_charge_samples','census_21','cancellation_cases')},indent=2))
if __name__=='__main__':main()
