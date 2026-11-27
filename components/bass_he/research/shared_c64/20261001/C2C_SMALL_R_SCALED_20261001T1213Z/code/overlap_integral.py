"""Frozen-state, common-O L2 overlap with geometry-resolved axis cusps.

Coordinate and phase conventions match C2 math/continuation.py.  No solve,
interpolation of states, derivative observable, or coefficient dot is used.
"""
from __future__ import annotations
from functools import lru_cache
import math
import numpy as np
from numpy.polynomial.legendre import leggauss
from scipy.interpolate import BSpline


def charge_center_positions(R, ZA, ZB):
    if not all(np.isfinite(x) for x in (R, ZA, ZB)) or R <= 0 or min(ZA,ZB) < 0 or ZA+ZB <= 0:
        raise ValueError('finite positive separation and nonnegative charges required')
    za, zb = -ZB*R/(ZA+ZB), ZA*R/(ZA+ZB)
    return za, zb, (za+zb)/2


def common_o_to_prolate(rho, z, state):
    za, zb, _ = charge_center_positions(state.R, state.ZA, state.ZB)
    ra, rb = np.hypot(rho,z-za), np.hypot(rho,z-zb)
    return np.maximum(1.0,(ra+rb)/state.R), np.clip((ra-rb)/state.R,-1.0,1.0)


class Values:
    """Vectorized scalar B-splines, exact zero extension of finite support."""
    def __init__(self,state):
        self.state=state
        if state.m not in (0,1):
            raise ValueError('only registered m=0 or bright m=1 supported')
        self.splines=[]
        for axis,coef in ((state._radial,state.radial_coefficients),(state._angular,state.angular_coefficients)):
            coef=np.asarray(coef)
            if coef.ndim != 1 or np.iscomplexobj(coef) or not np.all(np.isfinite(coef)):
                raise ValueError('finite real coefficient vectors required')
            basis=axis.basis
            self.splines.append(BSpline(np.array(basis.t,copy=True),np.array(basis.c@coef,copy=True),basis.k,extrapolate=False))
    def __call__(self,xi,eta):
        xi,eta=np.broadcast_arrays(np.asarray(xi,float),np.asarray(eta,float))
        if not np.all(np.isfinite(xi)) or not np.all(np.isfinite(eta)):
            raise ValueError('finite coordinates required')
        out=np.zeros(xi.shape)
        inside=(xi>=1)&(xi<=self.state.xi_max)&(np.abs(eta)<=1)
        x,y=xi[inside],eta[inside]
        # For source tensor patches repeated scalar coordinates are evaluated
        # only once; target coordinates are genuinely two dimensional.
        xx,ix=np.unique(x,return_inverse=True);yy,iy=np.unique(y,return_inverse=True)
        factor=np.sqrt(np.maximum(0.,(x*x-1)*(1-y*y))) if self.state.m else 1.
        out[inside]=self.state.normalization*factor*self.splines[0](xx)[ix]*self.splines[1](yy)[iy]
        if not np.all(np.isfinite(out)):
            raise FloatingPointError('nonfinite state value')
        return out


def _compatible(left,right):
    if (left.ZA,left.ZB,left.m)!=(right.ZA,right.ZB,right.m):
        raise ValueError('same charges and azimuthal sector required')
    for s in (left,right):
        charge_center_positions(s.R,s.ZA,s.ZB)
        if s.m not in (0,1) or isinstance(s.m,bool) or not np.isfinite(s.normalization) or s.normalization<=0:
            raise ValueError('registered m and positive finite normalization required')
        if not np.isfinite(s.xi_max) or s.xi_max<=1:
            raise ValueError('finite radial support required')
        for edges in (s._radial.edges,s._angular.edges):
            if not np.all(np.isfinite(edges)) or np.any(np.diff(edges)<=0):
                raise ValueError('finite strictly increasing edges required')
        if s._radial.edges[0]!=1 or s._angular.edges[0]!=-1 or s._angular.edges[-1]!=1:
            raise ValueError('standard prolate boundaries required')


def _insert(edges,value):
    """Insert an analytic landmark, snapping only within roundoff of a knot."""
    tolerance=64*np.finfo(float).eps*max(1.,abs(value),float(np.max(np.abs(edges))))
    j=int(np.argmin(np.abs(edges-value)))
    if abs(edges[j]-value)<=tolerance:
        return edges,float(edges[j])
    return np.sort(np.r_[edges,value]),float(value)


def geometry(source,target):
    """Tensor spline edges plus target nuclear axis points in (s,theta)."""
    se=np.sqrt(np.maximum(0.,np.asarray(source._radial.edges)**2-1))
    te=np.arccos(np.asarray(source._angular.edges)[::-1])
    _,_,mid=charge_center_positions(source.R,source.ZA,source.ZB)
    cusps=[]
    for z in charge_center_positions(target.R,target.ZA,target.ZB)[:2]:
        v=2*(z-mid)/source.R
        if abs(abs(v)-1)<=64*np.finfo(float).eps:
            v=math.copysign(1.,v)
        xi=max(1.,abs(v));eta=min(1.,max(-1.,v))
        if xi>source.xi_max:
            continue
        s=math.sqrt(xi*xi-1);theta=math.acos(eta)
        se,s=_insert(se,s);te,theta=_insert(te,theta)
        cusps.append((s,theta,xi))
    # If two distinct cusps would share an edge of one rectangle, split that
    # edge once so every corner transform has one singular point.
    for j,a in enumerate(cusps):
        for b in cusps[j+1:]:
            if a[0]==b[0] and a[1]!=b[1]:
                middle=(a[1]+b[1])/2
                if not np.any((te>min(a[1],b[1]))&(te<max(a[1],b[1]))):te,_=_insert(te,middle)
            if a[1]==b[1] and a[0]!=b[0]:
                middle=(a[0]+b[0])/2
                if not np.any((se>min(a[0],b[0]))&(se<max(a[0],b[0]))):se,_=_insert(se,middle)
    rectangles=[]
    def add(sl,sh,tl,th,depth=0):
        corner=[p for p in cusps if p[0] in (sl,sh) and p[1] in (tl,th)]
        if len(corner)>1:raise ValueError('multiple cusp corner cell')
        if corner:
            p=corner[0]
            # Outside a source focus: physical metric coefficients share
            # c*s_star, leaving ds/xi_star versus dtheta.  Inside: equal.
            hs=(sh-sl)/p[2] if p[0]>0 else sh-sl
            ht=th-tl
            if max(hs,ht)>2*min(hs,ht):
                if depth>=32:raise ValueError('geometry-only bisection cap')
                if hs>ht:
                    sm=(sl+sh)/2;add(sl,sm,tl,th,depth+1);add(sm,sh,tl,th,depth+1)
                else:
                    tm=(tl+th)/2;add(sl,sh,tl,tm,depth+1);add(sl,sh,tm,th,depth+1)
                return
        if len(rectangles)>=50000:raise ValueError('geometry-only partition cell cap')
        rectangles.append((sl,sh,tl,th,corner[0] if corner else None))
    for sl,sh in zip(se[:-1],se[1:]):
        for tl,th in zip(te[:-1],te[1:]):add(float(sl),float(sh),float(tl),float(th))
    return rectangles,{'target_nuclei_stheta':cusps,'base_s_cells':len(se)-1,'base_theta_cells':len(te)-1,
                       'rectangles':len(rectangles),'duffy_rectangles':sum(p[-1] is not None for p in rectangles),
                       'metric_aspect_cap':2.,'max_geometry_bisection_depth':32,'max_geometry_cells':50000}


@lru_cache(maxsize=8)
def _gauss(order):
    if isinstance(order,bool) or not isinstance(order,int) or order<2:
        raise ValueError('integer order >=2 required')
    q,w=leggauss(order);t=(q+1)/2;w=w/2
    T,U=np.meshgrid(t,t,indexing='ij');W=w[:,None]*w[None,:]
    return T,U,W


def patches(source,target,order):
    rectangles,meta=geometry(source,target)
    T,U,W=_gauss(order)
    for sl,sh,tl,th,corner in rectangles:
        hs,ht=sh-sl,th-tl
        if corner is None:
            yield sl+hs*T,tl+ht*U,hs*ht*W
        else:
            cs,ct,_=corner
            ss=1 if cs==sl else -1;st=1 if ct==tl else -1
            yield cs+ss*hs*T,ct+st*ht*T*U,hs*ht*T*W
            yield cs+ss*hs*T*U,ct+st*ht*T,hs*ht*T*W


def directed_overlap(source,target,order,backend='native',batch_patches=32):
    """Integrate on source support and evaluate target at the same O point."""
    if backend not in ('native','python'):
        raise ValueError('explicit native or python backend required')
    if isinstance(batch_patches,bool) or not isinstance(batch_patches,int) or batch_patches<1:
        raise ValueError('positive integer batch_patches required')
    if backend=='native':
        from integration_native import sum_products
    source_values,target_values=Values(source),Values(target)
    _,_,mid=charge_center_positions(source.R,source.ZA,source.ZB)
    totals=[];weights=[];a=[];b=[];counts=[];point_count=0;patch_count=0
    def flush():
        if not counts:return
        if backend=='native':
            totals.append(float(sum_products(np.concatenate(weights),np.concatenate(a),np.concatenate(b),np.asarray(counts,dtype=np.int32))))
        else:
            totals.append(math.fsum(float(np.sum(w*x*y,dtype=np.float64)) for w,x,y in zip(weights,a,b)))
        weights.clear();a.clear();b.clear();counts.clear()
    for s,t,w in patches(source,target,order):
        xi=np.sqrt(1+s*s);eta=np.cos(t)
        sint=np.sin(t);rho=source.R/2*s*sint;z=source.R/2*xi*eta+mid
        tx,ty=common_o_to_prolate(rho,z,target)
        jac=source.R**3/8*(s*s+sint*sint)*(s/xi)*sint
        weights.append(np.ascontiguousarray((w*jac).ravel()))
        a.append(np.ascontiguousarray(source_values(xi,eta).ravel()))
        b.append(np.ascontiguousarray(target_values(tx,ty).ravel()))
        counts.append(s.size);point_count+=s.size;patch_count+=1
        if len(counts)==batch_patches:flush()
    flush()
    result=math.fsum(totals)
    if not np.isfinite(result):raise FloatingPointError('nonfinite overlap')
    meta=geometry(source,target)[1]
    meta.update({'quadrature_points':point_count,'patches':patch_count,'batch_patches':batch_patches})
    return result,meta


def pair_overlap(left,right,order,backend='native'):
    _compatible(left,right)
    lr,lmeta=directed_overlap(left,right,order,backend)
    rl,rmeta=directed_overlap(right,left,order,backend)
    nl,_=directed_overlap(left,left,order,backend)
    nr,_=directed_overlap(right,right,order,backend)
    if min(nl,nr)<=0:raise FloatingPointError('nonpositive self norm')
    mean=(lr+rl)/2;norm=math.sqrt(nl*nr)
    return {'R_left':float(left.R),'R_right':float(right.R),'m':int(left.m),'order':order,'backend':backend,
            'overlap':mean,'normalized_overlap':mean/norm,'left_domain_overlap':lr,'right_domain_overlap':rl,
            'directional_difference_abs':abs(lr-rl),'self_norm_left':nl,'self_norm_right':nr,
            'max_self_norm_error_abs':max(abs(nl-1),abs(nr-1)),
            'phase_factor_suggestion':1 if mean>=0 else -1,'geometry_left':lmeta,'geometry_right':rmeta,
            'measure':'rho d(rho) dz in common O; finite states extended by zero',
            'quadrature':'s=sqrt(xi^2-1), theta=acos(eta); target nuclear cuts; metric-balanced corner Duffy',
            'selection_scope':'lowest fixed-m finite-state branch; rank-five cluster NOT_VERIFIED'}


def refinement_audit(records,tolerance=1e-7,minimum_overlap=0.5):
    """Require two successive increments plus direction/selfnorm consistency."""
    if len(records)<3:raise ValueError('at least three ordered refinement records required')
    records=records[-3:]
    if not np.isfinite(tolerance) or tolerance<=0 or not 0<minimum_overlap<=1:
        raise ValueError('invalid audit tolerances')
    for low,high in zip(records,records[1:]):
        if any(low[k]!=high[k] for k in ('R_left','R_right','m')) or low['order']>=high['order']:
            raise ValueError('incompatible or unordered records')
    keys=('left_domain_overlap','right_domain_overlap','normalized_overlap')
    increments=[max(abs(high[k]-low[k]) for k in keys) for low,high in zip(records,records[1:])]
    # All three terminal records must satisfy auxiliary consistency, preventing
    # a single fortuitous final-order cancellation from closing the sequence.
    consistency=max(max(r['directional_difference_abs'],r['max_self_norm_error_abs']) for r in records)
    last=records[-1];mag=abs(last['normalized_overlap'])
    passed=max(increments)<=tolerance and consistency<=tolerance
    transport=passed and minimum_overlap<=mag<=1+tolerance
    return {'quadrature_increments_abs':increments,'max_consistency_error_abs':consistency,
            'quadrature_tolerance_abs':tolerance,'minimum_normalized_overlap':minimum_overlap,
            'quadrature_pass':bool(passed),'transport_pass':bool(transport),
            'phase_factor':last['phase_factor_suggestion'] if transport else None,
            'status':'PASS_FIXED_M_LOCAL_STEP' if transport else 'HOLD',
            'certificate':'empirical frozen-state quadrature and local transport only'}
