"""Prepared, beta-free 21-state atomic kinetics at prescribed T and spectrum."""
from __future__ import annotations
import importlib.util
from pathlib import Path
import numpy as np
from scipy.linalg import expm, solve

ROOT=Path(__file__).resolve().parents[1]
_spec=importlib.util.spec_from_file_location('sandbox_atomic_donor',ROOT/'vendor/donor_atomic/code/atomic_network.py')
_donor=importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_donor)

class DomainError(ValueError):pass

class PreparedAtomic:
    """Retain 21 absolute abundances; share only identical electronic blocks.

    Temperatures/spectra are frozen per object. Decay D is deliberately unused.
    solve() initially defaults to dense; the diagnostic measures the valid default;
    solve_structured() remains the exact shared-block/rank-one alternative.
    """
    def __init__(self,T_K,uv=1.,cutoff_eV=200.):
        self.T_K=float(T_K);self.uv=float(uv);self.cutoff_eV=float(cutoff_eV)
        self.network=_donor.AtomicNetwork(uv_cutoff_eV=cutoff_eV)
        rates=self.network.rates(T_K,uv)
        self.P=np.array(rates['G0'],copy=True);self.R=np.array(rates['Gne'],copy=True)
        self.Grr=np.array(rates['Grr'],copy=True);self.Gdr=np.array(rates['Gdr'],copy=True)
        self.q=self.network.q;self.A=self.network.A;self.names=self.network.names
        self.groups=tuple(tuple(v) for v in self.network.isotope_groups.values())
        self.shared={size:[np.array(g,dtype=int) for g in self.groups if len(g)==size] for size in (2,3,4)}
        self.blocks={size:(self.P[np.ix_(groups[0],groups[0])],self.R[np.ix_(groups[0],groups[0])]) for size,groups in self.shared.items()}
        self.default_solver='dense';self.fallbacks=[]
        for size,groups in self.shared.items():
            p,r=self.blocks[size]
            for indices in groups:
                if not np.array_equal(p,self.P[np.ix_(indices,indices)]) or not np.array_equal(r,self.R[np.ix_(indices,indices)]):
                    raise ValueError('ELECTRONIC_BLOCKS_NOT_IDENTICAL')
    def _physical(self,Y,nb,fast_e=0.):
        y=np.asarray(Y,dtype=float)
        if y.shape!=(21,) or not np.all(np.isfinite(y)) or np.any(y<0):raise DomainError('INVALID_PHYSICAL_Y')
        if not np.isfinite(nb) or nb<0 or not np.isfinite(fast_e) or fast_e<0 or fast_e>float(self.q@y):raise DomainError('INVALID_DENSITY_OR_FAST_ELECTRONS')
        return y,float(nb),float(fast_e)
    def smooth_rhs(self,Y,nb,fast_e=0.):
        """Polynomial extension, for complex-step reference only."""
        y=np.asarray(Y);e=nb*(self.q@y-fast_e)
        return self.P@y+e*(self.R@y)
    def rhs(self,Y,nb,fast_e=0.):
        y,nb,f=self._physical(Y,nb,fast_e)
        return self.smooth_rhs(y,nb,f)
    def matrices(self,Y,nb,fast_e=0.):
        y,nb,f=self._physical(Y,nb,fast_e)
        e=nb*(self.q@y-f);B=self.P+e*self.R;u=nb*(self.R@y)
        return B,u,B+np.outer(u,self.q)
    def jacobian(self,Y,nb,fast_e=0.):return self.matrices(Y,nb,fast_e)[2]
    def fast_electron_column(self,Y,nb,fast_e=0.):return -self.matrices(Y,nb,fast_e)[1]
    def batch_rhs(self,Y,nb,fast_e=0.):
        y=np.asarray(Y,dtype=float)
        if y.ndim!=2 or y.shape[1]!=21 or y.shape[0]>256 or not np.all(np.isfinite(y)) or np.any(y<0):raise DomainError('INVALID_BATCH')
        density=np.broadcast_to(np.asarray(nb,dtype=float),(len(y),))
        f=np.broadcast_to(np.asarray(fast_e,dtype=float),(len(y),))
        electrons=y@self.q
        if np.any(~np.isfinite(density)) or np.any(density<0) or np.any(~np.isfinite(f)) or np.any(f<0) or np.any(f>electrons):raise DomainError('INVALID_BATCH_DENSITY_OR_FAST_ELECTRONS')
        return y@self.P.T+(density*(electrons-f))[:,None]*(y@self.R.T)
    @staticmethod
    def _thomas(matrix,rhs):
        n=len(matrix);diag=np.diag(matrix).copy();upper=np.diag(matrix,1);lower=np.diag(matrix,-1)
        b=np.array(rhs,copy=True)
        for i in range(n):
            scale=max(np.sum(np.abs(matrix[i])),1e-300)
            if not np.isfinite(diag[i]) or diag[i]<=1e-14*scale:raise ArithmeticError('UNSAFE_TRIDIAGONAL_PIVOT')
            if i+1<n:
                multiplier=lower[i]/diag[i]
                diag[i+1]-=multiplier*upper[i]
                b[i+1]-=multiplier*b[i]
        out=np.empty_like(b);out[-1]=b[-1]/diag[-1]
        for i in range(n-2,-1,-1):out[i]=(b[i]-upper[i]*out[i+1])/diag[i]
        return out,float(np.min(diag))
    def solve_dense(self,Y,nb,h,rhs,fast_e=0.):
        if not np.isfinite(h) or h<0:raise DomainError('INVALID_STEP')
        B,u,J=self.matrices(Y,nb,fast_e)
        return solve(np.eye(21)-h*J,np.asarray(rhs,dtype=float),check_finite=True)
    def solve_structured(self,Y,nb,h,rhs,fast_e=0.,return_info=False):
        if not np.isfinite(h) or h<0:raise DomainError('INVALID_STEP')
        y,nb,f=self._physical(Y,nb,fast_e);b=np.asarray(rhs,dtype=float)
        if b.shape!=(21,) or not np.all(np.isfinite(b)):raise DomainError('INVALID_LINEAR_RHS')
        e=nb*(self.q@y-f);u=nb*(self.R@y);z=b.copy();w=u.copy();pivots=[]
        try:
            for size,groups in self.shared.items():
                p,r=self.blocks[size];M=np.eye(size)-h*(p+e*r)
                columns=np.column_stack([b[g] for g in groups]+[u[g] for g in groups])
                solved,pivot=self._thomas(M,columns);pivots.append(pivot)
                for column,g in enumerate(groups):z[g]=solved[:,column];w[g]=solved[:,len(groups)+column]
            hqw=h*float(self.q@w);denom=1-hqw;denom_scale=1+abs(hqw)
            if not np.isfinite(denom) or abs(denom)<=1e-12*denom_scale:raise ArithmeticError('UNSAFE_RANK_ONE_DENOMINATOR')
            answer=z+h*w*(float(self.q@z)/denom)
            if not np.all(np.isfinite(answer)):raise ArithmeticError('NONFINITE_STRUCTURED_SOLUTION')
            B=self.P+e*self.R;A=np.eye(21)-h*(B+np.outer(u,self.q))
            residual=float(np.linalg.norm(A@answer-b,np.inf))/max(float(np.linalg.norm(A,np.inf))*float(np.linalg.norm(answer,np.inf))+float(np.linalg.norm(b,np.inf)),1e-300)
            if not np.isfinite(residual) or residual>1e-12:raise ArithmeticError('UNSAFE_STRUCTURED_BACKWARD_RESIDUAL')
            info={'method':'shared_tridiagonal_rank_one','denominator':denom,'denominator_term_scale':denom_scale,
                  'denominator_relative_magnitude':abs(denom)/denom_scale,'min_pivot':min(pivots),'backward_residual':residual,'fallback':False}
        except ArithmeticError as error:
            answer=self.solve_dense(y,nb,h,b,f)
            info={'method':'dense_fallback','fallback':True,'reason':str(error)}
            self.fallbacks.append(dict(info))
        return (answer,info) if return_info else answer
    def solve(self,Y,nb,h,rhs,fast_e=0.,method=None):
        method=method or self.default_solver
        if method=='dense':return self.solve_dense(Y,nb,h,rhs,fast_e)
        if method=='structured':return self.solve_structured(Y,nb,h,rhs,fast_e)
        raise ValueError('UNKNOWN_LINEAR_SOLVE_METHOD')
    def _frozen_exponential(self,Y,nb,h,electrons_Y):
        out=np.array(Y,copy=True);e=nb*float(self.q@electrons_Y)
        for size,groups in self.shared.items():
            p,r=self.blocks[size];transition=expm(h*(p+e*r))
            block_out=transition@np.column_stack([Y[g] for g in groups])
            for column,g in enumerate(groups):out[g]=block_out[:,column]
        return out
    def step_midpoint(self,Y,nb,h):
        y,nb,_=self._physical(Y,nb,0.)
        if not np.isfinite(h) or h<0:raise DomainError('INVALID_STEP')
        half=self._frozen_exponential(y,nb,h/2,y)
        final=self._frozen_exponential(y,nb,h,half)
        for g in self.groups:
            total=float(np.sum(y[list(g)]))
            if np.any(final[list(g)] < -1e-14*total):raise ArithmeticError('MATERIAL_NEGATIVE_ATOMIC_STEP')
        return final
