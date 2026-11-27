"""Independent exact-polynomial and original-full-state compact transport checks.

No benchmark is performed. The two physical parameter pairs each execute one
original and one compact full-window trajectory, at identical solver tolerances.
"""
from __future__ import annotations
import os
for name in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
             "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[name] = "1"
from fractions import Fraction as F
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import time

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT / "src"))
import compact_transport as compact
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from canonical_fv import CanonicalFVSpecies
from lrs_boltzmann import legendre_matrix


def add(a, b):
    out = [F(0)] * max(len(a), len(b))
    for i, x in enumerate(a): out[i] += x
    for i, x in enumerate(b): out[i] += x
    return out


def scale(a, value): return [x * value for x in a]


def mul(a, b):
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b): out[i+j] += x*y
    return out


def derivative(a): return [i*a[i] for i in range(1, len(a))]


def polys(n):
    p = [[F(1)], [F(0), F(1)]]
    for k in range(2, n+1):
        p.append(add(scale([F(0)] + p[-1], F(2*k-1, k)),
                     scale(p[-2], -F(k-1, k))))
    return p


def exact_forward_matrix(lmax, power):
    """Direct exact integration of P_l times original forward generator.

    This does not evaluate the implementation's adjoint coefficient formula.
    Boundary parity and monopole statements are checked on the full matrix.
    """
    p = polys(lmax)
    ans = []
    for ell in range(lmax+1):
        row = []
        for m in range(lmax+1):
            adv = mul([F(0), F(3), F(0), F(-3)], derivative(p[m]))
            redshift = mul([F(power), F(0), F(-3*power)], p[m])
            integrand = mul(p[ell], scale(add(adv, redshift), 2*m+1))
            row.append(sum((v / (k+1) for k,v in enumerate(integrand) if k%2 == 0), F(0)))
        ans.append(row)
    return ans


class ConstantElectrons:
    def __init__(self, ne): self.ne = ne
    def density(self, a): return self.ne


def reference(model, ne):
    return CanonicalFVSpecies(model.source, 2.7255, ellmax=model.ellmax,
        Sigma_ref=model.sigma/math.sqrt(2), orientation=0 if model.sigma == 0 else 1,
        kappa_gamma=model.ar, kappa_nu=model.ar,
        ne_source=None if ne == 0 else ConstantElectrons(ne),
        mass_fraction=model.fm, massive_A=model.am, mass_over_Tref=30.,
        radial_cells=24, angular_cells=12, subcell_gauss_order=3)


def project(full, ellmax):
    a = np.asarray(full)
    return np.r_[a[:3], a[4:].reshape(4, ellmax+1)[:, ::2].ravel()]


def ref_observables(ref, x, y):
    w = ref.fields(x, y)
    fac = compact.KAPPA_T * math.sqrt(6) / w["H"]**2
    pm = fac*w["Pi_matter_J_m3"]
    pg = fac*w["Pi_gamma_J_m3"]
    pn = fac*w["Pi_nu_J_m3"]
    return np.asarray([math.sqrt(6)*w["s"]/w["H"], pm, pg, pn,
                       abs(pm+pg+pn), w["H"]])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists(): raise FileExistsError(args.out)
    args.out.mkdir(parents=True)
    records = {"schema":"he32.compact.independent.v1",
        "tested_source_sha256":hashlib.sha256((UNIT/"src/compact_transport.py").read_bytes()).hexdigest(),
        "python":sys.version, "numpy":np.__version__, "scipy":scipy.__version__,
        "thresholds":{"original_matrix_abs":3e-12,"point_rhs_abs":2e-12,
                      "paired_state_abs":3e-10,"paired_observable_abs":3e-10,
                      "number_abs":5e-11,"brightness_sample_min":-1e-12},
        "rtol":3e-11, "atol":3e-13, "method":"DOP853",
        "benchmark_runs":0, "integration_attempts":0,
        "matrix_checks":[], "point_checks":[], "trajectory_pairs":[],
        "limits":["Parity is exact for the real finite operator. Original quadrature matrix has floating roundoff.",
                  "Sampled brightness positivity is not an angular continuum certificate.",
                  "Trajectory comparison is finite discretization parity, not global IVP or truncation accuracy."]}
    def save():
        (args.out/"INDEPENDENT_REVIEW.json").write_text(json.dumps(records, indent=2,
            default=lambda value: value.item() if isinstance(value,np.generic) else str(value))+"\n")
    save()
    for L in (2,8,16):
        for power in (3,4):
            exact = exact_forward_matrix(L, power)
            a = np.asarray([[float(v) for v in row] for row in exact])
            c = compact.even_operator(L,power)
            exact_even = np.array_equal(a[::2,::2], c)
            exact_cross_parity = all(exact[i][j] == 0 for i in range(L+1)
                                    for j in range(L+1) if (i-j)%2)
            monopole = [F(0)]*(L+1)
            if power == 4: monopole[2] = F(-2)
            old = legendre_matrix(L,power=power)
            delta = float(np.max(np.abs(a-old)))
            row = dict(L=L,power=power,exact_even_equal=exact_even,
                       exact_cross_parity_zero=exact_cross_parity,
                       exact_monopole=exact[0] == monopole,
                       maximum_original_quadrature_abs=delta,
                       immutable=not c.flags.writeable)
            row["pass"] = all((exact_even,exact_cross_parity,exact[0]==monopole,
                               delta <= records["thresholds"]["original_matrix_abs"],
                               not c.flags.writeable))
            records["matrix_checks"].append(row)
    # Both donor paths and both shear regimes are checked against independent
    # original RHS assembly at multiple off-trajectory states.
    for sigma,pm,pr in ((.003,.0003,-.001),(.6,0.,0.)):
        model = compact.CompactTransport(sigma,pm,pr)
        for ne in (0.,2e-5):
            ref = reference(model,ne)
            for x in (0.,.5,model.source.xmax):
                y = model.initial_state()
                y[0]=x; y[1]=.06*x; y[2]*=math.exp(-1.5*x)
                towers=y[3:].reshape(4,model.n)
                for k in range(4):
                    towers[k,1] += (k+1)*.002*x
                    towers[k,2] = (k-1.5)*.0003*x
                full=model.unpack_full(y)
                orig=ref.rhs(x,full)
                new=model.rhs(x,y,ne)
                error=float(np.max(np.abs(project(orig,8)-new)))
                odd=float(np.max(np.abs(orig[4:].reshape(4,9)[:,1::2])))
                records["point_checks"].append(dict(sigma=sigma,ne_cm3=ne,eta=x,
                    rhs_abs=error,original_odd_rhs_abs=odd,
                    compact_number_derivatives=[float(new[3+model.n]),float(new[3+3*model.n])],
                    pass_=error<=records["thresholds"]["point_rhs_abs"] and new[3+model.n]==0 and new[3+3*model.n]==0))
    # Count exact finite-volume moment calls made by one fresh RHS.
    model=compact.CompactTransport(.003,.0003,-.001)
    class CountingMoments:
        def __init__(self, wrapped): self.wrapped,self.calls=wrapped,0
        def moments(self,x,b): self.calls+=1; return self.wrapped.moments(x,b)
    counter=CountingMoments(model.moments);model.moments=counter
    model.rhs(0.,model.initial_state(),2e-5)
    records["moment_calls_per_rhs"]=counter.calls
    save()
    cases=[dict(id="weak_constant_electrons",sigma=.003,pm=.0003,pr=-.001,ne=2e-5),
           dict(id="strong_collisionless",sigma=.6,pm=0.,pr=0.,ne=0.)]
    for spec in cases:
        model=compact.CompactTransport(spec["sigma"],spec["pm"],spec["pr"])
        ref=reference(model,spec["ne"])
        grid=np.linspace(0.,model.source.xmax,121)
        initial_delta=float(np.max(np.abs(model.unpack_full(model.initial_state())-ref.initial_state())))
        start=time.monotonic();records["integration_attempts"]+=1;save()
        original=solve_ivp(ref.rhs,(0.,model.source.xmax),ref.initial_state(),
             t_eval=grid,method="DOP853",rtol=records["rtol"],atol=records["atol"])
        records["integration_attempts"]+=1;save()
        reduced=solve_ivp(lambda x,y:model.rhs(x,y,spec["ne"]),
             (0.,model.source.xmax),model.initial_state(),t_eval=grid,
             method="DOP853",rtol=records["rtol"],atol=records["atol"])
        elapsed=time.monotonic()-start
        if not original.success or not reduced.success:
            records["trajectory_pairs"].append(dict(spec=spec,pass_=False,
                 original_message=original.message,reduced_message=reduced.message));save()
            raise RuntimeError("paired integration failed")
        expanded=np.column_stack([model.unpack_full(v) for v in reduced.y.T])
        state_delta=float(np.max(np.abs(original.y-expanded)))
        original_obs=np.row_stack([ref_observables(ref,float(x),y) for x,y in zip(grid,original.y.T)])
        obs=[model.observables(float(x),y,spec["ne"]) for x,y in zip(grid,reduced.y.T)]
        reduced_obs=np.asarray([[o[k] for k in ("signed_Sigma","P_m","P_gamma","P_nu","Pi_total","H_per_s")] for o in obs])
        obs_delta=np.max(np.abs(original_obs-reduced_obs),axis=0)
        bright=min(model.brightness_min(y,angles=257) for y in reduced.y.T)
        number=max(max(abs(o[k]-1) for k in ("N_gamma_0","N_nu_0")) for o in obs)
        matter_number=np.asarray([o["matter_number_comoving"] for o in obs])
        matter_number_rel=float(np.max(np.abs(matter_number/matter_number[0]-1)))
        mincell=min(o["min_canonical_cell"] for o in obs)
        np.savez_compressed(args.out/(spec["id"]+".npz"),eta=grid,
            original=original.y,compact=reduced.y,original_observables=original_obs,
            compact_observables=reduced_obs)
        row=dict(spec=spec,initial_full_state_abs=initial_delta,
            full_state_abs=state_delta,observable_abs=obs_delta.tolist(),
            observable_order=["signed_Sigma","P_m","P_gamma","P_nu","Pi_total","H_per_s"],
            compact_photon_number_abs=number,compact_matter_number_rel=matter_number_rel,
            minimum_brightness_257_sampled_angles=bright,minimum_cell_population=mincell,
            original_nfev=original.nfev,compact_nfev=reduced.nfev,
            operational_elapsed_seconds_pair=elapsed,
            endpoint=obs[-1],global_error_bound=None)
        row["pass"]=(initial_delta<=1e-15 and state_delta<=records["thresholds"]["paired_state_abs"]
            and float(np.max(obs_delta))<=records["thresholds"]["paired_observable_abs"]
            and number<=records["thresholds"]["number_abs"] and matter_number_rel<=1e-12
            and bright>=records["thresholds"]["brightness_sample_min"] and mincell>=0)
        records["trajectory_pairs"].append(row);save()
    all_good=(all(x["pass"] for x in records["matrix_checks"])
          and all(x["pass_"] for x in records["point_checks"])
          and all(x["pass"] for x in records["trajectory_pairs"])
          and records["moment_calls_per_rhs"]==1)
    records["decision"]="PASS_SCOPED_COMPACT_OPTIMIZATION" if all_good else "FINDING_REQUIRES_REPAIR"
    records["source_hash_after"]=hashlib.sha256((UNIT/"src/compact_transport.py").read_bytes()).hexdigest()
    records["source_unchanged_during_checks"]=(records["source_hash_after"]==records["tested_source_sha256"])
    save()
    print(json.dumps({"decision":records["decision"],"integrations":records["integration_attempts"],
         "max_state_abs":max(x["full_state_abs"] for x in records["trajectory_pairs"]),
         "source_unchanged":records["source_unchanged_during_checks"]}))
    return 0 if all_good and records["source_unchanged_during_checks"] else 2


if __name__ == "__main__": raise SystemExit(main())
