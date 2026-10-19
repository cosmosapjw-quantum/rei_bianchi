"""Prescribed-opacity controls for the opt-in error norm; no native claim."""
from pathlib import Path
import argparse
import math
import time

import numpy as np
from scipy.integrate import solve_ivp

from error_control import error_control_identity, make_block_dop853
from run_refinement import save


def study():
    records = []
    for dimension in (2, 144, 1152, 9234):
        initial = np.zeros(dimension)
        initial[0] = math.log(1e-4)
        atol = np.full(dimension, 1e-11)
        atol[-1] = 1e-16

        def rhs(t, y):
            out = np.zeros(dimension)
            out[0] = -50.
            out[-1] = 50.*math.exp(y[0])
            return out

        for mode in ('rms', 'block-max'):
            method = 'DOP853' if mode == 'rms' else make_block_dop853((dimension-1, 1))
            start = time.monotonic()
            solution = solve_ivp(rhs, (0., 1.), initial, method=method,
                                 rtol=2e-10, atol=atol, first_step=.01)
            wall = time.monotonic()-start
            number = math.exp(solution.y[0, -1])
            photo = solution.y[-1, -1]
            expected_number = 1e-4*math.exp(-50.)
            expected_photo = 1e-4*(-math.expm1(-50.))
            residual = math.fsum([number, photo, -1e-4])
            records.append(dict(dimension=dimension, error_norm=mode,
                                success=solution.success, nfev=solution.nfev,
                                accepted_steps=len(solution.t)-1, wall_s=wall,
                                photon_N=number, cumulative_photo=photo,
                                analytic_N=expected_number, analytic_photo=expected_photo,
                                absolute_photo_error=abs(photo-expected_photo),
                                photon_residual=residual,
                                photon_normalized=abs(residual)/(abs(number)+abs(photo)+1e-4)))
    return dict(schema='rei.error_control.prescribed_opacity.v1',
                scope='Prescribed-opacity numerical control; no native convergence claim.',
                rtol=2e-10, log_atol=1e-11, ledger_atol=1e-16,
                first_step=.01, interval=[0.,1.], opacity_lambda=50.,
                initial_source_N=1e-4, identity=error_control_identity(), records=records)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    save(args.out,study())


if __name__ == '__main__':
    main()
