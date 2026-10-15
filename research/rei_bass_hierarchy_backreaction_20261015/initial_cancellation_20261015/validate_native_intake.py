"""Test compiled native Rust science intake and negative physical corruptions.

The source CSV remains untouched. Two counterexamples are made in a temporary
directory then rejected by the SAME compiled stdlib-only Rust consumer.
"""
from __future__ import annotations
import csv,hashlib,json,subprocess,tempfile,io
from pathlib import Path

HERE=Path(__file__).resolve().parent
CSV=HERE/"evidence/REI_SIGMA_PI_BACKGROUND_3864.csv"
SOURCE=HERE/"rust_pi_supplier_consumer.rs"

def run(out):
    if out.exists():raise FileExistsError(out)
    contract=json.loads((HERE/"evidence/REI_SIGMA_PI_SUPPLIER_CONTRACT.json").read_text())
    sha=lambda x:hashlib.sha256(x.read_bytes()).hexdigest()
    original_sha=sha(CSV)
    if original_sha!=contract["csv_sha256"]:
        raise RuntimeError("ORIGINAL_TABLE_BYTE_SHA_MISMATCH")
    with tempfile.TemporaryDirectory(prefix="rei_initial_pi_native_consumer_") as temp:
        tmp=Path(temp);exe=tmp/"consumer"
        compile=subprocess.run(["rustc","--edition=2021","-O",str(SOURCE),"-o",str(exe)],
                               capture_output=True,text=True)
        if compile.returncode!=0:raise RuntimeError(compile.stderr[-1600:])
        positive=subprocess.run([str(exe),str(CSV)],capture_output=True,text=True)
        if positive.returncode!=0:raise RuntimeError(positive.stderr[-1500:])
        receipt=json.loads(positive.stdout)
        if receipt["rows"]!=3864 or receipt["cases"]!=24:
            raise AssertionError("WRONG_STRESS_HISTORY_ROWS")
        original_text=CSV.read_text().splitlines()
        header=original_text[0].split(",")
        checks=[]
        for field,mult,expected in [
          # H tampering is caught earlier by the shear-scalar invariant.
          ("H_per_s",1.05,"PUBLIC_SCALAR_SIGMA_CONTRACT"),
          # Changing dust while leaving measured H/shear unchanged reaches
          # the independent Einstein Hamiltonian constraint directly.
          ("dust_energy_norm",1.05,"EINSTEIN_HAMILTONIAN_CONSTRAINT"),
          ("Pi_total_Pa",2.,"PI_TENSOR_AMPLITUDE_CLOSURE")]:
            lines=original_text.copy()
            i=header.index(field)
            # row 400 is physical source with nonzero initial and evolved stress.
            rr=lines[400].split(",")
            if len(rr)!=len(header):raise RuntimeError("BAD_CSV_TEST_FIXTURE")
            rr[i]=repr(float(rr[i])*mult)
            lines[400]=",".join(rr)
            candidate=tmp/(field+".csv")
            candidate.write_text("\n".join(lines)+"\n")
            negative=subprocess.run([str(exe),str(candidate)],capture_output=True,text=True)
            if negative.returncode!=3 or expected not in negative.stderr:
                raise AssertionError(f"NATIVE_CORRUPTED_{field}_WAS_NOT_REJECTED:{negative.stderr[-200:]}")
            checks.append({"altered_field":field,"factor":mult,"exit":negative.returncode,
                           "expected":expected,"observed_rejection":negative.stderr.strip()})
    if sha(CSV)!=original_sha:raise RuntimeError("ORIGINAL_REI_SOURCE_TABLE_ALTERED")
    d={"schema":"rei.initial_pi.native_Rust_consumer_positive_negative.v1",
        "input_sha256":original_sha,
        "rust_source_sha256":sha(SOURCE),
        "positive_exit":positive.returncode,
        "native_positive_result":receipt,
        "negative_checks":checks,
        "source_frozen_readback":True,
        "original_axbi_driver_edited":False,
        "scientific_admission":"scoped Einstein Vlasov source-table intake, not production native chemistry"}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(d,indent=2)+"\n")
    print(json.dumps({k:v for k,v in d.items() if k!="negative_checks"},indent=2))
    print("NEGATIVE_INJECTION_REJECTED",len(checks))
    return d

if __name__=="__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path,required=True)
    run(p.parse_args().output)
