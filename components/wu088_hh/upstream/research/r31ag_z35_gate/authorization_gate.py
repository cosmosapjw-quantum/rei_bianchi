from __future__ import annotations
import hashlib, json, math

SCHEMA="WU088_R31AF_Z35_MINIMAL_MIXED_AUTHORIZATION_V1"
ACTION="AUTHORIZE_R31AF_Z35_MINIMAL_MIXED_NODE"
EXPECTED_SCOPE_SHA256="f43faaf5746a5fda5cd26593ee69e97c0f2be8239727a62081d49357e3c2a9b4"

def canonical_json_bytes(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),allow_nan=False).encode("utf-8")

def canonical_sha256(obj):
    return hashlib.sha256(canonical_json_bytes(obj)).hexdigest()

def validate_envelope(envelope):
    if not isinstance(envelope,dict):
        return False,"AUTHORIZATION_ENVELOPE_NOT_OBJECT"
    required={"schema","authorize","action","scope_sha256","one_shot"}
    if set(envelope)!=required:
        return False,"AUTHORIZATION_ENVELOPE_KEYS_MISMATCH"
    if envelope["schema"]!=SCHEMA:
        return False,"AUTHORIZATION_SCHEMA_MISMATCH"
    if envelope["authorize"] is not True:
        return False,"AUTHORIZATION_NOT_AFFIRMATIVE"
    if envelope["action"]!=ACTION:
        return False,"AUTHORIZATION_ACTION_MISMATCH"
    if envelope["scope_sha256"]!=EXPECTED_SCOPE_SHA256:
        return False,"AUTHORIZATION_SCOPE_DRIFT"
    if envelope["one_shot"] is not True:
        return False,"AUTHORIZATION_NOT_ONE_SHOT"
    return True,"AUTHORIZED_ONE_SHOT"

def information_value():
    k=0.19122378403347964
    d=0.2095387347094023
    tol=1e-10
    return {
        "DeltaK_model_per_ta":k,
        "DeltaDmax_model_per_ta":d,
        "S_design_only_per_ta":math.hypot(k,d),
        "K_half_gap_per_ta":k/2,
        "Dmax_half_gap_per_ta":d/2,
        "K_separation_over_tolerance":k/tol,
        "Dmax_separation_over_tolerance":d/tol,
        "winner_prediction":False
    }
