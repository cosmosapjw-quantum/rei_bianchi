"""Full-target schedules; source quadrature energy kinks stay internal.

Only FLRW r=0 is admitted by the current C11 source. Hard source events solve
R(t) * q_edge = E_band using the frozen provider's ray and the same brentq
settings as c10/source_entry.py, but just the two physical band edges. Output
values are copied verbatim, never regenerated or interpolated. Exact duplicate
times merge labels; merely nearby floating values remain distinct.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
EPOCH_SOURCE_SHA256 = '91959c5e09073ae89afcfe14937e6bc2dc4478692143873471934f542fc1ad6d'


def _canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     allow_nan=False).encode()).hexdigest()


def _checked_epochs(document, end):
    times = [float(t) for t in document['time_s']]
    if (len(times) != 129 or any(not math.isfinite(t) for t in times)
            or times[0] != 0. or times[-1] != end
            or any(a >= b for a,b in zip(times,times[1:]))):
        raise ValueError('PRODUCTION_EXACT_EPOCH_DOMAIN')
    if [t.hex() for t in times] != document['time_s_hex']:
        raise ValueError('PRODUCTION_EXACT_EPOCH_HEX_IDENTITY')
    if document['shared65_indices'] != list(range(0,129,2)):
        raise ValueError('PRODUCTION_SHARED65_INDEX_IDENTITY')
    return times


def build_schedule(cell_source, epoch_document, *, provenance=None):
    """Pure builder from an existing provider/source and exact epoch document.

    No native call, source-rate evaluation or all-energy-knot scan occurs. The
    caller must pass the returned full hard_events_s to the controller, while
    each map retains source_precision.provider_event_times for its own source
    quadrature subdivisions. hard_events_s excludes t=0 for the existing
    checkpoint contract; epoch0 is represented in initial_boundary_labels.
    """
    p = cell_source.provider
    if p.r != 0.:
        raise ValueError('PRODUCTION_SCHEDULE_FLRW_ONLY')
    end = float(p.end_time_s)
    if not math.isfinite(end) or end <= 0.:
        raise ValueError('PRODUCTION_SCHEDULE_END_DOMAIN')
    epochs = _checked_epochs(epoch_document, end)
    edges = np.asarray(cell_source.edges, float)
    mu = np.asarray(cell_source.mu, float)
    band = np.asarray(p.photon_band_eV, float)
    if (edges.ndim != 1 or len(edges)<2 or not np.isfinite(edges).all()
            or np.any(edges<=0.) or np.any(np.diff(edges)<=0.)
            or mu.ndim!=1 or not len(mu) or not np.isfinite(mu).all()
            or np.any(np.abs(mu)>1.) or band.shape!=(2,)
            or not np.isfinite(band).all() or not 0.<band[0]<band[1]):
        raise ValueError('PRODUCTION_SCHEDULE_SOURCE_DOMAIN')
    def ray(t):
        value = np.asarray(p.ray(np.ones(len(mu)), mu, float(t))[2], float)
        if value.shape != mu.shape or not np.isfinite(value).all() or np.any(value<=0.):
            raise ValueError('PRODUCTION_SCHEDULE_RAY_DOMAIN')
        return value
    r0,r1 = ray(0.),ray(end)
    if np.any(r1>=r0):
        raise ValueError('PRODUCTION_SCHEDULE_EXPANDING_RAYS_REQUIRED')
    records = {}
    def add(t, label):
        t = float(t)
        if not math.isfinite(t) or not 0.<=t<=end:
            raise ValueError('PRODUCTION_SCHEDULE_EVENT_DOMAIN')
        labels = records.setdefault(t, [])
        if label not in labels:
            labels.append(label)
    for index,t in enumerate(epochs):
        add(t, {'kind':'OUTPUT','epoch_index':index})
    for angle in range(len(mu)):
        for edge_index,edge in enumerate(edges):
            for energy in band:
                target = float(energy/edge)
                if target==r0[angle]: t=0.
                elif target==r1[angle]: t=end
                elif r1[angle]<target<r0[angle]:
                    t = brentq(lambda t: ray(t)[angle]-target,0.,end,
                               xtol=1.e-4,rtol=4*math.ulp(1.))
                else: continue
                add(t, {'kind':'SOURCE_BAND_CELL_EDGE','angle_index':angle,
                        'edge_index':edge_index,'q_edge_eV':float(edge),
                        'energy_eV':float(energy)})
    z0,z1 = float(p.geometry(0.)['z']),float(p.geometry(end)['z'])
    zknots = np.asarray(p.tables['emissivity'].redshifts,float)
    if not np.isfinite(zknots).all() or not z0>z1:
        raise ValueError('PRODUCTION_SCHEDULE_REDSHIFT_DOMAIN')
    for z in zknots:
        if z==z0: t=0.
        elif z==z1: t=end
        elif z1<z<z0: t=p.background.time_of_redshift(float(z))
        else: continue
        add(t, {'kind':'EMISSIVITY_REDSHIFT_KNOT','z':float(z)})
    times = sorted(t for t in records if t>0.)
    physical = [t for t in times if any(l['kind']!='OUTPUT' for l in records[t])]
    schedule = {
        'schema':'rei.q1b.c12.production_schedule.v1',
        'scope':'PINNED_C11_FLRW_R0_WHOLE_HISTORY',
        'start_time_s':0.,'end_time_s':end,'target_time_s':end,
        'hard_events_s':times,
        'hard_event_times_hex':[t.hex() for t in times],
        'physical_hard_events_s':physical,
        'output_epochs_s':epochs,
        'output_epoch_times_hex':[t.hex() for t in epochs],
        'shared65_indices':list(range(0,129,2)),
        'hard_event_records':[{'time_s':t,'time_s_hex':t.hex(),'labels':records[t]} for t in times],
        'initial_boundary_labels':records[0.],
        'internal_source_quadrature':{
            'api':'source_precision.provider_event_times(cell_source,t0,t1)',
            'implementation':'c10/source_entry.py:provider_event_times',
            'includes_all_emissivity_energy_knots':True,
            'global_materialized':False,
            'unchanged_per_map_call_required':True},
        'opacity_thresholds':'Existing per-cell quadrature cuts; not new global hard events',
        'duplicate_policy':'Merge exact binary64 times only; retain all event labels',
        'root_solver':{'method':'scipy.optimize.brentq','xtol_s':1.e-4,
                       'rtol':4*math.ulp(1.),'same_as_frozen_source_entry':True},
        'provenance':{
            'provider_identity':dict(p.identity),
            'source_grid_inputs_sha256':_canonical_hash({'edges':edges.tolist(),'mu':mu.tolist(),'band':band.tolist()}),
            'epoch_document_sha256_canonical':_canonical_hash(epoch_document),
            'emissivity_redshift_knots_sha256_canonical':_canonical_hash(zknots.tolist()),
            'caller':{} if provenance is None else dict(provenance)},
        'native_calls':0,'old_completed_replays':0,
        'claim':'Schedule binding only; no full-history scientific admission'}
    schedule['content_sha256_canonical'] = _canonical_hash(schedule)
    return schedule


def build_real_schedule(cell_source):
    """Load the immutable saved 129-epoch file and its pinned Q0 source bytes."""
    path = HERE.parent/'production_design/OUTPUT_EPOCHS.json'
    document = json.loads(path.read_text())
    repo = HERE.parents[5]
    source_path = repo/document['source']
    source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
    if document['source_sha256'] != EPOCH_SOURCE_SHA256 or source_hash != EPOCH_SOURCE_SHA256:
        raise ValueError('PRODUCTION_SCHEDULE_Q0_SOURCE_IDENTITY')
    source = json.loads(source_path.read_text())
    if [float(x['time_s']) for x in source['exact_source_history']] != document['time_s']:
        raise ValueError('PRODUCTION_SCHEDULE_Q0_EPOCH_CONTENT_IDENTITY')
    return build_schedule(cell_source, document, provenance={
        'epoch_file':str(path.relative_to(repo)),
        'epoch_file_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
        'q0_source_file':document['source'],'q0_source_sha256':source_hash,
        'schedule_code_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})


def schedule_window(schedule,t0,t1):
    """Strict interior cuts for diagnostics; a zero-width interval has none."""
    t0,t1 = float(t0),float(t1)
    if (not math.isfinite(t0) or not math.isfinite(t1)
            or not 0.<=t0<=t1<=schedule['end_time_s']):
        raise ValueError('PRODUCTION_SCHEDULE_WINDOW_DOMAIN')
    return tuple(t for t in schedule['hard_events_s'] if t0<t<t1)
