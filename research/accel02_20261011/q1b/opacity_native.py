"""Q1B local actual native SIGMA binding; no gas RHS or history integrator.

No duplicated cross-section formula, no shifted energy, no endpoint trace
guess. Native sigma is returned by the hash-pinned N1 binary. Fixed-time
interior opacity Jacobians inherit the reconstruction's explicit limitations.
"""
from pathlib import Path
import hashlib
import sys
import numpy as np
from reconstruction import opacity_moments,TraceRequired

HERE=Path(__file__).resolve().parent
N1=HERE.parent/'n1'
DEFAULT_BINARY=N1/'native/target/release/rei_n1_native'
EXPECTED_BINARY_SHA256='3e3a3ef4d89019d791f4e2f4cf25108ac2c6d5e365c58a928d9ff8a85234a0ac'
C_CM_S=2.99792458e10
EV_ERG=1.602176634e-12
THRESHOLDS_EV=np.array([13.60,24.59,54.42])
CHEMICAL_CHI_EV=np.array([13.598434599702,24.587389011,54.41776])
sys.path.insert(0,str(N1))
from provider import Native


class NativeOpacity:
    def __init__(self,binary=DEFAULT_BINARY):
        self.binary=Path(binary).resolve()
        self.binary_sha256=hashlib.sha256(self.binary.read_bytes()).hexdigest()
        if self.binary_sha256!=EXPECTED_BINARY_SHA256:
            raise ValueError('Q1B_NATIVE_SIGMA_BINARY_IDENTITY')
        self.native=Native(self.binary)
        self.native_calls=0
        self.energy_evaluations=0
        self.closed=False

    def __enter__(self):return self

    def __exit__(self,*args):self.close()

    def close(self):
        if not self.closed:
            self.native.close()
            self.native.proc.stdout.close()
            self.native.proc.stderr.close()
            self.closed=True

    def sigma(self,energy):
        energy=np.asarray(energy,dtype=float)
        if energy.ndim!=1 or not energy.size or not np.all(np.isfinite(energy)) or np.any(energy<=0) or np.any(energy>50000.):
            raise ValueError('Q1B_NATIVE_SIGMA_ENERGY_DOMAIN_NO_SHIFT')
        out=self.native.call('SIGMA',energy)
        self.native_calls+=1
        self.energy_evaluations+=len(energy)
        if len(out)!=3*len(energy):raise ValueError('Q1B_NATIVE_SIGMA_SCHEMA')
        out=out.reshape(-1,3)
        if not np.all(np.isfinite(out)) or np.any(out<0):
            raise ValueError('Q1B_NATIVE_SIGMA_NONNEGATIVE_FINITE_DOMAIN')
        return out

    def moments(self,cell,*,orders=(64,128),rtol=1e-7):
        if cell.status not in ('INTERIOR','EMPTY','ZERO_WIDTH_EMPTY'):
            raise TraceRequired('NATIVE_ENDPOINT_TRACE_NOT_IMPLEMENTED_NO_ENERGY_SHIFT')
        if cell.status=='INTERIOR' and cell.R*cell.b>50000.:
            raise ValueError('Q1B_NATIVE_OCCUPIED_SUPPORT_ABOVE_PINNED_DOMAIN')
        splits=[float(E/cell.R) for E in THRESHOLDS_EV if cell.a<E/cell.R<cell.b]
        cache={}
        def all_kernels(q):
            energy=cell.R*q
            key=energy.tobytes()
            if key not in cache:cache[key]=C_CM_S*self.sigma(energy)
            return cache[key]
        results=[]
        before=self.native_calls
        for species in range(3):
            out=opacity_moments(cell,lambda q:all_kernels(q)[:,species],split_points=splits,
                orders=orders,rtol=rtol,require_jacobian=(cell.status=='INTERIOR'))
            results.append(out)
        K0=np.array([o['K0'] for o in results])
        KE=np.array([o['KE'] for o in results])
        chemical=CHEMICAL_CHI_EV*K0
        heat=KE-chemical
        if np.any(~np.isfinite(heat)) or np.any(heat<0):
            raise ArithmeticError('Q1B_NATIVE_PAIRED_HEAT_NEGATIVE_OR_NONFINITE_NO_CLIP')
        return {'native_binding':'ACTUAL_PINNED_SIGMA','binary_sha256':self.binary_sha256,
            'K0':K0.tolist(),'KE':KE.tolist(),'K1':(KE/cell.R).tolist(),
            'chemical_eV':chemical.tolist(),'heat_eV':heat.tolist(),
            'jacobian_N_U':[o['jacobian_N_U'] for o in results],
            'jacobian_status':cell.jacobian_status,'threshold_splits_q':splits,
            'species_diagnostics':results,'actual_native_calls':self.native_calls-before,
            'claim':'LOCAL_ACTUAL_OPACITY_ONLY_NOT_COUPLED_ODE_ADMISSION'}
