"""Independent, bounded two-center Coulomb separation prototype.

Coordinates: xi=(r_A+r_B)/R, eta=(r_A-r_B)/R; A is at -R/2,
B at +R/2. Computational units are a_A=hbar**2/(m_e*k),
E_A=hbar**2/(m_e*a_A**2). No nuclear-repulsion energy is included.

Only the lowest state in a fixed nonnegative |m| sector is selected.
Galerkin eigenresiduals are discrete residuals, not continuum certificates.
"""
from dataclasses import dataclass, asdict
import math

import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import BSpline
from scipy.linalg import eigh
from scipy.optimize import brentq


@dataclass(frozen=True)
class SpheroidalConfig:
    degree: int = 7
    radial_elements: int = 36
    angular_elements: int = 14
    quadrature_order: int = 12
    radial_extent: float = 24.0  # xi_max=1+2*extent/R, in a_A
    radial_grading: float = 2.0
    root_xtol: float = 2e-12  # in E_A; rtol is separately fixed below

    def validate(self, m):
        for name in ("degree", "radial_elements", "angular_elements",
                     "quadrature_order"):
            value = getattr(self, name)
            if isinstance(value, bool) or not isinstance(value, int) or value < 1:
                raise ValueError(f"{name} must be a positive integer")
        if self.degree < 2:
            raise ValueError("degree >= 2 is required for this prototype")
        if self.quadrature_order < self.degree + m + 2:
            raise ValueError("quadrature must integrate all polynomial matrix entries")
        for name in ("radial_extent", "radial_grading", "root_xtol"):
            value = getattr(self, name)
            if not np.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be finite and positive")


class _Axis:
    def __init__(self, edges, degree, order, m, radial):
        self.edges = np.asarray(edges)
        knots = np.r_[np.repeat(edges[0], degree), edges,
                      np.repeat(edges[-1], degree)]
        n = len(knots) - degree - 1
        # The last radial coefficient is fixed to zero, imposing X(xi_max)=0.
        coefficients = np.eye(n)[:, :n - int(radial)]
        self.basis = BSpline(knots, coefficients, degree, extrapolate=False)
        self.dbasis = self.basis.derivative()
        nodes, weights = leggauss(order)
        lo, hi = edges[:-1, None], edges[1:, None]
        self.nodes = ((hi + lo) / 2 + (hi - lo) / 2 * nodes).ravel()
        self.weights = ((hi - lo) / 2 * weights).ravel()
        b, db = self.basis(self.nodes), self.dbasis(self.nodes)
        p = self.nodes**2 - 1 if radial else 1 - self.nodes**2

        def product(values, left=b, right=b):
            return left.T @ (values[:, None] * right)

        w = self.weights * p**m
        self.mass = product(w)
        self.first = product(w * self.nodes)
        self.second = product(w * self.nodes**2)
        sign = -1 if radial else 1
        self.kinetic = (product(w * p, db, db)
                        + sign * m * (m + 1) * self.mass)

    def lowest(self, matrix):
        values, vectors = eigh(matrix, self.mass, subset_by_index=(0, 0),
                               driver="gvx", check_finite=False)
        vector = vectors[:, 0]
        # Lowest regular Sturm-Liouville eigenfunction has no interior nodes.
        midpoint = (self.edges[0] + self.edges[1]) / 2
        if self.basis(midpoint) @ vector < 0:
            vector = -vector
        eigenvalue = float(values[0])
        residual = matrix @ vector - eigenvalue * (self.mass @ vector)
        scale = (np.linalg.norm(matrix, 2) + abs(eigenvalue)
                 * np.linalg.norm(self.mass, 2)) * np.linalg.norm(vector)
        return eigenvalue, vector, float(np.linalg.norm(residual) / scale)


@dataclass
class SpheroidalState:
    R: float
    ZA: float
    ZB: float
    m: int
    config: SpheroidalConfig
    energy: float
    separation_radial: float
    separation_angular: float
    normalization: float
    root_derivative: float
    residuals: dict
    radial_coefficients: np.ndarray
    angular_coefficients: np.ndarray
    _radial: _Axis
    _angular: _Axis

    @property
    def xi_max(self):
        return float(self._radial.edges[-1])

    @staticmethod
    def _factor(x, m, radial):
        p = x**2 - 1 if radial else 1 - x**2
        if m == 0:
            return np.ones_like(x), np.zeros_like(x)
        with np.errstate(divide="ignore", invalid="ignore"):
            f = p**(m / 2)
            df = m * (x if radial else -x) * p**(m / 2 - 1)
        return f, df

    def evaluate(self, xi, eta):
        """Return normalized (G, dG/dxi, dG/deta), broadcasting arrays.

        int rho d(rho) dz G**2 = 1. Full wavefunctions are
        g=G/sqrt(2*pi) for m=0; b=G*cos(phi)/sqrt(pi) for m=1.
        For m>0 the coordinate derivatives can diverge at xi=1 or eta=+-1;
        use open quadrature nodes for derivatives. These are coordinate, not
        Cartesian, singularities. Values outside the finite domain are rejected.
        """
        xi, eta = np.broadcast_arrays(np.asarray(xi, float), np.asarray(eta, float))
        if (not np.all(np.isfinite(xi)) or not np.all(np.isfinite(eta))
                or np.any(xi < 1) or np.any(xi > self.xi_max)
                or np.any(np.abs(eta) > 1)):
            raise ValueError("evaluation point is outside the finite spheroidal domain")
        u = self._radial.basis(xi) @ self.radial_coefficients
        du = self._radial.dbasis(xi) @ self.radial_coefficients
        v = self._angular.basis(eta) @ self.angular_coefficients
        dv = self._angular.dbasis(eta) @ self.angular_coefficients
        f, df = self._factor(xi, self.m, True)
        h, dh = self._factor(eta, self.m, False)
        n = self.normalization
        return n*f*u*h*v, n*(df*u+f*du)*h*v, n*f*u*(dh*v+h*dv)

    def metadata(self):
        return {"R": self.R, "ZA": self.ZA, "ZB": self.ZB, "m": self.m,
                "units": {"length": "a_A=hbar^2/(m_e*k)",
                          "energy": "E_A=hbar^2/(m_e*a_A^2)"},
                "config": asdict(self.config), "actual_radial_edges": self._radial.edges.tolist(),
                "actual_radial_elements": len(self._radial.edges)-1, "energy": self.energy,
                "separation_radial": self.separation_radial,
                "separation_angular": self.separation_angular,
                "normalization": self.normalization,
                "root_derivative": self.root_derivative,
                "residuals": self.residuals, "xi_max": self.xi_max,
                "selection": "lowest fixed-|m| regular Sturm-Liouville state",
                "certificate": "DISCRETE_ONLY; truncation/basis error not enclosed"}


def solve(R, ZA=1.0, ZB=2.0, m=0, config=None, radial_edges=None):
    """Solve one fixed-R lowest-|m| state; no continuation or collision solve.

    Radial/axial endpoint regularity is enforced by X=(xi^2-1)^(m/2)u,
    Y=(1-eta^2)^(m/2)v in the finite-energy weak form. The log/negative-power
    endpoint branches are excluded. At infinity a finite outer Dirichlet
    boundary is used and must be varied independently in scientific audits.
    """
    if any(not np.isfinite(x) for x in (R, ZA, ZB)):
        raise ValueError("R and charges must be finite")
    if R <= 0 or ZA < 0 or ZB < 0 or ZA + ZB <= 0:
        raise ValueError("R>0 and nonnegative charges with positive total are required")
    if isinstance(m, bool) or not isinstance(m, int) or m < 0:
        raise ValueError("m must be a nonnegative integer representing |m|")
    config = config or SpheroidalConfig()
    config.validate(m)
    if radial_edges is None:
        radial_edges = 1 + (2*config.radial_extent/R) * np.linspace(
            0, 1, config.radial_elements + 1)**config.radial_grading
    else:
        radial_edges = np.asarray(radial_edges,dtype=float)
        if (radial_edges.ndim!=1 or len(radial_edges)<3 or not np.all(np.isfinite(radial_edges))
                or radial_edges[0]!=1 or radial_edges[-1]!=1+2*config.radial_extent/R
                or np.any(np.diff(radial_edges)<=0)):
            raise ValueError('explicit radial edges must increase from1 to configured xi_max')
    angular_edges = np.linspace(-1, 1, config.angular_elements + 1)
    radial = _Axis(radial_edges, config.degree, config.quadrature_order, m, True)
    angular = _Axis(angular_edges, config.degree, config.quadrature_order, m, False)
    radial_base = radial.kinetic - R*(ZA+ZB)*radial.first
    angular_base = angular.kinetic - R*(ZB-ZA)*angular.first
    coefficient = R**2/2
    last = {}

    def match(energy):
        # This cache is scoped to this solve and uses the exact float energy.
        if energy not in last:
            hr = radial_base - energy*coefficient*radial.second
            ha = angular_base + energy*coefficient*angular.second
            er, cr, rr = radial.lowest(hr)
            ea, ca, ra = angular.lowest(ha)
            last[energy] = (er, ea, cr, ca, rr, ra)
        return last[energy][0] + last[energy][1]

    nmin = m+1
    lower = -(ZA+ZB)**2/(2*nmin**2)
    upper = -max(ZA, ZB)**2/(2*nmin**2)
    # Pad physical variational brackets for finite Galerkin/truncation error.
    # This padding is a root finder device, not a certified energy enclosure.
    pad = max(1e-7, 0.02*abs(lower))
    lo, hi = lower-pad, min(-np.finfo(float).eps, upper+pad)
    flo, fhi = match(lo), match(hi)
    if not (flo > 0 and fhi < 0):
        raise RuntimeError(f"no monotone bound-state bracket: F(lo)={flo}, F(hi)={fhi}")
    energy = float(brentq(match, lo, hi, xtol=config.root_xtol,
                          rtol=8*np.finfo(float).eps, maxiter=100))
    er, ea, cr, ca, rr, ra = last[energy]
    xr2, eta2 = float(cr @ radial.second @ cr), float(ca @ angular.second @ ca)
    norm2 = R**3/8*(xr2-eta2)
    derivative = coefficient*(eta2-xr2)
    if not (np.isfinite(norm2) and norm2 > 0 and derivative < 0):
        raise RuntimeError("physical normalization / strict monotonicity failed")
    return SpheroidalState(
        float(R), float(ZA), float(ZB), m, config, energy, er, ea,
        1/math.sqrt(norm2), derivative,
        {"matching_absolute": abs(er+ea), "radial_discrete_relative": rr,
         "angular_discrete_relative": ra, "root_evaluations": len(last)},
        cr, ca, radial, angular)
