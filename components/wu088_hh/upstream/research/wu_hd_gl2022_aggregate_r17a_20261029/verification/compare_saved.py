"""Compare files written by two truly different algorithms; preregistered 1e-85 criterion."""
from pathlib import Path
from decimal import Decimal,localcontext
from fractions import Fraction
import json,sys

def compare(a:Path,b:Path):
    prod=json.loads(a.read_text());ref=json.loads(b.read_text())
    if len(prod['rows'])!=2 or len(ref['rows'])!=2: raise AssertionError('two rows')
    errors=[]
    with localcontext() as ctx:
        ctx.prec=100
        for x,y in zip(prod['rows'],ref['rows']):
            assert x['T_K']==y['T_K']
            for p,q in [('difference_printed_units','difference_exact'),('SQM_SI_m3_s','SQM_SI_exact'),('difference_over_printed_halfwidth_NOT_SIGMA','printed_displacement_exact')]:
                assert Fraction(x[p])==Fraction(y[q])
            for p,q in [('author_fit_at_T_printed_units_Decimal100','fit_mpmath_90digits'),('author_fit_to_printed_SQM_ratio_Decimal100','fit_ratio_mpmath_90digits')]:
                gap=abs(Decimal(x[p])-Decimal(y[q])); errors.append(str(gap))
                assert gap<Decimal('1e-85'),(p,str(gap))
    assert prod['state_resolved_admitted'] is False
    assert prod['physical_consumption_admitted'] is False
    assert prod['source_rows_native_reactive']==0
    return {'status':'PASS_SCOPED_TWO_POINT_AGGREGATE_ONLY','exact_comparisons':6,'high_precision_comparisons':4,'max_gap_decimal':str(max(Decimal(x) for x in errors)),'criterion':'absolute < 1e-85; fixed before execution','selected_native_rows':0,'physical_admission':False}

if __name__=='__main__':
    out=compare(Path(sys.argv[1]),Path(sys.argv[2]));p=Path(sys.argv[3]);
    with p.open('x',encoding='utf8') as f:f.write(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,sort_keys=True))
