"""C12 positive-offset assembly of the SAME pinned FLRW HM12 source moment.

For each fixed cell [a,b], N=integral s and D=integral(q-a)s are already
computed independently by C11's analytic positive formulas. This version forms
Q=fl(fl(a*N)+D), or symmetrically Q=fl(fl(b*N)-E) nearer the
upper face, with independently integrated E=integral(b-q)s >=0. U=fl(R*Q). D remains ephemeral source arithmetic; no new state/checkpoint field,
source floor, clipping, band movement, tolerance change or provider replacement.
The unchanged exact moment cone and original pair tolerance still fail closed.
"""
from __future__ import annotations
from pathlib import Path
import sys,math
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'c11/precision'))
import source_precision as _v1
SourceEntryError=_v1.SourceEntryError
PAIR_RTOL=_v1.PAIR_RTOL
provider_event_times=_v1.provider_event_times
advance_source=_v1.advance_source


def _negative_exponential_offsets(dx):
    """Positive integrals of (1-exp(-dx*u)) against 1-u and u."""
    if not 0<=dx<.5:raise ValueError('SOURCE_OFFSET_SEGMENT_WIDTH')
    t=dx;v0=v1=0.
    for k in range(1,25):
        v0+=t/((k+1)*(k+2));v1+=t/(k+2)
        t*=(-dx)/(k+1)
    if v0<0 or v1<0:raise ValueError('SOURCE_OFFSET_NEGATIVE_WEIGHT')
    return v0,v1

def _upper_offsets(source,t,band,indices):
    """Integrate positive b-q directly; never subtract b*N-Q to obtain E."""
    bg=source.provider.background;table=source.provider.tables['emissivity']
    lr=_v1.log_ray(bg,float(t));z=bg.z_i+(1.+bg.z_i)*math.expm1(lr)
    profile=table._z_profile(z);mod=sys.modules[type(table).__module__]
    factor=(1.+bg.z_i)**3/(mod.MPC_CM**3*mod.H_ERG_S)
    bounds=source.original._band(band);out=np.zeros((len(source.mu),len(source.edges)-1))
    for j in indices:
        a,b=source.edges[j:j+2];L=source.cell_width[j]
        lower=max(0.,_v1._log_ratio(bounds[0],a)-lr)
        upper=min(L,_v1._log_ratio(bounds[1],a)-lr)
        if upper<=lower:continue
        knots=source.native_logs[j]-lr
        begin=max(0,int(np.searchsorted(knots,lower,side='right'))-1)
        end=min(len(knots)-1,int(np.searchsorted(knots,upper,side='left')))
        terms=[]
        for i in range(begin,end):
            xl=max(lower,knots[i]);xr=min(upper,knots[i+1]);dx=xr-xl
            if dx<=0:continue
            width=_v1._log_ratio(source.native[i+1],source.native[i])
            f0=profile[i]+(profile[i+1]-profile[i])*((xl-knots[i])/width)
            f1=profile[i]+(profile[i+1]-profile[i])*((xr-knots[i])/width)
            if f0<0 or f1<0:raise ValueError('SOURCE_OFFSET_NEGATIVE_PROFILE')
            v0,v1=_negative_exponential_offsets(dx)
            # In reversed coordinate y, f=f1*(1-y)+f0*y and
            # b-q=b*[1-exp(xr-L)*exp(-dx*y)]. Every term is >=0.
            delta=xr-L
            if delta>0:raise ValueError('SOURCE_OFFSET_UPPER_SUPPORT')
            terms.append(dx*b*((-math.expm1(delta))*(f0+f1)*.5+
                math.exp(delta)*(f1*v0+f0*v1)))
        for k,w in enumerate(source.weights):out[k,j]=w*factor*math.fsum(terms)
    if not np.isfinite(out).all() or np.any(out<0):raise ValueError('SOURCE_OFFSET_UPPER_DOMAIN')
    return out

class StableCellSource(_v1.StableCellSource):
    def source(self,t,band=None):
        value=super().source(t,band)
        n,d,r=value['N'],value['D_eV'],value['R'];raw_q=value['Q_eV']
        a,b=self.edges[:-1][None,:],self.edges[1:][None,:]
        upper=d>.5*(b-a)*n
        upper_offset=_upper_offsets(self,t,band,np.flatnonzero(np.any(upper,axis=0)))
        q=a*n+d
        upper_q=b*n-upper_offset
        q[upper]=upper_q[upper]
        discrepancy=_v1._relative(raw_q,q)
        if discrepancy>PAIR_RTOL:
            raise SourceEntryError('SOURCE_OFFSET_ASSEMBLY_IDENTITY_REJECTED',{'relative':discrepancy,'rtol':PAIR_RTOL})
        if (not np.isfinite(q).all() or np.any(q<self.edges[:-1][None,:]*n)
                or np.any(q>self.edges[1:][None,:]*n)):
            raise ValueError('SOURCE_OFFSET_EXACT_MOMENT_CONE_REJECTED')
        value.update(Q_eV=q,U_eV=r[:,None]*q,
            moment_assembly=dict(formula='Q=a*N+D or b*N-E at nearest face; D=integral(q-a)s,E=integral(b-q)s'
                ,upper_face_cells=int(np.count_nonzero(upper)),
                raw_Q_relative_difference=discrepancy,rtol=PAIR_RTOL,
                source_N_unchanged=True,source_D_unchanged=True,source_R_unchanged=True,
                exact_cell_moment_cone=True,clipping=False,floor=False,
                state_representation_unchanged=True))
        return value

def integrate_source(cell_source,t0,t1,event_times=(),orders=(16,32),rtol=1e-10):
    source=cell_source if isinstance(cell_source,StableCellSource) else StableCellSource(cell_source)
    result=_v1.integrate_source(source,t0,t1,event_times=event_times,orders=orders,rtol=rtol)
    result['diagnostics']['source_moment_assembly']='C12_POSITIVE_TWO_FACE_OFFSET_ASSEMBLY'
    result['diagnostics']['source_assembly_pair_rtol']=PAIR_RTOL
    return result
