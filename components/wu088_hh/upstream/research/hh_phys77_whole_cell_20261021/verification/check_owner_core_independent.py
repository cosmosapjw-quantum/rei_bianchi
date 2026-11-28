"""Independent point checks: exact captured coefficients, no ODE integration.

The reference evaluates unfused dimensional formulas at Decimal precision 120.
It shares neither the normalized owner formulas nor packet caches with the core.
Point comparisons test the implementation; they are not whole-cell certificates.
"""
from __future__ import annotations

from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np


BASE = Path("/workspace/scratch/61913f66989c")
REPO = BASE / "WU088_HH_PHYS77"
CORE = REPO / "research/hh_phys77_whole_cell_20261021/source"
REQUEST = BASE / "phys77_audit/exports/REQUEST_FIRST_CELL.json"
OWNER_ROOT = BASE / "upstream_inputs/rei198_verified/repo_payload/research/rei_bianchi_sigma_pi_pilot_20261021"
sys.path.insert(0, str(CORE))

import export_owner
from owner_interval import FiniteOwner


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def direct_reference(table, x_string, state_strings):
    """Dimensionful direct equations, with separately reduced pressure moments."""
    with localcontext() as context:
        context.prec = 120
        c = {key: Decimal(value) for key, value in table["constants"].items()}
        x, y = Decimal(x_string), [Decimal(value) for value in state_strings]
        qnodes = [Decimal(value) for value in table["arrays"]["q"]]
        mus = [Decimal(value) for value in table["arrays"]["mu2"]]
        populations = [[Decimal(value) for value in row] for row in table["arrays"]["numbers"]]
        matrix = [[Decimal(value) for value in row] for row in table["arrays"]["M"]]
        redshift_factor = (-x).exp()
        transverse = (2*y[1]).exp()
        longitudinal = (-4*y[1]).exp()
        volume_factor = redshift_factor**3
        rho = pressure_perp = pressure_parallel = Decimal(0)
        packets = []
        for i, radial in enumerate(qnodes):
            for j, mu2 in enumerate(mus):
                u = (redshift_factor*radial)**2 * transverse * (1-mu2)
                v = (redshift_factor*radial)**2 * longitudinal * mu2
                energy = (c["mass"]**2+u+v).sqrt()
                weight = volume_factor/c["reference_energy_norm"] * populations[i][j]
                rho += weight*energy
                pressure_perp += weight*u/(2*energy)
                pressure_parallel += weight*v/energy
                packets.append((u, v, energy, weight))
        pbar = (2*pressure_perp+pressure_parallel)/3
        pi = (pressure_parallel-pressure_perp)/3
        scale_factor = c["a_ref"]*x.exp()
        dust = (1-c["f_m"])*c["omega_m"]/scale_factor**3
        radiation = c["omega_r"]/scale_factor**4
        shear_rate = c["h_ref"]*y[2]
        h2 = c["h0"]**2*(dust+c["mpref"]*rho+radiation*y[3]+c["omega_lambda"])+shear_rate**2
        h = h2.sqrt()
        shear_ratio = shear_rate/h
        pressure = radiation*y[4]/3+c["mpref"]*pi
        matrix_product = [sum((coefficient*e for coefficient, e in zip(row, y[3:])), Decimal(0))
                          for row in matrix]
        rhs = [c["h_ref"]/h, shear_ratio,
               -3*y[2]+3*c["h0"]**2*pressure/(c["h_ref"]*h)]
        rhs.extend(shear_ratio*value for value in matrix_product)
        # Differentiate every packet directly, without using the work-cancellation identity.
        rho_prime = sum((weight*(-3*energy+(-u-v+shear_ratio*(u-2*v))/energy)
                         for u, v, energy, weight in packets), Decimal(0))
        h2_prime = c["h0"]**2*(-3*dust+c["mpref"]*rho_prime
                                   +radiation*(-4*y[3]+rhs[3]))+2*c["h_ref"]**2*y[2]*rhs[2]
        alpha = 3+h2_prime/(2*h2)
        pm = Decimal(3).sqrt()*3*c["h0"]**2*c["mpref"]*pi/h2
        pr = Decimal(3).sqrt()*c["h0"]**2*radiation*y[4]/h2
        shear = Decimal(3).sqrt()*shear_ratio
        return {"rhs": rhs, "A": alpha, "A_chain_rule": alpha,
                "P_m": pm, "P_r": pr, "S": shear,
                "Pi_total_F": Decimal(2).sqrt()*abs(pm+pr),
                "Sigma_F": Decimal(2).sqrt()*abs(shear),
                "H": h, "H2_over_h0_squared": h2/c["h0"]**2,
                "delta_monopole": matrix_product[0]+2*y[4],
                "rho": rho, "pressure_perp": pressure_perp,
                "pressure_parallel": pressure_parallel, "pi": pi,
                "rho_minus_pbar": rho-pbar}


def main():
    paths = [CORE/"owner_interval.py", CORE/"cell_enclosure.py", CORE/"export_owner.py",
             REPO/"research/hh_phys76_time_transport_20261021/source/interval_transport.py"]
    source_hashes = {str(path.relative_to(REPO)): sha(path) for path in paths}
    request = json.loads(REQUEST.read_text())
    table = request["table"]
    owner = FiniteOwner(table, precision=50)
    loader = export_owner._load_pinned_loader(REPO)
    binary64_owner = loader._load_owner(OWNER_ROOT, export_owner.OWNER_FILES)
    binary64_owner.set_amplitude(float(Decimal(table["constants"]["amplitude"])))
    recaptured = export_owner.capture_coefficients(binary64_owner, sys.modules["pilot"].FM)
    if (recaptured["arrays"] != table["arrays"] or recaptured["constants"] != table["constants"]):
        raise AssertionError("POINT_FLOAT_COMPARATOR_COEFFICIENTS_CHANGED")
    points, all_pass = [], True
    for index, (x, state) in enumerate(zip(request["predictor"]["x"], request["predictor"]["state"])):
        boxes = owner.evaluate(owner.a.point(x), [owner.a.point(v) for v in state])
        reference = direct_reference(table, x, state)
        checks = {}
        for key, values in reference.items():
            entries = enumerate(values) if isinstance(values, list) else [(None, values)]
            for component, expected in entries:
                box = boxes[key][component] if component is not None else boxes[key]
                label = key+"["+str(component)+"]" if component is not None else key
                contained = box.lo <= expected <= box.hi
                with localcontext() as ctx:
                    ctx.prec = 120
                    width = box.hi-box.lo
                checks[label] = {"reference_120": str(expected), "core_50_bounds": box.strings(),
                                 "reference_inside": contained, "width": str(width)}
                all_pass = all_pass and contained
        float_rhs = binary64_owner.rhs(float(Decimal(x)), np.array([float(Decimal(v)) for v in state], dtype=np.float64))
        with localcontext() as ctx:
            ctx.prec = 120
            differences = [Decimal.from_float(float(observed))-expected
                           for observed, expected in zip(float_rhs, reference["rhs"])]
        points.append({"point": index, "x": x, "checks": checks,
                       "original_binary64_rhs": [float(value).hex() for value in float_rhs],
                       "original_rhs_minus_exact_coefficient_reference": [str(value) for value in differences],
                       "original_rhs_max_abs_difference": str(max(value.copy_abs() for value in differences)),
                       "binary64_comparison_role": "arithmetic-difference report only; NOT an interval acceptance test"})
    if source_hashes != {str(path.relative_to(REPO)): sha(path) for path in paths}:
        raise AssertionError("REVIEWED_SOURCE_CHANGED_DURING_POINT_CHECKS")
    result = {"schema": "PHYS77_INDEPENDENT_OWNER_POINT_REVIEW_V1",
              "status": "PASS_SCOPED" if all_pass else "FAIL_PRESERVED",
              "source_sha256": source_hashes, "review_script_sha256": sha(__file__),
              "request_file_sha256": sha(REQUEST), "table_sha256": table["table_sha256"],
              "reference_precision": 120, "core_precision": 50, "points": points,
              "method": "unfused dimensional direct finite sums; packet-level rho derivative; full M row",
              "limitations": "point verification only; high-precision reference is a numerical check, not a proof of whole-cell correctness or historical rounding",
              "runtime": {"python": platform.python_version(), "numpy": np.__version__},
              "core_point_evaluations": 2, "reference_point_evaluations": 2,
              "original_binary64_rhs_calls": 2, "new_ODE_solves": 0,
              "benchmark_runs": 0, "NCP_jobs": 0}
    output = BASE/"phys77_audit/verification/OWNER_CORE_INDEPENDENT_POINT_REVIEW.json"
    with output.open("x") as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write("\n")
    print(json.dumps({"status": result["status"], "path": str(output), "sha256": sha(output),
                      "source_sha256": source_hashes,
                      "point_comparisons": sum(len(p["checks"]) for p in points),
                      "original_rhs_max_abs_differences": [p["original_rhs_max_abs_difference"] for p in points]}, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    raise SystemExit(main())
