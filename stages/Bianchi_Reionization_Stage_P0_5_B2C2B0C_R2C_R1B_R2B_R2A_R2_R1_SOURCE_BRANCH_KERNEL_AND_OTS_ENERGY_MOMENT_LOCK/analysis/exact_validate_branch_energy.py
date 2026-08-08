#!/usr/bin/env python3
from __future__ import annotations
import json
from decimal import Decimal, getcontext
from pathlib import Path
import sympy as sp

getcontext().prec=90
root=Path(__file__).resolve().parents[1]
summary=json.loads((root/'data/BRANCH_ENERGY_SUMMARY.json').read_text())

v,f,y,z=sp.symbols('v f y z', real=True)
ell=sp.Rational(57,40); m=sp.Rational(737,1000)
w=(ell-m)+m*y
AH=v*w+(1-v)*f*z
AHe=v*m*(1-y)+(1-v)*f*(1-z)
non=v*(2-ell); esc=(1-v)*(1-f)
assert sp.simplify(AH+AHe+non+esc-(1+v))==0
assert sp.simplify(w+m*(1-y)-ell)==0
assert ell-m>0 and m>0 and 2-ell>0

# Hummer-Seaton table conversion v = X = 1 - [2(1-X)]/2.
table=[sp.Rational(143,100),sp.Rational(139,100),sp.Rational(96,100),sp.Rational(106,100),sp.Rational(122,100)]
# Actual ordered Table-V values 1.43,1.39,1.35,1.30,1.25.
table=[sp.Rational(143,100),sp.Rational(139,100),sp.Rational(135,100),sp.Rational(130,100),sp.Rational(125,100)]
expected=[sp.Rational(285,1000),sp.Rational(305,1000),sp.Rational(325,1000),sp.Rational(350,1000),sp.Rational(375,1000)]
assert [sp.simplify(1-t/2) for t in table]==expected

chiH=Decimal('13.598434599702'); chiHe=Decimal('24.587389011'); chiHe2=Decimal('54.417760')
E0=Decimal('0.75')*chiHe2
L=Decimal('1.425'); M=Decimal('0.737'); a=Decimal(2)-L; b=M-a; c=Decimal(1)-a-b
assert a==Decimal('0.575') and b==Decimal('0.162') and c==Decimal('0.263')
# Count equations from the three symmetric-pair support classes.
assert a+Decimal(2)*b+Decimal(2)*c==L
assert a+b==M
assert a+b+c==1
Hemin=M*E0-a*chiH-b*(E0-chiHe)
Hemax=M*E0-b*chiH
Hmin=E0-a*chiH; Hmax=E0
assert Hmax>Hmin and Hemax>Hemin

# Independent Decimal replay of stored bounds.
bounds=summary['two_photon_energy']['sharp_limiting_bounds_eV']
def rel(x,y):
    x=Decimal(str(x)); y=Decimal(str(y)); return abs(x-y)/max(abs(x),abs(y),Decimal('1e-80'))
checks={
 'H_energy_min':rel(bounds['H_capable_total_energy'][0],Hmin),
 'H_energy_max':rel(bounds['H_capable_total_energy'][1],Hmax),
 'He_energy_min':rel(bounds['HeI_capable_total_energy'][0],Hemin),
 'He_energy_max':rel(bounds['HeI_capable_total_energy'][1],Hemax),
}
assert max(checks.values())<Decimal('2e-15')

out={
 'classification':'R2B_R2A_R2_R1_EXACT_VALIDATION',
 'photon_identity':str(sp.simplify(AH+AHe+non+esc)),
 'two_photon_count_identity':str(sp.simplify(w+m*(1-y))),
 'v_table_exact':[str(q) for q in expected],
 'support_class_weights':{'a':str(a),'b':str(b),'c':str(c)},
 'decimal_relative_residuals':{k:str(v) for k,v in checks.items()},
 'status':'PASS'
}
(root/'receipts/EXACT_VALIDATION.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2))
