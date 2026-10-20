"""Requested independent decimal reference; not a new native execution."""
import decimal
import hashlib
import json
from pathlib import Path
import platform
from analytic_rate_curvature import li_be_rows, rr

base = Path(__file__).resolve().parent
table = base / "primary_sources/verner_ferland_table1.dat"
rows = []
with decimal.localcontext() as ctx:
    ctx.prec = 80
    D = decimal.Decimal
    for row in li_be_rows(table):
        if row["Z"] != 4:
            continue
        a,b,t0,t1 = (D(row[k]) for k in ("a_cm3_s","b","T0_K","T1_K"))
        u=(D(10000)/t0).sqrt()
        v=(D(10000)/t1).sqrt()
        truth=a/(u*(1+u)**(1-b)*(1+v)**(1+b))
        nearest = float(truth)
        original = rr(row,10000.0)
        rows.append({
            "ion_formed":row["ion_formed"],
            "T_K":10000,
            "reference_decimal80_cm3_s":str(truth),
            "reference_decimal80_rounded_binary64":nearest,
            "reference_decimal80_rounded_binary64_hex":nearest.hex(),
            "previous_log_domain_binary64":original,
            "previous_log_relative_difference_decimal80":str(D.from_float(original)/truth-1),
            "row":row,
        })
out={
    "unit":"RUN19_BE_GOLDEN_EVALUATOR_DIAGNOSTIC",
    "reason":"Requested by metals implementation reviewer to distinguish equation/row mismatch from log-domain vs direct-denominator binary64 roundoff.",
    "status":"NUMERICALLY_CHECKED",
    "interpretation":"Decimal80 evaluation is an independent high-precision numerical reference for the exact decimal table model, not a directed-rounding mathematical enclosure.",
    "source_table":{"path":str(table),"sha256":hashlib.sha256(table.read_bytes()).hexdigest()},
    "script":{"name":Path(__file__).name,"sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},
    "python_version":platform.python_version(),
    "precision_decimal_digits":80,
    "rows":rows,
    "native_rhs_calls":0,
    "ivp_runs":0,
    "tests_run":0,
    "old_results_modified":False,
}
path=base/"execution03"/"BE_GOLDEN_DECIMAL80.json"
path.parent.mkdir(exist_ok=True)
with path.open("x") as f:
    json.dump(out,f,indent=2)
    f.write("\n")
print(json.dumps({"output":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"rows":[{k:v for k,v in r.items() if k!="row"} for r in rows]}))
