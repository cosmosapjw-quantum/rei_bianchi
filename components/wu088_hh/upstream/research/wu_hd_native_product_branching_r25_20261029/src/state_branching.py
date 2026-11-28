"""GL2022 Table 1-10, (v,J)=(0,2) -> H2(v'=0,J'=0..9).

Scientific status: source-native *printed SQM rates* only. The ten-state
product branching is CONDITIONAL on the ten published final channels.
No PES-native reaction Q, reaction heat, reverse or physical chemistry owner.
"""
from __future__ import annotations
import argparse
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

PDF_SHA = "a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754"
PDF_BYTES = 273554
SOURCE_DOI = "10.1063/5.0128598"
TEMPERATURES = (15, 55, 105, 255, 505, 1005, 1505, 2005, 2505, 3005)
TARGET_INITIAL = (0, 2)
TARGET_PRODUCTS = tuple(range(10))
PRINTED_ZERO = "0.00(00)"
EXPECTED_105_J1 = "1.15(10)"
SOURCE_STATUS = "PUBLISHED_GL2022_STATE_TO_STATE_SQM_PRINTED_NOMINAL"
EXPECTED_GRID_SHA256 = "f1b8e438a0117688e2497af1434227a42c8c158bab9f810b536b3ad2c36e4174"
CHANNEL = "H+ + HD(X,v=0,J=2) -> D+ + H2(X,v'=0,J'=0..9)"

class SourceError(ValueError):
    pass


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def extract_source_tokens(pdf: Path) -> tuple[tuple[str, ...], ...]:
    pdf = Path(pdf)
    if not pdf.is_file() or pdf.stat().st_size != PDF_BYTES or sha256(pdf) != PDF_SHA:
        raise SourceError("original GL2022 supplementary PDF bytes/SHA mismatch")
    if shutil.which("pdftotext") is None:
        raise SourceError("pdftotext -layout required for native-PDF readback")
    p = subprocess.run(["pdftotext", "-layout", str(pdf), "-"],
                       capture_output=True, text=True, check=True)
    text = p.stdout
    table_matches = list(re.finditer(r"\bTable\s+(\d+)\s*:", text))
    results = []
    for table in range(1, 11):
        headers = [m for m in table_matches if int(m.group(1)) == table]
        if len(headers) != 1:
            raise SourceError(f"Table {table} occurrence mismatch")
        m = headers[0]
        end = next((x.start() for x in table_matches if x.start()>m.end()), len(text))
        chunk = text[m.end():end]
        # Table caption plus correct state header is a separate source-identity check.
        if not re.search(r"\b15\s+55\s+105\s+255\s+505\s+1005\s+1505\s+2005\s+2505\s+3005\b",chunk):
            raise SourceError(f"Table {table} source temperature order mismatch")
        rows = re.findall(r"^\s*\(0\s*,\s*2\)\s+([^\n]+)",chunk,flags=re.M)
        if len(rows) != 1:
            raise SourceError(f"Table {table} (0,2) target row missing/duplicated")
        tokens = re.findall(r"(?<!\w)((?:\d+(?:\.\d*)?|\.\d+)\(\d{2}\))(?!\w)", rows[0])
        if len(tokens) != 10:
            raise SourceError(f"Table {table}: expected ten printed rates")
        results.append(tuple(tokens))
    if results[1][2] != EXPECTED_105_J1:
        raise SourceError("R18 105K J'=1 original-rate anchor mismatch")
    if tuple(results[j][0] for j in (6,7,8,9)) != (PRINTED_ZERO,)*4:
        raise SourceError("15K printed-zero provenance mismatch")
    return tuple(results)


def source_record(pdf: Path) -> dict:
    rows=extract_source_tokens(pdf)
    return {
        "schema":"wu.r25.gl2022_source_native_product_grid.v1",
        "channel":CHANNEL,
        "original_pdf_SHA256":PDF_SHA,"original_pdf_size":PDF_BYTES,
        "doi":SOURCE_DOI,"source_tables":"supplementary Table 1..10",
        "temperature_nodes_K":list(TEMPERATURES),
        "H2_product_J_list":list(TARGET_PRODUCTS),
        "tokens_by_product_J":[list(x) for x in rows],
        "printed_zero_semantics":"UNQUALIFIED_NOT_AUTHENTICATED_PHYSICAL_EXACT_ZERO",
        "rate_source_type":SOURCE_STATUS,"units":"cm^3/s (printed token m(ee) means m*10^(-ee))",
        "physical_rate_uncertainty":None,"source_native_PES_threshold":None,
        "physical_Q_J_per_event":None,"owner_ACK":None,
        "central_DAG":"34/49_UNCHANGED","R23_scoped_workflow":"18/20",
        "R6":"NOT_RUN","C9":"NOT_RUN","HH_R10":"OFF","L4":False,"production":"NOT_ISSUED","full_A":None
    }


def parse_rate(token: str) -> Decimal | None:
    m = re.fullmatch(r"(\d+(?:\.\d*)?|\.\d+)\((\d{2})\)", token)
    if not m:
        raise SourceError("malformed original exponent token")
    if token == PRINTED_ZERO:
        return None
    a,exp=Decimal(m.group(1)),int(m.group(2))
    if not a.is_finite() or a<=0:
        raise SourceError("nonpositive original state-rate token")
    return a*(Decimal(10)**(-exp))


def strict_source_record(obj:dict) -> tuple[tuple[str,...],...]:
    if not isinstance(obj,dict) or obj.get("schema")!="wu.r25.gl2022_source_native_product_grid.v1":
        raise SourceError("source schema mismatch")
    for k,v in (("doi",SOURCE_DOI),("original_pdf_SHA256",PDF_SHA),
                ("original_pdf_size",PDF_BYTES),("rate_source_type",SOURCE_STATUS),
                ("central_DAG","34/49_UNCHANGED"),("HH_R10","OFF"),
                ("production","NOT_ISSUED"),("L4",False),
                ("printed_zero_semantics","UNQUALIFIED_NOT_AUTHENTICATED_PHYSICAL_EXACT_ZERO")):
        if obj.get(k)!=v:
            raise SourceError("provenance/gate mutation: "+k)
    for k in ("physical_rate_uncertainty","source_native_PES_threshold",
              "physical_Q_J_per_event","owner_ACK","full_A"):
        if obj.get(k,"missing") is not None:
            raise SourceError("false physical authority: "+k)
    if obj.get("channel") != CHANNEL:
        raise SourceError("ionic source reaction identity mismatch")
    if obj.get("temperature_nodes_K") != list(TEMPERATURES) or obj.get("H2_product_J_list")!=list(TARGET_PRODUCTS):
        raise SourceError("temperature or quantum-state identity mismatch")
    raw=obj.get("tokens_by_product_J")
    if type(raw) is not list or len(raw)!=10 or any(type(r) is not list or len(r)!=10 for r in raw):
        raise SourceError("incomplete channel grid")
    rows=tuple(tuple(r) for r in raw)
    canonical=json.dumps(raw,ensure_ascii=True,separators=(",",":"))
    if hashlib.sha256(canonical.encode("utf-8")).hexdigest()!=EXPECTED_GRID_SHA256:
        raise SourceError("source native 10x10 original literal content identity mismatch")
    if rows[1][2]!=EXPECTED_105_J1 or tuple(rows[j][0] for j in (6,7,8,9))!=(PRINTED_ZERO,)*4:
        raise SourceError("original channel anchors mismatched")
    for row in rows:
        for tok in row:
            parse_rate(tok)
    return rows


def build_result(obj:dict) -> dict:
    rows = strict_source_record(obj)
    data=[]
    with localcontext() as ctx:
        ctx.prec=75
        for ti,T in enumerate(TEMPERATURES):
            vals=[parse_rate(rows[j][ti]) for j in TARGET_PRODUCTS]
            missing=[j for j,v in enumerate(vals) if v is None]
            nonzero=sum((v for v in vals if v is not None),Decimal(0))
            if nonzero<=0: raise SourceError("no positive printed source rate")
            record={
                "T_K":T,"reported_positive_sum_cm3_s":str(nonzero),
                "printed_zero_unqualified_J":missing,
                "coverage":"ALL_TEN_REPORTED_CHANNELS_POSITIVE_PRINTED" if not missing else "PARTIAL_CENSORED_PRINTED_ZERO",
                "reported_total_rate_cm3_s":None if missing else str(nonzero),
                "branch_fraction_J_conditional":None,
                "ortho_fraction_J_odd_conditional":None,
                "para_fraction_J_even_conditional":None,
                "mean_J_conditional":None,
                "rate_J1_cm3_s":str(vals[1]),
            }
            if not missing:
                fracs=[v/nonzero for v in vals]
                odd=sum((fracs[j] for j in (1,3,5,7,9)),Decimal(0))
                mean=sum((Decimal(j)*fracs[j] for j in TARGET_PRODUCTS),Decimal(0))
                record.update(reported_total_rate_cm3_s=str(nonzero),
                              branch_fraction_J_conditional=list(map(str,fracs)),
                              ortho_fraction_J_odd_conditional=str(odd),
                              para_fraction_J_even_conditional=str(1-odd),
                              mean_J_conditional=str(mean))
            data.append(record)
    return {
        "schema":"wu.r25.gl2022_product_branching.v1",
        "model":"STATE_RESOLVED_PRODUCT_BRANCHING_CONDITIONAL_ON_TEN_REPORTED_J_CHANNELS",
        "source":obj["original_pdf_SHA256"],"data":data,
        "new_source_matrix_shape":[10,10],"positive_printed_cells":96,
        "printed_zero_unqualified_cells":4,
        "source_native_PES_threshold":None,"physical_Q_event":None,
        "physical_bath":None,"reverse_rates":None,"physical_rate_uncertainty":None,
        "owner_ACK":None,"full_A":None,"HH_R10":"OFF","production":"NOT_ISSUED",
        "L4":False,"canonical_DAG":"34/49_UNCHANGED"
    }


def piecewise_equal_reactants(obj:dict, *, n0_m3:Decimal, schedule:tuple[tuple[int,Decimal],...]) -> dict:
    """Reported-only chemistry. Equal initial H+ and HD, fixed volume, external T."""
    rows=strict_source_record(obj)
    n0=Decimal(n0_m3)
    if not n0.is_finite() or n0<=0 or not schedule:
        raise ValueError("positive initial density and nonempty schedule required")
    with localcontext() as ctx:
        ctx.prec=75
        left=n0
        products=[Decimal(0) for _ in TARGET_PRODUCTS]
        extents=[]
        for T,seconds in schedule:
            if type(T) is not int or T not in TEMPERATURES:
                raise ValueError("external schedule must use an original source temperature")
            if T==15: raise SourceError("15K printed-zero channel rates unqualified for full branching")
            duration=Decimal(seconds)
            if not duration.is_finite() or duration<=0: raise ValueError("duration positive finite")
            idx=TEMPERATURES.index(T)
            kj=[parse_rate(rows[j][idx])*Decimal("1e-6") for j in TARGET_PRODUCTS] # m³/s
            K=sum(kj,Decimal(0))
            y=K*duration*left
            post=left/(1+y)
            dx=left-post
            for j,k in enumerate(kj): products[j]+=dx*k/K
            extents.append({"T_K":T,"duration_s":str(duration),"K_reported_m3_s":str(K),
                            "reactant_density_before_m3":str(left),"reactant_density_after_m3":str(post),
                            "extent_m3":str(dx)})
            left=post
        dplus=n0-left; total=sum(products,Decimal(0))
        # full stoichiometric invariants use n0 H+ and n0 HD initially
        conservation={"H_nuclei_initial":str(2*n0),"H_nuclei_final":str(2*left+2*total),
                      "D_nuclei_initial":str(n0),"D_nuclei_final":str(left+dplus),
                      "charge_initial":str(n0),"charge_final":str(left+dplus),
                      "particles_initial":str(2*n0),"particles_final":str(2*left+dplus+total)}
        tol=Decimal("1e-60")*n0
        if abs(total-dplus)>tol:
            raise SourceError("product extent conservation loss")
        for key in ("H_nuclei","D_nuclei","charge","particles"):
            if abs(Decimal(conservation[key+"_initial"])-Decimal(conservation[key+"_final"]))>tol:
                raise SourceError("stoichiometric conservation loss: "+key)
        return {"schema":"wu.r25.reported_channel_external_schedule.v1",
            "interpretation":"CONDITIONAL_SYNTHETIC_DENSITY_AND_THERMAL_HISTORY_SOURCE_NATIVE_PRINTED_SQM",
            "source_pdf_sha256":PDF_SHA,"initial_Hplus_and_HD_each_per_m3":str(n0),
            "schedule":extents,"end_Hplus_m3":str(left),"end_HD_v0J2_m3":str(left),
            "end_Dplus_m3":str(dplus),"end_H2_v0J0_to_J9_m3":list(map(str,products)),
            "total_reported_product_m3":str(total),"conversion_fraction":str(dplus/n0),
            "conservation":conservation,"physical_Q":None,"physical_bath":None,"reverse_rate":None,
            "owner_ACK":None,"canonical_DAG":"34/49_UNCHANGED","full_A":None,"L4":False,
            "HH_R10":"OFF","production":"NOT_ISSUED"}


def main() -> None:
    p=argparse.ArgumentParser()
    p.add_argument("--pdf",type=Path,required=True)
    p.add_argument("--out-grid",type=Path,required=True)
    p.add_argument("--out-results",type=Path,required=True)
    p.add_argument("--out-history",type=Path,required=True)
    args=p.parse_args()
    paths=(args.out_grid,args.out_results,args.out_history)
    if any(x.exists() for x in paths): raise FileExistsError("exclusive-create: outputs already exist")
    record=source_record(args.pdf)
    out=build_result(record)
    history=piecewise_equal_reactants(record,n0_m3=Decimal("1e6"),
                                     schedule=((105,Decimal("5e9")),(255,Decimal("5e9"))))
    for pth,data in zip(paths,(record,out,history)):
        pth.parent.mkdir(parents=True,exist_ok=True)
        with pth.open("x") as fp:json.dump(data,fp,ensure_ascii=False,indent=2);fp.write("\n")
    print("source_native_cells",100,"positive",96,"printed_zero_censored",4)
    for row in out["data"]:
        print(row["T_K"],row["reported_positive_sum_cm3_s"],row["ortho_fraction_J_odd_conditional"])
    print("two_segment_conversion",history["conversion_fraction"])

if __name__=="__main__":main()
