"""Current-stage C02 caller; no time step, opacity cache across stages or policy changes."""
from pathlib import Path
import hashlib
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
Q1B = ROOT/'research/accel02_20261011/q1b'
sys.path.insert(0, str(Q1B))
from reconstruction import reconstruct
from opacity_native import NativeOpacity
from source_cells import table_cell_moments
from provider import Native

EV = 1.602176634e-12
CHI = np.array([13.598434599702,24.587389011,54.41776])
CELL_BINARY = Q1B/'native/target/release/rei_q1b_cell_native_v1'
CELL_SHA = 'e29245acfee5be4d43c27935e2abd212d578685efa70dffbeffa8f96dd3e4b6f'


class Caller:
    def __init__(self):
        if hashlib.sha256(CELL_BINARY.read_bytes()).hexdigest() != CELL_SHA:
            raise ValueError('HOLD_CELL_BINARY_IDENTITY')
        self.opacity = NativeOpacity()
        self.counts = {'native_processes': 1, 'SIGMA': 0, 'SIGMA_energies': 0, 'CELL_RHS_V1': 0}
        sigma = self.opacity.sigma
        def bounded_sigma(energy):
            if self.counts['SIGMA'] >= 1024 or self.counts['SIGMA_energies']+len(energy)>131072:
                raise RuntimeError('HOLD_CALL_CAP')
            self.counts['SIGMA'] += 1
            self.counts['SIGMA_energies'] += len(energy)
            return sigma(energy)
        self.opacity.sigma = bounded_sigma
        self.bridge = Native(CELL_BINARY)
        self.counts['native_processes'] += 1

    def close(self):
        for native in (self.opacity.native, self.bridge):
            if native.proc.poll() is None:
                native.close()
            native.proc.stdout.close()
            native.proc.stderr.close()

    def submit(self, t, g, gas, cells):
        cells = np.asarray(cells, float).reshape(-1,13)
        if self.counts['CELL_RHS_V1'] >= 96:
            raise RuntimeError('HOLD_CALL_CAP')
        self.counts['CELL_RHS_V1'] += 1
        values = np.r_[t,g['a_rel'],g['b'],g['H'],g['s'],g['nH'],g['nHe'],gas,g['Tcmb_K'],len(cells),cells.ravel()]
        result = self.bridge.call('CELL_RHS_V1', values)
        if len(result) != 15+2*len(cells):
            raise ValueError('HOLD_CELL_OUTPUT_SCHEMA')
        return result

    def assemble(self, t, g, gas, edges, mu, R, N, U, tables, weights):
        """Every request consumes one current N/U snapshot and one current geometry."""
        N,U = np.asarray(N,float),np.asarray(U,float)
        expected = (len(mu), len(edges)-1)
        if N.shape != expected or U.shape != expected:
            raise ValueError('HOLD_CURRENT_STATE_SHAPE')
        source = table_cell_moments(tables['emissivity'],g['z'],edges,R,weights)
        cells, moments, states = [], [], []
        # Intra-request identical (N,U,R,a,b) may share evaluation; never t-only reuse.
        cache = {}
        for j in range(len(mu)):
            for i,(a,b) in enumerate(zip(edges[:-1],edges[1:])):
                cap = max(float(a), min(float(b), 50000./R[j]))
                key = (float(N[j,i]),float(U[j,i]),float(R[j]),float(a),cap)
                rec = reconstruct(*key)
                if key not in cache:
                    cache[key] = self.opacity.moments(rec,orders=(64,128),rtol=1e-7)
                out = cache[key]
                lam = g['H']+g['s']*(3*mu[j]**2-1)
                cells.append([mu[j],R[j],lam,N[j,i],U[j,i],source['N'][j,i],source['U_eV'][j,i],*out['K0'],*out['KE']])
                moments.append(out)
                states.append(rec.status)
        cells = np.asarray(cells)
        return self.submit(t,g,gas,cells), cells, moments, states, source


def photon_jvp(jac, direction, g, dU, lam):
    """Chain rule only; gas held fixed. Diagnostic residual fields excluded."""
    jac = np.asarray(jac)
    dK = np.einsum('aij,j->ai',jac,direction)
    scaleK = np.einsum('aij,j->ai',abs(jac),abs(direction))
    nh,ne = g['nH'],g['nHe']; x,y,z = g['fractions']
    lower = np.array([nh*(1-x),ne*(1-y-z),ne*y]); V = g['a_rel']**3
    def transform(k):
        events = lower*k[:,0]/V
        out = np.zeros(17)
        out[:3] = [events[0]/nh,(events[1]-events[2])/ne,events[2]/ne]
        out[3] = np.dot(lower,k[:,1]-CHI*k[:,0])/(V*nh)
        out[7] = np.dot(lower,k[:,0]);out[8:11] = k[:,0]/V
        out[15] = -out[7];out[16] = -np.dot(lower,k[:,1])
        return out
    out = transform(dK)
    # Apply abs of the linear operator to termwise opacity scales.
    scales = np.zeros(17)
    for a in range(3):
        for k in range(2):
            basis = np.zeros((3,2));basis[a,k] = scaleK[a,k]
            scales += abs(transform(basis))
    out[5] = EV*lam*dU;out[16] -= lam*dU
    scales[5] += abs(EV*lam*dU);scales[16] += abs(lam*dU)
    return out,scales,dK,scaleK
