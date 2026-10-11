"""Positive time integration of fixed-q cell births and physical redshift work.

No photon seed, clipping, origin Jacobian or absorption is introduced. A caller
supplies genuine source/geometry events; omitted nonsmooth events can cause the
predetermined quadrature pair to reject. Local success is not history admission.
All energy-valued returns are eV per reference cm^3 (multiply by EV_ERG for erg).
"""
from __future__ import annotations
import math
import numpy as np

PAIR_RTOL = 1e-12


class SourceEntryError(FloatingPointError):
    def __init__(self, code, diagnostics):
        super().__init__(code)
        self.diagnostics = diagnostics


def provider_event_times(cell_source,t0,t1):
    """Locate pinned provider kinks/cell crossings in an expanding time span.

    Includes every emissivity energy knot and physical source-band edge crossing
    a fixed-q cell edge, plus emissivity redshift knots. No native opacity or
    gas event is included: those remain the coupled integrator's responsibility.
    """
    from scipy.optimize import brentq
    p = cell_source.provider
    if not (math.isfinite(t0) and math.isfinite(t1) and t1 > t0):
        raise ValueError('SOURCE_ENTRY_EVENT_TIME_DOMAIN')
    def ray(t):
        return p.ray(np.ones(len(cell_source.mu)),cell_source.mu,float(t))[2]
    r0,r1 = ray(t0),ray(t1)
    if np.any(r1 >= r0):
        raise ValueError('SOURCE_ENTRY_EVENTS_REQUIRE_EXPANDING_RAYS')
    table = p.tables['emissivity']
    lo,hi = p.photon_band_eV
    energy = np.unique(np.r_[table.energies_eV,lo,hi])
    energy = energy[(energy >= lo) & (energy <= hi)]
    events = []
    for angle in range(len(cell_source.mu)):
        for edge in cell_source.edges:
            ratios = energy/edge
            for target in ratios[(ratios < r0[angle]) & (ratios > r1[angle])]:
                events.append(brentq(lambda t:ray(t)[angle]-target,t0,t1,
                                     xtol=1e-4,rtol=4*math.ulp(1.)))
    z0,z1 = p.geometry(t0)['z'],p.geometry(t1)['z']
    for z in table.redshifts[(table.redshifts < z0) & (table.redshifts > z1)]:
        events.append(p.background.time_of_redshift(float(z)))
    return tuple(sorted(set(events)))


def _relative(coarse, fine):
    """Each cell uses its own fine amplitude; zero has no replacement floor."""
    difference = np.abs(coarse-fine)
    nonzero = np.abs(fine) > 0
    error = np.zeros_like(fine)
    np.divide(difference, np.abs(fine), out=error, where=nonzero)
    if np.any((~nonzero) & (difference != 0)):
        return math.inf
    return float(np.max(error))


def _snapshot(cell_source, t):
    value = cell_source.source(float(t))
    n, q, u, r = [np.asarray(value[key], dtype=float)
                   for key in ('N','Q_eV','U_eV','R')]
    if (n.ndim != 2 or q.shape != n.shape or u.shape != n.shape
            or r.shape != (n.shape[0],) or not n.size
            or any(not np.isfinite(v).all() for v in (n,q,u,r))
            or np.any(n < 0) or np.any(q < 0) or np.any(u < 0)
            or np.any(r <= 0)):
        raise ValueError('SOURCE_ENTRY_RATE_DOMAIN')
    if np.any((n == 0) != (q == 0)) or np.any((q == 0) != (u == 0)):
        raise ValueError('SOURCE_ENTRY_ZERO_MOMENT_PAIR')
    if _relative(r[:,None]*q, u) > PAIR_RTOL:
        raise ValueError('SOURCE_ENTRY_MOMENT_PAIR')
    if hasattr(cell_source, 'edges'):
        edges = np.asarray(cell_source.edges, dtype=float)
        if edges.shape != (n.shape[1]+1,):
            raise ValueError('SOURCE_ENTRY_EDGES_SHAPE')
        if np.any(q < edges[:-1][None,:]*n) or np.any(q > edges[1:][None,:]*n):
            raise ValueError('SOURCE_ENTRY_CELL_MOMENT_DOMAIN')
    return n,q,u,r


def _sum_arrays(terms):
    shape = terms[0].shape
    stack = np.asarray(terms).reshape(len(terms), -1)
    return np.array([math.fsum(col) for col in stack.T]).reshape(shape)


def integrate_source(cell_source, t0, t1, event_times=(), orders=(16,32), rtol=1e-10):
    """Integrate actual source moments with positive Gauss-Legendre weights.

    All moments share time nodes. Independent coarse/fine rules must satisfy
    `rtol` in each cell for N, Q, injected energy and physical source work.
    This checks quadrature resolution, not a rigorous quadrature error bound.
    Events outside this interval are ignored; nonfinite events are refused.
    """
    if not (math.isfinite(t0) and math.isfinite(t1) and t1 > t0
            and math.isfinite(rtol) and 0 < rtol <= 1e-10):
        raise ValueError('SOURCE_ENTRY_TIME_DOMAIN')
    if (len(orders) != 2 or any(isinstance(n,bool) or not isinstance(n,int)
                              or n < 2 for n in orders) or orders[1] <= orders[0]):
        raise ValueError('SOURCE_ENTRY_ORDER_PAIR')
    events = list(map(float,event_times))
    if not all(map(math.isfinite,events)):
        raise ValueError('SOURCE_ENTRY_NONFINITE_EVENT')
    points = [float(t0), *sorted(set(e for e in events if t0 < e < t1)), float(t1)]
    initial, final = _snapshot(cell_source,t0), _snapshot(cell_source,t1)
    n0, _, _, R0 = initial
    n1, _, _, R1 = final
    if n1.shape != n0.shape or np.any(R1 > R0):
        raise ValueError('SOURCE_ENTRY_NOT_EXPANDING_OR_SHAPE_CHANGE')
    names = ('dN','dQ','injected_energy_eV','radiation_source_work_eV')
    snapshots = 2
    approximations = []
    for order in orders:
        x,w = np.polynomial.legendre.leggauss(order)
        pieces = {key: [] for key in names}
        for left,right in zip(points[:-1],points[1:]):
            half = .5*(right-left)
            for xi,wi in zip(x,w):
                time = left+half*(1+xi)
                n,q,u,r = _snapshot(cell_source,time)
                snapshots += 1
                if n.shape != n0.shape or np.any(r < R1) or np.any(r > R0):
                    raise ValueError('SOURCE_ENTRY_RAY_ORDER_OR_SHAPE')
                factor = half*wi
                for key,array in zip(names,(n,q,u,(r-R1)[:,None]*q)):
                    pieces[key].append(factor*array)
        approximations.append({key:_sum_arrays(terms) for key,terms in pieces.items()})
    coarse,fine = approximations
    errors = {key:_relative(coarse[key],fine[key]) for key in names}
    diagnostics = {'schema':'rei.q1b.source_entry_time.v1','orders':list(orders),
        'rtol':rtol,'pair_rtol':PAIR_RTOL,'event_boundaries_s':points,
        'source_evaluations':snapshots,'per_cell_fine_scale_max_errors':errors,
        'zero_fine_requires_exact_zero':True,'photon_floor':False,
        'quadrature_claim':'Predetermined order-pair comparison, not a rigorous error certificate',
        'pass':all(v <= rtol for v in errors.values())}
    if not diagnostics['pass']:
        raise SourceEntryError('SOURCE_ENTRY_TIME_QUADRATURE_REJECTED',diagnostics)
    # This identity follows from the physical work integrand, not from defining
    # work as a ledger residual. Use compensated summation for the comparison.
    residual = _sum_arrays([R1[:,None]*fine['dQ'],fine['radiation_source_work_eV'],
                           -fine['injected_energy_eV']])
    scale = np.maximum.reduce([np.abs(R1[:,None]*fine['dQ']),
        np.abs(fine['radiation_source_work_eV']),np.abs(fine['injected_energy_eV'])])
    pairing = _scaled_residual(residual,scale)
    diagnostics['source_pairing_max_relative'] = pairing
    if pairing > PAIR_RTOL:
        raise SourceEntryError('SOURCE_ENTRY_SOURCE_PAIRING_REJECTED',diagnostics)
    return {**fine,'R0':R0.copy(),'R1':R1.copy(),'t0':float(t0),'t1':float(t1),
            'diagnostics':diagnostics}


def _scaled_residual(residual,scale):
    nonzero = scale > 0
    relative = np.zeros_like(scale)
    np.divide(np.abs(residual),scale,out=relative,where=nonzero)
    return (math.inf if np.any((~nonzero) & (residual != 0))
            else float(np.max(relative)))


def advance_source(N0,U0,result):
    """Apply the integrated source and exact redshift map to existing moments."""
    N0,U0 = np.asarray(N0,float),np.asarray(U0,float)
    if (N0.shape != result['dN'].shape or U0.shape != N0.shape
            or not np.isfinite(N0).all() or not np.isfinite(U0).all()
            or np.any(N0 < 0) or np.any(U0 < 0) or np.any((N0 == 0) != (U0 == 0))):
        raise ValueError('SOURCE_ENTRY_INITIAL_MOMENT_DOMAIN')
    r0,r1 = result['R0'][:,None],result['R1'][:,None]
    Q0 = U0/r0
    N,Q = N0+result['dN'],Q0+result['dQ']
    U = r1*Q
    work = (r0-r1)*Q0+result['radiation_source_work_eV']
    injected = result['injected_energy_eV']
    residual = _sum_arrays([U,-U0,work,-injected])
    scale = np.maximum.reduce([np.abs(U),np.abs(U0),np.abs(work),np.abs(injected)])
    pairing = _scaled_residual(residual,scale)
    if not all(np.isfinite(a).all() for a in (N,Q,U,work,residual)) or pairing > PAIR_RTOL:
        raise SourceEntryError('SOURCE_ENTRY_FINAL_PAIRING_REJECTED',{'pairing':pairing})
    return {'N':N,'U_eV':U,'Q_eV':Q,'radiation_work_eV':work,
            'energy_pairing_residual_eV':residual,
            'diagnostics':{'pairing_max_relative':pairing,'pair_rtol':PAIR_RTOL,
                           'pass':True,'claim':'Source plus redshift only; no absorption/gas/history admission'}}
