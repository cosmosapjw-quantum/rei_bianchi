"""Bounded JSON fixture CLI. Both physical-admission flags always remain false."""
import argparse
import json
from pathlib import Path

from .exact_events import (ContractError, Event, exact, integrate_events,
                           cross_section_weighted, zero_cross_section, serialize_bundle)
from .metadata import IDENTITIES, precheck_provider, safe_payload_name

MAX_FILE_BYTES = 1_048_576
MAX_EVENTS = 256
SI_UNITS = {"energy": "J", "mass": "kg", "momentum": "kg*m/s", "cross_section": "m^2"}


def strict_json_loads(data):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ContractError("duplicate JSON key: " + key)
            result[key] = value
        return result
    def constant(value):
        raise ContractError("nonfinite JSON constant refused: " + value)
    return json.loads(data, object_pairs_hook=pairs, parse_constant=constant)


def read_bytes(path):
    with path.open("rb") as stream:
        data = stream.read(MAX_FILE_BYTES + 1)
    if len(data) > MAX_FILE_BYTES:
        raise ContractError("file exceeds bounded fixture size")
    return data


def load_payloads(metadata, payload_root):
    root = Path(payload_root).resolve()
    payloads = {}
    bindings = metadata.get("bindings", {}) if isinstance(metadata, dict) else {}
    if not isinstance(bindings, dict):
        return payloads
    for binding in bindings.values():
        name = binding.get("payload") if isinstance(binding, dict) else None
        if not safe_payload_name(name) or name in payloads:
            continue
        path = (root / name).resolve()
        if not path.is_relative_to(root):
            raise ContractError("payload resolves outside declared payload root")
        if path.is_file():
            payloads[name] = read_bytes(path)
    return payloads


def validate_fixture_payload(payload):
    required = set(IDENTITIES) | {"schema", "units", "normalization", "m", "M", "E", "I", "sigma", "events"}
    if not isinstance(payload, dict) or not required.issubset(payload) or set(payload) - (required | {"description"}):
        raise ContractError("fixture payload has missing or unknown fields")
    if payload["schema"] != "heang.manufactured_event_law.v1" or payload["units"] != SI_UNITS:
        raise ContractError("manufactured fixture schema and SI units required")
    for key in IDENTITIES:
        if not isinstance(payload[key], str) or not payload[key].strip():
            raise ContractError("fixture identity missing: " + key)
    if not isinstance(payload["events"], list) or len(payload["events"]) > MAX_EVENTS:
        raise ContractError("events must be a bounded list of at most 256 entries")
    sigma = exact(payload["sigma"], "sigma")
    if sigma < 0:
        raise ContractError("sigma: nonnegative cross section required")
    args = tuple(payload[key] for key in ("m", "M", "E", "I"))
    if sigma == 0:
        if payload["events"] or payload["normalization"] != "cross_section_weighted":
            raise ContractError("zero sigma requires empty events and cross_section_weighted normalization")
        weighted = zero_cross_section(*args)
        return {"conditional_probability_constructed": False, "conditional": None,
                "cross_section_weighted": serialize_bundle(weighted)}
    if payload["normalization"] != "conditional_event":
        raise ContractError("positive-sigma manufactured fixture uses conditional event weights")
    conditional = integrate_events([Event.from_dict(event) for event in payload["events"]], *args)
    weighted = cross_section_weighted(conditional, sigma)
    return {"conditional_probability_constructed": True,
            "conditional": serialize_bundle(conditional),
            "cross_section_weighted": serialize_bundle(weighted)}


def validate_fixture_bindings(metadata, payload):
    """Match the known manufactured payload semantics to declared metadata."""
    if not isinstance(payload, dict):
        raise ContractError("manufactured payload must be a JSON object")
    for key in IDENTITIES:
        if payload.get(key) != metadata.get(key):
            raise ContractError("payload content identity differs from metadata: " + key)
    if payload.get("normalization") != metadata.get("moment_normalization"):
        raise ContractError("payload moment normalization differs from metadata")
    frame = metadata.get("frame", {})
    if frame.get("name") != "COM" or frame.get("incident_energy") != "relative_COM":
        raise ContractError("manufactured payload schema contains COM momenta and relative COM energy only")
    if metadata.get("support", {}).get("coordinates") != "discrete_events":
        raise ContractError("manufactured payload schema contains discrete event coordinates only")
    kinematics = metadata.get("kinematics", {})
    for field, declared in (("m", "m_kg"), ("M", "M_kg"), ("I", "I_J")):
        if exact(payload.get(field), field) != exact(kinematics.get(declared), declared):
            raise ContractError("payload kinematics differs from metadata: " + field)
    bounds = kinematics.get("incident_COM_energy_J")
    if not isinstance(bounds, (list, tuple)) or len(bounds) != 2:
        raise ContractError("declared COM energy domain requires two exact bounds")
    energy = exact(payload.get("E"), "E")
    if not exact(bounds[0]) <= energy <= exact(bounds[1]):
        raise ContractError("payload incident energy lies outside declared COM energy domain")
    if payload.get("units") != metadata.get("units"):
        raise ContractError("payload units differ from metadata")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("candidate", help="candidate metadata JSON")
    parser.add_argument("--payload-root", help="root for content-bound payload bytes; defaults to candidate directory")
    args = parser.parse_args(argv)
    try:
        candidate = Path(args.candidate)
        metadata = strict_json_loads(read_bytes(candidate))
        payloads = load_payloads(metadata, args.payload_root or candidate.parent)
        precheck = precheck_provider(metadata, payloads)
        output = {"provider_precheck": precheck, "empirical_admission": False, "runtime_activation": False}
        if precheck["status"] in {"REJECTED_INCONSISTENT", "DEFERRED_DEPENDENCY"}:
            print(json.dumps(output, sort_keys=True, allow_nan=False))
            return 2
        if metadata["source_class"] != "manufactured_fixture":
            raise ContractError("this CLI executes manufactured event fixtures only; physical source review is separate")
        name = metadata["bindings"]["moments"]["payload"]
        payload = strict_json_loads(payloads[name])
        validate_fixture_bindings(metadata, payload)
        output["fixture_result"] = validate_fixture_payload(payload)
        print(json.dumps(output, sort_keys=True, allow_nan=False))
        return 0
    except (ContractError, ValueError, TypeError, KeyError, OSError, UnicodeError) as exc:
        print(json.dumps({"status": "REJECTED_INCONSISTENT", "error": str(exc),
                          "empirical_admission": False, "runtime_activation": False}, allow_nan=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
