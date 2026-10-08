"""Exact-rational falsifier for binary64 fixture arithmetic and recorded Wide bound."""
import json,re,struct
from fractions import Fraction
from pathlib import Path
r=Path(__file__).parent
def f(bits):return struct.unpack('<d',struct.pack('<Q',int(bits)))[0]
results=[]
for row in re.findall(r'ORACLE (\d+) (\d+) (\d+) (\d+) (\d+) (-?\d+)',(r/'fraction-fixtures.log').read_text()):
 a,b,w,value,bmant,exp=row;exact=Fraction(f(a))+Fraction(f(b))*Fraction(f(w));actual=Fraction(f(value));bound=Fraction(f(bmant))*Fraction(2)**int(exp);error=abs(actual-exact)
 results.append({'operands_bits':[int(a),int(b),int(w)],'readout_bits':int(value),'absolute_error_fraction':str(error),'bound_fraction':str(bound),'passed':error<=bound})
if len(results)!=3:raise SystemExit('MISSING_FIXTURE')
(r/'EXACT_ORACLE.json').write_text(json.dumps({'passed':all(x['passed'] for x in results),'fixtures':results,'scope':'scaled owner arithmetic only; not kernel or continuous model'},indent=2)+'\n')
print(json.dumps({'passed':all(x['passed'] for x in results),'fixtures':len(results)}));raise SystemExit(0 if all(x['passed'] for x in results) else 1)
