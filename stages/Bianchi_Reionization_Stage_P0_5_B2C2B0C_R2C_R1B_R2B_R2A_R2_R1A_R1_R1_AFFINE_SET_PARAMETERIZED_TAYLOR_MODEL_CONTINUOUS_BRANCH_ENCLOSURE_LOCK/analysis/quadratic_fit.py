"""Small total-degree-two endpoint fit used only by the coherent-field auditor."""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


def design(points: np.ndarray) -> np.ndarray:
    p=np.asarray(points,dtype=np.float64)
    if p.ndim!=2 or p.shape[1]!=2:
        raise ValueError('points must have shape (n,2)')
    a,b=p.T
    return np.column_stack([np.ones(len(p)),a,b,a*a,a*b,b*b])


@dataclass(frozen=True)
class QuadraticEndpointFit:
    coefficients: np.ndarray
    training_residual: float

    @classmethod
    def fit(cls,points,values):
        x=design(np.asarray(points,dtype=np.float64))
        y=np.asarray(values,dtype=np.float64)
        if y.shape[0] != len(x):
            raise ValueError('values leading dimension must match points')
        output_shape=y.shape[1:]
        flat=y.reshape(len(x),-1)
        coef_flat,*_=np.linalg.lstsq(x,flat,rcond=None)
        coef=coef_flat.reshape((x.shape[1],)+output_shape)
        pred=np.tensordot(x,coef,axes=(1,0))
        scale=np.maximum(np.max(np.abs(y),axis=0),1.0e-300)
        residual=float(np.max(np.abs(pred-y)/scale))
        return cls(np.ascontiguousarray(coef),residual)

    def evaluate(self,points):
        return np.tensordot(design(np.asarray(points,dtype=np.float64)),self.coefficients,axes=(1,0))

    def exact_box(self, residual_absolute=0.0):
        """Exact range of the fitted quadratic on ``[-1,1]^2``.

        A quadratic reaches an extremum at a corner, an edge stationary point,
        or the unique interior stationary point.  The implementation evaluates
        those candidates componentwise without materializing a parameter grid.
        """
        c0,c1,c2,c3,c4,c5=self.coefficients
        def value(a,b):
            return c0+c1*a+c2*b+c3*a*a+c4*a*b+c5*b*b
        corners=np.stack([value(a,b) for a in (-1.0,1.0) for b in (-1.0,1.0)],axis=0)
        lower=np.min(corners,axis=0);upper=np.max(corners,axis=0)
        tiny=np.finfo(float).tiny
        for a in (-1.0,1.0):
            valid=np.abs(c5)>tiny
            b=np.where(valid,-(c2+c4*a)/(2.0*c5),0.0)
            valid=valid & (b>=-1.0) & (b<=1.0)
            candidate=value(a,b)
            lower=np.where(valid,np.minimum(lower,candidate),lower)
            upper=np.where(valid,np.maximum(upper,candidate),upper)
        for b in (-1.0,1.0):
            valid=np.abs(c3)>tiny
            a=np.where(valid,-(c1+c4*b)/(2.0*c3),0.0)
            valid=valid & (a>=-1.0) & (a<=1.0)
            candidate=value(a,b)
            lower=np.where(valid,np.minimum(lower,candidate),lower)
            upper=np.where(valid,np.maximum(upper,candidate),upper)
        determinant=4.0*c3*c5-c4*c4
        valid=np.abs(determinant)>tiny
        a=np.where(valid,(c4*c2-2.0*c5*c1)/determinant,0.0)
        b=np.where(valid,(c4*c1-2.0*c3*c2)/determinant,0.0)
        valid=valid & (a>=-1.0) & (a<=1.0) & (b>=-1.0) & (b<=1.0)
        candidate=value(a,b)
        lower=np.where(valid,np.minimum(lower,candidate),lower)
        upper=np.where(valid,np.maximum(upper,candidate),upper)
        pad=np.asarray(residual_absolute,dtype=np.float64)
        scale=np.maximum(np.maximum(np.abs(lower),np.abs(upper)),np.nextafter(0.0,1.0))
        rounding=64.0*np.finfo(float).eps*scale
        return np.nextafter(lower-pad-rounding,-np.inf),np.nextafter(upper+pad+rounding,np.inf)

    def empirical_box(self,*,grid_size:int=65,residual_absolute=0.0):
        # Retained for small audit objects; production-size arrays use exact_box.
        q=np.linspace(-1.0,1.0,int(grid_size))
        lower=None;upper=None
        for start in range(0,len(q)*len(q),64):
            pairs=np.asarray([(a,b) for a in q for b in q][start:start+64])
            vals=self.evaluate(pairs)
            item_lo=np.min(vals,axis=0);item_hi=np.max(vals,axis=0)
            lower=item_lo if lower is None else np.minimum(lower,item_lo)
            upper=item_hi if upper is None else np.maximum(upper,item_hi)
        pad=float(residual_absolute)
        return lower-pad,upper+pad

__all__=['QuadraticEndpointFit','design']
