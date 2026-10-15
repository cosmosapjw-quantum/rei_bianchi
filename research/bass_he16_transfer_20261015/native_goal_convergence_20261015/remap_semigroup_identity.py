"""Two-neighbor fixed-energy projection is not a semigroup.

Analytic local-uniform-grid toy model: a single photon starts at grid energy E.
A single small redshift takes an energy shift of α ΔE left, 0 < α < 1/2.
The exact free-flight energy after two shifts is E-2αΔE. Each projection
conserves photon number and mean energy. But applying two separate projections
does not equal a single projection after the combined shift.

This is a general non-associativity witness, not a simulation of the actual
multiplicative Bianchi geodesic flow.
"""
from __future__ import annotations
from fractions import Fraction


def _moments(weight):
    locations={0:Fraction(0),-1:Fraction(-1),-2:Fraction(-2)}
    total=sum(weight.values())
    m=sum(locations[k]*w for k,w in weight.items())/total
    v=sum((locations[k]-m)**2*w for k,w in weight.items())/total
    return total,m,v


def semigroup_witness(alpha: Fraction):
    if not Fraction(0)<alpha<Fraction(1,2):
        raise ValueError("Require 0 < α < 1/2 to avoid a grid-boundary crossing")
    repeated={0:(1-alpha)**2,-1:2*alpha*(1-alpha),-2:alpha*alpha}
    once={0:1-2*alpha,-1:2*alpha,-2:Fraction(0)}
    tr,mr,vr=_moments(repeated)
    to,mo,vo=_moments(once)
    gap=vr-vo
    if tr!=1 or to!=1 or mr!=mo or gap!=2*alpha*alpha:
        raise AssertionError("Two-neighbor interpolation algebra incorrect")
    return {
        "alpha":str(alpha),
        "weights_two_reprojections":{str(k):str(v) for k,v in repeated.items()},
        "weights_one_projection":{str(k):str(v) for k,v in once.items()},
        "photon_number_repeated":str(tr),
        "photon_number_once":str(to),
        "mean_grid_energy_shift_both":str(mr),
        "variance_repeated_units_deltaE_squared":str(vr),
        "variance_once_units_deltaE_squared":str(vo),
        "excess_variance_units_deltaE_squared":str(gap),
        "closed_form":"Var[R_alpha o R_alpha]-Var[R_2alpha] = 2 alpha^2 (DeltaE)^2",
    }


if __name__=="__main__":
    import json
    print(json.dumps({
        "schema":"he18.axbi.projection_nonsemigroup_exact_rational.v1",
        "status":"SYMBOLIC_DERIVED_PLUS_WOLFRAM_CHECKED",
        "example":semigroup_witness(Fraction(1,5)),
        "scope":"uniform additive grid translation toy analog; not actual Bianchi spectral error bound",
    },indent=2))
