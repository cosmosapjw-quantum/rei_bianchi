#!/usr/bin/env python3
"""Independent decimal-arithmetic corroboration, NOT independent science review."""
import argparse,json,math,pathlib,decimal,sys
from fractions import Fraction as F
ROOT=pathlib.Path(__file__).resolve().parent

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--results',required=True);args=ap.parse_args()
 d=json.loads((pathlib.Path(args.results)/'ANGULAR_BIRTH.json').read_text())
 rows=[json.loads(line) for line in (ROOT/'inputs/OWNER_PREBE_FINAL_BINARY.jsonl').read_text().splitlines()]
 n_checks=0;max_diff=decimal.Decimal(0)
 with decimal.localcontext() as ctx:
    ctx.prec=160
    D=decimal.Decimal
    for m in d['members']:
        idx=m['member']; row1=next(r for r in rows if r['member']==idx and r['label']=='half1_preBE')
        row2=next(r for r in rows if r['member']==idx and r['label']=='full_preBE')
        # Decimal.from_float transfers each stored f64 without a loss of a bit.
        w1=[D.from_float(float(w)) for w in row1['source_weights']]
        w2=[D.from_float(float(w)) for w in row2['source_weights']]
        den1=sum(w1,D(0));den2=sum(w2,D(0)); H=D.from_float(row1['source_n']);Ffull=D.from_float(row2['source_n'])
        assert Ffull==2*H;n_checks+=1
        delta=[H*(p/den1-q/den2) for p,q in zip(w1,w2)]
        tv=sum(map(abs,delta),D(0))/2
        native=[D.from_float(float(row1['source_n']*float(row1['source_weights'][i])))+D.from_float(float(row2['source_n']/2*float(row2['source_weights'][i])))-D.from_float(float(row2['source_n']*float(row2['source_weights'][i]))) for i in range(128)]
        actual=d['members'][idx]['angular_transport']['normalized_total_variation_photons_per_H_fraction']
        ref=F(actual);rounded=D(ref.numerator)/D(ref.denominator)
        error=abs(tv-rounded);max_diff=max(max_diff,error)
        assert error < D('1e-140'),(idx,error);n_checks+=1
        assert D(F(m['native_f64_count_defect_fraction']).numerator)/D(F(m['native_f64_count_defect_fraction']).denominator) == sum(native,D(0));n_checks+=1
        # Fresh centered time moment from independent scalar clocks.
        mm=(D.from_float(row1['endpoint_time'])-D.from_float(row2['endpoint_time']))*H
        frac=F(m['centered_M1_normalized_fraction']);t=D(frac.numerator)/D(frac.denominator)
        assert mm==t;n_checks+=1
    assert len(d['members'])==4
 out={'scope':'IND_DECIMAL_CORROBORATION_OF_STORED_F64_BIRTH_ONLY',
      'working_decimal_digits':160,'comparisons':n_checks,
      'max_decimal_fraction_abs_diff':str(max_diff),
      'passes':True,'new_root':False,'independent_formal_or_scientific_review':False,
      'continuous_error':None}
 print(json.dumps(out,sort_keys=True,indent=2))
if __name__=='__main__':main()
