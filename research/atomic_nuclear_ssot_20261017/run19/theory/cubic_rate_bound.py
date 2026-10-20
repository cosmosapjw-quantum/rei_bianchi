"""RUN19 exact-rational sufficient value-cubic truncation bounds.

Uses ideal real decimal-literal native formulas and exact log-temperature nodes.
Four-node support must stay on one source branch/floor/zero identity. Arithmetic
roundoff and actual table source-data roundoff are intentionally separate.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
import math
from pathlib import Path
import time
from analytic_rate_curvature import source_polynomials, derivative, bernstein, ratio

def polynomial_derivative_bounds(text):
    result={}
    for name,poly in source_polynomials(text).items():
        lower=-2 if name=="ci_hi" else -1
        derivatives=[]
        p=poly
        for order in range(1,5):
            p=derivative(p)
            values=[v for a in range(lower,5) for v in bernstein(p,F(a),F(a+1))]
            derivatives.append(max(map(abs,values)))
        if name=="rr_hii_high":
            derivatives[0]=max(derivatives[0],F("0.6353"))
        result[name]=derivatives
    return result
def rational_channel_bounds(text):
    poly=polynomial_derivative_bounds(text)
    L=F("69.07755278982137")
    # For f=log(1+0.3 exp(-u)), |D^n f| <=
    # .3 sum_k S(n,k) k^k exp(-k) for n<=4.
    # Bernoulli cumulants up to four are bounded by w<=.3 exp(-u).
    # e>8/3 makes the following entries exact rational upper bounds.
    stirling=[[1],[1,1],[1,3,1],[1,7,6,1]]
    mix=[F(3,10)*sum((F(coeff)*(F(3*k,8)**k) for k,coeff in enumerate(row,1)),F(0)) for row in stirling]
    B=F("40.49664394833662")/F("0.8")
    dr=[B+mix[i]+(F(3,2) if i==0 else 0) for i in range(4)]
    raw=[L+mix[i]+(F(3,2) if i==0 else 0) for i in range(4)]
    ce=lambda power:[L+abs(power)+F(1,2),L+F(1,16),L+F(1,32),L+F(1,64)]
    # a=1.1,b=.34; log10-coordinate y=5.5-log(T)/ln10.
    # e>8/3, ln10>2 and elementary maxima of |y|^k exp(-y²/3).
    r=F(34,110)
    brem=[F(1,2)+r/3,F(34,100)/(8*F(11,10))+F(34,100)/(6*F(144,100)),5*r/18,13*r/48]
    cooling=[F("0.965")+F("2.697")*F("0.502")]+[F("2.697")*F("0.502")**i/4 for i in range(2,5)]
    out={
      "ci_hi":poly["ci_hi"],"ci_hei":poly["ci_hei"],"ci_heii":poly["ci_heii"],
      "rr_hii":poly["rr_hii_high"],"rr_heii":[F("0.6353"),F(0),F(0),F(0)],
      "rr_heiii":[F("1.4")]+[F("0.7")**i/4 for i in range(2,5)],
      "dr_heii":dr,
      "ce_hi":ce(F(0)),"ce_hei":ce(F("-0.1687")),"ce_heii":ce(F("-0.3970")),
      "rr_cooling_hii":cooling,"rr_cooling_heii":[F("0.346"),F(0),F(0),F(0)],
      "rr_cooling_heiii":cooling,"dr_raw_cooling_heii":raw,"freefree":brem,
    }
    assert all(all(m>=0 for m in ms) for ms in out.values())
    return out
def bell4(ms):
    a,b,c,d=ms
    return d+4*a*c+3*b*b+6*a*a*b+a**4
def cubic_relative_bound(ms,nodes):
    # exp(2*h*M1)<=1/(1-2*h_upper*M1), with positive denominator.
    h_upper=F(6)*F(117,50)/(nodes-1)
    u=2*h_upper*ms[0]
    if u>=1:raise ValueError("Rational exponential majorant needs u<1")
    B=bell4(ms)
    epsilon=F(3,128)*h_upper**4*B/(1-u)
    h=math.log(1e6)/(nodes-1)
    return {"nodes":nodes,"h_approximate":h,"h_rational_upper":ratio(h_upper),
      "log_variation_rational_upper":ratio(u),"Bell4_rational":ratio(B),
      "relative_error_rational_upper":ratio(epsilon),
      "relative_error_exact_h_formula_approximate":3/128*h**4*math.exp(2*h*float(ms[0]))*float(B),
      "below_original_1e_minus_5":epsilon<F(1,100000)}
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-root",type=Path,required=True)
    ap.add_argument("--output",type=Path,required=True)
    args=ap.parse_args()
    start=time.perf_counter()
    source=args.source_root/"owner_src/igm_rates.rs"
    bounds=rational_channel_bounds(source.read_text())
    rows=[{"channel":name,"M1_to_M4_rational":[ratio(m) for m in ms],
           "candidate_bounds":[cubic_relative_bound(ms,n) for n in (16385,32769)]} for name,ms in bounds.items()]
    result={"unit":"RUN19_VALUE_CUBIC_LOG_TEMPERATURE_ANALYTIC_BOUND","status":"DERIVED_AND_EXACT_RATIONAL_CHECKED",
      "source":{"path":str(source),"bytes":source.stat().st_size,"sha256":hashlib.sha256(source.read_bytes()).hexdigest()},
      "code":{"self_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "analytic_rate_curvature_sha256":hashlib.sha256((Path(__file__).parent/"analytic_rate_curvature.py").read_bytes()).hexdigest()},
      "scope":"Each valid four-node support lies wholly on one smooth formula branch of ideal-real native decimal-literal coefficients. Exact log nodes, exact ideal source samples, and exact polynomial evaluation; f64 source/table/grid/exp/log rounding remains a distinct obligation.",
      "kernel":{"nodes_relative_to_cell_left":[-1,0,1,2],"query_theta":[0,1],"max_kernel_over_factorial4":"3/128",
                "relative_bound":"(3/128)*h^4*exp(2*h*M1)*(M4+4*M1*M3+3*M2^2+6*M1^2*M2+M1^4)"},
      "strict_domain_K":[1,1000000],"branch_support_policy":"Direct source fallback if any of three support cells has a branch knot, changes CI floor identity, contains an uncertified zero/non-normal endpoint, or the four nodes do not exist. Structural constant-zero channels stay exactly zero. Positive finite fallback protects admissibility; quantified accuracy also uses this bound or an independent scoped gate.",
      "channel_bounds":rows,
      "all_channels_16385_ideal_below_original_1e_minus_5":all(row["candidate_bounds"][0]["below_original_1e_minus_5"] for row in rows),
      "all_channels_32769_ideal_below_original_1e_minus_5":all(row["candidate_bounds"][1]["below_original_1e_minus_5"] for row in rows),
      "physical_fit_uncertainty":"Separate source-model uncertainty; no change or numerical certificate supplied",
      "new_native_rhs_calls":0,"new_ivp_runs":0,"historical_runs":0,
      "wall_seconds":time.perf_counter()-start}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    if args.output.exists():raise RuntimeError("Refusing to overwrite result")
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    summary={"result":str(args.output),"all16k":result["all_channels_16385_ideal_below_original_1e_minus_5"],
             "all32k":result["all_channels_32769_ideal_below_original_1e_minus_5"],
             "per_channel":[[r["channel"],[m["approximate_f64"] for m in r["M1_to_M4_rational"]],
                             [b["relative_error_rational_upper"]["approximate_f64"] for b in r["candidate_bounds"]]] for r in rows],
             "wall_seconds":result["wall_seconds"]}
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()

