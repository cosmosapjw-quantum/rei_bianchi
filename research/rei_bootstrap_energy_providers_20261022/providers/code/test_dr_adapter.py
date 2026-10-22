"""Frozen source checks and independent direct Decimal DR reference."""
import hashlib
import json
import math
import sys
from decimal import Decimal, localcontext
from pathlib import Path
from dr_adapter import CHANNELS, STATUS, dr_rate

SOURCE = Path(__file__).resolve().parents[1]/'sources/badnell_dr_clist_K'
DATA = json.loads(Path(__file__).with_name('dr_rows.json').read_text())
EXPECTED = {
    (2,1,1): (2, ('1.417e-3','2.235e-4','-2.185e-5'), ('4.633e5','5.532e5','8.887e5'), ('He3','He4'), (1,0)),
    (3,1,1): (2, ('1.451e-4','5.789e-3','1.889e-5'), ('8.529e5','1.056e6','1.170e7'), ('Li6','Li7'), (2,1)),
    (3,2,1): (1, ('2.941e-5','6.068e-5','-7.753e-7'), ('6.345e5','7.024e5','8.271e5'), ('Li6','Li7'), (1,0)),
}


def check_source():
    raw = SOURCE.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    assert sha == DATA['source_sha256'] == 'a43736b3c9fcc255c44312d3752c91304f8d6986feeeab85e32a0675d33186e9'
    assert '20230512' in raw.decode().splitlines()[0]
    blocks = {'C': {}, 'E': {}}
    block = None
    for line in raw.decode().splitlines():
        parts = line.split()
        if parts[:4] == ['Z','N','M','W']:
            block = parts[4][0]
        elif block and len(parts) >= 5:
            try:
                key_w = tuple(map(int, parts[:4]))
            except ValueError:
                continue
            if key_w[:3] in EXPECTED:
                assert key_w not in blocks[block]
                blocks[block][key_w] = tuple(Decimal(s) for s in parts[4:])
    assert set(blocks['C']) == set(blocks['E'])
    assert tuple(EXPECTED) == CHANNELS
    assert len(DATA['rows']) == 3
    selected = []
    for row in DATA['rows']:
        key = tuple(row['key'])
        w, cs, es, _, _ = EXPECTED[key]
        assert row['W'] == w
        assert blocks['C'][key+(w,)] == tuple(map(Decimal,cs))
        assert blocks['E'][key+(w,)] == tuple(map(Decimal,es))
        assert tuple(row['c']) == tuple(map(float,cs))
        assert tuple(row['E_K']) == tuple(map(float,es))
        selected.append({'key':list(key),'W':w,'c':list(cs),'E_K':list(es)})
    assert DATA['rows'][0]['c'][2] < 0 and DATA['rows'][2]['c'][2] < 0
    # Analytic lower bounds throughout the interval, independent of sampling.
    bounds = {'He_q1':float(Decimal('1.417e-3')-Decimal('2.185e-5')),
              'Li_q1':float(Decimal('2.941e-5')-Decimal('7.753e-7')),
              'Li_q2':float(Decimal('1.451e-4'))}
    assert all(v > 0 for v in bounds.values())
    return {'source_sha256':sha,'source_bytes':len(raw),'selected':selected,
            'continuum_shifted_sum_lower_bounds':bounds,'negative_coefficients_preserved':2}


def reference(key, temperature):
    # Direct original, unshifted signed formula. No production helper is reused.
    _, cs, es, _, _ = EXPECTED[key]
    with localcontext() as ctx:
        ctx.prec=90
        ctx.Emin=-999999
        ctx.Emax=999999
        t=Decimal.from_float(temperature)
        direct=sum((Decimal(c)*(-Decimal(e)/t).exp() for c,e in zip(cs,es)), Decimal(0))
        assert direct > 0
        alpha_cm=direct/(t*t.sqrt())
        alpha_si=alpha_cm*Decimal('1e-6')
        return alpha_cm.ln(), alpha_si.ln(), alpha_si


def check_decimal():
    worst_log=worst_relative=0.0
    counts={'normal':0,'subnormal':0,'underflow':0}
    samples=[]
    for key in EXPECTED:
        for j in range(9):
            temperature=100*100**(j/8)
            r=dr_rate(key,temperature)
            log_cm,log_si,rate=reference(key,temperature)
            for got,expected in ((r['log_alpha_cm3_s'],log_cm),(r['log_alpha_m3_s'],log_si)):
                err=abs(got-float(expected))
                worst_log=max(worst_log,err)
                assert err <= 2e-11,(key,temperature,err)
            represented=float(rate)
            expected_status='FLOAT_UNDERFLOW' if represented == 0 else 'REPRESENTABLE'
            assert r['representability_status'] == expected_status
            assert (r['alpha_m3_s'] == 0) == (represented == 0)
            if rate >= Decimal.from_float(sys.float_info.min):
                counts['normal']+=1
                rel=float(abs(Decimal.from_float(r['alpha_m3_s'])-rate)/rate)
                worst_relative=max(worst_relative,rel)
                assert rel <= 2e-11,(key,temperature,rel)
            elif represented:
                counts['subnormal']+=1
            else:
                counts['underflow']+=1
            samples.append({'key':list(key),'T_K':temperature,'log_alpha_m3_s':r['log_alpha_m3_s'],
                            'alpha_m3_s':r['alpha_m3_s'],'representability_status':r['representability_status']})
    assert counts['normal'] and counts['underflow']
    return {'cases':27,'precision':90,'Emin':-999999,'Emax':999999,
            'absolute_log_tolerance':2e-11,'normal_relative_tolerance':2e-11,
            'max_absolute_log_error':worst_log,'max_normal_relative_error':worst_relative,
            'counts':counts,'samples':samples}


def check_grid_and_api():
    counts={'REPRESENTABLE':0,'FLOAT_UNDERFLOW':0}
    min_s=math.inf
    for key,(_,_,_,isotopes,charges) in EXPECTED.items():
        for j in range(257):
            temperature=100*100**(j/256)
            r=dr_rate(key,temperature)
            assert (r['input_charge'],r['output_charge']) == charges
            assert r['isotopes'] == isotopes
            assert r['isotope_model'] == 'ElementalElectronicEquality'
            assert r['status'] == STATUS
            assert r['T_limits_K'] == (100.0,10000.0)
            assert r['shifted_signed_sum'] > 0
            min_s=min(min_s,r['shifted_signed_sum'])
            assert all(math.isfinite(r[k]) for k in ('log_alpha_cm3_s','log_alpha_m3_s','alpha_m3_s'))
            _,_,rate=reference(key,temperature)
            expected='FLOAT_UNDERFLOW' if float(rate) == 0 else 'REPRESENTABLE'
            assert r['representability_status'] == expected
            assert (r['alpha_m3_s'] == 0) == (float(rate) == 0)
            counts[expected]+=1
    invalid=[((2,1,1),t) for t in (99.999,10000.001,math.nan,math.inf,-math.inf,None,'bad')]
    invalid += [(key,1000) for key in ((1,0,1),(2,0,1),(3,0,1),(2,1,2),(99,1,1),None)]
    for key,t in invalid:
        try:
            dr_rate(key,t)
        except ValueError:
            pass
        else:
            raise AssertionError((key,t))
    return {'grid_cases':771,'decimal_status_reference_cases':771,'min_shifted_signed_sum':min_s,
            'representability_counts':counts,'invalid_cases':len(invalid),'inclusive_boundaries_checked':True}


def run():
    return {'source':check_source(),'decimal':check_decimal(),'grid_and_api':check_grid_and_api()}
