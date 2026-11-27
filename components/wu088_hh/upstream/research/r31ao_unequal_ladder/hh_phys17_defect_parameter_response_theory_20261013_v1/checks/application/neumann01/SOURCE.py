#!/usr/bin/env python3
"""Finite Neumann error bounds for the frozen PHYS17 derivative equation."""
import argparse
import hashlib
import importlib.util
import json
import pathlib
import resource
import sys
import time


def main(p15,p16,output):
    tic=time.perf_counter()
    root=pathlib.Path(__file__).resolve().parents[1]
    deps=[]
    def read(base,rel):
        path=base/rel;data=path.read_bytes()
        deps.append({'path':str(path),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        return json.loads(data)
    helper=p15/'inputs/phys14/src/phys14_advance.py'
    assert hashlib.sha256(helper.read_bytes()).hexdigest()=='d20d9797278b8da71d38a3db229325dc7792d3991863f07bcdb7f72f2ba5567a'
    spec=importlib.util.spec_from_file_location('p14_arithmetic',helper)
    old=importlib.util.module_from_spec(spec);sys.dont_write_bytecode=True;spec.loader.exec_module(old)
    I,raw=old.I,old.from_raw
    app=read(root,'checks/application/run02/results/PARAMETER_RESPONSE_RESULTS.json')
    assert deps[-1]['sha256']=='fd4fc0fe6bcf035496270bb92f0c56c44ca43d16694cb40296087569a305e7c0'
    endpoint=read(p16,'checks/endpoint/application01/ENDPOINT_REMAINDER_RESULTS.json')
    assert deps[-1]['sha256']=='6cf01b2c6f69c0ff89ab5f2a3487ea34fbd35da6c0f72b6f4ee09e1d7ad5b4c8'
    q=raw(app['fixed_transfer']['q']).hi
    LH=raw(endpoint['L_H']).hi
    a=raw(endpoint['a_after_endpoint_intersection']).hi
    S=[raw(x).hi for x in app['fixed_transfer']['S']]
    C=[[raw(x) for x in row] for row in app['fixed_transfer']['C']]
    d=[raw(x) for x in app['fixed_endpoint_data']['d']]
    assert max(d[i].mag()/S[i] for i in range(4))<=a
    assert q<1
    m=2
    geom=sum((q**k for k in range(m+1)))
    outputs={}
    for parameter,item in app['responses'].items():
        ftheta=[raw(x) for x in item['correlated_rhs']]
        cf=old.matvec(C,ftheta)
        cf_norm=max(cf[i].mag()/S[i] for i in range(4))
        atheta=cf_norm/(1-q)
        factor_F=q**(m+1)
        factor_y=factor_F+LH*a*geom
        epsF=factor_F*atheta
        epsy=factor_y*atheta
        row=[raw(x) for x in item['temperature_goal_row']]
        goalnorm=sum(row[i].mag()*S[i] for i in range(4))
        outputs[parameter]={
            'C_f_theta':cf,'C_f_theta_scaled_norm_upper':I(cf_norm),
            'a_theta_upper':I(atheta),'m':m,
            'JF_Neumann_error_upper_scaled':I(epsF),
            'Jy_Neumann_error_upper_scaled':I(epsy),
            'goal_row_weighted_one_norm_upper_K':I(goalnorm),
            'JF_temperature_derivative_surrogate_error_upper_K':I(goalnorm*epsF),
            'Jy_temperature_derivative_surrogate_error_upper_K':I(goalnorm*epsy),
            'JF_pointwise_polynomial':'sum_{k=0}^2 (I-C J_F)^k C f_theta',
            'Jy_pointwise_polynomial':'sum_{k=0}^2 (I-C J_y)^k C f_theta',
            'Jy_endpoint_change_factor_upper':I(LH*a*geom),
            'same_P4_geometry_term':'retained; only d_theta is replaced by the polynomial'}
    result={'schema':'WU088_HH_PHYS17_DERIVATIVE_NEUMANN_V1','status':'CANDIDATE_COMPUTED',
        'input_identities':deps,'q':I(q),'L_H':I(LH),'a_endpoint_defect':I(a),'S':S,
        'sum_q_0_to_2':I(geom),'responses':outputs,
        'formulae':{'a_theta':'||C f_theta||_S/(1-q)',
                   'JF':'q^3 a_theta',
                   'Jy':'[q^3+L_H a (1+q+q^2)] a_theta',
                   'Jacobian_difference':'||C(J_y-J_F)||_S <= L_H a; no factor 1/2',
                   'temperature':'weighted one-norm of the same P4 goal row times scaled defect error'},
        'source_calls':0,'root_solves':0,'history_replays':0,
        'elapsed_seconds':time.perf_counter()-tic,'peak_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    output.mkdir(parents=True,exist_ok=False)
    (output/'DERIVATIVE_NEUMANN_RESULTS.json').write_text(json.dumps(old.out(result),ensure_ascii=False,indent=2)+'\n')
    brief={p:{k:old.short(v[k]) for k in ('a_theta_upper','JF_Neumann_error_upper_scaled','Jy_Neumann_error_upper_scaled',
                'goal_row_weighted_one_norm_upper_K','JF_temperature_derivative_surrogate_error_upper_K','Jy_temperature_derivative_surrogate_error_upper_K')} for p,v in outputs.items()}
    (output/'SUMMARY.json').write_text(json.dumps(brief,indent=2)+'\n')
    print(json.dumps(brief,indent=2))


if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--parent15',type=pathlib.Path,required=True)
    ap.add_argument('--parent16',type=pathlib.Path,required=True)
    ap.add_argument('--output',type=pathlib.Path,required=True)
    a=ap.parse_args();main(a.parent15.resolve(),a.parent16.resolve(),a.output.resolve())
