#!/usr/bin/env python3
"""Reproduce the descriptive joint response from saved component history CSVs only."""
import os
for name in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):os.environ[name]='1'
import argparse,csv,hashlib,json,math
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent

def first_last(path):
    result={}
    with Path(path).open() as stream:
        for row in csv.DictReader(stream):
            cid=row['case_id']
            if cid not in result:result[cid]=[row,row,1]
            else:result[cid][1]=row;result[cid][2]+=1
    for cid,(_,_,count) in result.items():
        if count!=65:raise ValueError('expected65samples:'+cid)
    return result

def endpoints(source,kind):
    rows=[]
    for cid,(initial,last,count) in source.items():
        rows.append({'id':cid,'source':kind,'initial_signed_Sigma':math.sqrt(3)*float(initial['s_over_H']),'initial_signed_Pi_m':float(initial['signed_Pi_m']),'initial_signed_Pi_r':float(initial['signed_Pi_r']),'initial_signed_Pi_total':float(initial['signed_Pi_total']),'signed_Sigma_end':math.sqrt(3)*float(last['s_over_H']),'Sigma_end':float(last['Sigma']),'signed_Pi_m_end':float(last['signed_Pi_m']),'signed_Pi_r_end':float(last['signed_Pi_r']),'signed_Pi_total_end':float(last['signed_Pi_total'])})
    return rows

def design(rows):return np.array([[r['initial_signed_Sigma'],r['initial_signed_Pi_m'],r['initial_signed_Pi_r']] for r in rows])
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--old-history',type=Path,default=HERE/'decomposition/histories.csv');ap.add_argument('--new-history',type=Path,default=HERE/'results/new_sweep/histories.csv');ap.add_argument('--output',type=Path,default=HERE/'response_analysis.json');a=ap.parse_args()
    if a.output.exists():raise FileExistsError(a.output)
    old=endpoints(first_last(a.old_history),'OLD_RADIATION625_DECOMPOSITION_NO_NEW_ODE');new=endpoints(first_last(a.new_history),'NEW_COUPLED_ODE')
    training=old+[r for r in new if not r['id'].startswith('mixed_')];mixed=[r for r in new if r['id'].startswith('mixed_')]
    if len(old)!=625 or len(training)!=1225 or len(mixed)!=6:raise ValueError('FIT_SCOPE625plus600holdout6')
    X=design(training);y=np.array([r['signed_Sigma_end'] for r in training]);coeff=np.linalg.lstsq(X,y,rcond=None)[0];res=y-X@coeff
    for rows in (training,mixed):
        for r,pred in zip(rows,design(rows)@coeff):r.update({'fit_prediction':float(pred),'actual_minus_fit':float(r['signed_Sigma_end']-pred)})
    result={'kind':'Descriptive zero-intercept least-squares from existing radiation625 plus new matter600; mixed6 excluded; no duplicate25 reference controls','training_unique_rows':len(training),'old_radiation_rows':len(old),'new_matter_rows':600,'coefficients_signed_Sigma0_signed_Pi_m0_signed_Pi_r0':coeff.tolist(),'fit_max_abs_residual':float(np.max(abs(res))),'fit_rms_residual':float(np.sqrt(np.mean(res**2))),'radiation_to_matter_response_coefficient_ratio':float(coeff[2]/coeff[1]),'mixed_holdout_count':6,'mixed_max_abs_prediction_difference':max(abs(r['actual_minus_fit']) for r in mixed),'mixed_actual_results':mixed,'inputs':{str(p.resolve()):{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'size_bytes':p.stat().st_size} for p in (a.old_history,a.new_history)},'interpretation':'Empirical finite-grid descriptive fit only; no certified interpolation bound, global response law, linear-superposition replacement or new ODE solve.'}
    root=HERE/'ROOT_COMPONENT_ANALYSIS.json'
    if root.exists():
        prior=json.loads(root.read_text());result['root_finding_reproduction']={'max_coefficient_abs_difference':float(np.max(abs(coeff-np.array(prior['coefficients_signed_Sigma0_signed_Pi_m0_signed_Pi_r0'])))),'fit_max_residual_abs_difference':abs(result['fit_max_abs_residual']-prior['fit_max_abs_residual']),'mixed_max_prediction_difference_abs_difference':abs(result['mixed_max_abs_prediction_difference']-prior['mixed_max_abs_prediction_difference'])}
    a.output.write_text(json.dumps(result,indent=2)+'\n')
    table=a.output.with_suffix('.csv')
    with table.open('w') as stream:
        w=csv.DictWriter(stream,fieldnames=['partition',*training[0].keys()]);w.writeheader()
        for partition,rows in [('TRAIN_625_OLD_PLUS600_NEW',training),('HOLDOUT6_MIXED',mixed)]:
            for r in rows:w.writerow({'partition':partition,**r})
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
