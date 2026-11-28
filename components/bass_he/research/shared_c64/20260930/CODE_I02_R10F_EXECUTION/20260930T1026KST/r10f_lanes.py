"""R10F fixed GK15/GK7 five-lane replay on the exact boundary union."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from arseny_reimpl.cross_section import projectile_velocity_au
from arseny_reimpl.eq50_scoped import branch_state_indices
from bass_he.eq54 import BRANCHES, DIM, INITIAL_INDEX_ZERO_BASED
from bass_he.geometry import _gk15_reduce, atomic_json
from bass_he.transport import apply_eq50
from scripts.r10a_rho_freeze import _shell_summary
import r10e_lanes
from r10f_runner import HERE, R10C, plan_queries, validate_fixed_gk

LANES=r10e_lanes.LANES


def input_probabilities_union(table,nodes,energies,frozen):
    exact={(row['branch'],row['rho_hex']):float.fromhex(row['delta_hex']) for row in table['rows']}
    delta0={row['branch']:float.fromhex(row['delta0_hex']) for row in frozen['records']}
    expected={(row['branch'],row['rho_hex']) for row in plan_queries()['rows']}
    if len(exact)!=1035 or set(exact)!=expected or len(delta0)!=5:
        raise ValueError('R10F_EXACT_OR_FROZEN_TABLE_INCOMPLETE')
    E=np.asarray(energies,float);rho=np.asarray(nodes,float)
    if E.shape!=(2,) or rho.shape!=(255,) or np.any(E<=0) or np.any(rho<=0):
        raise ValueError('R10F_INPUT_SHAPE_MISMATCH')
    v=np.array([projectile_velocity_au(float(e)) for e in E])
    dynamic=np.zeros((len(rho),len(E),len(BRANCHES)))
    static=np.zeros_like(dynamic)
    for i,r in enumerate(rho):
        for k,b in enumerate(BRANCHES):
            if r<=b.support_cutoff:
                d=exact[(b.name,float(r).hex())]
                d0=delta0[b.name]
                if not math.isfinite(d) or not math.isfinite(d0) or d<0 or d0<0:
                    raise ValueError('R10F_NONFINITE_OR_NEGATIVE_DELTA')
                dynamic[i,:,k]=np.exp(-2*d/v)
                static[i,:,k]=np.exp(-2*d0/v)
    return dynamic.reshape(-1,len(BRANCHES)),static.reshape(-1,len(BRANCHES))


def classify_baseline_rows(rows):
    rule_path=HERE/'BASELINE_REGRESSION_RULE_PRECOMMITTED.json'
    rule=json.loads(rule_path.read_text())
    rel_limit=rule['stop_if_any_indexed_or_Z2_shell']['relative_difference_strictly_gt']
    error_factor=rule['stop_if_any_indexed_or_Z2_shell']['absolute_difference_strictly_gt_factor_times_sum_embedded_estimates']
    flagged=[]
    for i,row in enumerate(rows):
        before=float(row['r10c_value']);now=float(row['r10f_value'])
        difference=float(row['absolute_difference'])
        old_err=float(row['r10c_embedded_estimate']);new_err=float(row['r10f_embedded_estimate'])
        if not all(math.isfinite(x) for x in (before,now,difference,old_err,new_err)) or old_err<0 or new_err<0:
            raise ValueError('nonfinite baseline comparison')
        if difference!=abs(now-before):
            raise ValueError('inconsistent baseline difference')
        material=(before==0 or difference/abs(before)>rel_limit) and difference>error_factor*(old_err+new_err)
        if material:flagged.append(i)
    return {'status':'R10F_BASELINE_REGRESSION_UNRESOLVED' if flagged else 'PASS',
            'material_row_indices_zero_based':flagged,'rule':rule}


def run_fixed_gk():
    plan=plan_queries()
    path=HERE/'EXACT_NODE_TABLE.json'
    manifest=json.loads((HERE/'EXACT_NODE_TABLE_MANIFEST.json').read_text())
    if hashlib.sha256(path.read_bytes()).hexdigest()!=manifest['table_sha256']:
        raise ValueError('R10F_TABLE_HASH_MISMATCH')
    table=json.loads(path.read_text())
    if (table['status']!='COMPLETE_VALID_EXACT_NODE_TABLE' or len(table['rows'])!=1035 or
        manifest['row_count']!=1035 or manifest['unique_rho_count']!=255 or
        table['ordered_pair_identity_sha256']!=plan['ordered_pair_identity_sha256'] or
        [(x['branch'],x['rho_hex']) for x in table['rows']]!=
        [(x['branch'],x['rho_hex']) for x in plan['rows']]):
        raise ValueError('R10F_TABLE_QUERY_IDENTITY_MISMATCH')
    frozen=json.loads((R10C/'FROZEN_DELTA0_RECORD.json').read_text())
    nodes=plan['nodes'];E=np.array((0.5,5.0))
    pair_e=np.tile(E,len(nodes));pair_r=np.repeat(nodes,len(E))
    rotation=r10e_lanes.rotation_matrices(pair_e,pair_r)
    dynamic,static=input_probabilities_union(table,nodes,E,frozen)
    events=[]
    for b in BRANCHES:
        i,j=branch_state_indices(b)
        events.append((i-1,j-1,b.state_b[0]==3))
    initial=np.eye(DIM)[:,[INITIAL_INDEX_ZERO_BASED]]
    probabilities={}
    for name in LANES:
        prot=rotation['COUL_AUTHOR'] if name=='COUL_AUTHOR_FROZEN' else rotation[name]
        p=static if name=='COUL_AUTHOR_FROZEN' else dynamic
        probabilities[name]=apply_eq50(p,events,prot,initial)[...,0].reshape(len(nodes),len(E),DIM)
    keep=np.arange(DIM)!=INITIAL_INDEX_ZERO_BASED
    vals=np.concatenate([probabilities[name][...,keep].reshape(len(nodes),-1) for name in LANES],axis=1)
    if vals.shape!=(255,90) or np.any(~np.isfinite(vals)):
        raise ValueError('R10F_INTEGRAND_SHAPE_OR_FINITE_FAILURE')
    defect=max(float(np.max(abs(p.sum(-1)-1.))) for p in probabilities.values())
    minimum=min(float(p.min()) for p in probabilities.values())
    if defect>3e-10 or minimum < -2e-13:
        raise ArithmeticError('R10F_TRANSPORT_STOCHASTICITY_FAILURE')
    cut=plan['cutpoints']
    intervals=[_gk15_reduce(a*a,b*b,vals[15*i:15*(i+1)])
               for i,(a,b) in enumerate(zip(cut[:-1],cut[1:]))]
    total=sum((x['high'] for x in intervals),np.zeros(90))
    err=sum((x['error'] for x in intervals),np.zeros(90))
    gate=validate_fixed_gk(total,err,evaluations=255,refinements=0)
    scores=np.array([x['error']/(1e-10+2e-4*np.abs(total)) for x in intervals])
    k,j=np.unravel_index(int(np.argmax(scores)),scores.shape)
    gate.update({'mandatory_intervals':17,'worst_interval_index_zero_based':int(k),
                 'worst_interval_cutpoint_hex':[float(cut[k]).hex(),float(cut[k+1]).hex()],
                 'worst_component_index_zero_based':int(j),
                 'worst_lane':LANES[j//18],'worst_energy_keV_u':(0.5,5.0)[(j%18)//9],
                 'worst_component_index_within_energy_zero_based':j%9,
                 'worst_interval_normalized_error':float(scores[k,j]),
                 'interval_component_error_estimate':[x['error'].tolist() for x in intervals],
                 'interval_component_high_estimate':[x['high'].tolist() for x in intervals],
                 'max_column_sum_defect':defect,'minimum_probability':minimum,
                 'error_claim':'EMBEDDED_NUMERICAL_ESTIMATE_NOT_INTERVAL_BOUND'})
    atomic_json(HERE/'FIXED_GK_DIAGNOSTIC.json',gate)
    if gate['status']!='PASS':
        return {'status':'R10F_BOUNDARY_SPLIT_GK_UNRESOLVED','gate':gate}
    integrated=np.asarray(total).reshape(5,2,9)
    integrated_err=np.asarray(err).reshape(5,2,9)
    output={}
    for i,name in enumerate(LANES):
        output[name]={}
        for j,Evalue in enumerate((0.5,5.0)):
            vec=np.zeros(DIM);error=np.zeros(DIM)
            vec[keep]=integrated[i,j];error[keep]=integrated_err[i,j]
            output[name][str(Evalue)]={
                'indexed_transition_areas_a0sq':{str(k+1):float(v) for k,v in enumerate(vec) if keep[k]},
                'indexed_reaction_loss_a0sq':float(vec.sum()),
                'indexed_reaction_loss_error_estimate_a0sq':float(error.sum()),
                'Z2_shell_areas_a0sq':_shell_summary(vec),
                'Z2_shell_error_estimate_a0sq':_shell_summary(error),
                'component_error_estimate_a0sq':{str(k+1):float(v) for k,v in enumerate(error) if keep[k]}}
    result={'status':'R10F_ROTATION_BOUNDARY_SPLIT_FIXED_GK_PASS_NOT_GLOBAL_CONTINUUM_BOUND',
            'lanes':output,'evaluations':255,'refinements':0,'intervals':17,
            'new_delta_solves_during_integration':0,'straight_steps':64,'coulomb_steps':1024,
            'claim_limit':'FINITE_INDEXED_STATE_RESEARCH_INTEGRAL_NOT_PHYSICAL_PRODUCTION_CROSS_SECTION'}
    atomic_json(HERE/'FIVE_LANE_RESULT.json',result)
    return result


def baseline_regression():
    result=json.loads((HERE/'FIVE_LANE_RESULT.json').read_text())
    if result['status']!='R10F_ROTATION_BOUNDARY_SPLIT_FIXED_GK_PASS_NOT_GLOBAL_CONTINUUM_BOUND':
        raise ValueError('R10F GK PASS required')
    old=json.loads((R10C/'EXACT_THREE_LANE_RESULT.json').read_text())['lanes']['F2-RHO']
    new=result['lanes']['SL_CPC']
    rows=[]
    for energy in ('0.5','5.0'):
        old_error_vector=np.zeros(DIM)
        for index,value in old[energy]['component_error_estimate_a0sq'].items():
            old_error_vector[int(index)-1]=value
        old_shell_error=_shell_summary(old_error_vector)
        for valkey,errkey in (('indexed_transition_areas_a0sq','component_error_estimate_a0sq'),
                              ('Z2_shell_areas_a0sq','Z2_shell_error_estimate_a0sq')):
            for label,now in new[energy][valkey].items():
                before=old[energy][valkey][label]
                old_err=(old[energy]['component_error_estimate_a0sq'][label]
                         if valkey=='indexed_transition_areas_a0sq' else
                         old_shell_error[label])
                now_err=new[energy][errkey][label]
                diff=now-before
                relative=abs(diff)/max(abs(before),np.finfo(float).tiny)
                rows.append({'energy_keV_u':float(energy),'observable':valkey,'label':label,
                             'r10c_value':before,'r10f_value':now,'absolute_difference':abs(diff),
                             'relative_difference':relative,'r10c_embedded_estimate':old_err,
                             'r10f_embedded_estimate':now_err})
    classification=classify_baseline_rows(rows)
    summary={'status':classification['status'],'material_row_indices_zero_based':classification['material_row_indices_zero_based'],
             'rule':classification['rule'],
             'rows':rows,'max_absolute_difference':max(x['absolute_difference'] for x in rows),
             'max_relative_difference':max(x['relative_difference'] for x in rows),
             'claim_limit':'CONSISTENCY_DIAGNOSTIC_NOT_REPLACEMENT_OF_R10C'}
    atomic_json(HERE/'BASELINE_REGRESSION.json',summary)
    return summary


def effects_and_appendix():
    result=json.loads((HERE/'FIVE_LANE_RESULT.json').read_text())
    baseline=json.loads((HERE/'BASELINE_REGRESSION.json').read_text())
    if (result['status']!='R10F_ROTATION_BOUNDARY_SPLIT_FIXED_GK_PASS_NOT_GLOBAL_CONTINUUM_BOUND'
        or baseline['status']!='PASS'):
        raise ValueError('R10F GK and baseline admission required')
    source=HERE.parents[2]/'20260929/CODE_I02_R10A_RHO_FREEZE_IMPACT/20260929T1535KST'
    oracle=json.loads((source/'APPENDIX_A_ORACLE.json').read_text())
    old=json.loads((source/'APPENDIX_A_COMPARISON.json').read_text())
    scale=old['a0_squared_cm2']
    classification='AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION'
    metrics={}
    for name,lanes in result['lanes'].items():
        rows=[];all_logs=[];dominant_logs=[]
        for energy in ('0.5','5.0'):
            for shell in ('1','2','3'):
                model=lanes[energy]['Z2_shell_areas_a0sq'][shell]*scale
                author=oracle['shell_capture_cm2'][energy][shell]
                if model<=0 or author<=0:
                    raise ValueError('nonpositive Appendix-A comparison cell')
                ratio=model/author;logratio=math.log(ratio)
                rows.append({'energy_keV_u':float(energy),'shell_n':int(shell),
                             'model_cm2':model,'author_cm2':author,
                             'model_over_author':ratio,'log_ratio':logratio,
                             'classification':classification})
                all_logs.append(logratio)
                if shell in ('2','3'):dominant_logs.append(logratio)
        metrics[name]={'rows':rows,
                       'all_six_multiplicative_rms':math.exp(math.sqrt(sum(x*x for x in all_logs)/6)),
                       'dominant_n2_n3_multiplicative_rms':math.exp(math.sqrt(sum(x*x for x in dominant_logs)/4)),
                       'classification':classification}
    all_rule=(metrics['COUL_AUTHOR']['all_six_multiplicative_rms']<=
              .95*metrics['SL_CPC']['all_six_multiplicative_rms'])
    dominant_rule=(metrics['COUL_AUTHOR']['dominant_n2_n3_multiplicative_rms']<=
                   .95*metrics['SL_CPC']['dominant_n2_n3_multiplicative_rms'])
    appendix={'classification':classification,'metrics':metrics,
              'COUL_AUTHOR_all_six_improves_at_least_5pct':all_rule,
              'COUL_AUTHOR_dominant_improves_at_least_5pct':dominant_rule,
              'COUL_AUTHOR_both_materially_improve':all_rule and dominant_rule,
              'claim_limit':'AUTHOR_IMPLEMENTATION_COMPARISON_NOT_PHYSICAL_VALIDATION'}
    atomic_json(HERE/'APPENDIX_A_COMPARISON.json',appendix)
    effects={}
    for energy in ('0.5','5.0'):
        effects[energy]={}
        specs=(('indexed_transition_areas_a0sq','component_error_estimate_a0sq'),
               ('Z2_shell_areas_a0sq','Z2_shell_error_estimate_a0sq'),
               ('indexed_reaction_loss_a0sq','indexed_reaction_loss_error_estimate_a0sq'))
        for values_key,errors_key in specs:
            first=result['lanes']['SL_CPC'][energy][values_key]
            labels=list(first) if isinstance(first,dict) else ['total']
            cells={}
            for label in labels:
                values={name:(lane[energy][values_key][label] if isinstance(first,dict) else
                              lane[energy][values_key]) for name,lane in result['lanes'].items()}
                errors={name:(lane[energy][errors_key][label] if isinstance(first,dict) else
                              lane[energy][errors_key]) for name,lane in result['lanes'].items()}
                b=values['SL_CPC']
                ratios={name:(value/b if b>0 else None) for name,value in values.items()}
                logratios={name:(math.log(x) if x is not None and x>0 else None) for name,x in ratios.items()}
                material={name:(b>0 and abs(value-b)/b>.01 and
                                abs(value-b)>10*(errors[name]+errors['SL_CPC']))
                          for name,value in values.items() if name!='SL_CPC'}
                cells[label]={'values_a0sq':values,'errors_a0sq':errors,
                              'cutoff_effect':values['SL_AUTHORCUT']-b,
                              'trajectory_effect':values['COUL_CPC']-b,
                              'interaction':values['COUL_AUTHOR']-values['COUL_CPC']-values['SL_AUTHORCUT']+b,
                              'frozen_delta_addition_effect':values['COUL_AUTHOR_FROZEN']-values['COUL_AUTHOR'],
                              'ratios_to_SL_CPC':ratios,'log_ratios_to_SL_CPC':logratios,
                              'material_vs_SL_CPC':material}
            effects[energy][values_key]=cells
    atomic_json(HERE/'EFFECT_DECOMPOSITION.json',effects)
    return appendix


if __name__=='__main__':
    result=run_fixed_gk()
    print(result['status'],flush=True)
    if result['status']=='R10F_ROTATION_BOUNDARY_SPLIT_FIXED_GK_PASS_NOT_GLOBAL_CONTINUUM_BOUND':
        print('baseline',baseline_regression()['status'],flush=True)
