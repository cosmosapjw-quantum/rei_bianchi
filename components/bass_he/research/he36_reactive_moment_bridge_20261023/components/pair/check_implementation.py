"""New HE36 guard/algebra checks; no duplicated 6D quadrature or old suites."""
from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import resource
import sys
import time
import traceback

import numpy as np

import reactive_moments as rm


BASE = Path(__file__).resolve().parent
THETA_ONE_T = 1.0 / rm.K_B
ZERO = np.zeros((3, 3))
PI = np.array([[2.0, .4, -.3], [.4, -1.0, .2], [-.3, .2, -1.0]]) * .001


def close(actual, expected, rtol=3e-13, atol=0.):
    a, b = np.asarray(actual), np.asarray(expected)
    if not np.all(np.abs(a-b) <= atol + rtol*np.maximum(np.abs(a), np.abs(b))):
        raise AssertionError(f"mismatch {actual!r} != {expected!r}")


def rejected(call, exception=rm.MomentDomainError):
    try:
        call()
    except exception:
        return
    raise AssertionError(f"Expected {exception.__name__}")


def constant_moments(alpha=1.0):
    theta = rm.K_B*THETA_ONE_T
    return rm.RawMoments(alpha, 1.5*theta*alpha, 3.75*theta*theta*alpha,
                         provenance="manufactured constant K", temperature_K=THETA_ONE_T)


def call_pair(moments=None, **changes):
    args = dict(na=2.0, nb=3.0, ma=5.0, mb=7.0, T=THETA_ONE_T,
                pi_a=PI, pi_b=-2*PI, moments=moments or constant_moments(), linear_response=True)
    args.update(changes)
    return rm.binary_loss(**args)


def immutable_values():
    m = constant_moments()
    rejected(lambda: setattr(m, "alpha", 2.0), dataclasses.FrozenInstanceError)
    result = call_pair()
    for array in (result.J_a, result.J_b, result.S_a, result.S_b,
                  result.loss_block, result.coefficient_block):
        rejected(lambda a=array: a.setflags(write=True), ValueError)
    original = PI.copy()
    call_pair(pi_a=original)
    assert np.array_equal(original, PI)
    return {"immutable_moments": True, "immutable_output_arrays": 6, "caller_input_unchanged": True}


def moment_domain():
    bad = [(0, 1, 1), (1, 0, 1), (1, 1, 0), (-1, 1, 1),
           (1, -1, 1), (1, 1, -1), (1, 2, 1), (math.inf, 1, 1),
           (1, math.nan, 1), (True, 1, 1)]
    for row in bad:
        rejected(lambda row=row: rm.RawMoments(*row))
    rejected(lambda: rm.RawMoments(0, 0, 0))
    rejected(lambda: rm.RawMoments(1, 1, 1, unit_system="cgs"))
    rejected(lambda: rm.RawMoments(1, 1, 1, zero_reason="zero"))
    rejected(lambda: constant_moments().coefficients(2*THETA_ONE_T))
    # A roundoff-sized violation is recorded unchanged, never projected.
    g = math.nextafter(1.0, 0.0)
    m = rm.RawMoments(1.0, 1.0, g)
    assert m.gamma == g and m.cauchy_normalized_defect > 0
    return {"rejected_cases": len(bad)+4, "unrepaired_roundoff_defect": m.cauchy_normalized_defect}


def exponent_safety():
    # Raw alpha*gamma and beta^2 would underflow or overflow in these cases.
    rows = []
    for alpha, density in ((1e-250, 1e100), (1e250, 1e-100)):
        m = rm.RawMoments(alpha, alpha, alpha, provenance="manufactured monoenergy moments")
        out = call_pair(m, na=density, nb=density, ma=1e308, mb=1e308,
                        pi_a=PI*density, pi_b=-PI*density)
        expected = -float(density)*float(alpha)*float(density)
        close(out.Rn_a, expected, rtol=4e-15)
        close((out.mass_fraction_a, out.mass_fraction_b), (.5, .5), rtol=0)
        assert all(math.isfinite(v) and v > 0 for v in out.loss_eigenvalues)
        rows.append({"alpha":alpha,"density":density,"number_source":out.Rn_a,
                     "eigenvalues":out.loss_eigenvalues,"cauchy_defect":m.cauchy_normalized_defect})
    rejected(lambda: rm.mass_fractions(5e-324, 1e308), rm.MomentRepresentabilityError)
    # theta^2 alone underflows, whereas gamma/theta^2 is representable.
    T = 1e-160/rm.K_B
    small = rm.RawMoments(1e300, 1e140, 1e-20)
    k = small.coefficients(T)
    close(k.k1, (2/3)*1e300, rtol=4e-15)
    close(k.k2, (4/15)*1e300, rtol=4e-15)
    # A real nonzero underflow and real overflow raise; neither becomes zero.
    rejected(lambda: call_pair(rm.RawMoments(1e-300, 1e-300, 1e-300),
                              na=1e-100, nb=1e-100, pi_a=ZERO, pi_b=ZERO),
             rm.MomentRepresentabilityError)
    rejected(lambda: call_pair(na=1e300, nb=1e300, pi_a=ZERO, pi_b=ZERO),
             rm.MomentRepresentabilityError)
    return {"wide_exponents":rows,"theta_squared_not_formed":True,"true_unrepresentable_cases_rejected":3}


def explicit_zero_and_absent_species():
    zero = rm.RawMoments(0, 0, 0, zero_reason="declared physical zero kernel")
    result = call_pair(zero)
    assert result.Rn_a == result.Q_a == result.Q_b == 0
    assert np.all(result.S_a == 0) and np.all(result.S_b == 0)
    assert result.loss_eigenvalues == (0.0, 0.0)
    result = call_pair(na=0, pi_a=ZERO)
    assert result.Rn_a == result.Q_a == result.Q_b == 0
    assert np.all(result.S_a == 0) and np.all(result.S_b == 0)
    assert result.relative_anisotropy_a == 0
    rejected(lambda: call_pair(na=0, pi_a=PI))
    rejected(lambda: call_pair(nb=0, pi_b=PI))
    return {"zero_and_boundary_sources_zero":True,"absent_nonzero_tensors_rejected":2,
            "boundary_spectrum_is_algebraic_only":result.loss_eigenvalues}


def tensor_and_contract_guards():
    nonsymmetric = PI.copy(); nonsymmetric[0, 1] += .1
    bad = [dict(pi_a=np.eye(3)), dict(pi_a=nonsymmetric), dict(pi_a=np.ones((2, 2))),
           dict(pi_a=PI.astype(complex)+1j*np.eye(3)), dict(pi_a=np.ones((3, 3),dtype=bool)),
           dict(pi_b=np.full((3,3),math.inf)), dict(na=-1), dict(nb=True),
           dict(ma=0), dict(mb=math.inf), dict(T=0), dict(linear_response=False),
           dict(grad_budget=1e-8), dict(grad_budget=-1)]
    for row in bad:
        rejected(lambda row=row: call_pair(**row))
    # Accept roundoff residual but do not alter the supplied direction.
    residual_pi = PI.copy(); residual_pi[0, 0] += 1e-18
    output = call_pair(pi_a=residual_pi, grad_budget=.1)
    assert output.tensor_residuals[1] > 0
    assert "not_truncation_error_bound" in output.grad_budget_interpretation
    return {"rejected_cases":len(bad),"normalized_trace_residual_preserved":output.tensor_residuals[1],
            "relative_anisotropy":(output.relative_anisotropy_a,output.relative_anisotropy_b)}


def constant_kernel_tensor_removal():
    out = call_pair()
    theta = out.radial_coefficients.theta
    close(out.J_a, -3*PI, atol=1e-17)
    close(out.J_b, -2*(-2*PI), atol=1e-17)
    close(out.Q_a, -1.5*2*3*theta)
    close(out.Q_b, -1.5*2*3*theta)
    close(out.S_a, -3*(2*theta*np.eye(3)+PI), atol=1e-15)
    close(out.S_b, -2*(3*theta*np.eye(3)-2*PI), atol=1e-15)
    close(out.loss_eigenvalues, (2,3), rtol=8e-15)
    return {"number":out.Rn_a,"Q_a":out.Q_a,"Q_b":out.Q_b,
            "coefficient_block":out.coefficient_block.tolist(),"eigenvalues":out.loss_eigenvalues}


def signed_cross_coupling_and_dissipation():
    theta = rm.K_B*THETA_ONE_T
    m = rm.RawMoments(1, 2*theta, 6*theta*theta, provenance="K proportional sqrt(E)")
    out = call_pair(m, na=1, nb=1, ma=1, mb=1)
    close(out.coefficient_block, [[79/60,-1/60],[-1/60,79/60]], rtol=6e-15)
    close(out.loss_eigenvalues, (13/10,4/3), rtol=6e-15)
    assert out.coefficient_block[0,1] < 0
    frozen_derivative = 2*float(np.sum(PI*out.J_a)+np.sum((-2*PI)*out.J_b))
    assert frozen_derivative < 0
    return {"cross_coefficient":float(out.coefficient_block[0,1]),
            "positive_loss_eigenvalues":out.loss_eigenvalues,"frozen_quadratic_derivative":frozen_derivative}


def number_heat_do_not_determine_stf():
    theta = rm.K_B*THETA_ONE_T
    one = rm.RawMoments(1,1.5*theta,3.75*theta*theta,provenance="K1 Eq9")
    two = rm.RawMoments(1,1.5*theta,6.75*theta*theta,provenance="K2 Eq9 nonnegative polynomial")
    a = call_pair(one,na=1,nb=1,ma=1,mb=1)
    b = call_pair(two,na=1,nb=1,ma=1,mb=1)
    assert a.Rn_a == b.Rn_a and a.Q_a == b.Q_a and a.Q_b == b.Q_b
    close(b.radial_coefficients.k2/a.radial_coefficients.k2,9/5)
    close(a.loss_eigenvalues,(1,1));close(b.loss_eigenvalues,(1,7/5))
    assert np.max(np.abs(a.J_a-b.J_a)) > 1e-5
    return {"common_number_source":a.Rn_a,"common_Q_a":a.Q_a,
            "k2_ratio":b.radial_coefficients.k2/a.radial_coefficients.k2,
            "first_eigenvalues":a.loss_eigenvalues,"second_eigenvalues":b.loss_eigenvalues}


def derivative_adapter():
    theta = rm.K_B*THETA_ONE_T
    out = rm.moments_from_rate_derivatives(THETA_ONE_T,1.,2.,2.,
           kernel_temperature_independent=True,differentiation_justified=True,
           provenance="manufactured exact alpha proportional T^2")
    close(out.beta,3.5*theta);close(out.gamma,15.75*theta*theta)
    assert out.interpretation == "conditional_rate_fit_derivative"
    rejected(lambda: rm.moments_from_rate_derivatives(1.,1.,0.,0.,kernel_temperature_independent=False,differentiation_justified=True))
    rejected(lambda: rm.moments_from_rate_derivatives(1.,1.,0.,0.,kernel_temperature_independent=True,differentiation_justified=False))
    rejected(lambda: rm.moments_from_rate_derivatives(1.,1.,-10.,0.,kernel_temperature_independent=True,differentiation_justified=True))
    return {"beta":out.beta,"gamma":out.gamma,"interpretation":out.interpretation,
            "ordinary_second_derivative_distinguished_from_log_second_derivative":True}


def reactive_frame_one_step():
    mass,n,Rn,h=2.0,5.0,.7,.125
    u=np.array([.3,-.2,.5]);F=np.array([.8,-.4,.6])
    P=np.array([[3.,.1,-.2],[.1,4.,.3],[-.2,.3,5.]])
    R2=np.array([[.9,.1,.2],[.1,.4,-.05],[.2,-.05,.6]])
    C=rm.centralize_reactive_source(mass,Rn,F,R2,u)
    momentum=mass*n*u
    raw=P+mass*n*np.outer(u,u)
    next_n=n+h*Rn
    next_momentum=momentum+h*F
    next_raw=raw+h*R2
    next_pressure=next_raw-np.outer(next_momentum,next_momentum)/(mass*next_n)
    drift=F-mass*Rn*u
    direct_derivative=(next_pressure-P)/h+h*np.outer(drift,drift)/(mass*next_n)
    close(C,direct_derivative,rtol=3e-13,atol=4e-15)
    v=np.array([.4,.1,-.2])
    boosted_F=F+mass*Rn*v
    boosted_R2=R2+np.outer(v,F)+np.outer(F,v)+mass*Rn*np.outer(v,v)
    boosted=rm.centralize_reactive_source(mass,Rn,boosted_F,boosted_R2,u+v)
    close(C,boosted,rtol=3e-13,atol=4e-15)
    omitted_number_term=R2-np.outer(u,F)-np.outer(F,u)
    error=float(np.max(np.abs(C-omitted_number_term)))
    assert error>.1
    rejected(lambda: rm.centralize_reactive_source(mass,Rn,np.ones(2),R2,u))
    return {"max_one_step_algebra_difference":float(np.max(np.abs(C-direct_derivative))),
            "max_boost_difference":float(np.max(np.abs(C-boosted))),
            "omitted_number_term_mutant_error":error,"one_step_h":h}


def main():
    tag=time.strftime("attempt_%Y%m%dT%H%M%SZ",time.gmtime())
    directory=BASE/'attempts'/tag
    directory.mkdir(parents=True,exist_ok=False)
    files=[Path(__file__),BASE/'reactive_moments.py']
    code={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    start, cpu=time.perf_counter(),time.process_time()
    checks=[]
    for test in [immutable_values,moment_domain,exponent_safety,explicit_zero_and_absent_species,
                 tensor_and_contract_guards,constant_kernel_tensor_removal,
                 signed_cross_coupling_and_dissipation,number_heat_do_not_determine_stf,
                 derivative_adapter,reactive_frame_one_step]:
        try:
            result=test();checks.append({'name':test.__name__,'status':'PASS','result':result})
        except Exception:
            checks.append({'name':test.__name__,'status':'FAIL','traceback':traceback.format_exc()})
    failed=sum(x['status']=='FAIL' for x in checks)
    record={'schema':'he36.incoming_implementation_checks.v1','status':'PASS_SCOPED' if not failed else 'FAIL_PRESERVED',
            'checks':checks,'groups':len(checks),'passed':len(checks)-failed,'failed':failed,'source_sha256':code,
            'command':'python /tmp/he36_pair_implementation/check_implementation.py',
            'scope':'New guard/algebra/one-step-source checks only; independent 6D oracle owned separately',
            'environment':{'python':sys.version,'numpy':np.__version__,'platform':platform.platform()},
            'wall_s_after_imports':time.perf_counter()-start,'cpu_s_after_imports':time.process_time()-cpu,
            'process_peak_RSS_KiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            'IVP':0,'old_suite_replay':0,'render':0,'benchmark':0,'exit_code':1 if failed else 0}
    (directory/'RESULT.json').write_text(json.dumps(record,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'directory':str(directory),'passed':record['passed'],'failed':failed,'source_sha256':code}))
    for row in checks:
        if row['status']=='FAIL':print(row['name'],row['traceback'])
    raise SystemExit(record['exit_code'])


if __name__=='__main__':main()
