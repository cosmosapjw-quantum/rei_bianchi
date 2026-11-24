"""Replay the Rust transport on the admitted AX08 source and independently integrate it."""
import argparse
import csv
import gzip
import hashlib
import io
import json
import math
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MATERIAL = Path("research/rei_igm_sync_20261116/approximation_validity/incremental_fifth/results_five/five_case_abundances.csv.gz")
ARCHIVED = Path("research/rei_axbi_owner_loop_20261115/results/thomson_segment.csv.gz")
K = 299792458.0 * 6.6524587051e-29
E = (0.6, 0.0, 0.8)
CASES = ("ZERO", "SHEAR_HALF_PLUS", "SHEAR_HALF_MINUS", "SHEAR_MINUS", "SHEAR_PLUS")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, description):
    if not condition:
        raise ValueError(description)


def integrate(table):
    """Independent scalar clock and covector calculation, including REC's interpolation."""
    pairs = list(zip(table, table[1:]))
    linear = math.fsum((y[0]-x[0]) * K * 0.5 * (x[1]*x[2]+y[1]*y[2]) for x,y in pairs)
    # 3-node Gauss-Legendre is an independent evaluation of the smooth REC cell model.
    nodes = [(0.5*(1.0+u), w/2.0) for u,w in
             [(-math.sqrt(3/5),5/9),(0.0,8/9),(math.sqrt(3/5),5/9)]]
    cells = [K*(y[0]-x[0])*math.fsum(
        w*math.exp((1-u)*math.log(x[1])+u*math.log(y[1]))*((1-u)*x[2]+u*y[2])
        for u,w in nodes) for x,y in pairs]
    return linear, math.fsum(cells)


def run_case(rust, rec, material, work, case, convention, velocity):
    with material.open() as stream:
        rows = [r for r in csv.DictReader(stream) if r["case"] == case]
    end_t = float(rows[-1]["time_s"])
    betas = []
    for row in rows:
        t = float(row["time_s"]) / end_t
        betas.append({"zero": (0.,0.,0.), "constant": (0.1,0.,0.),
                      "varying": (0.2*t,-0.1*t,0.05*(1-t))}[velocity])
    if velocity == "varying":
        series = work / "velocity.tsv"
        with series.open("w") as f:
            f.write("normal_t_s\tbeta_x\tbeta_y\tbeta_z\n")
            for row, v in zip(rows,betas):
                f.write("\t".join([row["time_s"], *map(str,v)]) + "\n")
        velocity_args = ["--beta-series", str(series)]
    else:
        velocity_args = list(map(str,betas[0]))
    command = [rust, material, case, convention, *velocity_args, *map(str,E)]
    result = subprocess.run(command, text=True, capture_output=True, check=True)
    metadata = json.loads(result.stderr)
    samples = list(csv.DictReader(io.StringIO(result.stdout), delimiter="\t"))
    require(len(samples) == len(rows) == metadata["rows"] == 1001, "history length")
    end_b = float(rows[-1]["b"])
    independently = []
    max_direction_error = 0.0
    for native,s,beta in zip(rows,samples,betas):
        db = float(native["b"]) - end_b
        raw = [E[0]*math.exp(db), E[1]*math.exp(db), E[2]*math.exp(-2*db)]
        n = [c/math.hypot(*raw) for c in raw]
        max_direction_error = max(max_direction_error, *(abs(q-float(s[k])) for q,k in zip(n,("dir_x","dir_y","dir_z"))))
        gamma = 1/math.sqrt(1-math.fsum(v*v for v in beta))
        doppler = gamma*(1-math.fsum(v*d for v,d in zip(beta,n)))
        nh = float(native["nH_proper_cm3"])
        ne = float(native["ne_proper_cm3"])
        ref = nh*1e6 / (gamma if convention=="normal-inventory" else 1.0)
        independently.append((float(native["time_s"]), ref, ne/nh*doppler))
        require(math.isclose(ref,float(s["n_reference_rest_m3"]),rel_tol=1e-14), "rest-density convention")
    direct, rec_model = integrate(independently)
    require(max_direction_error < 1e-14, "native diagonal characteristic")
    require(abs(direct-metadata["tau_to_terminal"]) < 5e-14, "proper time optical depth")
    require(metadata["mass_closure_abs"] < 5e-14, "mass plus transmission")
    metadata["independent_trapezoid"] = direct
    metadata["independent_rec_interpolation"] = rec_model
    metadata["maximum_direction_component_error"] = max_direction_error
    if rec:
        exchange = work / "material.tsv"
        exchange.write_text(result.stdout)
        out = subprocess.run([rec,exchange],text=True,capture_output=True,check=True)
        bins = list(csv.DictReader(io.StringIO(out.stdout),delimiter="\t"))
        rec_tau = float(bins[0]["tau_far"])
        require(len(bins)==1000 and abs(rec_tau-rec_model) < 5e-13,"external REC cell interpolation")
        metadata["rec_binary_tau"] = rec_tau
    return metadata


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rei-binary",type=Path,required=True)
    p.add_argument("--rec-binary",type=Path)
    p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    metadata={"scenario":"PLANCKLIKE_MD14_BB50K_CONDITIONAL_HHE_V1",
              "domain":"zbar 20 to a conditional zbar=4 receiver",
              "source_commit":"d455e288bda954c89f3d9b70ba27f225638c74eb",
              "archive_sha256":{str(f):sha(ROOT/f) for f in (MATERIAL,ARCHIVED)},
              "baseline":[], "conditional_tilt_replays":[]}
    if a.rec_binary:
        metadata["rec_binary_sha256"]=sha(a.rec_binary)
    with tempfile.TemporaryDirectory() as temp:
        work=Path(temp)
        source=work/"source.csv"
        source.write_bytes(gzip.decompress((ROOT/MATERIAL).read_bytes()))
        archive={}
        with gzip.open(ROOT/ARCHIVED,"rt") as f:
            for row in csv.DictReader(f):
                archive.setdefault(row["case"],float(row["tau_to_conditional_z4_receiver"]))
        for case in CASES:
            m=run_case(a.rei_binary.resolve(),a.rec_binary,source,work,case,"rest","zero")
            if case in archive:
                m["archived_full_native_time_tau"]=archive[case]
                m["sampled_minus_native_time_tau"]=m["tau_to_terminal"]-archive[case]
                require(abs(m["sampled_minus_native_time_tau"]) < 2e-8,"AX08 sampling vs native four-case archive")
            metadata["baseline"].append(m)
        for velocity in ("constant","varying"):
            for convention in ("rest","normal-inventory"):
                metadata["conditional_tilt_replays"].append(run_case(
                    a.rei_binary.resolve(),a.rec_binary,source,work,"SHEAR_PLUS",convention,velocity))
        bad = work/"bad.tsv"
        bad.write_text("normal_t_s\tbeta_x\tbeta_y\tbeta_z\n0\t0\t0\t0\n")
        checks = {
            "missing_case": ["MISSING","rest","0","0","0"],
            "luminal_beta": ["ZERO","rest","1","0","0"],
            "short_velocity_series": ["ZERO","rest","--beta-series",str(bad)],
        }
        for key, arguments in checks.items():
            failure = subprocess.run([a.rei_binary.resolve(), source, *arguments, *map(str,E)],
                                     text=True,capture_output=True)
            require(failure.returncode != 0 and not failure.stdout, key)
        metadata["checked_rejections"]=list(checks)
    a.output.write_text(json.dumps(metadata,indent=2,allow_nan=False)+"\n")
if __name__=="__main__":
    main()
