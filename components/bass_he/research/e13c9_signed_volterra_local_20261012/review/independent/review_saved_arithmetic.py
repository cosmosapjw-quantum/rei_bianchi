#!/usr/bin/env python3
"""Independent E13C9 saved-evidence review; no candidate or quadrature import.

Fraction arithmetic reconstructs reported metric definitions and interval
assembly. A separate 100-digit Decimal exp enclosure is used only to check
saved causal recurrence/range algebra; no coefficients or paths are integrated.
"""
from collections import Counter
from datetime import datetime, timezone
from decimal import Decimal, Context, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN
from fractions import Fraction as F
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
RESTORE = ROOT.parent / 'RESTORED_E13C8'
R7 = RESTORE / 'runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1'
OUT = Path(__file__).with_name('SAVED_ARITHMETIC_REVIEW.json')
SP = ('HI', 'HeI', 'HeII')
MOM = ['Z_eV', 'QN', 'QE_eV'] + [p+'_'+s+('_eV' if p != 'A' else '') for p in ('A','B','H') for s in SP]
CHI = tuple(F.from_float(x) for x in (13.598434599702,24.587389011,54.41776))
COUNTS, FAILURES = Counter(), []
NEAR = Context(prec=100, rounding=ROUND_HALF_EVEN)
DOWN = Context(prec=100, rounding=ROUND_FLOOR)
UP = Context(prec=100, rounding=ROUND_CEILING)

def read(p):
    return json.loads(Path(p).read_bytes())

def sha(p):
    with Path(p).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()

def canonical(x):
    return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()

def pin(p):
    p=Path(p)
    return {'path':str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p),
            'bytes':p.stat().st_size,'sha256':sha(p)}

def check(category, condition, location, details=None):
    COUNTS[category] += 1
    if not condition:
        FAILURES.append({'category':category,'location':location,'details':details})

def box(o):
    a,b=F(o['lo']),F(o['hi'])
    if a>b:
        raise ArithmeticError('invalid saved interval')
    return (a,b)

def point(x):
    return (F(x),F(x))

def add(*args):
    return tuple(sum(v[i] for v in args) for i in (0,1))

def neg(a):
    return (-a[1],-a[0])

def sub(a,b):
    return add(a,neg(b))

def mul(a,b):
    products=[x*y for x in a for y in b]
    return min(products),max(products)

def width(a):
    return a[1]-a[0]

def contains(a,b):
    return a[0]<=b[0]<=b[1]<=a[1]

def zero(a):
    return a[0]<=0<=a[1]

def absmax(a):
    return max(abs(a[0]),abs(a[1]))

def encode(a):
    return {'lo':str(a[0]),'hi':str(a[1])}

def display(x):
    return str(NEAR.divide(Decimal(x.numerator),Decimal(x.denominator)))

@lru_cache(maxsize=128)
def exp_point(x):
    lo=DOWN.divide(Decimal(x.numerator),Decimal(x.denominator))
    hi=UP.divide(Decimal(x.numerator),Decimal(x.denominator))
    if x==0:
        return point(1)
    return F(NEAR.next_minus(NEAR.exp(lo))),F(NEAR.next_plus(NEAR.exp(hi)))

def metrics(track,weight):
    absolute={k:mul(box(track['true_moment_enclosures'][k]),point(weight)) for k in MOM}
    absolute['P_final']=mul(box(track['final_photon']['true_absolute_interval']),point(weight))
    absolute['anchor']=mul(box(track['summed_true_anchor_eV']),point(weight))
    correction={k:mul(box(track['cumulative_moment_corrections'][k]['interval']),point(weight)) for k in MOM}
    correction['P_final']=mul(box(track['final_photon']['true_minus_captured_interval']),point(weight))
    correction['energy_eV']=mul(box(track['final_energy_stock_eV']['true_minus_captured_interval']),point(weight))
    for collection in (absolute,correction):
        for p in ('A','B','H'):
            suffix='_eV' if p!='A' else ''
            collection[p+'_total'+suffix]=add(*(collection[p+'_'+s+suffix] for s in SP))
    return {'absolute':absolute,'correction':correction}

def compare(a,b):
    rows=[]
    for kind in sorted(a):
        for name in sorted(a[kind]):
            old,new=a[kind][name],b[kind][name]
            wo,wn=width(old),width(new)
            rows.append({'kind':kind,'quantity':name,'old':encode(old),'new_raw':encode(new),
                'old_width':str(wo),'new_width':str(wn),
                'overlap':max(old[0],new[0])<=min(old[1],new[1]),
                'nested':contains(old,new),'width_nonincreasing':wn<=wo,
                'gain_fraction':str((wo-wn)/wo) if wo else None})
    return rows

def all_boxes(obj,loc):
    if isinstance(obj,dict):
        if set(obj)=={'lo','hi'}:
            check('finite_ordered_boxes',box(obj)[0]<=box(obj)[1],loc)
        else:
            for k,v in obj.items():
                all_boxes(v,loc+'/'+k)
    elif isinstance(obj,list):
        for j,v in enumerate(obj):
            all_boxes(v,loc+'/'+str(j))

def source_revision_for(digest):
    candidates=[ROOT/'SOURCE_LOCK.json']+list((ROOT/'evidence').rglob('SOURCE_LOCK.json'))
    matches=[p for p in candidates if sha(p)==digest]
    if len(matches)!=1:
        raise ValueError('missing or ambiguous source lock identity '+digest)
    lock=read(matches[0])
    for rel,identity in lock['files'].items():
        possibilities=[ROOT/rel,matches[0].parent/rel,matches[0].parent/Path(rel).name]
        actual=next((p for p in possibilities if p.is_file() and p.stat().st_size==identity['bytes'] and sha(p)==identity['sha256']),None)
        check('source_revision_payloads',actual is not None,str(matches[0])+':'+rel)
    return str(matches[0].relative_to(ROOT))

def check_segment(seg,prior,control,M,loc):
    check('cache_local_signed_identity',seg['local']['signed']==prior['local']['signed'],loc)
    check('cache_local_bounds_identity',seg['local']['bounds']==prior['local']['bounds'],loc)
    check('cache_original_resolution',seg['local']['N_base']==prior['local']['cell_coverage']['dyadic_cells'],loc)
    for name in ('frozen','gains','captured','endpoint_energy_eV','initial_energy_eV','frozen_Lh'):
        check('unchanged_frozen_and_capture',seg[name]==prior[name],loc+'/'+name)
    c,eta=F(seg['incoming']['center']),F(seg['incoming']['radius'])
    check('incoming_interval',eta>=0 and contains(box(seg['incoming']['interval']),(c-eta,c+eta)),loc)
    r=seg['remainder']; b=seg['local']['bounds']; G={k:box(v) for k,v in seg['gains'].items()}
    S,D=F(r['S_upper']),F(r['D_upper'])
    check('new_S_carry_bound',S>=abs(c)+eta+F(b['B_r']['hi']),loc)
    check('whole_operator_D',D==F(b['D_L']['hi']) and D>=0,loc)
    check('unchanged_T_bounds',r['T_upper']==prior['remainder']['T_upper'],loc)
    second=seg['second_correction']
    for k in seg['outputs']:
        T=F(r['T_upper'][k]); inc=F(r['incoming_upper'][k]); coupling=F(r['incoming_coupling_upper'][k]); tail=F(r['second_volterra_remainder_upper'][k]); total=F(r['total_before_numerical_upper'][k])
        check('analytic_tail_components',inc>=absmax(G[k])*eta and coupling>=T*eta and tail>=T*D*S and total>=inc+coupling+tail,loc+'/'+k)
        f=box(seg['firstvariation_with_candidate_incoming'][k])
        check('first_variation_cache_plus_new_center',contains(f,add(box(baseline_signed:=seg['local']['signed'][k]),mul(G[k],point(c)))),loc+'/'+k)
        raw=box(seg['outputs'][k]['centered_secondvariation_plus_representation_interval'])
        expected=add(f,box(second['signed'][k]),sub(box(seg['frozen'][k]),box(seg['captured'][k])))
        check('signed_assembly',contains(raw,expected),loc+'/'+k)
        out=seg['outputs'][k]; center=F(out['candidate']); num=F(out['numerical_and_representation_radius']); radius=F(out['radius'])
        check('outward_center_and_radius',num>=absmax(sub(raw,point(center))) and radius>=num+total,loc+'/'+k)
        check('output_correction_enclosure',contains(box(out['true_minus_captured_interval']),(center-radius,center+radius)),loc+'/'+k)
        check('output_absolute_enclosure',contains(box(out['true_absolute_interval']),add(box(seg['captured'][k]),box(out['true_minus_captured_interval']))),loc+'/'+k)
    for k in ('QN','QE_eV'):
        check('unchanged_source_outputs',box(second['signed'][k])==point(0) and F(r['total_before_numerical_upper'][k])==0 and seg['outputs'][k]['true_minus_captured_interval']==prior['outputs'][k]['true_minus_captured_interval'],loc+'/'+k)
    check('prefix_center_only',box(second['prefix_initial'])==point(c) and second['incoming_uncertainty_in_prefix'] is False,loc)
    check('prefix_work_identity',len(second['cells'])==M and second['M_second']==M and second['new_coefficient_evaluations']==2*M and second['firstvariation_quadrature_replays']==0,loc)
    h=F.from_float(float(control['row']['h'])); L=sum(F.from_float(float(control['row']['lambda_'+sp])) for sp in SP)
    a=h*L; step=F(1,M); decay=exp_point(-a*step)
    dspan=(decay[0],F(1)); jspan=(F(0),(1-decay[0])/a) if a else (F(0),step)
    previous=point(c); trunc=F(0); sums={'P1':point(0),'H_total_eV':point(0)}
    for j,cell in enumerate(second['cells']):
        prefixleft=box(cell['prefix_left']); prefixright=box(cell['prefix_right']); within=box(cell['prefix_whole_cell']); forcing=box(cell['forcing_midpoint_integral']); radius=F(cell['forcing_midpoint_truncation_radius'])
        check('causal_cell_partition',cell['cell']==j and box(cell['x_left'])==point(F(j,M)) and box(cell['x_right'])==point(F(j+1,M)),loc+'/'+str(j))
        check('causal_prefix_continuity',prefixleft==previous,loc+'/'+str(j))
        lower_range=add(mul(dspan,prefixleft),mul(point(h),mul(jspan,box(cell['r_whole_cell']))))
        check('whole_cell_prefix_enclosure',contains(within,lower_range),loc+'/'+str(j))
        predicted=add(mul(decay,prefixleft),forcing,(-radius,radius))
        check('prefix_recurrence_saved_algebra',radius>=0 and contains(prefixright,predicted),loc+'/'+str(j))
        trunc+=radius; previous=prefixright
        sums['P1']=add(sums['P1'],box(cell['photon_signed_cell_integral']))
        sums['H_total_eV']=add(sums['H_total_eV'],box(cell['heat_total_signed_cell_integral_eV']))
    check('prefix_endpoint_identity',previous==box(second['prefix_endpoint']),loc)
    check('prefix_truncation_sum',F(second['prefix_local_truncation_radii_sum_upper'])>=trunc,loc)
    for k,v in sums.items():
        check('signed_cell_sum',contains(box(second['signed'][k]),v),loc+'/'+k)
    first={k:box(v) for k,v in seg['firstvariation_with_candidate_incoming'].items()}; secondvalues={k:box(v) for k,v in second['signed'].items()}
    own={'firstvariation_number':sub(add(first['P1'],first['A_total']),add(point(c),first['QN'])),
         'firstvariation_energy_eV':sub(add(first['P1_energy_eV'],first['B_total_eV'],first['Z_eV']),add(mul(box(seg['initial_energy_eV']),point(c)),first['QE_eV'])),
         'secondvariation_number':add(secondvalues['P1'],secondvalues['A_total']),
         'secondvariation_energy_eV':add(secondvalues['P1_energy_eV'],secondvalues['B_total_eV'],secondvalues['Z_eV'])}
    for name,vals in (('firstvariation',first),('secondvariation',secondvalues)):
        for sp,chi in zip(SP,CHI):
            own[name+'_heat_'+sp]=add(sub(vals['H_'+sp+'_eV'],vals['B_'+sp+'_eV']),mul(point(chi),vals['A_'+sp]))
    for k,v in own.items():
        check('segment_independent_ledgers',zero(v) and zero(box(seg['ledger_enclosures'][k])),loc+'/'+k)
    for k,v in seg['ledger_enclosures'].items():
        check('segment_saved_ledgers',zero(box(v)),loc+'/'+k)
    domain=seg['new_coefficient_domain']
    check('positive_actual_coefficient_domain',domain['positive_rate_evaluations']==2*M and domain['gas_checked_evaluations']==2*M and F(domain['H_min'])>0 and F(domain['q_min'])>=0 and F(domain['energy_min_eV'])>0 and F(domain['active_heat_weight_min_eV'])>=0,loc)

def check_track(track,baseline,controls,M,loc):
    check('segment_order_and_count',[x['key'] for x in track['segments']]==[x['key'] for x in controls]==[x['key'] for x in baseline['segments']],loc)
    check('seam_count',len(track['seams'])==len(controls)-1,loc)
    keys=list(track['cumulative_moment_corrections']); sumcorr={k:point(0) for k in keys}; sumcap={k:point(0) for k in keys}
    anchor=point(0)
    for j,(seg,prior,control) in enumerate(zip(track['segments'],baseline['segments'],controls)):
        sloc=loc+'/segment'+str(j)
        check_segment(seg,prior,control,M,sloc)
        if j==0:
            check('initial_correction_zero',F(seg['incoming']['center'])==F(seg['incoming']['radius'])==0,sloc)
        else:
            check('carry_identity',seg['incoming']==track['seams'][j-1]['next_incoming'],sloc)
        for k in keys:
            out=seg['outputs'][k]; c=F(out['candidate']); r=F(out['radius']); sumcorr[k]=add(sumcorr[k],(c-r,c+r)); sumcap[k]=add(sumcap[k],box(seg['captured'][k]))
            check('cumulative_correction_enclosure',contains(box(seg['cumulative_moment_corrections'][k]['interval']),sumcorr[k]),sloc+'/'+k)
            check('cumulative_capture_enclosure',contains(box(seg['cumulative_captured_moments'][k]),sumcap[k]),sloc+'/'+k)
        if j+1<len(controls):
            seam=track['seams'][j]; nextcontrol=controls[j+1]
            check('seam_order',seam['left']==control['key'] and seam['right']==nextcontrol['key'],sloc)
            check('seam_fixed_events',seam['event']['left_mask']==control['mask'] and seam['event']['right_mask']==nextcontrol['mask'] and seam['event']['source_left']==control['source_on'] and seam['event']['source_right']==nextcontrol['source_on'],sloc)
            de=sub(point(F.from_float(float(nextcontrol['row']['e0']))),box(seg['endpoint_energy_eV']))
            gap=sub(box(seg['captured']['P1']),point(F.from_float(float(nextcontrol['row']['f0']))))
            check('signed_energy_jump',contains(box(seam['DeltaE_eV']),de),sloc)
            check('exact_captured_photon_stitch',box(seam['captured_photon_stitch_residual'])==gap==point(0),sloc)
            photon=seg['outputs']['P1']; c=F(photon['candidate']); eta=F(photon['radius'])
            check('new_carry_enclosure',contains(box(seam['next_incoming']['interval']),add((c-eta,c+eta),gap)),sloc)
            anchorvalue=mul(box(seam['DeltaE_eV']),add(box(seg['captured']['P1']),box(photon['true_minus_captured_interval'])))
            check('signed_anchor_enclosure',contains(box(seam['true_anchor_eV']),anchorvalue),sloc)
            anchor=add(anchor,box(seam['true_anchor_eV']))
    check('summed_signed_anchor',contains(box(track['summed_true_anchor_eV']),anchor),loc)
    for k in keys:
        check('track_correction_end_state',track['cumulative_moment_corrections'][k]==track['segments'][-1]['cumulative_moment_corrections'][k],loc+'/'+k)
        check('track_true_moments',contains(box(track['true_moment_enclosures'][k]),add(box(track['cumulative_captured_moments'][k]),box(track['cumulative_moment_corrections'][k]['interval']))),loc+'/'+k)
    moments={k:box(v) for k,v in track['true_moment_enclosures'].items()}; f0=F.from_float(float(controls[0]['row']['f0'])); e0=F.from_float(float(controls[0]['row']['e0']))
    own={'number':sub(add(box(track['final_photon']['true_absolute_interval']),moments['A_total']),add(point(f0),moments['QN'])),
         'energy_eV_with_anchor_subtracted':sub(add(box(track['final_energy_stock_eV']['true_absolute_interval']),moments['B_total_eV'],moments['Z_eV']),add(point(e0*f0),moments['QE_eV'],box(track['summed_true_anchor_eV'])))}
    for sp,chi in zip(SP,CHI):
        own['heat_'+sp]=add(sub(moments['H_'+sp+'_eV'],moments['B_'+sp+'_eV']),mul(point(chi),moments['A_'+sp]))
    for k,v in own.items():
        check('global_independent_ledgers',zero(v) and zero(box(track['global_ledger_enclosures'][k])),loc+'/'+k)

def main():
    started=time.perf_counter(); startedutc=datetime.now(timezone.utc).isoformat()
    if OUT.exists():
        raise FileExistsError(OUT)
    selected=read(ROOT/'evidence/SELECTED_PATHS.json'); plan=read(ROOT/'WORK_PLAN.json')
    sys.path.insert(0,str(R7/'code'))
    from off_path_worker import Context
    ctx=Context(R7) # source-gated input reading only; no Context.run.
    check('baseline_source_lock',ctx.source_lock_sha256==plan['baseline_source_lock_sha256']==selected['source_lock']['sha256'],'source')
    controls_by_node={}; baselines={}; originalpins=[]
    for rec in selected['selected_paths']:
        node=rec['node']; controls,old,index=ctx.inputs(node); ic=ctx.validate_inputs(node,controls,old)
        check('independent_input_revalidation',all(x['pass'] for x in ic),str(node))
        controls_by_node[node]=controls
        for key in ('baseline_result','baseline_admission','baseline_complete'):
            pp=RESTORE/rec[key]['path_relative_to_restore']; check('baseline_file_identity',pp.stat().st_size==rec[key]['bytes'] and sha(pp)==rec[key]['sha256'],str(node)+'/'+key)
        bp=RESTORE/rec['baseline_result']['path_relative_to_restore']; baseline=read(bp); baselines[node]=baseline; originalpins.append(pin(bp))
        cache=[{'key':s['key'],'local':{k:s['local'][k] for k in ('signed','bounds')}} for s in baseline['track']['segments']]
        check('baseline_cache_subtree',hashlib.sha256(canonical(cache)).hexdigest()==rec['cached_local_signed_and_bounds_sha256'],str(node))
        check('path_input_identity',index['path_input_sha256']==baseline['path_input_sha256']==rec['path_input_sha256'],str(node))
        check('N_base_identity',baseline['work']['N']==plan['N_base_by_node'][str(node)] and baseline['work']['precision']==60,str(node))
    records=[]; final_rows=[]; aggregate_old={k:F(0) for k in ('P_final','H_total_eV')}; aggregate_new=dict(aggregate_old); aggregate_m128=dict(aggregate_old)
    for node in plan['nodes']:
        baseline=baselines[node]; controls=controls_by_node[node]; weight=F.from_float(float(controls[0]['row']['weight'])); bm=metrics(baseline['track'],weight)
        check('positive_exact_weight',weight>0,str(node))
        for phase in ('M32_REPAIRED','M128')+ (('M256_TARGETED',) if node==1162 else ()):
            directory=ROOT/'runs'/phase/f'node_{node:06d}'; data=read(directory/'RESULT.json'); complete=read(directory/'COMPLETE.json'); comp=read(directory/'COMPARISON.json'); start=read(directory/'START.json')
            label=phase+'/'+str(node); M=data['work']['M_second']; is_final=(phase=='M256_TARGETED' if node==1162 else phase=='M128')
            revision=source_revision_for(data['source_lock_sha256'])
            check('run_source_identity',complete['source_lock_sha256']==start['source_lock_sha256']==data['source_lock_sha256'],label)
            check('result_and_comparison_hashes',sha(directory/'RESULT.json')==complete['result_sha256'] and sha(directory/'COMPARISON.json')==complete['comparison_sha256'],label)
            scientific={k:v for k,v in data.items() if k not in ('elapsed_seconds','peak_RSS_KiB','finished_utc')}; scientific['track']={k:v for k,v in data['track'].items() if k!='elapsed_seconds'}
            check('numerical_semantic_identity',hashlib.sha256(b'bass-he-e13c9-path-v1\n'+canonical(scientific)).hexdigest()==complete['semantic_sha256'],label)
            check('run_work_identity',data['work']==complete['work']==start['work'] and data['work']['node']==node and data['work']['mode']=='OFF' and data['work']['precision']==60 and data['work']['N_base']==baseline['work']['N'],label)
            check('no_forbidden_scientific_replays',data['baseline_firstvariation_quadrature_replays']==0 and all(v==0 for v in data['forbidden_invocations'].values()),label)
            check('new_coefficient_count',data['new_coefficient_evaluations']==2*M*len(controls)==complete['new_coefficient_evaluations'],label)
            check('actual_local_limits',0<data['elapsed_seconds']<plan['per_path_wall_seconds'] and data['peak_RSS_KiB']*1024<plan['per_process_address_space_bytes'],label)
            check('no_intersection_or_fallback',comp['intersection_used'] is False and comp['old_interval_fallback_used'] is False,label)
            nm=metrics(data['track'],weight); rows=compare(bm,nm)
            check('all_34_exact_metric_parity',len(rows)==34 and rows==comp['comparisons'],label)
            for kind in bm:
                for key in bm[kind]:
                    check('saved_weighted_metric_parity',bm[kind][key]==box(comp['baseline_raw_weighted'][kind][key]) and nm[kind][key]==box(comp['candidate_raw_weighted'][kind][key]),label+'/'+kind+'/'+key)
            failures=[r for r in rows if not(r['nested'] and r['width_nonincreasing'])]
            check('reported_mechanical_counts',sum(r['nested'] for r in rows)==comp['nested_count']==complete['nested_count'] and sum(r['width_nonincreasing'] for r in rows)==comp['nonincreasing_count']==complete['nonincreasing_count'],label)
            record={'node':node,'phase':phase,'M_second':M,'selected_final':is_final,'source_revision':revision,'result':pin(directory/'RESULT.json'),'comparison':pin(directory/'COMPARISON.json'),'complete':pin(directory/'COMPLETE.json'),'semantic_sha256':complete['semantic_sha256'],'metric_count':len(rows),'nested_count':sum(r['nested'] for r in rows),'nonincreasing_count':sum(r['width_nonincreasing'] for r in rows),'mechanical_failures':failures,'elapsed_seconds':data['elapsed_seconds'],'peak_RSS_KiB':data['peak_RSS_KiB'],'new_coefficient_evaluations':data['new_coefficient_evaluations']}
            records.append(record)
            if phase=='M128':
                for k in aggregate_m128:
                    aggregate_m128[k]+=width(nm['absolute'][k])
            if is_final:
                all_boxes(data,label)
                check_track(data['track'],baseline['track'],controls,M,label)
                final_rows += [{'node':node,**r} for r in rows]
                for k in aggregate_old:
                    aggregate_old[k]+=width(bm['absolute'][k]); aggregate_new[k]+=width(nm['absolute'][k])
    agg={}
    for k in aggregate_old:
        old,new,unif=aggregate_old[k],aggregate_new[k],aggregate_m128[k]
        gain=(old-new)/old; ug=(old-unif)/old
        agg[k]={'baseline_width_exact':str(old),'selected_width_exact':str(new),'baseline_width_display':display(old),'selected_width_display':display(new),'selected_gain_exact':str(gain),'selected_gain_display':display(gain),'uniform_M128_gain_exact':str(ug),'uniform_M128_gain_display':display(ug),'useful_gain_threshold':'1/10','selected_gain_at_least_10_percent':gain>=F(1,10),'uniform_M128_gain_at_least_10_percent':ug>=F(1,10)}
        check('predeclared_aggregate_useful_gain',gain>=F(1,10) and ug>=F(1,10),k)
    check('selected_all_170_raw_nested_nonincreasing',len(final_rows)==170 and all(r['nested'] and r['width_nonincreasing'] for r in final_rows),'selected')
    result={'schema':'bass-he-e13c9-independent-saved-arithmetic-review-v1','role':'INDEPENDENT_FINAL_DECISION_REVIEWER_NOT_CANDIDATE_OR_CONTROL_AUTHOR','status':'PASS_SAVED_ARITHMETIC' if not FAILURES else 'REWORK_SAVED_ARITHMETIC_FINDINGS','started_utc':startedutc,'finished_utc':datetime.now(timezone.utc).isoformat(),'elapsed_seconds':time.perf_counter()-started,'reviewer_source':pin(__file__),'candidate_source_lock':pin(ROOT/'SOURCE_LOCK.json'),'baseline_results':originalpins,'check_counts':dict(COUNTS),'check_total':sum(COUNTS.values()),'failures':FAILURES,'reviewed_saved_runs':records,'selected_comparisons':final_rows,'selected_aggregate':agg,'execution_scope':{'candidate_method_imports':0,'coefficient_evaluations':0,'path_integrations':0,'old_baseline_replays':0,'full_population_runs':0,'NCP_launches':0,'read_only_Context_input_validation_paths':5},'limitations':['Saved-algebra checks do not independently recalculate coefficient functions, Jet2 derivatives, midpoint forcing values or signed rectangle kernels. These require source proof and separate manufactured controls.','Independent 100-digit Decimal exp enclosure shares the Python Decimal transcendental contract, but no candidate interval or prefix implementation is called.','Final numerical/scientific decision remains pending separate manufactured controls and direct critical source review.','Uniform M128 failure remains preserved; final selection is four M128 paths plus targeted M256 node 1162.','Physical, continuum, production, receiver and new full-population correction claims remain HOLD / NOT_RUN.']}
    OUT.parent.mkdir(parents=True,exist_ok=True)
    with OUT.open('x') as f:
        json.dump(result,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
    print(json.dumps({'status':result['status'],'checks':result['check_total'],'failures':len(FAILURES),'elapsed_seconds':result['elapsed_seconds'],'selected_aggregate':agg},sort_keys=True))
    if FAILURES:
        print(json.dumps(FAILURES,indent=2))
        return 2
    return 0

if __name__=='__main__':
    raise SystemExit(main())
