from __future__ import annotations
import importlib.util
from pathlib import Path
import subprocess
import sys
import numpy as np

STAGE=Path(__file__).resolve().parents[1]
REPO=STAGE.parents[1]


def _load(name,path):
 spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); sys.modules[name]=m; spec.loader.exec_module(m); return m


def _batch():
 tensor=_load('r2b_r2a_tensorized_backend_numpy',STAGE/'analysis/tensorized_inputs.py')
 data=tensor.load_tensorized_inputs(repo_root=REPO)
 n=256; y=data.state0.values[:,:n]; pop=y[:5].T.copy(); T=data.state0.temperature_K[:n]
 z=float(data.z_mid[0,0]); volume=data.comoving_volume_cm3[:n]/(1+z)**3
 heat=np.zeros(n); H=np.full(n,2e-18); U0=y[5].copy(); dt=np.full(n,2.5e12)
 return np.log(T),pop,volume,heat,H,U0,dt


def _run_isolated(case: str) -> None:
 proc=subprocess.run([sys.executable,str(STAGE/'analysis/jax_isolated_checks.py'),case],
                     cwd=REPO,text=True,capture_output=True,timeout=180)
 assert proc.returncode == 0, f"{case} failed\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"


def test_numpy_positive_root_matches_balance_gate():
 m=_load('r2b_r2a_thermal_backends_root_numpy',STAGE/'analysis/thermal_backends.py')
 logT,pop,volume,heat,H,U0,dt=_batch(); backend=m.NumpyThermalBackend()
 result=backend.solve(populations=pop,parent_energy=U0,parent_temperature=np.exp(logT),volume=volume,photoheat=heat,hubble=H,dt=dt)
 assert np.all(result.bracketed)
 assert np.all(result.temperature>0)
 assert np.max(result.relative_residual) <= 1e-10


def test_numpy_and_jax_thermal_backends_close(): _run_isolated('balance_parity')
def test_adaptive_dt_changes_do_not_recompile(): _run_isolated('balance_dt_compile')
def test_jax_compiled_positive_root_matches_numpy_root(): _run_isolated('root_parity')
def test_jax_root_variable_dt_does_not_recompile(): _run_isolated('root_dt_compile')
def test_jax_root_uses_locked_minimum_passing_iteration_count(): _run_isolated('metadata')
def test_jax_root_uses_one_synchronous_device_get_per_solve(): _run_isolated('device_get_count')
