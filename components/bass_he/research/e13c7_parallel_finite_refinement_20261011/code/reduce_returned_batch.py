#!/usr/bin/env python3
"""Chat-side exact reduction after return; also supports the completed local rehearsal."""
import argparse
import csv
import hashlib
import io
from pathlib import Path
from common import *
from analyze_local import load_complete

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--batch-dir',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--mode',choices=['ncp-return','local-rehearsal'],default='ncp-return')
    a=ap.parse_args();root=a.package.resolve();batch=a.batch_dir.resolve();out=a.output_dir.resolve()
    out.mkdir(parents=True,exist_ok=False)
    plan=read(root/'inputs/WORK_PLAN.json');pred=read(root/'inputs/PREDECESSOR_BUDGET.json')
    complete=read(batch/'BATCH_COMPLETE.json');index=read(root/'inputs/INPUT_INDEX.json')['records']
    source_sha=sha(root/'SOURCE_LOCK.json')
    if a.mode=='ncp-return':
        expected=plan['ncp_nodes'];n=plan['primary_N'];scope='ncp'
        if plan['status']!='SEALED_FOR_HEAVY_NCP' or len(expected)!=2331:
            raise ValueError('sealed full heavy plan required')
        expected_exec=sha(root/'EXECUTION_LOCK.json')
        local=read(root/'analysis/LOCAL/LOCAL_ADMITTED_CANDIDATE.json')
        retained=sum_metrics([decode_metrics(pred['prior_six']),decode_metrics(local['new_local_eight'])])
        before=decode_metrics(local['current_full_OFF'])
        expected_old_group=decode_metrics(pred['old_ncp_2331'])
    else:
        expected=plan['local_primary_nodes'];n=512;scope='local'
        expected_exec=sha(root/'evidence/LOCAL_PRIMARY_EXECUTION_LOCK.json')
        retained=sum_metrics([decode_metrics(pred['prior_six']),decode_metrics(pred['old_ncp_2331'])])
        before=decode_metrics(pred['E13C6_full'])
        expected_old_group=decode_metrics(pred['old_local_eight'])
    if complete['work']!={'mode':'OFF','N':n,'precision':60,'scope':scope,'nodes':expected}:
        raise ValueError('batch scope/work identity mismatch')
    if complete['execution_lock_sha256']!=expected_exec or any(complete['forbidden_invocations'].values()):
        raise ValueError('batch execution identity or invocation mismatch')
    entries=complete['ordered_paths']
    if [e['node'] for e in entries]!=sorted(expected):
        raise ValueError('missing/duplicate/unsorted batch node')
    collection={'work':complete['work'],'execution_lock_sha256':expected_exec,
        'paths':[{'node':e['node'],'semantic_sha256':e['summary']['semantic_sha256']} for e in entries]}
    if hashlib.sha256(b'bass-he-e13c7-ordered-path-collection-v1\n'+canonical(collection)).hexdigest()!=complete['collection_semantic_sha256']:
        raise ValueError('ordered batch semantic mismatch')
    old_group={'absolute':{},'correction':{}};new_group={'absolute':{},'correction':{}}
    rows=[];not_admissible=[]
    for e in entries:
        path=(batch/e['relative_directory']).resolve()
        if not path.is_relative_to(batch) or path.is_symlink():
            raise ValueError('unsafe returned path')
        for name,pin in e['files'].items():
            file=path/name
            if name not in ('COMPLETE.json','RESULT.json','ADMISSION.json') or file.stat().st_size!=pin['bytes'] or sha(file)!=pin['sha256']:
                raise ValueError('returned path byte identity mismatch')
        x=load_complete(root,path,index,source_sha)
        if x['result']['work']!={'mode':'OFF','node':e['node'],'N':n,'precision':60} or x['receipt']['semantic_sha256']!=e['summary']['semantic_sha256']:
            raise ValueError('returned path work/semantic mismatch')
        if not x['admission']['mechanically_admissible']:
            not_admissible.append(e['node'])
        old_group=sum_metrics([old_group,x['old']]);new_group=sum_metrics([new_group,x['new']])
        rows.append({'node':e['node'],'semantic_sha256':e['summary']['semantic_sha256'],
             'mechanically_admissible':x['admission']['mechanically_admissible']})
    if old_group!=expected_old_group or sum_metrics([retained,old_group])!=before:
        raise ValueError('actual returned-source group does not reproduce direct predecessor bridge')
    candidate=sum_metrics([retained,new_group]);comparison=compare_metrics(before,candidate)
    nested=all(r['nested'] and r['width_nonincreasing'] for r in comparison)
    status='PASS_MECHANICAL_PENDING_INDEPENDENT_REVIEW' if not not_admissible and nested else 'HOLD_RAW_NESTING_GATE'
    if a.mode=='local-rehearsal':
        if candidate!=decode_metrics(read(root/'analysis/LOCAL/LOCAL_ANALYSIS.json')['full_after_N512_eight_only']):
            raise ValueError('local batch rehearsal differs from separately saved local analysis')
        status='PASS_LOCAL_SAVED_BATCH_REDUCTION_REHEARSAL'
    result={'schema':'bass-he-e13c7-return-reduction-v1','status':status,'mode':a.mode,
        'execution_lock_sha256':expected_exec,'source_lock_sha256':source_sha,
        'ordered_collection_semantic_sha256':complete['collection_semantic_sha256'],
        'paths_consumed':len(entries),'path_evidence':rows,'not_admissible_nodes':not_admissible,
        'all_34_direct_predecessor_bridges':True,'old_group':encode_metrics(old_group),'new_raw_group':encode_metrics(new_group),
        'retained_direct_sum':encode_metrics(retained),'full_before':encode_metrics(before),'full_raw_candidate':encode_metrics(candidate),
        'full_comparison':comparison,'intersection_used':False,'old_fallback_used':False,
        'kernel_invocations_in_reduction':0,'global_physical_admission':'HOLD',
        'physical':'HOLD','continuum':'HOLD','production':'HOLD','receiver':'HOLD'}
    save(out/'REDUCTION.json',result)
    buf=io.StringIO(newline='');w=csv.writer(buf)
    w.writerow(['kind','quantity','old_width_exact','new_raw_width_exact','gain_percent','nested','width_nonincreasing'])
    for r in comparison:
        w.writerow([r['kind'],r['quantity'],r['old_width'],r['new_width'],decimal_display(100*F(r['gain_fraction'])) if r['gain_fraction'] is not None else 'EXACT_ZERO',r['nested'],r['width_nonincreasing']])
    save_bytes(out/'FULL_WIDTHS.csv',buf.getvalue().encode())
    digest=hashlib.sha256(b'bass-he-e13c7-return-reduction-v1\n'+canonical(result)).hexdigest()
    save(out/'REDUCTION_IDENTITY.json',{'semantic_sha256':digest,'result_sha256':sha(out/'REDUCTION.json'),'csv_sha256':sha(out/'FULL_WIDTHS.csv')})
    print(__import__('json').dumps({'status':status,'paths':len(entries),'semantic_sha256':digest,'kernel_invocations':0}))
    return 0 if not not_admissible and nested else 2

if __name__=='__main__':
    raise SystemExit(main())
