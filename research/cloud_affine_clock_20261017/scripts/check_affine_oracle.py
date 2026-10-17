import mpmath as mp,sympy as sy,csv,json,pathlib,math
root=pathlib.Path(__file__).resolve().parents[1];mp.mp.dps=100
rows=list(csv.DictReader((root/'evidence/affine_probe_v2.stdout').open()));results={}
for row in rows:
 name=row['case'];j0,j1,l0,l1,old=[mp.mpf(float(row[k])) for k in ['j0','j1','l0','l1','old']]
 tail=lambda s:(1-s)*(l0+(l1-l0)*s+l1)/2
 ref=old*mp.exp(-(l0+l1)/2)+mp.quad(lambda s:(j0+(j1-j0)*s)*mp.exp(-tail(s)),[0,1])
 err=abs(mp.mpf(float(row['surviving']))-ref);results.setdefault(name,[]).append({'steps':int(row['steps']),'abs_error':float(err),'reference':str(ref),'photon_residual':float(row['surviving'])+float(row['absorbed'])-float(old)-(float(j0)+float(j1))/2})
for name,r in results.items():
 for a,b in zip(r,r[1:]): b['observed_order']=math.log2(a['abs_error']/b['abs_error']) if b['abs_error'] and a['abs_error'] else None
 assert max(abs(x['photon_residual']) for x in r)<1e-13
 if name!='constant':
  assert all(3.8<x['observed_order']<4.2 for x in r[2:]),r
  assert r[-1]['abs_error']<1e-8
 else:assert max(x['abs_error'] for x in r)<1e-13
s,h,l0,l1,j0,j1=sy.symbols('s h l0 l1 j0 j1',positive=True)
u=sy.symbols('u');haz=sy.integrate(l0+(l1-l0)*u/h,(u,s,h));closed=(h-s)*(l0+(l1-l0)*s/h+l1)/2
nodes=[sy.Rational(1,2)-1/(2*sy.sqrt(3)),sy.Rational(1,2)+1/(2*sy.sqrt(3))];birth=sy.simplify(sum(h/2*((1-x)*j0+x*j1) for x in nodes)-h*(j0+j1)/2)
result={'scope':'externally prescribed affine scalar rates, fixed energy, no species allocation','rows':len(rows),'mpmath_dps':100,'results':results,'hazard_symbolic_residual':str(sy.simplify(haz-closed)),'injection_symbolic_residual':str(birth),'status':'PASS_SCOPED','gates':'variable cases N4..N32 order3.8..4.2 and N32abs<1e-8; ledgerabs<1e-13; constantabs<1e-13; not a general error bound'}
assert result['hazard_symbolic_residual']=='0' and birth==0
(root/'evidence/AFFINE_ORACLE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
