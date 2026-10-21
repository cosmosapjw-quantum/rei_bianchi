"""Targeted compact-reader equivalence and observed legend-overlap repair only."""
import json, pathlib, time, shutil
from types import SimpleNamespace
import numpy as np
import analyze_d9 as ad
root=pathlib.Path(__file__).resolve().parent
out=root/'figure_repair';out.mkdir(exist_ok=False)
start=time.process_time();wall=time.monotonic()
args=SimpleNamespace(portable_manifest=str(root/'results/portable_input/D9_COMPACT_IDENTITY.json'),portable_manifest_sha='97a28d989b5b18148924effb1d45869960fd33ec8e083158db79fcf9e5689a15',portable_input=str(root/'results/portable_input/D9_COMPACT_INPUT.npz'),contract=str(root/'EXECUTION_CONTRACT.md'))
x,arrays,bindings,manifest,d8=ad.portable_inputs(args)
with np.load(root/'results/sampled_diagnostics_175.npz',allow_pickle=False) as nz:
    b={k:np.array(nz[k]) for k in nz.files if k not in ('x','case_ids')}
focus=[i for i,r in enumerate(bindings) if r['Sigma_F_i']==.003 and r['P_r_i']==-.001]
i=focus[2]
rep=ad.budget(x,*[arrays[k][i] for k in ('a','H','s','Pi_F_signed_matter','Pi_F_signed_gamma','Pi_F_signed_nu')])
for key,value in rep.items():np.testing.assert_array_equal(value,b[key][i])
checks=ad.read_json(root/'results/D8_ACCEPTED_BRACKET_BUDGET_CHECKS.json')['checks']
ad.figures(out,x,arrays,b,bindings,focus,checks,endpoint_only=True)
name='all175_consistency_and_focus_endpoints'
original=out/'production_original';original.mkdir()
for ext in ('.png','.pdf'):
    shutil.copy2(root/'results'/(name+ext),original/(name+ext));shutil.copy2(out/(name+ext),root/'results'/(name+ext))
record={'scope':'One representative compact-reader numerical comparison; targeted legend relocation using saved diagnostics only','reader_status':'PASS_EXACT_REPRESENTATIVE_RESULT_IDENTITY','representative_case_id':bindings[i]['case_id'],'comparison_keys':list(rep),'full175_analysis_repeated':False,'ode_calls':0,'moment_recomputations':0,'plot_defect':'Top legend obscured largest residuals and threshold line','plot_repair':'Legend moved above axes with layout allowance','new_source_sha256':ad.sha((root/'analyze_d9.py').read_bytes()),'production_source_sha256':ad.read_json(root/'results/RUN_RECEIPT.json')['source_sha256'],'process_cpu_seconds':time.process_time()-start,'wall_seconds':time.monotonic()-wall}
ad.write_json(out/'TARGETED_REPAIR_RECEIPT.json',record)
print(json.dumps(record,indent=2))
