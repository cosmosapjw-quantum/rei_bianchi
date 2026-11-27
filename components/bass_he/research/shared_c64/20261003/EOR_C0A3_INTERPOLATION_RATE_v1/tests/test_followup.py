"""Post-implementation numerical and integration checks, not claimed as TDD."""
from pathlib import Path
from decimal import Decimal
from fractions import Fraction
import json, math, subprocess, sys
import pytest
import mpmath as mp
from bass_he_liu import load_dataset, ContractError, SourceUnavailable
from bass_he_liu_interp import Interpolator, KinematicBinding, maxwell_weights
ROOT=Path(__file__).resolve().parents[1]

def ds():return load_dataset(ROOT/'raw',ROOT/'provenance/INPUT_LOCK.json')

@pytest.mark.parametrize('method',['linear_E','loglog'])
def test_all_743_native_nodes_through_new_layer(method):
    d=ds();i=Interpolator(d,method=method,scope='payload_domain');n=0
    for cid,c in d.channels.items():
        for s in c.samples:
            p=i.evaluate(cid,s.energy_token)
            assert p['value_token']==s.value_token and not p['interpolated']
            assert p['source_line']==s.source_line and p['energy_column']==s.energy_column
            n+=1
    assert n==743

@pytest.mark.parametrize('method',['linear_E','loglog'])
def test_all_716_midpoints_positive_local_and_not_source(method):
    d=ds();i=Interpolator(d,method=method,scope='payload_domain');n=0
    for cid,c in d.channels.items():
        for l,r in zip(c.samples,c.samples[1:]):
            e=(l.energy+r.energy)/2;p=i.evaluate(cid,e);v=float(p['value'])
            lower,upper=sorted([float(l.value_token),float(r.value_token)])
            assert lower*(1-3e-14)<=v<=upper*(1+3e-14)
            assert v>0 and p['interpolated'] and p['interpolation_error_bound'] is None
            n+=1
    assert n==716

@pytest.mark.parametrize('a,d',[(0.,1e-12),(1e-7,.75),(1.,1e-10),(0.,1.),(1.,1.0000001),(5.,2.),(100.,1000.),(500.,2.5)])
def test_endpoint_weights_against_80digit_gamma_oracle(a,d):
    b=a+d;w=maxwell_weights(a,b)
    with mp.workdps(80):
        aa,bb=mp.mpf(a),mp.mpf(b);I1=mp.gammainc(2,aa,bb);I2=mp.gammainc(3,aa,bb)
        expected=[(bb*I1-I2)/(bb-aa),(I2-aa*I1)/(bb-aa)]
        assert max(float(abs(mp.mpf(x)/y-1)) for x,y in zip(w,expected))<3e-14

@pytest.mark.parametrize('cid,theta',[('EXC:1s:2p',2.),('EXC:1s:2p',20.),('EXC:1s:2p',200.),('NR_CX:1s:1s',2.),('NR_CX:1s:1s',20.),('NR_CX:1s:1s',200.),('NR_CX:2s:total',2.),('NR_CX:2s:total',20.),('NR_CX:2s:total',200.)])
def test_actual_finite_support_integral_independent_mp_quadrature(cid,theta):
    d=ds();i=Interpolator(d,method='linear_E')
    got=i.maxwell_functional(cid,'10','100',theta_native=theta)['value']
    c=d.channels[cid]
    with mp.workdps(60):
        es=[mp.mpf(s.energy_token) for s in c.samples];vs=[mp.mpf(s.value_token) for s in c.samples]
        def f(e):
            j=next(k for k in range(len(es)-1) if es[k]<=e<=es[k+1])
            t=(e-es[j])/(es[j+1]-es[j]);sig=(1-t)*vs[j]+t*vs[j+1]
            return sig*e/theta**2*mp.exp(-e/theta)
        points=[mp.mpf(10)]+[e for e in es if 10<e<100]+[mp.mpf(100)]
        expected=mp.fsum(mp.quad(f,[l,r]) for l,r in zip(points,points[1:]))
        assert float(abs(mp.mpf(got)/expected-1))<8e-14

@pytest.mark.parametrize('cid',['NR_CX:1s:n2','NR_CX:1s:n3','NR_CX:2s:n3','NR_CX:2s:n4'])
def test_derived_functional_equals_component_functionals(cid):
    d=ds();i=Interpolator(d,method='linear_E')
    full=i.maxwell_functional(cid,'10','100',theta_native=20.)['value']
    separate=math.fsum(i.maxwell_functional(c,'10','100',theta_native=20.)['value'] for c in d.members(cid))
    assert full==pytest.approx(separate,rel=3e-15)

def test_interval_additivity_and_no_tail_renormalization():
    i=Interpolator(ds(),method='linear_E')
    v=lambda a,b:i.maxwell_functional('EXC:1s:2p',a,b,theta_native=20.)
    a,b,c=v('10','30'),v('30','100'),v('10','100')
    assert a['value']+b['value']==pytest.approx(c['value'],rel=3e-15)
    assert 0<c['weight_mass_not_rate_fraction']<1 and c['full_functional'] is None

@pytest.mark.parametrize('kwargs',[{'energy_scale_J_per_native':0,'reduced_mass_kg':1,'authority':'x'}, {'energy_scale_J_per_native':1,'reduced_mass_kg':True,'authority':'x'},{'energy_scale_J_per_native':1,'reduced_mass_kg':1,'authority':''}])
def test_invalid_bindings_rejected(kwargs):
    with pytest.raises(ContractError):KinematicBinding(**kwargs)

def test_unknown_channel_not_residual_imputed():
    with pytest.raises(SourceUnavailable):Interpolator(ds(),method='linear_E').evaluate('NR_CX:1s:n5','50')

def test_cli_bad_json_and_no_context_do_not_create_output(tmp_path):
    for payload in ['{"authority":"x","authority":"y"}','{"energy_scale_J_per_native":NaN,"reduced_mass_kg":1,"authority":"x"}']:
        f=tmp_path/'input.json';f.write_text(payload);out=tmp_path/'out.json'
        p=subprocess.run([sys.executable,'-B','-m','bass_he_liu_interp','--root',str(ROOT),'partial-rate','EXC:1s:2p','10','100','--theta-J','1e-15','--binding',str(f),'--out',str(out)],capture_output=True,text=True)
        assert p.returncode==2 and not out.exists()
