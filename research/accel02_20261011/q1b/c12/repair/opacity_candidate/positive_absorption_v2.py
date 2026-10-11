"""Bounded positive-quadrature refinement for explicit incident-order refusal.

Preserve original native-conditioned implementation and its 64/128 default.
Only actual native INCIDENT_ORDER_PAIR refusal at requested (64,128) permits
one 128/256 reconstruction of the same incident moments. All physical supports,
threshold cuts, moment fitting, positivity and own-component tolerances remain
unchanged. Other failures propagate, as does a failed higher-order pair.
No global/source file is patched. Native gas execution is not part of this API.
"""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import copy
import sys

HERE=Path(__file__).resolve().parent;Q1B=HERE.parents[2]
for path in (Q1B,Q1B/'c10',Q1B/'c11/endpoint'):sys.path.insert(0,str(path))
import native_coordinate_absorption as _base
from opacity_native import NativeOpacity
from reconstruction import QuadratureNotConverged

absorb=_base.absorb
_REFINEMENTS=[]


def pop_refinement_records():
    """Drain this single-worker module's explicit per-map telemetry.

    Driver must require an empty queue before each map and persist records in a
    finally block even if the map fails. No cross-process/thread sharing claim.
    """
    records=copy.deepcopy(_REFINEMENTS);_REFINEMENTS.clear();return records


def prepare_incident(N,U,R,a,b,opacity,orders=(64,128),rtol=1e-7,*,support_cap_ev=None):
    try:
        return _base.prepare_incident(N,U,R,a,b,opacity,orders=orders,rtol=rtol,support_cap_ev=support_cap_ev)
    except QuadratureNotConverged as original:
        if not (isinstance(opacity,NativeOpacity) and tuple(orders)==(64,128)
                and str(original).startswith('INCIDENT_ORDER_PAIR:')):
            raise
        record=dict(schema='rei.c12.opacity.quadrature_refinement.v1',parameters=dict(N=float(N),U=float(U),R=float(R),a=float(a),b=float(b)),requested_orders=list(orders),effective_orders=[128,256],requested_rtol=float(rtol),effective_rtol=None,support_cap_ev=support_cap_ev,original_failure=dict(type=type(original).__name__,message=str(original)),status='REFINEMENT_STARTED',tolerance_changed=False,closure_changed=False,threshold_shifted=False,scientific_admission=False)
        _REFINEMENTS.append(record)
        try:
            prepared=_base.prepare_incident(N,U,R,a,b,opacity,orders=(128,256),rtol=rtol,support_cap_ev=support_cap_ev)
        except Exception as refined_failure:
            record.update(status='REFINEMENT_FAILED_CLOSED',refined_failure=dict(type=type(refined_failure).__name__,message=str(refined_failure)))
            refined_failure.add_note('C12 original 64/128 INCIDENT_ORDER_PAIR refusal preserved; one bounded 128/256 refinement also failed; no tolerance change or further retry.')
            raise
        record.update(status='REFINED_SAME_TOLERANCE',effective_rtol=float(prepared.rtol),incident_order_pair_max_error=float(prepared.diagnostics['order_pair_max_error']))
        diagnostics=dict(prepared.diagnostics,quadrature_refinement=copy.deepcopy(record))
        return replace(prepared,diagnostics=diagnostics)
