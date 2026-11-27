"""Versioned atomic rate/count export, with no implicit physical assumptions.

The original source evaluator and writer are inherited byte-for-byte. This module
adds a strict request boundary and provenance-preserving, replayable packet shape.
No cosmological state, density, geometry or heat closure is accepted.
"""
from __future__ import annotations
import copy
import hashlib
from importlib import resources
import json
from pathlib import Path
from typing import Any
from . import _rate
from ._io import write_json_create_only
from .registry import CORE_SHA256, IO_SHA256, sources

ContractError = _rate.ContractError
SourceUnavailable = _rate.SourceUnavailable
MAX_BATCH = 4096
REQUIRED_FIELDS = frozenset({
    'schema', 'source_id', 'temperature_K', 'distribution', 'isotope_basis',
    'initial_state', 'relative_drift_m_s', 'radiation_model',
    'acknowledge_source_conflict', 'unit', 'quantity',
})


def verify_runtime_bindings() -> dict[str, str]:
    """Detect changed inherited implementations; this is code identity, not physics."""
    expected = {'_rate.py': CORE_SHA256, '_io.py': IO_SHA256}
    actual = {}
    for name, sha in expected.items():
        b = resources.files('bass_he_atomic_export').joinpath(name).read_bytes()
        actual[name] = hashlib.sha256(b).hexdigest()
        if actual[name] != sha:
            raise ContractError('INHERITED_CODE_IDENTITY_MISMATCH: ' + name)
    return actual


def _canonical(value: Any) -> str:
    try:
        return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False,
                          separators=(',', ':'))
    except (ValueError, TypeError, RecursionError) as exc:
        raise ContractError('FINITE_JSON_VALUE_REQUIRED') from exc


def loads_strict(text: str | bytes, *, max_bytes: int = 33554432) -> Any:
    """Reject duplicate object keys, nonfinite tokens, oversized or malformed JSON."""
    if not isinstance(text, (str, bytes)):
        raise ContractError('JSON_TEXT_REQUIRED')
    if len(text if isinstance(text, bytes) else text.encode('utf-8')) > max_bytes:
        raise ContractError('JSON_SIZE_BUDGET_EXCEEDED')
    def pairs(items):
        result = {}
        for k, v in items:
            if k in result:
                raise ContractError('DUPLICATE_JSON_KEY: ' + k)
            result[k] = v
        return result
    def forbidden(token):
        raise ContractError('NONFINITE_JSON_TOKEN: ' + token)
    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=forbidden)
        _canonical(value)  # Also catches finite-looking exponents that overflow to inf.
        return value
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ContractError('INVALID_JSON') from exc


def _request(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or set(value) != REQUIRED_FIELDS:
        raise ContractError('EXACT_REQUEST_FIELDS_REQUIRED; NO_DENSITY_OR_GEOMETRY')
    if value['schema'] != 'bass-he.atomic-request.v1':
        raise ContractError('UNSUPPORTED_REQUEST_SCHEMA')
    if value['quantity'] not in ('thermal_rate', 'event_count_coefficients'):
        raise SourceUnavailable('REQUESTED_QUANTITY_HAS_NO_REGISTERED_PROVIDER')
    temps = value['temperature_K']
    if not isinstance(temps, list) or not 1 <= len(temps) <= MAX_BATCH:
        raise ContractError('TEMPERATURE_LIST_SIZE_OUTSIDE_1_TO_4096')
    _canonical(value)
    return copy.deepcopy(value)


def export_packet(request: dict[str, Any]) -> dict[str, Any]:
    """Evaluate one explicitly selected source for a whole valid batch.

    The returned count coefficients still need the physical density product at
    the consumer. This package deliberately does not compute it or evolve a gas.
    """
    req = _request(request)
    verify_runtime_bindings()
    if req['source_id'] != _rate.SOURCE_ID:
        raise SourceUnavailable('EXPLICIT_REGISTERED_RATE_SOURCE_REQUIRED')
    kw = {k: req[k] for k in ('source_id', 'distribution', 'isotope_basis',
        'initial_state', 'relative_drift_m_s', 'radiation_model',
        'acknowledge_source_conflict', 'unit')}
    evaluator = _rate.rate if req['quantity'] == 'thermal_rate' else _rate.count_coefficients
    records = [evaluator(t, **kw) for t in req['temperature_K']]
    return {
        'schema': 'bass-he.atomic-export.v1',
        'exporter': 'bass-he-atomic-export==0.1.0',
        'request': req,
        'source': sources()['sources'][0],
        'records': records,
        'contribution_role': 'ONE_SELECTED_PROVIDER_PER_REACTION',
        'reaction_id': _rate.REACTION_ID,
        'rate_available': True,
        'count_coefficients_available': req['quantity'] == 'event_count_coefficients',
        'heat_moment_available': False,
        'photon_spectrum_available': False,
        'momentum_transfer_available': False,
        'production_admission': 'NOT_GRANTED_BY_EXPORTER',
        'physical_accuracy_certified': False,
        'optical_recalculation_performed': False,
        'receiver_integration_tested': False,
        'scope': 'atomic-data-only; density multiplication and transport belong to consumer',
    }


def validate_packet(packet: Any) -> bool:
    """Replay the selected supplier and compare all fields, not just a schema label.

    This proves serialization and selected-code consistency, not true-rate
    accuracy, independent scientific review or scientific production readiness.
    """
    if not isinstance(packet, dict) or 'request' not in packet:
        raise ContractError('ATOMIC_PACKET_WITH_REQUEST_REQUIRED')
    expected = export_packet(packet['request'])
    if _canonical(packet) != _canonical(expected):
        raise ContractError('PACKET_SEMANTICS_OR_PAYLOAD_MISMATCH')
    return True


def bundle_packets(packets: list[dict[str, Any]]) -> dict[str, Any]:
    """Do not double-count distinct suppliers, or count/rate views, of one reaction."""
    if not isinstance(packets, list) or not 1 <= len(packets) <= 16:
        raise ContractError('PACKET_LIST_SIZE_OUTSIDE_1_TO_16')
    seen = set()
    for packet in packets:
        validate_packet(packet)
        key = packet['reaction_id']
        if key in seen:
            raise ContractError('DUPLICATE_REACTION_NOT_ADDITIVE: ' + key)
        seen.add(key)
    return {'schema': 'bass-he.atomic-bundle.v1', 'packets': copy.deepcopy(packets),
            'additive_reactions_checked': True, 'rate_values_summed': False,
            'production_admission': 'NOT_GRANTED_BY_EXPORTER'}


def write_packet(path: str | Path, request: dict[str, Any]) -> dict[str, Any]:
    """Prepare the entire packet before a create-only fsynced write."""
    packet = export_packet(request)
    write_json_create_only(path, packet)
    return packet
