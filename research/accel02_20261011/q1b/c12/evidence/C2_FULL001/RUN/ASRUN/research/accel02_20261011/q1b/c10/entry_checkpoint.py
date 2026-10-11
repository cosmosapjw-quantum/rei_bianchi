"""Strict C10 split-step boundary adapter over existing atomic publication.

This adapter preserves a *bounded sequence of accepted step boundaries*. Every
accepted boundary is in prefix_state; there is no compressed history, hidden
Newton state or BDF restart claim. It checks domains and paired ledgers again
on both write and load. Passing this validator does not admit a full history.
"""
from __future__ import annotations
import hashlib
from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'checkpoint'))
from atomic_checkpoint import (CheckpointError, publish_generation, load_generation)

COUNTERS = ('Nsource', 'Nabs', 'Esource_eV', 'Eescape_eV', 'Wrad_eV',
            'Wthermal_eV', 'ECMB_eV')
GAS_FIELDS = ('xHII', 'xHeII', 'xHeIII', 'w_eV_per_H')
CHI = np.array([13.598434599702, 24.587389011, 54.41776])
# Same constants used by n1 native gas provider; retain full ratio, not a fit.
KB_EV = 1.380649e-16 / 1.602176634e-12
RESTART = 'FRESH_SPLIT_STEP_AT_NATURAL_SEGMENT_BOUNDARY'
SCHEMA = 'rei.q1b.entry_checkpoint.v1'
SCOPES = {'MANUFACTURED_SPLIT_RADIATIVE_ESCAPE', 'SOURCE_ENTRY_POSITIVE_STEP_V1'}


def _require(ok, message):
    if not ok:
        raise CheckpointError(message)


def entry_identity(*, source, grid, binary, control, physics_contract):
    """Hash caller-selected actual files; this establishes bytes, not authority."""
    paths = dict(source=source, grid=grid, binary=binary, control=control,
                 physics_contract=physics_contract,
                 physical_validator=Path(__file__).resolve())
    return {name: hashlib.sha256(Path(path).read_bytes()).hexdigest()
            for name, path in paths.items()}


def pack_entry_state(gas, N, U_eV, counters):
    """Return [gas4, N[n], U[n], seven counters] without projection or floors."""
    gas, N, U_eV = (np.asarray(x, dtype=float) for x in (gas, N, U_eV))
    _require(gas.shape == (4,) and N.ndim == 1 and N.size > 0 and
             U_eV.shape == N.shape, 'Entry state shapes')
    _require(isinstance(counters, dict) and set(counters) == set(COUNTERS),
             'Exactly all seven paired counters are required')
    state = np.concatenate((gas, N, U_eV, [counters[k] for k in COUNTERS]))
    _require(np.isfinite(state).all(), 'Finite entry state required')
    return state


def unpack_entry_state(state, cells):
    state = np.asarray(state)
    _require(state.shape == (4+2*cells+len(COUNTERS),), 'Packed state shape')
    return dict(gas=state[:4].copy(), N=state[4:4+cells].copy(),
                U_eV=state[4+cells:4+2*cells].copy(),
                counters=dict(zip(COUNTERS, state[4+2*cells:].tolist())))


def _ledger_residuals(states, cells, nH, nHe):
    gas = states[:, :4]
    photons_N = states[:, 4:4+cells].sum(axis=1)
    photons_U = states[:, 4+cells:4+2*cells].sum(axis=1)
    counters = states[:, 4+2*cells:]
    dc = counters - counters[0]
    gas_E = nH*(gas[:,3]+CHI[0]*gas[:,0]) + nHe*(
        CHI[1]*gas[:,1]+(CHI[1]+CHI[2])*gas[:,2])
    energy = photons_U + gas_E
    number_residual = photons_N - photons_N[0] + dc[:,1] - dc[:,0]
    energy_residual = energy-energy[0]+dc[:,3]+dc[:,4]+dc[:,5]-dc[:,2]-dc[:,6]
    _require(np.isfinite(energy[0]) and energy[0] > 0, 'Positive initial energy origin required')
    return number_residual/nH, energy_residual/energy[0], energy[0]


def _layout(cells):
    fields = list(GAS_FIELDS) + [f'N[{i}]' for i in range(cells)] + [
        f'U_eV[{i}]' for i in range(cells)] + list(COUNTERS)
    units = ['1','1','1','eV/H']+['reference_cm-3']*cells+[
        'eV/reference_cm3']*cells+['reference_cm-3']*2+['eV/reference_cm3']*5
    return fields, units, list(range(4+2*cells, len(fields)))


def make_entry_snapshot(*, clocks, states, R, support, all_boundary_clocks,
                        nH_ref, nHe_ref, scales, physical_binding):
    """Build schema for a paused bounded sequence, retaining every boundary.

    R has shape [prefix,cell]; support is [prefix,cell,2] in q eV. A dormant
    cell may have b<=a but must then contain exactly zero N and U. Inputs use
    float64; no interpolation, repair, clipping or synthetic history is done.
    all_boundary_clocks must be the complete frozen sequence for this bounded
    run, including future boundaries; this is not an adaptive long-run API.
    """
    clocks, states, R, support, all_boundary_clocks, scales = (
        np.asarray(v, dtype=float).copy() for v in
        (clocks, states, R, support, all_boundary_clocks, scales))
    _require(states.ndim == 2 and states.shape[1] >= 13, 'State prefix shape')
    cells, rem = divmod(states.shape[1]-4-len(COUNTERS), 2)
    _require(rem == 0 and cells > 0, 'Packed cell count')
    _require(clocks.ndim == 1 and clocks.size == states.shape[0], 'Prefix clocks shape')
    fields, units, indices = _layout(cells)
    _require(type(nH_ref) in (int,float) and np.isfinite(nH_ref) and nH_ref>0 and
             type(nHe_ref) in (int,float) and np.isfinite(nHe_ref) and nHe_ref>=0,
             'Reference nuclei densities')
    rn, re, E0 = _ledger_residuals(states, cells, nH_ref, nHe_ref)
    completed = clocks.size-1
    edges = all_boundary_clocks
    _require(completed < edges.size and clocks[-1] == edges[completed], 'Natural boundary cursor')
    next_segment = None if completed == edges.size-1 else [float(edges[completed]),float(edges[completed+1])]
    arrays = dict(state=states[-1].copy(), scales=scales,
        counter_origins=states[0,indices].copy(), prefix_clock=clocks,
        prefix_state=states, scheduled_clock=edges.copy(), segment_edges=edges,
        accepted_min=states.min(axis=0), accepted_max=states.max(axis=0))
    metadata = dict(schema=SCHEMA, cell_count=cells, state_fields=fields,
        state_units=units, counter_indices=indices, current_clock=float(clocks[-1]),
        completed_segments=completed, next_segment_index=completed,
        next_segment=next_segment, accepted_domain_flags={'all_saved_boundaries':True},
        ledger_max={'number':float(np.max(abs(rn))),'energy':float(np.max(abs(re)))},
        ledger_origins={'number':float(nH_ref),'energy':float(E0)},
        restart_kind=RESTART, physical_binding=physical_binding,
        accepted_history_scope='EVERY_ACCEPTED_SPLIT_STEP_BOUNDARY_SAVED',
        precision_representation='BINARY64_N_U_NO_HIDDEN_LOW_COMPONENTS',
        native_driver_binding='REQUIRES_ACTUAL_DRIVER_EVIDENCE',
        nH_ref=float(nH_ref), nHe_ref=float(nHe_ref),
        prefix_R=R.tolist(), prefix_support=support.tolist(),
        current_R=R[-1].tolist(), current_support=support[-1].tolist(),
        ledger_tolerance={'number':1e-9,'energy':1e-9})
    return arrays, metadata


def validate_entry_snapshot(arrays, meta):
    """Domain/ledger callback, source-hashed by the generic atomic layer."""
    _require(meta.get('schema') == SCHEMA and meta.get('restart_kind') == RESTART,
             'Entry schema or split restart kind mismatch')
    _require(meta.get('physical_binding') in SCOPES, 'Unsupported entry physics scope')
    _require(meta.get('accepted_history_scope') == 'EVERY_ACCEPTED_SPLIT_STEP_BOUNDARY_SAVED',
             'Complete accepted boundary history is mandatory')
    _require(meta.get('precision_representation') == 'BINARY64_N_U_NO_HIDDEN_LOW_COMPONENTS',
             'Unsupported precision state: authoritative low components must be saved')
    _require(meta.get('ledger_tolerance') == {'number':1e-9,'energy':1e-9},
             'Frozen number/energy criteria changed')
    cells = meta.get('cell_count')
    _require(type(cells) is int and cells>0, 'Cell count')
    fields, units, indices = _layout(cells)
    _require(meta['state_fields']==fields and meta['state_units']==units and
             meta['counter_indices']==indices, 'State layout identity mismatch')
    history = arrays['prefix_state']
    _require(np.array_equal(arrays['scheduled_clock'], arrays['segment_edges']) and
             np.array_equal(arrays['prefix_clock'], arrays['segment_edges'][:history.shape[0]]),
             'Every accepted boundary must be preserved')
    _require(np.array_equal(arrays['accepted_min'], history.min(axis=0)) and
             np.array_equal(arrays['accepted_max'], history.max(axis=0)),
             'Extrema do not match complete accepted boundary history')
    nH, nHe = meta.get('nH_ref'), meta.get('nHe_ref')
    _require(type(nH) in (int,float) and type(nHe) in (int,float) and
             np.isfinite(nH) and nH>0 and np.isfinite(nHe) and nHe>=0,
             'Reference nuclei densities')
    gas = history[:,:4]
    _require(np.all((gas[:,0]>=0)&(gas[:,0]<=1)) and
             np.all(gas[:,1:3]>=0) and np.all(gas[:,1]+gas[:,2]<=1),
             'Gas ion fraction domain')
    particle_per_H = 1+nHe/nH+gas[:,0]+nHe/nH*(gas[:,1]+2*gas[:,2])
    temperature = 2*gas[:,3]/(3*KB_EV*particle_per_H)
    _require(np.all((temperature>=1)&(temperature<=1e6)), 'Gas temperature domain')
    try:
        R = np.asarray(meta['prefix_R'], dtype=float)
        support = np.asarray(meta['prefix_support'], dtype=float)
    except (KeyError,TypeError,ValueError) as exc:
        raise CheckpointError('Missing or malformed support/geometry history') from exc
    _require(R.shape==(history.shape[0],cells) and support.shape==(history.shape[0],cells,2)
             and np.isfinite(R).all() and np.isfinite(support).all() and np.all(R>0)
             and np.all(support>0), 'Support/geometry history domain')
    _require(np.array_equal(np.asarray(meta.get('current_R')), R[-1]) and
             np.array_equal(np.asarray(meta.get('current_support')), support[-1]),
             'Current support/geometry disagrees with history')
    N = history[:,4:4+cells]; U = history[:,4+cells:4+2*cells]
    _require(np.all(N>=0) and np.all(U>=0), 'Photon positivity')
    empty = N==0
    _require(np.all(U[empty]==0), 'Empty cell must have zero paired energy')
    active = ~empty
    if active.any():
        a,b = support[:,:,0],support[:,:,1]
        mean = U[active]/(R[active]*N[active])
        _require(np.all(a[active]<mean) and np.all(mean<b[active]),
                 'Incident moment cone or unimplemented endpoint trace')
    counters = history[:,4+2*cells:]
    _require(np.all(np.diff(counters[:,:6],axis=0)>=0),
             'Source, loss, and expansion work counters must not decrease')
    rn,re,E0 = _ledger_residuals(history,cells,nH,nHe)
    _require(meta['ledger_origins']=={'number':nH,'energy':float(E0)}, 'Ledger normalization origins changed')
    maxima = dict(number=float(np.max(abs(rn))),energy=float(np.max(abs(re))))
    for name in ('number','energy'):
        _require(maxima[name]<=1e-9 and meta['ledger_max'][name]<=1e-9,
                 f'{name}: paired ledger exceeds frozen tolerance')
        # Bookkeeping comparison only: allow a few normalized arithmetic ulps;
        # the independent frozen 1e-9 residual gate above has no allowance.
        _require(meta['ledger_max'][name]+16*np.finfo(float).eps>=maxima[name],
                 f'{name}: carried ledger maximum omits saved residual')
    return dict(domain_checked=True,ledgers_checked=True,scope=meta['physical_binding'],
                observed_ledger_max=maxima,native_driver_bound_by_this_adapter=False,
                scientific_admission=False)


def write_entry_checkpoint(directory, generation, arrays, metadata, expected_identity):
    return publish_generation(directory,generation,arrays,metadata,expected_identity,
                              validate_entry_snapshot)


def load_entry_checkpoint(directory, generation, expected_identity, *, expected_manifest_sha256=None):
    return load_generation(directory,generation,expected_identity,validate_entry_snapshot,
                           expected_manifest_sha256=expected_manifest_sha256)
