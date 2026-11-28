"""Source-only event registry using the frozen finite compiler.

No coefficient evaluation, integration, source energy repair, or consumer activation.
The normalized operator accepts event flux only after an independent rate binding.
"""
from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

COMPILER_SHA256 = "60a502895266b6feb96964abc4b24db61c2faed2344db0f7d12f16bb47ed62af"
BASE = Path(__file__).resolve().parent
COMPILER = BASE.parent / "rei_chem_ledger_20261025" / "chem_ledger.py"


def load_compiler():
    if hashlib.sha256(COMPILER.read_bytes()).hexdigest() != COMPILER_SHA256:
        raise ValueError("FROZEN_COMPILER_IDENTITY_CHANGED")
    spec = importlib.util.spec_from_file_location("frozen_chem_ledger", COMPILER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


core = load_compiler()


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def serial(obj):
    if isinstance(obj, Fraction):
        return str(obj)
    if isinstance(obj, dict):
        return {str(k): serial(v) for k, v in obj.items()}
    if isinstance(obj, (tuple, list)):
        return [serial(v) for v in obj]
    return obj


def pairs(side):
    """Retain multiplicity; never divide a column by gcd."""
    if isinstance(side, dict):
        return sorted(side.items())
    return sorted(Counter(side).items())


EXTERNAL = {
    "gamma:incident": (0, 0, 0), "gamma:escaping": (0, 0, 0),
    "antinu_e:escaping": (0, 0, -1), "nu_e:escaping": (0, 0, 1),
    "cosmic_ray_field": (0, 0, 0), "CR_induced_UV_field": (0, 0, 0),
}


def external_delta(side):
    result = [0, 0, 0]
    for name, count in side:
        if name not in EXTERNAL:
            raise ValueError("UNSUPPORTED_EXTERNAL_PARTICLE:" + name)
        if type(count) is not int or count <= 0:
            raise ValueError("INVALID_EXTERNAL_MULTIPLICITY")
        result = [a + count*b for a, b in zip(result, EXTERNAL[name])]
    return result


def external_signature(side):
    external_delta(side)  # validate before reducing repeated labels
    counts = Counter()
    for name, count in side:
        counts[name] += count
    return sorted(counts.items())


def compile_event(event, species_records):
    """Compile a declared number-operator projection, preserving every source gap."""
    if event.get("activation") is not False:
        raise ValueError("SOURCE_INGESTION_CANNOT_ACTIVATE_PROVIDER")
    if not event.get("branch_id"):
        raise ValueError("EXPLICIT_BRANCH_ID_REQUIRED")
    if not event.get("source_id") or not event.get("source_identity"):
        raise ValueError("SOURCE_IDENTITY_REQUIRED")
    if event.get("empirical_rate_admitted") or event.get("nuclear_Q_admitted"):
        raise ValueError("SOURCE_INGESTION_CANNOT_ISSUE_PHYSICAL_ADMISSION")
    species = core.catalog({name: row["compiler_record"] for name, row in species_records.items()})
    reaction = {
        "reactants": event["reactants"], "products": event["products"],
        "kind": event["kind"], "provider": event["source_id"],
        "provider_domain": event["domain"], "frame": event["frame"],
        "process": event["process"], "direction": "forward_as_supplied",
        "state_resolution": event["state_resolution"],
        "ownership_slot": event["ownership_slot"],
        # This is the *operator's* independent variable, not a relabelled k(T).
        "normalization": core.NORMALIZATION,
        "energy_qualification": "PROVIDER_SOURCE_ONLY_NOT_EVENT_ENERGY",
        "energy_partition": "UNBOUND",
    }
    result = core.compile_reaction(reaction, species, {})
    if result["energy"] is not None or result["energy_status"] != "UNQUALIFIED:ENERGY":
        raise ValueError("UNEXPECTED_PHYSICAL_ENERGY_PROMOTION")
    ext_in = external_signature(event["external_reactants"])
    ext_out = external_signature(event["external_products"])
    a, b = external_delta(ext_in), external_delta(ext_out)
    extra = [b[i] - a[i] for i in range(3)]
    # All present external rows have zero electric charge/baryon number.
    # Charged positrons need a separately reviewed extension, never fake nuclei.
    lepton_material = 0
    for name, n in result["nu"].items():
        s = species[name]
        bound = sum(z * count for (z, _a, _m), count in s.composition) - s.charge
        lepton_material += bound * n  # free electron has empty composition, q=-1
    lepton_total = lepton_material + extra[2]
    if result["baryon_delta"] + extra[0] or result["charge_delta"] + extra[1]:
        raise ValueError("TOTAL_PARTICLE_LEDGER_FAILED")
    if lepton_total:
        raise ValueError("ELECTRON_LEPTON_NUMBER_NOT_CONSERVED")
    core_key = serial(core.directed_event_key(reaction, species))
    extended_key = {"core": core_key, "branch": event["branch_id"],
                    "external_in": sorted(ext_in), "external_out": sorted(ext_out),
                    "radiation_count_qualification": event["radiation_count_qualification"]}
    # Ownership groups conservatively ignore provider support differences. Two
    # fits on overlapping or unpartitioned domains cannot both be selected.
    ownership_key = {"left": core_key[0], "right": core_key[1], "process": event["process"],
                     "branch": event["branch_id"], "external_in": ext_in, "external_out": ext_out}
    reversible, orientation = core.reversible_pair_key(reaction, species)
    return {
        "event_id": event["id"], "source_id": event["source_id"],
        "compiler_sha256": COMPILER_SHA256,
        "number_operator_status": "EXACT_INTEGER_PROJECTION_CHECKED",
        "projection_qualification": event["projection_qualification"],
        "stoichiometry": result["nu"],
        "isotope_delta": serial(result["isotope_delta"]),
        "charge_delta": result["charge_delta"], "baryon_delta": result["baryon_delta"],
        "electron_lepton_delta": lepton_total,
        "physical_event_key_sha256": digest(extended_key),
        "ownership_group_sha256": digest(ownership_key),
        "reversible_material_pair_sha256": digest(serial(reversible)),
        "material_pair_orientation": orientation,
        "reverse_rate_inferred": False,
        "provider_record_sha256": event["source_identity"],
        "energy_status": result["energy_status"], "Q_approved": False,
        "native_rate_evaluated": False, "rate_normalization_bound": False,
        "event_rate_unit_if_later_bound": core.NORMALIZATION,
        "activation": False,
    }


def verify_active_ownership(events, compiled):
    """Branch and external particles are part of identity; providers are not.

    Used on hypothetical choices in checks. It does not activate the registry.
    """
    by_id = {r["event_id"]: r for r in compiled}
    seen = {}
    for event in events:
        if event.get("activation") is not True:
            continue
        key = (event["ownership_slot"], by_id[event["id"]]["ownership_group_sha256"])
        if key in seen:
            raise ValueError("OWNER_OVERLAP_UNRESOLVED:" + event["ownership_slot"])
        seen[key] = event["id"]
    return seen


def within_native_intervals(temperature, intervals):
    """Exact declared interval membership only; no interpolation or rate value."""
    t = Fraction(str(temperature))
    return any(Fraction(lo) <= t <= Fraction(hi) for lo, hi in intervals)

