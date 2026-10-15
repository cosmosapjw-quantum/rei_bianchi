"""Direct original BASS source oracle, not a paraphrased mock hierarchy.

Externally read byte-pinned BASS Lewis–Challinor hierarchy and Fermi-Dirac
Vlasov source in authorized local workspace. Compare exact original BASS
l=2,i=0 RHS, direct distribution exact finite-difference derivatives and
new generic scalar shear coefficient, for both massless and massive cases.

This validation depends on source commit 45f31b8e... and original source
files' actual byte hashes. Does not copy or mutate BASS code, and no native
subagents are simulated.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import sys
import warnings

import numpy as np

from bass_hierarchy_transport import bass_hierarchy_scalar_shear_coefficient

SOURCE_SHA={
    "bianchi/matter/hierarchy.py":
        "27f81acd681acc34537ad59ad2bec923d95c0adb7ac6d52413c4e3b2e0980aa6",
    "bianchi/matter/freestream.py":
        "b03aeed2cfcdaa5baf45fdab626941905674e2385bc06d1173a4b8c39ebf8bb4",
    "bianchi/matter/viscous_derived.py":
        "48f39a2266272e20b5a1a26f6ffedc1813e300d2b1f00a24a415c7e6902413bf",
}
RADIATION_NORMALIZATION_SHA="332da19ccd5a949ab712b29f3d0e8634bff1aa71f0385f26f952a922fd6d73f2"
DOSSIER_SHA="8e4a20c228cb4f6760d258b9ecafb142423a7140698d45871b0151593feef075"


def _hash_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_l2_check(bass_root:Path,mode_root:Path,dossier_pdf:Path):
    for src,digest in SOURCE_SHA.items():
        actual=_hash_file(bass_root/src)
        if actual!=digest:
            raise ValueError(f"BASS source byte identity drift: {src}: {actual}")
    if _hash_file(mode_root/"htt/bass/hierarchy/pstf_radiation.py")!=RADIATION_NORMALIZATION_SHA:
        raise ValueError("BASS radiative I2/pi normalization source drift")
    if _hash_file(dossier_pdf)!=DOSSIER_SHA:
        raise ValueError("BASS Kinetic Transport dossier source drift")
    sys.path.insert(0,str(bass_root))
    from bianchi.matter import hierarchy as H,freestream as FS

    zero=np.zeros((3,3))
    samples=[]
    a=np.array([1.,1.,1.])
    sh=.01
    sigma=np.diag([-sh,-sh,2*sh])

    for mass in (0.,1.,4.,20.,100.):
        j0=H.J_moment(a,mass,0,0,backend="python")
        j1=H.J_moment(a,mass,0,1,backend="python")
        j2=H.J_moment(a,mass,0,2,backend="python")
        j={(0,1):j1,(0,2):j2,(2,0):zero.copy(),(2,1):zero.copy(),
            (4,0):np.zeros((3,)*4)}
        rhs=H.hierarchy_rhs(j,0.,sigma,2,0)
        ratio=bass_hierarchy_scalar_shear_coefficient(j1,j2)
        ref=ratio*sigma
        if np.max(np.abs(rhs-ref))>8e-14*max(abs(rhs[2,2]),1):
            raise AssertionError("BASS l2 instantaneous source coefficient differs")
        samples.append({
            "mass_in_BASS_T1_units":mass,"rho":float(j0),
            "J0_1":float(j1),"J0_2":float(j2),
            "source_coefficient":float(ratio),
            "pi_zz_rhs_original":float(rhs[2,2]),
            "relative_to_nonrel_minus_2p":float(
                ratio/(-2*j1/3)) if j1 else None,
        })
    if abs(samples[0]["source_coefficient"]/samples[0]["rho"]+8/15)>4e-14:
        raise AssertionError("BASS massless Misner -8/15 coefficient invalid")
    if abs(samples[-1]["relative_to_nonrel_minus_2p"]-1)>1e-3:
        raise AssertionError("BASS large-mass -2p source limit invalid")

    differentials=[]
    for mass,amp in ((0.,.2),(4.,.25)):
        def quadrupolar_f0(q,nh):
            W=1+amp*.5*(3*nh[:,2]**2-1)
            return FS.f_fermi_dirac(q)[:,None]*W[None,:]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore",RuntimeWarning)
            j={}
            for l,indices in ((0,(1,2)),(2,(0,1)),(4,(0,))):
                for i in indices:
                    j[(l,i)]=H.J_moment(a,mass,l,i,quadrupolar_f0,
                                        backend="python")
            rhs=H.hierarchy_rhs(j,.5,sigma,2,0)
            exact=H.dJ_dt_exact(a,mass,2,0,.5,(-sh,-sh,2*sh),
                                dt=1e-5,f0=quadrupolar_f0)
            rho=H.J_moment(a,mass,0,0,quadrupolar_f0,backend="python")
        residual=float(np.max(np.abs(rhs-exact))/(rho*(.5+sh)))
        if residual>2e-8:
            raise AssertionError(f"full BASS tensor l2 RHS mismatch {mass}: {residual}")
        differentials.append({
            "mass_in_BASS_T1_units":mass,"quadrupole_seed_amplitude":amp,
            "rho":float(rho),
            "original_BASS_l2_rhs_zz":float(rhs[2,2]),
            "direct_Vlasov_fd_zz":float(exact[2,2]),
            "normalized_full_tensor_RHS_difference":residual,
        })

    return {
        "schema":"rei.sigma.pi.BASS_direct_hierarchy_oracle.v1",
        "BASS_source_files_sha256":SOURCE_SHA,
        "BASS_radiation_I2_pi_source_sha256":RADIATION_NORMALIZATION_SHA,
        "dossier_kinetic_PDF_sha256":DOSSIER_SHA,
        "derived_massless_source":"(2/15)*(J^(2)-5*J^(1))=-8*rho/15",
        "derived_nonrel_source":"mass large: -2p*sigma_ab, Pi_scalar_dot=-6p*s",
        "actual_original_source_scalar_cases":samples,
        "actual_original_source_anisotropic_l2_RHS_vs_full_direct_momentum_oracle":differentials,
        "status":"PASS_BASS_DIRECT_MASSLESS_AND_MASSIVE_L2_SOURCE_LIOUVILLE",
        "does_not_prove":"No coupled finite massive radial hierarchy time integration, thermal collision or full REI photon source.",
    }


if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--bass-root",required=True,type=Path)
    ap.add_argument("--htt-root",required=True,type=Path)
    ap.add_argument("--dossier-pdf",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    z=ap.parse_args()
    result=source_l2_check(z.bass_root,z.htt_root,z.dossier_pdf)
    z.output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({
        "status":result["status"],"masses":len(result["actual_original_source_scalar_cases"]),
        "anisotropic_source_comparisons":result["actual_original_source_anisotropic_l2_RHS_vs_full_direct_momentum_oracle"],
        "source_bass_SHA":result["BASS_source_files_sha256"]["bianchi/matter/hierarchy.py"]
    },indent=2))
