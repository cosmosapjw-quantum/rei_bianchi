from pathlib import Path
import sys,time,json,hashlib
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
import lipschitz_lp_certificate as p

def one(L,subdiv):
 start=time.monotonic()
 r=p.report(L,subdiv,iterations=19)
 small={k:(float(Fraction(v)) if k in ('continuum_lower','continuum_upper','grid_lower_root_t','grid_upper_root_t') else v) for k,v in r.items() if k not in ('lower_lp_dual','upper_lp_dual')}
 small['verification']={'source_sha256_prior':p.SOURCE_SHA256, 'parent_pr':p.PARENT_PR,'parent_head':p.PARENT_HEAD,'runtime':'PYTHON_PASS','old_ivp':'NOT_RUN','old_suite':'NOT_RUN','independent_author':'NOT_RUN'}
 small['elapsed_s']=time.monotonic()-start
 f=ROOT/'evidence'/f"certificate_L_{L.replace('/','_')}_grid_{subdiv}.json"
 f.write_text(json.dumps(r,ensure_ascii=False,indent=2))
 s=ROOT/'evidence'/f"summary_L_{L.replace('/','_')}_grid_{subdiv}.json"
 s.write_text(json.dumps(small,ensure_ascii=False,indent=2))
 print('RESULT',L,subdiv,small['grid_lower_root_t'],small['grid_upper_root_t'],small['continuum_lower'],small['continuum_upper'],'elapsed',round(small['elapsed_s'],2),flush=True)
 return small
if __name__=='__main__':
 print('PYTHON_PASS',sys.version,flush=True)
 one(sys.argv[1],int(sys.argv[2]))
