"""Predeclared claim gate for source-safe versus coherent branch families."""
from __future__ import annotations
import math

def classify(*,source_safe_rank_lower_bound:int,global_parameter_rank:int,
             adversarial_outside_count:int,coherent_width_max:float,
             coherent_empirical_residual:float):
    finite=math.isfinite(coherent_width_max) and math.isfinite(coherent_empirical_residual)
    if not finite:
        classification='COHERENT_AUDITOR_NUMERICAL_FAILURE'
    elif source_safe_rank_lower_bound>global_parameter_rank or adversarial_outside_count>0:
        classification='SOURCE_SAFE_PARAMETER_RANK_NOT_REPRESENTED'
    elif coherent_width_max>2.0e-3:
        classification='CONTINUOUS_ENCLOSURE_TOO_WIDE'
    else:
        classification='SOURCE_SAFE_CONTINUOUS_ENCLOSURE_CERTIFIED'
    authorized=classification=='SOURCE_SAFE_CONTINUOUS_ENCLOSURE_CERTIFIED'
    return {
        'classification':classification,
        'production_authorized':authorized,
        'next_stage':None if authorized else 'SPARSE_LOCAL_GENERATOR_AFFINE_TAYLOR_MODEL_ENCLOSURE_LOCK',
        'coherent_auditor_only':classification=='SOURCE_SAFE_PARAMETER_RANK_NOT_REPRESENTED',
    }
