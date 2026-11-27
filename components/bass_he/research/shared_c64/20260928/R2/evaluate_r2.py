#!/usr/bin/env python3
"""Bounded replay on R1 saved traces. Never calls a spectral solver or cloud API."""
import argparse, hashlib, json, platform
from pathlib import Path
from prepared_io import publish_json, read_trace_inputs, require_new_output, tests_not_run


def dec(x):
    if isinstance(x,dict):
        if set(x)=={'complex'}:return complex(*x['complex'])
        return {k:dec(v) for k,v in x.items()}
    return x


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--r1-root',type=Path,required=True)
    ap.add_argument('--input-manifest',type=Path,default=Path(__file__).with_name('TRACE_INPUTS.json'))
    ap.add_argument('--out',type=Path,required=True)
    ap.add_argument('--verify-only',action='store_true',help='Check byte identity only; no numeric imports or computation')
    args=ap.parse_args()
    require_new_output(args.out)
    files,input_receipt=read_trace_inputs(args.r1_root,args.input_manifest)
    if args.verify_only:
        output=dict(node='SHARED_C64_R2',status='INPUT_IDENTITY_VERIFIED',
                    input_identity=input_receipt,saved_trace_analysis='NOT_RUN',
                    new_spectral_solves=0,new_cloud_runs=0,tests=tests_not_run(),
                    PROMOTE='HOLD',Eq55='NOT_RUN',continuum_ionization='NOT_ADMITTED')
        publish_json(args.out,output)
        print(json.dumps(output,indent=2,allow_nan=False))
        return
    import numpy as np
    import sympy as sy
    from error_envelopes import action_jet, interpolation_bound, gap_error_bound, certified_mesh, hybrid_telescope
    rows=[];budget=1e-5
    for relative,raw in files:
        o=json.loads(raw);traces={}
        for panels in ('32','64'):
            t=o['traces'][panels]
            R,g,dR=[np.array([dec(x) for x in t[key]],complex) for key in ('R','gap','dR')]
            rho_max=.75*R[0].real
            mesh=certified_mesh(R,g,dR,rho_max,budget)
            maxerr=0.;maxratio=0.;checked=0
            for i,(lo,hi) in enumerate(zip(mesh['nodes'][:-1],mesh['nodes'][1:])):
                A,B=mesh['values'][i:i+2];bound=mesh['interval_bounds'][i]
                for theta in (1/7,1/3,1/2,2/3,6/7):
                    rho=lo+(hi-lo)*theta
                    error=abs(action_jet(R,g,dR,rho)[0]-(A+(B-A)*theta))
                    maxerr=max(maxerr,error);maxratio=max(maxratio,error/bound if bound else 0.);checked+=1
                    if error>bound+1e-12:raise AssertionError('fixed-trace envelope violated')
            # Independent finite-difference of the SAME evaluator, not a proxy derivative.
            h=1e-4*R[0].real;x=.4*R[0].real
            f,df,ddf=action_jet(R,g,dR,x)
            fm=action_jet(R,g,dR,x-h)[0];fp=action_jet(R,g,dR,x+h)[0]
            dr1=abs((fp-fm)/(2*h)-df)/max(1.,abs(df))
            dr2=abs((fp-2*f+fm)/h**2-ddf)/max(1.,abs(ddf))
            traces[panels]=dict(R=R,g=g,dR=dR)
            rows.append(dict(branch=o['branch'],panels=int(panels),source_sha256=hashlib.sha256(raw).hexdigest(),
                action_units='Eh*a0',rho_units='a0',absolute_interpolation_research_budget=budget,
                intervals=len(mesh['interval_bounds']),withheld_comparisons=checked,
                max_observed_complex_error=maxerr,max_observed_error_over_analytic_bound=maxratio,
                max_interval_bound=max(mesh['interval_bounds']),first_derivative_fd_normalized_error=dr1,
                second_derivative_fd_normalized_error=dr2,
                curvature_global_bound=8*interpolation_bound(R,g,dR,0.,rho_max)/rho_max**2,
                domain_rho_max=rho_max,q_max=(rho_max/min(abs(R)))**2,
                precision='float64, no interval rounding',passed=True))
        low,high=traces['32'],traces['64']
        if not np.array_equal(low['R'],high['R'][::2]):raise AssertionError('shared knot mismatch')
        delta=abs(low['g']-high['g'][::2]);rows[-1]['coincident_node_gap_difference_max']=float(max(delta))
        rows[-1]['coincident_node_action_error_envelope']=gap_error_bound(low['R'],low['dR'],delta,.75*low['R'][0].real)
        rows[-1]['coincident_comparison_is_true_error_bound']=False
    # Symbolic independent validation.
    r,z=sy.symbols('r z',positive=True);K=(1-r*r/(z*z))**sy.Rational(-1,2)
    d1=r/z**2*(1-r*r/z**2)**sy.Rational(-3,2)
    d2=(1+2*r*r/z**2)/z**2*(1-r*r/z**2)**sy.Rational(-5,2)
    residuals=[str(sy.simplify(sy.diff(K,r)-d1)),str(sy.simplify(sy.diff(K,r,2)-d2))]
    assert residuals==['0','0']
    rng=np.random.default_rng(20260928);err=0.;ratio=0.;conserv=0.;tight=[]
    for _ in range(2000):
        p=rng.random(12);q=np.clip(p+rng.normal(0,.005,12),0,1)
        events=[(k%4,(k+1)%4,bool(k%3==0)) for k in range(12)]
        y=rng.random(4);y/=y.sum();w=rng.random(4)
        a=hybrid_telescope(p,q,events,y,w)
        err=max(err,abs(a['direct_difference']-sum(a['signed_contributions'])))
        ratio=max(ratio,abs(a['direct_difference'])/a['weighted_bound'] if a['weighted_bound'] else 0.)
        if abs(a['direct_difference'])>a['weighted_bound']+1e-13 or a['weighted_bound']>a['global_bound']+1e-13:conserv+=1
        tight.append(a['weighted_bound']/a['global_bound'])
    hist={}
    for workers in (16,32,60,64):
        n=max(24,2*workers);counts=[n//12+(i<n%12) for i in range(12)]
        hist[str(workers)]=dict(old_tasks=n,old_counts=counts,tv_from_uniform=sum(abs(x/n-1/12) for x in counts)/2,
                                comparable_proposed_tasks=132,comparable_counts=[11]*12)
    output=dict(node='SHARED_C64_R2',scope='FIXED_DISCRETE_TRACE_ANALYSIS_AND_TOY_OPERATORS',
        python=platform.python_version(),numpy=np.__version__,sympy=sy.__version__,
        source_trace_files=7,analyzed_traces=14,new_spectral_solves=0,new_cloud_runs=0,
        tests=tests_not_run(),input_identity=input_receipt,
        symbolic_residuals=residuals,rows=rows,
        interpolation=dict(budget=budget,budget_kind='new absolute RESEARCH-only interpolation budget, not production tolerance',
            sampled_validation_points=sum(r['withheld_comparisons'] for r in rows),
            max_observed_error=max(r['max_observed_complex_error'] for r in rows),
            max_error_over_bound=max(r['max_observed_error_over_analytic_bound'] for r in rows),
            interval_range=[min(r['intervals'] for r in rows),max(r['intervals'] for r in rows)],
            interval_bound_scope='fixed trace, exact arithmetic; floating-point comparisons not interval certificates'),
        hybrid_telescope=dict(toy_chains=2000,events=12,max_identity_residual=err,violations=conserv,
            max_actual_to_weighted_bound=ratio,median_weighted_to_global_bound=float(np.median(tight)),atomic_data_used=False),
        benchmark_histogram_diagnostic=hist,
        transfer_claim='reuse the structural-validation/cached-evaluator method, never foreign physical matrices or claim gates',
        live_three_job_idle_status='USER_REPORTED_NOT_OBSERVED',PROMOTE='HOLD',Eq55='NOT_RUN')
    publish_json(args.out,output)
    print(json.dumps({k:output[k] for k in ('analyzed_traces','new_spectral_solves','interpolation','hybrid_telescope')},indent=2))

if __name__=='__main__':main()
