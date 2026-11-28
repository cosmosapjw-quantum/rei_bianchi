"""Bounded algebraic control for PHYS78; no ODE or parameter sweep.

The input figure is a nuclear/atomic connectivity graph. Its ionic row placement
is not itself a charge-conserving reaction specification. Nuclear channels here
act on bare nuclei; beta decays keep pre-existing bound electrons and create one
free beta electron. No unprovided cross section or reaction rate is assigned.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np

NUCLIDES = (("H1",1,1),("D2",2,1),("T3",3,1),("He3",3,2),
            ("He4",4,2),("Li6",6,3),("Li7",7,3))

def make_registry():
    species = [{"id":"n","A":1,"Z":0,"q":0,"nuclide":"n"}]
    for name, mass, charge in NUCLIDES:
        species.extend({"id":f"{name}_{q}","A":mass,"Z":charge,"q":q,"nuclide":name}
                       for q in range(charge+1))
    species.append({"id":"e","A":0,"Z":0,"q":-1,"nuclide":None})
    return species

def make_channels():
    channels=[]
    def add(name,reactants,products,kind,figure_id=None):
        channels.append({"id":name,"reactants":reactants,"products":products,
                         "kind":kind,"figure_id":figure_id,"rate_status":"UNASSIGNED"})
    for name,_,charge in NUCLIDES:
        for q in range(charge):
            add(f"{name}_q{q}_photo",{f"{name}_{q}":1},{f"{name}_{q+1}":1,"e":1},"atomic_photo")
            add(f"{name}_q{q+1}_rr",{f"{name}_{q+1}":1,"e":1},{f"{name}_{q}":1},"atomic_rr")
    for fid,rea,prod in [
        (4,{"He4_2":1},{"He3_2":1,"n":1}),
        (5,{"He4_2":1},{"T3_1":1,"H1_1":1}),
        (6,{"He4_2":1},{"D2_1":2}),
        (7,{"He3_2":1},{"D2_1":1,"H1_1":1}),
        (8,{"D2_1":1},{"H1_1":1,"n":1}),
        (11,{"Li7_3":1},{"He4_2":1,"T3_1":1})]:
        add(f"figure_{fid}_photo",rea,prod,"nuclear_photo",fid)
    # A parent T ion with q charge has 1-q bound electrons; beta decay raises
    # nuclear Z by one and leaves them in the daughter, hence daughter q+1.
    for q in (0,1):
        add(f"figure_9_beta_T_q{q}",{f"T3_{q}":1},{f"He3_{q+1}":1,"e":1},"weak_beta",9)
    add("figure_10_beta_n",{"n":1},{"H1_1":1,"e":1},"weak_beta",10)
    for fid,rea,prod in [
        (12,{"H1_1":1,"n":1},{"D2_1":1}),
        (13,{"D2_1":1,"H1_1":1},{"He3_2":1}),
        (14,{"D2_1":2},{"T3_1":1,"H1_1":1}),
        (15,{"D2_1":2},{"He3_2":1,"n":1}),
        (16,{"T3_1":1,"D2_1":1},{"He4_2":1,"n":1}),
        (17,{"He3_2":1,"D2_1":1},{"He4_2":1,"H1_1":1}),
        (18,{"He3_2":1,"n":1},{"T3_1":1,"H1_1":1}),
        (19,{"T3_1":1,"He4_2":1},{"Li7_3":1})]:
        add(f"figure_{fid}",rea,prod,"nuclear_two_body",fid)
    return channels

def check():
    sp,ch=make_registry(),make_channels()
    ids={s["id"]:i for i,s in enumerate(sp)}
    stoich=np.zeros((len(sp),len(ch)),dtype=np.int64)
    for j,c in enumerate(ch):
        for k,n in c["products"].items():stoich[ids[k],j]+=n
        for k,n in c["reactants"].items():stoich[ids[k],j]-=n
    av=np.array([s["A"] for s in sp]);qv=np.array([s["q"] for s in sp]);zv=np.array([s["Z"] for s in sp])
    assert np.all(av@stoich==0),"baryon number defect"
    assert np.all(qv@stoich==0),"electric charge defect"
    atom=[j for j,c in enumerate(ch) if c["kind"].startswith("atomic")]
    for name,_,_ in NUCLIDES:
        marker=np.array([s["nuclide"]==name for s in sp],dtype=np.int64)
        assert np.all((marker@stoich)[atom]==0),f"{name} nuclear inventory changed by atomic channel"
    weak=[j for j,c in enumerate(ch) if c["kind"]=="weak_beta"]
    assert np.all((zv@stoich)[weak]==1),"beta changes nuclear charge by +1"
    assert np.all(stoich[ids["e"],weak]==1),"beta emits exactly one free electron"
    # Prescribed rate evaluations are unnecessary for this algebraic control.
    result={"status":"PASS_ALGEBRA_ONLY","species_count":len(sp),"channel_count":len(ch),
            "atomic_channel_count":len(atom),"weak_channel_count":len(weak),
            "max_baryon_defect":int(abs(av@stoich).max()),
            "max_charge_defect":int(abs(qv@stoich).max()),
            "new_ode_integrations":0,"benchmarks":0,
            "does_not_establish":"rate completeness, thermal closure, kinetic closure, or continuum error bounds"}
    root=Path(__file__).resolve().parent
    (root/"SPECIES_AND_CHANNELS.json").write_text(json.dumps({"species":sp,"channels":ch},indent=2)+"\n")
    (root/"STOICHIOMETRY_RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))

if __name__=="__main__":check()
