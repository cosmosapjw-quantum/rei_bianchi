"""Finite-mass angular pushforward for a declared centre-of-mass measure.

The map is F(mu) = gamma*(mu+a)/sqrt(1-mu**2+gamma**2*(mu+a)**2).
Both coordinates are cosines.  A density is per dmu (or per solid angle
at a fixed unchanged azimuth), never an implicit azimuthal average.  No
experimental cross section, event normalization or thermal consumer is inferred.

Binary64 inputs are interpreted as their exact stored real values.  Decimal
arithmetic with 80 significant digits protects inverse cancellation; returned
numbers are binary64, not certified intervals.  The computed binary64 fold
coordinate is a boundary sentinel: equality returns FOLD, not a regular root.
Unresolvable distinct roots, stopped directions, and ordinary points rounding
onto an endpoint are reported explicitly instead of silently clipping them.
"""

from dataclasses import dataclass
from decimal import Decimal, localcontext
from fractions import Fraction
from numbers import Real
import math


class ContractError(ValueError):
    """An input violates the declared mathematical or scalar contract."""


class AngularResolutionError(ContractError):
    """The requested regular angular information is not resolved in binary64."""


_PRECISION = 80
_MAX_PARAMETER = 1.0e6
_ZERO = Decimal(0)
_ONE = Decimal(1)
_TWO = Decimal(2)


def _finite(value, name):
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ContractError(f"{name} must be a finite real scalar, excluding bool")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise ContractError(f"{name} is outside binary64") from exc
    if not math.isfinite(result):
        raise ContractError(f"{name} must be finite")
    return result


def _cosine(value, name):
    value = _finite(value, name)
    if not -1.0 <= value <= 1.0:
        raise ContractError(f"{name} must be in [-1, 1]; no clipping is applied")
    return value


def _binary64(value, name, *, nonzero=False):
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise AngularResolutionError(f"{name} is not representable in binary64") from exc
    if not math.isfinite(result) or (nonzero and result == 0.0):
        raise AngularResolutionError(f"{name} is not representable in binary64")
    return result


def _decimal(value):
    return Decimal.from_float(value)


def _fraction_decimal(value):
    """Convert an already formed exact rational in the active Decimal context."""
    return Decimal(value.numerator) / Decimal(value.denominator)


@dataclass(frozen=True)
class AngularMap:
    """A scalar map with 1 <= gamma <= 10**6 and 0 <= a <= 10**6.

    a < 1 has one inverse branch on [-1,1].  a > 1 has a two-branch
    forward cone, with its fold at mu=-1/a.  At a=1, mu=-1 is a stopped
    daughter and has no direction; the angular image is (0,1].
    """

    gamma: float
    a: float

    def __post_init__(self):
        gamma = _finite(self.gamma, "gamma")
        a = _finite(self.a, "a")
        if not 1.0 <= gamma <= _MAX_PARAMETER:
            raise ContractError("gamma must satisfy 1 <= gamma <= 10**6")
        if not 0.0 <= a <= _MAX_PARAMETER:
            raise ContractError("a must satisfy 0 <= a <= 10**6")
        object.__setattr__(self, "gamma", gamma)
        object.__setattr__(self, "a", a)

    @property
    def regime(self):
        return "ONE_BRANCH" if self.a < 1.0 else (
            "STOPPED_BOUNDARY" if self.a == 1.0 else "TWO_BRANCH_FOLD")

    def _fold(self):
        if self.a <= 1.0:
            raise ContractError("this map has no fold")
        with localcontext() as context:
            context.prec = _PRECISION
            gamma, a = _decimal(self.gamma), _decimal(self.a)
            square = gamma * gamma * (a - _ONE) * (a + _ONE)
            nu = (square / (_ONE + square)).sqrt()
            return float(-_ONE / a), float(nu)

    @property
    def fold_mu(self):
        return self._fold()[0] if self.a > 1.0 else None

    @property
    def nu_min(self):
        if self.a <= 1.0:
            return -1.0 if self.a < 1.0 else 0.0
        nu = self._fold()[1]
        if not 0.0 < nu < 1.0:
            raise AngularResolutionError("the fold coordinate rounds onto a support endpoint")
        return nu

    @staticmethod
    def _jacobian(gamma, a, mu):
        transverse = (_ONE - mu) * (_ONE + mu)
        longitudinal = gamma * (mu + a)
        denominator_squared = transverse + longitudinal * longitudinal
        if denominator_squared <= 0:
            raise AngularResolutionError("a regular direction has zero or negative norm")
        return gamma * (_ONE + a * mu) / (
            denominator_squared * denominator_squared.sqrt())

    def forward(self, mu):
        mu = _cosine(mu, "mu")
        if self.a == 1.0 and mu == -1.0:
            return {"mu": mu, "nu": None, "jacobian_signed": None, "status": "STOPPED"}
        if self.a > 1.0 and mu == self.fold_mu:
            return {"mu": mu, "nu": self.nu_min, "jacobian_signed": 0.0, "status": "FOLD"}
        with localcontext() as context:
            context.prec = _PRECISION
            gamma, a, m = _decimal(self.gamma), _decimal(self.a), _decimal(mu)
            transverse = (_ONE - m) * (_ONE + m)
            longitudinal = gamma * (m + a)
            denominator = (transverse + longitudinal * longitudinal).sqrt()
            nu = _binary64(longitudinal / denominator, "lab direction cosine")
            if -1.0 < mu < 1.0 and abs(nu) == 1.0:
                raise AngularResolutionError("a regular interior direction rounds onto nu=+/-1")
            if self.a > 1.0 and -1.0 < mu < 1.0 and nu == self.nu_min:
                raise AngularResolutionError("a regular direction rounds onto the fold sentinel")
            jacobian = _binary64(self._jacobian(gamma, a, m), "signed Jacobian", nonzero=True)
        return {"mu": mu, "nu": nu, "jacobian_signed": jacobian, "status": "REGULAR"}

    def _branch(self, root, nu, gamma, a):
        mu = _binary64(root, "inverse branch cosine")
        if not -1.0 <= mu <= 1.0:
            raise AngularResolutionError("inverse branch lies outside representable cosine range")
        if -_ONE < root < _ONE and abs(mu) == 1.0:
            raise AngularResolutionError("an interior inverse branch rounds onto an endpoint")
        rounded_longitudinal = _decimal(mu) + a
        if (nu > 0 and rounded_longitudinal <= 0) or (nu < 0 and rounded_longitudinal >= 0):
            raise AngularResolutionError("inverse branch sign is lost on binary64 conversion")
        jacobian = abs(self._jacobian(gamma, a, root))
        return {"mu": mu, "jacobian_abs": _binary64(jacobian, "inverse absolute Jacobian", nonzero=True)}

    def inverse(self, nu):
        nu = _cosine(nu, "nu")
        if self.a >= 1.0 and nu < 0.0:
            return {"status": "OUTSIDE_SUPPORT", "branches": []}
        if self.a == 1.0 and nu == 0.0:
            return {"status": "OPEN_BOUNDARY", "branches": []}
        if self.a > 1.0:
            fold_mu, fold_nu = self._fold()
            if nu < fold_nu:
                return {"status": "OUTSIDE_SUPPORT", "branches": []}
            # nu=1 always has the two genuine endpoints.  When the cone is
            # narrower than binary64 can resolve, no interior fold is exposed.
            if nu != 1.0 and nu == fold_nu:
                return {"status": "FOLD", "branches": [{"mu": fold_mu, "jacobian_abs": 0.0}]}
        with localcontext() as context:
            context.prec = _PRECISION
            gamma, a, n = _decimal(self.gamma), _decimal(self.a), _decimal(nu)
            if nu == 1.0:
                roots = [-_ONE, _ONE] if self.a > 1.0 else [_ONE]
            elif nu == -1.0:
                roots = [-_ONE]
            elif nu == 0.0:
                roots = [-a]
            else:
                G = gamma * gamma * (_ONE - n) * (_ONE + n)
                L = G + n * n
                if self.a == 1.0:
                    roots = [_TWO * n * n / L - _ONE]
                    if roots[0] == -_ONE:
                        raise AngularResolutionError("positive lab angle cannot resolve the stopped endpoint")
                else:
                    B = n * n + G * (_ONE - a) * (_ONE + a)
                    if B <= 0:
                        raise AngularResolutionError("a declared regular inverse has an unresolved discriminant")
                    # Stable quadratic pair: the second root follows from the
                    # product, avoiding cancellation in -a*G + |nu|*sqrt(B).
                    q = -a * G - abs(n) * B.sqrt()
                    if q == 0:
                        raise AngularResolutionError("inverse quadratic pivot is unresolved")
                    candidates = [q / L, (a * a * G - n * n) / q]
                    roots = [m for m in candidates if -_ONE <= m <= _ONE and
                             ((n > 0 and m + a > 0) or (n < 0 and m + a < 0))]
                    expected = 2 if self.a > 1.0 else 1
                    if len(roots) != expected:
                        raise AngularResolutionError("inverse range/sign filtering did not resolve all branches")
            branches = [self._branch(root, n, gamma, a) for root in sorted(roots)]
            if len({branch["mu"] for branch in branches}) != len(branches):
                raise AngularResolutionError("distinct inverse branches collapse to the same binary64 cosine")
            if self.a > 1.0 and any(branch["mu"] == self.fold_mu for branch in branches):
                raise AngularResolutionError("a regular inverse branch rounds onto the fold sentinel")
        return {"status": "REGULAR", "branches": branches}

    def density(self, nu, f_cm):
        """Push forward a nonnegative density by summing every inverse branch.

        No pointwise value is supplied at a fold, even when f_cm could vanish
        there: such a removable limit requires its own regularity information.
        """
        if not callable(f_cm):
            raise ContractError("f_cm must be callable")
        inverse = self.inverse(nu)
        status, branches = inverse["status"], inverse["branches"]
        if status == "FOLD":
            return {"status": status, "density": None, "branches": branches, "singular": True}
        if status in ("OUTSIDE_SUPPORT", "OPEN_BOUNDARY"):
            return {"status": status, "density": 0.0, "branches": branches, "singular": False}
        with localcontext() as context:
            context.prec = _PRECISION
            total = _ZERO
            for branch in branches:
                value = _finite(f_cm(branch["mu"]), "f_cm(mu)")
                if value < 0:
                    raise ContractError("f_cm(mu) must be nonnegative")
                total += _decimal(value) / _decimal(branch["jacobian_abs"])
            density = _binary64(total, "pushforward density", nonzero=(total != 0))
        return {"status": status, "density": density, "branches": branches, "singular": False}

    def weighted_density(self, nu, f_cm, weight):
        """Push forward f_cm(mu)*weight(mu), retaining both branch contributions.

        f_cm is finite and nonnegative; weight is finite and may be signed.
        An energy or another event observable belongs to its own CM branch.
        The returned ``density`` is the weighted pushforward, while
        ``unweighted_density`` records the original angular measure.  No
        averaging of the two inverse branches occurs.  Fold limits require
        additional source regularity and are left undefined here.
        """
        if not callable(f_cm) or not callable(weight):
            raise ContractError("f_cm and weight must be callable")
        inverse = self.inverse(nu)
        status, branches = inverse["status"], inverse["branches"]
        if status == "FOLD":
            return {"status": status, "density": None, "unweighted_density": None,
                    "branches": branches, "singular": True}
        if status in ("OUTSIDE_SUPPORT", "OPEN_BOUNDARY"):
            return {"status": status, "density": 0.0, "unweighted_density": 0.0,
                    "branches": [], "singular": False}
        resolved = []
        with localcontext() as context:
            context.prec = _PRECISION
            total, unweighted_total = _ZERO, _ZERO
            for branch in branches:
                value = _finite(f_cm(branch["mu"]), "f_cm(mu)")
                if value < 0:
                    raise ContractError("f_cm(mu) must be nonnegative")
                observable = _finite(weight(branch["mu"]), "weight(mu)")
                unweighted = _decimal(value) / _decimal(branch["jacobian_abs"])
                contribution = unweighted * _decimal(observable)
                total += contribution
                unweighted_total += unweighted
                resolved.append({**branch, "cm_density": value, "weight": observable,
                                 "unweighted_contribution": _binary64(
                                     unweighted, "unweighted branch contribution", nonzero=(unweighted != 0)),
                                 "contribution": _binary64(
                                     contribution, "weighted branch contribution", nonzero=(contribution != 0))})
            density = _binary64(total, "weighted density", nonzero=(total != 0))
            unweighted_density = _binary64(
                unweighted_total, "unweighted density", nonzero=(unweighted_total != 0))
        return {"status": status, "density": density,
                "unweighted_density": unweighted_density, "branches": resolved,
                "singular": False}


def from_masses(A, M, e):
    """Build the map for photon + stationary target -> two identical daughters.

    A and M are rest energies in the same units as e, with 0 < A < 2M.
    gamma=(A+e)/sqrt(A*(A+2e)), kappa=sqrt(A*(e-eth)/2), and
    a=e/(2*gamma*kappa).  Rest-energy units retain the factors of c in
    A=m_target*c**2, M=m_daughter*c**2 and kappa=c*p_star.
    Threshold and transition comparisons use exact rational values of the
    stored binary64 inputs.  Only exact equality e=eth is a threshold atom;
    it has nu=1 and no angular density/Jacobian.  ``threshold`` in the return
    value is a rounded display value and is never used for admission.  Thus
    e equal to that rounded value need not be exactly at threshold.
    No PHOTON05 kernel is called.
    """
    A, M, e = _finite(A, "A"), _finite(M, "M"), _finite(e, "e")
    if A <= 0 or M <= 0 or e <= 0:
        raise ContractError("positive rest energies and photon energy are required")
    fA, fM, fe = Fraction.from_float(A), Fraction.from_float(M), Fraction.from_float(e)
    delta_exact = 2 * fM - fA
    if delta_exact <= 0:
        raise ContractError("the endothermic domain requires 0 < A < 2M")
    threshold_exact = delta_exact + delta_exact * delta_exact / (2 * fA)
    if fe < threshold_exact:
        raise ContractError("photon energy is below the exact threshold of the stored inputs")
    at_threshold = fe == threshold_exact
    transition_exact = fA * delta_exact / (2 * (fA - fM)) if fA > fM else None
    exact_transition = transition_exact is not None and fe == transition_exact
    with localcontext() as context:
        context.prec = _PRECISION
        dA, dM, de = _decimal(A), _decimal(M), _decimal(e)
        delta = _fraction_decimal(delta_exact)
        threshold = _binary64(threshold_exact, "threshold energy", nonzero=True)
        W = (dA * (dA + _TWO * de)).sqrt()
        gamma_decimal = (dA + de) / W
        gamma = _binary64(gamma_decimal, "gamma", nonzero=True)
        transition_energy = None if transition_exact is None else _binary64(
            transition_exact, "transition energy", nonzero=True)
        common = {"gamma": gamma, "threshold": threshold,
                  "threshold_comparison": "EXACT_RATIONAL_STORED_INPUTS",
                  "transition_energy": transition_energy,
                  "cm_energy": _binary64(W, "CM energy", nonzero=True),
                  "rest_deficit": _binary64(delta, "rest-energy deficit", nonzero=True)}
        if at_threshold:
            return {**common, "status": "THRESHOLD_ATOM", "map": None, "a": None,
                    "kappa": 0.0, "distribution": {"kind": "ATOM", "nu": 1.0}}
        # Form the small positive excess as an exact rational before Decimal
        # conversion: subtracting rounded energies can erase its sign/value.
        excess = _fraction_decimal(fe - threshold_exact)
        kappa_decimal = (dA * excess / _TWO).sqrt()
        kappa = _binary64(kappa_decimal, "CM momentum energy", nonzero=True)
        # Exact rational equality, rather than equality of rounded square-root
        # products or rounded Decimal expressions, defines the transition.
        a_decimal = _ONE if exact_transition else de / (_TWO * gamma_decimal * kappa_decimal)
        a = _binary64(a_decimal, "a", nonzero=True)
        if a == 1.0 and not exact_transition:
            raise AngularResolutionError("mass-derived angular regime rounds onto a=1")
        angular_map = AngularMap(gamma, a)
        return {**common, "status": "ANGULAR_MAP", "map": angular_map, "a": a,
                "kappa": kappa, "distribution": None}


def normalization_weights(convention):
    """Return factors for an explicitly declared identical-daughter convention.

    For an exchange-symmetric full-sphere event density f, integral(f) counts
    events, integral(f*(Q(u)+Q(-u))) gives the pair observable, and the
    inclusive single-particle density is 2f.  For a full-sphere inclusive
    daughter density h=2f, event and pair integrals instead use h/2.

    A representative-hemisphere event density H counts each unordered event
    once on that hemisphere.  An inclusive observable then requires the
    explicit sum Q(u)+Q(-u); no single multiplicative density factor on the
    same hemisphere supplies the missing other daughter.

    These factors are conditional on the declared convention.  This function
    does not establish symmetry, normalization or support for measured data.
    """
    if not isinstance(convention, str):
        raise ContractError("normalization convention must be an explicit string")
    if convention == "EVENT_SYMMETRIC_FULL_SPHERE":
        return {"convention": convention, "domain": "FULL_SPHERE",
                "event_weight_factor": 1.0, "pair_observable_factor": 1.0,
                "single_inclusive_factor": 2.0, "must_sum_pair": False}
    if convention == "INCLUSIVE_DAUGHTER_FULL_SPHERE":
        return {"convention": convention, "domain": "FULL_SPHERE",
                "event_weight_factor": 0.5, "pair_observable_factor": 0.5,
                "single_inclusive_factor": 1.0, "must_sum_pair": False}
    if convention == "EVENT_REPRESENTATIVE_HEMISPHERE":
        return {"convention": convention, "domain": "REPRESENTATIVE_HEMISPHERE",
                "event_weight_factor": 1.0, "pair_observable_factor": 1.0,
                "single_inclusive_factor": None, "must_sum_pair": True}
    raise ContractError("unknown normalization convention")


def inclusive_from_event_atom(weight):
    """Two daughter atoms from one explicitly weighted, already normalized event.

    This counts represented particles only.  It chooses no empirical DCS
    convention and applies no inferred identical-particle half factor.
    """
    weight = _finite(weight, "event atom weight")
    if weight < 0:
        raise ContractError("event atom weight must be nonnegative")
    total = 2.0 * weight
    if not math.isfinite(total):
        raise AngularResolutionError("inclusive atom weight is outside binary64")
    return {"event_weight": weight, "weights": (weight, weight), "count": 2,
            "inclusive_weight": total, "empirical_DCS_factor_applied": False,
            "physical_event_rate_inferred": False}
