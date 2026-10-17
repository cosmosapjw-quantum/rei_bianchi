#!/usr/bin/env python3
"""Independent NumPy ddof=1 analysis of frozen native exports; no BBN calls."""
import csv, json, math, pathlib
import numpy as np
ROOT=pathlib.Path(__file__).resolve().parents[2]
SELECTED=['YPBBN','DoH','He3oH','Li7oH','Be7','Li7']
NUCLIDES=['n','p','H2','H3','He3','He4','Li7','Be7']
A=np.array([1,1,2,3,3,4,7,7])

def load_samples(path):
    with path.open() as f:
        names=f.readline().strip().split('\t'); x=np.loadtxt(f,delimiter='\t',ndmin=2)
    return names,x

def load_matrix(path):
    with path.open() as f:
        lines=[line for line in f if not line.startswith('#')]
    names=lines[0].strip().split('\t')[1:]
    return names,np.array([[float(x) for x in line.strip().split('\t')[1:]] for line in lines[1:]])

def covariance(x):
    centered=x-x.mean(axis=0)
    return centered.T@centered/(len(x)-1)

def write_rows(path,names,x):
    with path.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(names);w.writerows(x)

def write_matrix(path,names,x):
    with path.open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['quantity']+names)
        for name,row in zip(names,x):w.writerow([name]+row.tolist())

def main():
    raw=ROOT/'evidence/laneD_raw'; e=ROOT/'evidence'; rec=json.loads((raw/'execution_receipt.json').read_text()); contract=json.loads((ROOT/'spec/NUCLEAR_PRIOR_CONTRACT.json').read_text())
    result={'status':'RETURN_TO_AUTHORITY','requested_executor':'lower-tier implementation/executor','observed_executor':'UNKNOWN (not exposed by runtime)','source_commit':rec['commit'],'source_manifest':'intake/PRIMAT_DOWNLOAD_MANIFEST.json','source_verification':'evidence/laneD_raw/source_verification.json','effective_parameters':contract['config'],'prior_definition':contract['prior'],'cap30_explicit':True,'runtime_budget':rec,'scope':'Exploratory finite-sample small-network source-native propagated nuclear-rate and neutron-lifetime prior covariance; no converged precision, observational fit, EFT truncation or original donor covariance claim.'}
    def save(): (e/'NUCLEAR_PRIOR_RESULT.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    if not rec.get('valid_samples'):
        result['failure']=rec['status'];save();write_execution(result);print(json.dumps({'status':result['status'],'failure':result['failure']}));return
    prefix=raw/rec['result_prefix'];names,allx=load_samples(pathlib.Path(str(prefix)+'_samples.tsv')); idx=[names.index(k) for k in SELECTED]; x=allx[:,idx]
    central_json=json.loads((raw/'nominal.stdout').read_text());tight_json=json.loads((raw/'tight.stdout').read_text())
    def central(d):return np.array([d[k] if k in d else d['Y_final'][k] for k in SELECTED])
    c=central(central_json);tight=central(tight_json)
    result.update({'sample_count':len(x),'seed':20261016,'selected_quantities':SELECTED,'native_quantities':names,'native_nuclides_retained':NUCLIDES,'native_files':{k:str(pathlib.Path(str(prefix)+'_'+k+'.tsv').relative_to(ROOT)) for k in ['samples','covariance','correlation']},'central_values':dict(zip(SELECTED,c.tolist()))})
    if not (np.isfinite(allx).all() and (x>0).all() and (c>0).all()):
        result['failure']='NONFINITE_OR_NONPOSITIVE_RETURN_TO_AUTHORITY';save();write_execution(result);return
    cov=covariance(x); std=np.sqrt(np.diag(cov))
    if np.any(std==0):
        result['failure']='ZERO_SELECTED_VARIANCE_RETURN_TO_AUTHORITY';save();write_execution(result);return
    scale=np.outer(std,std); corr=cov/scale
    mass7=x[:,4]+x[:,5]; augmented=np.column_stack([x,mass7]); anames=SELECTED+['Ymass7']; acov=covariance(augmented); acentral=np.r_[c,c[4]+c[5]]
    transform=np.vstack([np.eye(6),np.array([0,0,0,0,1,1])]); linear=transform@cov@transform.T; ascale=np.sqrt(np.outer(np.diag(acov),np.diag(acov)))
    cn,nativecov=load_matrix(pathlib.Path(str(prefix)+'_covariance.tsv'));rn,nativer=load_matrix(pathlib.Path(str(prefix)+'_correlation.tsv'))
    ci=[cn.index(k) for k in SELECTED];ri=[rn.index(k) for k in SELECTED]
    errors={'central_precision_relative':float(np.max(abs(c-tight)/c)),'central_precision_over_sample_std':float(np.max(abs(c-tight)/std)),'covariance_symmetry_standardized':float(np.max(abs(cov-cov.T)/scale)),'correlation_diagonal_abs':float(np.max(abs(np.diag(corr)-1))),'correlation_min_eigenvalue':float(np.linalg.eigvalsh(corr).min()),'native_covariance_standardized_difference':float(np.max(abs(cov-nativecov[np.ix_(ci,ci)])/scale)),'native_correlation_abs_difference':float(np.max(abs(corr-nativer[np.ix_(ri,ri)]))),'mass7_row_scaled_error':float(np.max(abs(augmented[:,6]-x[:,4]-x[:,5])/(1e-25+1e-12*abs(mass7)))),'mass7_covariance_transform_standardized':float(np.max(abs(acov-linear)/ascale))}
    repeat=None
    if rec['result_prefix']=='production':
        pn,px=load_samples(raw/'pilot_samples.tsv'); pidx=[pn.index(k) for k in SELECTED]; repeat=float(np.max(abs(x[:8]-px[:,pidx])/abs(px[:,pidx])));errors['repeat_first8_relative']=repeat
    gates={k:errors[k]<=v for k,v in contract['acceptance'].items() if isinstance(v,(int,float)) and not isinstance(v,bool) and k in errors and k!='correlation_min_eigenvalue'}
    gates['correlation_min_eigenvalue']=errors['correlation_min_eigenvalue']>=-1e-10;gates['mass7_row_identity']=errors['mass7_row_scaled_error']<=1
    gates['finite_native_samples']=bool(np.isfinite(allx).all());gates['positive_selected_samples']=bool((x>0).all());gates['positive_selected_central']=bool((c>0).all());gates['native_sample_count']=len(x)==rec['valid_samples'];gates['numerical_budget']=rec['numerical_wall_s']<=30
    write_rows(e/'nuclear_prior_samples.csv',anames,augmented)
    write_matrix(e/'nuclear_prior_covariance.csv',anames,acov)
    write_matrix(e/'nuclear_prior_correlation.csv',anames,acov/ascale)
    write_matrix(e/'nuclear_prior_fractional_covariance.csv',anames,acov/np.outer(acentral,acentral))
    ni=[names.index(k) for k in NUCLIDES];native=allx[:,ni];baryon=native@A; excluded=7*native[:,7]
    write_rows(e/'nuclear_prior_baryon_bookkeeping.csv',['baryon_sum_A_dot_Y','excluded_Be7_baryons','core7_baryon_sum','n','p','H2','H3','He3','He4','Li7'],np.column_stack([baryon,excluded,baryon-excluded,native[:,:7]]))
    reactions=(ROOT/'inputs/laneD/small.txt').read_text().splitlines()
    result.update({'reaction_list':reactions,'ddof':1,'sample_mean':dict(zip(anames,augmented.mean(axis=0).tolist())),'sample_std':dict(zip(anames,np.sqrt(np.diag(acov)).tolist())),'central_precision_errors_by_quantity':{'relative':dict(zip(SELECTED,(abs(c-tight)/c).tolist())),'over_sample_std':dict(zip(SELECTED,(abs(c-tight)/std).tolist()))},'errors':errors,'acceptance_gates':gates,'repeatability':{'status':'PASS' if repeat is not None and repeat<=1e-9 else 'NOT_APPLICABLE_PILOT_ONLY' if repeat is None else 'FAIL','relative_error':repeat},'covariance_units':{'YPBBN':'helium-4 baryon fraction','DoH':'number per H','He3oH':'number per H','Li7oH':'number per H','Be7':'number per baryon','Li7':'number per baryon','Ymass7':'number per baryon','matrix_entry':'product of row and column observable units; all ratios dimensionless'},'sampling_diagnostics':{'gaussian_variance_relative_SE_orientation':math.sqrt(2/(len(x)-1)),'convergence_claim':False,'half_samples':[{'N':len(half),'mean':dict(zip(anames,half.mean(axis=0).tolist())),'std':dict(zip(anames,half.std(axis=0,ddof=1).tolist()))} for half in np.array_split(augmented,2)],'bootstrap':'omitted: optional; no further solves'},'baryon_bookkeeping':{'all_native_isotopes':NUCLIDES,'A':A.tolist(),'sum_range':[float(baryon.min()),float(baryon.max())],'max_abs_one_minus_sum':float(np.max(abs(1-baryon))),'excluded_reservoir':'B_R=7*YBe7','excluded_baryon_range':[float(excluded.min()),float(excluded.max())],'core7':['n','p','H2','H3','He3','He4','Li7'],'renormalized':False,'claim':'endpoint bookkeeping only; not an atomic-history 17-state initial condition'},'status':('MECHANICAL_PASS_PENDING_INDEPENDENT_REVIEW' if all(gates.values()) else 'ACCEPTANCE_FAILED_RETURN_TO_AUTHORITY'),'budget_limited':rec['status']=='BUDGET_LIMITED'})
    save();write_execution(result);print(json.dumps({'status':result['status'],'N':len(x),'gates':gates,'errors':errors},indent=2))

def write_execution(result):
    rec=result['runtime_budget']; lines=['# Native nuclear-prior execution','',f"Status: {result['status']}",'',result['scope'],'','Source commit: `'+rec['commit']+'`; all '+str(rec['verified_files'])+' staged files verified against Git blob and SHA-256 manifest. No provider source edits.','', 'Portable source/license backup: `inputs/laneD/primat_source_4bf97d5082ee.tar.gz`; accepts `--provider-root` or `UNIT8_PRIMAT_PROVIDER_ROOT` and automatically restores included archive if the default provider is absent.','', 'Reproduce the prescribed execution once in a fresh output directory: `python code/laneD/run_native_prior.py --provider-root /path/to/provider`, then `python code/laneD/analyze_native_prior.py`. The receipt prevents accidental numerical reruns.','', '| Stage | Wall seconds | Exit | Timeout |','|---|---:|---:|---|']
    for r in rec['records']:lines.append(f"| {r['label']} | {r['wall_s']:.6f} | {r['returncode']} | {r['timed_out']} |")
    lines += ['',f"Total numerical wall: {rec.get('numerical_wall_s',0):.6f}s /30s; independent build ceiling30s.",'','All native MC quantities, eight nuclides, covariance and correlations remain in `evidence/laneD_raw`. Independent derived CSVs use ddof=1 and append Ymass7=Be7+Li7. Small network differs from the original donor network. All selected output uncertainty is conditional on the frozen coherent-temperature reaction prior, cap30 and independent neutron lifetime prior.','', 'The result is exploratory finite-sample prior propagation. Half-sample diagnostics and variance sampling-error orientation are recorded without a convergence requirement. Atomic-charge history, owner likelihood, EFT calibration/truncation, original large donor covariance, and T5 closure are separate claims.']
    if result.get('failure'):lines+=['','Failure: '+result['failure']]
    if 'errors' in result:lines+=['','Observed acceptance residuals:','', '```json',json.dumps(result['errors'],indent=2),'```']
    (ROOT/'evidence/NUCLEAR_PRIOR_EXECUTION.md').write_text('\n'.join(lines)+'\n')
if __name__=='__main__':main()
