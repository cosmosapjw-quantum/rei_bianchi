"""Photon-energy book-keeping with explicit identifiability limit.

Total absorbed photon energy can be reconstructed from the same producer
cumulative energy-ledger definition, subject to floating-point roundoff.
That does NOT identify the three species B_i or nonphoto micro terms.
"""
from fractions import Fraction as F


def reconstruct_total_absorption(qe: F, active: F, escaped: F, redshift: F) -> F:
    absorbed = qe-active-escaped-redshift
    if absorbed < 0:
        raise ValueError('NEGATIVE_RECONSTRUCTED_TOTAL_ABSORPTION')
    return absorbed


def unidentified_components(total:F) -> tuple[tuple[F,F,F],tuple[F,F,F]]:
    if total<=0: raise ValueError('NONPOSITIVE_EXAMPLE_TOTAL')
    return (total,F(0),F(0)),(total/F(2),total/F(4),total/F(4))
