"""Bind original strong bulk + all five exact distributional interfaces to H^-1.

DO NOT mix normalized D residual and the physical Hamiltonian -Delta/2 without
the factor-two conversion. Domain is the truncated annulus r0<r<20, and the
dual is (H_0^1(annulus))*. No origin, exterior boundary, or inverse theorem.
"""
from __future__ import annotations
from fractions import Fraction as F
from pathlib import Path
import hashlib,json
from .phys33_coupled_source import outward_decimal

PHYS36_PARENT_SHA256="f2cc27a97153b233bda8ae3146dacc8575bf83ec4df59de00cbcb184f484f6d2"


def truncated_distribution_certificate(bulk_file:str|Path,
                                       interface_file:str|Path,
                                       decimals:int=15)->dict:
    parent=Path(bulk_file).read_bytes()
    if hashlib.sha256(parent).hexdigest()!=PHYS36_PARENT_SHA256:
        raise ValueError("whole broken-bulk parent SHA256 mismatch")
    p=json.loads(parent)
    q=json.loads(Path(interface_file).read_bytes())
    if q['schema']!="WU088_HH_PHYS38_ALL_INTERFACES_HMINUS1_V1" or len(q['interfaces'])!=5:
        raise ValueError("all original five radial interfaces are needed")
    if p['input_sha256']!=q['input_sha256']:
        raise ValueError("input identities disagree")
    if not all(z['field_value_jump_exact_zero'] for z in q['interfaces']):
        raise ValueError("uncontrolled value jumps create delta-prime")
    b=F(p['norm_upper']['screened_broken_bulk_admitted'])
    i=F(q['full_broken_Laplacian_distribution_Hminus1_upper'])
    if min(b,i)<0:
        raise ValueError("negative norm envelope")
    return {
      "schema":"WU088_HH_PHYS38_TRUNCATED_GLOBAL_HMINUS1_V1",
      "source_sha256":p['input_sha256'],
      "parent_PHYS36_sha256":PHYS36_PARENT_SHA256,
      "scientific_domain":"piecewise frozen r0=1e-4 through r=20, all angles",
      "test_space":"(H_0^1(annulus), dimensionless a0 gradient) dual",
      "bulk_L2_upper":str(b),
      "five_interface_Ddelta_Hminus1_upper":str(i),
      "truncated_full_transformed_PDE_Hminus1_upper":
           outward_decimal(b+i,decimals,True),
      "proof":"L2 embeds continuously into H-1 with constant1; piecewise H1 field "
              "is exactly continuous at all saved interfaces; distributional "
              "Laplacian adds only first-normal-derivative delta sheets; "
              "bounded screened first-order and potential terms create no delta",
      "not_claimed":["continuous outgoing inverse","r<r0 excluded origin",
         "physical outer boundary and higher angular truncation error",
         "certified scattering intensity or HH thermal rate"],
    }
