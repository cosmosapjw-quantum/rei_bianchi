"""One bounded affected-scope check; no IVP, renderer or benchmark dispatch."""
from __future__ import annotations

import argparse
import datetime as dt
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
import warnings

import mpmath as mp
import numpy as np
import scipy
from scipy.integrate import quad, IntegrationWarning

from maxwellian_moments import PreparedMaxwellianMoments, ME_KG, A0_M

mp.mp.dps = 80

SOURCE_SHA = "7a87a2c9f2116ee36c0786b379dac08e1f4d92a49504fe542e6aa71cbb279bae"
GROUPS = ("constant_band_oracle", "temperature_derivative_oracle",
          "ccc_gl_quad_witness", "mass_and_linear_scaling", "bin_partition",
          "domain_guards", "underflow_and_zero", "immutability_and_identity")


def parse_ccc(path):
    raw = Path(path).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SOURCE_SHA
    rows = []
    for line in raw.decode().splitlines():
        fields = line.split()
        if fields and not fields[0].startswith("#"):
            rows.append((float(fields[0]), float(fields[1])))
    values = np.asarray(rows)
    assert values.shape == (87, 2)
    assert tuple(values[0]) == (13.6058, 0.0)
    assert values[-1, 0] == 968.61
    return values[:, 0], values[:, 1] * (5.29177210544e-11)**2


def relative(actual, expected):
    return np.abs(np.asarray(actual) / np.asarray(expected) - 1.0)


def finite_constant_oracle(temperature, mass, lower=0.25, upper=8.0, sigma=3e-20):
    # Independent SI-energy incomplete-gamma antiderivative, 80 decimal digits.
    ev = mp.mpf("1.602176634e-19")
    kb = mp.mpf("1.380649e-23")
    theta = kb * mp.mpf(temperature)
    mu = mp.mpf(mass)
    pre = mp.sqrt(8/(mp.pi*mu)) / theta**mp.mpf("1.5")
    return [pre * mp.mpf(sigma) * theta**(j+2)
            * mp.gammainc(j+2, mp.mpf(lower)*ev/theta, mp.mpf(upper)*ev/theta)
            for j in range(4)]


def make_constant(mass=ME_KG):
    e = np.array([0.25, 0.5, 0.75, 1., 1.5, 2., 4., 8.])
    return PreparedMaxwellianMoments(e, np.full(len(e), 3e-20), 0.0,
                                    "manufactured constant finite band", mass)


def constant_band_oracle(_energy, _sigma):
    temperatures = np.array([2000., 10000., 200000.])
    comparisons = []
    for mass in (ME_KG, ME_KG/2, 1.67262192595e-27):
        result = make_constant(mass).evaluate(temperatures)
        expected = np.array([[float(x) for x in finite_constant_oracle(t, mass)]
                             for t in temperatures])
        err = relative(result.moments_SI, expected)
        assert np.max(err) < 2e-9, err
        comparisons.append(dict(mass_kg=mass, max_relative=float(np.max(err)),
                                moments=result.moments_SI.tolist()))
    return dict(status="PASS", temperatures_K=temperatures.tolist(),
                gate_relative=2e-9, comparisons=comparisons,
                reference="independent80decimal SI incomplete-gamma integral")


def temperature_derivative_oracle(_energy, _sigma):
    kernel = make_constant()
    temperatures = [10000., 75000.]
    rows = []
    for temperature in temperatures:
        result = kernel.evaluate(temperature)
        independent = []
        for j in range(3):
            derivative = mp.diff(lambda logt: finite_constant_oracle(mp.exp(logt), ME_KG)[j],
                                 mp.log(mp.mpf(temperature)))
            independent.append(float(derivative))
        err = relative(result.dlogT_moments_SI[0], independent)
        assert np.max(err) < 2e-9, err
        # Deliberately wrong Maxwellian prefactor derivative must be distinguishable.
        wrong = result.dlogT_moments_SI[0] + 1.5*result.moments_SI[0, :3]
        mutation = relative(wrong, independent)
        assert np.max(mutation) > 1e-2
        rows.append(dict(T_K=temperature, dlogT_SI=result.dlogT_moments_SI[0].tolist(),
                         reference_SI=independent, max_relative=float(np.max(err)),
                         omitted_prefactor_mutation_max_relative=float(np.max(mutation))))
    return dict(status="PASS", gate_relative=2e-9, rows=rows,
                reference="80decimal differentiation of independentSI antiderivative")


def quad_witness(energy, sigma, temperature):
    # This witness directly uses J-energy, independent endpoint slopes, QUADPACK.
    ev, kb, mass = 1.602176634e-19, 1.380649e-23, 9.1093837139e-31
    energy_J = energy * ev
    theta = kb*temperature
    anchor = energy_J[0]
    pre = math.sqrt(8/(math.pi*mass)) / theta**1.5 * math.exp(-anchor/theta)
    outputs, errors, counts = [], [], []
    with warnings.catch_warnings():
        warnings.simplefilter("error", IntegrationWarning)
        for j in range(4):
            total, error, calls = 0., 0., 0
            for i in range(len(energy)-1):
                left, right = energy_J[i:i+2]
                slope = (sigma[i+1]-sigma[i])/(right-left)
                def integrand(energy_arg):
                    return (energy_arg**(j+1) * (sigma[i]+slope*(energy_arg-left))
                            * math.exp(-(energy_arg-anchor)/theta))
                value, estimate, info = quad(integrand, left, right, epsabs=0.,
                                            epsrel=4e-12, limit=100, full_output=1)
                total += value
                error += estimate
                calls += info["neval"]
            outputs.append(pre*total)
            errors.append(pre*error)
            counts.append(calls)
    return np.array(outputs), np.array(errors), counts


def ccc_gl_quad_witness(energy, sigma):
    temps = np.array([2000., 3000., 5000., 10000., 20000., 40000., 75000., 100000., 200000.])
    common = dict(energy_eV=energy, sigma_m2=sigma, threshold_eV=13.6058,
                  source_id="CCC87:"+SOURCE_SHA, energy_mapping="heavy_fixed_target_incident_electron")
    first = PreparedMaxwellianMoments(**common, quadrature_order=16).evaluate(temps)
    second = PreparedMaxwellianMoments(**common, quadrature_order=32).evaluate(temps)
    err = relative(first.moments_SI, second.moments_SI)
    assert np.max(err) < 2e-9, err
    witnesses = []
    for index in (0, 4, 8):
        value, estimate, calls = quad_witness(energy, sigma, temps[index])
        err_quad = relative(first.moments_SI[index], value)
        assert np.max(err_quad) < 2e-9, err_quad
        witnesses.append(dict(T_K=float(temps[index]), quad_SI=value.tolist(),
            estimated_abs_error_SI=estimate.tolist(), quad_function_calls_by_moment=calls,
            max_relative_GL16_quad=float(np.max(err_quad))))
    mean = first.conditional_mean_energy_J / 1.602176634e-19
    assert np.all(mean >= energy[0]) and np.all(mean <= energy[-1])
    variance_scale = first.gamma_J2_m3_s/first.alpha_m3_s/(
        first.beta_J_m3_s/first.alpha_m3_s)**2 - 1
    assert np.min(variance_scale) >= -1e-12
    # Scalar/batched order and repeated-temperature semantics, no cache interpolation.
    scalar = PreparedMaxwellianMoments(**common).evaluate([10000.]).moments_SI[0]
    scalar_batch_error = float(np.max(relative(scalar, first.moments_SI[3])))
    assert scalar_batch_error < 3e-13
    return dict(status="PASS", temperatures_K=temps.tolist(), gate_relative=2e-9,
        GL16_SI=first.moments_SI.tolist(), GL32_SI=second.moments_SI.tolist(),
        dlogT_SI=first.dlogT_moments_SI.tolist(), log_moments=first.log_moments_SI.tolist(),
        mean_energy_eV=mean.tolist(), min_weighted_variance_ratio=float(np.min(variance_scale)),
        max_relative_GL16_GL32=float(np.max(err)), scalar_batch_relative=scalar_batch_error, quad=witnesses,
        coverage=PreparedMaxwellianMoments(**common).coverage(), old_science_replay=0)


def mass_and_linear_scaling(_energy, _sigma):
    temps = [2000., 10000., 200000.]
    first = make_constant().evaluate(temps)
    other = make_constant(9*ME_KG).evaluate(temps)
    mass_error = float(np.max(relative(other.moments_SI, first.moments_SI/3)))
    assert mass_error < 2e-13
    e, sigma = np.array([0.1, 0.5, 1., 4.]), np.array([0., 3e-21, 1e-20, 2e-21])
    base = PreparedMaxwellianMoments(e, sigma, .1, "scaling witness").evaluate(temps)
    scaled = PreparedMaxwellianMoments(e, 7*sigma, .1, "scaling witness").evaluate(temps)
    scale_error = float(np.max(relative(scaled.moments_SI, 7*base.moments_SI)))
    assert scale_error < 2e-13
    return dict(status="PASS", mass_relative=mass_error, sigma_linear_relative=scale_error,
                reduced_mass_cases="manufactured only")


def bin_partition(_energy, _sigma):
    e = np.array([.25, .5, 1., 2., 4., 8.])
    s = np.array([0., 1., .3, .8, .4, 0.])*1e-20
    middle = (e[:-1]+e[1:])/2
    refined_e = np.sort(np.r_[e, middle])
    refined_s = np.interp(refined_e, e, s)
    a = PreparedMaxwellianMoments(e, s, .25, "partition coarse").evaluate([2000., 20000., 200000.])
    b = PreparedMaxwellianMoments(refined_e, refined_s, .25, "partition same function").evaluate([2000., 20000., 200000.])
    err = float(np.max(relative(a.moments_SI, b.moments_SI)))
    assert err < 2e-9
    return dict(status="PASS", relative=err, exact_model_unchanged=True, gate=2e-9)


def domain_guards(_energy, _sigma):
    rejected = []
    def reject(name, callback):
        try:
            callback()
        except (ValueError, FloatingPointError, OverflowError):
            rejected.append(name)
        else:
            raise AssertionError("failed to reject: "+name)
    for name, energy, sigma, threshold in [
        ("negative_sigma", [1., 2.], [-1., 1.], 1.),
        ("duplicate_energy", [1., 1.], [1., 2.], 1.),
        ("unordered_energy", [2., 1.], [1., 2.], 1.),
        ("nonfinite_energy", [1., np.inf], [1., 2.], 1.),
        ("nonfinite_sigma", [1., 2.], [1., np.nan], 1.),
        ("below_threshold", [1., 2.], [0., 1.], 1.1),
        ("negative_threshold", [1., 2.], [1., 2.], -1.),
        ("mismatched_arrays", [1., 2.], [1.], 1.),
        ("boolean_array", [True, False], [1., 2.], 0.)]:
        reject(name, lambda e=energy,s=sigma,t=threshold:PreparedMaxwellianMoments(e,s,t,"guard"))
    reject("zero_mass",lambda:PreparedMaxwellianMoments([1.,2.],[1.,2.],1.,"guard",0.))
    reject("unqualified_mass_mapping",lambda:PreparedMaxwellianMoments([1.,2.],[1.,2.],1.,"guard",2*ME_KG,"heavy_fixed_target_incident_electron"))
    reject("empty_source",lambda:PreparedMaxwellianMoments([1.,2.],[1.,2.],1.,""))
    reject("overflow_preparation",lambda:PreparedMaxwellianMoments([1e100,2e100],[1e200,2e200],1e100,"guard"))
    kernel = make_constant()
    for name, t in [("below_T",1999.),("above_T",200001.),("nan_T",np.nan),
                    ("bool_T",True),("complex_T",10000+0j),("empty_T",[])]:
        reject(name,lambda t=t:kernel.evaluate(t))
    reject("full_rate_claim",lambda:kernel.evaluate(10000.,require_full_physical_rate=True))
    reject("zero_batch",lambda:kernel.evaluate(10000.,batch_size=0))
    partial = PreparedMaxwellianMoments([2.,3.],[1e-20,1e-20],1.,"known missing lower gap")
    assert partial.coverage()["lower_gap_is_unmodeled"]
    return dict(status="PASS", rejected=rejected, count=len(rejected),
                lower_gap_never_zero_filled=True)


def underflow_and_zero(_energy, _sigma):
    kernel = PreparedMaxwellianMoments([100000.,100000.001], [1e-20,1e-20],
                                     100000., "manufactured underflow band")
    result = kernel.evaluate(2000.)
    assert np.all(result.moments_SI == 0) and np.all(result.underflow)
    assert np.isfinite(result.log_moments_SI).all()
    assert result.conditional_mean_energy_J[0] > 100000.*1.602176634e-19
    zero = PreparedMaxwellianMoments([1.,2.,3.], [0.,0.,0.], 1.,"zero table only").evaluate(10000.)
    assert zero.zero_tabulated_integral and np.all(zero.moments_SI == 0)
    assert not zero.underflow.any() and zero.conditional_mean_energy_J is None
    assert zero.logarithmic_slopes is None and zero.finite_source_partial
    return dict(status="PASS", log_moments_underflow=result.log_moments_SI.tolist(),
                underflow_is_not_physical_zero=True, all_zero_table_is_partial=True,
                underflow_case_accuracy_claim=False)


def immutability_and_identity(_energy, _sigma):
    energy = np.array([1.,2.]);sigma=np.array([0.,1e-20])
    kernel=PreparedMaxwellianMoments(energy,sigma,1.,"immutable")
    identity=kernel.identity;energy[1]=3.;sigma[1]=2e-20
    assert kernel.energy_eV[1] == 2. and kernel.sigma_m2[1] == 1e-20
    try:
        kernel.energy_eV.setflags(write=True)
    except ValueError:
        pass
    else:
        raise AssertionError("array became mutable")
    changed=PreparedMaxwellianMoments([1.,2.],[0.,1e-20],1.,"changed source")
    assert changed.identity != identity
    return dict(status="PASS", immutable_input_copy=True, source_identity_changes_hash=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument("--table",required=True)
    parser.add_argument("--output",required=True);parser.add_argument("--groups",nargs="+",choices=GROUPS,default=list(GROUPS))
    args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError("existing verification receipt cannot be overwritten")
    started=time.perf_counter();e,s=parse_ccc(args.table)
    record=dict(schema="he36.moment_checks.v1",started_utc=dt.datetime.now(dt.timezone.utc).isoformat(),
        Python=platform.python_version(),NumPy=np.__version__,SciPy=scipy.__version__,mpmath=mp.__version__,
        table_sha256=SOURCE_SHA,source_hashes={},groups=[],science_IVP_count=0,
        old_suite_replay=0,render_count=0,benchmark_count=0)
    for name in ("maxwellian_moments.py","check_moments.py"):
        record["source_hashes"][name]=hashlib.sha256((Path(__file__).parent/name).read_bytes()).hexdigest()
    for group in args.groups:
        try:
            result=globals()[group](e,s);record["groups"].append(dict(group=group,**result))
        except Exception as exc:
            record["groups"].append(dict(group=group,status="FAIL",error=str(exc),traceback=traceback.format_exc()))
    record["status"]="PASS" if all(x["status"]=="PASS" for x in record["groups"]) else "FAIL"
    record["elapsed_seconds"]=time.perf_counter()-started
    record["peak_rss_KiB"]=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    record["completed_utc"]=dt.datetime.now(dt.timezone.utc).isoformat()
    temporary=out.with_name(out.name+".tmp")
    with temporary.open("x") as f:
        json.dump(record,f,indent=2,allow_nan=False);f.write("\n");f.flush();os.fsync(f.fileno())
    os.link(temporary,out);temporary.unlink()
    print(json.dumps({"status":record["status"],"groups":[{"group":x["group"],"status":x["status"],"error":x.get("error")} for x in record["groups"]],"elapsed_seconds":record["elapsed_seconds"]}))
    return 0 if record["status"]=="PASS" else 1


if __name__ == "__main__":sys.exit(main())
