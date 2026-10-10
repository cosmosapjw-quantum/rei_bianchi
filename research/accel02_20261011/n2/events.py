"""Known characteristic kinks and analytic dormant-node support.

Returned u=t/t_end boundaries are integration restart points, not extra source
packets. Birth is still a continuous source after entry. For monotone decreasing
energies, q nodes above current50keV have the exact invariant N=0 until entry;
they can be omitted from the ODE unknowns and inserted with that analytic IC.
"""
from __future__ import annotations
import numpy as np
from scipy.optimize import brentq
from characteristics import geometry_nodes


def crossing_events(q_eV,mu0,geometry,end_time_s,energies=(10.,13.60,24.59,54.42,50000.)):
    """Resolve each known energy crossing using the actual geometry callable.

    Event roots use normalized time; no interpolated background or fixed H.
    Only monotone decreasing characteristic energies are supported here, as in
    the selected expanding r=0,.05 histories. Other geometries fail closed.
    """
    q=np.asarray(q_eV);m=np.asarray(mu0)
    if not np.isfinite(end_time_s) or end_time_s<=0:raise ValueError('EVENT_TIME_DOMAIN')
    e0=geometry_nodes(q,m,geometry(0.))[0]
    ef=geometry_nodes(q,m,geometry(end_time_s))[0]
    for f in [.25,.5,.75,1.]:
        current=geometry_nodes(q,m,geometry(f*end_time_s))[0]
        if np.any(current>e0*(1+8*np.finfo(float).eps)):raise ValueError('NONMONOTONE_CHARACTERISTIC_EVENTS')
        e0=current
    e0=geometry_nodes(q,m,geometry(0.))[0]
    events=[]
    # Axisymmetry gives identical energies for +/-mu, share their solved root.
    roots={}
    for threshold in sorted(set(float(x) for x in energies)):
        if not np.isfinite(threshold) or threshold<=0:raise ValueError('EVENT_ENERGY_DOMAIN')
        indices=np.flatnonzero((e0>threshold)&(ef<threshold))
        for j in indices:
            key=(float(q[j]),float(abs(m[j])),threshold)
            if key not in roots:
                def residual(u):
                    return geometry_nodes(q[j:j+1],m[j:j+1],geometry(float(u*end_time_s)))[0][0]/threshold-1.
                roots[key]=brentq(residual,0.,1.,xtol=np.nextafter(0.,1.),rtol=8*np.finfo(float).eps)
            events.append(dict(u=float(roots[key]),time_s=float(roots[key]*end_time_s),node=int(j),energy_eV=threshold))
    return sorted(events,key=lambda e:(e['u'],e['energy_eV'],e['node']))


def source_entry_events(q_eV,mu0,geometry,end_time_s,upper_eV=50000.):
    return crossing_events(q_eV,mu0,geometry,end_time_s,[upper_eV])


def native_jump_energies(table):
    energy=table.energies_eV
    return np.unique(energy[:-1][np.diff(energy)==0]).tolist()


def segment_active_indices(q_eV,mu0,geometry,t0_s,t1_s,upper_eV=50000.):
    """Use the open segment support. No negative evolved value is replaced."""
    if not 0<=t0_s<t1_s:raise ValueError('EVENT_SEGMENT_DOMAIN')
    energy=geometry_nodes(q_eV,mu0,geometry(.5*(t0_s+t1_s)))[0]
    return np.flatnonzero(energy<upper_eV)


def restart_boundaries(events):
    """Coalesce numerically identical roots, preserving first/last interval."""
    values=sorted(set([0.,1.]+[float(e['u']) for e in events]))
    output=[values[0]]
    for value in values[1:]:
        if value-output[-1]>16*np.spacing(max(abs(value),abs(output[-1]),1e-300)):
            output.append(value)
    if output[-1]!=1.: output.append(1.)
    return np.array(output)
