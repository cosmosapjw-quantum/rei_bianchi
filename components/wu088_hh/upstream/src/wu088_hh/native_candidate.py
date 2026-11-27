"""Guarded foreign-component ABI for benchmarks; not a promoted production provider."""
from __future__ import annotations
import ctypes as ct
from pathlib import Path
import numpy as np

class ForeignKernel:
    def __init__(self,path:Path):
        self.lib=ct.CDLL(str(path));self.path=Path(path)
        self.lib.precision_bits.restype=ct.c_int
        if self.lib.precision_bits()!=np.finfo(np.longdouble).nmant+1:
            raise RuntimeError('native and NumPy long-double formats disagree')
        self.fn=self.lib.mh_wide_foreign;self.fn.argtypes=[ct.c_size_t,ct.c_size_t]+[ct.c_void_p]*7;self.fn.restype=ct.c_int
        if hasattr(self.lib,'hh_set_num_threads'):
            self.lib.hh_set_num_threads.argtypes=[ct.c_int];self.lib.hh_set_num_threads.restype=ct.c_int
            self.lib.hh_last_team_size.restype=ct.c_int
    def set_threads(self,n:int):
        if hasattr(self.lib,'hh_set_num_threads'):
            if self.lib.hh_set_num_threads(n):raise ValueError('invalid native thread count')
        elif n!=1:raise ValueError('reference is serial')
    @property
    def observed_threads(self):
        return self.lib.hh_last_team_size() if hasattr(self.lib,'hh_last_team_size') else 1
    def __call__(self,t,gs,gw,W,pars):
        arrays=[np.ascontiguousarray(a,dtype=np.float64) for a in (t,gs,gw,W,pars)]
        t,gs,gw,W,pars=arrays;n=t.size
        if t.ndim!=1 or not 1<=n<=512 or gs.ndim!=1 or not 1<=gs.size<=192 or gw.shape!=gs.shape or W.shape!=(9,n,n) or pars.shape!=(4,):raise ValueError('invalid ABI shape')
        if not all(np.isfinite(a).all() for a in arrays) or np.any(t<=0) or np.any(gs<0) or np.any(pars[:2]<=0):raise ValueError('invalid/nonfinite ABI input')
        if abs(pars[2])>64:raise ValueError('outside frozen geometric domain')
        out=np.empty((2,2,3),np.clongdouble);sa=np.empty((2,2,3),np.longdouble)
        status=self.fn(n,gs.size,*[a.ctypes.data for a in arrays],out.ctypes.data,sa.ctypes.data)
        if status:raise RuntimeError(f'native status {status}')
        if not np.isfinite(out).all() or not np.isfinite(sa).all():raise FloatingPointError('nonfinite native result')
        return out,sa
