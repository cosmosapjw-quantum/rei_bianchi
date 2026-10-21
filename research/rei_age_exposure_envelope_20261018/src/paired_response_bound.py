"""Separate age-measure error from a known change in the physical response.

Each envelope bounds one response on BOTH measure supports. The supplied
response_sup_difference bounds |g_left-g_right| on their union, not just at
sampled endpoints. This is a conditional real-arithmetic comparison theorem;
ordinary binary64 evaluation is not outward-rounded interval arithmetic.
"""
import math
from age_response_bound import response_bound


def paired_bound(xa,wa,xb,wb,*,left_envelope,right_envelope,response_sup_difference):
    delta=float(response_sup_difference)
    if not math.isfinite(delta) or delta<0:
        raise ValueError('INVALID_RESPONSE_SUP_DIFFERENCE')
    left=response_bound(xa,wa,xb,wb,**left_envelope)
    right=response_bound(xa,wa,xb,wb,**right_envelope)
    ma,mb=left['masses']
    candidate_left=left['absolute_bound']+mb*delta
    candidate_right=right['absolute_bound']+ma*delta
    bound=min(candidate_left,candidate_right)
    if not math.isfinite(bound):
        raise OverflowError('NONFINITE_PAIRED_RESPONSE_BOUND')
    return dict(absolute_bound=bound,
        common_left_bound=left['absolute_bound'],
        common_right_bound=right['absolute_bound'],
        response_mismatch_left=mb*delta,response_mismatch_right=ma*delta,
        candidates=[candidate_left,candidate_right],masses=[ma,mb],
        chosen_common_response='left' if candidate_left<=candidate_right else 'right',
        claim='CONDITIONAL_TWO_RESPONSES; NO_NATIVE_OPACITY_CERTIFICATION')
