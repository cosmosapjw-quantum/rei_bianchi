"""Conditional15.9→4 source/geometry/gas input provider, not a time integrator.

UVB supplies ONLY the photon Cauchy state; emissivity supplies ONLY births.
The source is band limited in PHYSICAL energy, while retained photon counts
live on fixed initial-frame covectors. No later HM12 background is imposed.
"""
from __future__ import annotations
from pathlib import Path
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
import numpy as np

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
PHYSICAL = REPO / 'research/physical_provider_20261010'
EV_ERG = 1.602176634e-12
KB_ERG_K = 1.380649e-16
EXPECTED = {
    'background.py': 'b80f1d2ca8b4ab251d93447ff746428e6230130bee9b87500b7960bbc3a0076d',
    'hm12_data.py': 'ede512206bd6f5acc85b1c6b90fda4edc256b4dd8a70c42f9726932b6bff5121',
    'sources/emissivity.out': '88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b',
    'sources/UVB.out': 'a708586ead551202c068b049d48afa87b96695c5a5d12253e9b9bbb74efd75dc',
}

def _module(name):
    spec = importlib.util.spec_from_file_location('accel02_n1_'+name, PHYSICAL/(name+'.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

class HistoryProvider:
    """Fixed scientific contract with explicit conditional initial gas.

    r=s_i/H_i; h=.7, Omega_m=.3, Omega_Lambda=.7, Omega_b=.045, Y=.24.
    Changing these parameters requires a new input contract, not default reuse.
    """
    z_initial = 15.9
    z_final = 4.0
    photon_band_eV = (10.0, 50000.0)
    temperature_initial_K = 20.0
    fractions_initial = (2e-4, 0.0, 0.0)
    cmb_present_K = 2.7255

    def __init__(self, r=0.0):
        if not math.isfinite(r) or abs(r) > .1:
            raise ValueError('N1_SHEAR_CONDITIONAL_DOMAIN')
        self.identity = {}
        for path, expected in EXPECTED.items():
            digest = hashlib.sha256((PHYSICAL/path).read_bytes()).hexdigest()
            if digest != expected:
                raise ValueError('N1_SOURCE_IDENTITY_MISMATCH:'+path)
            self.identity[path] = digest
        self.tables = _module('hm12_data').load_hm12()
        self.background = _module('background').BianchiBackground(r=r, z_i=self.z_initial,t_max=1e17)
        self.end_time_s = self.background.time_of_redshift(self.z_final)
        # Strict external time boundary; underlying background remains unchanged.
        self.r = r
        g0 = self.geometry(0.0)
        xe = self.fractions_initial[0]
        self.initial_gas = np.array([*self.fractions_initial,
            1.5*KB_ERG_K*self.temperature_initial_K*(1+g0['nHe']/g0['nH']+xe)/EV_ERG])
        gf = self.geometry(self.end_time_s)
        self.q_min_eV = self.photon_band_eV[0]
        # Every locally emitted E<=50keV is represented over the entire interval.
        # q>50keV starts empty and acquires photons only when its local E enters.
        self.q_max_eV = self.photon_band_eV[1]*max(gf['scale_rel'])
        if any(h <= 0 for t in [0.0,self.end_time_s] for h in self.geometry(t)['hubble']):
            raise ValueError('N1_REQUIRES_EXPANDING_AXES')

    def geometry(self,t):
        if not math.isfinite(t) or not 0 <= t <= self.end_time_s:
            raise ValueError('N1_TIME_DOMAIN')
        g=self.background.at(float(t))
        g['Tcmb_K']=self.cmb_present_K*(1+g['z'])
        return g

    def ray(self,q,mu0,t):
        q,mu0=np.broadcast_arrays(np.asarray(q,float),np.asarray(mu0,float))
        if not np.isfinite(q).all() or not np.isfinite(mu0).all() or np.any(q<=0) or np.any(abs(mu0)>1):
            raise ValueError('N1_RAY_DOMAIN')
        g=self.geometry(t)
        r=np.sqrt((1-mu0**2)*np.exp(2*g['b'])+mu0**2*np.exp(-4*g['b']))/g['a_rel']
        return q*r,mu0*np.exp(-2*g['b'])/(g['a_rel']*r),r

    @staticmethod
    def _weights(weights,shape):
        weights=np.broadcast_to(np.asarray(weights,float),shape)
        if not np.isfinite(weights).all() or np.any(weights<0):
            raise ValueError('N1_QUADRATURE_WEIGHTS')
        return weights

    def initial_photons(self,q,weights):
        q=np.asarray(q,float)
        if not np.isfinite(q).all() or np.any(q<=0): raise ValueError('N1_INITIAL_Q_DOMAIN')
        weights=self._weights(weights,q.shape)
        v=np.zeros(q.shape)
        inside=(q>=self.photon_band_eV[0])&(q<=self.photon_band_eV[1])
        v[inside]=self.tables['uvb'].photon_number_log(q[inside],self.z_initial)*weights[inside]
        return v

    def source_reference(self,q,mu0,weights,t):
        energy,mu,r=self.ray(q,mu0,t)
        weights=self._weights(weights,energy.shape)
        v=np.zeros(energy.shape)
        inside=(energy>=self.photon_band_eV[0])&(energy<=self.photon_band_eV[1])
        # dOmega/dOmega0 = 1/(a_rel^3 r^3); multiply proper source by a_rel^3.
        v[inside]=self.tables['emissivity'].photon_emission_log(energy[inside],self.geometry(t)['z'])*weights[inside]/r[inside]**3
        return v

class Native:
    def __init__(self,binary):
        self.binary=Path(binary).resolve()
        self.binary_sha256=hashlib.sha256(self.binary.read_bytes()).hexdigest()
        self.proc=subprocess.Popen([str(self.binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    def call(self,command,values):
        self.proc.stdin.write(command+' '+' '.join(format(float(x),'.17e') for x in values)+'\n');self.proc.stdin.flush()
        result=self.proc.stdout.readline().strip()
        if not result.startswith('OK '): raise ValueError(result)
        arr=np.fromstring(result[3:],sep=' ')
        if not np.isfinite(arr).all(): raise ValueError('N1_NONFINITE_NATIVE_RETURN')
        return arr
    def rhs(self,t,g,gas,nodes):
        nodes=np.asarray(nodes,float).reshape(-1,4)
        values=np.r_[t,g['a_rel'],g['b'],g['H'],g['s'],g['nH'],g['nHe'],gas,g['Tcmb_K'],len(nodes),nodes.ravel()]
        result=self.call('RHS',values)
        if len(result)!=15+len(nodes): raise ValueError('N1_NATIVE_SCHEMA')
        return result
    def close(self):
        self.proc.stdin.close();self.proc.wait(timeout=10)
        if self.proc.returncode: raise RuntimeError(self.proc.stderr.read())
