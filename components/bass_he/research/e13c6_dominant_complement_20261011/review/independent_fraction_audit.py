#!/usr/bin/env python3
"""Independent bounded saved-output audit; no candidate/vendor imports or science calls."""
from pathlib import Path
from fractions import Fraction as F
from datetime import datetime, timezone
import csv, hashlib, json, math, sys, time

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / 'BASS_HE_E13C6_DOMINANT_COMPLEMENT_REFINEMENT_20261011_v1'
SP = ('HI','HeI','HeII')
NODES = (101,102,410,413)
UNITS = ('N32_P60','N128_P60','N512_P60','N32_P80')
EPS=F.from_float(1.602176634e-12)
MOMS=['Z_eV','QN','QE_eV']+[a+'_'+s+('_eV' if a!='A' else '') for a in ('A','B','H') for s in SP]
checks=[]
read_ids={}
def load(f):
    data=f.read_bytes();read_ids[str(f.relative_to(ROOT))]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
    return json.loads(data)
def identity(f):
    b=f.read_bytes();return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def ck(label,ok):
    checks.append({'id':label,'pass':bool(ok)})
def B(x): return F(x['lo']),F(x['hi'])
def E(x): return {'lo':str(x[0]),'hi':str(x[1])}
def add(a,b):return a[0]+b[0],a[1]+b[1]
def sub(a,b):return a[0]-b[1],a[1]-b[0]
def mul(a,b):
    x=[aa*bb for aa in a for bb in b];return min(x),max(x)
def scale(a,w):return mul(a,(w,w))
def sum_boxes(seq):
    out=(F(0),F(0))
    for b in seq:out=add(out,b)
    return out
def encloses(a,b):return a[0]<=b[0]<=b[1]<=a[1]
def overlap(a,b):return max(a[0],b[0])<=min(a[1],b[1])
def cap(x):return F.from_float(float(x))
def width(a):return a[1]-a[0]
def canon(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def totals(d):
    for prefix in ('A','B','H'):
        suffix='_eV' if prefix!='A' else ''
        d[prefix+'_total'+suffix]=sum_boxes(d[prefix+'_'+s+suffix] for s in SP)
    return d
def old_metrics(p):
    w=B(p['weight'])[0]
    a={k:B(v) for k,v in p['weighted_reduction'].items()}
    c={k:scale(B(v),w) for k,v in p['cumulative_correction'].items()}
    c['P_final']=scale(B(p['segments'][-1]['DP']),w)
    c['energy_eV']=scale(B(p['segments'][-1]['energy_endpoint_minus_captured_erg']),w/EPS)
    return {'absolute':totals(a),'correction':totals(c)}
def new_metrics(t,w):
    a={k:scale(B(t['true_moment_enclosures'][k]),w) for k in MOMS}
    c={k:scale(B(t['cumulative_moment_corrections'][k]['interval']),w) for k in MOMS}
    a['P_final']=scale(B(t['final_photon']['true_absolute_interval']),w)
    a['anchor']=scale(B(t['summed_true_anchor_eV']),w)
    c['P_final']=scale(B(t['final_photon']['true_minus_captured_interval']),w)
    c['energy_eV']=scale(B(t['final_energy_stock_eV']['true_minus_captured_interval']),w)
    return {'absolute':totals(a),'correction':totals(c)}
def walk_boxes(x,path):
    if isinstance(x,dict):
        if set(x)=={'lo','hi'}:
            try:ok=B(x)[0]<=B(x)[1]
            except (ValueError,ZeroDivisionError,OverflowError):ok=False
            ck(path+'/finite_ordered',ok)
        else:
            for k,v in x.items():walk_boxes(v,path+'/'+k)
    elif isinstance(x,list):
        for i,v in enumerate(x):walk_boxes(v,path+'/'+str(i))
def main():
    started=time.monotonic()
    lock=load(P/'SOURCE_LOCK.json')
    ck('fixed_source_lock_digest',identity(P/'SOURCE_LOCK.json')['sha256']=='0b4688c61c6070e0663fa78043a4ff3c37af2250f1e9d98d1e5485f568efaf47')
    for name,rec in lock['files'].items():ck('lock/'+name,identity(P/name)==rec)
    pr19=ROOT/'dependencies/pr19/BASS_HE_E13C5_INCOMING_ANCHOR_ENCLOSURE_20261011_v1/code'
    for name in ('directed_interval.py','local_enclosure.py','path_enclosure.py'):
        ck('vendor_unchanged/'+name,(P/'code/vendor'/name).read_bytes()==(pr19/name).read_bytes())
    prov=load(P/'INPUT_PROVENANCE.json')
    for rec in prov['source_records']:
        if 'local_file' in rec:ck('source_member/'+rec['local_file'],identity(P/rec['local_file'])=={k:rec[k] for k in ('bytes','sha256')})
    controls=load(P/'inputs/PATH_CONTROLS.json')['controls']
    old=[json.loads(x) for x in (P/'inputs/OLD_PATHS_OFF4.jsonl').read_bytes().splitlines()]
    read_ids[str((P/'inputs/OLD_PATHS_OFF4.jsonl').relative_to(ROOT))]=identity(P/'inputs/OLD_PATHS_OFF4.jsonl')
    ck('four_old_key_order',[(x['mode'],x['node']) for x in old]==[('OFF',n) for n in NODES])
    old={x['node']:x for x in old}
    rawrows=list(csv.DictReader((P/'inputs/source/OFF_SEGMENTS.csv').open()))
    selected={(r['mode'],int(r['step']),int(r['node']),int(r['segment'])):r for r in rawrows if int(r['step']) in (1,2) and int(r['node']) in NODES}
    ck('exact_eight_control_rows',len(controls)==len(selected)==8 and all(c['row']==selected[tuple(c['key'])] for c in controls))
    stages={int(x['step']):x for x in csv.DictReader((P/'inputs/source/OFF_STAGES.csv').open())}
    nodes={(int(x['step']),int(x['node'])):x for x in csv.DictReader((P/'inputs/source/OFF_NODES.csv').open())}
    weights={}
    for i,c in enumerate(controls):
        r=c['row'];node=c['key'][2];step=c['key'][1];oldseg=old[node]['segments'][step-1]
        ck('control/'+str(i)+'/stage',c['stage']==stages[step] and c['stage']['mode']=='OFF')
        ck('control/'+str(i)+'/node',c['node_row']==nodes[step,node])
        ck('control/'+str(i)+'/captured_width',cap(r['a'])+cap(r['h'])==cap(r['b']) and cap(r['h'])>0)
        ck('control/'+str(i)+'/source_mask',c['source_on'] is True and cap(r['source_on'])==1 and c['mask']==dict(HI=True,HeI=False,HeII=False))
        ck('control/'+str(i)+'/old_branch',oldseg['key']==c['key'] and oldseg['source_on']==c['source_on'] and oldseg['mask']==c['mask'])
        weights[node]=cap(r['weight'])
        ck('control/'+str(i)+'/weight',B(old[node]['weight'])==(weights[node],weights[node]) and weights[node]>0)
        refs={'QN':cap(r['qn']),'QE_eV':cap(r['qe'])/EPS,'Z_eV':cap(r['red'])/EPS}
        for sp,chi in zip(SP,(13.598434599702,24.587389011,54.41776)):
            refs['A_'+sp]=cap(r['A_'+sp]);refs['B_'+sp+'_eV']=cap(r['B_'+sp])/EPS
            refs['H_'+sp+'_eV']=refs['B_'+sp+'_eV']-cap(chi)*refs['A_'+sp]
        for k,v in refs.items():ck('control/'+str(i)+'/captured/'+k,encloses(B(oldseg['captured'][k]),(v,v)))
    for k in range(0,8,2):
        a,b=[c['row'] for c in controls[k:k+2]]
        ck('initial/'+str(k),cap(a['f0'])==0)
        for x,y in [('b','a'),('n','f0'),('eta','eta'),('weight','weight')]:
            ck('stitch/'+str(k)+'/'+x,cap(a[x])==cap(b[y]))
    oldm={n:old_metrics(old[n]) for n in NODES}
    budgets=load(P/'inputs/PREDECESSOR_BUDGET.json')
    predecessor=load(ROOT/'intake/returned/BUDGET_EXEC01/BUDGET/RESULTS.json')
    ck('predecessor_actual_return_digest',identity(ROOT/'intake/returned/BUDGET_EXEC01/BUDGET/RESULTS.json')['sha256']==budgets['source_return_result_sha256'])
    ck('partition_nodes',budgets['selected_nodes']==list(NODES) and budgets['previously_admitted_replacement_nodes']==[0,700] and budgets['direct_retained_nodes']==2434)
    for kind,rows in budgets['budgets'].items():
        for key,rec in rows.items():
            selected_sum=sum_boxes(oldm[n][kind][key] for n in NODES)
            full=B(predecessor['budgets_by_mode']['OFF'][kind][key]['hybrid']['full'])
            retained=B(rec['retained_outside_K4'])
            ck('old_selected/'+kind+'/'+key,selected_sum==B(rec['old_selected_K4']))
            ck('predecessor_full/'+kind+'/'+key,full==B(rec['predecessor_full']))
            ck('direct_retained_plus_K4/'+kind+'/'+key,add(retained,selected_sum)==full)
    unit_summary={}; primary_metrics={}
    projection_keys=('schema','work_unit','input_checks','new_coefficient_evaluations','new_local_enclosures','reused_local_enclosures','rounding_operation_counts','source_unchanged_during_run','source_lock_sha256','forbidden_invocations')
    for unit in UNITS:
        result=load(P/'runs'/unit/'RESULTS.json');pr=load(P/'runs'/unit/'NUMERICAL_PROJECTION.json');ni=load(P/'runs'/unit/'NUMERICAL_IDENTITY.json');rr=load(P/'runs'/unit/'RESOURCE_RECEIPT.json')
        expected_pr={k:result[k] for k in projection_keys};expected_pr['tracks']=[{k:v for k,v in t.items() if k!='elapsed_seconds'} for t in result['tracks']]
        ck(unit+'/projection_all_keys_exact',expected_pr==pr)
        ck(unit+'/semantic_digest',hashlib.sha256(b'bass-he-e13c6-off4-semantic-v1\n'+canon(pr)).hexdigest()==ni['semantic_sha256'])
        ck(unit+'/identity_files',identity(P/'runs'/unit/'RESULTS.json')['sha256']==ni['result_file_sha256'] and identity(P/'runs'/unit/'NUMERICAL_PROJECTION.json')['sha256']==ni['projection_file_sha256'])
        ck(unit+'/invocations',result['new_local_enclosures']==8 and result['reused_local_enclosures']==0 and result['new_coefficient_evaluations']==16*result['work_unit']['N'] and all(v==0 for v in result['forbidden_invocations'].values()))
        ck(unit+'/source_before_after',result['source_unchanged_during_run'] and result['identity']['source_sha256_before_run']==result['source_sha256_after_run']=={k:v['sha256'] for k,v in lock['files'].items()})
        ck(unit+'/lock_identity',result['source_lock_sha256']==identity(P/'SOURCE_LOCK.json')['sha256'])
        ck(unit+'/track_order',[t['track'] for t in result['tracks']]==[{'mode':'OFF','node':n} for n in NODES])
        ck(unit+'/claim_ceiling',all(result[k]=='HOLD' for k in ('physical','production','continuum','receiver')))
        walk_boxes(result['tracks'],unit+'/tracks')
        metrics={}; comparison_counts={'fields':0,'new_subset_old':0,'overlap':0,'raw_width_smaller':0}
        for ti,t in enumerate(result['tracks']):
            node=t['track']['node'];tag=unit+'/'+str(node)
            ck(tag+'/two_segments_one_seam',len(t['segments'])==2 and len(t['seams'])==1)
            ck(tag+'/initial_incoming_zero',B(t['segments'][0]['incoming']['interval'])==(F(0),F(0)) and F(t['segments'][0]['incoming']['center'])==F(t['segments'][0]['incoming']['radius'])==0)
            ck(tag+'/full_signed_seam_continuity',t['segments'][1]['incoming']==t['seams'][0]['next_incoming'])
            for si,s in enumerate(t['segments']):
                control=controls[2*ti+si];prefix=tag+'/segment'+str(si);inc=s['incoming'];rem=s['remainder'];radius=F(inc['radius']);center=F(inc['center'])
                ck(prefix+'/key',s['key']==control['key'])
                ck(prefix+'/new_local_only',s['local']['origin']=='NEW_E13C5_LOCAL_INTEGRALS' and s['local']['new_coefficient_evaluations']==2*result['work_unit']['N'])
                ck(prefix+'/S_upper',F(rem['S_upper'])>=abs(center)+radius+B(s['local']['bounds']['B_r'])[1])
                for key,v in s['outputs'].items():
                    prefix2=prefix+'/'+key;g=B(s['gains'][key]);candidate=F(v['candidate']);vr=F(v['radius']);num=F(v['numerical_and_representation_radius'])
                    ck(prefix2+'/represented_reference',encloses(B(s['representation_exactfrozen_minus_captured'][key]),sub(B(s['frozen'][key]),B(s['captured'][key]))))
                    ck(prefix2+'/firstvariation_incoming',encloses(B(s['firstvariation_with_candidate_incoming'][key]),add(B(s['local']['signed'][key]),scale(g,center))))
                    ck(prefix2+'/numerical_radius',num>=max(abs(B(v['centered_firstvariation_plus_representation_interval'])[0]-candidate),abs(B(v['centered_firstvariation_plus_representation_interval'])[1]-candidate)))
                    ck(prefix2+'/incoming_radius',F(rem['incoming_upper'][key])>=max(abs(g[0]),abs(g[1]))*radius)
                    ck(prefix2+'/coefficient_remainder',F(rem['nonlinear_upper'][key])>=F(rem['S_upper'])*F(rem['T_upper'][key]))
                    ck(prefix2+'/total_before_numerical',F(rem['total_before_numerical_upper'][key])>=F(rem['incoming_upper'][key])+F(rem['nonlinear_upper'][key]))
                    ck(prefix2+'/radius_components',vr>=num+F(rem['total_before_numerical_upper'][key]))
                    ck(prefix2+'/correction_bounds',encloses(B(v['true_minus_captured_interval']),(candidate-vr,candidate+vr)))
                    ck(prefix2+'/absolute_bounds',encloses(B(v['true_absolute_interval']),add(B(s['captured'][key]),B(v['true_minus_captured_interval']))))
                for key,v in s['ledger_enclosures'].items():ck(prefix+'/ledger/'+key,B(v)[0]<=0<=B(v)[1])
            seam=t['seams'][0];left=t['segments'][0];right_control=controls[2*ti+1];d=B(seam['DeltaE_eV'])
            ck(tag+'/seam_signed_delta',encloses(d,sub((cap(right_control['row']['e0']),)*2,B(left['endpoint_energy_eV']))))
            ck(tag+'/seam_preserved_nonzero_sign',(d[1]<0 if node in (101,102,410) else d[0]>0))
            ck(tag+'/seam_anchor_product',encloses(B(seam['true_anchor_eV']),mul(d,add(B(left['captured']['P1']),B(left['outputs']['P1']['true_minus_captured_interval'])))))
            ck(tag+'/seam_incoming_carry',encloses(B(seam['next_incoming']['interval']),add(B(left['outputs']['P1']['true_minus_captured_interval']),B(seam['captured_photon_stitch_residual']))))
            for key,v in t['global_ledger_enclosures'].items():ck(tag+'/global_ledger/'+key,B(v)[0]<=0<=B(v)[1])
            for key,v in t['cumulative_moment_corrections'].items():
                cs=sum(F(s['outputs'][key]['candidate']) for s in t['segments'])
                rs=sum(F(s['outputs'][key]['radius']) for s in t['segments'])
                ck(tag+'/cumulative_nondamped/'+key,encloses(B(v['interval']),(cs-rs,cs+rs)))
            m=new_metrics(t,weights[node]);metrics[node]=m
            for kind,rows in m.items():
                ck(tag+'/mapper_keys/'+kind,set(rows)==set(oldm[node][kind]))
                for key,newbox in rows.items():
                    oldbox=oldm[node][kind][key];same=overlap(oldbox,newbox)
                    ck(tag+'/old_new_nonempty/'+kind+'/'+key,same)
                    comparison_counts['fields']+=1;comparison_counts['overlap']+=int(same)
                    comparison_counts['new_subset_old']+=int(encloses(oldbox,newbox));comparison_counts['raw_width_smaller']+=int(width(newbox)<width(oldbox))
            if unit=='N512_P60':primary_metrics[str(node)]={kind:{key:{'old':E(oldm[node][kind][key]),'raw_new':E(v),'admitted_intersection':E((max(v[0],oldm[node][kind][key][0]),min(v[1],oldm[node][kind][key][1])))} for key,v in rows.items()} for kind,rows in m.items()}
        summary={}
        for kind,rows in budgets['budgets'].items():
            summary[kind]={}
            for key,rec in rows.items():
                old_full=B(rec['predecessor_full']);retained=B(rec['retained_outside_K4']);old_selected=B(rec['old_selected_K4'])
                new_sel=sum_boxes(metrics[n][kind][key] for n in NODES)
                admitted_sel=sum_boxes((max(oldm[n][kind][key][0],metrics[n][kind][key][0]),min(oldm[n][kind][key][1],metrics[n][kind][key][1])) for n in NODES)
                raw_full=add(retained,new_sel);admitted_full=add(retained,admitted_sel)
                summary[kind][key]={'old_full':E(old_full),'raw_new_full':E(raw_full),'admitted_full':E(admitted_full),'old_selected':E(old_selected),'raw_new_selected':E(new_sel),'admitted_selected':E(admitted_sel),'raw_width_gain':str(width(old_full)-width(raw_full)),'admitted_width_gain':str(width(old_full)-width(admitted_full)),'relative_raw_gain':str((width(old_full)-width(raw_full))/width(old_full)) if width(old_full)>0 else None,'relative_admitted_gain':str((width(old_full)-width(admitted_full))/width(old_full)) if width(old_full)>0 else None}
        unit_summary[unit]={'comparisons':comparison_counts,'semantic_sha256':ni['semantic_sha256'],'resources':rr,'budgets':summary}
    report={'schema':'bass-he-e13c6-independent-fraction-audit-v1','status':'PASS' if all(c['pass'] for c in checks) else 'FAIL','checks':len(checks),'failed_count':sum(not c['pass'] for c in checks),'failed_checks':[c for c in checks if not c['pass']],'check_definitions':'Source/input/point-reference checks; exact rational enclosure relationships and narrow 4-path+34-field mapping/budgets. Does not execute or independently rederive the inherited scientific coefficient kernels.','source_read_identities':read_ids,'work_units':unit_summary,'primary_per_path_metrics':primary_metrics,'scientific_kernel_imports':0,'coefficient_evaluations':0,'solver_invocations':0,'old_full_budget_invocations':0,'intake_contribution':'Same reviewer previously verified actual E13C5 return provenance/content. No E13C6 candidate or theory authorship.','elapsed_seconds':time.monotonic()-started,'finished_utc':datetime.now(timezone.utc).isoformat()}
    out=ROOT/'review/INDEPENDENT_FRACTION_AUDIT.json'
    out.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({'status':report['status'],'checks':len(checks),'failed_count':report['failed_count'],'failed_checks':report['failed_checks'][:30],'elapsed_seconds':report['elapsed_seconds']}))
    for key in ('P_final','H_total_eV'):
        a=unit_summary['N512_P60']['budgets']['absolute'][key]
        print(json.dumps({'metric':key,'relative_raw_gain':float(F(a['relative_raw_gain'])),'relative_admitted_gain':float(F(a['relative_admitted_gain'])),'old_width':float(width(B(a['old_full']))),'raw_new_width':float(width(B(a['raw_new_full']))),'admitted_width':float(width(B(a['admitted_full'])))}))
    return 0 if report['status']=='PASS' else 1
if __name__=='__main__':sys.exit(main())
