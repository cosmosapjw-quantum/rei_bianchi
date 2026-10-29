from pathlib import Path
from fractions import Fraction as Q
import importlib.util,json
from decimal import Decimal,localcontext
root=Path(__file__).resolve().parents[1]
s=importlib.util.spec_from_file_location('lift',root/'code/lift.py')
l=importlib.util.module_from_spec(s);s.loader.exec_module(l)
model,saved=l.load_inputs();_,num,gamma=l.owner_scales(model)
with localcontext() as ctx:
 ctx.prec=70
 def dec(q):return format(Decimal(q.numerator)/Decimal(q.denominator),'.65g')
 lines=[]
 for row in saved['rows']:
  y=[Q(v) for v in row['y']]
  charge=l.dot([0,1,2,3],y[13:17]); ref=gamma*charge
  lines.append('\t'.join([str(row['z']),dec(y[14]),dec(y[15]),dec(y[16]),dec(num['Li6']),dec(num['Li7']),dec(ref)]))
 (root/'results/CPP_INPUT.tsv').write_text('\n'.join(lines)+'\n')
