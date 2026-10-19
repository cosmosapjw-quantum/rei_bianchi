#!/usr/bin/env python3
"""Fetch and compare only the published RUN17 delivery delta; no science execution."""
import argparse, datetime, hashlib, json, os, platform, stat, subprocess, sys, time
from pathlib import Path, PurePosixPath
SCIENCE="589ffbaff7b74a6cf1dbaf797285f15a58131dbd"
DELIVERY="0e23addf4fefa69287d4626622bf97505677ea43"
TREE="a9a51ff2680454ea65fbcec8bc781a9b936f4a05"
PREFIX="research/atomic_nuclear_ssot_20261017/run17/"
SCIENCE_MANIFEST_SHA="256b084717e1039da6cdc1ac53d44d726c0f0a85f06a02387639a0db53dfaae7"
def ident(b):
    return {"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest(),"git_blob":hashlib.sha1(b"blob "+str(len(b)).encode()+b"\0"+b).hexdigest()}
def ordinary(p):
    if not stat.S_ISREG(p.lstat().st_mode): raise ValueError("not ordinary: "+str(p))
    return p.read_bytes()
def safe(s):
    if not s or "\\" in s or PurePosixPath(s).is_absolute() or any(x in ("",".","..") for x in s.split("/")):raise ValueError("unsafe path")
    return s
def write(p,b):
    with p.open("xb") as f:f.write(b)
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--repo",type=Path,required=True);ap.add_argument("--canonical",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);a=ap.parse_args()
    repo=a.repo.resolve();canonical=a.canonical.resolve();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
    report={"schema":"rei.run18.prior-run17-delivery-readback.v1","started_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),"science_commit":SCIENCE,"delivery_commit":DELIVERY,"delivery_tree":TREE,"repository":"cosmosapjw-quantum/rei_bianchi","checkout":str(repo),"canonical_run17":str(canonical),"commands":[],"environment":{"python":sys.version,"executable":sys.executable,"platform":platform.platform(),"GIT_OPTIONAL_LOCKS":"0"},"execution_counts":{"new_tests":0,"native_builds":0,"RHS":0,"quadratures":0,"IVPs":0,"certificate_replay":0},"invocation":[sys.executable,"-B",*sys.argv]}
    env=dict(os.environ);env["GIT_OPTIONAL_LOCKS"]="0"
    def run(label,parts,data=None,record_content=True):
        cmd=["git","-C",str(repo),*parts];t=time.monotonic();p=subprocess.run(cmd,input=data,capture_output=True,env=env)
        row={"argv":cmd,"exit_code":p.returncode,"wall_seconds":time.monotonic()-t,"stdout_identity":ident(p.stdout),"stderr_identity":ident(p.stderr)}
        if record_content:
            name=label+".stdout";write(out/name,p.stdout);row["stdout"]=name
        else:row["stdout_storage"]="hash only; exact object bytes parsed and compared in memory"
        name=label+".stderr";write(out/name,p.stderr);row["stderr"]=name
        if data is not None:
            name=label+".stdin";write(out/name,data);row["stdin"]=name;row["stdin_identity"]=ident(data)
        report["commands"].append(row)
        if p.returncode:raise RuntimeError("Git command failed: "+label)
        return p.stdout
    try:
        head_before=run("head_before",["rev-parse","HEAD","HEAD^{tree}"]).decode().splitlines()
        if head_before[0]!=SCIENCE:raise ValueError("preserved checkout not on science commit")
        ip=Path(run("index_path",["rev-parse","--git-path","index"]).decode().strip());ip=ip if ip.is_absolute() else repo/ip;index_before=ident(ordinary(ip))
        run("fetch_delivery",["fetch","--depth=1","--filter=blob:none","--no-tags","origin",DELIVERY])
        actual=run("delivery_ref",["rev-parse",DELIVERY,DELIVERY+"^{tree}"]).decode().splitlines()
        if actual!=[DELIVERY,TREE]:raise ValueError("delivery object identity mismatch")
        raw=run("delivery_delta",["diff-tree","--no-commit-id","--raw","-r","-z",SCIENCE,DELIVERY]);t=raw.split(b"\0");delta=[];i=0
        while i<len(t) and t[i]:
            m=t[i].decode().lstrip(":").split();name=t[i+1].decode();i+=2
            oldmode,mode,old,new,status=m
            if status!="A" or oldmode!="000000" or old!="0"*40 or not name.startswith(PREFIX):raise ValueError("not add-only run17 delta")
            rel=safe(name[len(PREFIX):])
            if mode not in ("100644","100755"):raise ValueError("nonordinary Git mode")
            delta.append({"path":rel,"git_mode":mode,"git_blob":new})
        if len(delta)!=44 or len({x["path"] for x in delta})!=44:raise ValueError("expected44uniqueadditions")
        rawtree=run("delivery_tree",["ls-tree","-r","-z","--full-tree",DELIVERY,"--",PREFIX.rstrip("/")]);tree={}
        for row in rawtree.split(b"\0"):
            if not row:continue
            m,name=row.split(b"\t",1);mode,kind,blob=m.decode().split();rel=safe(name.decode()[len(PREFIX):]);tree[rel]={"mode":mode,"type":kind,"blob":blob}
        if len(tree)!=155:raise ValueError("expected111science+44deliverytree")
        for row in delta:
            if tree[row["path"]]!={"mode":row["git_mode"],"type":"blob","blob":row["git_blob"]}:raise ValueError("delta/tree mismatch")
        ids=list(dict.fromkeys([r["git_blob"] for r in delta]+[tree["SCIENCE_MANIFEST.json"]["blob"]]))
        batch=run("delivery_blobs",["cat-file","--batch"],("\n".join(ids)+"\n").encode(),False);blobs={};offset=0
        for expected in ids:
            end=batch.index(b"\n",offset);header=batch[offset:end].decode().split()
            if len(header)!=3 or header[0]!=expected or header[1]!="blob":raise ValueError("unexpected blob header")
            n=int(header[2]);data=batch[end+1:end+1+n];offset=end+1+n
            if batch[offset:offset+1]!=b"\n" or ident(data)["git_blob"]!=expected:raise ValueError("blob framing/hash mismatch")
            offset+=1;blobs[expected]=data
        if offset!=len(batch):raise ValueError("extra blob batch bytes")
        sci=blobs[tree["SCIENCE_MANIFEST.json"]["blob"]]
        if ident(sci)["sha256"]!=SCIENCE_MANIFEST_SHA or sci!=ordinary(canonical/"SCIENCE_MANIFEST.json"):raise ValueError("science manifest changed")
        dmrow=next(x for x in delta if x["path"]=="DELIVERY_MANIFEST.json");dmraw=blobs[dmrow["git_blob"]];dm=json.loads(dmraw)
        if dm.get("schema")!="rei.run17.delivery-manifest.v1" or not dm.get("excludes_itself") or dm["science_commit"]!=SCIENCE or dm["payload_files"]!=43:raise ValueError("delivery manifest contract")
        manifest={r["path"]:r for r in dm["files"]}
        if len(manifest)!=43 or set(manifest)|{"DELIVERY_MANIFEST.json"}!={r["path"] for r in delta}:raise ValueError("delivery manifest membership")
        checks=[]
        for row in delta:
            rel=row["path"];data=blobs[row["git_blob"]];c=canonical/rel;actual=ident(data)
            if data!=ordinary(c):raise ValueError("canonical byte mismatch: "+rel)
            filesystem_mode=stat.S_IMODE(c.stat().st_mode)
            if filesystem_mode!=(0o755 if row["git_mode"]=="100755" else 0o644):raise ValueError("canonical filesystem mode mismatch: "+rel)
            if rel in manifest:
                e=manifest[rel]
                if any(actual[k]!=e[k] for k in ("bytes","sha256","git_blob")) or row["git_mode"]!=e["git_mode"]:raise ValueError("manifest identity mismatch: "+rel)
            checks.append({**row,**actual,"canonical_mode":format(filesystem_mode,"04o"),"canonical_byte_match":True,"manifest_match":True})
        if sum(x["bytes"] for x in checks if x["path"]!="DELIVERY_MANIFEST.json")!=dm["payload_bytes"]:raise ValueError("manifest byte sum mismatch")
        run("tracked_diff_after",["diff","--exit-code"]);run("cached_diff_after",["diff","--cached","--exit-code"])
        head_after=run("head_after",["rev-parse","HEAD","HEAD^{tree}"]).decode().splitlines();index_after=ident(ordinary(ip))
        if head_after!=head_before or index_after!=index_before:raise ValueError("existing worktree HEAD/index changed")
        report.update({"status":"VERIFIED_RUN17_DELIVERY44_FROM_GIT","new_delivery_files":checks,"file_count":44,"payload_bytes_including_manifest":sum(x["bytes"] for x in checks),"delivery_manifest":ident(dmraw),"science111_preserved":{"delta_additions_only":True,"modified_or_deleted_paths":0,"science_manifest":ident(sci),"method":"Global diff contains only44new run17 paths; original science manifest SHA and canonical bytes unchanged. No old science payload hashing rerun."},"unchanged_checkout":{"HEAD_before_after":head_before,"index_before":index_before,"index_after":index_after,"tracked_diff_empty":True,"cached_diff_empty":True,"canonical_writes":0},"scope_limits":["No science/test/build/IVP replay.","Remote blob batch content was compared exactly with canonical files and persisted by content identities; unchanged canonical/remote Git retain original bytes."],"next_parent_for_RUN18":DELIVERY})
        exit_code=0
    except Exception as e:
        report.update({"status":"BLOCKED_RUN17_DELIVERY_READBACK","error":{"type":type(e).__name__,"message":str(e)}});exit_code=1
    report["ended_utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat();raw=(json.dumps(report,ensure_ascii=False,indent=2)+"\n").encode();write(out/"RUN17_DELIVERY_READBACK.json",raw);print(json.dumps({"status":report["status"],"receipt":str(out/"RUN17_DELIVERY_READBACK.json"),**ident(raw)}));return exit_code
if __name__=="__main__":raise SystemExit(main())

