"""Independent reference: mpmath + Python Fraction, NEVER imports production module."""
import json
from fractions import Fraction
from decimal import Decimal
from pathlib import Path
import mpmath

def independent(path:Path):
    j=json.loads(path.read_text(encoding='utf-8'))
    a=[];mpmath.mp.dps=95
    for row in j['points']:
        t=int(row['T_K'])
        def ex(s): return Fraction(Decimal(s))
        k=ex(row['k_SQM_printed']);o=ex(row['k_experiment_printed']);h=ex(row['experimental_printed_halfwidth'])
        fit=mpmath.mpf('8.57')*mpmath.exp(-mpmath.mpf('405')/t)
        a.append({'T_K':t,'diff':k-o,'displacement':(k-o)/h,'SI':k/Fraction(10**16,1),'fit_mpmath':fit,'fit_ratio_mpmath':fit/mpmath.mpf(str(row['k_SQM_printed']))})
    gam=mpmath.log(mpmath.mpf('2.21')/mpmath.mpf('1.21'))/(1/mpmath.mpf(205)-1/mpmath.mpf(295))
    amp=mpmath.mpf('1.21')*mpmath.exp(gam/205)
    return a,gam,amp
