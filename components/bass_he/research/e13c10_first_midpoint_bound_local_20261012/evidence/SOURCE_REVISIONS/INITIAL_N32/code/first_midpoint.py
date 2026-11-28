#!/usr/bin/env python3
"""Signed C2 Peano midpoint enclosure, with immutable original integrands.

No fourth derivative is assumed. The cell correction is h*dx**3/24 times
the signed whole-cell second-derivative interval. Legacy symmetric bounds
are recorded from these same NEW evaluations for diagnosis only.
"""
import time

import directed_interval as di
from directed_interval import IV, Jet2, value
from local_enclosure import integrands


def integrate_signed(c, n):
    if not isinstance(n, int) or isinstance(n, bool) or n <= 0 or n & (n - 1):
        raise ValueError('positive dyadic first-integral N required')
    if c.h.lo <= 0:
        raise ValueError('positive segment width required')
    started = time.perf_counter()
    before = c.evaluations
    dx = IV(1) / n
    midpoint, curvature, symmetric_radii, cells = {}, {}, {}, []
    for j in range(n):
        left, right, mid = IV(j) / n, IV(j + 1) / n, IV(2*j + 1) / (2*n)
        field, _ = integrands(c, Jet2.variable(IV(left.lo, right.hi)))
        middle, _ = integrands(c, mid)
        if set(field) != set(middle):
            raise ArithmeticError('midpoint/whole-cell quantity mismatch')
        terms, corrections, derivatives, values = {}, {}, {}, {}
        for k, jet in field.items():
            if not isinstance(jet, Jet2):
                raise TypeError('whole-cell field must provide original Jet2 derivatives')
            term = c.h * dx * value(middle[k])
            correction = c.h * jet.d2 / (24*n**3)
            midpoint[k] = midpoint.get(k, IV(0)) + term
            curvature[k] = curvature.get(k, IV(0)) + correction
            symmetric_radii[k] = symmetric_radii.get(k, IV(0)) + c.h * IV(abs(jet.d2).hi) / (24*n**3)
            terms[k], corrections[k] = term, correction
            derivatives[k], values[k] = jet.d2, value(middle[k])
        cells.append({'cell':j, 'x_left':left, 'x_right':right, 'x_midpoint':mid,
            'midpoint_value':values, 'second_derivative':derivatives,
            'midpoint_term':terms, 'curvature_correction':corrections})
    signed = {k: midpoint[k] + curvature[k] for k in midpoint}
    symmetric = {k: midpoint[k] + IV(symmetric_radii[k].hi.copy_negate(), symmetric_radii[k].hi)
                 for k in midpoint}
    return {'origin':'NEW_SIGNED_C2_PEANO_MIDPOINT',
        'method':'positive_peano_kernel_signed_curvature_v1', 'N_first':n,
        'precision_digits':di.PRECISION,
        'signed':signed, 'midpoint':midpoint, 'curvature_correction':curvature,
        'same_new_grid_symmetric_diagnostic':symmetric,
        'same_new_grid_symmetric_radius_diagnostic':{k:v.hi for k,v in symmetric_radii.items()},
        'cell_coverage':{'normalized_domain':['0','1'],'dyadic_cells':n,
            'whole_cell_derivative_evaluations':n,'midpoint_evaluations':n},
        'cells':cells, 'new_coefficient_evaluations':c.evaluations-before,
        'old_firstvariation_replays':0,'raw_intersections':0,'old_interval_fallbacks':0,
        'elapsed_seconds':time.perf_counter()-started}
