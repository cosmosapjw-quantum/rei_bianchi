"""R10A research-only three-lane adapter. Not production Eq.50/54 policy."""
from __future__ import annotations

import math
import hashlib
import json
import platform
import sys
import time
import traceback
from pathlib import Path
import numpy as np
from bass_he.eq54 import BRANCHES, DeltaSurrogate, assemble_initial_column_batch, surrogate_geometry_mapping, validate_delta_surrogate, support_cutoffs
from bass_he.geometry import EvidenceCache, adaptive_seed_rhos, adaptive_vector_quadrature, atomic_json, contour_geometry
from bass_he.spectral import find_exceptional_point
from arseny_reimpl.cross_section import projectile_velocity_au
from arseny_reimpl.correlation import cordir_heh
from arseny_reimpl.state_index import enumerate_states


def frozen_geometry_mapping(surrogate, rhos):
    r=np.asarray(rhos,float)
    if r.ndim!=1 or np.any(~np.isfinite(r)) or np.any(r<0):
        raise ValueError('finite one-dimensional rho>=0 required')
    out={}
    for b in BRANCHES:
        delta0=float(surrogate.evaluate(b.name,[0.])[0])
        for rho in r[r<=b.support_cutoff]:
            out[(b.name,float(rho))]={'delta':delta0,'source':'R10A_FROZEN_RHO0_RESEARCH_ONLY'}
    return out


def assemble_three_lanes(surrogate, rhos, *, energies=(.5, 5.), rotation_steps=32):
    dynamic=assemble_initial_column_batch(surrogate_geometry_mapping(surrogate,rhos),energies,rhos,
                                           exponent_factors=(2,1),rotation_steps=rotation_steps)
    frozen=assemble_initial_column_batch(frozen_geometry_mapping(surrogate,rhos),energies,rhos,
                                          exponent_factors=(2,),rotation_steps=rotation_steps)
    lanes={'F2-RHO':dynamic['probabilities'][:,0],
           'F2-FROZEN':frozen['probabilities'][:,0],
           'F1-RHO':dynamic['probabilities'][:,1]}
    keep=np.arange(lanes['F2-RHO'].shape[-1])!=2
    return {'lanes':lanes,'components':np.concatenate([v[...,keep].reshape(len(rhos),-1)
                                                        for v in lanes.values()],axis=1)}


def probability_ratio(delta0, delta_rho, velocity):
    if not all(math.isfinite(x) for x in (delta0,delta_rho,velocity)) or velocity<=0:
        raise ValueError('finite deltas and positive velocity required')
    return math.exp(-2*(delta0-delta_rho)/velocity)


def validate_holdout_gate(surrogate, rows, *, threshold=2e-4):
    report=validate_delta_surrogate(surrogate,rows)
    report['threshold']=float(threshold)
    report['status']='PASS' if report['max_relative_error']<=threshold else 'FAIL'
    if report['status']!='PASS':
        raise ValueError(f"surrogate holdout gate failed: {report['max_relative_error']}")
    return report


def _source_identity(root):
    deps=('src/bass_he/geometry.py','src/bass_he/spectral.py','src/bass_he/eq54.py',
          'src/bass_he/rotation.py','src/bass_he/transport.py',
          'src/arseny_reimpl/eq50_scoped.py','src/arseny_reimpl/term_complex.py',
          'src/arseny_reimpl/term_real.py','src/arseny_reimpl/correlation.py',
          'scripts/r10a_rho_freeze.py')
    h=hashlib.sha256()
    for rel in deps:h.update(rel.encode()+b'\0'+(root/rel).read_bytes())
    return h.hexdigest(),deps


def _shell_summary(area):
    # These overlapping source correlations are diagnostic labels, not disjoint channels.
    by_shell={str(n):0.0 for n in (1,2,3)}
    for j,N,l,m in enumerate_states(3):
        if j==3:continue
        corr=cordir_heh(N,l,m)
        if corr.center=='Z2':by_shell[str(corr.n)]+=float(area[j-1])
    return by_shell


def run(outdir):
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    root=Path(__file__).resolve().parents[1]
    source,dependencies=_source_identity(root)
    contract={'source_sha256':source,'dependencies':dependencies,'numpy':np.__version__,
              'python':platform.python_version(),'depth':96,'panels':32,
              'surrogate_rule':'gk7','surrogate_holdout_relative_gate':2e-4,
              'integration_rule':'gk15','rtol':2e-4,'atol':1e-10,
              'max_intervals':96,'rotation_steps':32,'energies_keV_u':[.5,5.],
              'surrogate_source':'FRESH_R10A_REBUILD_NOT_DR8_BYTE_REPRODUCTION',
              'numerical_contract':'NEW_R10A_NUMERICAL_CONTRACT'}
    atomic_json(out/'RUN_CONTRACT.json',contract)
    cache=EvidenceCache(out/'cache')
    eps={};records={};anchor_rows={};hold_rows=[];diagnostic_rows=[];validation={}
    energies=(.5,5.)
    for b in BRANCHES:
        epkey={'source':source,'environment':(np.__version__,platform.python_version()),
               'kind':'R10A_EP','branch':b.name,'state_a':b.state_a,'state_b':b.state_b,
               'R':(b.R.real.hex(),b.R.imag.hex()),'depth':96}
        ep=cache.get(epkey)
        if ep is None:
            ep=find_exceptional_point(b.state_a,b.state_b,b.R,depth=96)
            cache.put(epkey,ep)
        if ep['certificate']['simple_fold'] is not True:raise RuntimeError(f'{b.name}: simple fold unavailable')
        eps[b.name]=ep
        atomic_json(out/f'EP_{b.name}.json',{'branch':b.name,'ep':ep})

        def exact(rho):
            rho=float(rho)
            key={'source':source,'environment':(np.__version__,platform.python_version()),
                 'kind':'R10A_CONTOUR','branch':b.name,'state_a':b.state_a,'state_b':b.state_b,
                 'R':(b.R.real.hex(),b.R.imag.hex()),'rho_hex':rho.hex(),
                 'depth':96,'panels':32}
            rec=cache.get(key)
            if rec is None:
                t=time.perf_counter()
                try:rec=contour_geometry(ep,rho,panels=32)
                except Exception:
                    atomic_json(out/f'FAIL_{b.name}_{rho.hex().replace("+", "p")}.json',
                                {'branch':b.name,'rho_hex':rho.hex(),'traceback':traceback.format_exc()})
                    raise
                rec['elapsed_s']=time.perf_counter()-t
                cache.put(key,rec)
            row={'branch':b.name,'rho':rho,'rho_hex':rho.hex(),'delta':float(rec['delta']),
                 'delta_hex':float(rec['delta']).hex(),'panels':32,
                 'max_spectral_residual':rec['max_spectral_residual'],
                 'minimum_normalized_sheet_gap':rec['minimum_normalized_sheet_gap'],
                 'accepted_continuation_steps':rec['accepted_continuation_steps'],
                 'bisected_continuation_steps':rec['bisected_continuation_steps'],
                 'elapsed_s':rec.get('elapsed_s')}
            records[(b.name,rho.hex())]=row
            atomic_json(out/f'PROGRESS_{b.name}.json',list(x for (name,_),x in records.items() if name==b.name))
            return row

        Rb=b.support_cutoff
        arhos=sorted(set([0.,Rb,*map(float,adaptive_seed_rhos([0.,Rb],rule='gk7'))]))
        anchors=[(rho,exact(rho)['delta']) for rho in arhos]
        fractions=(.125,.375,.625,.875,.95,.99)
        held=[exact(f*Rb) for f in fractions]
        surrogate=DeltaSurrogate({b.name:anchors})
        report=validate_delta_surrogate(surrogate,held)
        if report['max_relative_error']>2e-4:
            mid=Rb/math.sqrt(2)
            unit_seeds=adaptive_seed_rhos([0.,1.],rule='gk7')
            child_lo=[float(mid*x) for x in unit_seeds]
            child_hi=[float(math.sqrt(mid*mid+(Rb*Rb-mid*mid)*x*x)) for x in unit_seeds]
            extra=sorted(set([mid,*child_lo,*child_hi]))
            anchors=sorted(set(anchors+[(rho,exact(rho)['delta']) for rho in extra]))
            surrogate=DeltaSurrogate({b.name:anchors})
            report=validate_delta_surrogate(surrogate,held)
            report['refinement']='ONE_U_MIDPOINT_SPLIT'
        else:report['refinement']='NONE'
        report['threshold']=2e-4;report['status']='PASS' if report['max_relative_error']<=2e-4 else 'FAIL'
        validation[b.name]=report
        anchor_rows[b.name]=[{'rho':r,'rho_hex':r.hex(),'delta':d,'delta_hex':d.hex()} for r,d in anchors]
        hold_rows.extend(held)
        atomic_json(out/'SURROGATE_PROGRESS.json',{'anchors':anchor_rows,'holdouts':hold_rows,'validation':validation})
        if report['status']!='PASS':raise RuntimeError(f'{b.name}: SURROGATE_REBUILD_UNRESOLVED')

        delta0=exact(0.)['delta']
        for fraction in (0.,.25,.5,.75,.9,.99):
            row=exact(fraction*Rb)
            d=row['delta']
            by_energy={}
            for E in energies:
                v=projectile_velocity_au(E)
                p_rho=math.exp(-2*d/v);p_frozen=math.exp(-2*delta0/v)
                identity=probability_ratio(delta0,d,v)
                if not math.isclose(p_frozen/p_rho,identity,rel_tol=5e-13,abs_tol=5e-13):
                    raise ArithmeticError('probability ratio identity failed')
                by_energy[str(E)]={'velocity_au':v,'P_F2_RHO':p_rho,'P_F2_FROZEN':p_frozen,
                                   'frozen_over_rho':p_frozen/p_rho,'ratio_identity':identity}
            diagnostic_rows.append({'branch':b.name,'support_cutoff':Rb,'rho_fraction':fraction,
                                    'rho':row['rho'],'delta':d,'delta0':delta0,
                                    'delta_over_delta0':d/delta0,'active':row['rho']<=Rb,
                                    'energies':by_energy})
        atomic_json(out/'BRANCH_DIAGNOSTICS_PROGRESS.json',diagnostic_rows)

    surrogate=DeltaSurrogate({name:[(x['rho'],x['delta']) for x in rows]
                              for name,rows in anchor_rows.items()})
    validate_holdout_gate(surrogate,hold_rows,threshold=2e-4)
    atomic_json(out/'SURROGATE_MANIFEST.json',{'source':contract['surrogate_source'],
               'claim_ceiling':'R10A_HELDOUT_NUMERICALLY_VALIDATED_NOT_DR8_BYTE_IDENTICAL_NOT_GLOBAL_BOUND',
               'anchors':anchor_rows,'holdouts':hold_rows,'validation':validation})
    atomic_json(out/'BRANCH_DIAGNOSTICS.json',diagnostic_rows)

    diagnostics={'max_column_sum_defect':0.,'minimum_probability':1.,'maximum_probability':0.}
    def evaluate(rhos):
        result=assemble_three_lanes(surrogate,np.asarray(rhos,float),energies=energies,rotation_steps=32)
        for probs in result['lanes'].values():
            diagnostics['max_column_sum_defect']=max(diagnostics['max_column_sum_defect'],float(np.max(abs(probs.sum(-1)-1.))))
            diagnostics['minimum_probability']=min(diagnostics['minimum_probability'],float(np.min(probs)))
            diagnostics['maximum_probability']=max(diagnostics['maximum_probability'],float(np.max(probs)))
        return result['components']
    cuts=support_cutoffs(rotation_cut_scale=1.0)
    quad=adaptive_vector_quadrature(evaluate,cuts,rtol=2e-4,atol=1e-10,max_intervals=96,rule='gk15')
    values=np.asarray(quad['integral']).reshape(3,2,9)
    errors=np.asarray(quad['component_error_estimate']).reshape(3,2,9)
    lanes={}
    for k,name in enumerate(('F2-RHO','F2-FROZEN','F1-RHO')):
        lanes[name]={}
        for j,E in enumerate(energies):
            vec=np.zeros(10);err=np.zeros(10);vec[np.arange(10)!=2]=values[k,j];err[np.arange(10)!=2]=errors[k,j]
            lanes[name][str(E)]={'indexed_transition_areas_a0sq':{str(i+1):float(x) for i,x in enumerate(vec) if i!=2},
                                 'indexed_reaction_loss_a0sq':float(vec.sum()),
                                 'indexed_reaction_loss_error_estimate_a0sq':float(err.sum()),
                                 'Z2_shell_areas_a0sq':_shell_summary(vec),
                                 'component_error_estimate_a0sq':{str(i+1):float(x) for i,x in enumerate(err) if i!=2}}
    output={'contract':contract,'quadrature':{k:v for k,v in quad.items() if k!='integral' and k!='component_error_estimate' and k!='component_tolerance'},
            'max_normalized_component_error':float(np.max(quad['component_error_estimate']/quad['component_tolerance'])),
            'diagnostics':diagnostics,'lanes':lanes,
            'claim':'FINITE_INDEXED_STATE_RESEARCH_INTEGRAL_NOT_PHYSICAL_PRODUCTION_CROSS_SECTION'}
    atomic_json(out/'THREE_LANE_RESULT.json',output)
    return output


if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python scripts/r10a_rho_freeze.py OUTDIR')
    run(sys.argv[1])
