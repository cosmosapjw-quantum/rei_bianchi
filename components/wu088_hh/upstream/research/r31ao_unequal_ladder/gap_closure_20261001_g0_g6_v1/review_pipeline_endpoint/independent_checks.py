"""Synthetic-only integration/endpoint artifact checks; no HH inputs."""
import json
import struct
from decimal import Decimal as D, localcontext
from fractions import Fraction as F

from certificate_pipeline.synthetic import evaluate_synthetic_bundle
from exact_gram.engine import ComplexDisk, Limits, ResourceLimit
from endpoint_bound.engine import gaussian_field_majorant, upper_mass_bound


def array(values, shape):
    header = repr({'descr':'<c16','fortran_order':False,'shape':shape}).encode()
    header += b' '*((-10-len(header)-1)%64)+b'\n'
    body=b''.join(struct.pack('<dd',v,0) for v in values)
    return b'\x93NUMPY\x01\x00'+len(header).to_bytes(2,'little')+header+body


def fixture():
    def diagonal(x):return array((x,0,0,x),(2,2))
    raw={'D_col':diagonal(0),'D_row':diagonal(0)}
    models={name:{'D_col':diagonal(scale),'D_row':diagonal(0),'K':diagonal(scale/2)}
            for name,scale in [('R31AK',1),('R31Z',3),('R31AD',5)]}
    balls={key:[[ComplexDisk((F(0),F(0)),F(0)) for _ in range(2)] for _ in range(2)] for key in raw}
    return raw,models,balls


def decimal_pi():
    # Independent Machin-free Gauss-Legendre AGM diagnostic, not authority.
    a,b,t,p=D(1),D(1)/D(2).sqrt(),D(1)/4,D(1)
    for _ in range(10):
        an=(a+b)/2;b=(a*b).sqrt();t-=p*(a-an)**2;a=an;p*=2
    return (a+b)**2/(4*t)


def main():
    raw,models,balls=fixture()
    models['R31AK']['K']=array((100,0,0,100),(2,2))
    r=evaluate_synthetic_bundle(raw,models,balls,scope='SYNTHETIC_ONLY')
    assert r['comparisons']['PRIMARY']['lower_gaps']==['-197/2','2']
    assert r['status']=='SYNTHETIC_DECISION_BOUND_UNRESOLVED'
    assert r['rigorous'] is False and r['certified_epsilon'] is None and r['certified_eta'] is None
    assert r['target_provenance_admitted'] is False and r['machine_predicate_certified'] is False
    raw,models,balls=fixture()
    models['R31AK']['K']=array((0,)*6,(3,2))
    try:
        evaluate_synthetic_bundle(raw,models,balls,scope='SYNTHETIC_ONLY',limits=Limits(max_entries=4))
    except Exception as exc:
        resource_case={'exception':type(exc).__name__,'message':str(exc),'resource_classification':isinstance(exc,ResourceLimit)}
    else:
        raise AssertionError('over-cap model accepted')
    origin=(F(0),)*3
    with localcontext() as ctx:
        ctx.prec=100
        pi=decimal_pi()
        expected={('s','O'):pi**3,('s','G1'):8*pi**D('2.5'),
                  ('px','G1'):3*pi**3,('pz','G1'):4*pi**3,
                  ('s','G2'):12*pi**D('2.5'),('px','G2'):12*pi**2}
        results=[]
        for (angular,field),exact in expected.items():
            q=gaussian_field_majorant(F(4),F(9),origin,origin,0,angular,field,bits=160)
            got=D(q.numerator)/q.denominator
            assert got>=exact
            assert got-exact<D('1e-40')
            results.append({'angular':angular,'field':field,'upper_minus_diagnostic':str(got-exact)})
        for mu,T in [(F(1),F(1)),(F(7,3),F(5,2)),(F(3,8),F(9,7))]:
            q=upper_mass_bound(0,mu,T,bits=160)
            got=D(q.numerator)/q.denominator
            exact=(D(mu.numerator)/mu.denominator)/(4*pi.sqrt()*(D(T.numerator)/T.denominator)**2)
            assert got>=exact and got-exact<D('1e-40')
    return {'stored_prediction_K_independence':'PASS','certification_flags_false_or_null':'PASS',
            'model_only_resource_case':resource_case,'gaussian_majorant_closed_form_checks':results,
            'upper_tail_i0_closed_form_checks':3,'diagnostic_decimal_precision':100,
            'diagnostics_are_certificates':False,'actual_HH_inputs_evaluated':False}


if __name__=='__main__':print(json.dumps(main(),indent=2))
