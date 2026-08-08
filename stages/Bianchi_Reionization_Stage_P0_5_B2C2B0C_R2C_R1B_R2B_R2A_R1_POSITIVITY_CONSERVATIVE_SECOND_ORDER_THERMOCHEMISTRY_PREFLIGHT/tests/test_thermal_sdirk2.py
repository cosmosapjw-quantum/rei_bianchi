from __future__ import annotations
import importlib.util,sys
from pathlib import Path
import numpy as np

MODULE=Path(__file__).parents[1]/'analysis/thermal_sdirk2.py'

def load():
    spec=importlib.util.spec_from_file_location('r2b_r2a_r1_sdirk2',MODULE)
    m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m


def pop(): return np.array([[5.,3.,1.,0.5,0.2]])

def rhs(logt,population,volume,photoheat,hubble):
    m=load(); T=np.exp(logt); a,b,c,d,e=population.T
    particles=(a+b)+(c+d+e)+b+d+2*e
    return -3*hubble*m.KB_ERG*T*particles


def test_sdirk2_is_second_order_for_expansion_decay():
    m=load(); p=pop(); T0=np.array([1e4]); H=np.array([0.1]); errors=[]
    for n in (4,8,16,32):
        T=T0.copy(); U=m.energy_from_temperature(p,T); dt=1/n
        for _ in range(n):
            r=m.solve_sdirk2(
                parent_populations=p,stage_populations=p,final_populations=p,
                parent_energy=U,parent_temperature=T,
                stage_volume=np.ones(1),final_volume=np.ones(1),
                stage_photoheat=np.zeros(1),final_photoheat=np.zeros(1),
                stage_hubble=H,final_hubble=H,dt=np.array([dt]),rhs_function=rhs,
            )
            assert r.stage.bracketed[0] and r.final.bracketed[0]
            T=r.final.temperature; U=r.final.energy
        errors.append(float(abs(T[0]-T0[0]*np.exp(-0.2))))
    orders=[np.log(errors[i]/errors[i+1])/np.log(2) for i in range(3)]
    assert min(orders[-2:])>1.8,(errors,orders)


def test_sdirk2_final_balance_and_positivity():
    m=load(); p=pop(); T=np.array([5000.]); U=m.energy_from_temperature(p,T)
    r=m.solve_sdirk2(
        parent_populations=p,stage_populations=p,final_populations=p,
        parent_energy=U,parent_temperature=T,stage_volume=np.ones(1),final_volume=np.ones(1),
        stage_photoheat=np.zeros(1),final_photoheat=np.zeros(1),stage_hubble=np.array([0.2]),
        final_hubble=np.array([0.2]),dt=np.array([0.1]),rhs_function=rhs,
    )
    assert r.final.temperature[0]>0 and r.final.energy[0]>0
    assert r.final.relative_residual[0]<1e-12


def test_sdirk2_declares_exact_gamma():
    m=load()
    assert abs(m.GAMMA-(1.0-1.0/np.sqrt(2.0)))<1e-16
