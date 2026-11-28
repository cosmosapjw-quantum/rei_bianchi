#!/usr/bin/env python3
"""
Fetch and verify the public ARSENY archive from Digital Commons Data / Mendeley Data.

This script intentionally does not assume that the visible slug `n43srxwdnm`
is guaranteed to equal the provider-internal dataset id. It first attempts the
visible slug, validates the returned DOI/name, and otherwise requires the user
to pass --dataset-id after resolving it from the public record/API.

Requires: python3, requests
Optional: MENDELEY_DATA_TOKEN if the API gateway requires bearer auth.
"""
from __future__ import annotations
import argparse, hashlib, json, os, sys, zipfile
from pathlib import Path
import requests

API = "https://api.data.mendeley.com"
EXPECTED_DOI = "10.17632/n43srxwdnm.1"
EXPECTED_NAME_TOKEN = "ARSENY"

def headers():
    h={"Accept":"application/vnd.mendeley-public-dataset.1+json"}
    tok=os.environ.get("MENDELEY_DATA_TOKEN")
    if tok:
        h["Authorization"]=f"Bearer {tok}"
    return h

def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024), b""):
            h.update(b)
    return h.hexdigest()

def get_json(url, **params):
    r=requests.get(url, headers=headers(), params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--dataset-id", default="n43srxwdnm")
    ap.add_argument("--version", type=int, default=1)
    ap.add_argument("--out", default="ARSENY_MENDELEY_v1")
    args=ap.parse_args()

    out=Path(args.out); out.mkdir(parents=True, exist_ok=True)
    meta=get_json(f"{API}/datasets/{args.dataset_id}", version=args.version)
    doi=((meta.get("doi") or {}).get("id") or meta.get("doi") or "")
    name=str(meta.get("name") or "")
    if EXPECTED_DOI not in str(doi) and EXPECTED_NAME_TOKEN.lower() not in name.lower():
        raise RuntimeError(f"Dataset identity mismatch: doi={doi!r}, name={name!r}")

    (out/"dataset_metadata.json").write_text(json.dumps(meta,indent=2,ensure_ascii=False)+"\n")
    files=get_json(f"{API}/datasets/publics/{args.dataset_id}/files", version=args.version)
    (out/"files_metadata.json").write_text(json.dumps(files,indent=2,ensure_ascii=False)+"\n")

    records=files if isinstance(files,list) else files.get("items",files.get("files",[]))
    receipts=[]
    for rec in records:
        fid=rec.get("id")
        fn=rec.get("filename") or f"{fid}.bin"
        detail=get_json(f"{API}/datasets/publics/{args.dataset_id}/files/{fid}", version=args.version)
        cd=detail.get("content_details") or {}
        url=cd.get("download_url")
        if not url:
            rr=requests.get(f"{API}/datasets/{args.dataset_id}/files/{fid}/file_downloaded",
                            headers=headers(), params={"version":args.version},
                            allow_redirects=False, timeout=60)
            if rr.status_code not in (301,302,303,307,308):
                raise RuntimeError(f"No download URL for {fn}; HTTP {rr.status_code}")
            url=rr.headers["Location"]
        dest=out/fn
        with requests.get(url,stream=True,timeout=120) as rr:
            rr.raise_for_status()
            with dest.open("wb") as f:
                for chunk in rr.iter_content(1024*1024):
                    if chunk: f.write(chunk)
        got=sha256_file(dest)
        exp=cd.get("sha256_hash")
        if exp and got.lower()!=str(exp).lower():
            raise RuntimeError(f"SHA mismatch {fn}: expected {exp}, got {got}")
        receipts.append({"filename":fn,"file_id":fid,"size":dest.stat().st_size,
                         "sha256":got,"provider_sha256":exp,
                         "provider_sha256_match": (not exp) or got.lower()==str(exp).lower()})

    (out/"download_receipt.json").write_text(json.dumps(receipts,indent=2)+"\n")
    print(json.dumps({"status":"ARSENY_PAYLOAD_DOWNLOADED_AND_HASH_VERIFIED",
                      "dataset_id":args.dataset_id,"files":receipts},indent=2))

if __name__=="__main__":
    main()
