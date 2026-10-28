"""Bounded non-IVP source-rate response and pointwise support table."""
from pathlib import Path
import sys,json
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_response import *
ROOT=Path(__file__).resolve().parents[1]

def main():
    d,p,rows=load();geo=geometry(d)
    out=[]
    for zz in d['z']:
        z=float(zz);r=rate_response(z,geo['a0'],rows)
        det=pointwise_envelope(z,0.,geo,rows)
        scalar=pointwise_envelope(z,Q_SCALAR95,geo,rows)
        joint=pointwise_envelope(z,Q_JOINT2_95,geo,rows)
        out.append({'z':z,'P19_HI_s-1':float(r['p19'][0]),
                    'nominal_HI_s-1':float(r['moments'][0]),
                    'nominal_six_moments':r['moments'].tolist(),
                    'jac_HI_wrt_beta_kappa':r['jac'][0].tolist(),
                    'deterministic_logfactor':det['logfactor_dex'],
                    'scalar95_logfactor':scalar['logfactor_dex'],
                    'joint2_95_logfactor':joint['logfactor_dex'],
                    'deterministic_HI_rate':[float(det['moments_min'][0]),float(det['moments_max'][0])],
                    'scalar95_HI_rate':[float(scalar['moments_min'][0]),float(scalar['moments_max'][0])],
                    'joint2_95_HI_rate':[float(joint['moments_min'][0]),float(joint['moments_max'][0])]})
    result={'schema':'REI_UVB_SIX_MOMENT_RATE_RESPONSE_V1',
       'input':{'bb_sha256':BB_SHA,'p19_projection_sha256':P_SHA,
                'p19_original_git_blob':p['parent_git_blob'],
                'prior_pr260':'7438e2e85e8f0ecb03292558280521bbf58e707d'},
       'scope':'six physical-model H/He photoionization+heating moments, conditional fixed-template common beta/kappa rescaling, z2.4..4.75 only',
       'A':geo['A'].tolist(),'V':geo['V'].tolist(),
       'a0':geo['a0'].tolist(),'center':geo['center'].tolist(),
       'G':geo['G'].tolist(),'q_scalar95':Q_SCALAR95,'q_joint2_95':Q_JOINT2_95,
       'columns':list(FIELDS),'rows':out,
       'claim_gate':{'rate_port_jacobian':'NUMERICALLY_CHECKED_SCOPED',
         'physical_chemistry_state_response':None,'Thomson_tau_response':None,
         'observed_directional_redshift_map':None,'physical_density':None,
         'physical_mean_H':None,'actual_ionization_thresholds':None,
         'new_ivp':0,'F4':'PARTIAL','L4_ready':False,'native25':None,
         'original_working_DAG':'33/88','central_last_observed':'28/88',
         'original_DAG_delta':0}}
    path=ROOT/'results/RESULT.json'
    path.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'n':len(out),'HI_at_z3p6':out[3],
                      'A_identity_max':float(np.max(np.abs(geo['A']@geo['X']-np.eye(2))))},indent=2))
    return result
if __name__=='__main__':main()
