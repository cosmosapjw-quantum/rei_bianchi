"""Independent ODE angular/time convergence at source-grounded quadrupole ICs."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import numpy as np
from sigma_pi_coupled import SigmaPiScenario,historical_axis_ratio_to_sigma
from bass_hierarchy_transport import BASSQuadrupoleTransport


def main(scenario:Path,donor:Path,out:Path):
    m=SigmaPiScenario.from_locked_json(scenario,gas_case="donor",
                                       donor_path=donor)
    full=historical_axis_ratio_to_sigma(.01)[0]
    cases=[
        ("rad_seed_plus_no_shear",0.,0,.2,0.),
        ("rad_seed_minus_no_shear",0.,0,-.2,0.),
        ("matter_seed_no_shear",0.,0,0.,.5),
        ("both_seed_signed_plus",full,1,.2,.4),
        ("both_seed_signed_minus",full,-1,-.2,.4),
    ]
    reports=[]
    for label,sigma,eps,ar,am in cases:
        solutions=[]
        for nodes,rtol,atol,step in (
            (32,3e-9,3e-13,.03),
            (64,2e-10,1e-14,.015),
            (128,2e-12,1e-15,.0075),
        ):
            eq=BASSQuadrupoleTransport(m,sigma_ref=sigma,orientation=eps,
                   source_rad_amplitude=ar,source_matter_amplitude=am,
                   angular_n=nodes)
            sol=eq.evolution(rtol=rtol,atol=atol,max_step=step)
            e=eq.inspect(sol.t[-1],*sol.y[:2,-1])
            solutions.append({"nodes":nodes,"rtol":rtol,"atol":atol,
                "nfev":sol.nfev,"b":e.b,"s_per_H":e.shear_s_inv/e.H_s_inv,
                "Sigma":e.Sigma,"elapsed_s":float(sol.y[2,-1])})
        base=solutions[1]
        ref=solutions[2]
        errs={k:abs(base[k]-ref[k]) for k in ("b","s_per_H","Sigma","elapsed_s")}
        if errs["b"]>2e-10 or errs["Sigma"]>2e-10:
            raise AssertionError("unacceptable BASS seeded Einstein convergence")
        reports.append({"case":label,"initial":{"Sigma_ref":sigma,"orientation":eps,
            "A_rad":ar,"A_matter":am},"trials":solutions,
            "GL64_DOP853_vs_GL128_ref":errs,
            "allowed_eps_sigma":2e-10})
    payload={"schema":"rei.sigma_pi.BASS_initial_hierarchy_convergence.v1",
             "comparison_method":"GL32/64/128 and independently reduced ODE step+tol",
             "models":reports,"status":"PASS_SCOPED_LOCAL_INDEPENDENT_ANGULAR_TIME_CONVERGENCE"}
    out.write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"status":payload["status"],"cases":len(reports),
          "errors":[{"case":r["case"],"err":r["GL64_DOP853_vs_GL128_ref"]}
                    for r in reports]},indent=2))


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--scenario",type=Path,required=True)
    ap.add_argument("--donor",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    v=ap.parse_args()
    main(v.scenario,v.donor,v.output)
