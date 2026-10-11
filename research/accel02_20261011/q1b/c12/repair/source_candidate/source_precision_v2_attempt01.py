"""C12 positive-offset assembly of the SAME pinned FLRW HM12 source moment.

For each fixed cell [a,b], N=integral s and D=integral(q-a)s are already
computed independently by C11's analytic positive formulas. This version forms
Q=fl(fl(a*N)+D), then U=fl(R*Q), rather than independently rounding the Q
integral. D remains ephemeral source arithmetic; no new state/checkpoint field,
source floor, clipping, band movement, tolerance change or provider replacement.
The unchanged exact moment cone and original pair tolerance still fail closed.
"""
from __future__ import annotations
from pathlib import Path
import sys
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'c11/precision'))
import source_precision as _v1
SourceEntryError=_v1.SourceEntryError
PAIR_RTOL=_v1.PAIR_RTOL
provider_event_times=_v1.provider_event_times
advance_source=_v1.advance_source

class StableCellSource(_v1.StableCellSource):
    def source(self,t,band=None):
        value=super().source(t,band)
        n,d,r=value['N'],value['D_eV'],value['R'];raw_q=value['Q_eV']
        q=self.edges[:-1][None,:]*n+d
        discrepancy=_v1._relative(raw_q,q)
        if discrepancy>PAIR_RTOL:
            raise SourceEntryError('SOURCE_OFFSET_ASSEMBLY_IDENTITY_REJECTED',{'relative':discrepancy,'rtol':PAIR_RTOL})
        if (not np.isfinite(q).all() or np.any(q<self.edges[:-1][None,:]*n)
                or np.any(q>self.edges[1:][None,:]*n)):
            raise ValueError('SOURCE_OFFSET_EXACT_MOMENT_CONE_REJECTED')
        value.update(Q_eV=q,U_eV=r[:,None]*q,
            moment_assembly=dict(formula='Q=fl(fl(a*N)+D); D=integral(q-a)source',
                raw_Q_relative_difference=discrepancy,rtol=PAIR_RTOL,
                source_N_unchanged=True,source_D_unchanged=True,source_R_unchanged=True,
                exact_cell_moment_cone=True,clipping=False,floor=False,
                state_representation_unchanged=True))
        return value

def integrate_source(cell_source,t0,t1,event_times=(),orders=(16,32),rtol=1e-10):
    source=cell_source if isinstance(cell_source,StableCellSource) else StableCellSource(cell_source)
    result=_v1.integrate_source(source,t0,t1,event_times=event_times,orders=orders,rtol=rtol)
    result['diagnostics']['source_moment_assembly']='C12_POSITIVE_OFFSET_Q_aN_PLUS_D'
    result['diagnostics']['source_assembly_pair_rtol']=PAIR_RTOL
    return result
