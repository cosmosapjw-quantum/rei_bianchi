"""Independent finite control of the analytic HE34 reduction bounds.

No HE32 or HE33 IVP is rerun. The physical coefficient is the declared
piecewise-linear S(N) interpolant; chi is prescribed, not a transport fit.
"""
import json
import math
import numpy as np
from scipy.integrate import solve_ivp, quad


def root(s, chi):
    d = math.hypot(chi + 2*s, math.sqrt(32)*s)
    return -4*s/(chi + 2*s + d), d


def max_t_exp(rate, width):
    return width*math.exp(-rate*width) if rate*width <= 1 else 1/(rate*math.e)


def interval(sa, sb, chi, h, rleft, eleft, lleft):
    sm = max(abs(sa), abs(sb))
    ls = abs(sb-sa)/h
    kappa = chi-6*sm
    assert kappa > 0
    dmin = chi-2*sm
    bbound = 2*sm/dmin
    ba, d0 = root(sa, chi)
    delta0 = rleft-ba
    c = 4*sa*delta0/d0
    denominator_min = min(1., 1.-c)
    assert denominator_min > 0
    amplitude = abs(delta0)/denominator_min
    assert bbound+amplitude <= .5
    rb = min(2.25, 2+2*bbound+4*bbound**2)*ls/dmin
    ld = (2*chi+36*sm)*ls/dmin
    residual = rb+ld*amplitude*max_t_exp(d0,h)+4*ls*amplitude**2*max_t_exp(2*d0,h)
    gap = -math.expm1(-kappa*h)
    m0 = gap/kappa
    eend = (1-gap)*eleft+residual/kappa*gap
    eint = eleft*m0+residual/kappa*(h-m0)
    lend = lleft+4*sm*eint

    def delta(tau):
        ex = math.exp(-d0*tau)
        return delta0*ex/(1+c*math.expm1(-d0*tau))

    def approx(tau):
        return root(sa+(sb-sa)*tau/h, chi)[0]+delta(tau)

    def bound(tau):
        g = -math.expm1(-kappa*tau)
        return (1-g)*eleft+(residual/kappa)*g

    def logpressure_increment():
        # Root integral rationalized: -4 S b = 16 S^2/(chi+2S+D).
        def base(tau):
            ss=sa+(sb-sa)*tau/h
            dd=root(ss,chi)[1]
            return 16*ss*ss/(chi+2*ss+dd)
        qb, qb_err=quad(base,0,h,epsabs=1e-14,epsrel=1e-13)
        cap=min(d0*h,48.)
        def layer(x):
            ss=sa+(sb-sa)*x/(d0*h)
            de=delta0*math.exp(-x)/(1+c*math.expm1(-x))
            return -4*ss*de/d0
        ql,ql_err=quad(layer,0,cap,epsabs=1e-14,epsrel=1e-13)
        tail=4*sm*amplitude*math.exp(-cap)/d0 if cap<d0*h else 0.
        return qb+ql, qb_err+ql_err, tail

    ui, quadrature_estimate, tail_bound=logpressure_increment()
    return approx,bound,eend,lend,ui,{
        "ratio_endpoint_envelope":eend,"logpressure_envelope":lend,
        "residual_bound":residual,"kappa":kappa,
        "cone_sufficient_bound":bbound+amplitude,
        "quadrature_error_estimate":quadrature_estimate,
        "omitted_layer_tail_bound":tail_bound,
    }


def control(chi,shape):
    nodes=np.linspace(0,2,21)
    ss=.12+.04*np.sin(nodes) if shape=="positive" else .2*np.cos(2*nodes)
    rr=0.; uu=0.; ar=0.; au=0.; ee=0.; ll=0.
    max_ratio_error=0.; max_bound_ratio=0.; max_logpressure_error=0.
    max_residual_ratio=0.; nfev=0; estimates=0.; tails=0.; checkpoints=[]
    for j in range(len(nodes)-1):
        h=nodes[j+1]-nodes[j]
        sa=float(ss[j]);sb=float(ss[j+1])
        af,bf,en,ln,ui,record=interval(sa,sb,chi,h,ar,ee,ll)
        def fun(t,y):
            s=sa+(sb-sa)*t/h
            return [4*s*y[0]**2-(chi+2*s)*y[0]-2*s,-4*s*y[0]]
        def jac(t,y):
            s=sa+(sb-sa)*t/h
            return [[8*s*y[0]-chi-2*s,0],[-4*s,0]]
        sol=solve_ivp(fun,[0,h],[rr,uu],method="Radau",rtol=1e-11,atol=1e-13,jac=jac,dense_output=True)
        assert sol.success
        nfev+=sol.nfev
        for t in np.linspace(0,h,101):
            err=abs(float(sol.sol(t)[0])-af(float(t)))
            bd=bf(float(t))
            max_ratio_error=max(max_ratio_error,err)
            max_bound_ratio=max(max_bound_ratio,bd)
            if bd>1e-14: max_residual_ratio=max(max_residual_ratio,err/bd)
            assert err <= bd+5e-12, (j,t,err,bd)
        rr,uu=map(float,sol.y[:,-1])
        ar=af(h);au+=ui;ee=en;ll=ln
        lerr=abs(uu-au)
        max_logpressure_error=max(max_logpressure_error,lerr)
        estimates+=record["quadrature_error_estimate"]
        tails+=record["omitted_layer_tail_bound"]
        assert lerr <= ll+5e-12
        checkpoints.append({"N":float(nodes[j+1]),"ratio_reference":rr,"ratio_approx":ar,"ratio_error":abs(rr-ar),"ratio_bound":ee,"logpressure_error":lerr,"logpressure_bound":ll})
    return {"chi":chi,"shape":shape,"N_end":2.,"intervals":20,
       "r0":0.,"max_ratio_error":max_ratio_error,"max_ratio_envelope":max_bound_ratio,
       "max_ratio_error_to_envelope":max_residual_ratio,
       "max_logpressure_error_at_knots":max_logpressure_error,"logpressure_envelope_final":ll,
       "target":1e-6,"analytic_envelopes_meet_target":bool(max_bound_ratio<=1e-6 and ll<=1e-6),
       "reference_Radau_nfev":nfev,"numerical_quad_error_estimate":estimates,
       "analytic_omitted_initial_layer_tail_bound":tails,"checkpoints":checkpoints}


if __name__=="__main__":
    results=[control(chi,shape) for shape in ["positive","sign_change"] for chi in [10.,100.,1000.,10000.]]
    result={"schema":"he34.independent_reduction_control.v1","scope":"new synthetic mechanical coefficient controls only","reference":"scipy Radau rtol=1e-11 atol=1e-13, analytic Jacobian, one solve per coefficient interval","status":"pass_scoped","runs":results,"qualification":"Analytic envelopes are proved in THEORY.md; numerical reference and quadrature comparisons corroborate at finite sampled points, not a floating-point proof."}
    with open("/tmp/he34_reduction_theory/CONTROL_RESULTS.json","w") as f: json.dump(result,f,indent=2)
    print(json.dumps([{k:v for k,v in x.items() if k!="checkpoints"} for x in results],indent=2))
