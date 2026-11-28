"""Reproduce bounded first-panel diagnostics from immutable selected R10F bytes.

No dynamic Delta solve. No five-lane/Appendix-A scientific admission. An optional
new host rerun must be recorded as scoped numerical reproduction, not outcome-blind.
"""
import argparse,json,platform,hashlib
from pathlib import Path
import numpy as np
import scipy
from audit_support import frozen_components,original_adapter,BLOCKS
from eta_rotation import eta_rotation_batch,eta_dop853,velocity
from endpoint_quadrature import nodes,reduce,integrate_endpoint
ROOT=Path(__file__).resolve().parent


def run(out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    diag=json.loads((ROOT/'fixtures/FIXED_GK_DIAGNOSTIC.json').read_text())
    B=float.fromhex('0x1.05bbc59d8ffb1p-1');a=2/(.8*1836.153*float(velocity(5.))**2)
    hs=np.asarray(diag['interval_component_high_estimate'])[:,72:90]
    es=np.asarray(diag['interval_component_error_estimate'])[:,72:90]
    oldrho=np.sqrt(nodes(0.,B*B));old=frozen_components(oldrho,method='original',steps=1024)
    h,e=reduce(0.,B*B,np.pi*old)
    dh=float(np.max(abs(h-hs[0])));de=float(np.max(abs(e-es[0])))
    if max(dh,de)>1e-12:raise ArithmeticError('ARCHIVED_FIRST_PANEL_REPRODUCTION_FAILURE')
    overlaps=[]
    for E in (.5,5.):
        for N,l,_ in BLOCKS:
            for kind in ('CPC','AUTHOR'):
                cut=((l+.5)**2-(.5 if kind=='CPC' else 0))/3
                new=eta_rotation_batch(N,l,E,oldrho,R_cut=cut,steps=256)
                old=original_adapter()(N,l,E,oldrho,R_cut=cut,steps=1024)
                overlaps.append({'E':E,'N':N,'l':l,'cutoff':kind,'max_probability_difference':float(np.max(abs(new['P_abs']-old['P_abs'])))})
    pilot=integrate_endpoint(lambda r:frozen_components(r,method='eta',steps=256),
                            B=B,scale=a,tail=hs[1:].sum(0),tail_error=es[1:].sum(0))
    result={'scope':'ARCHIVED_FIRST_PANEL_FROZEN_DIAGNOSTIC_ONLY',
            'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__},
            'archive_first_panel_high_diff':dh,'archive_first_panel_error_diff':de,
            'old_first_panel_overlap':overlaps,'adaptive_frozen_pilot':pilot,
            'delta_calls':0,'old_outside_intervals_reused':16,'five_lane_integrals_admitted':False}
    (out/'ARCHIVED_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    if max(x['max_probability_difference'] for x in overlaps)>1e-8 or not pilot['converged']:
        raise ArithmeticError('R10G_ARCHIVED_OR_FROZEN_REVIEW_UNRESOLVED')
    print(json.dumps({'archive_high_diff':dh,'old_domain_max_representation_diff':max(x['max_probability_difference'] for x in overlaps),
                      'frozen_pilot_status':pilot['status'],'frozen_queries':pilot['evaluations'],'frozen_leaves':pilot['leaf_count']},indent=2))
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',default='audit_output');args=p.parse_args();run(args.out)
