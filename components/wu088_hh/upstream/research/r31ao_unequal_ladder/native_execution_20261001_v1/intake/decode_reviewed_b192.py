#!/usr/bin/env python3
"""Decode only the independently reviewed B192 bytes with the immutable decoder.

This is exact represented-data intake, not a continuum accuracy certificate.
Run under the existing 20-second / 1024-MiB process guard. Output is create-only.
"""
import argparse
from dataclasses import asdict
from fractions import Fraction
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import zipfile


REVIEW_SHA = "4c0b99329c13e9462bc66fcfc8b7bed902f98a20a46d08589423716ddf62cbb2"
DECODER_SHA = "bf1867616af07a670d61cd75c7ca0655c99e0be13fd6a73e9a4654f5fc0986f1"
ARCHIVES = {
    "OD_ASSEMBLED_OD.npz": "7e7b5782cc698a364aeac608620e56c7bfdc64035ffe5dfee501608dae7970df",
    "independent_JVP_ASSEMBLED.npz": "53569e92875254e897a7e23b55620cca9c5acf9f86124dc0a73198ad41d1df87",
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, value):
    with path.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        stream.write("\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    review_path = here.parent / "review/B192_BYTE_AND_SOURCE_REVIEW.json"
    review_bytes = review_path.read_bytes()
    if digest(review_bytes) != REVIEW_SHA:
        raise ValueError("Independent review bytes do not match the admitted receipt")
    review = json.loads(review_bytes)
    if (review["schema"] != "WU088_INDEPENDENT_B192_SOURCE_AND_BYTE_ABI_REVIEW_V1"
            or review["bounded_historical_layout_admitted"] is not True
            or review["status"] != "PASS_BOUNDED_HISTORICAL_LAYOUT_INFERENCE"):
        raise ValueError("Bounded historical review did not pass")
    approved = {r["archive"]: r["archive_sha256"] for r in review["npz_member_binding_observations"]}
    if approved != ARCHIVES:
        raise ValueError("Review scope differs from the two frozen archives")
    for name, expected in review["evidence_files_sha256"].items():
        path = here / ("evidence/" + name if name.startswith("historical_metadata/") else name)
        if digest(path.read_bytes()) != expected:
            raise ValueError("Review evidence hash changed: " + name)
    bindings_bytes = (here / "B192_MEMBER_BINDINGS.json").read_bytes()
    bindings = json.loads(bindings_bytes)
    decoder_path = here.parents[1] / "gap_closure_20261001_g0_g6_v1/exact_raw_decoder/decoder.py"
    if digest(decoder_path.read_bytes()) != DECODER_SHA:
        raise ValueError("Immutable decoder source hash changed")
    spec = importlib.util.spec_from_file_location("wu088_reviewed_exact_decoder", decoder_path)
    decoder = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = decoder
    spec.loader.exec_module(decoder)
    layout = review["admitted_layout"]
    if layout != {"byte_order": "little", "complex_component_order": "real_imag", "component_bytes": 16,
                  "format": "x87_80", "padding_policy": "Preserve raw bytes; ignore six padding bytes numerically",
                  "value_offset": 0}:
        raise ValueError("Unexpected reviewed layout")
    raw_hashes = {name: digest((args.raw_dir / name).read_bytes()) for name in ARCHIVES}
    if raw_hashes != ARCHIVES:
        raise ValueError("Raw archive identity mismatch")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    start = time.monotonic_ns()
    rows, skipped, arrays, authority_records = [], [], {}, []
    for record in bindings["records"]:
        filename = record["local_basename"]
        if filename not in ARCHIVES or record["sha256"] != ARCHIVES[filename]:
            raise ValueError("Member index archive identity mismatch")
        with zipfile.ZipFile(args.raw_dir / filename) as archive:
            indexed = {item["member"]: item for item in record["npy_members"]}
            if set(archive.namelist()) != set(indexed):
                raise ValueError("Archive members differ from reviewed scope")
            destination = args.output_dir / record["role"]
            destination.mkdir()
            for member, item in indexed.items():
                content = archive.read(member)
                if digest(content) != item["sha256"]:
                    raise ValueError("NPY member identity mismatch: " + member)
                if item["header"]["descr"] == "<i8" and member == "n.npy":
                    skipped.append({"archive": filename, "member": member, "reason": "Integer metadata is outside floating decoder API; byte binding preserved", "sha256": item["sha256"]})
                    continue
                header = decoder.inspect_npy_header(content, max_elements=4096)
                authority = None
                if header.descr in ("<c32", "<f16"):
                    authority = decoder.LayoutAuthority(
                        layout="x87_80", byte_order="little", component_bytes=16, value_offset=0,
                        complex_component_order="real_imag", scope="HISTORICAL_PRODUCER_LAYOUT_REVIEWED",
                        evidence_id="WU088_INDEPENDENT_B192_SOURCE_AND_BYTE_ABI_REVIEW_V1:" + REVIEW_SHA,
                        evidence_sha256=(REVIEW_SHA, digest(bindings_bytes), review["evidence_files_sha256"]["ABI_LAYOUT_EVIDENCE_CHAIN.json"]),
                        bound_npy_sha256=item["sha256"])
                    authority_records.append({"archive": filename, "member": member, **asdict(authority)})
                decoded = decoder.decode_npy_bytes(content, authority=authority, max_elements=4096)
                if decoded.payload_sha256 != item["payload_sha256"]:
                    raise ValueError("Payload identity mismatch")
                arrays[(record["role"], member)] = decoded
                # Use the frozen decoder's canonical dyadic serialization, never a float cast.
                values = []
                for value in decoded.values_c_order:
                    real, imaginary = value if isinstance(value, tuple) else (value, Fraction(0))
                    values.append([decoder._canonical_dyadic(real), decoder._canonical_dyadic(imaginary)])
                document = {"schema": "EXACT_DYADIC_ARRAY_V1", "shape": list(decoded.shape), "values": values}
                canonical_bytes = json.dumps(document, sort_keys=True, separators=(",", ":")).encode("ascii")
                if digest(canonical_bytes) != decoded.canonical_sha256:
                    raise ValueError("Canonical export hash mismatch")
                stem = Path(member).name.removesuffix(".npy")
                write_json(destination / (stem + ".exact_dyadic.json"), document)
                write_json(destination / (stem + ".provenance.json"), {
                    "header": asdict(decoded.header), "raw_npy_sha256": decoded.raw_npy_sha256,
                    "payload_sha256": decoded.payload_sha256, "canonical_sha256": decoded.canonical_sha256,
                    "negative_zero_c_order": decoded.negative_zero_c_order,
                    "padding_hex_c_order": decoded.padding_hex_c_order,
                    "authority_scope": decoded.authority_scope, "authority_evidence_id": decoded.authority_evidence_id})
                rows.append({"archive": filename, "member": member, "elements": header.element_count,
                             "raw_npy_sha256": decoded.raw_npy_sha256, "canonical_sha256": decoded.canonical_sha256,
                             "source_fortran_order": header.fortran_order, "dtype": header.descr})
    if arrays[("independent_JVP", "z.npy")].values_c_order != (Fraction(3, 4),):
        raise ValueError("Decoded historical JVP literal disagrees with locked 3/4")
    overlap = arrays[("OD", "O.npy")].values_c_order
    transpose = arrays[("OD", "O_row.npy")].values_c_order
    for channel in range(47):
        for cusp in range(2):
            real, imaginary = overlap[channel * 2 + cusp]
            if transpose[cusp * 47 + channel] != (real, -imaginary):
                raise ValueError("C/F exact conjugate-transpose consistency failed")
    if {name: digest((args.raw_dir / name).read_bytes()) for name in ARCHIVES} != ARCHIVES:
        raise ValueError("Raw archives changed during decode")
    write_json(args.output_dir / "PER_NPY_LAYOUT_AUTHORITIES.json", authority_records)
    summary = {"schema": "WU088_ACTUAL_B192_EXACT_DECODE_V1", "status": "PASS_BOUNDED_EXACT_RAW_DECODE",
               "scope": "Two exact reviewed B192 archive identities; represented values only",
               "review_sha256": REVIEW_SHA, "decoder_sha256": DECODER_SHA, "decoded_members": rows,
               "decoded_member_count": len(rows), "decoded_logical_elements": sum(r["elements"] for r in rows),
               "metadata_only_members": skipped, "exact_jvp_z_equals_3_over_4": True,
               "exact_od_conjugate_transpose_pairs": 94, "host_float_casts": 0, "numpy_imports": 0,
               "raw_archives_unchanged": True, "historical_layout_scope": "BOUNDED_REVIEWED_SOURCE_AND_BYTE_PROVENANCE",
               "historical_wheel_fidelity_claimed": False, "native_calls": 0, "integrations": 0,
               "machine_predicate_replays": 0, "continuum_error_certified": False, "production_admitted": False,
               "elapsed_ns": time.monotonic_ns() - start}
    write_json(args.output_dir / "DECODE_RESULT.json", summary)
    manifest = [{"path": str(p.relative_to(args.output_dir)), "bytes": p.stat().st_size, "sha256": digest(p.read_bytes())}
                for p in sorted(args.output_dir.rglob("*")) if p.is_file()]
    write_json(args.output_dir / "FILE_HASHES.json", manifest)
    print(json.dumps({key: summary[key] for key in ["status", "decoded_member_count", "decoded_logical_elements", "host_float_casts", "elapsed_ns"]}))


if __name__ == "__main__":
    main()
