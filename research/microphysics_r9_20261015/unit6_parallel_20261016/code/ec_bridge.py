"""Conditional nine-population Be7 electron-capture kernel and 22-state adapter.

No charge evolution, shakeoff kernel, plasma rate, cosmological clock, or heat
partition is inferred. Frozen supplied hazards are an external reservoir model.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import platform
import re
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[1]
DONOR_ORIGINAL=Path("/workspace/scratch/37bc4acea758/REI_R9_NCP_HANDOFF_20261016/unit2/bridge_code/inputs/R5_DONOR_BBN.json")
DONOR_PACKAGED=ROOT/"inputs/laneC/R5_DONOR_BBN.json"
DONOR_SHA256="47f93645a4c4fbcba0a6c3d1a9f8290adf847f011ab04d29b448633ec8525417"
SOURCE_COMMIT="4bf97d5082eee54b9df50d88f43182bb651fea80"
BE_ORDER=[f"Be7_{q}" for q in range(5)]
LI_ORDER=[f"Li7_{q}" for q in range(4)]
LIMITATIONS=["no spectator shakeoff; charge bins do not assert daughter electronic ground states",
             "prescribed continuum density is separate from the signed electron ledger",
             "no self-consistent recombination, charge evolution, or cosmological time history",
             "no native17 implementation; 17 existing states plus five auxiliary Be states",
             "no physical heat without electronic energies and neutrino/radiative/recoil partition"]


def _scalar(value,name):
    a=np.asarray(value)
    if a.ndim!=0 or a.dtype.kind not in "fiu" or not np.isfinite(a) or a<0:
        raise ValueError(f"{name} must be finite nonnegative real")
    return float(a)


def _vector(value,length,name):
    a=np.asarray(value)
    if a.shape!=(length,) or a.dtype.kind not in "fiu":
        raise ValueError(f"{name} must have length {length} and real numeric entries")
    a=np.asarray(a,dtype=np.float64)
    if not np.isfinite(a).all() or (a<0).any():
        raise ValueError(f"{name} must be finite nonnegative; no clipping")
    return a.copy()


def _hazards(bound,continuum):
    b=_vector(bound,5,"bound hazards")
    c=_vector(continuum,5,"continuum hazards")
    if b[4]!=0:raise ValueError("NO_BOUND_ELECTRON: bound q4 is forbidden")
    if c[0]!=0:raise ValueError("EXCLUDED_CHANNEL_LI_MINUS: continuum q0 is excluded")
    total=b+c
    if not np.isfinite(total).all():raise ValueError("total hazard must remain finite")
    return b,c,total


def prescribed_continuum_hazard(kappa_m3_s,n_e_m3):
    """Return n_e*kappa with explicit prescribed-density provenance."""
    kappa=_vector(kappa_m3_s,5,"kappa_m3_s")
    density=_scalar(n_e_m3,"prescribed n_e_m3")
    c=kappa*density
    if not np.isfinite(c).all():raise ValueError("prescribed continuum hazard must remain finite")
    if c[0]!=0:raise ValueError("EXCLUDED_CHANNEL_LI_MINUS: continuum q0 is excluded")
    return c,{"n_e_m3":density,"kappa_units":"m3/s","hazard_units":"s^-1",
              "closure":"prescribed reservoir-driven density, not dynamically closed electron density"}


def ledgers(be,li,free):
    be=np.asarray(be);li=np.asarray(li)
    B=float(math.fsum(be));L=float(math.fsum(li))
    nuclei=B+L
    bound=float(np.arange(4,-1,-1)@be+np.arange(3,-1,-1)@li)
    ionic=float(np.arange(5)@be+np.arange(4)@li)
    nuclear=4*B+3*L
    return {"Be_total":B,"Li_total":L,"nuclei":nuclei,"baryons":7*nuclei,
            "bound_electrons":bound,"free_electrons":float(free),"nuclear_charge":nuclear,
            "ionic_charge":ionic,"net_charge":ionic-float(free)}


def apply_event_counts(be,li,electron_ledger,bound_counts,continuum_counts):
    """Apply no-shakeoff events, preserving explicit signed electron deltas."""
    be=_vector(be,5,"be");li=_vector(li,4,"li")
    free=_scalar(electron_ledger,"electron_ledger")
    cb=_vector(bound_counts,5,"bound_counts")
    cc=_vector(continuum_counts,5,"continuum_counts")
    if cb[4]!=0:raise ValueError("NO_BOUND_ELECTRON: bound q4 is forbidden")
    if cc[0]!=0:raise ValueError("EXCLUDED_CHANNEL_LI_MINUS: continuum q0 is excluded")
    decayed=cb+cc
    if np.any(decayed>be):raise ValueError("PARENT_BUDGET_EXCEEDED")
    Cb=float(math.fsum(cb));Cc=float(math.fsum(cc));count=Cb+Cc
    electron_tol=1e-12*max(free,Cc)+1e-25
    if Cc-free>electron_tol:raise ValueError("ELECTRON_BUDGET_EXCEEDED: no implicit replenishment")
    final_be=be-decayed
    final_li=li+cb[:4]+cc[1:]
    final_free=free-Cc
    before=ledgers(be,li,free);after=ledgers(final_be,final_li,final_free)
    delta={"free_electrons":-Cc,"bound_electrons":-Cb,"nuclear_charge":-count,
           "ionic_charge":-Cc,"nuclei":0.,"baryons":0.,"net_charge":0.,
           "emitted_neutrinos":count,"electron_plus_neutrino_lepton":0.}
    residuals={name:after[name]-before[name]-delta[name] for name in
               ("free_electrons","bound_electrons","nuclear_charge","ionic_charge","nuclei","baryons","net_charge")}
    return {"be":final_be,"li":final_li,"electron_ledger":final_free,
            "bound_counts":cb,"continuum_counts":cc,"total_bound_count":Cb,"total_continuum_count":Cc,
            "delta_free":-Cc,"delta_bound":-Cb,"delta_nuclear_Z":-count,"delta_ionic_charge":-Cc,
            "delta_A":0.,"delta_nuclei":0.,"emitted_neutrinos":count,
            "ledgers_before":before,"ledgers_after":after,"signed_rewards":delta,"ledger_residuals":residuals,
            "electron_budget_tolerance":electron_tol,"electron_budget_raw_negative":final_free<0,
            "heat":None,"heat_status":"NEEDS_ENERGY_PARTITION","limitations":LIMITATIONS}


def frozen_hazard_step(be,li,electron_ledger,bound_s1,continuum_s1,dt_s):
    be=_vector(be,5,"be")
    li=_vector(li,4,"li")
    free=_scalar(electron_ledger,"electron_ledger")
    dt=_scalar(dt_s,"dt_s")
    b,c,total=_hazards(bound_s1,continuum_s1)
    active=total>0
    decayed=np.zeros(5);cb=np.zeros(5);cc=np.zeros(5)
    with np.errstate(over="ignore"):
        decayed[active]=be[active]*(-np.expm1(-total[active]*dt))
    cb[active]=decayed[active]*(b[active]/total[active])
    cc[active]=decayed[active]*(c[active]/total[active])
    result=apply_event_counts(be,li,free,cb,cc)
    result.update({"dt_s":dt,"bound_s1":b,"continuum_s1":c,
                   "hazard_model":"frozen prescribed hazards, no charge exchange"})
    return result


def build_generator(bound_s1,continuum_s1):
    b,c,total=_hazards(bound_s1,continuum_s1)
    G=np.zeros((9,9))
    G[np.arange(5),np.arange(5)]=-total
    for q in range(4):G[5+q,q]+=b[q]
    for q in range(1,5):G[5+q-1,q]+=c[q]
    return G


def uniformization_step(be,li,bound_s1,continuum_s1,dt_s,tail_tolerance=1e-14):
    """Independent compensated Poisson evaluation of the nuclear generator.

    The returned positive omitted-tail bound includes all split intervals.
    No signed electron reward is hidden in this one-particle generator.
    """
    y=np.concatenate((_vector(be,5,"be"),_vector(li,4,"li")))
    dt=_scalar(dt_s,"dt_s")
    b,c,total=_hazards(bound_s1,continuum_s1)
    G=build_generator(b,c)
    nu=float(total.max())
    if nu==0 or dt==0:
        return y,{"nu_s1":nu,"splits":0,"terms_per_split":0,"omitted_tail_bound":0.,
                  "generator_column_sum_residual":float(np.max(np.abs(G.sum(axis=0)))),"minimum_population":float(y.min())}
    exposure=nu*dt
    if not np.isfinite(exposure):raise ValueError("uniformization exposure must remain finite")
    splits=max(1,math.ceil(exposure/10))
    mu=exposure/splits
    P=np.eye(9)+G/nu
    tolerance=float(tail_tolerance)/splits
    total_tail=0.;max_terms=0
    for _ in range(splits):
        term=y.copy();weight=math.exp(-mu)
        answer=weight*term
        compensation=np.zeros_like(y)
        k=0
        while True:
            next_weight=weight*mu/(k+1)
            # Once descending, geometric comparison bounds all omitted weights.
            tail=next_weight/(1-mu/(k+2)) if k+2>mu else math.inf
            if tail<=tolerance:break
            k+=1;weight=next_weight;term=P@term
            correction=weight*term-compensation
            updated=answer+correction
            compensation=(updated-answer)-correction
            answer=updated
        y=answer
        total_tail+=tail
        max_terms=max(max_terms,k+1)
    return y,{"nu_s1":nu,"splits":splits,"terms_per_split":max_terms,"omitted_tail_bound":total_tail,
              "generator_column_sum_residual":float(np.max(np.abs(G.sum(axis=0)))),
              "transition_column_sum_residual":float(np.max(np.abs(P.sum(axis=0)-1))),
              "minimum_transition_entry":float(P.min()),"minimum_population":float(y.min())}


def _az(nuclide):
    if nuclide=="n":return 1,0
    if nuclide=="p":return 1,1
    match=re.fullmatch(r"([A-Za-z]+)([0-9]+)",nuclide)
    charge={"H":1,"He":2,"Li":3,"Be":4,"B":5,"C":6,"N":7,"O":8,"F":9,"Ne":10,"Na":11}
    if match is None or match[1] not in charge:raise ValueError(f"unknown donor nuclide {nuclide}")
    return int(match[2]),charge[match[1]]


def donor_inventory(path=None):
    path=Path(path) if path is not None else (DONOR_PACKAGED if DONOR_PACKAGED.exists() else DONOR_ORIGINAL)
    raw=path.read_bytes()
    observed=hashlib.sha256(raw).hexdigest()
    if observed!=DONOR_SHA256:raise ValueError(f"IMMUTABLE_DONOR_SHA_MISMATCH: {observed}")
    donor=json.loads(raw)
    if donor["source_commit"]!=SOURCE_COMMIT:raise ValueError("DONOR_SOURCE_COMMIT_MISMATCH")
    Y=donor["result"]["Y_final"]
    x=.000210349192936
    assignments=[("n",[1.]),("p",[1-x,x]),("H2",[1-x,x]),("H3",[1-x,x]),
                 ("He3",[1.,0.,0.]),("He4",[1.,0.,0.]),("Li7",[0.,1.,0.,0.])]
    names=["n","H1_0","H1_1","D_0","D_1","T_0","T_1","He3_0","He3_1","He3_2",
           "He4_0","He4_1","He4_2",*LI_ORDER]
    tracked=[]
    for nuclide,fractions in assignments:
        A,Z=_az(nuclide)
        for q,fraction in enumerate(fractions):
            tracked.append({"state":names[len(tracked)],"nuclide":nuclide,"A":A,"Z":Z,"q":q,"Y":Y[nuclide]*fraction})
    original_excluded={k:v for k,v in Y.items() if k not in {name for name,_ in assignments}}
    excluded=dict(original_excluded)
    be_amount=excluded.pop("Be7")  # Move exactly once; all other excluded nuclides are retained.
    for q in range(5):tracked.append({"state":BE_ORDER[q],"nuclide":"Be7","A":7,"Z":4,"q":q,"Y":be_amount if q==4 else 0.})
    full_baryons=math.fsum(_az(k)[0]*v for k,v in Y.items())
    tracked_baryons=math.fsum(row["A"]*row["Y"] for row in tracked)
    excluded_baryons=math.fsum(_az(k)[0]*v for k,v in excluded.items())
    free=math.fsum(row["q"]*row["Y"] for row in tracked)
    bound=math.fsum((row["Z"]-row["q"])*row["Y"] for row in tracked)
    nuclear=math.fsum(row["Z"]*row["Y"] for row in tracked)
    return {"identity":{"read_path":str(path),"original_path":str(DONOR_ORIGINAL),"sha256":observed,
                        "expected_sha256":DONOR_SHA256,"source_commit":SOURCE_COMMIT,"name":donor["name"]},
            "endpoint":donor["endpoint"],"overlay":donor["change"],"original_Y_final":Y,
            "tracked22":tracked,"old_excluded":original_excluded,"excluded_after_Be_move":excluded,
            "Be_move_count":1,"tracked_population_count":22,"native17_claim":False,
            "generator_population_count":9,"full_baryons":full_baryons,"normalization_defect_unrepaired":full_baryons-1,
            "tracked_baryons":tracked_baryons,"excluded_baryons":excluded_baryons,
            "baryon_map_residual":tracked_baryons+excluded_baryons-full_baryons,
            "tracked_free_electrons":free,"tracked_bound_electrons":bound,"tracked_nuclear_charge":nuclear,
            "tracked_electron_closure_residual":free+bound-nuclear,
            "be":np.array([0.,0.,0.,0.,Y["Be7"]]),"li":np.array([0.,Y["Li7"],0.,0.]),
            "conditional_assignment":{"H_D_T_ionized_fraction":x,"He3_He4":"neutral","Li7":"singly ionized","Be7":"bare q4"},
            "heat":None,"heat_status":"NEEDS_ENERGY_PARTITION","limitations":LIMITATIONS}


def synthetic_energy_identity():
    return {"physical_input":False,"Q_nuc_eV":1000.,"Eel_parent_eV":-100.,"Eel_daughter_eV":-40.,
            "delta_Eel_eV":60.,"captured_continuum_K_eV":10.,"outgoing_total_eV":950.,
            "E_neutrino_eV":900.,"E_nonthermal_eV":40.,"delta_Uthermal_eV":0.,
            "outgoing_identity_residual_eV":950.-(1000.+10.-60.),
            "complete_identity_residual_eV":0.+60.+900.+40.-1000.,
            "note":"synthetic bookkeeping; outgoing remaining 10eV replaces captured thermal 10eV, not a Be energy prediction"}


def conditional_donor_report(path=None):
    inventory=donor_inventory(path)
    B=inventory["original_Y_final"]["Be7"];L=inventory["original_Y_final"]["Li7"]
    exposures=[]
    for channel,q in (("bound",3),("continuum",4)):
        for exposure in (0.,math.log(2),math.log(4),10.):
            be=np.zeros(5);be[q]=B
            b=np.zeros(5);c=np.zeros(5)
            (b if channel=="bound" else c)[q]=1.
            result=frozen_hazard_step(be,inventory["li"],1.,b,c,exposure)
            exposures.append({"channel":channel,"prepared_q":q,"exposure":exposure,"result":result,
                              "claim":"conditional charge preparation and exposure; no recombination or adopted continuum rate"})
    half_life_days=106.4
    rate=math.log(2)/(half_life_days*86400)
    anchors=[]
    for days in (106.4,212.8):
        be=np.zeros(5);be[3]=B
        b=np.zeros(5);b[3]=rate
        result=frozen_hazard_step(be,inventory["li"],1.,b,np.zeros(5),days*86400)
        anchors.append({"elapsed_days":days,"lambda_b3_s-1":rate,"result":result})
    return {"inventory":inventory,"exposure_families":exposures,"hydrogenic_clock":{
                "half_life_days":half_life_days,"anchors":anchors,
                "source":"Khatri-Sunyaev arXiv:1009.3932v2 section2 eqs3-4 and Fig2",
                "assumptions":"prepared Be3, fixed statistical hyperfine mixture; no charge exchange or continuum capture",
                "claim":"conditional elapsed time only; no cosmological epoch or universal all-charge rate"},
            "analytic_complete_limit":{"Be_total":0.,"Li_total":B+L,"mass7_baryons":7*(B+L),
                                       "Li_total_over_donor_p":(B+L)/inventory["original_Y_final"]["p"],
                                       "classification":"analytic infinite-exposure endpoint; not finite numeric infinity input"},
            "synthetic_energy":synthetic_energy_identity(),"heat":None,"heat_status":"NEEDS_ENERGY_PARTITION",
            "runtime":{"python":sys.version,"numpy":np.__version__,"platform":platform.platform(),
                       "requested_model":"gpt-6.1-sol","observed_runtime_model":"UNKNOWN"},
            "scientific_admission":"PENDING_INDEPENDENT_REVIEW","limitations":LIMITATIONS}


def json_ready(obj):
    if isinstance(obj,np.ndarray):return obj.tolist()
    if isinstance(obj,np.generic):return obj.item()
    if isinstance(obj,dict):return {key:json_ready(value) for key,value in obj.items()}
    if isinstance(obj,(list,tuple)):return [json_ready(value) for value in obj]
    return obj


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--donor",type=Path,default=DONOR_PACKAGED if DONOR_PACKAGED.exists() else DONOR_ORIGINAL)
    parser.add_argument("--out",type=Path,required=True)
    args=parser.parse_args(argv)
    if args.out.exists():parser.error("--out must be a new JSON file")
    result=conditional_donor_report(args.donor)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(json_ready(result),indent=2)+"\n")
    print(json.dumps({"output":str(args.out),"donor_sha256":DONOR_SHA256,"heat_status":"NEEDS_ENERGY_PARTITION"}))


if __name__=="__main__":main()
