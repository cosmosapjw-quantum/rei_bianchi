"""HE23: real density ownership and independent per-H dimensional controls."""
import math,os,sys
from pathlib import Path
import numpy as np
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import he22_native_client as client
from he21_photo import Y_HE,N_H_Z20,EV_ERG,BIND_EV
from he22_contract import photomap,evaluate,PhotoOnlyTestDouble
from he22_coupled import run_coupled


def test_native_density_interface_exists():
    assert hasattr(client,'NativeDensityProvider'), 'missing source-bound total-nuclei provider'


def test_coupler_uses_injected_total_density():
    seen=[]
    def factory(a,x):
        nh=N_H_Z20*1.25*math.exp(-3*x)
        seen.append(nh)
        return PhotoOnlyTestDouble(nh)
    def density(a,x):return N_H_Z20*1.25*math.exp(-3*x)
    # A mismatch in the volume event check exposes a coupler still using old N_H_Z20.
    r=run_coupled(factory,m=4,steps=2,q=0.,density_provider=density)
    assert len(seen)==2
    assert abs(r['number_defect'])<3e-15
    assert abs(r['energy_defect'])<3e-12


def test_species_per_total_h_and_volume_conversion():
    nh=.002;dt=1e8;g=np.array([.2,.1,.3,.004])
    n=np.array([1e-6,2e-7,3e-8]);e=np.array([18.,35.,80.])
    p=photomap(g,n,e,nh,dt)
    # Independently derive competing probabilities from volumetric absorber counts.
    from he21_photo import sigma_cm2,C_CM_S
    densities=np.array([nh*.8,nh*Y_HE*.6,nh*Y_HE*.1])
    optical=C_CM_S*dt*sigma_cm2(e)*densities
    lost=n*(-np.expm1(-optical.sum(axis=1)))
    expected=(lost[:,None]*optical/optical.sum(axis=1)[:,None]).sum(axis=0)
    np.testing.assert_allclose(p.events_per_H,expected,rtol=2e-14,atol=0)
    np.testing.assert_allclose(densities*p.gamma_s,nh*expected/dt,rtol=2e-14,atol=0)
    np.testing.assert_allclose(densities*p.heat_erg_per_absorber_s,nh*p.heat_per_H*EV_ERG/dt,rtol=2e-14,atol=0)
    assert np.all(p.new_counts>=0) and np.all(p.heat_per_H>0)
    assert abs(np.dot(n-p.new_counts,e)-np.dot(expected,BIND_EV)-sum(p.heat_per_H))<1e-18


@pytest.mark.skipif(not os.getenv('HE23_NATIVE_BIN'),reason='real native binary must be explicitly supplied')
def test_real_native_density_and_strict_old_density_rejection(tmp_path):
    provider=client.NativeDensityProvider(os.environ['HE23_NATIVE_BIN'],client.OWNER_SOURCE_SHA,evidence_dir=tmp_path)
    # Independent cosmological density, same fixed source constants, not .9998 inference.
    h0=67.4e5/3.0856775814913673e24
    rho=3*h0*h0/(8*math.pi*6.67430e-8)
    nh0=(1-.2454)*(.0224/.674**2)*rho/1.67262192595e-24
    for a in (1/21,0.047620181473387826,.1,.2):
        d=provider(a,math.log(a*21))
        assert math.isclose(d.nh,nh0/a**3,rel_tol=1e-12)
        assert math.isclose(d.nhe/d.nh,Y_HE,rel_tol=1e-14)
        assert d.source_sha==client.OWNER_SOURCE_SHA
        g=np.array([.00001,.00001,0.,.0012]);gam=np.array([1e-18,2e-18,3e-18]);heat=gam*1e-11
        owner=client.NativeRustPoint(os.environ['HE23_NATIVE_BIN'],a,d.nh,evidence_dir=tmp_path)
        point=owner(g,gam,heat)
        alpha=np.array([1-g[0],Y_HE*(1-g[1]-g[2]),Y_HE*g[1]])
        np.testing.assert_allclose(point.photo_events_cm3_s,d.nh*alpha*gam,rtol=2e-14,atol=0)
        bad=client.NativeRustPoint(os.environ['HE23_NATIVE_BIN'],a,d.nh*.9998,evidence_dir=tmp_path)
        with pytest.raises(AssertionError,match='DENSITY_OR_HELIUM'):
            bad(g,gam,heat)


def test_newton_must_satisfy_existing_energy_gate_before_stopping():
    # Manufactured nonlinear RR with exact binding->escape ownership.
    # Fraction error below 3e-12 can still exceed the existing energy gate.
    from he22_contract import NativePoint,solve_midpoint
    nh=.002;dt=1e11;rate=300/dt
    def owner(g,gamma,power):
        rec=rate*g[0]**2
        binding=-nh*rec*BIND_EV[0]*EV_ERG
        return NativePoint(np.array([-rec,0.,0.]),0.,8.,np.zeros(3),
                           0.,binding,-binding,0.,0.)
    result=solve_midpoint(np.array([1e-5,1e-5,0.,.001]),np.empty(0),np.empty(0),nh,dt,owner)
    assert result.scaled_implicit_residual<3e-12
    assert abs(result.total_energy_residual_ev_per_H)<=2e-15


def test_bootstrap_preserves_existing_execution_directory(tmp_path):
    import subprocess
    work=tmp_path/'prior_run';work.mkdir()
    sentinel=work/'SUMMARY.json';sentinel.write_text('FIRST_FAILURE_OR_SUCCESS')
    script=Path(__file__).resolve().parents[1]/'ncp/NCP_BOOTSTRAP_AND_TEST.sh'
    env=os.environ.copy();env['HE22_WORK_ROOT']=str(work)
    p=subprocess.run(['bash',str(script)],env=env,capture_output=True,text=True)
    assert p.returncode!=0 and 'HE23_WORK_ROOT_NOT_EMPTY' in p.stderr
    assert sentinel.read_text()=='FIRST_FAILURE_OR_SUCCESS'
    assert list(work.iterdir())==[sentinel]


def test_raw_evidence_publishes_only_complete_json_and_keeps_failure(tmp_path):
    with pytest.raises(ValueError):client.record_evidence(tmp_path,'invalid',{'value':float('nan')})
    assert not list(tmp_path.glob('*_invalid.json'))
    assert list(tmp_path.glob('*.partial'))
    assert list(tmp_path.glob('*.failure'))


def test_native_timeout_retains_exact_command_and_partial_stream(tmp_path):
    exe=tmp_path/'slow_point'
    exe.write_text('#!/usr/bin/env python3\nimport time\nprint("before_timeout",flush=True)\ntime.sleep(5)\n')
    exe.chmod(0o700)
    owner=client.NativeRustPoint(exe,1/21,.002,timeout_s=.1,evidence_dir=tmp_path/'evidence')
    import subprocess
    with pytest.raises(subprocess.TimeoutExpired):
        owner(np.array([1e-5,1e-5,0.,.001]),np.zeros(3),np.zeros(3))
    import json
    files=list((tmp_path/'evidence').glob('*_rhs.json'))
    assert len(files)==1
    r=json.loads(files[0].read_text())
    assert r['exception_type']=='TimeoutExpired'
    assert r['argv'][0]==str(exe)
    assert 'before_timeout' in r['stdout']
