"""Post-gate R10G research comparison from stored 90-component integral only."""
import json
import math
import pathlib
import sys
import numpy as np

repo=pathlib.Path(sys.argv[1]);run=pathlib.Path(sys.argv[2]);out=pathlib.Path(sys.argv[3])
sys.path[:0]=[str(repo),str(repo/'src')]
from scripts.r10a_rho_freeze import _shell_summary
report=json.loads((run/'RETURN_REPORT.json').read_text())
baseline=json.loads((out/'BASELINE_REGRESSION.json').read_text())
assert report['converged'] and baseline['status']=='PASS'
names=['SL_CPC','SL_AUTHORCUT','COUL_CPC','COUL_AUTHOR','COUL_AUTHOR_FROZEN']
values=np.array(report['integral']).reshape(5,2,9)
errors=np.array(report['error_estimate']).reshape(5,2,9)
keep=np.arange(10)!=2
lanes={}
for k,name in enumerate(names):
    lanes[name]={}
    for j,E in enumerate(('0.5','5.0')):
        v=np.zeros(10);er=np.zeros(10);v[keep]=values[k,j];er[keep]=errors[k,j]
        lanes[name][E]={'indexed_transition_areas_a0sq':{str(i+1):float(v[i]) for i in range(10) if keep[i]},
                        'component_error_estimate_a0sq':{str(i+1):float(er[i]) for i in range(10) if keep[i]},
                        'Z2_shell_areas_a0sq':_shell_summary(v),
                        'Z2_shell_error_estimate_a0sq':_shell_summary(er),
                        'indexed_reaction_loss_a0sq':float(sum(v)),
                        'indexed_reaction_loss_error_estimate_a0sq':float(sum(er))}
(out/'FIVE_LANE_RESULT.json').write_text(json.dumps({'status':'R10G_LOCAL_ENDPOINT_NUMERICAL_PASS_NOT_GLOBAL_OR_PHYSICAL_CERTIFICATE',
 'lanes':lanes,'evaluations_new_first_interval':60,'outside_intervals_reused':16,
 'claim_limit':'FINITE_INDEXED_STATE_RESEARCH_INTEGRAL_NOT_PHYSICAL_PRODUCTION_CROSS_SECTION'},indent=2,allow_nan=False)+'\n')
root=repo/'research/shared_c64/20260929/CODE_I02_R10A_RHO_FREEZE_IMPACT/20260929T1535KST'
oracle=json.loads((root/'APPENDIX_A_ORACLE.json').read_text())
scale=json.loads((root/'APPENDIX_A_COMPARISON.json').read_text())['a0_squared_cm2']
classification='AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION'
metrics={}
for name in names:
    rows=[];all_logs=[];dominant_logs=[]
    for energy in ('0.5','5.0'):
        for shell in ('1','2','3'):
            model=lanes[name][energy]['Z2_shell_areas_a0sq'][shell]*scale
            author=oracle['shell_capture_cm2'][energy][shell]
            assert model>0 and author>0
            ratio=model/author;logratio=math.log(ratio)
            rows.append({'energy_keV_u':float(energy),'shell_n':int(shell),'model_cm2':model,
                         'author_cm2':author,'model_over_author':ratio,'log_ratio':logratio,
                         'classification':classification})
            all_logs.append(logratio)
            if shell in ('2','3'):dominant_logs.append(logratio)
    metrics[name]={'rows':rows,'all_six_multiplicative_rms':math.exp(math.sqrt(sum(x*x for x in all_logs)/6)),
                   'dominant_n2_n3_multiplicative_rms':math.exp(math.sqrt(sum(x*x for x in dominant_logs)/4)),
                   'classification':classification}
all_rule=metrics['COUL_AUTHOR']['all_six_multiplicative_rms']<=.95*metrics['SL_CPC']['all_six_multiplicative_rms']
dom_rule=metrics['COUL_AUTHOR']['dominant_n2_n3_multiplicative_rms']<=.95*metrics['SL_CPC']['dominant_n2_n3_multiplicative_rms']
appendix={'classification':classification,'metrics':metrics,
          'COUL_AUTHOR_all_six_improves_at_least_5pct':all_rule,
          'COUL_AUTHOR_dominant_improves_at_least_5pct':dom_rule,
          'COUL_AUTHOR_both_materially_improve':all_rule and dom_rule,
          'claim_limit':'AUTHOR_IMPLEMENTATION_COMPARISON_NOT_PHYSICAL_VALIDATION'}
(out/'APPENDIX_A_COMPARISON.json').write_text(json.dumps(appendix,indent=2,allow_nan=False)+'\n')
effects={}
for energy in ('0.5','5.0'):
    effects[energy]={}
    for vk,ek in [('indexed_transition_areas_a0sq','component_error_estimate_a0sq'),
                  ('Z2_shell_areas_a0sq','Z2_shell_error_estimate_a0sq'),
                  ('indexed_reaction_loss_a0sq','indexed_reaction_loss_error_estimate_a0sq')]:
        first=lanes['SL_CPC'][energy][vk];labels=list(first) if isinstance(first,dict) else ['total'];cells={}
        for label in labels:
            v={name:(lane[energy][vk][label] if isinstance(first,dict) else lane[energy][vk]) for name,lane in lanes.items()}
            e={name:(lane[energy][ek][label] if isinstance(first,dict) else lane[energy][ek]) for name,lane in lanes.items()}
            base=v['SL_CPC'];ratios={name:(value/base if base>0 else None) for name,value in v.items()}
            cells[label]={'values_a0sq':v,'errors_a0sq':e,
                          'cutoff_effect':v['SL_AUTHORCUT']-base,
                          'trajectory_effect':v['COUL_CPC']-base,
                          'interaction':v['COUL_AUTHOR']-v['COUL_CPC']-v['SL_AUTHORCUT']+base,
                          'frozen_delta_addition_effect':v['COUL_AUTHOR_FROZEN']-v['COUL_AUTHOR'],
                          'ratios_to_SL_CPC':ratios,
                          'material_vs_SL_CPC':{name:(base>0 and abs(value-base)/base>.01 and abs(value-base)>10*(e[name]+e['SL_CPC'])) for name,value in v.items() if name!='SL_CPC'}}
        effects[energy][vk]=cells
(out/'EFFECT_DECOMPOSITION.json').write_text(json.dumps(effects,indent=2,allow_nan=False)+'\n')
print(json.dumps({'appendix_rms':{n:{k:v for k,v in x.items() if k.endswith('rms')} for n,x in metrics.items()},
                  'both_materially_improve':appendix['COUL_AUTHOR_both_materially_improve']},indent=2))
