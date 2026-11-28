"""Recover verified UTF-8 source overlays from the exported R5 Drive text document.
This creates a NEW directory, not a full git clone. No source code is executed.
"""
import argparse, hashlib, json, pathlib, re
p=argparse.ArgumentParser()
p.add_argument("exported_text")
p.add_argument("new_destination")
a=p.parse_args()
raw=pathlib.Path(a.exported_text).read_text(encoding="utf-8")
dest=pathlib.Path(a.new_destination)
if dest.exists():
    raise SystemExit("DESTINATION_MUST_NOT_EXIST")
capsules=[]
for line in raw.splitlines():
    if not line.startswith('{"schema":"WU_R5_TEXT_RECOVERY_CAPSULE_V1"'):
        continue
    cap=json.loads(line)
    if cap.get("schema")!="WU_R5_TEXT_RECOVERY_CAPSULE_V1":
        raise SystemExit("BAD_SCHEMA")
    digest=hashlib.sha256((line+"\n").encode()).hexdigest()
    header="=== "+cap["stage"]+" "+cap["source_commit"]+" SHA256 "+digest+" ==="
    if header not in raw:
        raise SystemExit("CAPSULE_HASH_HEADER_MISSING")
    capsules.append(cap)
if not capsules:
    raise SystemExit("NO_CAPSULES")
required=[f"S{i:02d}" for i in range(1,11)]
if [cap["stage"] for cap in capsules[:10]]!=required:
    raise SystemExit("REQUIRE_COMPLETE_S01_THROUGH_S10_PREFIX")
if capsules[0]["parent"]!="4ea08eb3709c90285946dce2cf824f402056d645":
    raise SystemExit("PINNED_PARENT_MISMATCH")
seen={}
for index,cap in enumerate(capsules):
    if index and cap["previous_checkpoint"]!=capsules[index-1]["source_commit"]:
        raise SystemExit("CHECKPOINT_CHAIN_MISMATCH")
    for row in cap["members"]:
        path=row["path"]
        pure=pathlib.PurePosixPath(path)
        if pure.is_absolute() or ".." in pure.parts:
            raise SystemExit("UNSAFE_MEMBER_PATH")
        content=cap["files"][path]
        data=content.encode("utf-8")
        if len(data)!=row["bytes"] or hashlib.sha256(data).hexdigest()!=row["sha256"]:
            raise SystemExit("MEMBER_HASH_MISMATCH")
        sha1=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
        if sha1!=row["git_blob_sha1"]:
            raise SystemExit("GIT_BLOB_MISMATCH")
        seen[path]=data
dest.mkdir()
for name,data in seen.items():
    path=dest/name
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open("xb") as f:
        f.write(data)
print(json.dumps({"status":"RECOVERED_OVERLAY_NOT_FULL_REPOSITORY","capsules":len(capsules),"files":len(seen),"last_source_commit":capsules[-1]["source_commit"],"science_executed":False}))
