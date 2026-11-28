"""Provenance-locked research view for ONE documented Q23 node collision.

Not a general tolerance-based deduplicator. It preserves the original parent
GK7 midpoint and excludes only the explicitly identified split-midpoint alias
from a NEW fit view. Neither input records nor production code are modified.
No new spectral data, interpolation method, or tolerance is introduced.
"""
from __future__ import annotations
from copy import deepcopy
import hashlib
import json

INPUT_CANONICAL_SHA256 = '3279b84a3fa1698b076a270ecf8543fa411c71acc769d0319d968e396e8cd8d3'
KEEP_RHO_HEX = '0x1.a0e8bdf74847dp+2'
DROP_RHO_HEX = '0x1.a0e8bdf74847cp+2'


def make_view(manifest: dict) -> tuple[dict, dict]:
    """Return a copy with 23 Q23 fit records and a complete exclusion receipt.

    This operation applies only to the exact archived R10A manifest. A different
    input must obtain a separate provenance decision, not an automatic merge.
    """
    if type(manifest) is not dict:
        raise ValueError('INPUT_IDENTITY_MISMATCH: expected manifest dictionary')
    try:
        raw = json.dumps(manifest, sort_keys=True, separators=(',', ':'), allow_nan=False).encode('utf-8')
    except (TypeError, ValueError) as exc:
        raise ValueError('INPUT_IDENTITY_MISMATCH: noncanonical manifest') from exc
    if hashlib.sha256(raw).hexdigest() != INPUT_CANONICAL_SHA256:
        raise ValueError('INPUT_IDENTITY_MISMATCH: not the pinned R10A dataset')
    anchors = deepcopy(manifest['anchors'])
    rows = anchors['Q23']
    keep = [row for row in rows if row['rho_hex'] == KEEP_RHO_HEX]
    drop = [row for row in rows if row['rho_hex'] == DROP_RHO_HEX]
    if len(rows) != 24 or len(keep) != 1 or len(drop) != 1:
        raise ValueError('MIDPOINT_PROVENANCE_MISMATCH')
    anchors['Q23'] = [row for row in rows if row['rho_hex'] != DROP_RHO_HEX]
    receipt = {
        'status': 'RESEARCH_VIEW_PREPARED_NOT_SCIENTIFIC_ADMISSION',
        'input_canonical_sha256': INPUT_CANONICAL_SHA256,
        'geometric_node_id': 'Q23/u_over_Rb_squared=1/2',
        'retained_role': 'parent_GK7_center',
        'excluded_role': 'explicit_split_midpoint_Rb_div_sqrt2',
        'retained_record': deepcopy(keep[0]),
        'excluded_record': deepcopy(drop[0]),
        'selection_rule': 'retain_original_parent_node_by_generation_role_not_smallest_reference_error',
        'general_distance_or_rounding_merge': False,
        'new_delta_solves': 0,
        'new_refinement': False,
        'interpolation_method_changed': False,
        'historical_result_overwritten': False,
        'Q23_fit_records_before': 24,
        'Q23_fit_records_after': 23,
    }
    return anchors, receipt
