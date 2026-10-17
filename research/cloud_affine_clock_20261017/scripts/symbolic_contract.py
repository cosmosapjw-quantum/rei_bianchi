import sympy as s,json,pathlib
x,t,h,j,n,l,a,b=s.symbols('x t h j n l a b',positive=True)
f=n*s.exp(-l*t)+j*(-s.expm1(-l*t) if hasattr(s,'expm1') else 1-s.exp(-l*t))/l
ode=s.simplify(s.diff(f,t)-(j-l*f));one=n*s.exp(-l*(a+b))+j*(1-s.exp(-l*(a+b)))/l
mid=n*s.exp(-l*a)+j*(1-s.exp(-l*a))/l;two=mid*s.exp(-l*b)+j*(1-s.exp(-l*b))/l
semigroup=s.simplify(one-two);phi=(1-s.exp(-x))/x
res={'sympy_version':s.__version__,'ode_residual':str(ode),'constant_source_semigroup_residual':str(semigroup),'phi_series':str(s.series(phi,x,0,8)),'psi_series':str(s.series(1-phi,x,0,8)),'scope':'constant source fixed opacity only; no nonlinear 2nd-order claim','status':'PASS' if ode==0 and semigroup==0 else 'FAIL'}
p=pathlib.Path(__file__).resolve().parents[1]/'evidence/SYMPY_CONTRACT.json';p.write_text(json.dumps(res,indent=2)+'\n');print(json.dumps(res,indent=2));assert res['status']=='PASS'
