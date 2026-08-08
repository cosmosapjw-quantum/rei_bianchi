from __future__ import annotations
import importlib.util, sys
from pathlib import Path
import numpy as np
import pytest

MODULE=Path(__file__).parents[1]/'analysis/thermal_trapezoid.py'

def load():
    spec=importlib.util.spec_from_file_location('r2b_r2a_r1_thermal2',MODULE)
    m=importlib.util.module_from_spec(spec); sys.modules[spec.name]=m; spec.loader.exec_module(m); return m


def fixed_pop():
    return np.array([[5.0,3.0,1.0,0.5,0.2]])


def expansion_rhs(logt,pop,volume,photoheat,hubble):
    m=load(); T=np.exp(logt)
    nhi,nhii,nhei,nheii,nheiii=pop.T
    particles=(nhi+nhii)+(nhei+nheii+nheiii)+nhii+nheii+2*nheiii
    return -3.0*hubble*m.KB_ERG*T*particles


def energy(m,pop,T):
    return m.energy_from_temperature(pop,np.asarray(T,float))


def test_trapezoid_is_second_order_for_expansion_only():
    m=load(); pop=fixed_pop(); T0=np.array([1.0e4]); H=0.1
    errors=[]
    for n in (4,8,16,32):
        T=T0.copy(); U=energy(m,pop,T); dt=1.0/n
        for _ in range(n):
            r=m.solve_trapezoid_corrector(
                parent_populations=pop,final_populations=pop,
                parent_energy=U,parent_temperature=T,
                volume0=np.ones(1),volume1=np.ones(1),
                photoheat0=np.zeros(1),photoheat1=np.zeros(1),
                hubble0=np.full(1,H),hubble1=np.full(1,H),dt=np.full(1,dt),
                rhs_function=expansion_rhs,
            )
            assert r.bracketed[0]
            T=r.temperature; U=r.energy
        exact=T0*np.exp(-2.0*H)
        errors.append(float(np.max(np.abs(T-exact))))
    orders=[np.log(errors[i]/errors[i+1])/np.log(2.0) for i in range(3)]
    assert min(orders[-2:])>1.8,(errors,orders)


def test_backward_euler_predictor_is_positive_and_balanced():
    m=load(); pop=fixed_pop(); T=np.array([5000.]); U=energy(m,pop,T)
    r=m.solve_backward_euler(
        populations=pop,parent_energy=U,parent_temperature=T,
        volume=np.ones(1),photoheat=np.zeros(1),hubble=np.array([0.2]),dt=np.array([0.1]),
        rhs_function=expansion_rhs,
    )
    assert r.bracketed[0] and r.temperature[0]>0 and r.energy[0]>0
    assert r.relative_residual[0]<1e-12


def test_trapezoid_balance_residual_is_small():
    m=load(); pop=fixed_pop(); T=np.array([8000.]); U=energy(m,pop,T)
    r=m.solve_trapezoid_corrector(
        parent_populations=pop,final_populations=pop,
        parent_energy=U,parent_temperature=T,
        volume0=np.ones(1),volume1=np.ones(1),
        photoheat0=np.zeros(1),photoheat1=np.zeros(1),
        hubble0=np.array([0.1]),hubble1=np.array([0.1]),dt=np.array([0.2]),
        rhs_function=expansion_rhs,
    )
    assert r.relative_residual[0]<1e-12


def test_no_positive_root_fails_closed_without_clipping():
    m=load(); pop=fixed_pop(); T=np.array([1.0]); U=energy(m,pop,T)
    def impossible(logt,pop,volume,photoheat,hubble):
        return np.full(logt.shape,-1.0e100)
    r=m.solve_trapezoid_corrector(
        parent_populations=pop,final_populations=pop,
        parent_energy=U,parent_temperature=T,
        volume0=np.ones(1),volume1=np.ones(1),
        photoheat0=np.zeros(1),photoheat1=np.zeros(1),
        hubble0=np.zeros(1),hubble1=np.zeros(1),dt=np.ones(1),
        rhs_function=impossible,
    )
    assert not r.bracketed[0]
    assert r.temperature[0]==T[0]


def test_invalid_shape_fails_closed():
    m=load()
    with pytest.raises(ValueError):
        m.energy_from_temperature(np.ones((2,4)),np.ones(2))
