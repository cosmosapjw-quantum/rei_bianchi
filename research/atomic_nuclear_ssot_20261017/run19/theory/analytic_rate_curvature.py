"""RUN19 source-bound ideal-real log-curvature certificate and RR references.

No native RHS, IVP, old history, or table benchmark is executed. Polynomial
coefficients are parsed from the actual immutable Rust source; their decimal
literals are interpreted as exact real rationals in this mathematical model.
The already deployed f64 table remains a distinct rounded implementation.
"""
from __future__ import annotations
import argparse
import ast
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import re
import time

def plus(a, b):
    n=max(len(a),len(b))
    return [(a[i] if i<len(a) else F(0))+(b[i] if i<len(b) else F(0)) for i in range(n)]
def times(a,b):
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j]+=x*y
    return out
def exact_polynomial(expression):
    text=re.sub(r"l\.powi\((\d+)\)",r"l**\1",expression)
    text=" ".join(text.split())
    def walk(node):
        if isinstance(node,ast.Constant) and isinstance(node.value,(float,int)):
            return [F(ast.get_source_segment(text,node))]
        if isinstance(node,ast.Name) and node.id=="l":
            return [F(0),F(1)]
        if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):
            return [-v for v in walk(node.operand)]
        if isinstance(node,ast.BinOp):
            if isinstance(node.op,ast.Add):return plus(walk(node.left),walk(node.right))
            if isinstance(node.op,ast.Sub):return plus(walk(node.left),[-v for v in walk(node.right)])
            if isinstance(node.op,ast.Mult):return times(walk(node.left),walk(node.right))
            if isinstance(node.op,ast.Pow) and isinstance(node.right,ast.Constant) and isinstance(node.right.value,int):
                out=[F(1)]
                for _ in range(node.right.value):out=times(out,walk(node.left))
                return out
        raise ValueError(f"Unrecognized source polynomial: {ast.dump(node)}")
    return walk(ast.parse(text,mode="eval").body)
def derivative(p):
    return [i*p[i] for i in range(1,len(p))] or [F(0)]
def bernstein(p,a,b):
    """Exact coefficients of p(a+(b-a)u), then power-to-Bernstein on [0,1]."""
    n=len(p)-1
    power=[sum((p[i]*math.comb(i,j)*a**(i-j)*(b-a)**j for i in range(j,n+1)),F(0)) for j in range(n+1)]
    return [sum((power[j]*F(math.comb(k,j),math.comb(n,j)) for j in range(k+1)),F(0)) for k in range(n+1)]
def exact_value(p,x):
    v=F(0)
    for a in reversed(p):v=v*x+a
    return v
def ratio(v):
    return {"numerator":str(v.numerator),"denominator":str(v.denominator),"approximate_f64":float(v)}
def source_polynomials(text):
    pats={
        "ci_hi":r"let v = \((.*?)\)\s*\.exp\(\);",
        "ci_hei":r"let k3 = \|\| \{.*?\(([-]44.*?)\)\s*\.exp\(\)",
        "ci_heii":r"let k5 = \|\| \{.*?\(([-]68.*?)\)\s*\.exp\(\)",
        "rr_hii_high":r"if t > 5500\.0 \{\s*\((.*?)\)\s*\.exp\(\)",
    }
    return {name:exact_polynomial(re.search(p,text,re.S).group(1)) for name,p in pats.items()}
def polynomial_certificates(text):
    rows={}
    for name,p in source_polynomials(text).items():
        # ci_hi at log(te)<=-2 is certainly floor selected: every term is
        # negative and p<=c0-2*c1<-50; exp(-50)<1e-20 because exp(2.5)>10.
        lower=-2 if name=="ci_hi" else -1
        second=derivative(derivative(p))
        panels=[]
        for a in range(lower,5):
            bs=bernstein(second,F(a),F(a+1))
            panels.append({"lower":a,"upper":a+1,"bernstein_coefficients":[ratio(x) for x in bs],"min":ratio(min(bs)),"max":ratio(max(bs))})
        maximum=max(abs(F(int(r["numerator"]),int(r["denominator"]))) for panel in panels for r in panel["bernstein_coefficients"])
        rows[name]={"source_decimal_coefficients":[str(v) for v in p],"enclosing_log_temperature_interval":[lower,5],
                    "M_exact":ratio(maximum),"panels":panels}
    p=source_polynomials(text)["ci_hi"]
    assert all(p[n]*((-1)**n)<0 for n in range(len(p)))
    assert p[0]-2*p[1]<-50
    assert sum((F(5,2)**i/F(math.factorial(i)) for i in range(5)),F(0))>10
    return rows
def li_be_rows(path):
    selected=[]
    for line in path.read_text().splitlines():
        z=int(line[9:11])
        if z not in (3,4):continue
        row={"ion_formed":line[:8].strip(),"Z":z,"N_final":int(line[12:14]),
             "a_cm3_s":line[16:25].strip(),"b":line[27:33].strip(),
             "T0_K":line[35:44].strip(),"T1_K":line[46:55].strip(),
             "raw_line":line}
        row["initial_charge"]=z-row["N_final"]+1
        row["final_charge"]=z-row["N_final"]
        selected.append(row)
    assert len(selected)==6
    return selected
def rr(row,t):
    if not math.isfinite(t) or not 3.0<=t<=1e9:raise ValueError("VF96_LOW_Z_TEMPERATURE_DOMAIN")
    a,b,t0,t1=(float(row[k]) for k in ("a_cm3_s","b","T0_K","T1_K"))
    r0=math.sqrt(t/t0);r1=math.sqrt(t/t1)
    logv=math.log(a)-math.log(r0)-(1-b)*math.log1p(r0)-(1+b)*math.log1p(r1)
    return math.exp(logv)
def analytic_bounds(poly):
    L=F("69.07755278982137")
    # DR coefficient uses te=T/11605. The positive exponential sum has
    # |D²log(1+0.3 exp(-u))| <= .3(4/e²+1/e)<.6.
    dr=F("40.49664394833662")/F("0.8")+F(3,5)
    brem=F(34,100)/(8*F(11,10))+F(34,100)/(6*F(144,100))
    return {
      "ci_hi":F(int(poly["ci_hi"]["M_exact"]["numerator"]),int(poly["ci_hi"]["M_exact"]["denominator"])),
      "ci_hei":F(int(poly["ci_hei"]["M_exact"]["numerator"]),int(poly["ci_hei"]["M_exact"]["denominator"])),
      "ci_heii":F(int(poly["ci_heii"]["M_exact"]["numerator"]),int(poly["ci_heii"]["M_exact"]["denominator"])),
      "rr_hii":F(int(poly["rr_hii_high"]["M_exact"]["numerator"]),int(poly["rr_hii_high"]["M_exact"]["denominator"])),
      "rr_heii":F(0),
      "rr_heiii":F("0.7")**2/4,
      "dr_heii":dr,
      "ce_hi":L+F(1,16),
      "ce_hei":L+F(1,16),
      "ce_heii":L+F(1,16),
      "rr_cooling_hii":F("2.697")*F("0.502")**2/4,
      "rr_cooling_heii":F(0),
      "rr_cooling_heiii":F("2.697")*F("0.502")**2/4,
      "dr_raw_cooling_heii":L+F(3,5),
      "freefree":brem,
    }
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    start=time.perf_counter()
    owner=args.source_root/"owner_src"
    source=owner/"igm_rates.rs"
    text=source.read_text()
    table=Path(__file__).parent/"primary_sources/verner_ferland_table1.dat"
    poly=polynomial_certificates(text)
    bounds=analytic_bounds(poly)
    h=math.log(1e6)/65536
    # Rational h<14.04/65536 follows ln10<2.34.
    # Exact exp(2.34)>10 is verified by a positive finite Taylor sum.
    exp_lower=sum((F(117,50)**i/F(math.factorial(i)) for i in range(14)),F(0))
    assert exp_lower>10
    h_upper=F(6)*F(117,50)/65536
    rrrows=li_be_rows(table)
    refs=[]
    for row in rrrows:
        refs.append({**row,"rates":[{"T_K":t,"alpha_cm3_s_f64":rr(row,t),"alpha_m3_s_f64":rr(row,t)*1e-6} for t in (3.,10.,100.,1e4,1e6,1e9)]})
    allrows=[]
    for name,M in bounds.items():
        eps=M*h_upper*h_upper/8
        # exp(eps)-1<=eps/(1-eps) for 0<=eps<1, exact rational certificate.
        rel=eps/(1-eps)
        allrows.append({"channel":name,"M_exact":ratio(M),"log_error_rational_upper":ratio(eps),
          "relative_error_rational_upper":ratio(rel),"log_slope_error_rational_upper":ratio(M*h_upper/2),
          "below_1e_minus_5_ideal_real":rel<F(1,100000),
          "approximate_sharp_h_relative_error":math.expm1(float(M)*h*h/8)})
    inputs=[]
    for path in (source,owner/"rate_table.rs",owner/"igm_thermal.rs",owner/"deuterium_atomic.rs",table):
        inputs.append({"path":str(path),"bytes":path.stat().st_size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()})
    result={"unit":"RUN19_ANALYTIC_RATE_CURVATURE_AND_PRIMARY_RR","status":"DERIVED_AND_EXACT_RATIONAL_POLYNOMIAL_CHECKED",
      "scope":"Ideal real native decimal-literal rate functions on one smooth native branch, exact log coordinates and ideal endpoint samples; not f64 packet rounding, branch selection at adjacent f64 values, physical fit uncertainty, derivative at knots, or coupled history.",
      "inputs":inputs,"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
      "log_grid":{"nodes":65537,"T_domain_K":[1,1000000],"h_approximate":h,"h_rational_upper":ratio(h_upper)},
      "polynomial_certificates":poly,"channel_bounds":allrows,
      "all_15_channel_ideal_relative_bounds_below_1e_minus_5":all(r["below_1e_minus_5_ideal_real"] for r in allrows),
      "six_author_RR_rows":refs,"RR_model_scope":"Total elemental electronic RR only, all final levels; coefficients are literature data, not isotope-specific and not a thermal cooling moment. Prior REI alternate-branch reuse status is recorded separately.",
      "native_rhs_calls":0,"ivp_runs":0,"historical_runs":0,
      "wall_seconds":time.perf_counter()-start}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():raise RuntimeError("Refusing to overwrite a result")
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"result":str(args.output),"all15":result["all_15_channel_ideal_relative_bounds_below_1e_minus_5"],
                      "M":[[r["channel"],r["M_exact"]["approximate_f64"],r["relative_error_rational_upper"]["approximate_f64"]] for r in allrows],
                      "RR_1e4":[[r["ion_formed"],r["rates"][3]["alpha_cm3_s_f64"]] for r in refs],
                      "wall_seconds":result["wall_seconds"]},indent=2))
if __name__=="__main__":main()

