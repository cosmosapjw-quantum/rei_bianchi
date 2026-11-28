from __future__ import annotations
import hashlib, importlib.util, json, math
from pathlib import Path
import numpy as np
from scipy.linalg import norm

EXPECTED='565a9ee6d831f5f9e3e69010270f5319aa3328432950efcfda81cfabf325c079'
TOL=1e-10

def _load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def analyze(input_path,r31z_source,r31aa_source):
    p=Path(input_path);raw=p.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=EXPECTED: raise ValueError('snapshot SHA mismatch')
    z=_load(r31z_source,'r31z_source_bound_for_r31ab')
    a=_load(r31aa_source,'r31aa_local_for_r31ab')
    with np.load(p,allow_pickle=False) as f:d={k:f[k] for k in f.files}
    v=float(d['velocity']);
    if not math.isfinite(v) or v<=0:raise ValueError('positive finite velocity required')
    T=4/v
    O=[np.array(d['z0_od_O'],complex),np.array(d['direct_O'][:47,47:],complex),np.array(d['z4_od_O'],complex)]
    dot=[np.array(d['z0_j_dotO'],complex),np.array(d['direct_dotO'][:47,47:],complex),np.array(d['z4_j_dotO'],complex)]
    Dc=[np.array(d['z0_od_D_col'],complex),np.array(d['direct_D'][:47,47:],complex),np.array(d['z4_od_D_col'],complex)]
    Dr=[np.array(d['z0_od_D_row'],complex),np.array(d['direct_D'][47:,:47],complex),np.array(d['z4_od_D_row'],complex)]
    K=[(c-r.conj().T)/2 for c,r in zip(Dc,Dr)]
    s=.25
    Og,dg=z.quintic_hermite(O,dot,T,s);Kg=z.quadratic_three_nodes(K,s);Dcg=dg/2+Kg;Drg=(dg/2-Kg).conj().T
    Ol,dl,Dcl,Drl,Kl=a.local_candidate(O,dot,K,T,s)
    sep={
      'O':float(norm(Og-Ol,2)),
      'dotO':float(norm(dg-dl,2)),
      'K':float(norm(Kg-Kl,2)),
      'Dcol':float(norm(Dcg-Dcl,2)),
      'Drow':float(norm(Drg-Drl,2)),
    }
    sep['Dmax']=max(sep['Dcol'],sep['Drow'])
    return {
      'schema':'WU088_R31AB_Z1_INFORMATION_V1',
      'input_sha256':EXPECTED,
      'z_a0':1.0,'time_ta':1/v,
      'models':['R31Z_GLOBAL_QUINTIC_O_QUADRATIC_K','R31AA_LOCAL_PIECEWISE_CUBIC_O_LINEAR_K'],
      'model_separation':sep,
      'truth_independent_half_gap_lower_bound':{
        'K':sep['K']/2,'Dcol':sep['Dcol']/2,'Drow':sep['Drow']/2,'Dmax':sep['Dmax']/2,
        'logic':'for any truth X, ||G-L|| <= ||G-X||+||L-X||, so at least one model error >= separation/2'
      },
      'comparison_tolerance':TOL,
      'separation_over_tolerance':{'K':sep['K']/TOL,'Dmax':sep['Dmax']/TOL},
      'information_verdict':'HIGH_DISCRIMINATION_EXPECTED',
      'existing_equivalent_z1_mixed_node':'NOT_FOUND_IN_PARENT_CP4_INVENTORY',
      'new_scientific_node_executed':False,
      'execution_authorized_here':False,
      'claim_ceiling':'model-separation analysis only; no prediction of which model will win'
    }

def main():
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path,required=True);ap.add_argument('--r31z',type=Path,required=True);ap.add_argument('--r31aa',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    if a.out.exists():raise FileExistsError(a.out)
    r=analyze(a.input,a.r31z,a.r31aa)
    a.out.write_text(json.dumps(r,indent=2,allow_nan=False)+'\n')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
