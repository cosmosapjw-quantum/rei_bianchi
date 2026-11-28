#!/usr/bin/env python3
"""Exact Fraction analysis of saved E13C10 evidence; no scientific imports."""
import argparse
import csv
from datetime import datetime, timezone
from decimal import Decimal, localcontext
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import time


def read(p): return json.loads(Path(p).read_bytes())
def sha(p):
    with Path(p).open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def box(x): return F(x['lo']),F(x['hi'])
def half(x): a,b=box(x);return (b-a)/2
def enc(x): return {'lo':str(x[0]),'hi':str(x[1])}
def display(x):
    with localcontext() as c:
        c.prec=24
        return str(Decimal(x.numerator)/Decimal(x.denominator))
def metrics(x): return {kind:{q:box(v) for q,v in row.items()} for kind,row in x.items()}
def total(seq):
    return {kind:{q:tuple(sum(x[kind][q][i] for x in seq) for i in (0,1)) for q in seq[0][kind]} for kind in seq[0]}
def compare(a,b):
    rows=[]
    for kind in sorted(a):
        for q in sorted(a[kind]):
            x,y=a[kind][q],b[kind][q];wa=x[1]-x[0];wb=y[1]-y[0]
            rows.append({'kind':kind,'quantity':q,'baseline':enc(x),'candidate':enc(y),
                'overlap':max(x[0],y[0])<=min(x[1],y[1]),'nested':x[0]<=y[0]<=y[1]<=x[1],
                'nonincreasing':wb<=wa,'baseline_width':str(wa),'candidate_width':str(wb),
                'baseline_width_display':display(wa),'candidate_width_display':display(wb),
                'gain_fraction':str((wa-wb)/wa) if wa else None,
                'gain_percent_display':display(100*(wa-wb)/wa) if wa else None})
    return rows


CATEGORIES=('first_curvature_range','first_midpoint_rounding','signed_rectangle','finite_volterra_tail','other_rounding')
def zero():return {k:F(0) for k in CATEGORIES}
def add(a,b):return {k:a[k]+b[k] for k in CATEGORIES}


def allocation(track,weight,absolute):
    incoming=zero();heat={sp:zero() for sp in ('HI','HeI','HeII')}
    for j,s in enumerate(track['segments']):
        if sum(incoming.values())!=F(s['incoming']['radius']):raise ArithmeticError('incoming allocation mismatch')
        outputs={}
        for q in ['P1']+['H_'+sp+'_eV' for sp in heat]:
            gl,gh=box(s['gains'][q]);factor=max(abs(gl),abs(gh))+F(s['remainder']['T_upper'][q])
            parts={k:factor*v for k,v in incoming.items()}
            parts['first_curvature_range']+=half(s['local']['curvature_correction'][q])
            parts['first_midpoint_rounding']+=half(s['local']['midpoint'][q])
            parts['signed_rectangle']+=half(s['second_correction']['signed'][q])
            parts['finite_volterra_tail']+=F(s['remainder']['second_volterra_remainder_upper'][q])
            extra=F(s['outputs'][q]['radius'])-sum(parts.values())
            if extra<0:raise ArithmeticError('negative direct allocation remainder')
            parts['other_rounding']+=extra;outputs[q]=parts
        for sp in heat:
            q='H_'+sp+'_eV';heat[sp]=add(heat[sp],outputs[q])
            extra=F(s['cumulative_moment_corrections'][q]['radius'])-sum(heat[sp].values())
            if extra<0:raise ArithmeticError('negative accumulated allocation remainder')
            heat[sp]['other_rounding']+=extra
        incoming=outputs['P1']
        if j<len(track['seams']):
            extra=F(track['seams'][j]['next_incoming']['radius'])-sum(incoming.values())
            if extra<0:raise ArithmeticError('negative seam allocation remainder')
            incoming['other_rounding']+=extra
    P={k:v*weight for k,v in outputs['P1'].items()}
    H={k:sum(v[k] for v in heat.values())*weight for k in CATEGORIES}
    answer={}
    for q,parts in [('P_final',P),('H_total_eV',H)]:
        hw=(absolute[q][1]-absolute[q][0])/2;extra=hw-sum(parts.values())
        if extra<0:raise ArithmeticError('negative final allocation remainder')
        parts['other_rounding']+=extra
        answer[q]={'halfwidth':str(hw),'components':{k:str(v) for k,v in parts.items()},
            'percent':{k:display(100*v/hw) if hw else None for k,v in parts.items()},
            'exact_reconstruction':sum(parts.values())==hw}
    return answer


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument('--restored-e13c9',type=Path,required=True)
    ap.add_argument('--output-dir',type=Path,required=True)
    args=ap.parse_args();started=time.perf_counter();root=args.package.resolve();out=args.output_dir.resolve();out.mkdir(parents=True,exist_ok=False)
    source=read(root/'evidence/SELECTED_INPUTS.json');rows=[];baselines=[];candidates=[];allocations=[];selected=[];same_grid=[]
    input_root=args.restored_e13c9.resolve()/'runtime/E13C8/runtime/E13C7_INPUT/BASS_HE_E13C7_PARALLEL_FINITE_REFINEMENT_20261011_v1'
    weights={}
    with (input_root/'inputs/source/OFF_SEGMENTS.csv').open() as f:
        for row in csv.DictReader(f):
            if int(row['step'])==1:weights[int(row['node'])]=F.from_float(float(row['weight']))
    for rec in source['selected_paths']:
        node=rec['node'];directory=root/'runs/REFINED'/f'node_{node:06d}'
        comp,result,complete=[read(directory/n) for n in ('COMPARISON.json','RESULT.json','COMPLETE.json')]
        if sha(directory/'RESULT.json')!=complete['result_sha256'] or sha(directory/'COMPARISON.json')!=complete['comparison_sha256']:raise ValueError('saved path byte identity mismatch')
        old,new=metrics(comp['baseline_raw_weighted']),metrics(comp['candidate_raw_weighted'])
        comparison=compare(old,new);baselines.append(old);candidates.append(new)
        rows.append({'node':node,'selection_reason':rec['selection_reason'],'work':result['work'],
            'comparison_rows':comparison,'nested_count':sum(x['nested'] for x in comparison),
            'nonincreasing_count':sum(x['nonincreasing'] for x in comparison),
            'P_H_summary':{q:next(x for x in comparison if x['kind']=='absolute' and x['quantity']==q) for q in ('P_final','H_total_eV')},
            'elapsed_seconds':result['elapsed_seconds'],'cpu_seconds':result['cpu_seconds'],'peak_RSS_KiB':result['peak_RSS_KiB']})
        allocations.append({'node':node,'quantities':allocation(result['track'],weights[node],new['absolute'])})
        for s in result['track']['segments']:
            for q,v in s['local']['signed'].items():
                x=box(s['local']['same_new_grid_symmetric_diagnostic'][q]);y=box(v)
                same_grid.append({'node':node,'key':s['key'],'quantity':q,'nested':x[0]<=y[0]<=y[1]<=x[1],
                    'nonincreasing':y[1]-y[0]<=x[1]-x[0]})
        selected.append({'node':node,'work':result['work'],'result':{'relative_path':str((directory/'RESULT.json').relative_to(root)),
            'bytes':(directory/'RESULT.json').stat().st_size,'sha256':complete['result_sha256']},
            'comparison':{'relative_path':str((directory/'COMPARISON.json').relative_to(root)),'sha256':complete['comparison_sha256']},
            'semantic_sha256':complete['semantic_sha256'],'source_lock_sha256':result['source_lock_sha256'],'path_input_sha256':result['path_input_sha256']})
    aggregate=compare(total(baselines),total(candidates))
    ph={q:next(x for x in aggregate if x['kind']=='absolute' and x['quantity']==q) for q in ('P_final','H_total_eV')}
    useful=all(F(x['gain_fraction'])>=F(1,2) for x in ph.values())
    convergence=[]
    for node in (1,1976):
        coarse=root/'runs/N32'/f'node_{node:06d}'
        fine=root/'runs/REFINED'/f'node_{node:06d}'
        c32=read(coarse/'COMPARISON.json');cfine=read(fine/'COMPARISON.json')
        convergence.append({'node':node,'coarse_N':32,'fine_N':1024,
            'comparison_rows':compare(metrics(c32['candidate_raw_weighted']),metrics(cfine['candidate_raw_weighted'])),
            'interpretation':'Observed raw resolution comparison; not a universal convergence-order claim.'})
    all_runs=[read(p) for p in sorted((root/'runs').glob('*/node_*/COMPLETE.json'))]
    resources={'completed_path_invocations_including_diagnostics':len(all_runs),
        'new_first_integral_coefficient_evaluations':sum(x['new_first_integral_coefficient_evaluations'] for x in all_runs),
        'second_correction_coefficient_evaluations_during_new_path_assembly':sum(x['new_second_correction_coefficient_evaluations'] for x in all_runs),
        'total_coefficient_evaluations':sum(x['new_coefficient_evaluations'] for x in all_runs),
        'sum_per_path_elapsed_seconds_not_wall':sum(x['elapsed_seconds'] for x in all_runs),
        'sum_per_path_process_cpu_seconds':sum(x['cpu_seconds'] for x in all_runs),
        'max_per_path_elapsed_seconds':max(x['elapsed_seconds'] for x in all_runs),
        'peak_individual_process_RSS_KiB':max(x['peak_RSS_KiB'] for x in all_runs),
        'prior_complete_path_work_units_replayed':0,'old_firstvariation_quadrature_replays':0,
        'NCP_launches':0,'E13C10_full_population':'NOT_RUN','same_work_speedup':'NOT_ESTABLISHED',
        'CPU_utilization':'NOT_MEASURED','provider_attestation':'NOT_ASSERTED',
        'note':'Second-correction functions are recomputed with the current new path carry. Subcalculations whose incoming center stayed identical can repeat deterministic old arithmetic.'}
    component_totals={}
    for q in ('P_final','H_total_eV'):
        hw=sum(F(x['quantities'][q]['halfwidth']) for x in allocations)
        parts={k:sum(F(x['quantities'][q]['components'][k]) for x in allocations) for k in CATEGORIES}
        component_totals[q]={'halfwidth':str(hw),'components':{k:str(v) for k,v in parts.items()},
            'percent':{k:display(100*v/hw) for k,v in parts.items()},'exact_reconstruction':sum(parts.values())==hw}
    result={'schema':'bass-he-e13c10-local-analysis-v1','status':'PENDING_INDEPENDENT_DECISION',
        'date_utc':datetime.now(timezone.utc).isoformat(),'selected_paths':rows,'selected_path_count':len(rows),
        'selected_segment_count':source['selected_segment_count'],'nested_count':sum(x['nested_count'] for x in rows),
        'nonincreasing_count':sum(x['nonincreasing_count'] for x in rows),'required_count':34*len(rows),
        'selected_aggregate_P_H_at_least_50_percent':useful,'selected_aggregate_summary':ph,
        'aggregate_comparisons':aggregate,'same_new_grid_signed_vs_symmetric':same_grid,
        'resolution_discriminators_preserved_N32_to_same_original_N':convergence,
        'selected_bound_halfwidth_allocation':component_totals,'resources':resources,
        'prior_admissions_changed':False,'raw_intersections':0,'old_interval_fallbacks':0,
        'physical_continuum_production_receiver':'HOLD',
        'interpretation':'Finite interval widths and positive bound allocation, not measured true error or a full-population result.',
        'elapsed_seconds':time.perf_counter()-started}
    result['mechanical_acceptance']=result['nested_count']==result['required_count'] and result['nonincreasing_count']==result['required_count'] and useful
    def save(name,obj):
        with (out/name).open('x') as f:json.dump(obj,f,indent=2,sort_keys=True);f.write('\n')
    save('LOCAL_ANALYSIS.json',result)
    save('BOUND_ALLOCATION.json',{'paths':allocations,'selected_totals':component_totals,'definition':'Exact nonnegative halfwidth decomposition with propagated carry; bounds, not observed errors.'})
    save('SELECTED_CANDIDATE.json',{'schema':'bass-he-e13c10-selected-candidate-v1','status':'PENDING_INDEPENDENT_DECISION','paths':selected,
        'analysis_sha256':sha(out/'LOCAL_ANALYSIS.json'),'raw_intersections':0,'old_interval_fallbacks':0})
    save('EXECUTION_RECEIPT.json',{'code_sha256':sha(Path(__file__)),'analysis_sha256':sha(out/'LOCAL_ANALYSIS.json'),
        'elapsed_seconds':time.perf_counter()-started,'scientific_kernel_invocations':0,'mechanical_acceptance':result['mechanical_acceptance']})
    print(json.dumps({'mechanical_acceptance':result['mechanical_acceptance'],'nested':result['nested_count'],
        'gain_percent':{q:x['gain_percent_display'] for q,x in ph.items()},'resources':resources,
        'bound_allocation_percent':{q:x['percent'] for q,x in component_totals.items()},
        'same_new_grid_nested':sum(x['nested'] for x in same_grid),'same_new_grid_count':len(same_grid)},indent=2))


if __name__=='__main__':main()
