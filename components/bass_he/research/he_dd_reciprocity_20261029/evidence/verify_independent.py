"""Compare independent Decimal80 four-vector oracle against exact Fraction API."""
import json,sys
from pathlib import Path
from decimal import Decimal as D,localcontext
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from reciprocity import T_matching,reciprocity_ratio,ORDERED
p=json.loads(Path(__file__).with_name('INDEPENDENT_ORACLE.json').read_text())
with localcontext() as ctx:
    ctx.prec=95
    err=D(0)
    for x in p['cases']:
        e=F(x['Egamma_MeV'])
        for val,actual in [(T_matching(e),D(x['Td_MeV'])),
                           (reciprocity_ratio(e,ORDERED),D(x['ordered_ratio']))]:
            err=max(err,abs(D(val.numerator)/D(val.denominator)-actual))
        for key in ['E_sum_residual_MeV','p_z_sum_residual_MeV2',
                    'p_z_sum_residual_MeV','mass_shell_plus_residual_MeV2',
                    'mass_shell_minus_residual_MeV2']:
            if key in x:err=max(err,abs(D(x[key])))
    print('independent_Decimal80_cases',len(p['cases']))
    print('max_abs_residual',err)
    assert err < D('1e-70')
