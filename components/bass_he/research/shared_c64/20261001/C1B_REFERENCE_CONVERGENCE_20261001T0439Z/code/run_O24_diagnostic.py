"""One authorized original O-centered diagnostic; no existing C1 run repeated."""
from pathlib import Path
import sys,time,resource,json
ROOT=Path(__file__).resolve().parents[1]
from parent_inputs import resolve_parent
PARENT=resolve_parent(ROOT)
sys.path.insert(0,str(PARENT/'code'))
from evidence_io import atomic_json,sha256
OUT=ROOT/'evidence/O24_DIAGNOSTIC.json'
if OUT.exists():raise FileExistsError(OUT)
resource.setrlimit(resource.RLIMIT_AS,(4*1024**3,4*1024**3))
import partialwave as pw
start=time.perf_counter()
g=pw.solve(2,m=0,lmax=24,elements=56,degree=4,rmax=24,quadrature=14)
b=pw.solve(2,m=1,lmax=24,elements=56,degree=4,rmax=24,quadrature=14)
x={'scope':'R2 original O-centered new l24 diagnostic','config':{'R':2,'lmax':24,'elements':56,'degree':4,'rmax':24,'quadrature':14},'energies':[g.energy,b.energy],'L_O_bar':pw.direct_angular_coupling(g,b),'residuals':[g.residual,b.residual],'metadata':[g.metadata,b.metadata],'elapsed_seconds':time.perf_counter()-start,'max_rss_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'parent_module_sha256':sha256(pw.__file__),'driver_sha256':sha256(__file__),'contract_sha256':sha256(ROOT/'NUMERICAL_CONTRACT.json')}
atomic_json(OUT,x);print(json.dumps(x),flush=True)
