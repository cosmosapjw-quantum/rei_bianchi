"""A few algebraic states, original-moment parity and conservation; no benchmark."""
from __future__ import annotations

import argparse
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import sys

import numpy as np


def check(vendor_root: Path) -> dict:
    vendor_root = vendor_root.resolve()
    sys.path.insert(0, str(vendor_root))
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
    import canonical_fv
    from prepared_moments import PreparedCanonicalMoments

    ode_calls = 0
    def no_ode(*args, **kwargs):
        nonlocal ode_calls
        ode_calls += 1
        raise AssertionError("this algebraic check must not integrate an ODE")
    canonical_fv.solve_ivp = no_ode

    states = [(0.0, 0.0, 0.0), (0.4, 0.02, 0.03),
              (float(np.log(4.2)), 0.1, -0.02),
              (float(np.log(7.0)), 0.2, 0.01), (0.0, -1.0, 0.02),
              (1000.0, 1.0, 0.0)]
    records = []
    cases = [dict(mass_over_Tref=30.0, amplitude=0.5, radial_cells=24,
                  angular_cells=12, gauss_order=3),
             dict(mass_over_Tref=100000.0, amplitude=2.0, radial_cells=4,
                  angular_cells=4, gauss_order=4)]
    for params in cases:
        original = canonical_fv.CanonicalMomentumFV(**params)
        prepared = PreparedCanonicalMoments(original)
        outputs = []
        ref_outputs = []
        for eta, b, v in states:
            ref = original.moments(eta, b)
            got = prepared.moments(eta, b)
            assert type(got) is canonical_fv.FVMoments
            x = np.array([got.rho, got.pressure_perp, got.pressure_parallel])
            y = np.array([ref.rho, ref.pressure_perp, ref.pressure_parallel])
            np.testing.assert_allclose(x, y, rtol=3e-14, atol=0.0)
            assert got.ncell_number == ref.ncell_number
            assert got.min_cell_number == ref.min_cell_number
            outputs.append(x)
            ref_outputs.append(y)
            rel = np.divide(abs(x-y), abs(y), out=np.zeros(3), where=y != 0)
            item = dict(params=params, eta=eta, b=b, bprime=v,
                        maximum_moment_relative_error=float(np.max(rel)))
            if eta < 10:
                # Independent differentiation of the original mass-shell sum.
                q2 = original._q ** 2
                qp2 = np.exp(-2*eta + 2*b) * q2 * (1-original._mu2)
                qz2 = np.exp(-2*eta - 4*b) * q2 * original._mu2
                energy = np.sqrt(original.mass**2 + qp2 + qz2)
                w = np.exp(-3*eta) * original._numbers / original.reference_energy_norm
                drho = np.sum(w * (-3*energy - (qp2+qz2)/energy
                                  + v*(qp2-2*qz2)/energy))
                residual = drho + 3*(got.rho+got.pbar) + 6*v*got.pi_s
                scaled = float(abs(residual)/(got.rho+got.pbar))
                number_residual = float(abs(got.ncell_number*np.exp(3*eta)
                                           / original.total_cell_number-1))
                assert scaled < 3e-14
                assert number_residual < 3e-14
                item.update(energy_work_scaled_residual=scaled,
                            number_relative_residual=number_residual)
            records.append(item)

        budget = 2 * 2 * prepared.packet_count * 8  # two states per two work arrays
        batch = prepared.moment_batch([s[0] for s in states], [s[1] for s in states],
                                      chunk=32, max_work_bytes=budget)
        np.testing.assert_allclose(batch, ref_outputs, rtol=3e-14, atol=0.0)
        assert batch.dtype == np.float64
        assert prepared.moment_batch([], []).shape == (0, 3)
        assert np.array_equal(prepared.cell_numbers, original.cell_numbers)
        assert not np.any(prepared.distribution_change_deta())
        assert prepared.total_cell_number == original.total_cell_number
        assert prepared.packet_count == original.packet_count
        for name in ("_q_perp2", "_q_parallel2", "_weights", "_weighted_q_perp2",
                     "_weighted_q_parallel2", "_cell_numbers"):
            array = getattr(prepared, name)
            assert array.dtype == np.float64 and not array.flags.writeable
            try:
                array.flags.writeable = True
            except ValueError:
                pass
            else:
                raise AssertionError("prepared array must own immutable backing bytes")
        try:
            prepared.mass = 1.0
        except FrozenInstanceError:
            pass
        else:
            raise AssertionError("prepared scalar identity must be frozen")
        for eta, b in [(-0.1, 0.0), (0.0, 1.01), (float("nan"), 0.0)]:
            for evaluator in (original, prepared):
                try:
                    evaluator.moments(eta, b)
                except ValueError:
                    pass
                else:
                    raise AssertionError("original and prepared domains must agree")

    source_paths = [vendor_root / x for x in
                    ("canonical_fv.py", "species_hierarchy.py", "lrs_boltzmann.py")]
    implementation = Path(__file__).resolve().parents[1] / "src" / "prepared_moments.py"
    source_paths += [implementation, Path(__file__).resolve()]
    return dict(status="PASS_SCOPED_ALGEBRAIC_PARITY", ode_calls=ode_calls,
        benchmark_runs=0, new_physical_trajectories=0, independent_result_admission=False,
        binary64=True, bitwise_parity_claim=False, numpy_version=np.__version__,
        python=sys.version, source_sha256={str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                                          for p in source_paths},
        states_per_source=len(states), source_instances=len(cases),
        checks=records,
        max_scalar_relative_error=max(x["maximum_moment_relative_error"] for x in records),
        max_energy_work_scaled_residual=max(x.get("energy_work_scaled_residual", 0)
                                            for x in records),
        max_number_relative_residual=max(x.get("number_relative_residual", 0)
                                         for x in records),
        batch_two_state_workspace_cap_checked=True, immutable_arrays_checked=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vendor-root", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check(args.vendor_root)
    body = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(body)
    print(body, end="")
