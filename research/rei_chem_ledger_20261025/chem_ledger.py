"""Exact finite isotope/molecule event interface; synthetic ledger, no rates or IVP."""
from dataclasses import dataclass
from fractions import Fraction


NORMALIZATION = "events_per_reference_nucleus_per_proper_second"
RESERVOIRS = ("thermal", "fast", "radiation", "external_source")


class LedgerError(ValueError):
    pass


class Unqualified(LedgerError):
    pass


def exact(value):
    """Accept declared exact rational inputs, avoiding silent float conversion."""
    if isinstance(value, Fraction):
        return value
    if type(value) is int or isinstance(value, str):
        return Fraction(value)
    raise LedgerError("EXACT_RATIONAL_REQUIRED")


def integer(value, label):
    if type(value) is not int:
        raise LedgerError("INTEGER_REQUIRED:" + label)
    return value


@dataclass(frozen=True)
class Species:
    composition: tuple
    charge: int
    state: str
    pool: str

    @classmethod
    def from_record(cls, record):
        composition = {}
        for entry in record["composition"]:
            z = integer(entry["Z"], "Z")
            a = integer(entry["A"], "A")
            isomer = entry["isomer"]
            count = integer(entry["count"], "count")
            if z < 0 or a <= 0 or a < z or not isinstance(isomer, str) or not isomer or count <= 0:
                raise LedgerError("INVALID_NUCLEUS_OR_MULTIPLICITY")
            key = (z, a, isomer)
            composition[key] = composition.get(key, 0) + count
        q = integer(record["charge"], "charge")
        state, pool = record["state"], record["pool"]
        if not isinstance(state, str) or not state:
            raise LedgerError("EXPLICIT_STATE_REQUIRED")
        if pool == "material":
            if not composition or q > sum(k[0] * n for k, n in composition.items()):
                raise LedgerError("INVALID_MATERIAL_CHARGE_OR_COMPOSITION")
        elif pool in ("electron_thermal", "electron_fast"):
            if composition or q != -1:
                raise LedgerError("INVALID_ELECTRON")
        else:
            raise LedgerError("INVALID_POOL")
        return cls(tuple(sorted(composition.items())), q, state, pool)

    def key(self):
        return (self.composition, self.charge, self.state, self.pool)

    def isotope_count(self, nucleus):
        return dict(self.composition).get(nucleus, 0)

    def baryon_count(self):
        return sum(key[1] * n for key, n in self.composition)


def catalog(records):
    result = {name: Species.from_record(row) for name, row in records.items()}
    if len({s.key() for s in result.values()}) != len(result):
        raise LedgerError("DUPLICATE_SPECIES_IDENTITY")
    return result


def side_counts(side, species):
    result = {}
    for name, count in side:
        if name not in species:
            raise LedgerError("UNKNOWN_SPECIES:" + name)
        integer(count, "event_count")
        if count < 0:
            raise LedgerError("NONNEGATIVE_EVENT_MULTIPLICITY_REQUIRED")
        if count:
            result[name] = result.get(name, 0) + count
    return result


def stoichiometry(reaction, species):
    left = side_counts(reaction["reactants"], species)
    right = side_counts(reaction["products"], species)
    return {name: right.get(name, 0) - left.get(name, 0)
            for name in sorted(left.keys() | right.keys())
            if right.get(name, 0) != left.get(name, 0)}


def side_signature(side, species):
    return tuple(sorted((species[name].key(), n) for name, n in side_counts(side, species).items()))


def reversible_pair_key(reaction, species):
    left = side_signature(reaction["reactants"], species)
    right = side_signature(reaction["products"], species)
    pair = tuple(sorted((left, right)))
    orientation = 0 if left == right else (1 if pair[0] == left else -1)
    return pair, orientation


def require_provider(reaction):
    if reaction.get("normalization") != NORMALIZATION:
        raise Unqualified("UNQUALIFIED:PROVIDER_NORMALIZATION")
    for key in ("provider", "provider_domain", "frame", "process", "direction", "state_resolution", "ownership_slot"):
        if not isinstance(reaction.get(key), str) or not reaction[key]:
            raise Unqualified("UNQUALIFIED:MISSING_" + key.upper())


def directed_event_key(reaction, species):
    require_provider(reaction)
    return (side_signature(reaction["reactants"], species),
            side_signature(reaction["products"], species),
            reaction["direction"], reaction["process"], reaction["normalization"],
            reaction["frame"], reaction["provider_domain"], reaction["state_resolution"],
            reaction.get("energy_partition", "explicit_reservoirs"))


def register_ownership(reactions, species):
    active = {}
    for reaction in reactions:
        key = (reaction["ownership_slot"], directed_event_key(reaction, species))
        activation = reaction.get("activation", "active")
        if activation not in ("active", "alternative_inactive"):
            raise LedgerError("INVALID_PROVIDER_ACTIVATION")
        if activation == "alternative_inactive":
            continue
        if key in active:
            raise LedgerError("OWNER_OVERLAP_UNRESOLVED:" + reaction["ownership_slot"])
        active[key] = reaction["provider"]
    return active


def composition_delta(nu, species):
    nuclei = sorted({key for name in nu for key, _ in species[name].composition})
    return {key: sum(species[name].isotope_count(key) * n for name, n in nu.items())
            for key in nuclei}


def conservation(reaction, species):
    nu = stoichiometry(reaction, species)
    isotopes = composition_delta(nu, species)
    charge = sum(species[name].charge * n for name, n in nu.items())
    baryon = sum(species[name].baryon_count() * n for name, n in nu.items())
    kind = reaction["kind"]
    if kind not in ("chemical", "nuclear"):
        raise LedgerError("EXPLICIT_CHEMICAL_OR_NUCLEAR_TYPE_REQUIRED")
    if charge:
        raise LedgerError("CHARGE_NOT_CONSERVED")
    if kind == "chemical" and any(isotopes.values()):
        raise LedgerError("ISOTOPE_NOT_CONSERVED")
    if kind == "nuclear" and baryon:
        raise LedgerError("BARYON_NOT_CONSERVED")
    return {"nu": nu, "isotope_delta": isotopes, "charge_delta": charge, "baryon_delta": baryon}


def qualified_energy(reaction, species, epsilon):
    if reaction.get("energy_qualification") != "SYNTHETIC_EXACT":
        raise Unqualified("UNQUALIFIED:ENERGY")
    participants = side_counts(reaction["reactants"], species).keys() | side_counts(reaction["products"], species).keys()
    for name in participants:
        if name not in epsilon or epsilon[name] in (None, "UNQUALIFIED"):
            raise Unqualified("UNQUALIFIED:EPSILON:" + name)
    reservoirs = reaction.get("reservoirs", {})
    if any(name not in reservoirs for name in RESERVOIRS):
        raise Unqualified("UNQUALIFIED:RESERVOIR_DECLARATION")
    delta = sum((exact(epsilon[name]) * n for name, n in stoichiometry(reaction, species).items()), Fraction(0))
    physical = {name: exact(value) for name, value in reservoirs.items()}
    residual = delta + sum(physical.values(), Fraction(0))
    return {"delta_internal": delta, "Q": -delta, "reservoirs": physical, "residual": residual,
            "diagnostic_tallies": {k: exact(v) for k, v in reaction.get("diagnostic_tallies", {}).items()}}


def compile_reaction(reaction, species, epsilon):
    require_provider(reaction)
    result = conservation(reaction, species)
    try:
        result["energy"] = qualified_energy(reaction, species, epsilon)
        result["energy_status"] = "SYNTHETIC_EXACT"
    except Unqualified as error:
        result["energy"] = None
        result["energy_status"] = str(error)
    result["radiation_count"] = radiation_event(reaction)
    return result


def radiation_event(reaction):
    """A declared signed photon count is separate from material/charge rows."""
    if "photon_count_per_event" not in reaction or "photon_energy_eV" not in reaction:
        return {"qualification": "UNQUALIFIED", "count_per_event": None,
                "energy_eV": None, "energy_increment": None, "energy_residual": None}
    count = Fraction(integer(reaction["photon_count_per_event"], "photon_count_per_event"))
    energy = exact(reaction["photon_energy_eV"])
    if energy <= 0:
        raise LedgerError("POSITIVE_DECLARED_PHOTON_ENERGY_REQUIRED")
    increment = count * energy
    return {"qualification": "SYNTHETIC_SINGLE_ENERGY_PHOTON", "count_per_event": count,
            "energy_eV": energy, "energy_increment": increment,
            "energy_residual": exact(reaction["reservoirs"]["radiation"]) - increment}


def radiation_source(reaction, rate, signed_tangent=False):
    require_provider(reaction)
    r = exact(rate)
    if r < 0 and not signed_tangent:
        raise LedgerError("NEGATIVE_PHYSICAL_RATE")
    event = radiation_event(reaction)
    if event["qualification"] == "UNQUALIFIED":
        return {"qualification": "UNQUALIFIED", "count_source": None, "energy_source": None, "energy_residual": None}
    return {"qualification": event["qualification"], "count_source": event["count_per_event"] * r,
            "energy_source": event["energy_increment"] * r, "energy_residual": event["energy_residual"] * r}


def source(reaction, species, rate, signed_tangent=False):
    require_provider(reaction)
    r = exact(rate)
    if r < 0 and not signed_tangent:
        raise LedgerError("NEGATIVE_PHYSICAL_RATE")
    nu = conservation(reaction, species)["nu"]
    return {name: r * n for name, n in nu.items()}


def source_residuals(dx, species):
    return {"isotopes": composition_delta(dx, species),
            "charge": sum((species[name].charge * value for name, value in dx.items()), Fraction(0)),
            "baryon": sum((species[name].baryon_count() * value for name, value in dx.items()), Fraction(0))}


def neutralizing_diagnostic(abundance, species, reconstructed_electron_source=False):
    if reconstructed_electron_source:
        raise LedgerError("DUPLICATE_ELECTRON_SOURCE_RECONSTRUCTION")
    return sum((s.charge * exact(abundance.get(name, 0)) for name, s in species.items()), Fraction(0))


def reference_delta(reaction, species, epsilon, family, lambdas):
    if family == "isotope_charge" and reaction["kind"] != "chemical":
        raise LedgerError("ISOTOPE_REFERENCE_NOT_APPLICABLE_TO_NUCLEAR")
    if family not in ("isotope_charge", "baryon_charge"):
        raise LedgerError("UNKNOWN_REFERENCE_FAMILY")
    conservation(reaction, species)
    shift = {}
    for name, s in species.items():
        shift[name] = exact(lambdas["charge"]) * s.charge
        if family == "isotope_charge":
            shift[name] += sum((exact(lambdas["isotopes"].get(key, 0)) * n for key, n in s.composition), Fraction(0))
        else:
            shift[name] += exact(lambdas["baryon"]) * s.baryon_count()
    nu = stoichiometry(reaction, species)
    original = sum((exact(epsilon[name]) * n for name, n in nu.items()), Fraction(0))
    shifted = sum(((exact(epsilon[name]) + shift[name]) * n for name, n in nu.items()), Fraction(0))
    return {"original": original, "shifted": shifted, "residual": shifted - original}


def reverse(reaction):
    result = dict(reaction)
    result["reactants"], result["products"] = reaction["products"], reaction["reactants"]
    result["direction"] = "reverse_of:" + reaction["direction"]
    result["reservoirs"] = {k: str(-exact(v)) for k, v in reaction.get("reservoirs", {}).items()}
    result["diagnostic_tallies"] = {k: str(-exact(v)) for k, v in reaction.get("diagnostic_tallies", {}).items()}
    if "photon_count_per_event" in reaction:
        result["photon_count_per_event"] = -reaction["photon_count_per_event"]
    return result
