#!/usr/bin/env python3
"""Offline, bounded replay. Does not run any upstream history or provider."""
from pathlib import Path
from fractions import Fraction as F
from itertools import product
import argparse, hashlib, json, platform, resource, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from bridge.joint_moment import FixedContext, JointMomentFamily, conditional_joint_enclosure
from bridge.vendor.source_transfer import State, Moments, project, conditional_source_box

def rational(v):
    return F(int(v['numerator']), int(v['denominator']))

def parse(record):
    state = State(**{k:rational(v) for k,v in record['gas'].items()})
    m = record['moments']
    return state, Moments(tuple(map(rational,m['gamma'])), tuple(map(rational,m['energy_ev_s']))), tuple(map(rational,record['chi_ev']))

def mix(a,b,scale_a,scale_b):
    return Moments(tuple(scale_a*x+scale_b*y for x,y in zip(a.gamma,b.gamma)),
                   tuple(scale_a*x+scale_b*y for x,y in zip(a.energy_ev_s,b.energy_ev_s)))

def independent(state, m, chi):
    """Direct thermodynamic formula, independent of upstream project implementation."""
    f=state.n_he/state.n_h
    dh=(1-state.h)*m.gamma[0]
    dy=(1-state.y-state.z)*m.gamma[1]-state.y*m.gamma[2]
    dz=state.y*m.gamma[2]
    xe=dh+f*(dy+2*dz)
    targets=(1-state.h,f*(1-state.y-state.z),f*state.y)
    heat=state.ev_erg*sum((a*(e-c*g) for a,e,c,g in zip(targets,m.energy_ev_s,chi,m.gamma)),F(0))
    particles=1+f+state.h+f*(state.y+2*state.z)
    temp=2*heat/(3*state.kb_erg_k*particles)-2*state.w_erg_h*xe/(3*state.kb_erg_k*particles**2)
    return {'electron_dt_per_h_s':xe,'heat_erg_h_s':heat,'temperature_dt_k_s':temp,
            'photo_q_ell_source':state.c_thomson_cm3_s*state.n_h*xe/state.hubble_s**2}

def source_hashes():
    files=list((ROOT/'bridge').rglob('*.py'))+list((ROOT/'tests').rglob('*.py'))+list((ROOT/'inputs').glob('*'))+list((ROOT/'scripts').glob('*.py'))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files) if p.is_file()}

def experiment():
    fixture=json.loads((ROOT/'inputs/OFF_H4_K5_fixture.json').read_text())
    records=fixture['records']; parity=0; oracle=0
    for record in records.values():
        st,m,chi=parse(record); got=project(st,m,chi)
        for key,value in got.items():
            assert value==rational(record['projection'][key]), ('UPSTREAM_PARITY',key)
            parity+=1
        for key,value in independent(st,m,chi).items():
            assert value==got[key],('INDEPENDENT_ALGEBRA',key)
            oracle+=1
    comparisons=[]
    for comparison in fixture['comparisons']:
        left=records['OFF_H4_K5_'+comparison['left']]
        right=records['OFF_H4_K5_'+comparison['right']]
        st,a,chi=parse(left); other,b,other_chi=parse(right)
        assert st==other and chi==other_chi and left['s']==right['s']
        delta=project(st,b-a,chi)
        for key,val in comparison['source_difference'].items():
            assert delta[key]==rational(val),('SAVED_DELTA',key)
            parity+=1
        context=FixedContext('CR-R11:'+fixture['source_archive_sha256'],'stored-ln-a-OFF-H4-K5',
                             'OFF-H4-K5-exact-gas','R11-pinned-chi-Verner-readout',st,rational(left['s']),chi)
        center=mix(a,b,F(1,2),F(1,2)); generator=mix(a,b,F(-1,2),F(1,2))
        family=JointMomentFamily(center,(generator,),context,
                    family_id=comparison['left']+'__'+comparison['right'],family_kind='finite_rule_envelope',generator_ids=('same-rule-interpolation',))
        enclosure=conditional_joint_enclosure(st,chi,family,context=context,
            premises=('Only convex combinations of these two saved finite-rule moment vectors at the same fixed state.',
                      'This hull is not a bound on true spectral/time/provider error.'))
        vertices=[independent(st,m,chi) for m in (a,b)]
        for key in vertices[0]:
            assert enclosure.bounds_native[key]==(min(v[key] for v in vertices),max(v[key] for v in vertices))
            oracle+=1
        gb=tuple((min(x,y),max(x,y)) for x,y in zip(a.gamma,b.gamma))
        eb=tuple((min(x,y),max(x,y)) for x,y in zip(a.energy_ev_s,b.energy_ev_s))
        rectangular=conditional_source_box(st,chi,gb,eb,premises='The same finite-rule marginal ranges, deliberately decorrelated.')
        gains={}
        for key in enclosure.bounds_native:
            lo,hi=enclosure.bounds_native[key]; rlo,rhi=rectangular[key]
            assert rlo<=lo<=hi<=rhi
            gains[key]=None if hi==lo else float((rhi-rlo)/(hi-lo))
        comparisons.append({'pair':family.family_id,'enclosure':enclosure.as_json(),
                            'independent_box_width_over_correlated_width':gains,
                            'heat_delta':str(delta['heat_erg_h_s']),
                            'temperature_delta':str(delta['temperature_dt_k_s'])})
    old=json.loads((ROOT/'inputs/RAW4_ENDCUT4_11_epoch_projection.json').read_text())['records']
    inversions=sum(rational(r['source_difference']['heat_erg_h_s'])*rational(r['source_difference']['temperature_dt_k_s'])<0 for r in old)
    return {'status':'PASS_BOUNDED_ALGEBRA_ONLY','actual_saved_input_records':len(records),
            'upstream_exact_scalar_replay_comparisons':parity,'independent_formula_comparisons':oracle,
            'new_correlated_finite_rule_families':len(comparisons),'comparisons':comparisons,
            'recount_of_saved_11_epoch_deltas':{'records':len(old),'heat_T_sign_inversions':inversions,'new_spectral_sums':0},
            'provider_calls':0,'new_history_steps':0,'true_spectral_error':None,'physical':'HOLD',
            'receiver_integration':'NOT_IMPLEMENTED; actual midpoint records have integrated A/B and zero nonphoto-stage photo RHS; separate instantaneous moment exporter needed.'}

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    args.output.mkdir(parents=True,exist_ok=False)
    before=source_hashes(); start=time.monotonic(); usage=resource.getrusage(resource.RUSAGE_SELF)
    test=subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-v'],cwd=ROOT,text=True,capture_output=True,timeout=90)
    (args.output/'tests.stdout').write_text(test.stdout);(args.output/'tests.stderr').write_text(test.stderr)
    report={'tests_exit':test.returncode,'source_before':before,'python':platform.python_version()}
    try:
        if test.returncode: raise RuntimeError('TARGETED_TESTS_FAILED')
        report.update(experiment())
    except Exception as exc:
        report.update(status='FAIL',failure_type=type(exc).__name__,failure=str(exc));raise
    finally:
        report['source_after']=source_hashes();report['source_unchanged']=before==report['source_after']
        report['wall_seconds']=time.monotonic()-start
        end=resource.getrusage(resource.RUSAGE_SELF)
        report['owner_cpu_seconds']=end.ru_utime+end.ru_stime-usage.ru_utime-usage.ru_stime
        report['owner_maxrss_KiB']=end.ru_maxrss
        (args.output/'RESULTS.json').write_text(json.dumps(report,indent=2)+'\n')
    assert report['source_unchanged'],'SOURCE_MUTATED_DURING_REPLAY'
    print(json.dumps({k:v for k,v in report.items() if k not in ['source_before','source_after','comparisons']},indent=2))

if __name__=='__main__': main()
