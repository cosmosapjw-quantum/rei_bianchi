"""Component integration checks, NOT all-94 scientific admission."""
import ctypes as ct
import os
from pathlib import Path
import subprocess
import numpy as np
import pytest

ROOT=Path(__file__).resolve().parents[1]

@pytest.fixture(scope='module')
def libs(tmp_path_factory):
    build=tmp_path_factory.mktemp('native')
    out=[]
    for lane in ('reference','candidate'):
        so=build/(lane+'.so')
        cpp=ROOT/'native'/lane/'r31a/hybrid12_wide_h_v2.cpp'
        cmd=['g++','-O3','-std=c++17','-fPIC','-shared','-fno-fast-math','-ffp-contract=off','-fopenmp',str(cpp),'-o',str(so)]
        subprocess.run(cmd,check=True,capture_output=True,text=True,timeout=60)
        lib=ct.CDLL(str(so))
        lib.mh_wide_foreign.argtypes=[ct.c_size_t,ct.c_size_t]+[ct.c_void_p]*7
        lib.mh_wide_foreign.restype=ct.c_int
        if lane=='candidate':
            lib.hh_set_num_threads.argtypes=[ct.c_int];lib.hh_set_num_threads.restype=ct.c_int
            lib.hh_last_team_size.restype=ct.c_int
        out.append(lib)
    return out


def inputs(z=8.,a=.2,b=.3):
    t=np.array([.01,.1,1.,10.]);gs=np.array([.08,.8,8.]);gw=np.array([.2,.7,.1])
    weights=np.random.default_rng(123).normal(size=(9,4,4)).astype('d')
    weights[:,1,1]=0  # exact sparse node, not threshold pruning
    pars=np.array([a,b,z,.4472517464474613],dtype='d')
    return t,gs,gw,weights,pars


def call(lib,args):
    t,gs,gw,w,pars=args
    out=np.full(12,complex(np.nan),dtype=np.clongdouble);aa=np.full(12,np.nan,dtype=np.longdouble)
    rc=lib.mh_wide_foreign(len(t),len(gs),*[x.ctypes.data for x in (t,gs,gw,w,pars,out,aa)])
    return rc,out,aa


def test_requested_parallel_team_actually_runs(libs):
    _,c=libs
    assert c.hh_set_num_threads(2)==0
    rc,_,_=call(c,inputs())
    assert rc==0
    assert c.hh_last_team_size()==2


@pytest.mark.parametrize('z',[0.,8.,16.,32.,48.,64.])
@pytest.mark.parametrize('ab',[(.002,.015),(.2,30.)])
def test_native_order_preserving_equivalence(libs,z,ab):
    r,c=libs; args=inputs(z,*ab);rc,ref,ra=call(r,args)
    assert rc==0
    for threads in (1,2):
        assert c.hh_set_num_threads(threads)==0
        st,out,aa=call(c,args)
        assert st==rc
        np.testing.assert_array_equal(out,ref)
        np.testing.assert_array_equal(aa,ra)


def test_native_rejects_invalid_configuration(libs):
    r,c=libs
    assert c.hh_set_num_threads(0)<0
    args=list(inputs()); args[-1]=args[-1].copy();args[-1][0]=-1
    for lib in (r,c): assert call(lib,args)[0]==-306


def test_scalar_and_even_sources_are_byte_preserved():
    for relative in ['r31a/continuation.hpp','radial/analytic_wide.cpp']:
        assert (ROOT/'native/reference'/relative).read_bytes()==(ROOT/'native/candidate'/relative).read_bytes()
    old=(ROOT/'native/reference/r31a/hybrid12_wide_h_v2.cpp').read_text().split('// R30 H-level bridge:')[0]
    new=(ROOT/'native/candidate/r31a/hybrid12_wide_h_v2.cpp').read_text().split('// R31K-B candidate.')[0]
    assert old.rstrip()==new.rstrip()


def test_guarded_python_abi_rejects_nonfinite_and_wrong_shape(libs):
    from wu088_hh.native_candidate import ForeignKernel
    kernel=ForeignKernel(Path(libs[1]._name));args=list(inputs())
    args[-1]=args[-1].copy();args[-1][2]=np.nan
    with pytest.raises(ValueError,match='finite'):kernel(*args)
    args=list(inputs());args[3]=args[3][:3]
    with pytest.raises(ValueError,match='shape'):kernel(*args)


def test_fast_math_compilation_is_rejected():
    p=subprocess.run(['g++','-std=c++17','-fopenmp','-ffast-math','-fsyntax-only',str(ROOT/'native/candidate/r31a/hybrid12_wide_h_v2.cpp')],capture_output=True,text=True,timeout=30)
    assert p.returncode!=0
    assert 'Strict floating point required' in p.stderr
