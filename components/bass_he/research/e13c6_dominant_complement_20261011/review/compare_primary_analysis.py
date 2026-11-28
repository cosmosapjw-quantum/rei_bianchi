#!/usr/bin/env python3
"""Compare all saved primary endpoint maps and budgets to independent Fraction audit."""
from pathlib import Path
from fractions import Fraction as F
from decimal import Decimal, localcontext
from datetime import datetime, timezone
import csv, hashlib, json, sys, time
from independent_fraction_audit import old_metrics,new_metrics,B,identity,canon,width,encloses,overlap,NODES,UNITS,EPS

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'BASS_HE_E13C6_DOMINANT_COMPLEMENT_REFINEMENT_20261011_v1'
read=lambda p:json.loads(p.read_text())
def display(v):
    if v is None:return None
    with localcontext() as c:
        c.prec=22
        return str(Decimal(v.numerator)/Decimal(v.denominator))
checks=[]
def ck(k,v):checks.append({'id':k,'pass':bool(v)})
started=time.monotonic()
ind=read(ROOT/'review/INDEPENDENT_FRACTION_AUDIT.json')
ck('independent_audit_pass',ind['status']=='PASS' and ind['failed_count']==0)
old=[json.loads(x) for x in (P/'inputs/OLD_PATHS_OFF4.jsonl').read_text().splitlines()]
byunit={}
for u in UNITS:
    r=read(P/'runs'/u/'RESULTS.json')
    a=read(P/'analysis'/u/'GLOBAL_ANALYSIS.json')
    ai=read(P/'analysis'/u/'ANALYSIS_IDENTITY.json')
    ck(u+'/analysis_sha',identity(P/'analysis'/u/'GLOBAL_ANALYSIS.json')['sha256']==ai['analysis_file_sha256'])
    ck(u+'/analysis_semantic',hashlib.sha256(b'bass-he-e13c6-budget-semantic-v1\n'+canon(a)).hexdigest()==ai['semantic_sha256'])
    ck(u+'/same_numerical_semantic',a['source_numerical_semantic_sha256']==ind['work_units'][u]['semantic_sha256'])
    ck(u+'/intersection_not_used',a['intersection_used'] is False and all(z['intersection_used'] is False for d in a['global_OFF'].values() for z in d.values()))
    counts={'path_metric_pairs':0,'overlapping_pairs':0,'nested_pairs':0,'nonincreasing_width_pairs':0}
    for o,n,path in zip(old,r['tracks'],a['paths']):
        w=B(o['weight'])[0];oldmap=old_metrics(o);newmap=new_metrics(n,w)
        for kind,rows in oldmap.items():
            for key,oldbox in rows.items():
                newbox=newmap[kind][key];claim=path['metrics'][kind][key]
                ck(u+'/'+str(o['node'])+'/'+kind+'/'+key+'/endpoints',B(claim['old'])==oldbox and B(claim['new_raw'])==newbox)
                ck(u+'/'+str(o['node'])+'/'+kind+'/'+key+'/widths',F(claim['old_width'])==width(oldbox) and F(claim['new_width'])==width(newbox) and F(claim['width_gain'])==width(oldbox)-width(newbox))
                expected={'overlap':overlap(oldbox,newbox),'new_subset_old':encloses(oldbox,newbox),'width_nonincreasing':width(newbox)<=width(oldbox)}
                ck(u+'/'+str(o['node'])+'/'+kind+'/'+key+'/flags',all(claim[k]==v for k,v in expected.items()))
                counts['path_metric_pairs']+=1
                counts['overlapping_pairs']+=expected['overlap'];counts['nested_pairs']+=expected['new_subset_old'];counts['nonincreasing_width_pairs']+=expected['width_nonincreasing']
    ck(u+'/all_counts',all(a['checks'][k]==v for k,v in counts.items()) and a['checks']['old_selected_bridges']==a['checks']['full_predecessor_bridges']==34)
    for kind,rows in a['global_OFF'].items():
        for key,c in rows.items():
            z=ind['work_units'][u]['budgets'][kind][key]
            ck(u+'/global/'+kind+'/'+key+'/endpoints',B(c['old'])==B(z['old_full']) and B(c['new_raw'])==B(z['raw_new_full']))
            ck(u+'/global/'+kind+'/'+key+'/selected',B(c['old_selected_K4'])==B(z['old_selected']) and B(c['new_selected_K4_raw'])==B(z['raw_new_selected']))
            ow,nw=width(B(z['old_full'])),width(B(z['raw_new_full']))
            ck(u+'/global/'+kind+'/'+key+'/exactwidth',F(c['old_width'])==ow and F(c['new_width'])==nw and F(c['width_gain'])==ow-nw)
            ck(u+'/global/'+kind+'/'+key+'/display',c['old_width_decimal']==display(ow) and c['new_width_decimal']==display(nw) and c['width_reduction_percent']==display(100*(ow-nw)/ow if ow else None))
    csvrows=list(csv.DictReader((P/'analysis'/u/'GLOBAL_WIDTHS.csv').open()))
    ck(u+'/csv34',len(csvrows)==34 and len({(z['kind'],z['metric']) for z in csvrows})==34)
    for z in csvrows:
        c=a['global_OFF'][z['kind']][z['metric']]
        for k in z:
            if k in ('scope','kind','metric'):continue
            ck(u+'/csv/'+z['kind']+'/'+z['metric']+'/'+k,z[k]==('' if c[k] is None else str(c[k])))
    byunit[u]={'counts':counts,'photon_width_reduction_percent':a['global_OFF']['absolute']['P_final']['width_reduction_percent'],'heat_width_reduction_percent':a['global_OFF']['absolute']['H_total_eV']['width_reduction_percent'],'analysis_identity':identity(P/'analysis'/u/'GLOBAL_ANALYSIS.json'),'semantic_sha256':ai['semantic_sha256']}
schedule=read(P/'runs/SCHEDULE_RECEIPT.json')
ck('work_unit_order',[x['label'] for x in schedule['actual']]==list(UNITS))
ck('work_unit_exit_all_zero',all(x['exit_code']==0 and x['automatic_retries']==0 for x in schedule['actual']))
for u in UNITS:
    ni=read(P/'runs'/u/'NUMERICAL_IDENTITY.json')
    ck(u+'/resource_scoped',read(P/'runs'/u/'RESOURCE_RECEIPT.json')['scientific_work_unit_invocations']==1)
drift={}
for kind,key in [('absolute','P_final'),('absolute','H_total_eV')]:
    w60=width(B(ind['work_units']['N32_P60']['budgets'][kind][key]['raw_new_full']))
    w80=width(B(ind['work_units']['N32_P80']['budgets'][kind][key]['raw_new_full']))
    drift[key]={'relative_width_change_P80_vs_P60_exact':str((w80-w60)/w60),'relative_width_change_display':display((w80-w60)/w60)}
res={'schema':'bass-he-e13c6-primary-independent-analysis-comparison-v1','status':'PASS' if all(x['pass'] for x in checks) else 'FAIL','checks':len(checks),'failed_count':sum(not x['pass'] for x in checks),'failed_checks':[x for x in checks if not x['pass']],'work_units':byunit,'precision_control':drift,'analyzer_source_identity':identity(P/'code/analyze_refinement.py'),'numerical_source_lock_identity':identity(P/'SOURCE_LOCK.json'),'independent_audit_identity':identity(ROOT/'review/INDEPENDENT_FRACTION_AUDIT.json'),'independent_intersection_diagnostics':'INDEPENDENT_FRACTION_AUDIT computes a hypothetical old/new intersection as an unused diagnostic. Candidate replacement and admitted N512 result use raw new intervals without intersection. For N512 all 136 pairs are nested, so the diagnostic happens to coincide.','candidate_or_vendor_function_imports':0,'science_or_coefficient_invocations':0,'elapsed_seconds':time.monotonic()-started,'finished_utc':datetime.now(timezone.utc).isoformat()}
(ROOT/'review/PRIMARY_ANALYSIS_COMPARISON.json').write_text(json.dumps(res,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'status':res['status'],'checks':len(checks),'failed_count':res['failed_count'],'failed_checks':res['failed_checks'][:10],'precision_control':drift,'elapsed_seconds':res['elapsed_seconds']}))
sys.exit(0 if res['status']=='PASS' else 1)
