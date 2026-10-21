"""Mass-aware finite age-measure response bounds with explicit threshold jumps.

Conditional theorem for a COMMON response g on both measures:
  |g|<=G,  g=g_smooth+sum J_i*1(age>=cut_i), Lip(g_smooth)<=L.
The routine does not infer G, L, jumps, source equivalence or native gas history.
Units: age coordinate times L has the units of g; weights are photon count/H.
Binary64 evaluation is not an outward-rounded error certificate.
"""
import math
from compare_results import w1


def response_bound(xa,wa,xb,wb,*,response_abs_max,smooth_lipschitz,jumps=()):
    def measure(x,w):
        if len(x)!=len(w):raise ValueError('AGE_MASS_LENGTH_MISMATCH')
        if not all(math.isfinite(v) and v>=0 for v in [*x,*w]):
            raise ValueError('INVALID_PHYSICAL_AGE_OR_MASS')
        mass=math.fsum(w)
        if not math.isfinite(mass):raise ValueError('NONFINITE_TOTAL_MASS')
        return mass
    ma=measure(xa,wa);mb=measure(xb,wb)
    G=float(response_abs_max);L=float(smooth_lipschitz)
    if not all(math.isfinite(v) and v>=0 for v in (G,L)):
        raise ValueError('INVALID_RESPONSE_ENVELOPE')
    cuts=[]
    for cut,jump in jumps:
        if not math.isfinite(cut) or not math.isfinite(jump):
            raise ValueError('INVALID_RESPONSE_JUMP')
        cuts.append((cut,jump))
    mass_term=G*abs(ma-mb)
    if ma==0 or mb==0:
        return dict(absolute_bound=mass_term,mass_term=mass_term,smooth_age_term=0.,
                    threshold_term=0.,age_W1=None,masses=[ma,mb],thresholds=[],
                    claim='CONDITIONAL_COMMON_RESPONSE; NOT_NATIVE_ACCURACY')
    distance=w1(xa,wa,xb,wb);common=min(ma,mb)
    threshold=[]
    for cut,jump in cuts:
        pa=math.fsum(w for t,w in zip(xa,wa) if t>=cut)/ma
        pb=math.fsum(w for t,w in zip(xb,wb) if t>=cut)/mb
        threshold.append(dict(cut=cut,jump=jump,tail_probability_difference=abs(pa-pb),
                              bound=common*abs(jump)*abs(pa-pb)))
    smooth=common*L*distance
    jump_term=math.fsum(v['bound'] for v in threshold)
    total=math.fsum((mass_term,smooth,jump_term))
    if not math.isfinite(total):raise OverflowError('NONFINITE_RESPONSE_BOUND')
    return dict(absolute_bound=total,mass_term=mass_term,smooth_age_term=smooth,
                threshold_term=jump_term,age_W1=distance,masses=[ma,mb],thresholds=threshold,
                claim='CONDITIONAL_COMMON_RESPONSE; NOT_NATIVE_ACCURACY')
