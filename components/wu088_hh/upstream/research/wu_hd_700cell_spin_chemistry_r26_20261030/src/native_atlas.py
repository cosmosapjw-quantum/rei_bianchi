"""Source-locked GL2022 ionic H+ + HD(v0,J0..6) -> D+ + H2(v0,J'0..9).

Original article DOI: 10.1063/5.0128598; original supplementary PDF locked
at source byte-level. The printed tokens are computational SQM nominal rates,
NOT experimental uncertainties, exact physical zeros, scattering Q, or an
approved molecular chemistry consumer. Do not extrapolate source values.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from decimal import Decimal, localcontext
import hashlib
import json
from pathlib import Path
import re
import subprocess

DOI="10.1063/5.0128598"
PDF_SHA="a65b1cba4208552e7eac6341b462487b23c5afe79f3ba0d2ca009fdee7dd1754"
PDF_SIZE=273554
R25_TOKENS_SHA="f1b8e438a0117688e2497af1434227a42c8c158bab9f810b536b3ad2c36e4174"
SOURCE_700_TOKENS_SHA="1258b1150577e732a8e175a16a7a78b09e69bc5a02407ed6e351f7e31eb3d7c8"
SOURCE_TABLE11_TOKENS_SHA="4c58cf6c6373540ab232abbc8dbcb12a8508bfb629a487d36271f6b1092d297b"
TEMPS=(15,55,105,255,505,1005,1505,2005,2505,3005)
INITIAL=tuple(range(7))
FINAL=tuple(range(10))
TOKEN_RE=re.compile(r"(?<![\w.])(?:\d+(?:\.\d*)?|\.\d+)\(\d{2}\)(?!\w)")
ROW_RE=re.compile(r"^\s*\(0,\s*([0-6])\)\s+(.+)$",re.M)
R25_ANCHOR="1.15(10)" # J2,J'1,T105
SOURCE_SUSPECT={(5,1,None):"IDENTICAL_TO_PRODUCT_J0_ALL_T",(3,7,2505):"ISOLATED_LITERAL_EXPONENT_16"}

class SourceContractError(ValueError):pass

def check_pdf(pdf:Path):
    p=Path(pdf)
    if not p.exists() or p.stat().st_size!=PDF_SIZE or hashlib.sha256(p.read_bytes()).hexdigest()!=PDF_SHA:
        raise SourceContractError("original GL2022 PDF bytes/SHA mismatch")


def parse_printed(tok:str):
    """Return Decimal cm3/s or None for publisher's zero-printed token."""
    m=re.fullmatch(r"(\d+(?:\.\d*)?|\.\d+)\((\d{2})\)",tok)
    if m is None:raise SourceContractError("not a printed mantissa(exponent): "+repr(tok))
    number=Decimal(m.group(1)); exponent=int(m.group(2))
    if number==0: return None
    if number<0 or not number.is_finite():raise SourceContractError("invalid source printed rate")
    return number*(Decimal(10)**(-exponent))


def _extract(pdf:Path)->tuple[list,list]:
    check_pdf(pdf)
    try:
        text=subprocess.run(["pdftotext","-layout",str(pdf),"-"],capture_output=True,text=True,check=True).stdout
    except (OSError,subprocess.CalledProcessError) as exc:
        raise SourceContractError("original PDF text extraction unavailable") from exc
    positions=[(int(x.group(1)),x.start(),x.end()) for x in re.finditer(r"\bTable\s+(\d+)\s*:",text)]
    blocks={}
    for i,(num,start,end) in enumerate(positions):
        if num in blocks:raise SourceContractError("duplicated source table header: "+str(num))
        blocks[num]=text[end:positions[i+1][1] if i+1<len(positions) else len(text)]
    if any(i not in blocks for i in range(1,12)):raise SourceContractError("missing a source Table 1..11")
    source=[]
    for fp in FINAL:
        table=blocks[fp+1]
        if not re.search(r"\b15\s+55\s+105\s+255\s+505\s+1005\s+1505\s+2005\s+2505\s+3005\b",table):
            raise SourceContractError("temperature grid mismatch in table "+str(fp+1))
        rows=ROW_RE.findall(table)
        if len(rows)!=7 or [int(j) for j,_ in rows]!=list(INITIAL):
            raise SourceContractError("initial rotational state labels/rows mismatch: "+str(fp))
        one=[]
        for j,line in rows:
            tokens=TOKEN_RE.findall(line)
            if len(tokens)!=10:raise SourceContractError(f"bad printed row productJ={fp} initialJ={j}, n={len(tokens)}")
            for token in tokens:parse_printed(token)
            one.append(tokens)
        source.append(one)
    tab11=TOKEN_RE.findall(blocks[11])
    if len(tab11)!=10 or tab11[0]!="2.47(21)" or tab11[-1]!="7.22(10)":
        raise SourceContractError("published Table11 completeness mismatch")
    if source[1][2][2]!=R25_ANCHOR:raise SourceContractError("R18/R25 original anchor mismatch")
    return source,tab11


def extract_source(pdf:Path)->dict:
    source,tab11=_extract(pdf)
    old=[[source[out][2][ti] for ti in range(10)] for out in FINAL]
    old_hash=hashlib.sha256(json.dumps(old,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
    if old_hash!=R25_TOKENS_SHA:raise SourceContractError("R25 original 100-cell tokens changed")
    digest=hashlib.sha256(json.dumps(source,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
    if digest!=SOURCE_700_TOKENS_SHA:raise SourceContractError("original 700-cell printed-literal SHA mismatch")
    thermal_digest=hashlib.sha256(json.dumps(tab11,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
    if thermal_digest!=SOURCE_TABLE11_TOKENS_SHA:raise SourceContractError("original Table11 token SHA mismatch")
    # Detect literal anomaly; do not correct or mask the original source.
    if source[0][5]!=source[1][5] or source[7][3][8]!="6.72(16)":
        raise SourceContractError("original source anomaly witnesses changed")
    return {"schema":"wu.r26.source_700.v1","doi":DOI,"pdf_sha256":PDF_SHA,"pdf_bytes":PDF_SIZE,
      "shape":[10,7,10],"axes_order":["H2_final_J","HD_initial_J","temperature"],
      "temperature_nodes_K":list(TEMPS),"HD_initial_J":list(INITIAL),"H2_final_J":list(FINAL),
      "tokens_jprime_j_T":source,"table11_thermal_nominal_tokens":tab11,
      "token_sha256":digest,"r25_subset_sha256":old_hash,
      "status":"PUBLISHED_COMPUTED_SQM_RATE_LITERALS_NOT_EXPERIMENT",
      "printed_zero_semantics":"UNQUALIFIED_NOT_CERTIFIED_EXACT_ZERO",
      "source_suspect_cells":[{"j":5,"jprime":1,"temperatures_K":list(TEMPS),"reason":"DUPLICATE_WITH_JPRIME0_ROW"},
          {"j":3,"jprime":7,"T_K":2505,"token":"6.72(16)","reason":"EXPONENT_ISOLATED_AMONG_NEIGHBOURS"}],
      "thermal_definition":"Main article Eq5 uses initial j0..8 and product spin weights Eq6-7; supplement covers initial j0..6 only",
      "PES_native_threshold":None,"physical_Q":None,"source_uncertainty":None,"owner_ACK":None,
      "R6":"NOT_RUN","C9":"NOT_RUN","HH_R10":"OFF","production":"NOT_ISSUED","full_A":None,"L4":False,"canonical_DAG":"34/49_UNCHANGED"}


def verify_source(obj:dict)->list:
    if obj.get("schema")!="wu.r26.source_700.v1" or obj.get("doi")!=DOI or obj.get("pdf_sha256")!=PDF_SHA or obj.get("pdf_bytes")!=PDF_SIZE:
        raise SourceContractError("source identity/schema mismatch")
    if obj.get("shape")!=[10,7,10] or obj.get("axes_order")!=["H2_final_J","HD_initial_J","temperature"]:
        raise SourceContractError("source coordinate mismatch")
    if obj.get("temperature_nodes_K")!=list(TEMPS) or obj.get("HD_initial_J")!=list(INITIAL) or obj.get("H2_final_J")!=list(FINAL):
        raise SourceContractError("quantum labels or temperatures mismatch")
    for key in ("physical_Q","PES_native_threshold","source_uncertainty","owner_ACK","full_A"):
        if key not in obj or obj[key] is not None:raise SourceContractError("forbidden authority: "+key)
    for key,val in (("R6","NOT_RUN"),("C9","NOT_RUN"),("HH_R10","OFF"),("production","NOT_ISSUED"),("L4",False),("canonical_DAG","34/49_UNCHANGED")):
        if obj.get(key)!=val:raise SourceContractError("science gate changed: "+key)
    tokens=obj.get("tokens_jprime_j_T")
    if not isinstance(tokens,list) or len(tokens)!=10 or any(not isinstance(a,list) or len(a)!=7 for a in tokens):
        raise SourceContractError("invalid table shape")
    if any(not isinstance(v,list) or len(v)!=10 for a in tokens for v in a):raise SourceContractError("invalid row lengths")
    digest=hashlib.sha256(json.dumps(tokens,ensure_ascii=True,separators=(",",":")).encode()).hexdigest()
    if digest!=SOURCE_700_TOKENS_SHA or digest!=obj["token_sha256"]:raise SourceContractError("modified source token content")
    if tokens[0][5]!=tokens[1][5] or tokens[7][3][8]!="6.72(16)":raise SourceContractError("source anomalous literals mismatch")
    for a in tokens:
        for row in a:
            for item in row:parse_printed(item)
    if len(obj.get("table11_thermal_nominal_tokens",[]))!=10 or hashlib.sha256(json.dumps(obj["table11_thermal_nominal_tokens"],ensure_ascii=True,separators=(",",":")).encode()).hexdigest()!=SOURCE_TABLE11_TOKENS_SHA:
        raise SourceContractError("source Table11 missing or changed")
    return tokens


def cell_issue(j,jprime,T,token):
    if parse_printed(token) is None:return "PRINTED_ZERO_UNQUALIFIED"
    if j==5 and jprime in (0,1):return "SOURCE_SUSPECT_IDENTICAL_PRODUCT_ROWS"
    if (j,jprime,T)==(3,7,2505):return "SOURCE_SUSPECT_EXPONENT_16"
    return "POSITIVE_PRINTED_NOMINAL"


def expand_csv(obj)->list[dict]:
    tokens=verify_source(obj);rows=[]
    for jp in FINAL:
        for j in INITIAL:
            for it,T in enumerate(TEMPS):
                tok=tokens[jp][j][it]; rate=parse_printed(tok)
                rows.append({"doi":DOI,"initial_v":0,"initial_J":j,"final_v":0,"final_J":jp,
                   "T_K":T,"original_table":jp+1,"printed_token":tok,"published_rate_cm3_s":str(rate) if rate is not None else "",
                   "published_rate_m3_s":str(rate*Decimal("1e-6")) if rate is not None else "",
                   "qualification":cell_issue(j,jp,T,tok)})
    if len(rows)!=700:raise SourceContractError("700-cell census failed")
    return rows


def moment_at(obj, T:int, j:int, spin:bool)->dict:
    """Rates for one initial state; exclude 15K/uncertain or suspect rows from accepted totals."""
    tok=verify_source(obj)
    if T not in TEMPS or j not in INITIAL:raise SourceContractError("unpublished initial state or temperature")
    it=TEMPS.index(T)
    vs=[parse_printed(tok[jp][j][it]) for jp in FINAL]
    issues=[cell_issue(j,jp,T,tok[jp][j][it]) for jp in FINAL]
    censored=[jp for jp,x in enumerate(vs) if x is None]
    suspect=[jp for jp,issue in enumerate(issues) if "SUSPECT" in issue]
    with localcontext() as ctx:
        ctx.prec=64
        weighted=[(None if x is None else x * (Decimal(3)/4 if jp%2 else Decimal(1)/4)) if spin else x for jp,x in enumerate(vs)]
        positive_sum=sum((x for x in weighted if x is not None),Decimal(0))
        if positive_sum<=0:raise SourceContractError("empty source rates")
        status="PASS_PRINTED_COMPLETE" if not censored and not suspect else "SOURCE_HELD_PARTIAL_OR_SUSPECT"
        # Report the printed sum for diagnostics, do not call it a full-state physical total when held.
        fractions=[str(x/positive_sum) for x in weighted] if status=="PASS_PRINTED_COMPLETE" else None
        odd_fraction=sum((weighted[jp] for jp in FINAL if jp%2 and weighted[jp] is not None),Decimal(0))/positive_sum if status=="PASS_PRINTED_COMPLETE" else None
        return {"T_K":T,"HD_J":j,"policy":"Eq6_7_spin_weighted" if spin else "raw_SQM",
                "source_status":status,"censored_Jprime":censored,"suspect_Jprime":suspect,
                "positive_sum_cm3_s":str(positive_sum),"full_qualified_sum_cm3_s":str(positive_sum) if status=="PASS_PRINTED_COMPLETE" else None,
                "branching_by_Jprime":fractions,"odd_Jprime_fraction":str(odd_fraction) if odd_fraction is not None else None}


def analyze(obj)->dict:
    rows=expand_csv(obj)
    return {"schema":"wu.r26.source_native_atlas_summary.v1","pdf_sha256":PDF_SHA,"cell_count":len(rows),
        "positive_cells":sum(bool(v["published_rate_cm3_s"]) for v in rows),
        "printed_zero_unqualified":sum(v["qualification"]=="PRINTED_ZERO_UNQUALIFIED" for v in rows),
        "source_suspect_nonzero":sum("SUSPECT" in v["qualification"] for v in rows),
        "original_table11_cm3_s":[str(parse_printed(x)) for x in obj["table11_thermal_nominal_tokens"]],
        "thermal_Table11_reconstruction":"NOT_QUALIFIED_MISSING_HD_INITIAL_J7_8_AND_STATE_ENERGY_PROVENANCE",
        "rows":[moment_at(obj,T,j,spin) for spin in (False,True) for T in TEMPS for j in INITIAL],
        "physical_Q":None,"PES_native_threshold":None,"owner_ACK":None,"source_uncertainty":None,
        "HH_R10":"OFF","production":"NOT_ISSUED","L4":False,"canonical_DAG":"34/49_UNCHANGED"}


def save_exclusive(path:Path,payload:dict):
    path.parent.mkdir(exist_ok=True,parents=True)
    with path.open("x",encoding="utf8") as h:json.dump(payload,h,ensure_ascii=False,indent=2);h.write("\n")


def main(argv=None):
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument("--pdf",required=True,type=Path)
    a.add_argument("--out-source",required=True,type=Path)
    a.add_argument("--out-atlas",required=True,type=Path)
    a.add_argument("--out-csv",required=True,type=Path)
    z=a.parse_args(argv)
    for path in (z.out_source,z.out_atlas,z.out_csv):
        if path.exists():raise FileExistsError("exclusive-create output: "+str(path))
    source=extract_source(z.pdf)
    atlas=analyze(source)
    save_exclusive(z.out_source,source);save_exclusive(z.out_atlas,atlas)
    z.out_csv.parent.mkdir(parents=True,exist_ok=True)
    with z.out_csv.open("x",encoding="utf8",newline="") as f:
        rows=expand_csv(source);w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
    print("source_sha",source["token_sha256"],"rates",atlas["cell_count"],"positive",atlas["positive_cells"],"censored",atlas["printed_zero_unqualified"],"suspect",atlas["source_suspect_nonzero"])

if __name__=="__main__":main()
