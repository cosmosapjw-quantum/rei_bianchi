"""Checks already computed evidence; does not replay a photon or gas campaign."""
import argparse
import copy
import json
from pathlib import Path
from decimal import Decimal
import sys
import numpy as np
from continuous_defect import verify_inputs, read_csv, SegmentBatch


def run(root, output):
    root=Path(root)
    verify_inputs(root)
    lo=json.loads((root/'evidence/defect_rtol_2e9/RESULTS.json').read_text())
    hi=json.loads((root/'evidence/defect_rtol_2e11/RESULTS.json').read_text())
    oracle=json.loads((root/'evidence/ORACLE_RESULTS.json').read_text())
    symbolic=json.loads((root/'evidence/SYMBOLIC_VERIFICATION.json').read_text())
    rows=[];maxpair=0.;maxn=0.;maxb=0.
    if len(lo['records'])!=6 or len(hi['records'])!=6:
        raise ValueError('expected six saved fixed-gas transactions')
    for a,b in zip(lo['records'],hi['records']):
        if (a['mode'],a['step'])!=(b['mode'],b['step']):raise ValueError('record identity')
        gap=max(abs(x-y) for x,y in zip(a['projected_over_algebraic_TOL'],b['projected_over_algebraic_TOL']))
        maxpair=max(maxpair,gap)
        rows.append({'id':[a['mode'],a['step']],'rtol_pair_max_scaled_difference':gap})
    controls=[]
    for a in hi['local_oracle_controls']:
        b=next(x for x in oracle['results'] if x['key']==a['id'])
        d=b['signed_continuous_minus_frozen']
        n=max([abs(a['delta_P']-float(d['P1']))]+[abs(x-float(y)) for x,y in zip(a['delta_A'],d['A'])])
        e=max(abs(x-float(y)) for x,y in zip(a['delta_B_eV'],d['B_eV']))
        maxn=max(maxn,n);maxb=max(maxb,e)
        controls.append({'id':a['id'],'max_abs_P_A_difference':n,'max_abs_B_eV_difference':e})
    # These controls test unsupported-domain and physical-limit risks, rather
    # than duplicating the new variable-coefficient output with copied values.
    upstream=root/'inputs/upstream_e13c1'
    row=read_csv(upstream/'evidence/capture/OFF/SEGMENTS.csv')[0]
    stage=read_csv(upstream/'inputs/OFF_STAGES.csv')[0]
    class ConstantControl(SegmentBatch):
        def coeff(self,t):
            return self.lf,self.qf,self.e0*np.exp(-self.h*np.longdouble(t))
    b=ConstantControl([row],stage)
    endpoint,_,_=b.solve(np.zeros(1),2e-9)
    zero_defect=bool(np.all(endpoint==0))
    rejection={}
    for name,field,value in [('negative_initial','f0','-1'),('unsupported_outflow','outn','1'),
                              ('inconsistent_source_flag','source_on','0')]:
        edited=copy.deepcopy(row);edited[field]=value
        try:
            SegmentBatch([edited],stage)
        except ValueError:
            rejection[name]=True
        else:
            rejection[name]=False
    checks={'rtol_pair':maxpair<=.01,'independent_oracle_P_A':maxn<=1e-22,
            'independent_oracle_B':maxb<=1e-20,'oracle_internal_gates':oracle['verdict']=='PASS_SCOPED',
            'constant_coefficients_zero_defect':zero_defect,
            'domain_rejections':all(rejection.values()),
            'no_native_or_gas_advances':hi['native_runs']==lo['native_runs']==hi['new_gas_steps']==lo['new_gas_steps']==0}
    # The independent formal-polynomial packet has its own exact checks and
    # explicit status. Preserve its original structure and status in the report.
    result={'task':'E13C2_RESEARCH_VERIFICATION','checks':checks,
            'rtol_pair_max_over_old_algebraic_TOL':maxpair,
            'independent_oracle_max_absolute_P_A':maxn,
            'independent_oracle_max_absolute_B_eV':maxb,
            'oracle_degree_difference_number':str(max(Decimal(x['max_abs_degree_difference_number']) for x in oracle['results'])),
            'oracle_degree_difference_energy_eV':str(max(Decimal(x['max_abs_degree_difference_energy_eV']) for x in oracle['results'])),
            'rows':rows,'controls':controls,'rejections':rejection,
            'symbolic_verification':symbolic,
            'validation_scope':'finite specified six paths and six local controls; not enclosure or physical accuracy admission',
            'verdict':'PASS_SCOPED' if all(checks.values()) else 'FAIL'}
    output=Path(output)
    if output.exists():raise FileExistsError('refusing to overwrite prior verification result')
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('rows','controls','symbolic_verification')}))
    if result['verdict']!='PASS_SCOPED':raise SystemExit(1)
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args()
    run(args.root,args.output)
