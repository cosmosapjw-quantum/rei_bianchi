"""Nonlinear physical IC degeneracy in the original source-locked Einstein FV.

Exactly match ONE late scalar signed shear with distinct initial shear and
photon stress, then check whether late photon/quadrupole and geometry differ.
This is a physical forward-model degeneracy, NOT a posterior or observation.
"""
from __future__ import annotations
from pathlib import Path
import json,sys,time
from scipy.optimize import brentq
import numpy as np

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from response import one,BASE,source_lock,actual_electrons

def run(owner:Path,output:Path):
    if output.exists():raise FileExistsError(output)
    donor,donormeta=actual_electrons(owner)
    start=time.perf_counter()
    base=one(*BASE,donor=donor,n=121)
    shear_target=base["obs"][-1,0]
    q_new=5e-5
    def resid(kg):
        args=[q_new,kg,BASE[2],BASE[3]]
        return one(*args,donor=donor,n=121)["obs"][-1,0]-shear_target
    l,r=.10,.20
    if not(resid(l)<0 and resid(r)>0):
        raise ArithmeticError("PHYSICAL_GAMMA_KAPPA_ROOT_NOT_BRACKETED")
    kg_new=brentq(resid,l,r,xtol=1e-14)
    pert=one(q_new,kg_new,BASE[2],BASE[3],donor=donor,n=121)
    diff=pert["obs"]-base["obs"]
    assert abs(diff[-1,0])<3e-13
    assert abs(diff[-1,2])>1e-3
    assert abs(diff[-1,1])>1e-5
    assert pert["physical"]["min_massive_cell_number"]>=0
    contract={"schema":"rei.sigma_pi.nonlinear_fixed_shear_degeneracy.v1",
      "source_parent_sha":"54e29dff5a90c0a785cb6dcfb004403614ca403b",
      "electron_source_sha256":donormeta["history_sha256"],
      "physics":"non-tilted LRS Einstein Bianchi I; FD massive positive canonical FV; gamma/nu L8, electron Thomson gamma only from original frozen ZERO HHe",
      "baseline_IC":{"signed_q_ref":float(BASE[0]),"kappa_gamma":float(BASE[1]),
                    "kappa_nu":float(BASE[2]),"initial_A_massive":float(BASE[3])},
      "distinct_IC":{"signed_q_ref":q_new,"kappa_gamma":kg_new,
                    "kappa_nu":float(BASE[2]),"initial_A_massive":float(BASE[3])},
      "same_signed_s_over_H_at_z4":float(shear_target),
      "new_signed_s_over_H_at_z4":float(pert["obs"][-1,0]),
      "abs_match_error":float(abs(diff[-1,0])),
      "observables_end_delta":dict(zip(("signed_s_over_H","b","gamma_E2","nu_E2","massive_Pi_norm"),diff[-1].tolist())),
      "initial_pi":{"baseline":{k:v for k,v in base["physical"].items() if k.startswith("initial_")},
                    "distinct":{k:v for k,v in pert["physical"].items() if k.startswith("initial_")}},
      "max_history_delta_signed_s_over_H":float(np.max(abs(diff[:,0]))),
      "maximum_full_constraint_error":max(base["physical"]["Einstein_H2_constraint_max_relative"],
          pert["physical"]["Einstein_H2_constraint_max_relative"]),
      "source_initial_shear_sigma_user_definition":"Sigma=sqrt3 abs(s)/H, signed q stored separately",
      "statement":"same one endpoint scalar does not imply same physical solution, full angular moments distinguish",
      "observational_posterior":None,"full_ionizing_source_selfconsistent":False,
      "x":base["x"].tolist(),"base":base["obs"].tolist(),"distinct":pert["obs"].tolist(),
      "wall_time_s":time.perf_counter()-start}
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(contract,indent=2)+"\n")
    print(json.dumps({k:v for k,v in contract.items() if k not in ("x","base","distinct")},indent=2))
if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--owner",type=Path,required=True)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args();run(a.owner,a.output)
