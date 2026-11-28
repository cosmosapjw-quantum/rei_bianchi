"""Research-only Appendix-A implementation reproduction comparison."""
from __future__ import annotations
import json
import math
import sys
from pathlib import Path
from scipy import __version__ as scipy_version
from scipy.constants import physical_constants
from bass_he.geometry import atomic_json

LABEL='AUTHOR_IMPLEMENTATION_REPRODUCTION_ONLY_NOT_PHYSICAL_VALIDATION'


def compare(root):
    p=Path(root)
    model=json.loads((p/'attempt2/THREE_LANE_RESULT.json').read_text())
    oracle=json.loads((p/'APPENDIX_A_ORACLE.json').read_text())
    a0sq_cm2=(physical_constants['Bohr radius'][0]*100)**2
    lanes={}
    for name,es in model['lanes'].items():
        rows=[];all_logs=[];dominant_logs=[];total={}
        for E,record in es.items():
            source_shells=oracle['shell_capture_cm2'][E]
            model_shells=record['Z2_shell_areas_a0sq']
            for n in ('1','2','3'):
                value=model_shells[n]*a0sq_cm2
                ratio=value/source_shells[n]
                row={'classification':LABEL,'energy_keV_u':float(E),'shell_n':int(n),
                     'model_cm2':value,'author_cm2':source_shells[n],
                     'model_over_author':ratio,'log_ratio':math.log(ratio)}
                rows.append(row);all_logs.append(row['log_ratio'])
                if n in ('2','3'):dominant_logs.append(row['log_ratio'])
            total[E]={'classification':LABEL,
                      'model_cm2':sum(model_shells[n] for n in ('1','2','3'))*a0sq_cm2,
                      'author_cm2':sum(source_shells.values())}
            total[E]['model_over_author']=total[E]['model_cm2']/total[E]['author_cm2']
        lanes[name]={'rows':rows,'total_capture':total,
                     'all_six_multiplicative_rms':math.exp((sum(x*x for x in all_logs)/len(all_logs))**.5),
                     'dominant_n2_n3_multiplicative_rms':math.exp((sum(x*x for x in dominant_logs)/len(dominant_logs))**.5)}
    frozen=model['lanes']['F2-FROZEN'];dynamic=model['lanes']['F2-RHO']
    impact={}
    for E in ('0.5','5.0'):
        x=frozen[E]['indexed_reaction_loss_a0sq'];y=dynamic[E]['indexed_reaction_loss_a0sq']
        err=x*0+frozen[E]['indexed_reaction_loss_error_estimate_a0sq']+dynamic[E]['indexed_reaction_loss_error_estimate_a0sq']
        impact[E]={'F2_FROZEN_over_F2_RHO':x/y,'absolute_change_a0sq':x-y,
                   'relative_change':x/y-1,'summed_embedded_error_estimate_a0sq':err,
                   'change_over_summed_error_estimate':(x-y)/err}
    result={'classification':LABEL,'oracle_pdf_sha256':oracle['private_readonly_pdf_sha256'],
            'bohr_radius_m':physical_constants['Bohr radius'][0],
            'a0_squared_cm2':a0sq_cm2,'scipy_version_for_unit_conversion':scipy_version,
            'lanes':lanes,'F2_frozen_impact':impact,
            'case':'B_CHANGES_OUTPUT_BUT_WORSENS_AGGREGATE_AUTHOR_REPRODUCTION',
            'claim_ceiling':'FIVE_BRANCH_NMAX3_TWO_ENERGY_IMPLEMENTATION_DIAGNOSTIC_ONLY'}
    atomic_json(p/'APPENDIX_A_COMPARISON.json',result)
    return result


if __name__=='__main__':
    if len(sys.argv)!=2:raise SystemExit('usage: python scripts/r10a_compare_appendix.py ROOT')
    compare(sys.argv[1])
