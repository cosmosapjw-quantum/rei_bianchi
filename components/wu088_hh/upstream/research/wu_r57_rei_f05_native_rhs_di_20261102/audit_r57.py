#!/usr/bin/env python3
"""Same-author disjoint formula/byte audit of original 184,320 REI RHS rows
and newly evolved 46,080 WU R57 D histories. No R57 production-module import.
"""
from pathlib import Path
import csv,gzip,json,math,hashlib
HERE=Path(__file__).resolve().parent
ORIGINAL=Path("/home/cosmosapjw/archives/rei_f05_owner_accepted_trajectory_rhs_20261102/private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz")
NEW=HERE/"source_private/ORIGINAL_F05_4EPOCH_46080_26EVENT_RHS.csv.gz"
N=46080;ETA=2.5e-5;KB=1.380649e-16

def sha(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()
def require(p,msg):
    if not p:raise AssertionError(msg)

def audit():
    science=json.loads((HERE/"results/R57_RESULTS.json").read_text())
    require(science["original_rei_tick161"]=="HOLD","PREMATURE_TICK161")
    require(science["DAG"]=={"WU":"34/49","REI_CENTRAL":"28/88","REI_WORKING":"33/88","FAST":"4/7","canonical_delta":0},"FALSE_CANONICAL_NODE")
    require(sha(ORIGINAL)==science["source_original_REI367_20field_private_sha256"],"SOURCE_ORIGINAL_REI367_SHA")
    require(sha(NEW)==science["new_source_original_derivative_27field_sha256"],"SOURCE_EXTENDED_REI367_SHA")
    n=0;maxe=0.;maxT=0.;maxH=0.;maxpop=0.
    with gzip.open(ORIGINAL,"rt") as a,gzip.open(NEW,"rt") as b:
        before=csv.DictReader(a);now=csv.DictReader(b)
        require(now.fieldnames[:20]==before.fieldnames,"FIRST_20_COLUMNS_CHANGED")
        for old,new in zip(before,now,strict=True):
            i=int(new["node"]);tick=int(new["accepted_tick"])
            require(i==n%N and tick==(0,64,128,160)[n//N],"ORIGINAL_SOURCE_ROW_ORDER")
            for k in before.fieldnames:require(new[k]==old[k],"SOURCE_26EVENT_FIELD_CHANGED_"+k)
            ne=float(new["N_e"]);nh=float(new["N_H"]);he=float(new["N_He"])
            HII=float(new["N_HII_point"]);II=float(new["N_HeII_point"]);III=float(new["N_HeIII_point"])
            require(0<HII<nh and 0<II and 0<III and 0<he-II-III,"NATIVE_HHE_POPULATION")
            maxpop=max(maxpop,abs((HII+II+2*III)-ne)/max(ne,1e-290))
            dne=float(new["dN_e_dt_per_s"])
            alt=math.fsum([float(new["dN_HII_dt_per_s"]),float(new["dN_HeII_dt_per_s"]),2*float(new["dN_HeIII_dt_per_s"])])
            maxe=max(maxe,abs(alt-dne)/max(abs(dne),abs(alt),1e-250))
            T=float(new["T_K"]);Udot=float(new["Udot_thermochemical_erg_s"])
            ln=Udot/(1.5*KB*(nh+he+ne)*T)-dne/(nh+he+ne)
            direct=float(new["dlogT_dt_per_s"])
            maxT=max(maxT,abs(ln-direct)/max(abs(ln),abs(direct),1e-120))
            n+=1
    require(n==184320 and maxe<5e-13 and maxT<5e-12 and maxpop<1e-12,"SOURCE_NATIVE_RHS_IDENTITY")
    f=HERE/"results"/science["files"]["physical_full"]
    require(sha(f)==science["files"]["sha256"],"R57_PHYSICAL_FULL_SHA")
    scenarios=science["results"]
    counts={k:[] for k in scenarios}
    n=0;nonpositive=0
    with gzip.open(f,"rt") as z:
        rows=csv.DictReader(z)
        for r in rows:
            require(int(r["node"])==n,"R57_CELL_ROW_ORDER")
            NH=float(r["original_H_nuclei"])
            require(NH>0,"NATIVE_H_NUCLEI")
            for label in scenarios:
                y=float(r[label+"_DII_tick160"])
                y1=float(r[label+"_DII_tick161"])
                if not(0<=y<=1 and 0<=y1<=1):nonpositive+=1
                p=float(r[label+"_DI_gross_photo_per_D_160to161"])
                q=float(r[label+"_DI_gross_photoheat_erg_per_H_160to161"])
                require(p>=0 and q>=0,"UNPHYSICAL_GROSS_PHOTON_OR_HEAT")
                counts[label].append(ETA*NH*p)
            n+=1
    require(n==N and nonpositive==0,"R57_D_CONE")
    err={}
    for label,values in counts.items():
        got=math.fsum(values)
        expected=scenarios[label]["first_tick_gross_photons_total"]
        err[label]=abs(got-expected)/max(expected,1.)
        require(err[label]<5e-12,"GROUP_GROSS_PHOTON_SUM_"+label)
        s=scenarios[label]
        require(s["max_photon_conservation_residual_rel"]<5e-11 and s["max_full_population_ledger"]<1e-11,"R57_PHOTON_OR_5FLUX_LEDGER")
    result={
        "schema":"WU_R57_SAME_AUTHOR_DISJOINT_REI367_SOURCE_AND_46080_PHYSICAL_DATA_AUDIT",
        "original_source_rows":184320,"original_source_first_20_columns_byte_content_equal":True,
        "original_source_native_electron_identity_max_rel":maxe,
        "original_source_native_thermal_logT_identity_max_rel":maxT,
        "original_source_native_charge_state_identity_max_rel":maxpop,
        "R57_full_physical_cells":n,
        "R57_DI_positive_cone_violations":nonpositive,
        "first_tick_photons_independent_all_cell_recount_rel":err,
        "original_26event_continuous_history":"NOT_RUN",
        "original_tick161":"HOLD",
        "same_author":True,"native_subagent":"NOT_RUN",
        "verdict":"PASS_SCOPED_SOURCE_NATIVE_ENDPOINT_RHS_AND_CONDITIONAL_D_MEMORY"}
    out=HERE/"results/R57_INDEPENDENT_AUDIT.json"
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,sort_keys=True))
    return result
if __name__=="__main__":audit()
