"""PHYS55: source-locked all-ell screened collar + CENTRAL outgoing hybrid.

Proof: all ell>=21, all m, B=20, T=27 Bohr, kappa=7/10.
- Physical Q S Q noncentral screened potential is inside collar [B,T].
- Outside T the exact outgoing DtN is CENTRAL Coulomb Z_C, *not* screened.
- The new quantitative TT coercivity and diagonal Coulomb compact-principal
  theorem give a bounded invertible high-trace hybrid Robin operator.
- The actual physical screened exterior / original xi / sigma(E) / k(T) remain
  unresolved and HH_R10=OFF.

The exact rational certificates do not rely on floating Coulomb samples.
Finite-element screens, special functions and surrogate matrices are
NUMERICAL_DIAGNOSTICS only, not infinite-dimensional enclosures.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import hashlib

B, T, R, FIRST_HIGH = 20, 27, F(7, 10), 21
KAPPA = F(7, 10)
COULOMB_ETA = -F(10, 7)
ORIGINAL_SHA = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
SCREEN_DELTA_LOOSE = F(1, 10**12)
CERTIFIED_C_D = F(9, 1000)
SCHEMA = "WU088_HH_PHYS55_INFINITE_HYBRID_CENTRAL_OUTGOING_V1"


def original_sha(path: str | Path) -> str:
    digest = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    if digest != ORIGINAL_SHA:
        raise ValueError("immutable original 1386 complex128 H-H source SHA mismatch")
    return digest


def exp_lower(x: F, terms: int = 30) -> F:
    """Exact Taylor lower bound for e^x (x>=0)."""
    if not isinstance(x, F) or x < 0 or type(terms) is not int or not 16 <= terms <= 80:
        raise ValueError("positive exact rational argument and terms in [16,80]")
    s, p = F(1), F(1)
    for n in range(1, terms + 1):
        p *= x / n
        s += p
    return s


def screen_collar_upper(terms: int = 30) -> F:
    """Exact bound sup_(r>=20, sphere) 2(1+1/s)exp(-2s)."""
    d = F(B) - R
    return 2*(1 + 1/d)/exp_lower(2*d, terms)


def barrier_a2(ell: int, conservative_delta: F = SCREEN_DELTA_LOOSE) -> F:
    if type(ell) is not int or ell < FIRST_HIGH:
        raise ValueError("full high angular ell >=21 only")
    if conservative_delta < 0 or conservative_delta > SCREEN_DELTA_LOOSE:
        raise ValueError("use a certified 2S supremum")
    return F(ell*(ell+1), T*T) - F(2, B) - KAPPA*KAPPA - conservative_delta


def weighted_ratio2(ell: int, conservative_delta: F = SCREEN_DELTA_LOOSE) -> F:
    return barrier_a2(ell, conservative_delta) / (ell+1)**2


def collar_certificate(original_npz: str | Path, terms: int = 30) -> dict:
    """Exact Fraction proof certificate for TT collar lower bound.

    Minimize the positive screened high angular energy at fixed g_B=0,
    g_T arbitrary; at every ell potential >=a_ell². Scalar 1d problem
    has min energy a_ell coth(a_ell*(T-B))|g_T|² >=a_ell |g_T|².
    The ratio a_ell/(ell+1) grows for ell>=21, so c_D=9/1000
    applies to all ell/m, even with actual off-centre QS Q mixing.
    """
    digest = original_sha(original_npz)
    delta = screen_collar_upper(terms)
    if not 0 < delta < SCREEN_DELTA_LOOSE:
        raise ArithmeticError("screen upper not sufficient for collar proof")
    first = weighted_ratio2(FIRST_HIGH)
    margin = first - CERTIFIED_C_D**2
    if margin <= 0:
        raise ArithmeticError("wrong collider barrier constant")
    # derivative wrt real ell x of a_ell²/(ell+1)²:
    # 1/[T²(x+1)²]+2(2/B+k²+delta)/(x+1)³ >0 for x>=21.
    assert F(1,T*T) > 0 and F(2,B)+KAPPA*KAPPA+SCREEN_DELTA_LOOSE > 0
    return {
        "schema": SCHEMA,
        "original_SHA256": digest,
        "kappa": str(KAPPA),
        "radii_B_T_a0": [B,T],
        "all_high_ell_from": FIRST_HIGH,
        "all_m": True,
        "actual_screen_2S_sup_r_ge_20_up_fraction": str(delta),
        "screen_dominating_delta_fraction": str(SCREEN_DELTA_LOOSE),
        "a21_squared_fraction": str(barrier_a2(FIRST_HIGH)),
        "first_weighted_ratio_squared_fraction": str(first),
        "margin_over_cD_squared_fraction": str(margin),
        "cD_certified_fraction": str(CERTIFIED_C_D),
        "cD_certified_float": float(CERTIFIED_C_D),
        "collar_TT":"Re<g,Lambda_D_TT g> >= cD ||g||_X² with g_B=0",
        "central_principal":"Z_C,l/(ell+1) -> -1/T (DLMF 33.5.8-9 + 33.4 derivative recurrence)",
        "central_bounded":"Z_C:X -> X* bounded; W^-1/2 Z_C W^-1/2 +(1/T)I compact",
        "central_hybrid":"M=Lambda_D_TT-Z_C:X -> X* is Fredholm index0 and injective by positive Coulomb current; hence bounded bijection",
        "not_established":["physical noncentral screened outer Z_S", "uniform operator bound Z_S-Z_C", "actual g_B or original driven xi=Fy-phi", "full physical scattering sigma(E)", "identical H-H Maxwellian k(T)", "rei_bianchi HH_R10"],
        "HH_R10":"OFF",
    }


def central_impedance(ell: int, radius: int | float = T, dps: int = 70) -> dict:
    """High-precision Coulomb log derivative and Wronskian j, DIAGNOSTIC.

    Real log derivative uses DLMF 33.4 recurrence (the derivative of
    the Coulomb G+iF wave); positive imaginary part j is evaluated
    separately by the Wronskian to avoid catastrophic cancellation.
    """
    if type(ell) is not int or ell < 0 or ell > 1024:
        raise ValueError("finite integer ell in 0..1024")
    if not (isinstance(radius, (int,float)) and 20 <= radius <= 100):
        raise ValueError("radius between 20 and 100 Bohr")
    if type(dps) is not int or not 55 <= dps <= 150:
        raise ValueError("multiprecision digits 55..150")
    import mpmath as mp
    with mp.workdps(dps):
        k = mp.mpf(7)/10
        eta = -1/k
        rho = k*mp.mpf(str(radius))
        h0 = mp.coulombg(ell,eta,rho) + 1j*mp.coulombf(ell,eta,rho)
        h1 = mp.coulombg(ell+1,eta,rho) + 1j*mp.coulombf(ell+1,eta,rho)
        zh = k*((ell+1)/rho + eta/(ell+1) - mp.sqrt(1+(eta/(ell+1))**2)*h1/h0)
        j = k/(abs(h0)**2)
        if j <= 0:
            raise ArithmeticError("nonpositive outgoing Wronskian current")
        return {
            "ell":ell, "radius_Bohr":float(radius),
            "Re_Z_per_Bohr":mp.nstr(mp.re(zh),min(43,dps-10)),
            "weighted_negative_real_ratio":mp.nstr(-mp.re(zh)/(ell+1),min(43,dps-10)),
            "Im_Z_per_Bohr_positive_Wronskian":mp.nstr(j,min(43,dps-10)),
            "log10_Im_Z":mp.nstr(mp.log10(j),min(43,dps-10)),
            "principal_limit":f"1/{radius}",
            "physical_scope":"CENTRAL_COULOMB_REFERENCE_ONLY",
        }


def fd_screened_collar_hybrid(ells: tuple[int, ...] = (21,22,23), m: int = 0,
                               elements: int = 40, nodes: int = 96) -> dict:
    """Noncertifying actual screened finite-element collar + CENTRAL Z_C.

    Linear finite elements, nodal trapezoid screen potential. This is
    *not* a proof, error enclosure or a global physical scattering solve.
    """
    if not ells or any(type(l) is not int or l<21 for l in ells) or len(set(ells))!=len(ells):
        raise ValueError("distinct high ell only")
    if type(m) is not int or any(abs(m)>l for l in ells):
        raise ValueError("invalid axial harmonic m")
    if type(elements) is not int or not 12<=elements<=96 or type(nodes) is not int or not 64<=nodes<=256:
        raise ValueError("bounded finite grid")
    import numpy as np
    from numpy.polynomial.legendre import leggauss
    from scipy.special import gammaln, lpmv
    mu,w=leggauss(nodes)
    A=[]
    for l in ells:
        norm=np.sqrt((2*l+1)/2*np.exp(gammaln(l-abs(m)+1)-gammaln(l+abs(m)+1)))
        A.append(norm*lpmv(abs(m),l,mu))
    A=np.asarray(A)
    nd=len(ells); h=(T-B)/elements
    ugrid=np.linspace(B,T,elements+1)
    stiffness=np.zeros(((elements+1)*nd,(elements+1)*nd),dtype=float)
    I=np.eye(nd)
    screen_offdiagonal_at_B = None
    screen_opnorm_at_B = None
    for j in range(elements):
        i0=slice(j*nd,(j+1)*nd);i1=slice((j+1)*nd,(j+2)*nd)
        stiffness[i0,i0]+=I/h; stiffness[i1,i1]+=I/h
        stiffness[i0,i1]-=I/h; stiffness[i1,i0]-=I/h
    for j,r in enumerate(ugrid):
        s=np.sqrt(r*r+float(R)**2-2*r*float(R)*mu)
        screen=(1+1/s)*np.exp(-2*s)
        Q=(A*(w*screen)[None,:])@A.T
        if j == 0:
            screen_offdiagonal_at_B = float(np.max(np.abs(Q-np.diag(np.diag(Q)))))
            screen_opnorm_at_B = float(np.linalg.norm(Q,ord=2))
        V=np.diag([l*(l+1)/r**2-2/r-float(KAPPA)**2 for l in ells])-2*Q
        weight=h/2 if j in (0,elements) else h
        sl=slice(j*nd,(j+1)*nd)
        stiffness[sl,sl]+=weight*V
    # u_B=0; eliminate interior 1..elements-1 and retain boundary T.
    idx=np.arange(nd,nd*elements)
    boundary=np.arange(nd*elements,nd*(elements+1))
    D=stiffness[np.ix_(idx,idx)]
    C=stiffness[np.ix_(idx,boundary)]
    lam=stiffness[np.ix_(boundary,boundary)]-C.T@np.linalg.solve(D,C)
    wdiag=np.diag([1/np.sqrt(l+1) for l in ells])
    normalized=wdiag@lam@wdiag
    zdiag=np.diag([complex(float(central_impedance(l,T)["Re_Z_per_Bohr"]),float(central_impedance(l,T)["Im_Z_per_Bohr_positive_Wronskian"])) for l in ells])
    hybrid=wdiag@(lam-zdiag)@wdiag
    v=np.linalg.eigvalsh(normalized)
    return {
        "ell":list(ells),"m":m,"elements":elements,"mu_nodes":nodes,
        "screen_offdiagonal_abs_at_B":screen_offdiagonal_at_B,
        "screen_operator_norm_at_B":screen_opnorm_at_B,
        "min_eigen_weighted_collar":float(v.min()),
        "cD_analytic_exact":float(CERTIFIED_C_D),
        "min_singular_weighted_hybrid":float(np.linalg.svd(hybrid,compute_uv=False).min()),
        "imag_current_of_matched_test_g":float(np.imag(np.vdot(np.ones(nd),zdiag@np.ones(nd)))),
        "no_full_physics_claim":True,
        "scientific_status":"FINITE_ELEMENT_NONCERTIFYING_CENTRAL_OUTGOING_HYBRID",
    }
