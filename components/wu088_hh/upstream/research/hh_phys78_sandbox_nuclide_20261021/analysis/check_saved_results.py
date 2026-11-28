#!/usr/bin/env python3
"""Inspect immutable pilot/refinement data. This program never integrates ODEs."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'source'))
import atomic_network as atomic
import run_pilot as runner


def analyze(root):
    root=Path(root)
    rows=[]; records={}; mutants=[]
    total_defect=0.; sqrt2_defect=0.
    for path in sorted((root/'results/pilot/cases').glob('*.json')):
        receipt=json.loads(path.read_text())
        status,_=runner.existing_case(root/'results/pilot',receipt['science_id'],receipt['binding'])
        if status!='COMPLETE':
            raise ValueError('Noncomplete case cannot be admitted to plots')
        with np.load(path.with_suffix('.npz'),allow_pickle=False) as data:
            d={k:data[k].copy() for k in data.files}
        cid=receipt['case']['id'];records[cid]=(receipt,d)
        m=d['signed_Pi_m_F'];r=d['signed_Pi_r_F'];t=d['Pi_total_F']
        total_defect=max(total_defect,float(np.max(abs(t-abs(m+r)))))
        sqrt2_defect=max(sqrt2_defect,float(np.max(abs(d['Sigma_F']-np.sqrt(2)*d['Sigma_half']))),
                         float(np.max(abs(t-np.sqrt(2)*d['Pi_total_half']))))
        sign_mutant=float(np.max(abs(abs(m-r)-t)))
        norm_mutant=float(np.max(abs(abs(m)+abs(r)-t)))
        if sign_mutant>1e-8 and norm_mutant>1e-8:
            mutants.append({'case':cid,'radiation_sign_difference':sign_mutant,
                            'sum_of_norms_difference':norm_mutant})
        rows.append({'case':cid,**receipt['case'],
            'Sigma_F_z20':float(d['Sigma_F'][0]),'Sigma_F_z2':float(d['Sigma_F'][-1]),
            'Pi_m_F_max':float(d['Pi_m_F'].max()),'Pi_r_F_max':float(d['Pi_r_F'].max()),
            'Pi_total_F_max':float(t.max()),'T_min_K':float(d['T_K'].min()),
            'T_max_K':float(d['T_K'].max()),'xe_z2':float(d['xe'][-1]),
            'max_nuclei_relative':float(d['nuclei_rel_error'].max()),
            'max_sampled_energy_identity':float(abs(d['energy_balance_rel']).max()),
            'minimum_species':float(d['Y'].min()),'npz_sha256':receipt['npz']['sha256']})
    if len(records)!=31 or total_defect>1e-14 or sqrt2_defect>1e-14 or not mutants:
        raise ArithmeticError('Pilot completeness or tensor convention check failed')
    reference_path=next((root/'results/refinement/cases').glob('*.json'))
    refined_record=json.loads(reference_path.read_text())
    status,_=runner.existing_case(root/'results/refinement',refined_record['science_id'],refined_record['binding'])
    if status!='COMPLETE':raise ValueError('Refinement is incomplete')
    with np.load(reference_path.with_suffix('.npz'),allow_pickle=False) as data:
        fine={k:data[k].copy() for k in data.files}
    coarse=records['P024'][1]
    if not np.array_equal(coarse['x'],fine['x']):raise ValueError('Common output grid required')
    metrics={k:float(np.max(abs(coarse[k]-fine[k]))/(np.max(abs(fine[k]))+1e-12))
             for k in ('Sigma_F','Pi_m_F','Pi_r_F','Pi_total_F')}
    metrics['H_relative']=float(np.max(abs(coarse['H_per_s']/fine['H_per_s']-1)))
    metrics['T_relative']=float(np.max(abs(coarse['T_K']/fine['T_K']-1)))
    metrics['xe_absolute']=float(np.max(abs(coarse['xe']-fine['xe'])))
    scales=atomic.ISOTOPE_SUM.T@(atomic.ISOTOPE_SUM@fine['Y'][0]);active=scales>0
    metrics['abundance_fraction_by_isotope_absolute']=float(np.max(
        abs(coarse['Y'][:,active]-fine['Y'][:,active])/scales[active]))
    checks={k:metrics[k]<(1e-4 if k=='H_relative' else .002 if k=='xe_absolute'
                         else .003 if k=='abundance_fraction_by_isotope_absolute' else .005)
            for k in metrics}
    if not all(checks.values()):raise ArithmeticError('Predeclared refinement criterion failed')
    result={'status':'PASS_SCOPED','case_count':len(rows),'saved_epochs_per_case':len(fine['x']),
            'sampled_energy_identity_max':max(r['max_sampled_energy_identity'] for r in rows),
            'isotope_conservation_max':max(r['max_nuclei_relative'] for r in rows),
            'tensor_sum_defect':total_defect,'sqrt2_defect':sqrt2_defect,
            'refinement_metrics':metrics,'refinement_predeclared_checks':checks,
            'wrong_sign_and_sum_of_norms_detected_cases':mutants,
            'new_ODE_calls':0,'benchmark':False,
            'scope':'Saved-data checks and one combined refinement; not continuum/global error certificate'}
    output=root/'verification';output.mkdir(exist_ok=True)
    (output/'SAVED_RESULTS_CHECK.json').write_text(json.dumps(result,indent=2)+'\n')
    with (output/'PILOT_ENDPOINTS_AND_RANGES.csv').open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--root',type=Path,default=ROOT)
    args=parser.parse_args();answer=analyze(args.root)
    print(json.dumps({k:answer[k] for k in ('status','case_count','refinement_metrics','new_ODE_calls')}))
