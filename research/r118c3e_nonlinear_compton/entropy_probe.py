import numpy as np,json
from pathlib import Path
D=Path(__file__).resolve().parent;rng=np.random.default_rng(87);n=10000
a=np.exp(rng.uniform(-20,10,n));b=np.exp(rng.uniform(-20,10,n));d=np.exp(rng.uniform(-8,3,n))
J=b*(1+a)-np.exp(-d)*a*(1+b)
mu=np.log(b/(1+b))-np.log(a/(1+a))+d
assert min(J*mu)>=0
out=dict(samples=n,min_dissipation=float(min(J*mu)),max_dissipation=float(max(J*mu)),scope='finite positive pair sign check; direct proof in R5')
print(out);(D/'ENTROPY_PROBE.json').write_text(json.dumps(out,indent=2)+'\n')
