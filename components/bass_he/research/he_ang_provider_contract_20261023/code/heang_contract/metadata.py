"""Structural provider precheck. Metadata never grants physical admission."""
import hashlib
from pathlib import PurePosixPath
import re

from .exact_events import ContractError, exact


IDENTITIES = ("source_id", "event_law_id", "preparation_id", "angle_source_id")
TOP_FIELDS = set(IDENTITIES) | {
    "schema", "description", "source_class", "bindings", "preparation", "labels",
    "frame", "domain", "support", "uncertainty", "x1", "units", "moment_normalization",
    "kinematics",
}
X1_ALGORITHM_SCIENCE_PIN = "eb03981d15ad291375dd6d574a9c28809f85fc02"


def safe_payload_name(name):
    return (isinstance(name, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_./-]*", name))
            and not PurePosixPath(name).is_absolute()
            and all(part not in {"", ".", ".."} for part in name.split("/")))


def precheck_provider(metadata, payloads=None):
    """Validate declared structure and optional actual bytes; never infer empirical truth.

    payloads maps safe relative names to bytes, not untrusted filesystem paths.
    Unknown/missing calibration evidence stays an explicit dependency.
    X1 decisions are read as records; the X1 code and tests are not imported.
    """
    violations, missing, partial, verified = [], [], [], {}

    def result(status, x1=None, rate_law=None):
        return {"status": status, "violations": sorted(set(violations)),
                "missing_dependencies": sorted(set(missing)), "partial_scope": sorted(set(partial)),
                "payload_verification": verified, "x1_record": x1,
                "rate_law_dependency": rate_law,
                "empirical_admission": False, "runtime_activation": False,
                "interpretation": "Structural evidence only; an independent source review remains required."}

    if not isinstance(metadata, dict):
        violations.append("metadata must be an object")
        return result("REJECTED_INCONSISTENT")
    if any(not isinstance(key, str) for key in metadata):
        violations.append("metadata keys must be strings")
        return result("REJECTED_INCONSISTENT")
    if payloads is not None and not isinstance(payloads, dict):
        violations.append("payloads must map safe names to bytes")
        return result("REJECTED_INCONSISTENT")
    if set(metadata) - TOP_FIELDS:
        violations.append("unknown metadata fields: " + ",".join(sorted(set(metadata) - TOP_FIELDS)))

    def obj(parent, key, path):
        if key not in parent:
            missing.append(path)
            return {}
        value = parent[key]
        if not isinstance(value, dict):
            violations.append(path + " must be an object")
            return {}
        return value

    def text(parent, key, path, allowed=None, required=True):
        if key not in parent or parent[key] is None:
            if required:
                missing.append(path)
            return None
        value = parent[key]
        if not isinstance(value, str) or not value.strip():
            violations.append(path + " must be a nonempty string")
            return None
        if allowed is not None and value not in allowed:
            violations.append(path + " has an unsupported value")
        return value

    text(metadata, "schema", "schema", {"heang.provider_candidate.v1"})
    source_class = text(metadata, "source_class", "source_class",
                        {"manufactured_fixture", "empirical_data", "physical_theory"})
    shared = {key: text(metadata, key, key) for key in IDENTITIES}
    normalization = text(metadata, "moment_normalization", "moment_normalization",
                         {"conditional_event", "cross_section_weighted"})
    units = obj(metadata, "units", "units")
    for key, expected in {"energy": "J", "mass": "kg", "momentum": "kg*m/s", "cross_section": "m^2"}.items():
        text(units, key, "units." + key, {expected})

    kinematics = obj(metadata, "kinematics", "kinematics")
    text(kinematics, "mass_convention", "kinematics.mass_convention", {"HE38_h_equals_M_plus_m"})
    text(kinematics, "target_state", "kinematics.target_state", {"H1_ground"})
    text(kinematics, "domain_reference", "kinematics.domain_reference")
    constants = {}
    for key in ("m_kg", "M_kg", "I_J"):
        if key not in kinematics or kinematics[key] is None:
            missing.append("kinematics." + key)
            continue
        try:
            constants[key] = exact(kinematics[key], "kinematics." + key)
            if constants[key] <= 0:
                violations.append("kinematics." + key + " must be positive")
        except ContractError as exc:
            violations.append(str(exc))
    energy_domain = kinematics.get("incident_COM_energy_J")
    if energy_domain is None:
        missing.append("kinematics.incident_COM_energy_J")
    elif not isinstance(energy_domain, (list, tuple)) or len(energy_domain) != 2:
        violations.append("kinematics.incident_COM_energy_J must have two exact bounds")
    else:
        try:
            low, high = (exact(value, "incident_COM_energy_J") for value in energy_domain)
            if low < 0 or high < low:
                violations.append("incident COM energy bounds must be ordered and nonnegative")
            if normalization == "conditional_event" and "I_J" in constants and low < constants["I_J"]:
                violations.append("conditional event domain extends below declared threshold")
        except ContractError as exc:
            violations.append(str(exc))

    bindings = obj(metadata, "bindings", "bindings")
    if set(bindings) - {"sigma", "electron", "moments", "correlation"}:
        violations.append("bindings contains unknown components")
    for component in ("sigma", "electron", "moments", "correlation"):
        if component not in bindings and component == "correlation":
            partial.append("same-law joint correlation or equivalent ion tensor not supplied")
            continue
        binding = obj(bindings, component, "bindings." + component)
        if set(binding) - (set(IDENTITIES) | {"payload", "sha256"}):
            violations.append("bindings." + component + " contains unknown fields")
        for key in IDENTITIES:
            value = text(binding, key, f"bindings.{component}.{key}")
            if value is not None and shared[key] is not None and value != shared[key]:
                violations.append(f"bindings.{component}.{key} differs from common source law")
        name = text(binding, "payload", f"bindings.{component}.payload")
        digest = text(binding, "sha256", f"bindings.{component}.sha256")
        if name is not None and not safe_payload_name(name):
            violations.append(f"bindings.{component}.payload is not a safe relative name")
            continue
        if digest is not None and not re.fullmatch(r"[0-9a-f]{64}", digest):
            violations.append(f"bindings.{component}.sha256 must be 64 lowercase hex digits")
            continue
        if name is None or digest is None:
            continue
        if payloads is None or name not in payloads:
            missing.append("actual payload bytes: " + name)
            continue
        if not isinstance(payloads[name], bytes):
            violations.append("payload " + name + " must contain bytes")
            continue
        actual = hashlib.sha256(payloads[name]).hexdigest()
        verified[name] = {"declared_sha256": digest, "actual_sha256": actual, "matches": actual == digest}
        if actual != digest:
            violations.append("content digest mismatch: " + name)

    preparation = obj(metadata, "preparation", "preparation")
    prep_id = text(preparation, "id", "preparation.id")
    if prep_id is not None and shared["preparation_id"] is not None and prep_id != shared["preparation_id"]:
        violations.append("preparation.id differs from bound preparation_id")
    prep_kind = text(preparation, "kind", "preparation.kind", {"unpolarized_isotropic", "specified"})
    text(preparation, "reference", "preparation.reference")
    text(preparation, "description", "preparation.description")
    rate_law = "sigma(E) under declared isotropic unpolarized preparation" if prep_kind == "unpolarized_isotropic" else "sigma(E,a;preparation)"

    labels = obj(metadata, "labels", "labels")
    convention = text(labels, "convention", "labels.convention",
                      {"unordered_physical_events", "ordered_exchange_symmetric", "energy_ordered_with_partner"})
    for key, value in (("inclusive_count", 2), ("ion_count", 1)):
        if key not in labels:
            missing.append("labels." + key)
        elif type(labels[key]) is not int or labels[key] != value:
            violations.append("labels." + key + " has wrong type or value")
    exchange = text(labels, "exchange", "labels.exchange",
                    {"source_included", "manufactured_label_symmetry", "unresolved"})
    text(labels, "exchange_reference", "labels.exchange_reference")
    if exchange == "unresolved":
        missing.append("physical exchange convention")
    if exchange == "manufactured_label_symmetry" and source_class != "manufactured_fixture":
        violations.append("manufactured label symmetry is not a physical exchange source")
    slow = text(labels, "slow_electron_support", "labels.slow_electron_support",
                {"full_inclusive", "partial_inclusive", "slow_only"})
    if slow in {"partial_inclusive", "slow_only"}:
        partial.append("electron coverage is " + slow)
    if convention == "energy_ordered_with_partner":
        text(labels, "partner_reference", "labels.partner_reference")

    frame = obj(metadata, "frame", "frame")
    frame_name = text(frame, "name", "frame.name", {"COM", "LAB"})
    incident = text(frame, "incident_energy", "frame.incident_energy", {"relative_COM", "projectile_lab"})
    text(frame, "axis", "frame.axis", {"relative_incident_velocity"})
    text(frame, "relative_flux", "frame.relative_flux", {"relative_speed"})
    text(frame, "target_motion", "frame.target_motion")
    if frame_name == "LAB" or incident == "projectile_lab":
        text(frame, "map_reference", "frame.map_reference")

    domain = obj(metadata, "domain", "domain")
    coverage = text(domain, "coverage", "domain.coverage", {"full", "partial"})
    text(domain, "reference", "domain.reference")
    text(domain, "extrapolation", "domain.extrapolation", {"none"})
    if coverage == "partial":
        partial.append("source has a declared partial domain")
        text(domain, "missing_domain_reference", "domain.missing_domain_reference")
    support = obj(metadata, "support", "support")
    density = text(support, "coordinates", "support.coordinates",
                   {"discrete_events", "momentum_measure", "energy_solid_angle", "fivefold_joint_shell_density"})
    text(support, "event_support_reference", "support.event_support_reference")
    if density in {"energy_solid_angle", "fivefold_joint_shell_density"}:
        text(support, "jacobian_reference", "support.jacobian_reference")
    if density == "fivefold_joint_shell_density":
        text(support, "root_convention_reference", "support.root_convention_reference")

    uncertainty = obj(metadata, "uncertainty", "uncertainty")
    if "separate_ledgers" not in uncertainty:
        missing.append("uncertainty.separate_ledgers")
    elif uncertainty["separate_ledgers"] is not True:
        violations.append("physical uncertainty and numerical error must have separate ledgers")
    physical = obj(uncertainty, "physical", "uncertainty.physical")
    physical_status = text(physical, "status", "uncertainty.physical.status",
                           {"calibrated", "unknown", "not_applicable_manufactured"})
    text(physical, "reference", "uncertainty.physical.reference")
    if physical_status == "unknown":
        missing.append("physical uncertainty calibration")
    if physical_status == "not_applicable_manufactured" and source_class != "manufactured_fixture":
        violations.append("physical source cannot use manufactured uncertainty exemption")
    numerical = obj(uncertainty, "numerical", "uncertainty.numerical")
    numerical_status = text(numerical, "status", "uncertainty.numerical.status",
                            {"calibrated", "unknown", "exact_rational_arithmetic"})
    text(numerical, "reference", "uncertainty.numerical.reference")
    if numerical_status == "unknown":
        missing.append("numerical error calibration")

    x1 = obj(metadata, "x1", "x1")
    decision = text(x1, "decision", "x1.decision", {"PASS", "FAIL", "INDETERMINATE"})
    algorithm_pin = text(x1, "algorithm_science_pin", "x1.algorithm_science_pin")
    if algorithm_pin is not None and algorithm_pin != X1_ALGORITHM_SCIENCE_PIN:
        violations.append("x1.algorithm_science_pin differs from the frozen reused algorithm evidence")
    text(x1, "algorithm_evidence_reference", "x1.algorithm_evidence_reference")
    candidate_digest = text(x1, "candidate_moments_sha256", "x1.candidate_moments_sha256")
    moment_binding = bindings.get("moments", {})
    if candidate_digest is not None:
        if not re.fullmatch(r"[0-9a-f]{64}", candidate_digest):
            violations.append("x1.candidate_moments_sha256 must be a 64-digit digest")
        elif isinstance(moment_binding, dict) and moment_binding.get("sha256") != candidate_digest:
            violations.append("X1 candidate certificate is not bound to the current moments payload")
    text(x1, "candidate_evidence_kind", "x1.candidate_evidence_kind",
         {"direct_event_support_algebra", "separately_recorded_candidate_certificate"})
    text(x1, "candidate_certificate_provenance", "x1.candidate_certificate_provenance")
    text(x1, "candidate_evidence_reference", "x1.candidate_evidence_reference")
    text(x1, "candidate_execution_status", "x1.candidate_execution_status",
         {"NOT_RUN_ANALYTIC_SUPPORT", "RECORDED_SEPARATELY"})
    text(x1, "source_uncertainty", "x1.source_uncertainty",
         {"not_supplied", "supplied", "exact_mathematical_fixture"})
    if x1.get("represented_input_only") is not True:
        missing.append("x1.represented_input_only qualification")
    if decision == "FAIL":
        violations.append("inherited X1 record reports FAIL")
    elif decision == "INDETERMINATE":
        missing.append("inherited X1 numerical boundary remains INDETERMINATE")

    if violations:
        status = "REJECTED_INCONSISTENT"
    elif missing:
        status = "DEFERRED_DEPENDENCY"
    elif partial:
        status = "PARTIAL_SCOPED"
    else:
        status = "STRUCTURALLY_READY_REQUIRES_SOURCE_REVIEW"
    return result(status, dict(x1), rate_law)
