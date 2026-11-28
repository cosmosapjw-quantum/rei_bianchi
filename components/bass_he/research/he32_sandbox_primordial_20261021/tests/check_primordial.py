"""Small algebraic checks of grouped primordial chemistry; no IVP/benchmark.

Independent full21 transition-flux assembly is compared with the grouped
generator.  The analytic electron-coupled9x9 Jacobian is checked by central
differences at interior states, avoiding a boundary/clipping oracle.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import tempfile

for key in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
            "NUMEXPR_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[key] = "1"

UNIT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT/"src"))
import numpy as np
import scipy
from primordial_network import PrimordialNetwork, NEUTRON_MEAN_LIFETIME_S, TRITIUM_HALF_LIFE_S


def atomic_json(path, payload):
    fd, name = tempfile.mkstemp(prefix="check_write_", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(payload, f, indent=2)
            f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(name, path)
        fd = os.open(path.parent, os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
    finally:
        if os.path.exists(name): os.unlink(name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)
    records = dict(schema="he32.primordial_algebraic_checks.v1", status="running",
        integration_attempts=0, benchmark_runs=0, python=sys.version,
        numpy=np.__version__, scipy=scipy.__version__, checks=[],
        files_sha256={name:hashlib.sha256((UNIT/name).read_bytes()).hexdigest()
            for name in ("src/primordial_network.py", "src/atomic_photo_rr.py",
                         "data/ATOMIC_PHOTO_RR.json", "data/ISOTOPE_SCENARIO.json",
                         "tests/check_primordial.py")},
        scope="Algebraic source/grouping/charge/weak/Jacobian checks only; no cosmological trajectory")
    output = args.out/"PRIMORDIAL_CHECKS.json"
    save = lambda: atomic_json(output, records)
    def check(name, passed, **details):
        records["checks"].append(dict(name=name, passed=bool(passed), **details))
        save()
    save()
    try:
        model = PrimordialNetwork()
        records["network_metadata"] = model.metadata
        f = np.array([.61, .39, .28, .45, .27, .16, .31, .23, .30])
        Y = model.abundance_per_H(f)
        expected = np.array([0., .61, .39,
            2.503248144e-5*.61, 2.503248144e-5*.39, 0., 0.,
            1.049996333e-5*.28, 1.049996333e-5*.45, 1.049996333e-5*.27,
            .0819407011917237*.28, .0819407011917237*.45, .0819407011917237*.27,
            1e-14*.16, 1e-14*.31, 1e-14*.23, 1e-14*.30,
            5.36802116e-10*.16, 5.36802116e-10*.31, 5.36802116e-10*.23, 5.36802116e-10*.30])
        lift_error = float(np.max(np.abs(Y-expected)))
        mass_fraction = float(4*np.sum(Y[10:13])/(model.species_A@Y))
        check("21-state lift and exact He4 mass convention", len(model.species_names)==21
              and len(model.nuclide_names)==8 and lift_error<2e-16
              and abs(mass_fraction-.2468382676)<2e-15,
              maximum_lift_absolute=lift_error, Y_He4=mass_fraction,
              nH0_m3=model.nH0_m3, species_names=list(model.species_names))

        mass22 = np.r_[model.species_A, 0]
        charge22 = np.r_[model.species_charge, -1]
        b_res = mass22@model.photo_stoichiometry22
        q_res = charge22@model.photo_stoichiometry22
        wb_res = mass22@model.weak_operator22_per_s
        wq_res = charge22@model.weak_operator22_per_s
        check("atomic and weak stoichiometric baryon and charge nullvectors",
            np.array_equal(b_res, np.zeros(13)) and np.array_equal(q_res, np.zeros(13))
            and np.max(np.abs(wb_res))<1e-20 and np.max(np.abs(wq_res))<1e-20,
            atomic_baryon_residual=b_res.tolist(), atomic_charge_residual=q_res.tolist(),
            weak_baryon_residual_max=float(np.max(np.abs(wb_res))),
            weak_charge_residual_max=float(np.max(np.abs(wq_res))))

        for a in (1/21., 1/9., 1/3.):
            nH = model.nH0_m3*1e-6/a**3
            independent_e_by_A = np.array([
                np.dot(np.arange(block.stop-block.start), Y[block])*nH
                for block in model.nuclide_slices])
            e_by_A = model.electron_by_nuclide_cm3(a, f)
            e_error = float(np.max(np.abs(independent_e_by_A-e_by_A)))
            e_total_error = abs(model.electron_density_cm3(a, f)-float(np.sum(independent_e_by_A)))
            slow, de = model.full_rhs_and_electron_per_s(a, Y)
            fast = model.lift_matrix@model.rhs_per_s(a, f)
            denom = max(float(np.max(np.abs(slow))), 1e-100)
            group_relative = float(np.max(np.abs(slow-fast)))/denom
            dy_density = model.full_density_rhs_per_s(a, nH*Y)
            density_relative = float(np.max(np.abs(dy_density-nH*slow)))/max(nH*denom, 1e-100)
            baryon_rate = float(model.species_A@slow)
            charge_rate = float(model.species_charge@slow-de)
            # Exact integer nullvectors were checked above.  Evaluated floating
            # fluxes are assessed against their dot-product roundoff scale;
            # an absolute1e-28 threshold alone was not scale invariant atz2.
            baryon_roundoff=16*np.finfo(float).eps*max(float(np.sum(np.abs(model.species_A*slow))),1e-300)
            charge_roundoff=16*np.finfo(float).eps*max(float(np.sum(np.abs(model.species_charge*slow)))+abs(de),1e-300)
            check(f"live census and full21/grouped physical-time operator a={a:.8g}",
                e_error<2e-18 and e_total_error<2e-18 and group_relative<3e-14
                and density_relative<3e-14 and abs(baryon_rate)<=baryon_roundoff and abs(charge_rate)<=charge_roundoff,
                a=a, ne_cm3=model.electron_density_cm3(a,f), maximum_nuclide_e_error=e_error,
                total_e_error=e_total_error, grouped_full_relative=group_relative,
                physical_density_relative=density_relative,
                baryon_derivative=baryon_rate, total_charge_derivative=charge_rate,
                baryon_roundoff_allowance=baryon_roundoff, charge_roundoff_allowance=charge_roundoff)

        # Jacobian comparison uses genuinely independent central differences of
        # the full nonlinear function, including ne's composition dependence.
        # The RHS is exactly quadratic in fractions, so central differences
        # have no truncation term.  A larger interior step suppresses large
        # photo-term subtraction roundoff without relaxing the acceptance.
        fd_step = 1e-3
        for eta, H in ((0., 1.2e-16), (math.log(21/9), 3e-17), (math.log(7), 7e-18)):
            jac = model.jacobian(eta, f, H)
            fd = np.zeros((9,9))
            for j in range(9):
                delta = np.zeros(9); delta[j] = fd_step
                fd[:,j] = (model.rhs(eta,f+delta,H)-model.rhs(eta,f-delta,H))/(2*fd_step)
            error = float(np.max(np.abs(jac-fd)/(1+np.abs(jac))))
            a = model.scale_factor(eta)
            grad = model.electron_gradient_cm3(a)
            fdgrad = np.empty(9)
            for j in range(9):
                delta = np.zeros(9); delta[j]=fd_step
                fdgrad[j]=(model.electron_density_cm3(a,f+delta)-model.electron_density_cm3(a,f-delta))/(2*fd_step)
            gradient_error = float(np.max(np.abs(grad-fdgrad))/np.max(np.abs(grad)))
            simplex_jac = max(float(np.max(np.abs(np.sum(jac[b],axis=0)))) for b in model.fraction_groups)
            check(f"analytic nonlinear9x9 Jacobian eta={eta:.8g}", error<2e-7
                and gradient_error<2e-10 and simplex_jac<2e-10,
                eta=eta, H_per_s=H, fd_step=fd_step,
                maximum_scaled_jacobian_error=error,
                gradient_error_relative_to_maximum=gradient_error,
                maximum_group_sum_jacobian_residual=simplex_jac)

        # Arbitrary full nuclear/ionic populations exercise n/T outside the
        # grouping invariant, with explicit free-electron bookkeeping.
        v = np.zeros(22)
        v[0],v[5],v[6],v[1],v[7]=.2,.3,.4,.7,.11
        v[21]=float(model.species_charge@v[:21])
        for dt in (0., 2*NEUTRON_MEAN_LIFETIME_S, TRITIUM_HALF_LIFE_S, 1e17):
            out=model.weak_decay_step(v,dt)
            baryon_error=abs(float(mass22@(out-v)))
            charge_error=abs(float(charge22@(out-v)))
            n_error=abs(out[0]-.2*math.exp(-dt/NEUTRON_MEAN_LIFETIME_S))
            t_error=max(abs(out[j]-v[j]*2**(-dt/TRITIUM_HALF_LIFE_S)) for j in (5,6))
            check(f"exact full22 weak-only step dt={dt:.8g}",
                min(out)>=0 and baryon_error<2e-15 and charge_error<2e-15
                and n_error<2e-15 and t_error<2e-15,
                dt_s=dt, baryon_change=baryon_error, charge_change=charge_error,
                neutron_survival_error=n_error, tritium_survival_error=t_error,
                electrons_created=float(out[21]-v[21]))

        rhs_full, de = model.full_rhs_and_electron_per_s(1/9., v[:21], include_weak=True)
        check("full21 atomic plus weak conservation on nonzero n/T control",
            abs(float(model.species_A@rhs_full))<2e-18
            and abs(float(model.species_charge@rhs_full-de))<2e-18,
            baryon_rate=float(model.species_A@rhs_full),
            charge_rate=float(model.species_charge@rhs_full-de))

        high_li = np.zeros(21); high_li[20]=1.
        d_high = model.full_rhs_per_s(1/3., high_li, include_weak=False)
        initial_Y = model.abundance_per_H(model.initial_fractions)
        initial_d = model.full_rhs_per_s(1/3., initial_Y)
        check("LiIV recombination present and cutoff upper photo channels remain zero",
            d_high[20]<0 and d_high[19]>0
            and model.provider.photo_ratios[4]==0 and model.provider.photo_ratios[5]==0
            and np.all(initial_d[[15,16,19,20]]==0)
            and np.all(model.weak_decay_rhs_per_s(initial_Y)==0),
            LiIV_loss_per_s=float(d_high[20]), LiIII_gain_per_s=float(d_high[19]),
            upper_photo_ratios=model.provider.photo_ratios[4:].tolist())

        invalid = f.copy();invalid[0]=-.01
        before = invalid.copy()
        rejected=False
        try: model.validate_fractions(invalid)
        except ValueError: rejected=True
        check("positivity check rejects without state clipping", rejected and np.array_equal(before,invalid))
        initial_check=model.validate_fractions(model.initial_fractions, tolerance=2e-15)
        check("initial simplex valid and readonly",not model.initial_fractions.flags.writeable,
              **initial_check)
        scenario = json.loads((UNIT/"data/ISOTOPE_SCENARIO.json").read_text())
        rejected_fields=[]
        with tempfile.TemporaryDirectory(prefix="he32_primordial_") as tmp:
            for field in ("n_over_H", "T_over_H"):
                modified=json.loads(json.dumps(scenario));modified["composition"][field]=1e-20
                path=Path(tmp)/(field+".json");path.write_text(json.dumps(modified))
                try: PrimordialNetwork(path)
                except ValueError as error:
                    if "requires n=T=0" in str(error): rejected_fields.append(field)
        check("fast path refuses nonzero n/T input", rejected_fields==["n_over_H","T_over_H"],
              rejected_fields=rejected_fields)
        all_good=all(row["passed"] for row in records["checks"])
        records["status"]="completed"
        records["decision"]="PASS_SCOPED_PRIMORDIAL_NETWORK" if all_good else "FINDING_REQUIRES_REPAIR"
        records["source_unchanged_during_checks"]=(records["files_sha256"]["src/primordial_network.py"]
             == hashlib.sha256((UNIT/"src/primordial_network.py").read_bytes()).hexdigest())
        save()
        print(json.dumps({"decision":records["decision"],"checks":len(records["checks"]),
                          "integration_attempts":0,"benchmark_runs":0,
                          "source_unchanged":records["source_unchanged_during_checks"]}))
        return 0 if all_good and records["source_unchanged_during_checks"] else 2
    except Exception as error:
        records["status"]="failed";records["exception"]=repr(error);save()
        raise


if __name__=="__main__": raise SystemExit(main())
