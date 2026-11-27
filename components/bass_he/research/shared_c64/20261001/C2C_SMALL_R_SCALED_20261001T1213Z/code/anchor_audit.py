"""Pure scalar C2c spherical-anchor evaluator; no file I/O or scientific calls.

API: evaluate_anchors(observations, selected_prolate, contract, *, state_values=None)
observations maps l72/l96 and optional h80/p5 to observe_pair returned values.
state_values maps the same labels to [m0 DATA.value, m1 DATA.value].  It may
alternatively be embedded in each observation as its `state_values` member.
Use merge_observation_values(initial, fallback) to combine frozen q evaluations.
Malformed/missing evidence is UNKNOWN, numerical excess is FAIL, all gates must
be PASS for acceptance.  Energy has a raw-only registered criterion.
"""
from copy import deepcopy
import hashlib
import json
import math


class InputError(ValueError):
    pass


def _number(value, where):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise InputError(f"{where} must be a finite real scalar")
    return float(value)


def _vector(value, where):
    if not isinstance(value, (list, tuple)) or len(value) != 2:
        raise InputError(f"{where} must contain exactly two ordered sector scalars")
    return [_number(x, f"{where}[{i}]") for i, x in enumerate(value)]


def _mapping(value, where):
    if not isinstance(value, dict):
        raise InputError(f"{where} must be an object")
    return value


def _field(value, name, where):
    if name not in value:
        raise InputError(f"missing {where}.{name}")
    return value[name]


def _scalar(value, name, where):
    return _number(_field(value, name, where), f"{where}.{name}")


def _status(gates):
    values = [g["status"] for g in gates]
    if any(value == "UNKNOWN" for value in values):
        return "UNKNOWN"
    if not values or any(value != "PASS" for value in values):
        return "FAIL"
    return "PASS"


def _add(gates, name, value, threshold, **details):
    value, threshold = _number(value, name), _number(threshold, name+".threshold")
    if threshold < 0 or value < 0:
        raise InputError("nonnegative error and threshold required")
    gates.append(dict(name=name, status="PASS" if value <= threshold else "FAIL",
                      value=value, threshold=threshold, **details))


def _exact(gates, name, actual, expected):
    gates.append(dict(name=name, status="PASS" if actual == expected else "FAIL",
                      actual=actual, expected=expected))


def _unknown(gates, name, reason):
    gates.append(dict(name=name, status="UNKNOWN", reason=str(reason)))


def merge_observation_values(*values):
    """Merge only quadrature maps from otherwise identical frozen observations.

    Duplicate orders must have byte-semantic identical scalar records.  This
    function raises InputError on ambiguity; it never selects an attractive row.
    """
    if not values:
        raise InputError("at least one observation is required")
    first = deepcopy(_mapping(values[0], "observation"))
    _mapping(first.get("direct"), "observation.direct")
    for value in values[1:]:
        value = _mapping(value, "observation")
        if {k: v for k, v in first.items() if k != "direct"} != {
                k: v for k, v in value.items() if k != "direct"}:
            raise InputError("cannot merge observations from different frozen states/metadata")
        for key, row in _mapping(value.get("direct"), "observation.direct").items():
            if key in first["direct"] and first["direct"][key] != row:
                raise InputError(f"conflicting duplicate quadrature order {key}")
            first["direct"][key] = deepcopy(row)
    return first


def _contract(contract):
    contract = _mapping(contract, "contract")
    anchor = _mapping(_field(contract, "spherical_anchor", "contract"), "spherical_anchor")
    raw = _mapping(_field(contract, "raw_criteria", "contract"), "raw_criteria")
    scaled = _mapping(_field(contract, "scaled_criteria", "contract"), "scaled_criteria")
    R = _scalar(anchor, "R", "spherical_anchor")
    if R <= 0 or R**3 == 0:
        raise InputError("positive nonsingular anchor R required")
    for name in ("independent_spherical_L_O_abs", "independent_spherical_energy_abs",
                 "independent_spherical_increment_abs", "algebraic_residual_relative",
                 "norm_error_abs", "operator_quadrature_abs", "momentum_gap_dipole_abs",
                 "origin_identity_abs", "energy_refinement_abs"):
        if _scalar(raw, name, "raw_criteria") < 0:
            raise InputError("negative raw tolerance")
    for name in ("spherical_L_O_agreement_abs", "spherical_L_O_increment_abs",
                 "spherical_L_O_quadrature_abs", "momentum_induced_L_O_abs", "origin_identity_abs"):
        if _scalar(scaled, name, "scaled_criteria") < 0:
            raise InputError("negative scaled tolerance")
    if anchor.get("sectors") != [0, 1] or contract.get("charges") != [1, 2]:
        raise InputError("unsupported charge or sector convention")
    initial, extra = anchor.get("operator_orders"), anchor.get("fallback_operator_orders")
    if (not isinstance(initial, list) or len(initial) != 3 or not isinstance(extra, list)
            or len(extra) != 2 or any(type(x) is not int or x < 1 for x in initial+extra)
            or any(a >= b for a, b in zip(initial+extra, (initial+extra)[1:]))):
        raise InputError("invalid registered spherical quadrature ladder")
    return anchor, raw, scaled, R, initial, extra


def _direct_row(row, where):
    row = _mapping(row, where)
    return {name: _scalar(row, name, where) for name in (
        "L_O_over_minus_i_hbar", "L_center_over_minus_i_hbar",
        "p_x_over_minus_i_hbar", "dipole_x", "origin_shift_center_to_O")}


def _one_level(label, observation, quality, specification, anchor, raw, scaled, R, initial, extra):
    gates, diagnostics = [], {}
    result = dict(label=label, gates=gates, diagnostics=diagnostics)
    try:
        value = _mapping(observation, label)
        _exact(gates, "R", _scalar(value, "R", label), R)
        _exact(gates, "sectors", value.get("sectors"), [0, 1])
        _exact(gates, "new_eigensolves_in_observer", value.get("new_eigensolves"), 0)
        energies = _vector(value.get("energies"), label+".energies")
        phases = _vector(value.get("phase_probes"), label+".phase_probes")
        if min(phases) <= 0:
            raise InputError("nonpositive archived phase; no absolute-value refitting allowed")
        result["energies"] = energies
        direct = _mapping(value.get("direct"), label+".direct")
        keys = list(direct)
        if any(not isinstance(k, str) or not k.isdecimal() or str(int(k)) != k for k in keys):
            raise InputError("quadrature keys must be canonical decimal strings")
        orders = sorted(int(k) for k in keys)
        if orders not in (initial, initial+extra):
            raise InputError("need exactly initial three or complete five registered quadrature orders")
        terminal = orders[-3:]
        result.update(orders=orders, terminal_orders=terminal)
        rows = {q: _direct_row(direct[str(q)], f"{label}.direct.{q}") for q in orders}
        shift, gap = R/3, energies[1]-energies[0]
        if gap <= 0:
            raise InputError("nonpositive selected-sector energy gap")
        condition = {}
        for q in terminal:
            row = rows[q]
            p, d = row["p_x_over_minus_i_hbar"], row["dipole_x"]
            local, total = row["L_center_over_minus_i_hbar"], row["L_O_over_minus_i_hbar"]
            _exact(gates, f"q{q}.origin_center", direct[str(q)].get("origin_center"), "B")
            _exact(gates, f"q{q}.origin_shift", row["origin_shift_center_to_O"], shift)
            momentum_error = abs(p-gap*d)
            origin_error = abs(total-local-shift*p)
            _add(gates, f"q{q}.momentum_raw", momentum_error, raw["momentum_gap_dipole_abs"])
            _add(gates, f"q{q}.momentum_induced_scaled", momentum_error/(3*R**2), scaled["momentum_induced_L_O_abs"])
            _add(gates, f"q{q}.origin_raw", origin_error, raw["origin_identity_abs"])
            _add(gates, f"q{q}.origin_scaled", origin_error/R**3, scaled["origin_identity_abs"])
            condition[str(q)] = (abs(local)+abs(shift*p))/abs(total) if total != 0 else None
        for qa, qb in zip(terminal[:-1], terminal[1:]):
            for key in ("L_O_over_minus_i_hbar", "L_center_over_minus_i_hbar", "p_x_over_minus_i_hbar", "dipole_x"):
                delta = abs(rows[qb][key]-rows[qa][key])
                _add(gates, f"q{qa}_to_q{qb}.{key}.raw", delta, raw["operator_quadrature_abs"])
                if key == "L_O_over_minus_i_hbar":
                    _add(gates, f"q{qa}_to_q{qb}.L_O_scaled", delta/R**3, scaled["spherical_L_O_quadrature_abs"])
        result["selected_order"] = orders[-1]
        result["L_O_bar"] = rows[orders[-1]]["L_O_over_minus_i_hbar"]
        result["L_O_scaled"] = result["L_O_bar"]/R**3
        result["initial_terminal_L_O_bar"] = rows[initial[-1]]["L_O_over_minus_i_hbar"]
        diagnostics.update(cancellation_condition=condition, gap=gap,
                           origin_check_scope="construction identity, not independent physics evidence")
        if quality is None:
            quality = value.get("state_values")
        if not isinstance(quality, (list, tuple)) or len(quality) != 2:
            raise InputError("state_values for both ordered sectors required for norm/residual evidence")
        identities = value.get("states")
        if not isinstance(identities, list) or len(identities) != 2:
            raise InputError("observer must carry two archived state identities")
        for m, state in enumerate(quality):
            state = _mapping(state, f"{label}.state_values.{m}")
            residual = _scalar(state, "residual", label)
            if residual < 0:
                raise InputError("negative algebraic residual")
            _add(gates, f"m{m}.residual", residual, raw["algebraic_residual_relative"])
            _add(gates, f"m{m}.norm", abs(_scalar(state, "mass_norm", label)-1), raw["norm_error_abs"])
            _exact(gates, f"m{m}.energy_binding", _scalar(state, "energy", label), energies[m])
            _exact(gates, f"m{m}.phase_binding", _scalar(state, "phase_probe", label), phases[m])
            for key in ("state_sha256", "state_bytes"):
                expected = _field(_mapping(identities[m], label+".states"), key, label+".states")
                _exact(gates, f"m{m}.{key}_binding", _field(state, key, label), expected)
            meta = _mapping(state.get("metadata"), label+".metadata")
            for key, expected in (("origin_center", "B"), ("origin_shift_center_to_O", shift),
                                  ("nuclear_positions", [-R, 0.]), ("angular_lmax", specification["lmax"]),
                                  ("degree", specification["degree"]), ("rmax", specification["rmax"]),
                                  ("radial_quadrature", specification["quadrature"])):
                _exact(gates, f"m{m}.metadata.{key}", meta.get(key), expected)
    except (InputError, KeyError, TypeError, OverflowError, ZeroDivisionError) as exc:
        _unknown(gates, "complete_scalar_input", exc)
    result["status"] = _status(gates)
    return result


def evaluate_anchors(observations, selected_prolate, contract, *, state_values=None):
    """Return a JSON-safe fail-closed scalar audit; does not open any paths.

    The caller must separately bind these scalars to verified DATA/RESULT/source
    identities.  Acceptance here does not re-certify the selected prolate quartet.
    No threshold is inferred from results or from the analytic cubic coefficient.
    """
    result = dict(schema="c2c-spherical-anchor-scalar-audit-v1", status="UNKNOWN", accepted=False,
                  levels={}, comparisons=[], gates=[], initial_primary={}, fallback_used=False,
                  failures=[], unknown=[], new_eigensolves=0, new_operator_integrations=0,
                  scope="one-point independent representation sanity check; empirical only",
                  energy_scaling="raw energy agreement only; no registered scaled energy gate",
                  identity_scope="caller must verify source/task/archive provenance before scalar admission",
                  prolate_selection_scope="selected prolate quartet acceptance is caller-owned",
                  full_C2_closed=False)
    try:
        anchor, raw, scaled, R, initial, extra = _contract(contract)
        result["contract_canonical_json_sha256"] = hashlib.sha256(json.dumps(
            contract, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()
        result["R"] = R
        observations = _mapping(observations, "observations")
        if state_values is not None:
            state_values = _mapping(state_values, "state_values")
        allowed = {"l72", "l96", "h80", "p5"}
        if not set(observations) <= allowed:
            raise InputError("unregistered anchor labels")
        fallback = bool({"h80", "p5"} & set(observations))
        result["fallback_used"] = fallback
        labels = ["l72", "l96"]+(["h80", "p5"] if fallback else [])
        if not set(labels) <= set(observations):
            raise InputError("both initial labels and, when used, both fallback labels are required")
        specifications = {**anchor["configurations"], **anchor["fallback_configurations"]}
        for label in labels:
            result["levels"][label] = _one_level(label, observations[label],
                state_values.get(label) if state_values is not None else None,
                specifications[label], anchor, raw, scaled, R, initial, extra)
        prolate = _mapping(selected_prolate, "selected_prolate")
        _exact(result["gates"], "prolate_R", _scalar(prolate, "R", "selected_prolate"), R)
        energies = _vector(prolate.get("energies"), "selected_prolate.energies")
        p_direct = _mapping(prolate.get("direct"), "selected_prolate.direct")
        p_orders = sorted(int(k) for k in p_direct if isinstance(k, str) and k.isdecimal() and str(int(k)) == k)
        registered_prolate = contract["operators"]["direct_orders"]+contract["operators"]["fallback_direct_orders"]
        if len(p_orders) != len(p_direct) or not p_orders or not set(p_orders) <= set(registered_prolate):
            raise InputError("invalid selected prolate direct quadrature keys")
        target = _scalar(_mapping(p_direct[str(p_orders[-1])], "prolate direct"), "L_O_bar", "prolate direct")
        result["prolate_selected_order"] = p_orders[-1]
        for label in ["l96"]+(["h80", "p5"] if fallback else []):
            level, gates = result["levels"][label], []
            if "L_O_bar" not in level or "energies" not in level:
                _unknown(gates, "comparison_input", f"missing evaluated {label} scalars")
            else:
                delta = abs(level["L_O_bar"]-target)
                energy_abs = [abs(a-b) for a, b in zip(level["energies"], energies)]
                _add(gates, "L_O_agreement_raw", delta, raw["independent_spherical_L_O_abs"])
                _add(gates, "L_O_agreement_scaled", delta/R**3, scaled["spherical_L_O_agreement_abs"])
                for m, error in enumerate(energy_abs):
                    _add(gates, f"m{m}.energy_agreement_raw", error, raw["independent_spherical_energy_abs"])
            result["comparisons"].append(dict(label=label, gates=gates, status=_status(gates)))
        low, high = result["levels"]["l72"], result["levels"]["l96"]
        if "L_O_bar" not in low or "L_O_bar" not in high:
            raise InputError("initial angular levels lack complete coupling scalars")
        angular = abs(high["L_O_bar"]-low["L_O_bar"])
        _add(result["gates"], "original_l72_to_l96_increment_raw", angular, raw["independent_spherical_increment_abs"])
        _add(result["gates"], "original_l72_to_l96_increment_scaled", angular/R**3, scaled["spherical_L_O_increment_abs"])
        initial_delta = abs(high["initial_terminal_L_O_bar"]-low["initial_terminal_L_O_bar"])
        initial_agreement = abs(high["initial_terminal_L_O_bar"]-target)
        result["initial_primary"] = dict(order=initial[-1], angular_increment_raw=initial_delta,
            angular_increment_scaled=initial_delta/R**3, L_O_agreement_raw=initial_agreement,
            L_O_agreement_scaled=initial_agreement/R**3,
            note="Preserved initial-order scalar checks; current comparison uses caller-selected prolate state.")
        result["angular_energy_increment_raw_diagnostic"] = [abs(a-b) for a, b in zip(high["energies"], low["energies"])]
        if fallback:
            current = [result["levels"][key] for key in ("l96", "h80", "p5")]
            if any("L_O_bar" not in level or "energies" not in level for level in current):
                raise InputError("fallback labels lack complete scalar observables")
            values = [level["L_O_bar"] for level in current]
            spread = max(values)-min(values)
            _add(result["gates"], "fallback_l96_h80_p5_spread_raw", spread, raw["independent_spherical_increment_abs"])
            _add(result["gates"], "fallback_l96_h80_p5_spread_scaled", spread/R**3, scaled["spherical_L_O_increment_abs"])
            for m in (0, 1):
                values = [level["energies"][m] for level in current]
                _add(result["gates"], f"fallback_m{m}.energy_spread_raw", max(values)-min(values), raw["energy_refinement_abs"])
            result["fallback_selection_policy"] = "retain l96 comparison, require h80 and p5 agreement and joint spatial spread; no best-result selection"
    except (InputError, KeyError, TypeError, ValueError, OverflowError, ZeroDivisionError) as exc:
        _unknown(result["gates"], "complete_audit_input", exc)
    all_gates = [("anchor", gate) for gate in result["gates"]]
    for label, level in result["levels"].items():
        all_gates.extend((label, gate) for gate in level["gates"])
    for comparison in result["comparisons"]:
        all_gates.extend((comparison["label"]+".vs_prolate", gate) for gate in comparison["gates"])
    result["failures"] = [dict(scope=scope, **gate) for scope, gate in all_gates if gate["status"] == "FAIL"]
    result["unknown"] = [dict(scope=scope, **gate) for scope, gate in all_gates if gate["status"] == "UNKNOWN"]
    result["status"] = _status([gate for _, gate in all_gates])
    result["accepted"] = result["status"] == "PASS"
    return result
