"""Portable HE36 supplied-event/finite-source/source-lift adapter package.

No module import executes an IVP, physical source admission, or research test.
Dependencies are Python, NumPy, and the pinned local modules in this package.
"""
from .event_bridge import (
    EventTensorSource, attach_event_tensor, NET_TENSOR_SCOPE, CENTRAL_FRAME,
    EVENT_ENERGY_UNIT, ALL_RETAINED_THERMAL, NEUTRAL_21_STATE_CENSUS,
    Coefficient, ResolvedEvent, Unresolved,
)
from .finite_bridge import (
    FiniteMomentRecord, from_finite_evaluation, RADIAL_DIAGNOSTIC, MANUFACTURED_PAIR,
)
from .source_lift import SourceLiftReport, SourceLiftDefect, validate_source_lift

__all__ = [
    "EventTensorSource", "attach_event_tensor", "NET_TENSOR_SCOPE", "CENTRAL_FRAME",
    "EVENT_ENERGY_UNIT", "ALL_RETAINED_THERMAL", "NEUTRAL_21_STATE_CENSUS",
    "Coefficient", "ResolvedEvent", "Unresolved",
    "FiniteMomentRecord", "from_finite_evaluation", "RADIAL_DIAGNOSTIC", "MANUFACTURED_PAIR",
    "SourceLiftReport", "SourceLiftDefect", "validate_source_lift",
]
