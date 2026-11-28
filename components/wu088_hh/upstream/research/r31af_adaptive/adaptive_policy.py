from __future__ import annotations
import math
from numbers import Real

def _positive(x,name):
    if isinstance(x,bool) or not isinstance(x,Real) or not math.isfinite(float(x)) or float(x)<=0:
        raise ValueError(name+" must be positive finite")
    return float(x)

def midpoint_lower_bounds(E_O,E_K,h_t,h_z=1.0):
    EO=_positive(E_O,"E_O"); EK=_positive(E_K,"E_K")
    ht=_positive(h_t,"h_t"); hz=_positive(h_z,"h_z")
    return {
        "O_fourth_lower_per_t4":384*EO/ht**4,
        "K_second_lower_per_t3":8*EK/ht**2,
        "O_fourth_lower_per_z4":384*EO/hz**4,
        "K_second_lower_per_t_z2":8*EK/hz**2,
    }

def consume_validation_as_training():
    return {
        "training_nodes_z":[0.0,0.5,1.0,2.0,3.0,4.0],
        "cell_widths_z":[0.5,0.5,1.0,1.0,1.0],
        "z05_status":"PRIOR_INDEPENDENT_VALIDATION_CONSUMED_AS_R31AF_TRAINING",
        "independent_validation_points":[]
    }

def next_validation_design():
    rows=[
      {"z":2.5,"DeltaK":0.1912237840334797,"DeltaDmax":0.20561180584475613,"S":0.280789512416017},
      {"z":3.5,"DeltaK":0.19122378403347964,"DeltaDmax":0.2095387347094023,"S":0.2836776637729875},
    ]
    best=max(rows,key=lambda r:(r["S"],-r["z"]))
    return {
      "rows":rows,
      "selected_z":best["z"],
      "criterion":"max S among remaining fresh candidates; exact tie -> lower z",
      "selected_K_half_gap":best["DeltaK"]/2,
      "selected_Dmax_half_gap":best["DeltaDmax"]/2,
      "execution_authorized":False,
    }
