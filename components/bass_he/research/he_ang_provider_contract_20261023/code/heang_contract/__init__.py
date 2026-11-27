"""Bounded HE-ANG contract implementation; no empirical admission or activation."""

__version__ = "0.1.0"

from .exact_events import (
    ContractError, Event, RawMoments, EventMoments, exact,
    integrate_events, cross_section_weighted, zero_cross_section,
    transform_raw, serialize_bundle, serialize_raw,
)
from .metadata import precheck_provider

__all__ = [
    "ContractError", "Event", "RawMoments", "EventMoments", "exact",
    "integrate_events", "cross_section_weighted", "zero_cross_section",
    "transform_raw", "serialize_bundle", "serialize_raw", "precheck_provider",
]
