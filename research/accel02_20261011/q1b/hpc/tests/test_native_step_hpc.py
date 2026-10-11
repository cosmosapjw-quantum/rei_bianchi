"""Manufactured whole-map equality against frozen v4; no physical history run."""
from pathlib import Path
import importlib.util
import json
import sys
import tempfile
import unittest
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ordered_cell_pool import Pool
from native_step_hpc import positive_native_step
from native_step_v4_diagnostics import positive_native_step as serial_step
from native_step_v3 import COUNTER_NAMES,gas_temperature
from test_cell_pool import ABSORBER,manufactured_opacity


class Provider:
    def geometry(self,t):
        return dict(a_rel=1.,b=0.,H=0.,s=0.,nH=1.,nHe=.1,Tcmb_K=2.7)
    def ray(self,q,mu,t):return q,mu,np.ones_like(mu)


class Source:
    provider=Provider()
    mu=np.array([-.5,.5])
    edges=np.array([10.,20.,30.])


class SourceAPI:
    @staticmethod
    def provider_event_times(source,t0,t1):return ()
    @staticmethod
    def integrate_source(source,t0,t1,event_times):
        n=np.full((2,2),.01*(t1-t0));u=n*np.array([15.,25.])[None,:]
        return dict(dN=n,dU=u,R1=np.ones(2),injected_energy_eV=u,
                    diagnostics=dict(manufactured_source=True))
    @staticmethod
    def advance_source(N,U,integrated):
        return dict(N=N+integrated['dN'],U_eV=U+integrated['dU'],
                    radiation_work_eV=np.zeros_like(N),diagnostics=dict(manufactured_pairing=True))


class Native:
    def __init__(self):self.calls=0;self.inputs=[]
    def rhs(self,t,g,gas,cells):
        self.calls+=1;self.inputs.append(np.array(cells,copy=True))
        out=np.zeros(15+2*len(cells));out[11]=gas_temperature(gas,g)
        return out


def normalize(value):
    if isinstance(value,np.ndarray):return value.tolist()
    if isinstance(value,np.generic):return value.item()
    if isinstance(value,dict):return {k:normalize(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)):return [normalize(v) for v in value]
    return value


class NativeMapIntegration(unittest.TestCase):
    def test_parallel_map_matches_frozen_v4_payload_and_preserves_parent(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'absorber.py';path.write_text(ABSORBER)
            spec=importlib.util.spec_from_file_location('serial_manufactured_absorption',path)
            absorber=importlib.util.module_from_spec(spec);spec.loader.exec_module(absorber)
            n=np.array([[1.,2.],[3.,4.]])
            state=dict(t_s=0.,gas=np.array([.1,.2,.1,1.]),N=n,U_eV=n*np.array([15.,25.])[None,:],
                R=np.ones_like(n),support=np.broadcast_to(np.array([[10.,20.],[20.,30.]]),(2,2,2)),
                counters={name:0. for name in COUNTER_NAMES},nH_ref=1.,nHe_ref=.1)
            before=json.dumps(normalize(state),sort_keys=True)
            reference_native=Native();actual_native=Native()
            opacity=manufactured_opacity(None)
            try:
                reference=serial_step(state,.5,Source(),opacity,reference_native,
                                      source_api=SourceAPI,absorption_api=absorber)
            finally:opacity.close()
            with Pool(workers=2,timeout_s=10.,absorption_path=path,
                      opacity_factory=manufactured_opacity) as pool:
                actual=positive_native_step(state,.5,Source(),pool,actual_native,source_api=SourceAPI)
                metrics=actual.pop('hpc_metrics')
                self.assertEqual(metrics['sigma_calls'],4)
                self.assertEqual(metrics['native_rhs_calls'],1)
                self.assertEqual(len(pool.pop_refinement_records()),4)
            self.assertEqual(normalize(actual),normalize(reference))
            self.assertEqual(len(actual_native.inputs),len(reference_native.inputs))
            for a,b in zip(actual_native.inputs,reference_native.inputs):np.testing.assert_array_equal(a,b)
            self.assertEqual(before,json.dumps(normalize(state),sort_keys=True))


if __name__=='__main__':unittest.main()
