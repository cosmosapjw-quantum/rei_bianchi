"""DR11 finite-Markov first-hit bookkeeping; NOT physical ionization.

Adds diagnostic observables without changing the inherited Eq50 propagator.
A trajectory tag records whether the path has ever entered shell >= threshold.
The tag is classical path information: no coherent-history interpretation is made.
"""
from __future__ import annotations
from numbers import Integral
from typing import Sequence
import numpy as np
from arseny_reimpl.correlation import cordir_heh


def _integer(value: int, name: str, minimum: int = 1) -> int:
    if isinstance(value, (bool, np.bool_)) or not isinstance(value, Integral) or value < minimum:
        raise ValueError(f'{name} must be an integer >= {minimum}')
    return int(value)


def _shell_array(shells: Sequence[int], dim: int) -> np.ndarray:
    raw = list(shells)
    if len(raw) != dim:
        raise ValueError('one shell label per state is required')
    return np.array([_integer(s, 'shell') for s in raw], dtype=int)


def tagged_eq50(probabilities, events, P_rot, initial, *, shells, threshold: int) -> dict:
    """Apply the unchanged Eq50 event order with a passive first-hit tag.

    Inputs use the inherited batch/state/initial-column convention. Probabilities
    and each initial column must be normalized and nonnegative. ``events`` are
    zero-based (i,j,absorbing_j). ``first_hit_flux`` includes the initial hit mass,
    then one value after every event or rotation. It counts each path only once.
    """
    threshold = _integer(threshold, 'threshold')
    p = np.asarray(probabilities, dtype=float)
    rot = np.asarray(P_rot, dtype=float)
    init = np.asarray(initial, dtype=float)
    if p.ndim != 2 or p.shape[0] == 0 or p.shape[1] != len(events):
        raise ValueError('invalid probability batch')
    if rot.ndim != 3 or rot.shape[0] != p.shape[0] or rot.shape[1] != rot.shape[2]:
        raise ValueError('invalid rotation batch')
    dim = rot.shape[1]
    if dim == 0 or init.ndim != 2 or init.shape[0] != dim or init.shape[1] == 0:
        raise ValueError('invalid initial columns')
    if (np.any(~np.isfinite(p)) or np.any((p < 0) | (p > 1))
            or np.any(~np.isfinite(rot)) or np.any(rot < 0)
            or np.any(~np.isfinite(init)) or np.any(init < 0)):
        raise ValueError('finite nonnegative probabilities are required')
    if np.max(abs(rot.sum(axis=1)-1)) > 2e-10 or np.max(abs(init.sum(axis=0)-1)) > 2e-10:
        raise ValueError('rotation and initial columns must be normalized')
    sh = _shell_array(shells, dim)
    hit_mask = sh >= threshold
    ev = []
    for event in events:
        if len(event) != 3:
            raise ValueError('event must be (i,j,absorbing_j)')
        i, j, sink = event
        i = _integer(i, 'event i', 0); j = _integer(j, 'event j', 0)
        if i >= dim or j >= dim or i == j or not isinstance(sink, (bool, np.bool_)):
            raise ValueError('invalid event index or absorbing flag')
        ev.append((i, j, bool(sink)))
    never = np.broadcast_to(init, (len(p), *init.shape)).copy()
    hit = np.zeros_like(never)
    flux = []

    def tag() -> None:
        first = never[:, hit_mask, :].copy()
        flux.append(first.sum(axis=1))
        hit[:, hit_mask, :] += first
        never[:, hit_mask, :] = 0.

    def update(k: int) -> None:
        i, j, sink = ev[k]
        q = p[:, k, None]
        for y in (never, hit):
            yi = y[:, i, :].copy(); yj = y[:, j, :].copy()
            if sink:
                y[:, i, :] = (1-q)*yi
                y[:, j, :] = yj+q*yi
            else:
                y[:, i, :] = (1-q)*yi+q*yj
                y[:, j, :] = (1-q)*yj+q*yi
        tag()

    tag()
    for k in reversed(range(len(ev))):
        update(k)
    never = rot @ never
    hit = rot @ hit
    tag()
    for k in range(len(ev)):
        update(k)
    return {'never_hit': never, 'hit': hit, 'total': never+hit,
            'first_hit_flux': np.stack(flux, axis=1), 'threshold': threshold,
            'shells': sh, 'claim': 'PASSIVE_FINITE_MARKOV_FIRST_HIT_BOOKKEEPING'}


def migration_budget(result: dict, *, shells, old_threshold: int, new_threshold: int) -> dict:
    """Split formerly absorbed paths into return, resolved promotion and new tail.

    Equality to an independently computed old-N sink requires matching the
    pre-first-hit dynamics. The function does NOT assume this merely because
    two calculations have consecutive Nmax labels.
    """
    old_threshold = _integer(old_threshold, 'old threshold')
    new_threshold = _integer(new_threshold, 'new threshold')
    if old_threshold >= new_threshold or result['threshold'] != old_threshold:
        raise ValueError('require tag threshold = old threshold < new threshold')
    hit = np.asarray(result['hit'], dtype=float)
    if hit.ndim != 3 or np.any(~np.isfinite(hit)) or np.any(hit < 0):
        raise ValueError('invalid tagged population')
    sh = _shell_array(shells, hit.shape[1])
    if not np.array_equal(sh, result['shells']) or np.any(sh > new_threshold):
        raise ValueError('shell labels inconsistent with tag or final truncation')
    returned = hit[:, sh < old_threshold, :].sum(axis=1)
    promoted = hit[:, (sh >= old_threshold) & (sh < new_threshold), :].sum(axis=1)
    unresolved = hit[:, sh == new_threshold, :].sum(axis=1)
    ever_hit = hit.sum(axis=1)
    return {'returned_below_old': returned, 'resolved_old_to_new': promoted,
            'new_unresolved': unresolved, 'ever_hit': ever_hit,
            'first_hit_flux_total': result['first_hit_flux'].sum(axis=1),
            'closure_defect': ever_hit-returned-promoted-unresolved,
            'never_hit_total': result['never_hit'].sum(axis=1),
            'old_model_equivalence_automatic': False,
            'claim': 'COMMON_HISTORY_MIGRATION_IDENTITY_NOT_PHYSICAL_CONTINUUM'}


def correlation_rows(Nmax: int) -> list[dict]:
    """Inventory the inherited folded-|m| CORDIR map, with disjoint model roles.

    Finite endpoint labels never turn a truncation-sink population into a bound
    yield. N>3 uses the inherited ordered-complement extension, NOT a newly
    independently validated correlation formula.
    """
    Nmax = _integer(Nmax, 'Nmax')
    rows = []
    for N in range(1, Nmax+1):
        for l in range(N):
            for m in range(l+1):
                s = cordir_heh(N, l, m)
                unresolved = N == Nmax
                channel = None if unresolved else (
                    'capture_Z2' if s.center == 'Z2' else
                    'survival_Z1_1s' if s.n == 1 else 'excitation_Z1')
                rows.append({'index': len(rows), 'united': [N,l,m],
                    'kind': 'unresolved' if unresolved else 'resolved_bound_model',
                    'physical_channel': channel,
                    'formal_asymptote': {'center': s.center, 'Z': s.Z, 'n': s.n,
                        'n1': s.n1, 'n2': s.n2, 'm': s.m,
                        'energy_hartree': -s.Z**2/(2.*s.n**2)},
                    'map_authority': ('APPENDIX_A_NMAX3_MATCH_INHERITED' if N <= 3 else
                        'ORDERED_COMPLEMENT_EXTENSION_NOT_INDEPENDENTLY_VALIDATED')})
    return rows


def channel_ledger(population, Nmax: int) -> dict:
    """Disjoint finite-model totals for the H(1s) entrance, not elastic areas."""
    rows = correlation_rows(Nmax)
    p = np.asarray(population, dtype=float)
    if p.ndim != 1 or len(p) != len(rows) or np.any(~np.isfinite(p)) or np.any(p < 0):
        raise ValueError('invalid normalized population vector')
    if abs(p.sum()-1) > 2e-10:
        raise ValueError('population must be normalized')
    keys = ('survival_Z1_1s', 'excitation_Z1', 'capture_Z2', 'unresolved')
    result = {k: 0. for k in keys}
    resolved = {}
    for weight, row in zip(p, rows):
        key = 'unresolved' if row['kind'] == 'unresolved' else row['physical_channel']
        result[key] += float(weight)
        if row['kind'] != 'unresolved':
            s = row['formal_asymptote']
            label = f"{s['center']}:n={s['n']}"
            resolved[label] = resolved.get(label, 0.)+float(weight)
    result.update(resolved_separated_shells=resolved,
        probability_closure_defect=float(sum(result[k] for k in keys)-p.sum()),
        ionization_available=False, physical_convergence_certified=False,
        elastic_cross_section_available=False,
        claim='DISJOINT_FINITE_MODEL_CHANNEL_LEDGER_ONLY')
    return result


def shell_coverage(center: str, n: int, Nmax: int) -> dict:
    """Audit completeness of a FIXED separated shell, not a moving united shell.

    Enumerates folded-|m| parabolic channels, without an extra 2-fold multiplier.
    Completeness here is representational only, NOT dynamical convergence.
    For Z1, Eq17 implies N=2*n+n2, so Nmax>=3*n is necessary and sufficient
    to place the whole shell strictly below the absorbing united-atom boundary.
    Z2 beyond Appendix A remains conditional on the inherited complement map.
    """
    from arseny_reimpl.correlation import corinv_heh
    if center not in ('Z1','Z2'):
        raise ValueError('center must be Z1 or Z2')
    n = _integer(n, 'separated n'); Nmax = _integer(Nmax, 'Nmax')
    states = []
    for m in range(n):
        for n1 in range(n-m):
            n2 = n-1-m-n1
            u = corinv_heh(center,n,n1,n2,m)
            role = 'resolved' if u.N < Nmax else 'boundary' if u.N == Nmax else 'outside'
            states.append({'separated': {'center':center,'n':n,'n1':n1,'n2':n2,'m':m},
                           'united':[u.N,u.l,u.m],'role':role})
    counts = {f'{role}_count':sum(x['role']==role for x in states)
              for role in ('resolved','boundary','outside')}
    return {'center':center,'n':n,'Nmax':Nmax,**counts,'folded_channel_count':len(states),
            'minimum_Nmax_for_resolved_shell':max(x['united'][0] for x in states)+1,
            'complete_resolved_shell':counts['resolved_count']==len(states),
            'dynamical_convergence_certified':False,'states':states,
            'authority':('DERIVED_FROM_SOURCE_EQ17' if center=='Z1' else
                'CONDITIONAL_ON_INHERITED_ORDERED_COMPLEMENT_MAP')}
