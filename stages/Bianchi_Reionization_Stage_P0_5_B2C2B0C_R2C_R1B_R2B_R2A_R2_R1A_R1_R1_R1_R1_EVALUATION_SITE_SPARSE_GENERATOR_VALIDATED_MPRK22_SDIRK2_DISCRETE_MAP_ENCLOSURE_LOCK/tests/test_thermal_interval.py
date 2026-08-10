from __future__ import annotations
import importlib.util,sys
from pathlib import Path
import numpy as np
ANALYSIS=Path(__file__).resolve().parents[1]/'analysis'

def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);sys.modules[s.name]=m;s.loader.exec_module(m);return m

def test_point_interval_contains_exact_rhs_derivative():
 iv=load('evalsite_thermal_interval_test',ANALYSIS/'thermal_interval.py')
 root=Path(__file__).resolve().parents[3]
 parent=next(root.glob('stages/*R2A_R1_POSITIVITY_CONSERVATIVE_SECOND_ORDER_THERMOCHEMISTRY_PREFLIGHT'))/'analysis/thermal_fast_root.py'
 th=load('evalsite_thermal_parent_test',parent)
 pop=np.array([[2.0,1.0,0.5,0.2,0.1],[3.0,0.8,0.7,0.1,0.05]])
 volume=np.array([1e62,2e62]);heat=np.array([1e45,2e45]);H=np.array([2e-17,2e-17])
 ctx=th.ThermalContext.build(pop,volume,heat,H);x=np.log(np.array([8000.0,25000.0]))
 _,exact=ctx.rhs_and_derivative(x)
 lo,hi=iv.rhs_derivative_interval(ctx,x,x)
 assert np.all(lo<=exact) and np.all(exact<=hi)

def test_nonzero_log_temperature_box_contains_samples():
 iv=load('evalsite_thermal_interval_test2',ANALYSIS/'thermal_interval.py')
 root=Path(__file__).resolve().parents[3]
 parent=next(root.glob('stages/*R2A_R1_POSITIVITY_CONSERVATIVE_SECOND_ORDER_THERMOCHEMISTRY_PREFLIGHT'))/'analysis/thermal_fast_root.py'
 th=load('evalsite_thermal_parent_test2',parent)
 pop=np.array([[2.0,1.0,0.5,0.2,0.1]])
 ctx=th.ThermalContext.build(pop,np.array([1e62]),np.array([1e45]),np.array([2e-17]))
 x=np.log(np.array([14000.0]));r=np.array([1e-3]);lo,hi=iv.rhs_derivative_interval(ctx,x-r,x+r)
 for t in np.linspace(x[0]-r[0],x[0]+r[0],101):
  _,d=ctx.rhs_and_derivative(np.array([t]));assert lo[0]<=d[0]<=hi[0]

def test_root_derivative_interval_contains_exact_samples():
 iv=load('evalsite_thermal_interval_test3',ANALYSIS/'thermal_interval.py')
 root=Path(__file__).resolve().parents[3]
 parent=next(root.glob('stages/*R2A_R1_POSITIVITY_CONSERVATIVE_SECOND_ORDER_THERMOCHEMISTRY_PREFLIGHT'))/'analysis/thermal_fast_root.py'
 th=load('evalsite_thermal_parent_test3',parent)
 pop=np.array([[2.0,1.0,0.5,0.2,0.1]])
 ctx=th.ThermalContext.build(pop,np.array([1e62]),np.array([1e45]),np.array([2e-17]))
 x=np.log(np.array([14000.0]));r=np.array([2e-3]);weighted_step=np.array([3.25e10])
 lo,hi=iv.root_derivative_interval(ctx,x-r,x+r,weighted_step)
 for t in np.linspace(x[0]-r[0],x[0]+r[0],101):
  _,dr=ctx.rhs_and_derivative(np.array([t]))
  exact=ctx.energy_coefficient*np.exp(t)-weighted_step*dr
  assert lo[0]<=exact[0]<=hi[0]
