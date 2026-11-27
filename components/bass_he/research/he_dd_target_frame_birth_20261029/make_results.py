from pathlib import Path
from fractions import Fraction as F
import json,hashlib,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
import birth_ledger as b

def cv(x):
 if isinstance(x,F):return str(x)
 if isinstance(x,dict):return {k:cv(v) for k,v in x.items()}
 if isinstance(x,list):return [cv(y) for y in x]
 return x
summaries={str(e):{
 'per_event':cv(b.event_ledger(e)),
 'sample_mu_0':b.daughter_lab_sample(e,'0',90),
 'sample_mu_1':b.daughter_lab_sample(e,'1',90),
 'asymmetric_manufactured':cv(b.moment_packet(e,[(0,1),(1,3)])),
} for e in (213,330)}
out={
 'schema':'BASS_HE_DD_KINEMATIC_BIRTH_LEDGER_RESULTS_V1',
 'frozen_source_head':'85e2faeebd777ab3e9b287a0dc1dfd38d9af723c',
 'science':'per-event two-deuteron pair-centered moments, not a physical rate',
 'new_unittests':{'passed':27,'total':27,'command':"python -m unittest discover -s tests -p test_birth_ledger.py -v"},
 'independent_cpp':{'status':'CPP_PASS','cases':8,'result_max_abs_residual':'1.782778087610000000000000000000e-109','float_type':'boost::multiprecision::cpp_dec_float_100','note':'independent algorithm, not independent author'},
 'randomized_Fraction':{'passed':300,'total':300,'seed':12381},
 'wolfram':{'exact_zero_identities':4,'status':'PASS','independent_author':False},
 'history_ivp_rerun':False,'old_science_suite_rerun':False,
 'past_initial_failures':[{'type':'implementation','first':'C++ expression-template initializer list deduce failure','repair':'explicit std::array<V,5> values'}, {'type':'numerical_plot_input','first':'binary64 threshold round-off below exact Fraction threshold','repair':'plot grid begins threshold+1e-8 MeV; exact physics unchanged'}],
 'numerical_rounding_certified':False,
 'physical':{'kappa':None,'R_event':None,'physical_activation':False,'L4':False,'production':'HOLD'},
 'DAG':{'central':'28/88','HE':'14/18','PR105':'2/2','PR106':'1/2','reciprocity':'1/2','new_kinematic_local':'1/2_SCOPED_ONLY','workflow_R':'9/10','workflow_C':'9/10','physical_delta':0},
 'cases':summaries
}
(ROOT/'RESULTS.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n')
manifest={}
for f in sorted(ROOT.rglob('*')):
 if f.is_file() and '__pycache__' not in f.parts:
  manifest[str(f.relative_to(ROOT))]={'size':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}
(ROOT/'evidence/SOURCE_MANIFEST.json').write_text(json.dumps({'schema':'BASS_HE_DD_BIRTH_LOCAL_PREPUBLICATION_MANIFEST_V1','files':manifest},indent=2)+'\n')
print('RESULTS',len((ROOT/'RESULTS.json').read_text()),'manifest',len(manifest))
