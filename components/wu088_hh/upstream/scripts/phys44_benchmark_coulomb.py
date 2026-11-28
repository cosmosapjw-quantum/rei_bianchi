#!/usr/bin/env python3
"""Matched 21-mode finite-radius Coulomb reference benchmark, no solver speed claim."""
from __future__ import annotations

import argparse,json,time
from pathlib import Path
import mpmath as mp

from wu088_hh.phys44_boundary import outward_coulomb_reference


def naive_21(dps:int)->list:
    with mp.workdps(dps):
        eta=-mp.mpf(10)/7
        rho=mp.mpf(14)
        k=mp.mpf(7)/10
        z=[]
        for ell in range(21):
            def h(r):
                return mp.coulombg(ell,eta,r)+1j*mp.coulombf(ell,eta,r)
            v=h(rho)
            d=mp.diff(h,rho)
            z.append(k*d/v)
        return z


def benchmark(dps:int=50)->dict:
    if dps<36 or dps>90:
        raise ValueError("bounded high-precision benchmark")
    a=time.perf_counter()
    optimized=outward_coulomb_reference(dps=dps,workers=1)
    t_optimized=time.perf_counter()-a
    b=time.perf_counter()
    baseline=naive_21(dps)
    t_baseline=time.perf_counter()-b
    with mp.workdps(dps):
        errors=[]
        for ell,ref in enumerate(optimized):
            x=mp.mpc(ref["outgoing_z_re_per_a0"],ref["outgoing_z_im_per_a0"])
            errors.append(abs(x-baseline[ell]))
        max_err=max(errors)
    # The serialized optimized reference intentionally publishes only
    # min(dps-12,42) significant decimal digits. Compare at that explicit
    # representation precision, NOT an impossible dps-10 threshold.
    printed=min(dps-12,42)
    print_floor=mp.mpf(10)**(-(printed-2))
    return {
        "schema":"WU088_HH_PHYS44_COULOMB_21_MODE_HIGH_PRECISION_BENCH_V1",
        "dps":dps,"radius_a0":"20","ell_count":21,
        "optimized_cached_neighbor_recurrence_wall_s":t_optimized,
        "independent_naive_mp_diff_wall_s":t_baseline,
        "naive_over_optimized_wall_ratio":t_baseline/t_optimized,
        "max_complex_log_derivative_abs_difference":mp.nstr(max_err,24),
        "published_significant_digits":printed,
        "representation_parity_upper":mp.nstr(print_floor,12),
        "same_21_physical_Coulomb_reference":max_err < print_floor,
        "benchmark_scope":"only 21-mode Coulomb special-function evaluation, not original scattering solver or REI ODE"
    }


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--dps",type=int,default=50)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    d=benchmark(a.dps)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(d,indent=2)+"\n")
    print(json.dumps(d))
    if not d["same_21_physical_Coulomb_reference"]:
        raise RuntimeError("baseline Coulomb reference mismatch")

if __name__=="__main__":main()
