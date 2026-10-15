#!/usr/bin/env python3
"""Original REI PR136 BASS massless and nonrel massive source-moment adapter.

C13 source photons give an independent *additional* ionizing photon Pi_ion.
We explicitly call the pinned original PR136 BASSQuadrupoleTransport and verify
its baseline massless Pi agrees with the pinned PR135 CMB reference at the same
historical prescribed source b(a). The matter frozen-collisionless quadrupole
is a SEPARATE physics diagnostic, not the photoheated C13 gas pressure and
not a right to restart the original stress-free chemistry checkpoints.
"""
from __future__ import annotations
import sys,json,math
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import supplier_sigma_pi_PR135 as old
# Preserve PR136 original import without modifying its immutable copied bytes.
sys.modules.setdefault("sigma_pi_coupled",old)
import supplier_bass_hierarchy_PR136 as pr136
from short_interval import NativeStellarSource,Scenario,ROOT,Background,Family,run


def sample(q,steps=32,ar=0.,am=0.):
    m=Scenario(ROOT)
    src=NativeStellarSource.load(m,HERE/"NATIVE_SOURCE_8X8.csv")
    history=run(q,src,nstep=steps)
    end=history["end"]
    scen=old.SigmaPiScenario.from_locked_json(
       ROOT/"research/axbi_goal_20261014/scenario/SCENARIO_LOCK.json")
    amplitude,orientation=old.historical_axis_ratio_to_sigma(q)
    trans=pr136.BASSQuadrupoleTransport(
        scen,sigma_ref=amplitude,orientation=orientation,
        source_rad_amplitude=ar,source_matter_amplitude=am,
        geometry="prescribed_source",angular_n=64)
    bg=Background(Family(q))
    geo=bg.at_a(.2)
    initial_geo=bg.at_a(bg.aref)
    initial_Sigma,_=old.sigma_from_signed_axis(initial_geo["shear_s_per_s"],initial_geo["H_mean_per_s"])
    endpoint_Sigma,endpoint_orientation=old.sigma_from_signed_axis(geo["shear_s_per_s"],geo["H_mean_per_s"])
    eta=math.log(.2/scen.a_ref)
    radE,radPi,delta,press=trans.moments(eta,geo["b"])
    matterE,matterPi,matterP=trans.matter(eta,geo["b"])
    linRad,linMatter=trans.hierarchy_linearized_pi(eta,geo["b"])
    if ar==0.:
        denom=max(1e-35,abs(end["Pi_CMB_source_Pa"]))
        if abs(radPi-end["Pi_CMB_source_Pa"])/denom>2e-10:
            raise ValueError("PR136_BASS_BASELINE_CMB_STRESS_NOT_MATCHING_ORIGINAL_PR135")
    if (end["shear_orientation"]!=orientation or endpoint_orientation!=orientation
        or abs(initial_Sigma-amplitude)>1e-12
        or abs(end["Sigma"]-endpoint_Sigma)>1e-12):
        raise ValueError("HISTORICAL_INITIAL_SIGMA_VS_EVOLVED_ENDPOINT_CONTRACT")
    return {"q":q,"Sigma_ref":amplitude,"orientation":orientation,
            "Sigma_initial_from_BASS_clock":initial_Sigma,
            "C13_Sigma_at_z4":end["Sigma"],
            "PR136_amp_rad":ar,"PR136_amp_matter":am,
            "BASS_cmb_rad_energy_Pa":radE,"BASS_cmb_Pi_Pa":radPi,
            "BASS_massive_matter_Pi_Pa":matterPi,
            "BASS_massive_matter_energy_Pa":matterE,
            "BASS_massless_linearization_Pi_Pa":linRad,
            "BASS_matter_linearization_Pi_Pa":linMatter,
            "C13_ionizing_U_Pa":end["ion_rad_energy_Pa"] if "ion_rad_energy_Pa" in end else None,
            "C13_ionizing_Pi_Pa":end["Pi_ion_Pa"],
            "C13_ionizing_Pi_vs_CMB_Pi":abs(end["Pi_ion_Pa"])/abs(radPi) if radPi else None,
            "source_identity":trans.source_identity(),
            "science_boundary":"PR136 collisionless massive source is NOT C13 photoheated matter pi; NO Einstein feedback or native AX08 admission"}


def main():
    cases=[sample(q,32,0.,0.) for q in (-.01,0.,.01)]
    cases.append(sample(0.,32,.2,.4))
    out={"schema":"rei.c13.actual_pr136_bass_hierarchy_source_boundary.v1",
         "PR136_git_blob_sha1":"7abb53320534203715cd65d909cfa3764396e6d0",
         "PR135_git_blob_sha1":"c1f8c351a04891085fb6cfdc7fcb2956fa97c8da",
         "cases":cases}
    (HERE/"PR136_HIERARCHY_COUPLING.json").write_text(json.dumps(out,indent=2)+"\n")
    for c in cases:
        print("q",c["q"],"A",c["PR136_amp_rad"],c["PR136_amp_matter"],
              "Pi_rad",c["BASS_cmb_Pi_Pa"],"Pi_m",c["BASS_massive_matter_Pi_Pa"],
              "Pi_ion",c["C13_ionizing_Pi_Pa"])
    return out

if __name__=="__main__":main()
