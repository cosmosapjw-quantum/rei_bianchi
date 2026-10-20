"""Pure, frozen-bath rate-edge defect controls. No physical rate providers.

Column-generator convention: pair (i, j) is forward i -> j, backward j -> i.
All inputs are ordinary finite real numbers; outputs use floating arithmetic.
Panel certificates are conditional on caller-supplied continuous suprema.
"""

from dataclasses import dataclass
import math
from numbers import Integral, Real
from typing import Optional


def _real(value, name, nonnegative=False):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name} must be a finite real number")
    try:
        value = float(value)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"{name} must be finite") from exc
    if not math.isfinite(value) or (nonnegative and value < 0):
        raise ValueError(f"{name} must be finite" + (" and nonnegative" if nonnegative else ""))
    return value


def _vector(values, name, length=None, nonnegative=False):
    try:
        values = tuple(values)
    except TypeError as exc:
        raise ValueError(f"{name} must be an iterable") from exc
    if length is not None and len(values) != length:
        raise ValueError(f"{name} has length {len(values)}; expected {length}")
    return tuple(_real(x, name, nonnegative) for x in values)


def _finite(value, name):
    if not math.isfinite(value):
        raise ValueError(f"nonfinite arithmetic result in {name}")
    return value


def _sum(values, name):
    try:
        return _finite(math.fsum(values), name)
    except (OverflowError, ValueError) as exc:
        raise ValueError(f"nonfinite arithmetic result in {name}") from exc


def _network(n, pairs, population):
    if isinstance(n, bool) or not isinstance(n, Integral) or n < 0:
        raise ValueError("n must be a nonnegative integer")
    population = _vector(population, "population", n)
    try:
        pairs = tuple(tuple(pair) for pair in pairs)
    except TypeError as exc:
        raise ValueError("pairs must be iterable pairs of indices") from exc
    seen = set()
    for pair in pairs:
        if len(pair) != 2:
            raise ValueError("each pair must have two indices")
        i, j = pair
        if any(isinstance(x, bool) or not isinstance(x, Integral) for x in pair):
            raise ValueError("edge indices must be integers")
        if not (0 <= i < n and 0 <= j < n):
            raise ValueError("edge index outside state range")
        if i == j:
            raise ValueError("self edge is not permitted")
        key = (min(i, j), max(i, j))
        if key in seen:
            raise ValueError("duplicate unordered pair; aggregate subchannels first")
        seen.add(key)
    return pairs, population


@dataclass(frozen=True)
class EdgeDefect:
    exact_defect: Optional[tuple]
    exact_l1: Optional[float]
    signed_pair_defects: Optional[tuple]
    pair_triangle_bound: Optional[float]
    independent_rate_majorant: Optional[float]
    negative_population_indices: tuple
    source_difference: tuple
    source_mass_difference: float
    source_l1: float
    combined_defect: Optional[tuple]
    combined_l1: Optional[float]
    combined_majorant: Optional[float]


def assemble_rate_defect(n, pairs, population, *, delta_forward=None,
                         delta_backward=None, absolute_forward=None,
                         absolute_backward=None, source_difference=None):
    """Assemble (K_hat-K)p in O(E+N), preserving the supplied orientation.

    Supply both signed delta arrays, both nonnegative absolute-error arrays,
    or both sets. If both are supplied, each eta must bound |delta|. For a
    delta-only call, |delta| itself supplies an independent absolute majorant.
    Negative p is retained and reported, and the majorant uses |p|.
    source_difference, when supplied, is b_hat-b in the same clock as K.
    No summation error enclosure is claimed by these floating-point values.
    """
    pairs, p = _network(n, pairs, population)
    edges = len(pairs)
    have_delta = delta_forward is not None or delta_backward is not None
    have_bounds = absolute_forward is not None or absolute_backward is not None
    if have_delta and (delta_forward is None or delta_backward is None):
        raise ValueError("both signed delta arrays are required")
    if have_bounds and (absolute_forward is None or absolute_backward is None):
        raise ValueError("both absolute bound arrays are required")
    if not have_delta and not have_bounds:
        raise ValueError("supply signed rate differences or absolute rate bounds")
    df = _vector(delta_forward, "delta_forward", edges) if have_delta else None
    db = _vector(delta_backward, "delta_backward", edges) if have_delta else None
    af = _vector(absolute_forward, "absolute_forward", edges, True) if have_bounds else None
    ab = _vector(absolute_backward, "absolute_backward", edges, True) if have_bounds else None
    if have_delta and have_bounds:
        if any(abs(x) > a or abs(y) > b for x, y, a, b in zip(df, db, af, ab)):
            raise ValueError("absolute bounds do not enclose supplied rate differences")
    if not have_bounds:
        af, ab = tuple(map(abs, df)), tuple(map(abs, db))

    # Lists of signed contributions permit accurate fsum at each vertex while
    # retaining O(E+N) time and memory, including sparse/isolated states.
    contributions = [[] for _ in range(n)] if have_delta else None
    signed = [] if have_delta else None
    majorant_terms = []
    for edge, (i, j) in enumerate(pairs):
        majorant_terms.extend((af[edge] * abs(p[i]), ab[edge] * abs(p[j])))
        if have_delta:
            d = _sum((df[edge] * p[i], -db[edge] * p[j]), "pair defect")
            signed.append(d)
            contributions[i].append(-d)
            contributions[j].append(d)
    independent = _finite(2 * _sum(majorant_terms, "independent majorant"), "independent majorant")
    exact = tuple(_sum(v, "state defect") for v in contributions) if have_delta else None
    l1 = _sum(map(abs, exact), "exact l1") if have_delta else None
    triangle = _finite(2 * _sum(map(abs, signed), "pair triangle"), "pair triangle") if have_delta else None
    source = (0.0,) * n if source_difference is None else _vector(source_difference, "source_difference", n)
    source_mass = _sum(source, "source mass")
    source_l1 = _sum(map(abs, source), "source l1")
    combined = tuple(_sum((x, s), "combined defect") for x, s in zip(exact, source)) if have_delta else None
    combined_l1 = _sum(map(abs, combined), "combined l1") if have_delta else None
    return EdgeDefect(exact, l1, tuple(signed) if have_delta else None, triangle,
                      independent, tuple(i for i, x in enumerate(p) if x < 0),
                      source, source_mass, source_l1, combined, combined_l1,
                      _sum((independent, source_l1), "combined majorant"))


@dataclass(frozen=True)
class CommonRelativeDefect:
    declared_relative_perturbations: tuple
    unperturbed_net_fluxes: tuple
    edge_result: EdgeDefect


def declared_common_relative_defect(n, pairs, population, forward_rates,
                                    backward_rates, relative_perturbations):
    """Explicitly impose delta_f=epsilon*k_f AND delta_b=epsilon*k_b.

    One epsilon per pair, shared by that pair's two directions. This identity
    is the caller's declaration; equal independent error bounds do not imply it.
    epsilon >= -1 ensures the reconstructed rates stay nonnegative.
    """
    pairs, p = _network(n, pairs, population)
    kf = _vector(forward_rates, "forward_rates", len(pairs), True)
    kb = _vector(backward_rates, "backward_rates", len(pairs), True)
    eps = _vector(relative_perturbations, "relative_perturbations", len(pairs))
    if any(x < -1 for x in eps):
        raise ValueError("common relative perturbation must be >= -1")
    df = tuple(_finite(e * k, "common forward difference") for e, k in zip(eps, kf))
    db = tuple(_finite(e * k, "common backward difference") for e, k in zip(eps, kb))
    net = tuple(_sum((f * p[i], -b * p[j]), "net flux")
                for (i, j), f, b in zip(pairs, kf, kb))
    return CommonRelativeDefect(eps, net, assemble_rate_defect(
        n, pairs, p, delta_forward=df, delta_backward=db))


def observable_mixed_bound(weights, l1_error_bound, *, mass_error_bound=None):
    """Bound |w^T e|; M=0 must be explicitly justified by matched mass.

    Without M, use ||w||_infinity E. With |sum e| <= M, use
    (max(w)-min(w))/2 E + |(max(w)+min(w))/2| M.
    """
    w = _vector(weights, "weights")
    error = _real(l1_error_bound, "l1_error_bound", True)
    mass = None if mass_error_bound is None else _real(mass_error_bound, "mass_error_bound", True)
    if not w:
        return 0.0
    if mass is None:
        return _finite(max(map(abs, w)) * error, "observable bound")
    # Half first to avoid an unnecessary overflow from adding finite weights.
    lo, hi = min(w), max(w)
    radius, center = hi / 2 - lo / 2, hi / 2 + lo / 2
    return _sum((radius * error, abs(center) * mass), "observable mixed bound")


@dataclass(frozen=True)
class IntegralBound:
    status: str
    clock: str
    panel_integral: Optional[float]
    event_total: float
    total: Optional[float]
    premise: str


def _integral_inputs(widths, event_l1_bounds, clock):
    widths = _vector(widths, "widths", nonnegative=True)
    events = _vector(event_l1_bounds, "event_l1_bounds", nonnegative=True)
    if not isinstance(clock, str) or not clock.strip():
        raise ValueError("clock must explicitly name the integration coordinate")
    return widths, _sum(events, "event total")


def panel_supremum_integral_bound(widths, *, supremum_bounds=None,
                                 supremum_provenance=None, samples=None,
                                 event_l1_bounds=(), clock):
    """Sum width*supremum + event bounds, conditional on continuous enclosures.

    The integrand must already be the defect per unit of the stated clock.
    For x clocks this includes dt/dx exactly once. No Jacobian is inferred.
    Suprema require caller-supplied provenance; sampled values alone return
    unresolved_samples_only with total=None. Events are independent l1 bounds
    of jumps in the error (including an approximation reset when appropriate).
    This is a mathematical conditional estimate, not interval arithmetic.
    """
    widths, event_total = _integral_inputs(widths, event_l1_bounds, clock)
    if supremum_bounds is None:
        if samples is not None:
            _vector(samples, "samples", len(widths) + 1, True)
        return IntegralBound("unresolved_samples_only" if samples is not None else "unresolved_no_suprema",
                             clock, None, event_total, None,
                             "Continuous panel suprema or a proved quadrature remainder are missing.")
    if samples is not None:
        raise ValueError("supply suprema to this API; send samples to sampled_trapezoid_diagnostic")
    if not isinstance(supremum_provenance, str) or not supremum_provenance.strip():
        raise ValueError("continuous suprema require an explicit provenance statement")
    suprema = _vector(supremum_bounds, "supremum_bounds", len(widths), True)
    integral = _sum((h * s for h, s in zip(widths, suprema)), "panel integral")
    return IntegralBound("conditional_certificate", clock, integral, event_total,
                         _sum((integral, event_total), "total integral bound"),
                         "Caller must justify continuous suprema: " + supremum_provenance)


def sampled_trapezoid_diagnostic(widths, samples, *, event_l1_bounds=(), clock):
    """Finite sampled trapezoid value, explicitly without continuous certification."""
    widths, event_total = _integral_inputs(widths, event_l1_bounds, clock)
    samples = _vector(samples, "samples", len(widths) + 1, True)
    integral = _sum((h * (a / 2 + b / 2)
                     for h, a, b in zip(widths, samples, samples[1:])), "sampled integral")
    return IntegralBound("sampled_diagnostic", clock, integral, event_total,
                         _sum((integral, event_total), "diagnostic total"),
                         "Samples give no continuous residual enclosure or quadrature remainder.")
