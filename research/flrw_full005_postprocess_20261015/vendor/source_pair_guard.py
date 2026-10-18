"""Bind source relation before labelling a comparison as paired/refinement.

Equal byte identities are a sufficient common-source witness, not the definition
of semantic identity. A different implementation can be admitted only via an
explicit, source-pair-bound reviewed semantic-equivalence record. This helper
checks the record binding; it does NOT prove that equivalence.
"""
from __future__ import annotations
import re

class SourceRelationHold(ValueError):
    pass

def require_source_relation(reference: dict, candidate: dict, manifest: dict) -> str:
    left=reference.get('spec',reference).get('source_identity',{}).get('sha256')
    right=candidate.get('spec',candidate).get('source_identity',{}).get('sha256')
    valid=lambda x:isinstance(x,str) and re.fullmatch(r'[0-9a-f]{64}',x) is not None
    if not valid(left) or not valid(right):
        raise SourceRelationHold('HOLD_SOURCE_IDENTITY_MISSING')
    if left==right:
        return 'BYTE_IDENTICAL_COMPILED_SOURCE'
    relation=manifest.get('source_relation') or {}
    if not isinstance(relation,dict):
        raise SourceRelationHold('HOLD_SOURCE_RELATION_UNBOUND')
    if (relation.get('reference_sha256')==left and relation.get('candidate_sha256')==right
        and relation.get('relation')=='REVIEWED_SAME_PHYSICAL_MODEL'
        and relation.get('status')=='ACCEPTED_SCOPED'
        and isinstance(relation.get('evidence'),str) and relation['evidence'].strip()):
        return 'DECLARED_REVIEWED_SEMANTIC_RELATION_NOT_PROVED_BY_REDUCER'
    raise SourceRelationHold('HOLD_SOURCE_RELATION_UNBOUND')
