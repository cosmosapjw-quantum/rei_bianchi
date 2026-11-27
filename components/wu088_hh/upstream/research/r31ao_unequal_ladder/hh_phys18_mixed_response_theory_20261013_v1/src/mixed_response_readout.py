#!/usr/bin/env python3
"""Finite mixed-response implications and common-inverse grouped readout.

Postprocess only the stored PHYS18 mixed enclosure. Each attributed group uses
one and the same Full inverse and temperature row. No roots or source callbacks.
"""
import argparse,hashlib,importlib.util,json,pathlib,resource,sys,time
from fractions import Fraction as Q

def main(p15,result,output):
    tic=time.perf_counter()
    helper=p15/'inputs/phys14/src/phys14_advance.py'
    assert hashlib.sha256(helper.read_bytes()).hexdigest()=='d20d9797278b8da71d38a3db229325dc7792d3991863f07bcdb7f72f2ba5567a'
    assert hashlib.sha256(result.read_bytes()).hexdigest()=='69cb5d38bae33fb15b9533895e15022acc992f7a893903d17615bde8563ab889'
    spec=importlib.util.spec_from_file_location('p14_interval',helper);old=importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode=True;spec.loader.exec_module(old)
    I,raw,dot,mv=old.I,old.from_raw,old.dot,old.matvec
    r=json.loads(result.read_text())
    C=[[raw(z) for z in row] for row in r['fixed_transfer']['C']]
    B=[[raw(z).hi for z in row] for row in r['fixed_transfer']['B']]
    EJ=[[raw(z) for z in row] for row in r['fixed_transfer']['I_CJF']]
    row=[raw(z) for z in r['fixed_endpoint']['common_goal_row']]
    def transfer(rhs):
        cr=mv(C,rhs)
        mat=[[Q(i==j)-B[i][j] for j in range(4)]+[cr[i].mag()] for i in range(4)]
        for j in range(4):
            k=next(k for k in range(j,4) if mat[k][j]);mat[j],mat[k]=mat[k],mat[j]
            factor=mat[j][j];mat[j]=[x/factor for x in mat[j]]
            for k in range(4):
                if k!=j:
                    factor=mat[k][j];mat[k]=[x-factor*y for x,y in zip(mat[k],mat[j])]
        mag=[v[-1] for v in mat]
        rem=[sum(B[i][j]*mag[j] for j in range(4)) for i in range(4)]
        val=[z+I(-e,e) for z,e in zip(cr,rem)]
        for _ in range(3):val=[v.meet(cr[i]+dot(EJ[i],val)) for i,v in enumerate(val)]
        return val
    parts={**r['mixed_residual_sectors'],**r['endpoint_correction_sectors']}
    groups={
        'HH_gradient_terms':['HH_gradient_time','HH_gradient_birth_increment','HH_gradient_movement',
                             'endpoint_HH_gradient_difference','endpoint_HH_birth_defect'],
        'photon_seven_sectors':list(r['photon_jets'])}
    used=set(sum(groups.values(),[]));groups['remaining_gas_and_endpoint_terms']=[n for n in parts if n not in used]
    assert len(set(sum(groups.values(),[])))==len(parts)==len(sum(groups.values(),[]))
    grouped={}
    for name,names in groups.items():
        rhs=[sum((raw(parts[n][i]) for n in names),I(0)) for i in range(4)]
        derivative=transfer(rhs)
        grouped[name]={'sector_names':names,'combined_rhs':rhs,'d_mixed':derivative,'temperature_K':dot(row,derivative)}
    F=raw(r['DeltaT_mixed_intersection_K']);orig=raw(r['DeltaT_mixed_original_subtraction_K']);direct=raw(r['DeltaT_mixed_direct_K'])
    prior=raw(r['interaction_previous_magnitude_bound_K'])
    geom=raw(r['temperature_geometry_K'])
    result0={
        'schema':'WU088_HH_PHYS18_FINITE_MIXED_READOUT_V1','status':'CANDIDATE_COMPUTED',
        'input_identities':[{'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in (helper,result)],
        'parameter_domain':'lambda,b in [0,1], shared global parameters and same fixed alpha',
        'DeltaT_lambdab_K':F,'four_corner_interaction_K':raw(r['four_corner_interaction_K']),
        'strict_negative_margin_K':I(-F.hi),
        'subrectangle_identity':'C([l0,l1],[b0,b1])=integral_l0^l1 integral_b0^b1 F_lambdab db dlambda',
        'subrectangle_enclosure':'area * DeltaT_lambdab_K, area=(l1-l0)*(b1-b0)>=0',
        'mixed_mean_per_unit_area_K':F,
        'birth_change_of_lambda_response_K':F,
        'lambda_change_of_birth_response_K':F,
        'interpretation':{'lambda_response':'F_lambda becomes strictly more negative as b increases',
                          'birth_response':'F_b decreases as lambda increases while retaining the inherited positive sign',
                          'interaction':'strictly submodular temperature defect on every positive-area parameter rectangle'},
        'comparison':{'previous_reported_magnitude_bound_K':prior,
                      'magnitude_bound_improvement_factor':prior/I(F.mag()),
                      'original_subtraction_width_improvement_factor':I(orig.hi-orig.lo)/I(F.hi-F.lo),
                      'direct_mixed_implicit_width_improvement_factor':I(direct.hi-direct.lo)/I(F.hi-F.lo)},
        'grouped_attribution':grouped,'thermal_geometry_K':geom,
        'sum_of_group_enclosures_K':sum((v['temperature_K'] for v in grouped.values()),I(0))+geom,
        'actual_four_corner_root_evaluations':0,
        'finite_interaction_method':'uniform mixed derivative inclusion followed by exact rectangle integral identity',
        'source_calls':0,'root_solves':0,'history_replays':0,
        'elapsed_seconds':time.perf_counter()-tic,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    output.mkdir(parents=True,exist_ok=False)
    (output/'FINITE_MIXED_READOUT.json').write_text(json.dumps(old.out(result0),ensure_ascii=False,indent=2)+'\n')
    summary={k:old.short(result0[k]) for k in ('status','DeltaT_lambdab_K','four_corner_interaction_K','strict_negative_margin_K','comparison','thermal_geometry_K','sum_of_group_enclosures_K')}
    summary['grouped_attribution_K']={k:old.short(v['temperature_K']) for k,v in grouped.items()}
    summary['resources']={k:result0[k] for k in ('elapsed_seconds','peak_rss_kib')}
    (output/'SUMMARY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':
    a=argparse.ArgumentParser()
    for key in ('parent15','result','output'):a.add_argument('--'+key,type=pathlib.Path,required=True)
    p=a.parse_args();main(p.parent15.resolve(),p.result.resolve(),p.output.resolve())
