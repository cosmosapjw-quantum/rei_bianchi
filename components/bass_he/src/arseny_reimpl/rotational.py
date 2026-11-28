"""Paper-derived clean-room implementation of CPC Eqs. (47)-(48).

NOT AUTHOR CODE.

The published paper specifies the small-R rotational evolution

    i dA/dt = [epsilon R(t)^2 L_x^2 + omega(t) L_z] A,

with dimension 2l+1.  This module supplies a transparent independent
implementation for the straight-line trajectory used in the same paper.

The author WRN/ODEINT implementation is not available and no implementation
identity is claimed.
"""
from __future__ import annotations

from dataclasses import dataclass
import math
import numpy as np

from .cross_section import projectile_velocity_au
from .state_index import state_index


@dataclass(frozen=True)
class RotationalBlockResult:
    N: int
    l: int
    energy_keV_per_amu: float
    velocity_au: float
    rho: float
    R_cut: float
    epsilon: float
    steps: int
    propagator_z_basis: np.ndarray
    probability_z_basis: np.ndarray
    propagator_mx_basis: np.ndarray
    probability_signed_mx: np.ndarray
    probability_abs_mx: np.ndarray
    unitarity_defect: float
    signed_stochastic_defect: float
    collapsed_column_defect: float
    z_parity_leakage: float
    entered_rotational_region: bool


@dataclass(frozen=True)
class RotationalConvergenceResult:
    coarse: RotationalBlockResult
    medium: RotationalBlockResult
    fine: RotationalBlockResult
    error_coarse_medium: float
    error_medium_fine: float
    observed_order: float | None
    rk4_probability_difference: float
    rk4_norm_defect: float


def angular_momentum_operators(l: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return m_z labels, Lx and Lz in the signed-m basis, hbar=1."""
    if not isinstance(l, int) or l < 0:
        raise ValueError("l must be a non-negative integer")
    mvals = np.arange(-l, l + 1, dtype=int)
    dim = len(mvals)
    lp = np.zeros((dim, dim), dtype=complex)
    ll = float(l * (l + 1))
    for j, m in enumerate(mvals[:-1]):
        # <m+1|L+|m>
        lp[j + 1, j] = math.sqrt(ll - m * (m + 1))
    lm = lp.conj().T
    lx = 0.5 * (lp + lm)
    lz = np.diag(mvals.astype(float)).astype(complex)
    return mvals, lx, lz


def molecular_x_basis(l: int) -> tuple[np.ndarray, np.ndarray]:
    """Return signed m_x labels and the unitary z->x eigenbasis matrix.

    Columns of Vx are Lx eigenvectors represented in the standard Lz basis,
    ordered by eigenvalue m_x=-l,...,+l.
    """
    _, lx, _ = angular_momentum_operators(l)
    vals, vecs = np.linalg.eigh(lx)
    target = np.arange(-l,l+1,dtype=float)
    if np.max(np.abs(vals-target)) > 5e-13:
        raise ArithmeticError("Lx eigenspectrum mismatch")
    return target.astype(int), vecs


def epsilon_rotational(N: int, l: int, Z1: float = 1.0, Z2: float = 2.0) -> float:
    """CPC Eq. (48)."""
    if N < 1 or l < 1 or l >= N:
        raise ValueError("Eq. (48) requires N>=2 and 1<=l<N")
    den = N**3 * l * (l + 1) * (2*l - 1) * (2*l + 1) * (2*l + 3)
    return 6.0 * Z1 * Z2 * (Z1 + Z2)**2 / den


def s_sigma_boundary(l: int, Z1: float = 1.0, Z2: float = 2.0) -> float:
    """Default DR6 small-R boundary from CPC Eq. (36), m=0, Re R_infty.

    The paper states that rotational evolution acts after S-series on approach
    until S-series on recession.  We therefore use the published S_{l,sigma}
    series limit-point real part as a transparent generic boundary policy.
    This is a derived clean-room convention, not a claim about hidden WRN code.
    """
    if l < 1:
        raise ValueError("rotational block requires l>=1")
    z = Z1 + Z2
    return ((l + 0.5)**2 - 0.5) / z


def _trajectory_window(velocity: float, rho: float, R_cut: float) -> tuple[float, float] | None:
    if velocity <= 0:
        raise ValueError("velocity must be positive")
    if rho < 0:
        raise ValueError("rho must be non-negative")
    if R_cut <= 0:
        raise ValueError("R_cut must be positive")
    if rho >= R_cut:
        return None
    x_max = math.sqrt(max(R_cut*R_cut - rho*rho, 0.0))
    t_max = x_max / velocity
    return -t_max, t_max


def _hamiltonian(t: float, *, eps: float, velocity: float, rho: float,
                 lx2: np.ndarray, lz: np.ndarray) -> np.ndarray:
    x = velocity * t
    r2 = x*x + rho*rho
    # theta=atan2(rho,X) for the straight trajectory R=(X,rho,0), X=vt.
    # Hence omega=dtheta/dt=-rho*v/R^2.  This sign is a derived geometry
    # convention; collapsed |m| probabilities are insensitive to reversal of
    # collision-plane orientation.
    omega = 0.0 if rho == 0.0 else -rho * velocity / r2
    return eps * r2 * lx2 + omega * lz


def _unitary_midpoint_propagator(N: int, l: int, energy_keV_per_amu: float, rho: float,
                                 *, steps: int, Z1: float, Z2: float,
                                 R_cut: float) -> tuple[np.ndarray, bool]:
    if steps < 4:
        raise ValueError("steps must be >=4")
    velocity = projectile_velocity_au(energy_keV_per_amu)
    window = _trajectory_window(velocity, rho, R_cut)
    dim = 2*l + 1
    U = np.eye(dim, dtype=complex)
    if window is None:
        return U, False
    _, lx, lz = angular_momentum_operators(l)
    lx2 = lx @ lx
    eps = epsilon_rotational(N, l, Z1, Z2)
    ta, tb = window
    dt = (tb - ta) / steps
    for k in range(steps):
        tm = ta + (k + 0.5) * dt
        H = _hamiltonian(tm, eps=eps, velocity=velocity, rho=rho, lx2=lx2, lz=lz)
        # H is Hermitian.  Exponentiating its instantaneous eigensystem makes
        # every midpoint step exactly unitary up to eigensolver roundoff.
        evals, evecs = np.linalg.eigh(H)
        phase = np.exp(-1j * evals * dt)
        Ustep = (evecs * phase) @ evecs.conj().T
        U = Ustep @ U
    return U, True


def _rk4_propagator(N: int, l: int, energy_keV_per_amu: float, rho: float,
                    *, steps: int, Z1: float, Z2: float, R_cut: float) -> tuple[np.ndarray, bool]:
    """Independent fixed-step RK4 auditor for the published ODE."""
    velocity = projectile_velocity_au(energy_keV_per_amu)
    window = _trajectory_window(velocity, rho, R_cut)
    dim = 2*l + 1
    U = np.eye(dim, dtype=complex)
    if window is None:
        return U, False
    _, lx, lz = angular_momentum_operators(l)
    lx2 = lx @ lx
    eps = epsilon_rotational(N, l, Z1, Z2)
    ta, tb = window
    dt = (tb - ta) / steps

    def rhs(t, Y):
        H = _hamiltonian(t, eps=eps, velocity=velocity, rho=rho, lx2=lx2, lz=lz)
        return -1j * (H @ Y)

    t = ta
    for _ in range(steps):
        k1 = rhs(t, U)
        k2 = rhs(t + 0.5*dt, U + 0.5*dt*k1)
        k3 = rhs(t + 0.5*dt, U + 0.5*dt*k2)
        k4 = rhs(t + dt, U + dt*k3)
        U = U + (dt/6.0)*(k1 + 2*k2 + 2*k3 + k4)
        t += dt
    return U, True


def signed_probability(U: np.ndarray) -> np.ndarray:
    return np.abs(np.asarray(U, dtype=complex))**2


def collapse_signed_m_probability(P_signed: np.ndarray, l: int) -> np.ndarray:
    """Collapse signed molecular m_x to the paper's |m|-labelled basis.

    Eq. (47) is represented numerically in the Lz basis because the rotation
    generator is simple there, but the two-center state label m is projection
    on the internuclear x axis.  The caller must therefore first transform the
    propagator to the Lx eigenbasis.  DR6 then uses the explicit *incoherent
    degeneracy adapter*

      P(|mf| <- |mi|) = (1/g_i) sum_{mi=±|mi|} sum_{mf=±|mf|} P(mf<-mi),

    with g_0=1 and g_m=2 for m>0.

    This adapter is derived and fully documented; equivalence to the unavailable
    author MODKG implementation is NOT claimed.
    """
    P = np.asarray(P_signed, dtype=float)
    dim = 2*l + 1
    if P.shape != (dim, dim):
        raise ValueError("signed probability shape mismatch")
    mvals = np.arange(-l, l+1)
    out = np.zeros((l+1, l+1), dtype=float)
    for ai in range(l+1):
        rows = np.where(np.abs(mvals) == ai)[0]
        for bi in range(l+1):
            cols = np.where(np.abs(mvals) == bi)[0]
            out[ai, bi] = P[np.ix_(rows, cols)].sum() / len(cols)
    return out


def _diagnostics(Uz: np.ndarray, Pz: np.ndarray, Pmx: np.ndarray, Pabs: np.ndarray, l: int):
    dim=2*l+1
    I=np.eye(dim)
    unitary=float(np.max(np.abs(Uz.conj().T@Uz-I)))
    signed_stochastic=float(max(
        np.max(np.abs(Pmx.sum(axis=0)-1.0)),
        np.max(np.abs(Pmx.sum(axis=1)-1.0)),
    ))
    collapsed_col=float(np.max(np.abs(Pabs.sum(axis=0)-1.0)))
    # Published Eq. (47) selection rule refers to projection on z.
    m_z=np.arange(-l,l+1)
    leakage=0.0
    for a,ma in enumerate(m_z):
        for b,mb in enumerate(m_z):
            if (ma-mb)%2:
                leakage=max(leakage,abs(float(Pz[a,b])))
    return unitary,signed_stochastic,collapsed_col,float(leakage)

def rotational_block(N: int, l: int, energy_keV_per_amu: float, rho: float, *,
                     steps: int = 256, Z1: float = 1.0, Z2: float = 2.0,
                     R_cut: float | None = None) -> RotationalBlockResult:
    if R_cut is None:
        R_cut = s_sigma_boundary(l, Z1, Z2)
    Uz, entered = _unitary_midpoint_propagator(
        N,l,energy_keV_per_amu,rho,steps=steps,Z1=Z1,Z2=Z2,R_cut=R_cut
    )
    Pz=signed_probability(Uz)
    _,Vx=molecular_x_basis(l)
    Umx=Vx.conj().T @ Uz @ Vx
    Pmx=signed_probability(Umx)
    Pabs=collapse_signed_m_probability(Pmx,l)
    u,ss,c,leak=_diagnostics(Uz,Pz,Pmx,Pabs,l)
    return RotationalBlockResult(
        N,l,energy_keV_per_amu,projectile_velocity_au(energy_keV_per_amu),
        rho,R_cut,epsilon_rotational(N,l,Z1,Z2),steps,Uz,Pz,Umx,Pmx,Pabs,
        u,ss,c,leak,entered
    )


def rotational_convergence(N: int, l: int, energy_keV_per_amu: float, rho: float, *,
                           base_steps: int = 64, Z1: float = 1.0, Z2: float = 2.0,
                           R_cut: float | None = None) -> RotationalConvergenceResult:
    if R_cut is None:
        R_cut=s_sigma_boundary(l,Z1,Z2)
    a=rotational_block(N,l,energy_keV_per_amu,rho,steps=base_steps,Z1=Z1,Z2=Z2,R_cut=R_cut)
    b=rotational_block(N,l,energy_keV_per_amu,rho,steps=2*base_steps,Z1=Z1,Z2=Z2,R_cut=R_cut)
    c=rotational_block(N,l,energy_keV_per_amu,rho,steps=4*base_steps,Z1=Z1,Z2=Z2,R_cut=R_cut)
    e1=float(np.max(np.abs(a.probability_abs_mx-b.probability_abs_mx)))
    e2=float(np.max(np.abs(b.probability_abs_mx-c.probability_abs_mx)))
    order=None
    if e1>1e-15 and e2>1e-15:
        order=float(math.log(e1/e2,2.0))
    Urk, entered = _rk4_propagator(
        N,l,energy_keV_per_amu,rho,steps=8*base_steps,Z1=Z1,Z2=Z2,R_cut=R_cut
    )
    _,Vx=molecular_x_basis(l)
    Urkx=Vx.conj().T @ Urk @ Vx
    Prk=collapse_signed_m_probability(signed_probability(Urkx),l)
    rkdiff=float(np.max(np.abs(Prk-c.probability_abs_mx)))
    rknorm=float(np.max(np.abs(Urk.conj().T@Urk-np.eye(2*l+1))))
    return RotationalConvergenceResult(a,b,c,e1,e2,order,rkdiff,rknorm)


def full_rotational_probability(Nmax: int, energy_keV_per_amu: float, rho: float, *,
                                steps: int = 256, Z1: float = 1.0, Z2: float = 2.0) -> np.ndarray:
    """Block-diagonal |m|-basis P_rot through Nmax under DR6 conventions."""
    if Nmax < 1:
        raise ValueError("Nmax must be >=1")
    jmax = state_index(Nmax,Nmax-1,Nmax-1)
    P=np.eye(jmax,dtype=float)
    for N in range(2,Nmax+1):
        for l in range(1,N):
            block=rotational_block(N,l,energy_keV_per_amu,rho,steps=steps,Z1=Z1,Z2=Z2).probability_abs_mx
            inds=[state_index(N,l,m)-1 for m in range(l+1)]
            P[np.ix_(inds,inds)] = block
    return P
