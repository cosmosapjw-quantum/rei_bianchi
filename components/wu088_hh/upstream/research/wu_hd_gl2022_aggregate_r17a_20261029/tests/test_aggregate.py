from __future__ import annotations
import copy, json, os, subprocess, sys
from pathlib import Path
from fractions import Fraction
from decimal import Decimal
import pytest
ROOT=Path(__file__).parents[1]
sys.path.insert(0,str(ROOT/'src'))
sys.path.insert(0,str(ROOT/'verification'))
from aggregate import read_evaluate,validated_printed_data,SourceIdentityError,fraction_decimal
from independent_reference import independent
SRC=ROOT/'authority/PUBLISHED_TWO_POINT_TRANSCRIPTION.json'

def raw(): return json.loads(SRC.read_text())
def result(): return read_evaluate(SRC)

def test_exact_published_si():
    r=result()['rows'];assert [x['SQM_printed_1e-10_cm3_s'] for x in r]==['121/100','221/100']
    assert [Fraction(x['SQM_SI_m3_s']) for x in r]==[Fraction(121,10**18),Fraction(221,10**18)]

def test_printed_differences_without_probability():
    r=result()['rows'];assert [x['difference_printed_units'] for x in r]==['11/100','51/100']
    assert [x['difference_over_printed_halfwidth_NOT_SIGMA'] for x in r]==['11/20','51/20']
    assert result()['statistics_probability_or_sigma_admitted'] is False

def test_aggregate_cannot_be_state_admitted():
    r=result();assert r['source_rows_native_reactive']==0
    assert not r['state_resolved_admitted'] and not r['physical_consumption_admitted'] and not r['interpolation_or_extrapolation_admitted']

def test_independent_mpmath_precision():
    r=result()['rows'];a,_,_=independent(SRC)
    from mpmath import mp
    with mp.workdps(90):
        for rrow,ref in zip(r,a):
            assert Fraction(rrow['difference_printed_units'])==ref['diff']
            assert Fraction(rrow['SQM_SI_m3_s'])==ref['SI']
            assert mp.fabs(mp.mpf(rrow['author_fit_at_T_printed_units_Decimal100'])-ref['fit_mpmath'])<mp.mpf('1e-88')
            assert mp.fabs(mp.mpf(rrow['author_fit_to_printed_SQM_ratio_Decimal100'])-ref['fit_ratio_mpmath'])<mp.mpf('1e-88')

def test_reproduction_only_two_points():
    assert [x[0] for x in validated_printed_data(raw())]==[205,295]

def test_conservation():
    s=[-1,-1,1,1]
    assert sum(a*b for a,b in zip([1,1,0,2],s))==0
    assert sum(a*b for a,b in zip([0,1,1,0],s))==0
    assert sum(a*b for a,b in zip([1,0,1,0],s))==0

def test_nonidentification_constructor():
    K=Fraction(121,100);w=[Fraction(1,4),Fraction(3,4)]
    a=[K/w[0],Fraction(0)];b=[Fraction(0),K/w[1]]
    assert sum(w[i]*a[i] for i in range(2))==sum(w[i]*b[i] for i in range(2))==K
    assert a[0]!=b[0] and all(x>=0 for x in a+b)

@pytest.mark.parametrize('mutator',[
    lambda x: x['article'].__setitem__('doi','10.0000/fake'),
    lambda x: x['article'].__setitem__('reaction','H+ + HD -> H+ + HD'),
    lambda x: x['article'].__setitem__('method','TIQM'),
    lambda x: x['article'].__setitem__('printed_rate_unit','m^3 s^-1'),
    lambda x: x['points'][0].__setitem__('T_K','204'),
    lambda x: x['points'][0].__setitem__('k_SQM_printed','1.22'),
    lambda x: x['points'][0].__setitem__('k_experiment_printed',1.1),
    lambda x: x['points'][1].__setitem__('experimental_printed_halfwidth','-0.2'),
    lambda x: x['native_reactive_supplement'].__setitem__('status','AVAILABLE'),
    lambda x: x.__setitem__('is_state_rate',True),
])
def test_source_mutations_fail(mutator):
    j=raw();mutator(j)
    with pytest.raises(SourceIdentityError): validated_printed_data(j)

def test_cli_create_only(tmp_path):
    dst=tmp_path/'out.json'; cmd=[sys.executable,str(ROOT/'src/cli.py'),'--source',str(SRC),'--output',str(dst)]
    p=subprocess.run(cmd,text=True,capture_output=True,timeout=10);assert p.returncode==0,p.stderr
    assert json.loads(dst.read_text())['state_resolved_admitted'] is False
    p2=subprocess.run(cmd,text=True,capture_output=True,timeout=10);assert p2.returncode!=0 and 'FileExistsError' in p2.stderr

def test_no_source_file_implies_no_admission():
    obj=raw();assert obj['native_reactive_supplement']['SHA256'] is None
    assert result()['source_native_file_SHA256'] is None
