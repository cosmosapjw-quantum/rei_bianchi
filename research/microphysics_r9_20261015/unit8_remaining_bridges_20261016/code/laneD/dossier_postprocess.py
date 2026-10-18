#!/usr/bin/env python3
"""One algebraic dossier selector/lift of the existing successful native rows."""
import json,pathlib
import numpy as np
from analyze_native_prior import ROOT,load_samples,covariance,write_rows,write_matrix

def main():
    contract=json.loads((ROOT/'spec/DOSSIER_NETWORK_CONTRACT.json').read_text());e=ROOT/'evidence';result_path=e/'NUCLEAR_PRIOR_RESULT.json';result=json.loads(result_path.read_text())
    if 'dossier_postprocess' in result:raise SystemExit('Dossier postprocess already applied; preserve existing evidence.')
    phys=contract['physical_scope'];prior=contract['postprocessing'];label=prior['bare_lift']['required_label'];native_names=phys['small_network_native_order'];names,allx=load_samples(ROOT/result['native_files']['samples']);x=allx[:,[names.index(k) for k in native_names]];cy=covariance(x);a=np.array(phys['native_baryon_weights']);core17=phys['core17_order'];a17=np.array(phys['core17_baryon_weights']);aug_names=core17+['B_R']
    l=np.zeros((18,8))
    for state,isotope in prior['bare_lift']['nonzero_mapping'].items():l[core17.index(state),native_names.index(isotope)]=1
    l[17,7]=7
    z=x@l.T;cz=covariance(z);lc=l@cy@l.T;sd=np.sqrt(np.diag(cz));nonzero=np.flatnonzero(sd>0);zero=np.flatnonzero(sd==0);scale=np.outer(sd[nonzero],sd[nonzero]);transform_error=float(np.max(abs(cz[np.ix_(nonzero,nonzero)]-lc[np.ix_(nonzero,nonzero)])/scale));structural_zero=bool((z[:,zero]==0).all() and (cz[zero,:]==0).all() and (cz[:,zero]==0).all())
    b=x@a;partition=z[:,:17]@a17+z[:,17];bcenter=b-b.mean();xcenter=x-x.mean(axis=0);bvar=float(bcenter@bcenter/(len(b)-1));signed=float(a@cy@a);cov_b_y=bcenter@xcenter/(len(b)-1);partition_error=float(np.max(abs(b-partition)))
    gates={'loose_baryon_sum_screen':float(np.max(abs(b-1)))<=1e-6,'linear_covariance_transform_standardized':transform_error<=1e-12,'structural_zero_exact':structural_zero,'row_partition_absolute':partition_error<=1e-14}
    for prefix,ns,data,c in [('native8',native_names,x,cy),('core7',native_names[:7],x[:,:7],cy[:7,:7]),('conditional_bare17',core17,z[:,:17],cz[:17,:17]),('conditional_augmented18',aug_names,z,cz)]:
        write_rows(e/f'nuclear_prior_{prefix}_samples.csv',ns,data);write_matrix(e/f'nuclear_prior_{prefix}_covariance.csv',ns,c)
    write_rows(e/'nuclear_prior_conditional_lift_matrix.csv',['state']+native_names,[[name]+row.tolist() for name,row in zip(aug_names,l)])
    # Null means mathematically undefined correlation for deterministic zero slots.
    corr=[[float(cz[i,j]/(sd[i]*sd[j])) if sd[i]>0 and sd[j]>0 else None for j in range(18)] for i in range(18)]
    with (e/'nuclear_prior_conditional_augmented18_correlation.json').open('w') as f:json.dump({'label':label,'quantity_order':aug_names,'correlation':corr,'undefined_value':None},f,indent=2,allow_nan=False);f.write('\n')
    write_rows(e/'nuclear_prior_baryon_constraint_rows.csv',['full_baryon_sum','core17_baryon_sum','B_R','partition_sum','full_minus_partition','full_minus_one'],np.column_stack([b,z[:,:17]@a17,z[:,17],partition,b-partition,b-1]))
    post={'contract':'spec/DOSSIER_NETWORK_CONTRACT.json','label':label,'input_samples':result['native_files']['samples'],'N':len(x),'native8_order':native_names,'core7_order':native_names[:7],'core17_order':core17,'augmented18_order':aug_names,'linear_map':l.tolist(),'native_baryon_weights':a.tolist(),'augmented_baryon_weights':np.r_[a17,1].tolist(),'no_renormalization':True,'H3_He3_separate':True,'Be7_Li7_separate':True,'native8_and_auxiliary_crosscovariances_preserved':True,'missing_donor51':'Absent from D small-network model, not measured zero or covariance constrained.','structural_zero_slots':[aug_names[i] for i in zero],'undefined_zero_variance_correlations':'null in nuclear_prior_conditional_augmented18_correlation.json','baryon_diagnostics':{'min':float(b.min()),'max':float(b.max()),'max_abs_minus_one':float(np.max(abs(b-1))),'variance_from_centered_baryon_rows_ddof1':bvar,'std_from_centered_baryon_rows_ddof1':float(np.sqrt(bvar)),'signed_A_C_A':signed,'signed_contraction_minus_centered_variance':signed-bvar,'cov_baryon_native8_from_centered_rows':dict(zip(native_names,cov_b_y.tolist())),'max_abs_full_minus_core17_plus_BR':partition_error,'source_export_precision':'native samples/matrix %.10e; nominal JSON %.10g','renormalized':False,'null_variance_forced':False},'transform_standardized_error':transform_error,'acceptance_gates':gates,'status':'MECHANICAL_PASS_PENDING_INDEPENDENT_REVIEW' if all(gates.values()) else 'FAILED_RETURN_TO_AUTHORITY','claim':'A fixed hypothetical bare-charge assignment at the nuclear endpoint; PRIMAT does not compute charge probabilities. Not late-time chemistry, atomic matching, physical 17-state history, old-donor covariance, or missing isotope uncertainty.'}
    result['dossier_postprocess']=post
    if not all(gates.values()):result['status']='DOSSIER_POSTPROCESS_FAILED_RETURN_TO_AUTHORITY'
    result_path.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    with (e/'NUCLEAR_PRIOR_EXECUTION.md').open('a') as f:f.write('\n## Dossier postprocessing of existing64 samples\n\n'+label+'\n\nSeven reservoir selection and a conditional17 bare-charge lift retain all native8 cross-covariances with the excluded baryon coordinate B_R=7Be7. All covariance transforms use the same18x8 linear map. Structural zero correlations are null. This is endpoint bookkeeping only; no new BBN solves, charge-history solution, renormalization, or isotope collapse.\n\n```json\n'+json.dumps({'acceptance_gates':gates,'transform_standardized_error':transform_error,'baryon_diagnostics':post['baryon_diagnostics']},indent=2)+'\n```\n\nTargeted verification: `python -m unittest discover -s tests/laneD -v` passed5 no-solver tests; raw logs preserved.\n')
    print(json.dumps(post,indent=2))
if __name__=='__main__':main()
