"""Conservative byte-level matching of tested Rust function bodies across epochs.

Full built crate source identities may differ. This report certifies ONLY the
ten function surfaces explicitly extracted below, never an entire source epoch.
"""
import argparse
import hashlib
import json
from pathlib import Path

SURFACES = {
    "axbi_driver.rs":["pub fn deposit(", "pub fn geometry_map(", "fn ray(",
                      "pub fn new(config: DriverConfig)"],
    "axbi_background.rs":["fn rates(", "pub fn point_at_scale(", "pub fn geometry("],
    "bianchi_i.rs":["fn scaled_components(", "pub fn pullback(", "pub fn snapshot("],
}

def sha(data):
    return hashlib.sha256(data.encode()).hexdigest()

def body(text, keyword):
    start=text.index(keyword)
    index=text.index("{",start)
    depth=0
    for j in range(index,len(text)):
        if text[j]=="{":depth+=1
        elif text[j]=="}":
            depth-=1
            if depth==0:return text[start:j+1]
    raise ValueError("Unbalanced function braces")

def main(current, frozen_file, rlib_file, out):
    old=frozen_file.read_text()
    built=rlib_file.read_text()
    rows=[]
    for filename,needles in SURFACES.items():
        current_text=(current/filename).read_text()
        for needle in needles:
            fn=body(current_text,needle)
            orig=fn in old
            linked=fn in built
            if not orig or not linked:
                raise ValueError("Frozen and linked tested Rust bodies differ: "+filename+" "+needle)
            rows.append({"file":filename,"function":needle,"source_bytes_utf8":len(fn.encode()),
                         "function_sha256":sha(fn),
                         "matches_frozen_source":orig,
                         "matches_compiled_rlib_source":linked})
    result={"schema":"he18.axbi.rust_function_surface_identity.v1",
            "frozen_full_source_identity_sha256":hashlib.sha256(frozen_file.read_bytes()).hexdigest(),
            "rlib_full_source_identity_sha256":hashlib.sha256(rlib_file.read_bytes()).hexdigest(),
            "full_source_epochs_identical":old==built,
            "source_function_count":len(rows),
            "all_ten_tested_function_bytes_equal":all(x["matches_frozen_source"] and
                      x["matches_compiled_rlib_source"] for x in rows),
            "function_surfaces":rows,
            "scientific_scope":"Identical tested function bodies, not whole compiler/artifact identity; original native nine-run executable remains independently SHA-pinned"}
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in (
        "frozen_full_source_identity_sha256","rlib_full_source_identity_sha256",
        "full_source_epochs_identical","source_function_count",
        "all_ten_tested_function_bytes_equal")},indent=2))

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--src",type=Path,required=True)
    p.add_argument("--frozen-source",type=Path,required=True)
    p.add_argument("--compiled-source",type=Path,required=True)
    p.add_argument("--out",type=Path,required=True)
    a=p.parse_args()
    main(a.src,a.frozen_source,a.compiled_source,a.out)
