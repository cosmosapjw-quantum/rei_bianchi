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
        coef,*_=np.linalg.lstsq(x,y,rcond=None)
        pred=np.tensordot(x,coef,axes=(1,0))
        scale=np.maximum(np.max(np.abs(y),axis=0),1.0e-300)
        residual=float(np.max(np.abs(pred-y)/scale))
        return cls(np.ascontiguousarray(coef),residual)

    def evaluate(self,points):
        return np.tensordot(design(np.asarray(points,dtype=np.float64)),self.coefficients,axes=(1,0))

    def empirical_box(self,*,grid_size:int=65,residual_absolute=0.0):
        q=np.linspace(-1.0,1.0,int(grid_size))
        aa,bb=np.meshgrid(q,q,indexing='ij')
        vals=self.evaluate(np.column_stack([aa.ravel(),bb.ravel()]))
        pad=float(residual_absolute)
        return np.min(vals,axis=0)-pad,np.max(vals,axis=0)+pad

__all__=['QuadraticEndpointFit','design']
