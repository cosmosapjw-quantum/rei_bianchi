#!/usr/bin/env python3
"""Source-bound conditional H/He interval; all atomic/AXI RHS calls are native.

This research entry point does not alter or admit production PhysicalHistory.
Coordinates are initial-frame comoving photon momenta, not fixed lab energies.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

HERE = Path(__file__).resolve().parent
EV = 1.602176634e-12
KB = 1.380649e-16
C = 29979245800.0
CHI = np.array([13.598434599702, 24.587389011, 54.41776])
EDGES = [*CHI, 13.6, 24.59, 54.42]


class Native:
    def __init__(self, binary: Path):
        self.proc = subprocess.Popen([str(binary)], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     text=True, bufsize=1)
        self.calls = {"RATES": 0, "SIGMA": 0, "RHS": 0}

    def call(self, command, values):
        self.calls[command] += 1
        line = command + " " + " ".join(format(float(v), ".17e") for v in values) + "\n"
        self.proc.stdin.write(line)
        self.proc.stdin.flush()
        result = self.proc.stdout.readline().strip()
        if not result.startswith("OK "):
            raise RuntimeError(f"Native {command}: {result!r}")
        out = np.fromstring(result[3:], sep=" ")
        if not np.isfinite(out).all():
            raise RuntimeError("nonfinite native output")
        return out

    def close(self):
        self.proc.stdin.close()
        self.proc.wait(timeout=10)
        err = self.proc.stderr.read()
        if self.proc.returncode != 0:
            raise RuntimeError(f"native exit {self.proc.returncode}: {err}")


def quadrature(energy_knots, order, nmu, emax=200.):
    """Split at native knots/jumps and both binding and fit thresholds."""
    if not math.isfinite(emax) or not 54.42 < emax <= 50000:
        raise ValueError('NATIVE_ENERGY_BAND_DOMAIN')
    xedges = np.log(np.unique(np.r_[10., emax, EDGES,
                   np.asarray(energy_knots)[(np.asarray(energy_knots)>10.) &
                                            (np.asarray(energy_knots)<emax)]]))
    xi, wi = np.polynomial.legendre.leggauss(order)
    q = np.exp(np.concatenate([.5*(lo+hi)+.5*(hi-lo)*xi
                               for lo, hi in zip(xedges[:-1], xedges[1:])]))
    w = np.concatenate([.5*(hi-lo)*wi for lo, hi in zip(xedges[:-1], xedges[1:])])
    mu, wm = np.polynomial.legendre.leggauss(nmu)
    return np.repeat(q,nmu), np.tile(mu,len(q)), np.repeat(w,nmu)*np.tile(wm/2,len(q))


def neutral_equilibrium(nh, nhe, gamma, rates):
    alpha, beta, dr = rates[:3], rates[3:6], rates[6:8]
    alpha = alpha.copy()
    alpha[1] += dr.sum()
    def fractions(ne):
        ion = gamma + beta*ne
        rr = alpha*ne
        h = ion[0]/(ion[0]+rr[0])
        # Products avoid ratios which diverge near ne=0.
        h0, h1, h2 = rr[1]*rr[2], ion[1]*rr[2], ion[1]*ion[2]
        denom = h0+h1+h2
        return np.array([h, h1/denom, h2/denom])
    def residual(ne):
        x = fractions(ne)
        return ne-nh*x[0]-nhe*(x[1]+2*x[2])
    maximum = nh+2*nhe
    ne = brentq(residual, maximum*1e-12, maximum,
                xtol=maximum*1e-14, rtol=1e-14)
    return fractions(ne), float(residual(ne)/maximum)


def characteristic(q, mu0, geom):
    b, a = geom['b'], geom['a_rel']
    r = np.sqrt((1-mu0**2)*np.exp(2*b)+mu0**2*np.exp(-4*b))/a
    return q*r, mu0*np.exp(-2*b)/(a*r), r


class Interval:
    def __init__(self, native, uvb, emissivity, background, order=2, nmu=4, source_scale=1.,emax=200.):
        self.native, self.uvb, self.emissivity, self.background = native, uvb, emissivity, background
        if not math.isfinite(source_scale) or source_scale < 0:
            raise ValueError('SOURCE_SCALE_DOMAIN')
        self.source_scale = source_scale
        self.q, self.mu0, self.weights = quadrature(np.r_[uvb.energies_eV,emissivity.energies_eV],order,nmu,emax)
        self.n = len(self.q)
        g = background(0.)
        self.nh0, self.nhe0 = g['nH'], g['nHe']
        self.initial_photons = uvb.photon_number_log(self.q,g['z'])*self.weights
        sig = native.call('SIGMA',self.q).reshape(-1,3)
        gamma = C*np.sum(sig*self.initial_photons[:,None],axis=0)
        rates = native.call('RATES',[50000.])
        x, self.neutrality_error = neutral_equilibrium(self.nh0,self.nhe0,gamma,rates)
        ne = self.nh0*x[0]+self.nhe0*(x[1]+2*x[2])
        w = 1.5*KB*50000.*(self.nh0+self.nhe0+ne)/(self.nh0*EV)
        # Counters: escaped energy, expansion/shear work, supplied energy,
        # absorbed photon count, injected photon count, all reference volume.
        self.y0 = np.r_[x,w,self.initial_photons,np.zeros(5)]
        self.scales = np.r_[np.ones(3),w,
                           np.maximum(self.initial_photons,1e-12*self.initial_photons.sum()),
                           np.full(3,self.energy(0.,self.y0)),
                           np.full(2,self.initial_photons.sum())]
        self.max_local_number = self.max_local_energy = 0.
        self.initial_gamma = gamma

    def energy(self,t,y):
        g = self.background(t)
        e,_,_ = characteristic(self.q,self.mu0,g)
        x = y[:3]
        chemical = self.nh0*x[0]*CHI[0]+self.nhe0*(x[1]*CHI[1]+x[2]*(CHI[1]+CHI[2]))
        return EV*(self.nh0*y[3]+chemical+np.dot(y[4:4+self.n],e))

    def rhs(self,t,y):
        g = self.background(t)
        e,mu,r = characteristic(self.q,self.mu0,g)
        source = self.source_scale*self.emissivity.photon_emission_log(e,g['z'])*self.weights/r**3
        nodes = np.column_stack([e,mu,y[4:4+self.n],source]).ravel()
        # Node count is encoded as a float-token accepted as integer-valued.
        values = np.r_[t,g['a_rel'],g['b'],g['H'],g['s'],g['nH'],g['nHe'],y[:4],self.n,nodes]
        result = self.native.call('RHS',values)
        if len(result) != 14+self.n:
            raise RuntimeError(f"native RHS length {len(result)} != {14+self.n}")
        self.max_local_number = max(self.max_local_number,abs(result[12]))
        self.max_local_energy = max(self.max_local_energy,abs(result[13]))
        return np.r_[result[:4],result[14:],result[4:8],source.sum()]

    def output(self,t,y):
        g = self.background(t)
        e,mu,_ = characteristic(self.q,self.mu0,g)
        nproper = y[4:4+self.n]/g['a_rel']**3
        sig = self.native.call('SIGMA',e).reshape(-1,3)
        gamma = C*np.sum(sig*nproper[:,None],axis=0)
        ne = g['nH']*y[0]+g['nHe']*(y[1]+2*y[2])
        temp = 2*y[3]*g['nH']*EV/(3*KB*(g['nH']+g['nHe']+ne))
        u = EV*np.dot(nproper,e)
        delta_p = EV*np.dot(nproper*e,(3*mu**2-1)/2)
        counters=y[4+self.n:]
        eres = (self.energy(t,y)+counters[0]+counters[1]-counters[2]-self.energy(0.,self.y0))/self.energy(0.,self.y0)
        nres = (sum(y[4:4+self.n])+counters[3]-counters[4]-sum(self.initial_photons))/sum(self.initial_photons)
        return dict(time_s=float(t),z=g['z'],xHII=y[0],xHeII=y[1],xHeIII=y[2],
                    T_K=temp,nH_cm3=g['nH'],ne_cm3=ne,
                    photon_cm3=float(nproper.sum()),photon_erg_cm3=float(u),
                    delta_pressure_erg_cm3=float(delta_p),GammaHI_s=gamma[0],GammaHeI_s=gamma[1],GammaHeII_s=gamma[2],
                    energy_ledger_scaled=float(eres),number_ledger_scaled=float(nres),
                    min_photon_cm3_reference=float(y[4:4+self.n].min()),
                    escape_erg_cm3_reference=counters[0],work_erg_cm3_reference=counters[1],
                    source_erg_cm3_reference=counters[2],absorbed_cm3_reference=counters[3],source_cm3_reference=counters[4])

    def run(self,method,steps,rtol):
        tau = np.linspace(0.,1.,17)
        end = 1e11
        scaled0 = self.y0/self.scales
        def rhs_scaled(u,v):
            return end*self.rhs(end*u,v*self.scales)/self.scales
        if method == 'RK4':
            if steps % 16: raise ValueError('RK4 steps must be multiple of16')
            values=[scaled0.copy()];v=scaled0.copy();h=1/steps
            for i in range(steps):
                t=i*h;k1=rhs_scaled(t,v);k2=rhs_scaled(t+h/2,v+h*k1/2)
                k3=rhs_scaled(t+h/2,v+h*k2/2);k4=rhs_scaled(t+h,v+h*k3)
                v=v+h*(k1+2*k2+2*k3+k4)/6
                if (i+1)%(steps//16)==0: values.append(v.copy())
            arr=np.array(values).T
            evaluations=steps*4
        else:
            sol=solve_ivp(rhs_scaled,(0.,1.),scaled0,method=method,t_eval=tau,
                          rtol=rtol,atol=rtol*1e-3,max_step=1/16)
            if not sol.success: raise RuntimeError(sol.message)
            arr=sol.y;evaluations=sol.nfev
        states=arr*self.scales[:,None]
        rows=[self.output(end*t,states[:,i]) for i,t in enumerate(tau)]
        return rows,states,dict(method=method,nfev=evaluations,rtol=rtol,steps=steps,
                               nodes=self.n,neutrality_scaled=self.neutrality_error,
                               max_local_number_ledger=self.max_local_number,
                               max_local_energy_ledger=self.max_local_energy)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary',type=Path,default=HERE/'native/target/release/rei_physical_native')
    parser.add_argument('--order',type=int,default=2)
    parser.add_argument('--nmu',type=int,default=4)
    parser.add_argument('--method',choices=['DOP853','RK4'],default='DOP853')
    parser.add_argument('--steps',type=int,default=32)
    parser.add_argument('--rtol',type=float,default=2e-10)
    parser.add_argument('--shear',type=float,default=.001)
    parser.add_argument('--source-scale',type=float,default=1.)
    parser.add_argument('--emax',type=float,default=50000.)
    parser.add_argument('--tag',default='base')
    args=parser.parse_args()
    from hm12_data import load_hm12
    from background import BianchiBackground
    tables=load_hm12();uvb,emissivity=tables['uvb'],tables['emissivity']
    bg=BianchiBackground(r=args.shear)
    native=Native(args.binary.resolve());start=time.perf_counter()
    try:
        interval=Interval(native,uvb,emissivity,bg.at,args.order,args.nmu,args.source_scale,args.emax)
        rows,states,meta=interval.run(args.method,args.steps,args.rtol)
        meta.update(native_calls=native.calls,elapsed_wall_s=time.perf_counter()-start,
                    band_eV=[10,args.emax],order=args.order,nmu=args.nmu,shear_ratio=args.shear,source_scale=args.source_scale,
                    source_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in (HERE/'sources').glob('*.out')},
                    claim='SOURCE_BACKED_CONDITIONAL_INTERVAL_NOT_PHYSICAL_EOR_ADMISSION')
        out=HERE/'evidence';out.mkdir(exist_ok=True)
        (out/f'{args.tag}.json').write_text(json.dumps(dict(metadata=meta,history=rows),indent=2)+'\n')
        np.savez_compressed(out/f'{args.tag}_dataset.npz',q_eV=interval.q,mu0=interval.mu0,
                            weights=interval.weights,initial_state=interval.y0,
                            times_s=np.linspace(0,1e11,17),states=states)
        print(json.dumps(dict(tag=args.tag,metadata=meta,initial=rows[0],final=rows[-1]),indent=2))
    finally:
        native.close()

if __name__=='__main__':main()
