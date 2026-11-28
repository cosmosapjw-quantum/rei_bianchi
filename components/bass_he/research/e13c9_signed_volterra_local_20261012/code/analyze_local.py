#!/usr/bin/env python3
"""Exact saved-output analysis of the E13C9 local method; no kernel import."""
import argparse
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time


def read(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def box(x): return F(x['lo']),F(x['hi'])
def half(x): a,b=box(x);return (b-a)/2
def width(x): a,b=box(x);return b-a
def enc(x): return {'lo':str(x[0]),'hi':str(x[1])}
def display(x):
    with localcontext() as c:
        c.prec=24
        return str(Decimal(x.numerator)/Decimal(x.denominator))
def metric(x): return {k:{q:box(v) for q,v in row.items()} for k,row in x.items()}
def total(seq):
    return {kind:{k:tuple(sum(x[kind][k][i] for x in seq) for i in (0,1)) for k in seq[0][kind]} for kind in seq[0]}
def comparisons(a,b):
    rows=[]
    for kind in sorted(a):
        for q in sorted(a[kind]):
            x,y=a[kind][q],b[kind][q];wa=x[1]-x[0];wb=y[1]-y[0]
            rows.append({'kind':kind,'quantity':q,'baseline':enc(x),'candidate':enc(y),
                'overlap':max(x[0],y[0])<=min(x[1],y[1]),
                'nested':x[0]<=y[0]<=y[1]<=x[1],'nonincreasing':wb<=wa,
                'baseline_width':str(wa),'candidate_width':str(wb),
                'baseline_width_display':display(wa),'candidate_width_display':display(wb),
                'gain_fraction':str((wa-wb)/wa) if wa else None,
                'gain_percent_display':display(100*(wa-wb)/wa) if wa else None})
    return rows


CATEGORIES=('first_midpoint','new_signed_rectangle','finite_volterra_tail','other_numerical_rounding')
def zero(): return {k:F(0) for k in CATEGORIES}
def add(a,b): return {k:a[k]+b[k] for k in CATEGORIES}


def allocation(track,weight,absolute):
    """Positive bound allocation, not actual error; include all carry factors."""
    incoming=zero(); heat={sp:zero() for sp in ('HI','HeI','HeII')}
    for j,s in enumerate(track['segments']):
        eta=F(s['incoming']['radius'])
        if sum(incoming.values())!=eta: raise ArithmeticError('incoming decomposition mismatch')
        out={}
        for q in ['P1']+['H_'+sp+'_eV' for sp in heat]:
            gl,gh=box(s['gains'][q]);factor=max(abs(gl),abs(gh))+F(s['remainder']['T_upper'][q])
            part={k:factor*v for k,v in incoming.items()}
            part['first_midpoint']+=F(s['local']['midpoint_radius'][q])
            part['new_signed_rectangle']+=half(s['second_correction']['signed'][q])
            part['finite_volterra_tail']+=F(s['remainder']['second_volterra_remainder_upper'][q])
            excess=F(s['outputs'][q]['radius'])-sum(part.values())
            if excess<0: raise ArithmeticError('negative direct rounding allocation')
            part['other_numerical_rounding']+=excess
            out[q]=part
        for sp in heat:
            q='H_'+sp+'_eV';heat[sp]=add(heat[sp],out[q])
            extra=F(s['cumulative_moment_corrections'][q]['radius'])-sum(heat[sp].values())
            if extra<0:raise ArithmeticError('negative accumulated rounding allocation')
            heat[sp]['other_numerical_rounding']+=extra
        incoming=out['P1']
        if j<len(track['seams']):
            extra=F(track['seams'][j]['next_incoming']['radius'])-sum(incoming.values())
            if extra<0:raise ArithmeticError('negative seam rounding allocation')
            incoming['other_numerical_rounding']+=extra
    P={k:v*weight for k,v in out['P1'].items()}
    H={k:sum(v[k] for v in heat.values())*weight for k in CATEGORIES}
    answer={}
    for name,parts in [('P_final',P),('H_total_eV',H)]:
        exact_half=(absolute[name][1]-absolute[name][0])/2
        extra=exact_half-sum(parts.values())
        if extra<0:raise ArithmeticError('negative final absolute rounding allocation')
        parts['other_numerical_rounding']+=extra
        answer[name]={'halfwidth':str(exact_half),'components':{k:str(v) for k,v in parts.items()},
            'percent':{k:display(100*v/exact_half) if exact_half else None for k,v in parts.items()},
            'exact_reconstruction':sum(parts.values())==exact_half}
    return answer


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--output-dir',type=Path,required=True)
    ap.add_argument('--restored-e13c8',type=Path,required=True)
    a=ap.parse_args();start=time.perf_counter();root=a.package.resolve();out=a.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    source=read(root/'evidence/SELECTED_PATHS.json')
    nodes=source['selected_nodes'];baselines=[]; levels={'M32':[],'M128':[],'SELECTED':[]};path_rows=[];selected_files=[];allocations=[]
    for rec in source['selected_paths']:
        node=rec['node']
        # The exact weight is preserved in the original captured input metadata.
        from_restore=a.restored_e13c8.resolve()/'runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1'
        import csv
        with (from_restore/'inputs/source/OFF_SEGMENTS.csv').open() as f:
            row=next(x for x in csv.DictReader(f) if int(x['node'])==node and int(x['step'])==1)
        weight=F.from_float(float(row['weight']))
        paths={'M32':root/'runs/M32_REPAIRED'/f'node_{node:06d}',
            'M128':root/'runs/M128'/f'node_{node:06d}',
            'SELECTED':root/('runs/M256_TARGETED' if node==1162 else 'runs/M128')/f'node_{node:06d}'}
        records={}
        for level,directory in paths.items():
            comp,result,complete=[read(directory/n) for n in ('COMPARISON.json','RESULT.json','COMPLETE.json')]
            if sha(directory/'RESULT.json')!=complete['result_sha256'] or sha(directory/'COMPARISON.json')!=complete['comparison_sha256']:raise ValueError('actual result identity mismatch')
            base,new=metric(comp['baseline_raw_weighted']),metric(comp['candidate_raw_weighted'])
            rows=comparisons(base,new)
            if not all(r['overlap'] for r in rows):raise ArithmeticError('saved nonoverlap')
            if level=='M32':baselines.append(base)
            levels[level].append(new)
            records[level]={'work':result['work'],'relative_result':str((directory/'RESULT.json').relative_to(root)),
                'result_sha256':complete['result_sha256'],'source_lock_sha256':result['source_lock_sha256'],
                'comparison_rows':rows,'nested_count':sum(r['nested'] for r in rows),
                'nonincreasing_count':sum(r['nonincreasing'] for r in rows),
                'elapsed_seconds':result['elapsed_seconds'],'peak_RSS_KiB':result['peak_RSS_KiB']}
            if level=='SELECTED':
                allocations.append({'node':node,'quantities':allocation(result['track'],weight,new['absolute'])})
                selected_files.append({'node':node,'M_second':result['work']['M_second'],
                    'N_base':result['work']['N_base'],'precision':60,
                    'result':{'relative_path':str((directory/'RESULT.json').relative_to(root)),'bytes':(directory/'RESULT.json').stat().st_size,'sha256':complete['result_sha256']},
                    'comparison':{'relative_path':str((directory/'COMPARISON.json').relative_to(root)),'sha256':complete['comparison_sha256']},
                    'semantic_sha256':complete['semantic_sha256'],'source_lock_sha256':result['source_lock_sha256'],
                    'path_input_sha256':result['path_input_sha256']})
        path_rows.append({'node':node,'selection_reason':rec['selection_reason'],'active_species_class':rec['active_species_class'],'levels':records})
    baseline=total(baselines);sums={k:comparisons(baseline,total(v)) for k,v in levels.items()}
    selected_summary={q:next(r for r in sums['SELECTED'] if r['kind']=='absolute' and r['quantity']==q) for q in ('P_final','H_total_eV')}
    useful=all(F(r['gain_fraction'])>=F(1,10) for r in selected_summary.values())
    all_runs=[read(p) for p in sorted((root/'runs').glob('*/node_*/COMPLETE.json'))]
    resources={'completed_path_invocations_including_preserved_diagnostics':len(all_runs),
        'new_coefficient_evaluations_including_preserved_diagnostics':sum(x['new_coefficient_evaluations'] for x in all_runs),
        'sum_reported_per_path_elapsed_seconds_not_wall_or_CPU_time':sum(x['elapsed_seconds'] for x in all_runs),
        'max_reported_per_path_seconds':max(x['elapsed_seconds'] for x in all_runs),
        'peak_individual_process_RSS_KiB':max(x['peak_RSS_KiB'] for x in all_runs),
        'baseline_firstvariation_quadrature_replays':sum(x['baseline_firstvariation_quadrature_replays'] for x in all_runs),
        'NCP_launches':0,'full_population_second_correction':'NOT_RUN',
        'serial_same_work_speedup':'NOT_ESTABLISHED','CPU_utilization':'NOT_MEASURED','provider_attestation':'NOT_ASSERTED'}
    component_totals={}
    for q in ('P_final','H_total_eV'):
        halfwidth=sum(F(x['quantities'][q]['halfwidth']) for x in allocations)
        comp={k:sum(F(x['quantities'][q]['components'][k]) for x in allocations) for k in CATEGORIES}
        component_totals[q]={'halfwidth':str(halfwidth),'components':{k:str(v) for k,v in comp.items()},'percent':{k:display(100*v/halfwidth) for k,v in comp.items()},'exact_reconstruction':sum(comp.values())==halfwidth}
    result={'schema':'bass-he-e13c9-local-saved-analysis-v1','status':'PASS_MECHANICAL_PENDING_INDEPENDENT_ADMISSION',
        'date_utc':datetime.now(timezone.utc).isoformat(),'selected_nodes':nodes,'selected_segments':source['selected_segment_count'],
        'uniform_M32_nested_count':sum(x['levels']['M32']['nested_count'] for x in path_rows),
        'uniform_M128_nested_count':sum(x['levels']['M128']['nested_count'] for x in path_rows),
        'selected_mixed_resolution_nested_count':sum(x['levels']['SELECTED']['nested_count'] for x in path_rows),
        'selected_mixed_resolution_nonincreasing_count':sum(x['levels']['SELECTED']['nonincreasing_count'] for x in path_rows),
        'required_count':34*len(nodes),'selected_aggregate_P_H_at_least_10_percent':useful,
        'selected_aggregate_summary':selected_summary,'aggregate_comparisons':sums,'paths':path_rows,
        'selected_bound_halfwidth_allocation':component_totals,'resources':resources,
        'E13C8_full_finite_admission_changed':False,'physical_continuum_production_receiver':'HOLD',
        'interpretation':'Selected finite enclosure width and positive bound allocation; not measured true error or a full-population result.',
        'elapsed_seconds':time.perf_counter()-start}
    if result['selected_mixed_resolution_nested_count']!=34*len(nodes) or not useful:raise ArithmeticError('declared selected local acceptance not met')
    def save(name,x):
        with (out/name).open('x') as f:json.dump(x,f,indent=2,sort_keys=True);f.write('\n')
    save('LOCAL_ANALYSIS.json',result)
    save('BOUND_ALLOCATION.json',{'paths':allocations,'selected_totals':component_totals,'definition':'Exact nonnegative bound allocation with propagated (abs(G)+T) incoming categories, direct cached midpoint, new rectangle halfwidth, finite TDS tail, and outward residual. Not actual error.'})
    save('SELECTED_CANDIDATE.json',{'schema':'bass-he-e13c9-selected-local-candidate-v1','status':'PENDING_INDEPENDENT_DECISION','paths':selected_files,'analysis_sha256':sha(out/'LOCAL_ANALYSIS.json'),'raw_intersections':0,'old_interval_fallbacks':0})
    save('EXECUTION_RECEIPT.json',{'analysis_sha256':sha(out/'LOCAL_ANALYSIS.json'),'code_sha256':sha(Path(__file__)),'elapsed_seconds':time.perf_counter()-start,'scientific_kernel_invocations':0,'basis':'Actual saved local numerical outputs only'})
    print(json.dumps({'status':result['status'],'selected_nested':result['selected_mixed_resolution_nested_count'],'gain_percent':{k:v['gain_percent_display'] for k,v in selected_summary.items()},'resources':resources,'allocation':component_totals},indent=2))


if __name__=='__main__':main()
