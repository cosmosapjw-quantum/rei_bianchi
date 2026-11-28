"""In-process ORIGINAL event-box observer for native HeIII Lyalpha local reabsorption.

No original source file mutation and no synthetic spatial transfer. All source
site arrays are taken from exactly the original event_box(model,pop,temp,t).
"""
from __future__ import annotations
import numpy as np

E_ALPHA_EV = 40.813320
CHI_H = 13.598434599702
CHI_HE = 24.587389011
EV_ERG = 1.602176634e-12

def nonnegative_outer(value):
    lo = np.maximum(np.asarray(value.lo, dtype=np.float64), 0.0)
    hi = np.maximum(np.asarray(value.hi, dtype=np.float64), 0.0)
    if np.any(~np.isfinite(lo)) or np.any(~np.isfinite(hi)) or np.any(lo > hi):
        raise ArithmeticError("NATIVE_OTS_NONNEGATIVE_OUTER_INVALID")
    return lo,hi

def overlapping(left,right):
    return bool(np.all(left.lo <= right.hi) and np.all(left.hi >= right.lo))

def escaped_photon_energy_matches(photon_count, native_energy, rtol=6e-12):
    """Compare the same escaped source in photons and erg after conversion.

    This checks source representation, not a physical acceptance tolerance.
    The original f interval includes 1, so both lower bounds can be zero;
    interval intersection alone then cannot detect a wrong energy scale.
    Use the existing independent audit's 6e-12 representation tolerance.
    """
    photons = nonnegative_outer(photon_count)
    energy = nonnegative_outer(native_energy)
    return all(np.allclose(n * E_ALPHA_EV * EV_ERG, e, rtol=rtol, atol=0.0)
               for n, e in zip(photons, energy))

class OriginalEventObserver:
    def __init__(self, original_module):
        self.m=original_module
        self.original=original_module.event_box
        self.records={}
        self.calls=0
        self.max_heat_nonintersection=0
        self.max_escape_nonintersection=0

    def __call__(self, model, pop, temp, time_s):
        m=self.m
        ev=self.original(model,pop,temp,time_s)
        IV=m._I
        r=m.rim
        n=[IV(pop.lo[:,i],pop.hi[:,i]) for i in range(5)]
        vol=model.forcing_bounds(time_s,time_s).volume_cm3
        electron=(n[1]+n[3]+2*n[4])/vol
        z_h=(n[0]/vol)*r.SIGMA_OTS_H41
        z_he=(n[2]/vol)*r.SIGMA_OTS_HEI41
        z=z_h/(z_h+z_he+1.0e-300)
        v=m._source_v(temp)
        f=IV(np.full_like(temp.lo,.1),np.full_like(temp.hi,1.))
        a_b=r._alpha_b_heiii(temp)
        a_n2=m.iv.minimum(r._alpha_heiii_n2(temp),a_b)
        r_cas=n[4]*electron*m.iv.maximum(a_b-a_n2,0.)
        emitted=r_cas*(1-v)
        local_H=emitted*f*z
        local_HeI=emitted*f*(1-z)
        escaped=emitted*(1-f)
        chemical=(local_H*CHI_H+local_HeI*CHI_HE)*EV_ERG
        photoheat=(local_H*(E_ALPHA_EV-CHI_H)+local_HeI*(E_ALPHA_EV-CHI_HE))*EV_ERG
        energy_esc=escaped*E_ALPHA_EV*EV_ERG
        if not overlapping(photoheat,ev.resolved_heat):
            self.max_heat_nonintersection+=1
        if not overlapping(energy_esc,ev.escaped_energy):
            self.max_escape_nonintersection+=1
        payload={
            "emitted":emitted,
            "absorbed_H":local_H,
            "absorbed_HeI":local_HeI,
            "escaped":escaped,
            "chemical":chemical,
            "photoheat":photoheat,
            "heat_original":ev.resolved_heat,
            "escape_original":ev.escaped_energy,
            "r_cascade":r_cas,
        }
        self.records[id(ev)]=payload
        self.calls+=1
        return ev

    def snapshot(self, source_step):
        out={}
        for phase in ("stage_event","final_event"):
            event=getattr(source_step,phase)
            if id(event) not in self.records:
                raise RuntimeError("CAPTURED_ORIGINAL_STEP_EVENT_ID_MISSING_"+phase)
            out[phase]=self.records[id(event)]
        self.records.clear()
        return out
