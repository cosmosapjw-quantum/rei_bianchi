"""Four algebraic states; no ODE integration or performance benchmark."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

import numpy as np


def verify(root: Path) -> dict:
    root = root.resolve()
    sys.path.insert(0, str(root / "vendor"))
    from canonical_fv import CanonicalMomentumFV
    model = CanonicalMomentumFV(30.0, 0.5, 24, 12, 3)
    checks = []
    for eta, b, g in [(0.0, 0.0, 0.0), (0.4, 0.02, 0.03),
                      (np.log(4.2), 0.1, -0.02), (np.log(7.0), 0.2, 0.01)]:
        q, mu2 = model._q, model._mu2
        w = model._numbers / model.reference_energy_norm
        perp2 = np.exp(-2 * eta + 2 * b) * q * q * (1 - mu2)
        para2 = np.exp(-2 * eta - 4 * b) * q * q * mu2
        energy = np.sqrt(model.mass**2 + perp2 + para2)
        weight = np.exp(-3 * eta) * w
        moment = model.moments(float(eta), b)
        derivative = np.sum(weight * (-3 * energy - (perp2 + para2) / energy
                                      + g * (perp2 - 2 * para2) / energy))
        residual = derivative + 3 * (moment.rho + moment.pbar) + 6 * g * moment.pi_s
        checks.append(dict(eta=float(eta), b=b, bprime=g,
            energy_identity_abs_residual=float(abs(residual)),
            energy_identity_scaled_residual=float(abs(residual)/(moment.rho+moment.pbar)),
            canonical_number_relative_residual=float(abs(
                moment.ncell_number*np.exp(3*eta)/model.total_cell_number-1))))
    paths = ["vendor/canonical_fv.py", "vendor/species_hierarchy.py",
             "vendor/lrs_boltzmann.py", "src/coordinates.py", "src/split_pilot.py"]
    result = dict(status="numerically checked",
        kind="algebraic moment checks only; no ODE integration, no benchmark",
        python=sys.version, numpy=np.__version__,
        input=dict(mass_over_Tref=30.0, amplitude=0.5, radial_cells=24,
                   angular_cells=12, gauss_order=3),
        source_sha256={p: hashlib.sha256((root/p).read_bytes()).hexdigest() for p in paths},
        checks=checks)
    assert max(x["energy_identity_scaled_residual"] for x in checks) < 3e-14
    assert max(x["canonical_number_relative_residual"] for x in checks) < 3e-14
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pilot_root", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = verify(args.pilot_root)
    serialized = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized)
    print(serialized, end="")
