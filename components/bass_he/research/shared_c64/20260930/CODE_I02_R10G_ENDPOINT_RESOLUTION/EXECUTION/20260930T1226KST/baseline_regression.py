"""R10G SL_CPC vs R10C baseline rule, using stored result only."""
import json
import math
import pathlib
import sys
import numpy as np

repo = pathlib.Path(sys.argv[1])
run = pathlib.Path(sys.argv[2])
out = pathlib.Path(sys.argv[3])
sys.path[:0] = [str(repo), str(repo / 'src')]
from scripts.r10a_rho_freeze import _shell_summary

rulepath = repo / 'research/shared_c64/20260930/CODE_I02_R10F_EXECUTION/20260930T1026KST/BASELINE_REGRESSION_RULE_PRECOMMITTED.json'
oldpath = repo / 'research/shared_c64/20260929/CODE_I02_R10C_EXACT_NODE_EXECUTION/20260929T1842KST/EXACT_THREE_LANE_RESULT.json'
rule = json.loads(rulepath.read_text())
old = json.loads(oldpath.read_text())['lanes']['F2-RHO']
new = json.loads((run / 'RETURN_REPORT.json').read_text())
assert new['converged'] and new['stable_confirmation']
values = np.array(new['integral']).reshape(5,2,9)[0]
errors = np.array(new['error_estimate']).reshape(5,2,9)[0]
rows=[]
for j, energy in enumerate(('0.5','5.0')):
    vector=np.zeros(10); errvector=np.zeros(10); keep=np.arange(10)!=2
    vector[keep]=values[j];errvector[keep]=errors[j]
    now_index={str(i+1):float(vector[i]) for i in range(10) if keep[i]}
    now_err_index={str(i+1):float(errvector[i]) for i in range(10) if keep[i]}
    now_shell=_shell_summary(vector); now_err_shell=_shell_summary(errvector)
    old_errvec=np.zeros(10)
    for idx, v in old[energy]['component_error_estimate_a0sq'].items(): old_errvec[int(idx)-1]=v
    old_err_shell=_shell_summary(old_errvec)
    for label, value in now_index.items():
        before=float(old[energy]['indexed_transition_areas_a0sq'][label]); old_error=float(old[energy]['component_error_estimate_a0sq'][label])
        rows.append({'energy_keV_u':float(energy),'observable':'indexed_transition_areas_a0sq','label':label,
                     'r10c_value':before,'r10g_value':value,'r10c_embedded_estimate':old_error,
                     'r10g_embedded_estimate':now_err_index[label]})
    for label,value in now_shell.items():
        before=float(old[energy]['Z2_shell_areas_a0sq'][label]);old_error=float(old_err_shell[label])
        rows.append({'energy_keV_u':float(energy),'observable':'Z2_shell_areas_a0sq','label':label,
                     'r10c_value':before,'r10g_value':value,'r10c_embedded_estimate':old_error,
                     'r10g_embedded_estimate':now_err_shell[label]})
flags=[]
rel=rule['stop_if_any_indexed_or_Z2_shell']['relative_difference_strictly_gt']
factor=rule['stop_if_any_indexed_or_Z2_shell']['absolute_difference_strictly_gt_factor_times_sum_embedded_estimates']
for i,row in enumerate(rows):
    before=row['r10c_value'];now=row['r10g_value'];diff=abs(now-before)
    row['absolute_difference']=diff
    row['relative_difference']=None if before==0 else diff/abs(before)
    material=(before==0 or diff/abs(before)>rel) and diff>factor*(row['r10c_embedded_estimate']+row['r10g_embedded_estimate'])
    if material:flags.append(i)
result={'status':'PASS' if not flags else 'R10G_BASELINE_REGRESSION_UNRESOLVED',
        'rule':rule,'source_r10c':str(oldpath.relative_to(repo)),
        'flagged_row_indices_zero_based':flags,'rows':rows,
        'max_absolute_difference':max(x['absolute_difference'] for x in rows),
        'max_relative_difference_nonzero_reference':max(x['relative_difference'] for x in rows if x['relative_difference'] is not None),
        'claim':'CONSISTENCY_HEURISTIC_NOT_PHYSICAL_VALIDATION'}
out.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:result[k] for k in ('status','flagged_row_indices_zero_based','max_absolute_difference','max_relative_difference_nonzero_reference')},indent=2))
