"""Create an immutable donor from the restored R15 NPZ or actual AXBI CSV.

No chemistry integration is performed. A new directory is mandatory.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
from pathlib import Path

import numpy as np

from electron_donor import ElectronDonor, SCHEMA, INTERPOLATION, sha256_file
from bindings import load_runner

R15_SHA = "93d16f478d2cc28b1f7b3d5287f07432b0e17107b3dd3f684890e77f6133cfa4"


def write_bundle(out, columns, *, density_unit, density_frame, provenance):
    donor = ElectronDonor.from_arrays(**columns, density_unit=density_unit,
                    density_frame=density_frame, provenance=provenance)
    out = Path(out)
    out.mkdir(parents=True, exist_ok=False)
    data = out/"history.npz"
    with data.open("xb") as stream:
        np.savez_compressed(stream, **columns)
        stream.flush()
        os.fsync(stream.fileno())
    manifest = dict(schema=SCHEMA, interpolation=INTERPOLATION, data_file=data.name,
                    data_sha256=sha256_file(data), identity_sha256=donor.identity,
                    density_unit=density_unit, density_frame=density_frame,
                    provenance=provenance, report=donor.report())
    load_runner().atomic_json(out/"manifest.json", manifest, replace=False)
    # This readback checks the written bundle, not the source chemistry.
    recovered = ElectronDonor.load(out/"manifest.json")
    if recovered.identity != donor.identity:
        raise RuntimeError("donor bundle readback identity failure")
    return manifest


def from_r15(path, out):
    if sha256_file(path) != R15_SHA:
        raise ValueError("the selected actual R15 history SHA does not match")
    with np.load(path, allow_pickle=False) as raw:
        a = 1/(1+raw["z"])
        he_h = .2453/(4*(1-.2453))
        columns = dict(a=a, nH=raw["nH_cm3"], nHe=raw["nH_cm3"]*he_h,
                       xHII=raw["Q"], xHeII=raw["Q"], xHeIII=np.zeros_like(a),
                       ne_reference=raw["ne_cm3"])
    provenance = dict(kind="actual_history", source_sha256=R15_SHA,
        repository="cosmosapjw-quantum/rei_bianchi",
        commit="f66929c23ea3fa6e39dd4808e5b27d136c568a03",
        path="research/broad_history_20261010/evidence/RUN002/flrw_n16384/history.npz",
        closure="R15 emissivity; HG97 Case-B; Q filling factor; HII+HeII inside; neutral outside; T=20000K; C=3; HeIII=0; no residual electrons",
        donor_geometry="original flat FLRW h=.6774 Omega_m=.309; one-way prescription in target mean a",
        source_status="COMPUTED_SCOPED_NOT_YET_REVIEWED in original COMPLETE; restored-byte and input-projection checks reused",
        source_domain="mean-volume z20 to z4", helium_to_hydrogen_number=he_h)
    return write_bundle(out, columns, density_unit="cm^-3", density_frame="proper",
                        provenance=provenance)


def from_axbi(path, out, provenance_path, helium_to_hydrogen):
    provenance = json.loads(Path(provenance_path).read_text())
    expected = provenance.get("source_sha256")
    if sha256_file(path) != expected:
        raise ValueError("actual AXBI input SHA differs from provenance")
    if not np.isfinite(helium_to_hydrogen) or not 0 < helium_to_hydrogen < 1:
        raise ValueError("explicit source nHe/nH abundance required")
    names = ["a", "nH_proper_cm3", "x_HII", "x_HeII", "x_HeIII", "ne_proper_cm3"]
    with Path(path).open(newline="") as stream:
        reader = csv.DictReader(stream)
        if not set(names).issubset(reader.fieldnames or []):
            raise ValueError("AXBI source header differs from the reviewed contract")
        indices = [reader.fieldnames.index(name) for name in names]
    # Parse only the six numeric columns; avoid a large Python list of rows.
    rows = np.loadtxt(path, delimiter=",", skiprows=1, usecols=indices, ndmin=2)
    if rows.ndim != 2 or rows.shape[1] != len(names):
        raise ValueError("empty or malformed AXBI history")
    columns = dict(a=rows[:,0], nH=rows[:,1], nHe=rows[:,1]*helium_to_hydrogen,
                   xHII=rows[:,2], xHeII=rows[:,3], xHeIII=rows[:,4],
                   ne_reference=rows[:,5])
    provenance = dict(provenance, helium_to_hydrogen_number=helium_to_hydrogen)
    return write_bundle(out, columns, density_unit="cm^-3", density_frame="proper",
                        provenance=provenance)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="kind", required=True)
    r15 = sub.add_parser("r15")
    r15.add_argument("--source", type=Path, required=True)
    r15.add_argument("--out", type=Path, required=True)
    axbi = sub.add_parser("axbi")
    axbi.add_argument("--source", type=Path, required=True)
    axbi.add_argument("--out", type=Path, required=True)
    axbi.add_argument("--provenance", type=Path, required=True)
    axbi.add_argument("--helium-to-hydrogen", type=float, required=True)
    args = parser.parse_args()
    result = (from_r15(args.source, args.out) if args.kind == "r15" else
              from_axbi(args.source, args.out, args.provenance, args.helium_to_hydrogen))
    print(json.dumps(result["report"], indent=2))


if __name__ == "__main__":
    main()
