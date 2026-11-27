#!/usr/bin/env python3
"""Archive an acknowledged PHYS68 science commit and existing evidence only."""
from __future__ import annotations

import argparse
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[3]
WORK = ROOT.parent
NAME = "WU088_HH_PHYS68_SOURCE_AND_EVIDENCE_20261019"
PARENT = "1a149efeba61a9ffd7ea882bdd86f7ea36c0b78c"
SOURCE_PATH = "research/hh_phys34_20261015/inputs/FROZEN_U_SUBSET.npz"
SOURCE_SHA = "f1bd3074950163960cc2011682d013af60f9b17c471bea72ecbc2ffb19e6855d"
PANEL_PATH = "research/hh_phys68_20261019/profiles/PROFILE_PANEL_PAYLOADS_20261019.zip"
PANEL_SHA = "b930a1dff10f656c853d81f7ddc8048e9eb7b188431958cd8c4ca702ca87d1e3"
RUNNERS = (
    ("delivery_phys68/WU088_HH_PHYS68_L64_D2_RUNNER_20261019.zip",
     "b31f72af3101c71fb69036421bbe3542f40e7efca15d391878d5bd47eb0e9580"),
    ("intake_phys68_library/WU088_HH_PHYS66_LONGTAIL_RUNNER_20261019.zip",
     "34a59dfe3158c454811ed6e6f47c82357e502ef8cdef9ee5f14640b37f73a835"),
)


def encode(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False)+"\n").encode()


def sha(data):
    return hashlib.sha256(data).hexdigest()


def command(argv, *, cwd=ROOT, timeout=60, check=True, env=None):
    result = subprocess.run(argv,cwd=cwd,env=env,capture_output=True,timeout=timeout)
    if check and result.returncode:
        raise RuntimeError(f"command failed: {argv!r}: {result.stderr.decode(errors='replace')}")
    return result


def git(*args):
    return command(["git",*args]).stdout


def safe_path(path):
    p=PurePosixPath(path)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError("unsafe archive path")
    if any(part in {"__pycache__",".git",".venv","node_modules"} for part in p.parts):
        raise ValueError("cache, environment or Git internals cannot be payloads")


def dependency_modules(path,data):
    result=set()
    for node in ast.walk(ast.parse(data.decode(),filename=path)):
        names=[]
        if isinstance(node,ast.Import):
            names=[a.name for a in node.names]
        elif isinstance(node,ast.ImportFrom):
            if node.level:
                if not path.startswith("src/wu088_hh/"):
                    continue
                package=path[:-3].split("/")[1:-1]
                package=package[:len(package)-node.level+1]
                module=".".join(package+([node.module] if node.module else []))
            else:
                module=node.module or ""
            names=[module]
            if module=="wu088_hh":
                names.extend(module+"."+a.name for a in node.names if a.name!="*")
        result.update(n for n in names if n=="wu088_hh" or n.startswith("wu088_hh."))
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--science-commit",required=True)
    parser.add_argument("--remote-receipt",type=Path,required=True)
    parser.add_argument("--out",type=Path,required=True)
    parser.add_argument("--receipt",type=Path,required=True)
    args=parser.parse_args()
    started=time.monotonic()
    if args.out.exists() or args.receipt.exists():
        raise FileExistsError("archive and receipt outputs are create-only")
    ack=args.remote_receipt.read_bytes()
    json.loads(ack)
    identity=git("show","-s","--format=%H %T %P",args.science_commit).decode().split()
    commit,tree,*parents=identity
    if commit!=args.science_commit or parents!=[PARENT]:
        raise ValueError("science commit must be the actual direct descendant of the verified PR117 base")
    if commit.encode() not in ack or tree.encode() not in ack:
        raise ValueError("remote ACK must contain both the actual science commit and tree")
    delta=git("diff","--name-only","-z",PARENT,commit).decode().split("\0")[:-1]
    statuses=git("diff","--name-status",PARENT,commit).decode()
    if any(line.startswith(("D\t","R","C")) for line in statuses.splitlines()):
        raise ValueError("this capsule builder expects the reviewed additive/modified delta")
    catalog=set(git("ls-tree","-r","--name-only","-z",commit).decode().split("\0")[:-1])
    paths=set(delta)
    paths.update(p for p in catalog if p.startswith("research/hh_phys68_20261019/"))
    paths.update([
        SOURCE_PATH,"src/wu088_hh/__init__.py",
        "research/hh_phys65_20261018/r5/PROOF.md",
        "research/hh_phys66_20261018/r5/PROOF.md",
        "research/hh_phys66_20261018/local_verification/PROOF.md",
        "research/hh_phys66_20261018/c5c8/REPORT_KO.md",
        "research/hh_phys66_20261018/c5c8/results/PILOT_L28_T65.json",
        "research/hh_phys66_20261018/c5c8/results/PILOT_L28_T65.npz",
        "research/hh_phys67_20261019/first_born/FIRST_BORN_CERTIFICATE.json",
    ])
    # Include available prior proof/report citations without copying provider inventories.
    paths.update(p for p in catalog if p.startswith("research/hh_phys67_20261019/")
                 and (p.endswith("/PROOF.md") or p.endswith("/REPORT_KO.md")))
    payloads={}
    origins={}
    pending=list(sorted(paths))
    while pending:
        path=pending.pop()
        if path in payloads:
            continue
        safe_path(path)
        if path not in catalog:
            raise FileNotFoundError("required source/evidence absent from science commit: "+path)
        data=git("show",commit+":"+path)
        if data.startswith(b"\x7fELF") or path.endswith((".pyc",".pyo")):
            raise ValueError("compiled binary unexpectedly tracked: "+path)
        payloads[path]=data
        origins[path]={"kind":"git_science_commit","commit":commit}
        if path.endswith(".py"):
            for module in dependency_modules(path,data):
                candidate="src/"+module.replace(".","/")+".py"
                if candidate not in catalog:
                    candidate="src/"+module.replace(".","/")+"/__init__.py"
                if candidate in catalog and candidate not in payloads:
                    pending.append(candidate)
                elif module.startswith("wu088_hh.") and candidate not in catalog:
                    # A from-package import may refer to a package attribute.
                    if module.rsplit(".",1)[0]!="wu088_hh":
                        raise FileNotFoundError("unresolved local import: "+module)
    # The original panel ZIP is an immutable external evidence payload, not a
    # tracked Git blob. Its hash was checked before publication and must match.
    panel_bytes=(ROOT/PANEL_PATH).read_bytes()
    payloads[PANEL_PATH]=panel_bytes
    origins[PANEL_PATH]={"kind":"previously_verified_immutable_panel_archive",
                         "sha256":PANEL_SHA,"git_tracked":False}
    if sha(payloads[SOURCE_PATH])!=SOURCE_SHA or sha(panel_bytes)!=PANEL_SHA:
        raise ValueError("protected source or original panel archive identity differs")
    for source,expected in RUNNERS:
        data=(WORK/source).read_bytes()
        if sha(data)!=expected:
            raise ValueError("runner archive identity differs: "+source)
        path="archives/"+Path(source).name
        payloads[path]=data
        origins[path]={"kind":"previously_verified_immutable_runner","sha256":expected}
    payloads["publication/SCIENCE_REMOTE.json"]=ack
    origins["publication/SCIENCE_REMOTE.json"]={"kind":"actual_remote_science_ack"}
    payloads["publication/PHYS68_FULL_INDEX.patch"]=git("diff","--binary","--full-index",PARENT,commit,"--")
    origins["publication/PHYS68_FULL_INDEX.patch"]={"kind":"git_diff","base":PARENT,"head":commit}
    bundle_result={"status":"NOT_ATTEMPTED"}
    with tempfile.TemporaryDirectory(prefix="phys68_bundle_") as temporary:
        bundle=Path(temporary)/"PHYS68_INCREMENTAL.bundle"
        made=command(["git","bundle","create",str(bundle),commit,"^"+PARENT],check=False)
        bundle_result={"create_exit_code":made.returncode,"stdout":made.stdout.decode(errors="replace"),
                       "stderr":made.stderr.decode(errors="replace"),"prerequisite_commit":PARENT}
        if made.returncode==0:
            verified=command(["git","bundle","verify",str(bundle)],check=False)
            bundle_result.update({"verify_exit_code":verified.returncode,
                                  "verify_stdout":verified.stdout.decode(errors="replace"),
                                  "verify_stderr":verified.stderr.decode(errors="replace")})
            if verified.returncode==0:
                data=bundle.read_bytes()
                payloads["publication/PHYS68_INCREMENTAL.bundle"]=data
                origins["publication/PHYS68_INCREMENTAL.bundle"]={"kind":"verified_incremental_git_bundle",
                                                                  "prerequisite_commit":PARENT}
                bundle_result.update({"status":"INCLUDED_VERIFIED","bytes":len(data),"sha256":sha(data)})
            else:
                bundle_result["status"]="UNAVAILABLE_BUNDLE_VERIFY_FAILED_PATCH_AND_SOURCE_INCLUDED"
        else:
            bundle_result["status"]="UNAVAILABLE_BUNDLE_CREATE_FAILED_PATCH_AND_SOURCE_INCLUDED"
    readme=("# PHYS68 source and evidence\n\n"
            f"Science commit: `{commit}`\n\nTree: `{tree}`\n\nParent: `{PARENT}`\n\n"
            "All Git-origin payloads were read from the acknowledged science Git object. "
            "The separately hash-locked original panel ZIP is external evidence. "
            "Later publication/backup acknowledgements belong to the outer DELIVERY.\n\n"
            "The 78 original panel JSON payloads remain compressed in "
            "`research/hh_phys68_20261019/profiles/PROFILE_PANEL_PAYLOADS_20261019.zip`. "
            "Extract this archive into its containing profiles directory to reconstruct "
            "the original and completed run directories. This is byte restoration only.\n\n"
            "The complete implemented optional L64 runner and unchanged PHYS66 six-case "
            "longtail runner are in `archives/`. Both are PREPARED_NOT_SUBMITTED here. "
            "Read their instructions and reconcile existing host receipts before execution.\n\n"
            "Existing PHYS64 runs, completed PHYS68 L28 panels, native Rust reference runs "
            "and earlier passed suites must be reused. This packaging step ran none of them.\n\n"
            "The full-index binary patch applies to the exact parent above. "
            "Any included incremental Git bundle requires that parent and its history. "
            "Manifest entries identify source origin, bytes and SHA256.\n\nHH_R10=OFF.\n")
    payloads["README_SOURCE_AND_EVIDENCE.md"]=readme.encode()
    origins["README_SOURCE_AND_EVIDENCE.md"]={"kind":"packaging_description"}
    manifest={"schema":"WU088_HH_PHYS68_SOURCE_CAPSULE_V1","science_commit":commit,
              "science_tree":tree,"parent_commit":PARENT,"git_delta_paths":delta,
              "source_sha256":SOURCE_SHA,"panel_archive_sha256":PANEL_SHA,
              "bundle":bundle_result,"HH_R10":"OFF","science_reruns":0,
              "manifest_excludes_itself":True,
              "payloads":[{"path":p,"bytes":len(d),"sha256":sha(d),"origin":origins[p]}
                          for p,d in sorted(payloads.items())]}
    payloads["MANIFEST.json"]=encode(manifest)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(args.out,"x",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for path,data in sorted(payloads.items()):
            item=zipfile.ZipInfo(NAME+"/"+path,(2026,10,19,0,0,0))
            item.compress_type=zipfile.ZIP_DEFLATED;item.external_attr=0o100644<<16
            archive.writestr(item,data,compresslevel=9)
    restore_checks=[]
    with tempfile.TemporaryDirectory(prefix="phys68_source_restore_") as temporary:
        with zipfile.ZipFile(args.out) as archive:
            if archive.testzip() is not None:
                raise ValueError("source archive CRC mismatch")
            for name in archive.namelist():
                safe_path(name)
            archive.extractall(temporary)
        restored=Path(temporary)/NAME
        for entry in manifest["payloads"]:
            data=(restored/entry["path"]).read_bytes()
            if len(data)!=entry["bytes"] or sha(data)!=entry["sha256"]:
                raise ValueError("clean restore payload identity mismatch")
        environment=dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"]="1"
        environment["PYTHONPATH"]=str(restored/"src")
        modules=sorted(p[4:-3].replace("/",".") for p in payloads
                       if p.startswith("src/") and p.endswith(".py") and not p.endswith("/__init__.py"))
        program="import importlib,json; names="+repr(modules)+"; [importlib.import_module(n) for n in names]; print(json.dumps({'imports':names,'scientific_executions':0}))"
        checked=command([sys.executable,"-c",program],cwd=restored,env=environment,timeout=30)
        restore_checks.append({"kind":"all_packaged_source_module_imports","exit_code":checked.returncode,
                               "stdout":checked.stdout.decode(),"stderr":checked.stderr.decode()})
    final=args.out.read_bytes()
    receipt={"schema":"WU088_HH_PHYS68_SOURCE_CAPSULE_BUILD_AND_RESTORE_V1",
             "created_utc":datetime.now(timezone.utc).isoformat(),
             "elapsed_seconds":time.monotonic()-started,"archive":str(args.out.resolve()),
             "bytes":len(final),"sha256":sha(final),"science_commit":commit,"science_tree":tree,
             "parent_commit":PARENT,"payload_count_excluding_manifest":len(manifest["payloads"]),
             "status":"PASS_MANIFEST_HASH_SIZE_IMPORT_ONLY","restore_checks":restore_checks,
             "bundle":bundle_result,"science_reruns":0,"tests_rerun":0,"NCP_submissions":0,
             "HH_R10":"OFF"}
    args.receipt.parent.mkdir(parents=True,exist_ok=True)
    with args.receipt.open("xb") as stream:
        stream.write(encode(receipt))
    print(encode(receipt).decode(),end="")


if __name__=="__main__":
    main()
