#!/usr/bin/env python3
"""Compare frozen Rust output to independent continuous and matched-path results."""
from __future__ import annotations
import argparse
import csv
import json
import math
from pathlib import Path
from independent_birth_reference import sha


MAP={'born_com3':'source_count','survivor_com3':'survival','age_sum_com_s':'age',
 'age2_sum_com_s2':'age2','thermal_j':'thermal','chemical_j':'chemical','source_j':'source_energy',
 'surviving_j':'energy','absorbed_j':'absorbed_energy','work_ledger_j':'work','work_independent_j':'work',
 'q2_numerator_j':'q2'}


def rows(path):
    with path.open(newline='') as stream:return list(csv.DictReader(stream))


def diff(actual,reference):
    d=actual-reference
    return {'actual':actual,'reference':reference,'difference':d,'relative':d/reference if reference else None}


def compare(name,directory,reference,matched=None):
    srows=rows(directory/'SUMMARY.csv')
    if len(srows)!=1:raise ValueError('summary row count')
    summary=srows[0];templates=rows(directory/'TEMPLATES_RESULT.csv')
    if int(summary['templates'])!=int(summary['available_templates']):raise ValueError('prefix study is not full-source matrix')
    if len(templates)!=int(summary['templates']):raise ValueError('template count mismatch')
    ref=dict(reference);ref['thermal']=math.fsum(ref['heat'].values());ref['chemical']=math.fsum(ref['binding'].values())
    fields={k:diff(float(summary[k]),ref[v]) for k,v in MAP.items()}
    for sp in ('HI','HeI','HeII','DI'):fields[sp]=diff(float(summary[sp]),ref['events'][sp])
    fields['mean_age_s']=diff(float(summary['age_sum_com_s'])/float(summary['survivor_com3']),ref['mean_age_s'])
    fields['mean_age2_s2']=diff(float(summary['age2_sum_com_s2'])/float(summary['survivor_com3']),ref['mean_age2_s2'])
    fields['energy_weighted_q2']=diff(float(summary['q2_numerator_j'])/float(summary['surviving_j']),ref['energy_weighted_q2'])
    source_e=float(summary['source_j'])
    for key,value in fields.items():
        if key.endswith('_j'):value['difference_over_source_energy']=value['difference']/source_e
    template_checks={}
    for key in [*MAP,'HI','HeI','HeII','DI']:
        total=math.fsum(float(r[key]) for r in templates)
        actual=float(summary[key]);scale=max(abs(total),abs(actual),1e-300)
        rel=abs(total-actual)/scale
        template_checks[key]=rel
        # Signed tiny work/q2 use physically useful absolute scale too.
        if abs(total-actual)>3e-12*scale+1e-14*(source_e if key.endswith('_j') else 0):
            raise ValueError('summary/template accounting '+name+' '+key)
    result={'label':name,'directory':str(directory),'controls':{k:summary[k] for k in
       ('case','birth','refinement','birth_degree','path_slabs','opacity_degree','event_degree','split','templates','cohorts')},
       'continuous_comparison':fields,'template_accounting_relative':template_checks,
       'internal_work_ledger_minus_independent_over_source_energy':(float(summary['work_ledger_j'])-float(summary['work_independent_j']))/source_e,
       'number_ledger_relative':float(summary['number_residual'])/float(summary['born_com3']),
       'independent_energy_ledger_relative':float(summary['energy_residual_j'])/source_e,
       'inputs':[{'path':str(directory/p),'sha256':sha(directory/p)} for p in ('SUMMARY.csv','TEMPLATES_RESULT.csv','BIRTHS.csv')]}
    if matched:
        m=json.loads(matched.read_text());tot=m['totals']
        # Matched reference fixes the emitted representation, isolating path changes.
        mm={'survivor_com3':'survival','age_sum_com_s':'age','age2_sum_com_s2':'age2','surviving_j':'energy',
            'absorbed_j':'absorbed','work_independent_j':'work','work_ledger_j':'work','chemical_j':'chemical','thermal_j':'heat',
            'q2_numerator_j':'q2'}
        result['matched_path_comparison']={k:diff(float(summary[k]),tot[v]) for k,v in mm.items()}
        for sp in ('HI','HeI','HeII','DI'):result['matched_path_comparison'][sp]=diff(float(summary[sp]),tot[sp])
        result['matched_path_comparison']['mean_age_s']=diff(float(summary['age_sum_com_s'])/float(summary['survivor_com3']),tot['mean_age_s'])
        result['matched_path_comparison']['mean_age2_s2']=diff(float(summary['age2_sum_com_s2'])/float(summary['survivor_com3']),tot['mean_age2_s2'])
        result['matched_path_comparison']['energy_weighted_q2']=diff(float(summary['q2_numerator_j'])/float(summary['surviving_j']),tot['energy_weighted_q2'])
        for key,value in result['matched_path_comparison'].items():
            if key.endswith('_j'):value['difference_over_source_energy']=value['difference']/source_e
        result['matched_reference']={'path':str(matched),'sha256':sha(matched),'maxima':m.get('maxima',{})}
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True)
    p.add_argument('--reference-plus',type=Path);p.add_argument('--run',action='append',required=True,help='LABEL=RUN_DIRECTORY')
    p.add_argument('--matched',action='append',default=[],help='LABEL=MATCHED_JSON')
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    refs={'SIGNED_MINUS':json.loads(a.reference.read_text())['executions'][-1]['result']}
    if a.reference_plus:refs['SIGNED_PLUS']=json.loads(a.reference_plus.read_text())['executions'][-1]['result']
    matched={k:Path(v) for k,v in (x.split('=',1) for x in a.matched)};results=[]
    for item in a.run:
        label,path=item.split('=',1);d=Path(path);case=rows(d/'SUMMARY.csv')[0]['case']
        if case not in refs:raise ValueError('missing signed reference')
        if rows(d/'SUMMARY.csv')[0]['split']=='true':raise ValueError('split-spectrum comparison needs its own independent spectral reference')
        results.append(compare(label,d,refs[case],matched.get(label)))
    receipt={'schema_version':1,'status':'completed','runs':results,'reference':{'path':str(a.reference),'sha256':sha(a.reference)},
      'scope':'One frozen recorded gas operator; continuous error combines birth and path, matched-path errors fix emitted cohorts; tiny ledgers are not accuracy bounds',
      'script_sha256':sha(__file__)}
    if a.reference_plus:receipt['reference_plus']={'path':str(a.reference_plus),'sha256':sha(a.reference_plus)}
    (a.output/'RUST_INDEPENDENT_COMPARISONS.json').write_text(json.dumps(receipt,indent=2)+'\n')
    columns=['label','quantity','actual','reference','difference','relative','difference_over_source_energy']
    with (a.output/'RUST_INDEPENDENT_COMPARISONS.csv').open('w',newline='') as z:
        w=csv.DictWriter(z,fieldnames=columns);w.writeheader()
        for r in results:
            for key,value in r['continuous_comparison'].items():w.writerow({'label':r['label'],'quantity':key,**value})
    print(json.dumps({'runs':len(results),'output':str(a.output/'RUST_INDEPENDENT_COMPARISONS.json')}))


if __name__=='__main__':main()
