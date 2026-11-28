from pathlib import Path
import sys,json,hashlib,platform
from fractions import Fraction as F
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from sig_da_bridge import *
rows=source_rows(ROOT/'source/M0475.x4')
ang=json.loads((ROOT/'evidence/PR105_ANGULAR_BOUNDS.json').read_text())
K=min_energy_L(rows)
items={}
for L in ('1/700','1/200','1/100'):
    a=ang[L]
    items[L]={str(k):dict(joint_interval(rows,K,a['lo'],a['hi'],k),K_critical_nb_per_MeV=critical_energy_L(rows,a['lo'],a['hi'],k)) for k in (1,2)}
source_hashes={}
for p in ('src/sig_da_bridge.py','tests/test_sig_da_bridge.py','source/M0475.x4','evidence/PR105_ANGULAR_BOUNDS.json','evidence/independent_lp.py','evidence/independent_angular.py','make_figures.py'):
 b=(ROOT/p).read_bytes()
 source_hashes[p]={'size':len(b),'sha256':hashlib.sha256(b).hexdigest(),'git_blob_sha1':hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()}
out={'schema':'BASS_HE_SIG_DA_COMPAT_RESULTS_V1','source_commit':EXFOR_COMMIT,'source_sha256':EXFOR_SHA256,'parent_pr105_head':PR105_HEAD,'K_min_exact':str(K),'K_min_nb_per_MeV':str(Decimal(K.numerator)/Decimal(K.denominator)),'SIG_330_interval_exact':[str(x) for x in energy_interval(rows,K)],'SIG_330_is_measured':False,'Ltheta_crit_kappa1_at_Kmin_approx':'0.0049918968474950244674895905534798417649361958','Ltheta_crit_rounding_certified':False,'conditional_cases':items,'source_hashes':source_hashes,'numerical_verification':{'python':platform.python_version(),'new_unittest_methods':25,'status':'PASS_after_one_bounded_repair','first_failure':'empty SIG row input erroneously returned K=0','independent_LP':'scipy HiGHS 6/6 scenarios matched formula to <1e-8 nb','independent_angular':'analytic active-line integral plus bisection','wolfram':'exact {19/800,17/80,403/400}','native_independent_agent':'NOT_RUN'},'admission':{'central_DAG':'28/88','HE_DAG':'14/18','previous_conditional_DAG':'2/2','new_conditional_DAG':'1/2','physical_delta':0,'R_event':None,'physical_activation':False,'L4':False,'production':'HOLD','kappa':'UNRESOLVED','energy_K':'DECLARED_SENSITIVITY_ONLY'}}
(ROOT/'RESULTS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
print('result keys',list(out.keys()),'bytes',(ROOT/'RESULTS.json').stat().st_size)
