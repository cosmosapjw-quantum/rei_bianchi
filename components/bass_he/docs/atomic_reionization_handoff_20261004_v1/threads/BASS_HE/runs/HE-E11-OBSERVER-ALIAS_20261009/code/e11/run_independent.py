"""Independent high-precision arithmetic checks on selected saved binary64 rows."""
import json,sys,os
from pathlib import Path
from decimal import Decimal,localcontext
from e11.run_analysis import parse_mode,display
from e11.observer_alias import f64,source
from e11.high_precision import decimal_photo,fraction_to_decimal

STEPS=(0,1,16,24,59,192,384)
MODES=('OFF','KF','GM')

def main(e10:Path,e7:Path,out:Path):
    if out.exists():raise FileExistsError('NEW_OUTPUT_ONLY')
    out.mkdir(parents=True)
    checks=0;worse=Decimal(0)
    samples={}
    for mode in MODES:
        r,_,_=parse_mode(mode,e10,e7)
        samples[mode]={}
        for k in STEPS:
            x=r[k]
            samples[mode][k]={}
            for label in ('live','endpoint'):
                gamma=[x['n'][c] for c in ('Gamma_hi','Gamma_hei','Gamma_heii')] if label=='live' else [x['e'][c] for c in ('Gamma_HI','Gamma_HeI','Gamma_HeII')]
                d=decimal_photo(x['e'],gamma,120)
                with localcontext() as ctx:
                    ctx.prec=120
                    expected=fraction_to_decimal(x[label+'_photo'] if label=='endpoint' else x['native_photo'],120)
                    ratio=abs(d-expected)/max(abs(expected),Decimal('1e-160'))
                worse=max(worse,ratio)
                if ratio>Decimal('1e-105'):
                    raise ArithmeticError('INDEPENDENT_SAVED_F64_ARITHMETIC_DISAGREEMENT')
                samples[mode][k][label]=str(d)
                checks+=1
    for mode in ('KF','GM'):
        for k in STEPS:
            for label in ('live','endpoint'):
                with localcontext() as ctx:
                    ctx.prec=120
                    q=Decimal(samples[mode][k][label])-Decimal(samples['OFF'][k][label])
                    # independent rational subtraction is only evaluated after Decimal input assembly
                    data_m=parse_mode(mode,e10,e7)[0][k]
                    data_off=parse_mode('OFF',e10,e7)[0][k]
                    qfrac=(data_m['native_photo']-data_off['native_photo']) if label=='live' else (data_m['endpoint_photo']-data_off['endpoint_photo'])
                    want=fraction_to_decimal(qfrac,120)
                    diff=abs(q-want)/max(abs(want),Decimal('1e-160'))
                worse=max(worse,diff)
                if diff>Decimal('1e-100'):raise ArithmeticError('DECIMAL_PAIRED_SIGNAL_DISAGREEMENT')
                checks+=1
    result={'checked_decimal_expressions':checks,'precision_digits':120,'max_relative_difference':str(worse),
        'scope':'Independent Decimal f64 reconstruction and algebra only; not independent atomic fit, ODE, spectrum or true error',
        'epochs':STEPS,'modes':MODES}
    with (out/'HIGH_PRECISION.json').open('x') as f:
        json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    return result
if __name__=='__main__':
    if len(sys.argv)!=4:raise SystemExit('USAGE python -m e11.run_independent E10 E7 NEW_OUT')
    print(main(*(Path(q) for q in sys.argv[1:])))
