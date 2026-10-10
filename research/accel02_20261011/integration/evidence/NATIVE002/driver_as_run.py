"""New native coupled history. No reduced RUN002 execution or implicit admission."""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import traceback

import numpy as np
from scipy.integrate import BDF
from scipy.sparse import coo_matrix

HERE = Path(__file__).resolve().parent
EV = 1.602176634e-12
KB = 1.380649e-16
C = 29979245800.
CHI = np.array([13.598434599702, 24.587389011, 54.41776])


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class Coupled:
    def __init__(self, provider, native, characteristics, ne, nmu, coordinate='energy'):
        self.provider, self.native, self.char = provider, native, characteristics
        self.q, self.mu, self.weights = characteristics.make_grid(ne, nmu, provider.q_max_eV)
        self.n = len(self.q)
        self.end = provider.end_time_s
        self.g0 = provider.geometry(0.)
        if coordinate not in ('number', 'energy'):
            raise ValueError('PHOTON_COORDINATE')
        self.coordinate = coordinate
        initial = provider.initial_photons(self.q, self.weights)
        initial_state = initial*self.q if coordinate == 'energy' else initial
        self.initial_number = initial.sum()
        self.y0 = np.r_[provider.initial_gas, initial_state, np.zeros(6)]
        self.e0 = self.energy(0., self.y0)
        # Scaling is a numerical coordinate change, not added photons/energy.
        source = np.maximum.reduce([provider.source_reference(self.q, self.mu, self.weights,
                                    self.end*f) for f in (0., .25, .5, .75, 1.)])
        pscale = np.maximum.reduce([initial, source * self.end,
                                   np.full(self.n, self.g0['nH'] * 1e-20)])
        if coordinate == 'energy':
            pscale *= self.q
        self.scales = np.r_[np.ones(3), max(1., self.y0[3]), pscale,
                            np.full(3, self.e0), self.g0['nH'], self.g0['nH'], self.e0]
        self.calls = 0
        self.jcalls = 0
        self.max_local_number = self.max_local_energy = 0.
        self.cache_t = None
        self.started = time.monotonic()
        self.last_progress = self.started

    def coefficients(self, t):
        if t != self.cache_t:
            g = self.provider.geometry(t)
            e, mu, ratio = self.char.geometry_nodes(self.q, self.mu, g)
            source = self.char.source_reference(self.q, self.mu, self.weights, g,
                                                self.provider.tables['emissivity'])
            sigma = np.zeros((self.n, 3))
            mask = e <= 50000.
            sigma[mask] = self.native.call('SIGMA', e[mask]).reshape(-1, 3)
            self.cache = (g, e, mu, source, sigma)
            self.cache_t = t
        return self.cache

    def physical_rhs(self, t, y):
        g, e, mu, source, _ = self.coefficients(t)
        photon_state = y[4:4+self.n]
        number = photon_state/e if self.coordinate == 'energy' else photon_state
        nodes = np.column_stack([e, mu, number, source])
        result = self.native.rhs(t, g, y[:4], nodes)
        self.calls += 1
        self.max_local_number = max(self.max_local_number, abs(result[12]))
        self.max_local_energy = max(self.max_local_energy, abs(result[13]))
        # Counters: escape, expansion work, source energy, absorbed N, source N, CMB.
        photon_dot = result[15:]
        if self.coordinate == 'energy':
            # U_i = E_i(t) N_i, in eV per reference cm^3. Same characteristic.
            lam = g['H']+g['s']*(3*mu*mu-1)
            photon_dot = e*photon_dot-lam*photon_state
        return np.r_[result[:4], photon_dot, result[4:8], source.sum(), result[14]]

    def rhs(self, u, v):
        t = float(u * self.end)
        result = self.end * self.physical_rhs(t, v * self.scales) / self.scales
        now = time.monotonic()
        if now - self.last_progress > 30:
            print(json.dumps({'elapsed_s': now-self.started, 'rhs_calls': self.calls,
                              'z': self.provider.geometry(t)['z']}), flush=True)
            self.last_progress = now
        return result

    def jac(self, u, v):
        """Native gas columns; exact linear photon columns in the same variables."""
        self.jcalls += 1
        t = float(u * self.end)
        y = v * self.scales
        f = self.physical_rhs(t, y)
        rows, cols, vals = [], [], []
        # One-sided physical-state differences: no clipping or invalid stage query.
        for j in range(4):
            delta = 1e-7 * max(abs(y[j]), 1e-5 if j < 3 else .01)
            if j == 0 and y[0]+delta > 1:
                delta = -delta
            if j in (1, 2) and y[1]+y[2]+delta > 1:
                delta = -delta
            yp = y.copy()
            yp[j] += delta
            column = (self.physical_rhs(t, yp)-f)/delta
            nonzero = np.flatnonzero(column)
            rows.extend(nonzero)
            cols.extend([j]*len(nonzero))
            vals.extend(column[nonzero])
        g, e, mu, _, sigma = self.coefficients(t)
        vol = g['a_rel']**3
        h, he1, he2 = y[:3]
        lower = np.array([g['nH']*(1-h), g['nHe']*(1-he1-he2), g['nHe']*he1])
        kappa = C * (sigma @ lower)
        gas_columns = np.vstack([
            C/vol*sigma[:, 0]*(1-h),
            C/vol*(sigma[:, 1]*(1-he1-he2)-sigma[:, 2]*he1),
            C/vol*sigma[:, 2]*he1,
            C/vol/g['nH']*np.sum(sigma*lower*(e[:, None]-CHI), axis=1)])
        if self.coordinate == 'energy':
            gas_columns /= e
        pcols = np.arange(4, 4+self.n)
        for row in range(4):
            rows.extend([row]*self.n); cols.extend(pcols); vals.extend(gas_columns[row])
        lam = g['H']+g['s']*(3*mu*mu-1)
        diagonal = -kappa-lam if self.coordinate == 'energy' else -kappa
        rows.extend(pcols); cols.extend(pcols); vals.extend(diagonal)
        work = EV*lam if self.coordinate == 'energy' else EV*e*lam
        rows.extend([5+self.n]*self.n); cols.extend(pcols); vals.extend(work)
        absorbed_column = kappa/e if self.coordinate == 'energy' else kappa
        rows.extend([7+self.n]*self.n); cols.extend(pcols); vals.extend(absorbed_column)
        rows, cols, vals = np.asarray(rows), np.asarray(cols), np.asarray(vals)
        vals *= self.end*self.scales[cols]/self.scales[rows]
        return coo_matrix((vals, (rows, cols)), shape=(len(y), len(y))).tocsc()

    def energy(self, t, y):
        g = self.provider.geometry(t)
        e, _, _ = self.char.geometry_nodes(self.q, self.mu, g)
        h, he1, he2 = y[:3]
        chemical = self.g0['nH']*h*CHI[0]+self.g0['nHe']*(he1*CHI[1]+he2*(CHI[1]+CHI[2]))
        photon_energy = (sum(y[4:4+self.n]) if self.coordinate == 'energy'
                         else np.dot(y[4:4+self.n], e))
        return EV*(self.g0['nH']*y[3]+chemical+photon_energy)

    def output(self, u, v):
        t, y = float(u*self.end), v*self.scales
        g, e, _, _, sigma = self.coefficients(t)
        h, he1, he2 = y[:3]
        photons = y[4:4+self.n]/e if self.coordinate == 'energy' else y[4:4+self.n]
        counters = y[4+self.n:]
        ne = g['nH']*h+g['nHe']*(he1+2*he2)
        temp = 2*y[3]*g['nH']*EV/(3*KB*(g['nH']+g['nHe']+ne))
        energy = self.energy(t, y)
        residual = energy+counters[0]+counters[1]-counters[2]-counters[5]-self.e0
        budget = self.e0+abs(energy)+np.abs(counters[[0, 1, 2, 5]]).sum()
        number_residual = photons.sum()+counters[3]-counters[4]-self.initial_number
        row = dict(time_s=t, z=g['z'], xHII=h, xHeII=he1, xHeIII=he2, T_K=temp,
                   ne_cm3=ne, photon_cm3=photons.sum()/g['a_rel']**3,
                   GammaHI_s=C*np.dot(photons, sigma[:, 0])/g['a_rel']**3,
                   GammaHeI_s=C*np.dot(photons, sigma[:, 1])/g['a_rel']**3,
                   GammaHeII_s=C*np.dot(photons, sigma[:, 2])/g['a_rel']**3,
                   energy_ledger_scaled=residual/self.e0,
                   energy_ledger_budget_scaled=residual/budget,
                   number_ledger_scaled=number_residual/self.g0['nH'],
                   min_N_ref=photons.min(), escaped_energy_ref=counters[0],
                   work_energy_ref=counters[1], source_energy_ref=counters[2],
                   cmb_energy_ref=counters[5])
        return {k: float(x) for k, x in row.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--n1', type=Path, default=HERE.parent/'n1')
    parser.add_argument('--n2', type=Path, default=HERE.parent/'n2')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--shear', type=float, default=0.)
    parser.add_argument('--energy', type=int, default=128)
    parser.add_argument('--angle', type=int, default=2)
    parser.add_argument('--rtol', type=float, default=1e-8)
    parser.add_argument('--max-step', type=float, default=1/256)
    parser.add_argument('--photon-coordinate', choices=['number', 'energy'], default='energy')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    n1 = load('native_history_n1', args.n1/'provider.py')
    n2 = load('native_history_n2', args.n2/'characteristics.py')
    provider = n1.HistoryProvider(args.shear)
    native = n1.Native(args.n1/'native/target/release/rei_n1_native')
    problem = Coupled(provider, native, n2, args.energy, args.angle, args.photon_coordinate)
    identity = dict(provider=provider.identity, native_sha256=native.binary_sha256,
                    driver_sha256=sha(__file__), n1_sha256=sha(args.n1/'provider.py'),
                    n2_sha256=sha(args.n2/'characteristics.py'),
                    contract_sha256=sha(HERE/'CONTRACT.json'),
                    args={k: str(v) if isinstance(v, Path) else v for k, v in vars(args).items()})
    (args.output/'IDENTITY.json').write_text(json.dumps(identity, indent=2)+'\n')
    rows = [problem.output(0., problem.y0/problem.scales)]
    saved_u, saved_v = [0.], [problem.y0/problem.scales]
    samples = np.linspace(0, 1, 129)
    sample_i = 1
    start = time.monotonic()
    status, failure = 'RUNNING', None
    solver = None
    try:
        solver = BDF(problem.rhs, 0., problem.y0/problem.scales, 1.,
                     rtol=args.rtol, atol=args.rtol*1e-8, jac=problem.jac,
                     max_step=args.max_step)
        while solver.status == 'running':
            message = solver.step()
            if solver.status == 'failed':
                raise RuntimeError(message)
            dense = solver.dense_output()
            while sample_i < len(samples) and samples[sample_i] <= solver.t:
                u = float(samples[sample_i]); v = dense(u)
                rows.append(problem.output(u, v)); saved_u.append(u); saved_v.append(v)
                sample_i += 1
            if len(rows) % 16 == 0:
                (args.output/'PROGRESS.json').write_text(json.dumps(rows[-1], indent=2)+'\n')
        status = 'COMPUTED_NOT_REVIEWED'
    except Exception as exc:
        status = 'FAILED_PRESERVED'
        failure = dict(type=type(exc).__name__, message=str(exc), traceback=traceback.format_exc(),
                       last_accepted_u=None if solver is None else float(solver.t))
        (args.output/'FIRST_FAILURE.json').write_text(json.dumps(failure, indent=2)+'\n')
        if solver is not None:
            np.savez_compressed(args.output/'LAST_ACCEPTED.npz', u=solver.t, scaled_y=solver.y,
                                scales=problem.scales)
    finally:
        native.close()
    np.savez_compressed(args.output/'history.npz', u=saved_u, scaled_states=np.array(saved_v),
                        scales=problem.scales, q=problem.q, mu=problem.mu, weights=problem.weights)
    meta = dict(status=status, elapsed_s=time.monotonic()-start, rhs_calls=problem.calls,
                jac_calls=problem.jcalls, node_count=problem.n, sampled_epochs=len(rows),
                end_time_s=problem.end, max_local_number=problem.max_local_number,
                max_local_energy=problem.max_local_energy, history=rows, failure=failure)
    (args.output/'RESULT.json').write_text(json.dumps(meta, indent=2)+'\n')
    print(json.dumps({k: v for k, v in meta.items() if k not in ('history', 'failure')}), flush=True)
    return 0 if status == 'COMPUTED_NOT_REVIEWED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
