"""Research-only fixed-node factorial rotation comparison after R10E gate PASS."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np

from arseny_reimpl.cross_section import projectile_velocity_au
from arseny_reimpl.eq50_scoped import branch_state_indices
from arseny_reimpl.rotational import s_sigma_boundary
from bass_he.eq54 import BRANCHES, DIM, INITIAL_INDEX_ZERO_BASED, support_cutoffs
from bass_he.geometry import AdaptiveQuadratureError, _gk15_reduce, atomic_json
from bass_he.rotation import full_rotation_batch, rotation_batch
from bass_he.transport import apply_eq50
from arseny_reimpl.state_index import state_index
from scripts.r10a_rho_freeze import _shell_summary
from coulomb_rotation import author_cutoff, coulomb_rotation_batch
from rotation_convergence import fixed_rhos
from r10c_runner import fixed_node_integrate, validate_exact_table

HERE = Path(__file__).resolve().parent
R10C = HERE.parents[2]/'20260929/CODE_I02_R10C_EXACT_NODE_EXECUTION/20260929T1842KST'
R10A = HERE.parents[2]/'20260929/CODE_I02_R10A_RHO_FREEZE_IMPACT/20260929T1535KST'
TABLE = R10C/'EXACT_NODE_TABLE.json'
LANES = ('SL_CPC','SL_AUTHORCUT','COUL_CPC','COUL_AUTHOR','COUL_AUTHOR_FROZEN')
CLASS = 'AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION'


def rotation_matrices(E, rho):
    """Four explicitly selected rotation models on the same source state basis."""
    matrices = {}
    for trajectory, cutoff_label in (('SL','CPC'),('SL','AUTHORCUT'),('COUL','CPC'),('COUL','AUTHOR')):
        P = np.broadcast_to(np.eye(DIM),(len(E),DIM,DIM)).copy()
        for N,l in ((2,1),(3,1),(3,2)):
            cut = s_sigma_boundary(l) if cutoff_label=='CPC' else author_cutoff(l)
            if trajectory=='SL':
                block = rotation_batch(N,l,E,rho,steps=64,R_cut=cut)['P_abs']
            else:
                block = coulomb_rotation_batch(N,l,E,rho,steps=1024,R_cut=cut)['P_abs']
            ids=np.array([state_index(N,l,m)-1 for m in range(l+1)])
            P[:,ids[:,None],ids]=block
        matrices[trajectory+'_'+cutoff_label]=P
    # The baseline is the source implementation with the accepted resolution.
    if not np.array_equal(matrices['SL_CPC'],full_rotation_batch(3,E,rho,steps=64,R_cut_scale=1.0)):
        raise AssertionError('SL_CPC source baseline mismatch')
    return matrices


def input_probabilities(table, rho, E, frozen):
    exact={(row['branch'],row['rho_hex']):float.fromhex(row['delta_hex']) for row in table['rows']}
    delta0={row['branch']:float.fromhex(row['delta0_hex']) for row in frozen['records']}
    if len(delta0)!=5 or len(exact)!=360:
        raise ValueError('exact/frozen table incomplete')
    velocities=np.array([projectile_velocity_au(float(x)) for x in E])
    dynamic=np.zeros((len(rho),len(E),len(BRANCHES)))
    static=np.zeros_like(dynamic)
    for i,r in enumerate(rho):
        for k,b in enumerate(BRANCHES):
            if r <= b.support_cutoff:
                d=exact[(b.name,float(r).hex())]
                dynamic[i,:,k]=np.exp(-2*d/velocities)
                static[i,:,k]=np.exp(-2*delta0[b.name]/velocities)
    return dynamic.reshape(-1,len(BRANCHES)),static.reshape(-1,len(BRANCHES))


def prepare_inputs():
    convergence=json.loads((HERE/'EXTENDED_CONVERGENCE.json').read_text())
    if convergence['status']!='R10E_ROTATION_NUMERICS_PASS_EXTENDED_CONTRACT':
        raise RuntimeError('R10E_NUMERICAL_GATE_REQUIRED')
    gate=json.loads((HERE/'GATE_PRECOMMITTED.json').read_text())
    if convergence['gate_sha256']!=hashlib.sha256((HERE/'GATE_PRECOMMITTED.json').read_bytes()).hexdigest():
        raise ValueError('R10E_GATE_IDENTITY_MISMATCH')
    if hashlib.sha256(TABLE.read_bytes()).hexdigest()!=gate['r10c_table_sha256']:
        raise ValueError('R10C_TABLE_IDENTITY_MISMATCH')
    table=json.loads(TABLE.read_text())
    manifest=json.loads((R10C/'EXACT_NODE_TABLE_MANIFEST.json').read_text())
    if manifest['table_sha256']!=gate['r10c_table_sha256'] or manifest['row_count']!=360:
        raise ValueError('R10C_MANIFEST_MISMATCH')
    nodes=fixed_rhos(TABLE)
    if [float(x).hex() for x in nodes]!=gate['rho_hex']:
        raise ValueError('FIXED_NODE_IDENTITY_MISMATCH')
    if table['query_sha256']!=manifest['query_sha256']:
        raise ValueError('R10B_QUERY_IDENTITY_MISMATCH')
    expected=[{'branch':b.name,'rho':float(r),'rho_hex':float(r).hex()}
              for b in BRANCHES for r in nodes if r<=b.support_cutoff]
    validate_exact_table(expected,table['rows'])
    frozen=json.loads((R10C/'FROZEN_DELTA0_RECORD.json').read_text())
    return table, frozen, nodes


def run():
    table,frozen,nodes=prepare_inputs()
    E=np.array((0.5,5.0))
    cuts=support_cutoffs(rotation_cut_scale=1.0)
    expected_hex=[float(x).hex() for x in nodes]
    captured={}
    events=[]
    for b in BRANCHES:
        i,j=branch_state_indices(b)
        events.append((i-1,j-1,b.state_b[0]==3))
    initial=np.eye(DIM)[:,[INITIAL_INDEX_ZERO_BASED]]

    def evaluate(rhos):
        if [float(x).hex() for x in rhos]!=expected_hex:
            raise ValueError('fixed GK consumed-node order mismatch')
        pair_e=np.tile(E,len(rhos));pair_r=np.repeat(rhos,len(E))
        rotations=rotation_matrices(pair_e,pair_r)
        p_dyn,p_frozen=input_probabilities(table,rhos,E,frozen)
        probabilities={}
        for name in LANES:
            rotation=rotations['COUL_AUTHOR'] if name=='COUL_AUTHOR_FROZEN' else rotations[name]
            crossing=p_frozen if name=='COUL_AUTHOR_FROZEN' else p_dyn
            probabilities[name]=apply_eq50(crossing,events,rotation,initial)[...,0].reshape(len(rhos),len(E),DIM)
        keep=np.arange(DIM)!=INITIAL_INDEX_ZERO_BASED
        values=np.concatenate([probabilities[name][...,keep].reshape(len(rhos),-1) for name in LANES],axis=1)
        captured['values']=values
        captured['max_column_sum_defect']=max(float(np.max(abs(p.sum(-1)-1.))) for p in probabilities.values())
        captured['minimum_probability']=min(float(p.min()) for p in probabilities.values())
        captured['rotation_max_column_sum_defect']=max(float(np.max(abs(p.sum(1)-1.))) for p in rotations.values())
        return values

    try:
        quad=fixed_node_integrate(evaluate,cuts,expected_hex,rtol=2e-4,atol=1e-10)
        converged=True; exception=None
    except AdaptiveQuadratureError as exc:
        quad=None;converged=False;exception=str(exc)
    if 'values' not in captured:
        raise RuntimeError('no fixed nodes evaluated')
    intervals=[_gk15_reduce(a*a,b*b,captured['values'][15*i:15*(i+1)])
               for i,(a,b) in enumerate(zip(cuts[:-1],cuts[1:]))]
    total=sum((x['high'] for x in intervals),np.zeros_like(intervals[0]['high']))
    error=sum((x['error'] for x in intervals),np.zeros_like(total))
    tolerance=1e-10+2e-4*np.abs(total)
    diagnostic={'status':'PASS' if converged else 'R10E_FIXED_GK_QUADRATURE_UNRESOLVED',
                'evaluations':105,'refinements':0,'mandatory_intervals':len(cuts)-1,
                'rtol':2e-4,'atol':1e-10,'failed_component_count':int(np.sum(error>tolerance)),
                'max_normalized_component_error':float(np.max(error/np.maximum(tolerance,np.finfo(float).tiny))),
                'component_error_estimate':error.tolist(),'component_tolerance':tolerance.tolist(),
                'max_column_sum_defect':captured['max_column_sum_defect'],
                'rotation_max_column_sum_defect':captured['rotation_max_column_sum_defect'],
                'minimum_probability':captured['minimum_probability'],'adaptive_exception':exception,
                'error_claim':'EMBEDDED_NUMERICAL_ESTIMATE_NOT_INTERVAL_BOUND'}
    atomic_json(HERE/'FIXED_GK_DIAGNOSTIC.json',diagnostic)
    if not converged:
        return {'status':'R10E_FIXED_GK_QUADRATURE_UNRESOLVED'}
    if quad['evaluations']!=105 or quad['refinements']!=0 or np.any(error>tolerance):
        raise AssertionError('fixed GK internal verdict contradiction')
    vals=np.asarray(quad['integral']).reshape(5,2,9)
    errs=np.asarray(quad['component_error_estimate']).reshape(5,2,9)
    output={}
    for k,name in enumerate(LANES):
        output[name]={}
        for j,energy in enumerate(E):
            vec=np.zeros(DIM); err=np.zeros(DIM)
            vec[np.arange(DIM)!=INITIAL_INDEX_ZERO_BASED]=vals[k,j]
            err[np.arange(DIM)!=INITIAL_INDEX_ZERO_BASED]=errs[k,j]
            output[name][str(float(energy))]={
                'indexed_transition_areas_a0sq':{str(i+1):float(v) for i,v in enumerate(vec) if i!=INITIAL_INDEX_ZERO_BASED},
                'indexed_reaction_loss_a0sq':float(vec.sum()),
                'indexed_reaction_loss_error_estimate_a0sq':float(err.sum()),
                'Z2_shell_areas_a0sq':_shell_summary(vec),
                'Z2_shell_error_estimate_a0sq':_shell_summary(err),
                'component_error_estimate_a0sq':{str(i+1):float(v) for i,v in enumerate(err) if i!=INITIAL_INDEX_ZERO_BASED}}
    result={'status':'R10E_FIVE_LANE_FIXED_GK_PASS','lanes':output,'evaluations':105,'refinements':0,
            'new_contour_solves':0,'straight_steps':64,'coulomb_steps':1024,
            'claim_limit':'FINITE_INDEXED_STATE_RESEARCH_INTEGRAL_NOT_PHYSICAL_PRODUCTION_CROSS_SECTION'}
    atomic_json(HERE/'FIVE_LANE_RESULT.json',result)
    return result


def effects_and_appendix():
    result=json.loads((HERE/'FIVE_LANE_RESULT.json').read_text())
    if result['status']!='R10E_FIVE_LANE_FIXED_GK_PASS':
        raise ValueError('five-lane GK admission required')
    oracle=json.loads((R10A/'APPENDIX_A_ORACLE.json').read_text())
    old=json.loads((R10A/'APPENDIX_A_COMPARISON.json').read_text())
    scale=old['a0_squared_cm2']
    metrics={}
    for name,lane in result['lanes'].items():
        rows=[];all_logs=[];dom_logs=[]
        for energy in ('0.5','5.0'):
            for shell in ('1','2','3'):
                model=lane[energy]['Z2_shell_areas_a0sq'][shell]*scale
                author=oracle['shell_capture_cm2'][energy][shell]
                if model<=0 or author<=0:
                    raise ValueError('nonpositive Appendix comparison cell')
                logratio=math.log(model/author)
                rows.append({'energy_keV_u':float(energy),'shell_n':int(shell),'model_cm2':model,
                             'author_cm2':author,'model_over_author':model/author,
                             'log_ratio':logratio,'classification':CLASS})
                all_logs.append(logratio)
                if shell in ('2','3'):dom_logs.append(logratio)
        metrics[name]={'all_six_multiplicative_rms':math.exp(math.sqrt(sum(x*x for x in all_logs)/6)),
                       'dominant_n2_n3_multiplicative_rms':math.exp(math.sqrt(sum(x*x for x in dom_logs)/4)),
                       'rows':rows,'classification':CLASS}
    keys=(('indexed_transition_areas_a0sq','component_error_estimate_a0sq'),
          ('Z2_shell_areas_a0sq','Z2_shell_error_estimate_a0sq'))
    decomposition={}
    for energy in ('0.5','5.0'):
        decomposition[energy]={}
        for valkey,errkey in keys:
            cells={}
            labels=result['lanes']['SL_CPC'][energy][valkey].keys()
            for label in labels:
                x={name:result['lanes'][name][energy][valkey][label] for name in LANES}
                e={name:result['lanes'][name][energy][errkey][label] for name in LANES}
                baseline=x['SL_CPC']
                changes={'cutoff_effect':x['SL_AUTHORCUT']-baseline,
                         'trajectory_effect':x['COUL_CPC']-baseline,
                         'interaction':x['COUL_AUTHOR']-x['COUL_CPC']-x['SL_AUTHORCUT']+baseline,
                         'frozen_delta_addition_effect':x['COUL_AUTHOR_FROZEN']-x['COUL_AUTHOR']}
                lane_ratios={name:(x[name]/baseline if baseline>0 else None) for name in LANES}
                log_ratios={name:(math.log(ratio) if ratio is not None and ratio>0 else None) for name,ratio in lane_ratios.items()}
                material={name:(baseline>0 and abs(x[name]-baseline)/baseline>0.01 and
                                abs(x[name]-baseline)>10*(e[name]+e['SL_CPC'])) for name in LANES if name!='SL_CPC'}
                cells[label]={'values_a0sq':x,'errors_a0sq':e,**changes,
                              'ratios_to_SL_CPC':lane_ratios,'log_ratios_to_SL_CPC':log_ratios,
                              'material_vs_SL_CPC':material}
            decomposition[energy][valkey]=cells
        x={name:result['lanes'][name][energy]['indexed_reaction_loss_a0sq'] for name in LANES}
        e={name:result['lanes'][name][energy]['indexed_reaction_loss_error_estimate_a0sq'] for name in LANES}
        base=x['SL_CPC']
        decomposition[energy]['indexed_reaction_loss']={'values_a0sq':x,'errors_a0sq':e,
            'cutoff_effect':x['SL_AUTHORCUT']-base,'trajectory_effect':x['COUL_CPC']-base,
            'interaction':x['COUL_AUTHOR']-x['COUL_CPC']-x['SL_AUTHORCUT']+base,
            'frozen_delta_addition_effect':x['COUL_AUTHOR_FROZEN']-x['COUL_AUTHOR'],
            'ratios_to_SL_CPC':{name:x[name]/base for name in LANES},
            'material_vs_SL_CPC':{name:abs(x[name]-base)/base>0.01 and
                                   abs(x[name]-base)>10*(e[name]+e['SL_CPC']) for name in LANES if name!='SL_CPC'}}
    base=metrics['SL_CPC'];author=metrics['COUL_AUTHOR']
    improvement={key:author[key]<=0.95*base[key]
                 for key in ('all_six_multiplicative_rms','dominant_n2_n3_multiplicative_rms')}
    comparison={'classification':CLASS,'metrics':metrics,'COUL_AUTHOR_improvement_vs_SL_CPC':improvement,
                'both_materially_improve':all(improvement.values()),
                'baseline':'SL_CPC','claim_limit':'AUTHOR_IMPLEMENTATION_COMPARISON_NOT_PHYSICAL_VALIDATION'}
    atomic_json(HERE/'EFFECT_DECOMPOSITION.json',decomposition)
    atomic_json(HERE/'APPENDIX_A_COMPARISON.json',comparison)
    return comparison


if __name__=='__main__':
    result=run()
    print(result['status'],flush=True)
    if result['status']=='R10E_FIVE_LANE_FIXED_GK_PASS':
        print('COUL_AUTHOR both metrics improve',effects_and_appendix()['both_materially_improve'])
