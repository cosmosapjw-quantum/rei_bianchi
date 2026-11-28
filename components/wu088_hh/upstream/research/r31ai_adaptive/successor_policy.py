from __future__ import annotations
import math
from numbers import Real

def _finite_nonnegative(x,name):
    if isinstance(x,bool) or not isinstance(x,Real) or not math.isfinite(float(x)) or float(x)<0:
        raise ValueError(name+" must be finite nonnegative")
    return float(x)

def _positive(x,name):
    x=_finite_nonnegative(x,name)
    if x<=0: raise ValueError(name+" must be positive")
    return x

def midpoint_lower_bounds(E_O,E_K,h_t,h_z=1.0):
    EO=_finite_nonnegative(E_O,"E_O"); EK=_finite_nonnegative(E_K,"E_K")
    ht=_positive(h_t,"h_t"); hz=_positive(h_z,"h_z")
    return {
      "O_fourth_lower_per_t4":384*EO/ht**4,
      "K_second_lower_per_t3":8*EK/ht**2,
      "O_fourth_lower_per_z4":384*EO/hz**4,
      "K_second_lower_per_t_z2":8*EK/hz**2,
    }

def successor_training_policy():
    return {
      "training_nodes_z":[0.0,0.5,1.0,2.0,3.0,3.5,4.0],
      "cell_widths_z":[0.5,0.5,1.0,1.0,0.5,0.5],
      "z35_status":"PRIOR_INDEPENDENT_VALIDATION_CONSUMED_AS_R31AI_TRAINING",
      "independent_validation_points":[]
    }

def next_holdout_information():
    dk=0.1912237840334797
    dd=0.20561180584475613
    return {
      "z":2.5,
      "DeltaK_per_ta":dk,
      "DeltaDmax_per_ta":dd,
      "S_design_only_per_ta":math.hypot(dk,dd),
      "K_half_gap_per_ta":dk/2,
      "Dmax_half_gap_per_ta":dd/2,
      "execution_authorized":False,
      "winner_prediction":False
    }

def conditional_halving_coefficients():
    return {"O_cubic":1/16,"K_linear":1/4}
