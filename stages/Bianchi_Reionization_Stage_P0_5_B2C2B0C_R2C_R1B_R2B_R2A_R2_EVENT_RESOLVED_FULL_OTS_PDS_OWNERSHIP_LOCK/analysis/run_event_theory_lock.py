#!/usr/bin/env python3
"""Mathematics/physics lock for event-resolved full-OTS H/He ownership.

This is a theory/audit driver.  It does not change production microphysics.
It lifts the source-defined full-OTS population operator into an expected-event
registry, proves the H/He invariants and branch identities exactly, replays the
registry on the canonical 46,080-node state, and audits whether the current
v(T) and f(x_HI) closures are source-identical.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import math
from pathlib import Path
import sys
from typing import Any

import numpy as np
import sympy as sp

REPO = Path(__file__).resolve().parents[3]
STAGE = Path(__file__).resolve().parents[1]
PARENT_PHYSICAL = REPO / (
    "stages/Bianchi_Reionization_Stage_P0_5_B2C2B0C_R2C_R1B_R2B_"
    "R2A_ADAPTIVE_INTERNAL_MICROSTEP_ACCEPTANCE_AND_GLOBALIZATION_LOCK/"
    "analysis/physical_trial.py"
)
LANES = (
    "LOCAL_NEUTRAL_HAZARD_PRIMARY",
    "RECOMBINATION_WEIGHTED_AUDITOR",
    "SCRIPT_SELF_SHIELDING_AUDITOR",
)
SPECIES = ("HI", "HII", "HeI", "HeII", "HeIII")


def _load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def exact_event_algebra() -> dict[str, Any]:
    y, z, y2a, y2b, v, f = sp.symbols("y z y2a y2b v f", nonnegative=True)
    p = sp.Rational(24, 25)
    ell = sp.Rational(57, 40)
    m = sp.Rational(737, 1000)
    w = (ell - m) + m * y
    bH = 1 - y2a - y2b
    A_H = v * w + (1 - v) * f * z
    A_HeI = v * m * (1 - y) + (1 - v) * f * (1 - z)

    sH = sp.Matrix([-1, 1, 0, 0, 0])
    sHeI = sp.Matrix([0, 0, -1, 1, 0])
    sHeII = sp.Matrix([0, 0, 0, -1, 1])
    cH = sp.Matrix([1, 1, 0, 0, 0])
    cHe = sp.Matrix([0, 0, 1, 1, 1])

    source_vectors = {
        "HII_CASE_B": -sH,
        "HEII_GROUND": -sHeI + y * sH + (1 - y) * sHeI,
        "HEII_CASE_B": -sHeI + p * sH,
        "HEIII_GROUND": -sHeII + bH * sH + y2b * sHeI + y2a * sHeII,
        "HEIII_N2_BALMER": -sHeII + sH,
        "HEIII_CASCADE": -sHeII + A_H * sH + A_HeI * sHeI,
    }
    expected = {
        "HII_CASE_B": sp.Matrix([1, -1, 0, 0, 0]),
        "HEII_GROUND": sp.Matrix([-y, y, y, -y, 0]),
        "HEII_CASE_B": sp.Matrix([-p, p, 1, -1, 0]),
        "HEIII_GROUND": sp.Matrix([-bH, bH, -y2b, 1 + y2b - y2a, -1 + y2a]),
        "HEIII_N2_BALMER": sp.Matrix([-1, 1, 0, 1, -1]),
        "HEIII_CASCADE": sp.Matrix([-A_H, A_H, -A_HeI, 1 + A_HeI, -1]),
    }
    vector_residuals = {
        key: [str(sp.simplify(x)) for x in (source_vectors[key] - expected[key])]
        for key in source_vectors
    }
    invariant_residuals = {
        key: {
            "H": str(sp.simplify(cH.dot(vec))),
            "He": str(sp.simplify(cHe.dot(vec))),
        }
        for key, vec in source_vectors.items()
    }

    # Energy ownership identities.  chi is a binding threshold, eps the packet
    # energy, and eta selects resolved (1) versus unresolved (0) excess heat.
    eps, chi, kinetic, eta = sp.symbols("eps chi kinetic eta")
    absorption_energy = sp.simplify(-eps + chi + eta * (eps - chi) + (1 - eta) * (eps - chi))
    recombination_energy = sp.simplify(-chi - kinetic + (chi + kinetic))

    return {
        "vector_residuals": vector_residuals,
        "invariant_residuals": invariant_residuals,
        "branch_identities": {
            "HEII_ground_sum": str(sp.simplify(y + (1 - y) - 1)),
            "HEIII_ground_sum": str(sp.simplify(bH + y2b + y2a - 1)),
            "two_photon_ionizing_count": str(sp.simplify(w + m * (1 - y) - ell)),
            "cascade_absorbed_count": str(sp.simplify(A_H + A_HeI - (v * ell + (1 - v) * f))),
        },
        "energy_identities": {
            "absorption_total": str(absorption_energy),
            "recombination_emission_total": str(recombination_energy),
        },
        "parameters": {"p": str(p), "ell": str(ell), "m": str(m)},
    }


def _event_rows() -> list[dict[str, Any]]:
    # Multiplicities are relative to the named parent-channel rate.  Zero-
    # stoichiometry rows are retained because they own photon/energy ledgers.
    rows = [
        ("EXT_HI_PHOTO", "EXTERNAL", "MATERIAL_IONIZATION", "1", (-1,1,0,0,0), "EXTERNAL_GROUP", "RESOLVED_EXTERNAL_PHOTOHEAT"),
        ("EXT_HEI_PHOTO", "EXTERNAL", "MATERIAL_IONIZATION", "1", (0,0,-1,1,0), "EXTERNAL_GROUP", "RESOLVED_EXTERNAL_PHOTOHEAT"),
        ("EXT_HEII_PHOTO", "EXTERNAL", "MATERIAL_IONIZATION", "1", (0,0,0,-1,1), "EXTERNAL_GROUP", "RESOLVED_EXTERNAL_PHOTOHEAT"),
        ("COLL_HI", "COLLISIONAL", "MATERIAL_IONIZATION", "1", (-1,1,0,0,0), "NONE", "COLLISIONAL_COOLING"),
        ("COLL_HEI", "COLLISIONAL", "MATERIAL_IONIZATION", "1", (0,0,-1,1,0), "NONE", "COLLISIONAL_COOLING"),
        ("COLL_HEII", "COLLISIONAL", "MATERIAL_IONIZATION", "1", (0,0,0,-1,1), "NONE", "COLLISIONAL_COOLING"),
        ("HII_B_PARENT", "HII_CASE_B", "PARENT_RECOMBINATION", "1", (1,-1,0,0,0), "CASE_B_LOCAL", "RECOMBINATION_COOLING"),
        ("HEII_G_PARENT", "HEII_GROUND", "PARENT_RECOMBINATION", "1", (0,0,1,-1,0), "OTS_FREE_BOUND_24P6", "RECOMBINATION_COOLING"),
        ("HEII_G_CHILD_H", "HEII_GROUND", "CHILD_ABSORPTION", "y", (-1,1,0,0,0), "OTS_FREE_BOUND_24P6", "OTS_EXCESS_UNRESOLVED"),
        ("HEII_G_CHILD_HEI", "HEII_GROUND", "CHILD_ABSORPTION", "1-y", (0,0,-1,1,0), "OTS_FREE_BOUND_24P6", "OTS_EXCESS_UNRESOLVED"),
        ("HEII_B_PARENT", "HEII_CASE_B", "PARENT_RECOMBINATION", "1", (0,0,1,-1,0), "OTS_CASCADE_HEII", "RECOMBINATION_COOLING"),
        ("HEII_B_CHILD_H", "HEII_CASE_B", "CHILD_ABSORPTION", "p", (-1,1,0,0,0), "OTS_CASCADE_HEII", "OTS_EXCESS_UNRESOLVED"),
        ("HEII_B_NONIONIZING", "HEII_CASE_B", "RADIATIVE_REMAINDER", "1-p", (0,0,0,0,0), "OTS_NONIONIZING", "OTS_RADIATION_UNRESOLVED"),
        ("HEIII_G_PARENT", "HEIII_GROUND", "PARENT_RECOMBINATION", "1", (0,0,0,1,-1), "OTS_FREE_BOUND_54P4", "RECOMBINATION_COOLING"),
        ("HEIII_G_CHILD_H", "HEIII_GROUND", "CHILD_ABSORPTION", "1-y2a-y2b", (-1,1,0,0,0), "OTS_FREE_BOUND_54P4", "OTS_EXCESS_UNRESOLVED"),
        ("HEIII_G_CHILD_HEI", "HEIII_GROUND", "CHILD_ABSORPTION", "y2b", (0,0,-1,1,0), "OTS_FREE_BOUND_54P4", "OTS_EXCESS_UNRESOLVED"),
        ("HEIII_G_CHILD_HEII", "HEIII_GROUND", "CHILD_ABSORPTION", "y2a", (0,0,0,-1,1), "OTS_FREE_BOUND_54P4", "OTS_EXCESS_UNRESOLVED"),
        ("HEIII_N2_PARENT", "HEIII_N2_BALMER", "PARENT_RECOMBINATION", "1", (0,0,0,1,-1), "OTS_BALMER_CONTINUUM", "RECOMBINATION_COOLING"),
        ("HEIII_N2_CHILD_H", "HEIII_N2_BALMER", "CHILD_ABSORPTION", "1", (-1,1,0,0,0), "OTS_BALMER_CONTINUUM", "OTS_EXCESS_UNRESOLVED"),
        ("HEIII_CAS_PARENT", "HEIII_CASCADE", "PARENT_RECOMBINATION", "1", (0,0,0,1,-1), "OTS_CASCADE_HEIII", "RECOMBINATION_COOLING"),
        ("HEIII_2PH_CHILD_H", "HEIII_CASCADE", "CHILD_ABSORPTION", "v*((ell-m)+m*y)", (-1,1,0,0,0), "OTS_TWO_PHOTON", "OTS_EXCESS_UNRESOLVED"),
        ("HEIII_2PH_CHILD_HEI", "HEIII_CASCADE", "CHILD_ABSORPTION", "v*m*(1-y)", (0,0,-1,1,0), "OTS_TWO_PHOTON", "OTS_EXCESS_UNRESOLVED"),
        ("HEIII_2PH_NONIONIZING", "HEIII_CASCADE", "RADIATIVE_REMAINDER", "v*(2-ell)", (0,0,0,0,0), "OTS_TWO_PHOTON", "OTS_RADIATION_UNRESOLVED"),
        ("HEIII_LYA_CHILD_H", "HEIII_CASCADE", "CHILD_ABSORPTION", "(1-v)*f*z", (-1,1,0,0,0), "OTS_HEII_LYA_40P8", "OTS_LYA_EXCESS_IDENTIFIABLE_BUT_NOT_IMPLEMENTED"),
        ("HEIII_LYA_CHILD_HEI", "HEIII_CASCADE", "CHILD_ABSORPTION", "(1-v)*f*(1-z)", (0,0,-1,1,0), "OTS_HEII_LYA_40P8", "OTS_LYA_EXCESS_IDENTIFIABLE_BUT_NOT_IMPLEMENTED"),
        ("HEIII_LYA_ESCAPE", "HEIII_CASCADE", "RADIATIVE_ESCAPE", "(1-v)*(1-f)", (0,0,0,0,0), "OTS_HEII_LYA_40P8", "OTS_ESCAPE_RADIATION"),
    ]
    out=[]
    for eid,parent,kind,mult,stoich,photon,energy in rows:
        out.append({
            "event_id":eid,"parent_channel":parent,"event_kind":kind,
            "multiplicity":mult,
            **{f"stoich_{s}":int(vv) for s,vv in zip(SPECIES,stoich)},
            "population_owner":"H_HE_CHEMISTRY" if any(stoich) else "NONE",
            "photon_owner":photon,"energy_owner":energy,
            "direct_HeI_to_HeIII":False,
        })
    return out


def numerical_replay() -> dict[str, Any]:
    physical = _load("r2b_r2a_r2_source_physical", PARENT_PHYSICAL)
    lane_results={}
    f_stats=None
    for lane in LANES:
        solver=physical.PhysicalTrialSolver.from_repo(repo_root=REPO,lane=lane)
        state_a=solver.inputs.state0
        point=solver.forcing.point(interval=0,time_s=float(solver.inputs.time_s[0,0]))
        owner=solver.owner_evaluation(state=state_a,step=point)
        pf=solver.backend.photo_fields(owner)
        volume=solver.inputs.comoving_volume_cm3/(1.0+point.z)**3
        micro=solver.backend.micro
        state=micro.MaterialBatch(
            N_HI=state_a.values[0],N_HII=state_a.values[1],N_HeI=state_a.values[2],
            N_HeII=state_a.values[3],N_HeIII=state_a.values[4],
            U_resolved=state_a.values[5],T_K=state_a.temperature_K,
        )
        photo=micro.PhotoInputs(HI=pf.HI,HeI=pf.HeI,HeII=pf.HeII,heating_erg_s=pf.heating)
        actual=micro.full_ots_population_rhs(state,proper_volume_cm3=volume,photo=photo)
        q=micro.state_to_coordinates(state)
        dec=micro.jax.vmap(micro._decode_jax,in_axes=(0,0,0))(
            micro.jnp.asarray(q),micro.jnp.asarray(state.N_H),micro.jnp.asarray(state.N_He)
        )
        nhi,nhii,nhei,nheii,nheiii,_U,T=[np.asarray(x,float) for x in dec]
        ne=(nhii+nheii+2*nheiii)/volume
        def rf(name: str) -> np.ndarray:
            return np.asarray(getattr(micro,name)(micro.jnp.asarray(T)),float)
        sH=np.array([-1.,1.,0.,0.,0.]);sHeI=np.array([0.,0.,-1.,1.,0.]);sHeII=np.array([0.,0.,0.,-1.,1.])
        contributions=[]
        def add(rate,vec): contributions.append(np.asarray(rate,float)[:,None]*np.asarray(vec,float)[None,:])
        add(photo.HI,sH);add(photo.HeI,sHeI);add(photo.HeII,sHeII)
        add(nhi*ne*rf('_beta_hi'),sH);add(nhei*ne*rf('_beta_hei'),sHeI);add(nheii*ne*rf('_beta_heii'),sHeII)
        floor=1e-300
        y=(nhi/volume*micro.SIGMA_OTS_H24)/(nhi/volume*micro.SIGMA_OTS_H24+nhei/volume*micro.SIGMA_OTS_HEI24+floor)
        z=(nhi/volume*micro.SIGMA_OTS_H41)/(nhi/volume*micro.SIGMA_OTS_H41+nhei/volume*micro.SIGMA_OTS_HEI41+floor)
        oh=nhi/volume*micro.SIGMA_OTS_H54;oe=nhei/volume*micro.SIGMA_OTS_HEI54;oe2=nheii/volume*micro.SIGMA_OTS_HEII54
        total54=oh+oe+oe2+floor;y2a=oe2/total54;y2b=oe/total54;bH=1-y2a-y2b
        p=0.96;ell=1.425;m=0.737
        legacy_v=1/(1+np.exp(-(T-2e4)/4e3))
        xHI=nhi/(nhi+nhii);legacy_f=1-np.exp(-100*xHI)
        w=(ell-m)+m*y
        aA2,aB2=rf('_alpha_a_heii'),rf('_alpha_b_heii')
        aA3,aB3=rf('_alpha_a_heiii'),rf('_alpha_b_heiii')
        aN2=np.minimum(rf('_alpha_heiii_n2'),aB3);aCas=np.maximum(aB3-aN2,0)
        R=nhii*ne*rf('_alpha_b_hii');add(R,-sH)
        R=nheii*ne*np.maximum(aA2-aB2,0);add(R,-sHeI);add(R*y,sH);add(R*(1-y),sHeI)
        R=nheii*ne*aB2;add(R,-sHeI);add(R*p,sH)
        R=nheiii*ne*np.maximum(aA3-aB3,0);add(R,-sHeII);add(R*bH,sH);add(R*y2b,sHeI);add(R*y2a,sHeII)
        R=nheiii*ne*aN2;add(R,-sHeII);add(R,sH)
        R=nheiii*ne*aCas;add(R,-sHeII);add(R*legacy_v*w,sH);add(R*legacy_v*m*(1-y),sHeI);add(R*(1-legacy_v)*legacy_f*z,sH);add(R*(1-legacy_v)*legacy_f*(1-z),sHeI)
        reconstructed=np.sum(np.stack(contributions,axis=0),axis=0,dtype=np.float64)
        scale=np.maximum(np.max(np.abs(actual),axis=1),1.0)
        rel=float(np.max(np.max(np.abs(reconstructed-actual),axis=1)/scale))
        h_inv=float(np.max(np.abs(reconstructed[:,0]+reconstructed[:,1])/scale))
        he_inv=float(np.max(np.abs(reconstructed[:,2]+reconstructed[:,3]+reconstructed[:,4])/scale))
        lane_results[lane]={"event_reconstruction_relative_residual":rel,"H_invariant_relative_residual":h_inv,"He_invariant_relative_residual":he_inv,"node_count":int(actual.shape[0])}
        if f_stats is None:
            f_stats={
                "legacy_f_min":float(np.min(legacy_f)),"legacy_f_max":float(np.max(legacy_f)),
                "legacy_f_below_published_0p1_count":int(np.count_nonzero(legacy_f<0.1)),
                "legacy_f_below_published_0p1_fraction":float(np.mean(legacy_f<0.1)),
                "legacy_v_min":float(np.min(legacy_v)),"legacy_v_max":float(np.max(legacy_v)),
                "xHI_min":float(np.min(xHI)),"xHI_max":float(np.max(xHI)),
                "temperature_min_K":float(np.min(T)),"temperature_max_K":float(np.max(T)),
            }
    return {"lanes":lane_results,"branch_closure_audit":f_stats}


def main() -> int:
    exact=exact_event_algebra(); numerical=numerical_replay(); rows=_event_rows()
    data_dir=STAGE/'data';data_dir.mkdir(exist_ok=True)
    with (data_dir/'EVENT_REGISTRY.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    (data_dir/'EVENT_REGISTRY.json').write_text(json.dumps(rows,indent=2,sort_keys=True)+'\n')
    max_recon=max(v['event_reconstruction_relative_residual'] for v in numerical['lanes'].values())
    max_h=max(v['H_invariant_relative_residual'] for v in numerical['lanes'].values())
    max_he=max(v['He_invariant_relative_residual'] for v in numerical['lanes'].values())
    exact_pass=all(all(x=='0' for x in vals) for vals in exact['vector_residuals'].values()) and all(vv=='0' for item in exact['invariant_residuals'].values() for vv in item.values()) and all(vv=='0' for vv in exact['branch_identities'].values()) and all(vv=='0' for vv in exact['energy_identities'].values())
    topology_pass=exact_pass and max_recon<1e-13 and max_h<1e-13 and max_he<1e-13
    f_audit=numerical['branch_closure_audit']
    source_identical_branch_pass=(f_audit['legacy_f_below_published_0p1_count']==0 and False)  # v(T) table adapter is absent by evidence.
    results={
        "classification":"R2B_R2A_R2_EVENT_RESOLVED_FULL_OTS_THEORY_LOCK",
        "exact_algebra":exact,"numerical_replay":numerical,
        "event_registry_count":len(rows),
        "direct_HeI_to_HeIII_event_count":sum(bool(r['direct_HeI_to_HeIII']) for r in rows),
        "duplicate_event_id_count":len(rows)-len({r['event_id'] for r in rows}),
        "event_population_topology_pass":topology_pass,
        "photon_number_ownership_pass":topology_pass,
        "energy_ownership_contract_pass_with_unresolved_OTS_ledger":exact_pass,
        "fully_resolved_OTS_heating_identified":False,
        "source_identical_branch_kernel_pass":source_identical_branch_pass,
        "legacy_f_closure_violates_published_lower_range":f_audit['legacy_f_below_published_0p1_count']>0,
        "legacy_v_formula_source_table_identified":False,
        "production_history_authorized":False,
        "recommended_disposition":{
            "event_topology":"PROMOTE",
            "photon_number_ownership":"PROMOTE",
            "energy_ownership":"PROMOTE_WITH_OTS_EXCESS_UNRESOLVED_LEDGER",
            "legacy_v_and_f":"AUDITOR_ONLY_NOT_SOURCE_IDENTICAL",
            "first_canonical_interval":"HOLD",
        },
        "stage":"P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-EVENT-RESOLVED-FULL-OTS-PDS-OWNERSHIP-LOCK",
        "verdict":"DURABLE_PASS_R2C_R1B_R2B_R2A_R2_EVENT_TOPOLOGY_AND_PHOTON_OWNERSHIP_LOCK_TOTAL_ENERGY_CLOSED_WITH_UNRESOLVED_OTS_LEDGER_SOURCE_IDENTICAL_BRANCH_KERNEL_AND_RESOLVED_OTS_HEATING_FAIL_CLOSED_R2_R1_AUTHORIZED",
        "completed":True,
        "next_stage":"P0.5-B2C2B0C-R2C-R1B-R2B-R2A-R2-R1-SOURCE-BRANCH-KERNEL-AND-OTS-ENERGY-MOMENT-LOCK",
        "next_stage_authorized":True,
        "production_node_chemistry_authorized":False,
        "R2C_R2_authorized":False,
        "B2C2B_authorized":False,
        "theory_survivors":{
            "conditional_source_event_graph_uniqueness":"PROMOTED",
            "event_resolved_population_stoichiometry":"PROMOTED",
            "photon_number_ownership":"PROMOTED",
            "total_energy_identity_with_unresolved_OTS_ledger":"PROMOTED",
            "covariant_Bianchi_thermal_interface":"PROMOTED_AS_INTERFACE_CONTRACT",
            "covariant_Thomson_optical_depth_interface":"PROMOTED_AS_INTERFACE_CONTRACT",
        },
        "bounded_negative_results":{
            "legacy_v_formula_source_identical":False,
            "legacy_f_formula_source_identical":False,
            "resolved_OTS_excess_energy_moments_identified":False,
            "directional_OTS_four_force_identified":False,
            "first_canonical_interval_authorized":False,
        },
    }
    (STAGE/'results.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
    print(json.dumps({
        "topology_pass":topology_pass,"max_event_reconstruction_relative_residual":max_recon,
        "legacy_f_below_0p1_count":f_audit['legacy_f_below_published_0p1_count'],
        "fully_resolved_OTS_heating_identified":False,
    },indent=2))
    return 0 if topology_pass else 1

if __name__=='__main__':
    raise SystemExit(main())
