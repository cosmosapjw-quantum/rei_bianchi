"""Fetch small pinned official crate distributions, verify and safely vendor.

This downloads only five pure-Rust numeric/build-support crates plus optional
inari source for inspection. It does not invoke Cargo, build scripts or ODEs.
"""
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import tarfile
import urllib.request

ROOT = Path(__file__).resolve().parent
CRATES = [("num-rational", "0.4.2"), ("num-bigint", "0.4.6"),
          ("num-integer", "0.1.46"), ("num-traits", "0.2.19"),
          ("autocfg", "1.5.0"), ("inari", "2.0.0")]


def fetch(url, cap):
    request = urllib.request.Request(url,
        headers={"User-Agent": "REI-RUN18-bounded-exact-arithmetic/1.0"})
    with urllib.request.urlopen(request, timeout=15) as response:
        data = response.read(cap+1)
    if len(data) > cap:
        raise ValueError("download cap exceeded")
    return data


def main():
    metadata_dir = ROOT/"official_metadata"
    downloads = ROOT/"crate_downloads"
    vendor = ROOT/"vendor"
    for folder in (metadata_dir, downloads, vendor):
        folder.mkdir(exist_ok=True)
    results = []
    for name, version in CRATES:
        stem = f"{name}-{version}"
        api_url = f"https://crates.io/api/v1/crates/{name}/{version}"
        meta_path = metadata_dir/f"{stem}.json"
        metadata = meta_path.read_bytes() if meta_path.exists() else fetch(api_url, 250000)
        parsed = json.loads(metadata)["version"]
        if not meta_path.exists():
            with meta_path.open("xb") as stream:
                stream.write(metadata)
        archive_url = f"https://static.crates.io/crates/{name}/{stem}.crate"
        payload = fetch(archive_url, 300000)
        identity = hashlib.sha256(payload).hexdigest()
        if identity != parsed["checksum"] or len(payload) != parsed["crate_size"]:
            raise ValueError(f"official metadata checksum/size mismatch: {stem}")
        archive_path = downloads/f"{stem}.crate"
        with archive_path.open("xb") as stream:
            stream.write(payload)
        files = []
        with tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz") as archive:
            seen = set()
            expanded_bytes = 0
            for member in archive.getmembers():
                path = PurePosixPath(member.name)
                if (path.is_absolute() or ".." in path.parts or not path.parts or
                        path.parts[0] != stem or str(path) in seen):
                    raise ValueError("unsafe or duplicate archive path")
                seen.add(str(path))
                if member.isdir():
                    continue
                if not member.isfile() or member.size > 2000000:
                    raise ValueError("unexpected archive member type/size")
                expanded_bytes += member.size
                if expanded_bytes > 8000000:
                    raise ValueError("expanded archive cap exceeded")
                raw = archive.extractfile(member).read()
                if len(raw) != member.size:
                    raise ValueError("member size mismatch")
                files.append((path, raw))
        destination = vendor/stem
        destination.mkdir(exist_ok=False)
        checksums = {}
        for path, raw in files:
            relative = PurePosixPath(*path.parts[1:])
            target = destination/str(relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open("xb") as stream:
                stream.write(raw)
            checksums[str(relative)] = hashlib.sha256(raw).hexdigest()
        with (destination/".cargo-checksum.json").open("x") as stream:
            json.dump({"files": checksums, "package": identity}, stream, sort_keys=True)
            stream.write("\n")
        results.append({"crate": name, "version": version, "metadata_url": api_url,
            "metadata_sha256": hashlib.sha256(metadata).hexdigest(),
            "archive_url": archive_url, "archive_bytes": len(payload),
            "archive_sha256": identity, "metadata_checksum_match": True,
            "files": len(files), "expanded_bytes": expanded_bytes,
            "source_directory": str(destination), "build_executed": False,
            "role": "inspection_only_no_GMP_build" if name == "inari" else "exact_arithmetic_dependency",
            "vendor_checksum_metadata": "new standard Cargo vendor checksum map; original package files unchanged"})
        print(json.dumps({"crate": stem, "verified_bytes": len(payload), "files": len(files)}), flush=True)
    receipt = {"schema": "rei.run18.crate-downloads.v1", "packages": results,
        "total_downloaded_crate_bytes": sum(x["archive_bytes"] for x in results),
        "official_metadata_agrees_with_actual_distribution_bytes": True,
        "independent_signature_verification": False,
        "builds": 0, "native_science_calls": 0, "new_installer_attachments": 0}
    with (ROOT/"CRATE_DOWNLOAD_RECEIPT.json").open("x") as stream:
        json.dump(receipt, stream, indent=2)
        stream.write("\n")


if __name__ == "__main__":
    main()
